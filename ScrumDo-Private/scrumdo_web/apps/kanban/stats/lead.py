import datetime
import math
import logging
import itertools
import json

from operator import itemgetter
from dateutil.parser import parse as parseDate
from ..models import StepMovement, BacklogHistorySnapshot, WorkflowStep
from ..util import getMovements
import apps.kanban.tasks as tasks
from django_redis import get_redis_connection

from apps.projects.models import Story, Iteration

logger = logging.getLogger(__name__)

FIVEDAYS = 5 * 24 * 60 * 60
THREE_DAYS = 3 * 24 * 60 * 60

def createIfMissing(stories, storyId, story_num):
    if not storyId in stories:
        stories[storyId] = {"enter":None, "exit":None, "duration": None, "story_number": story_num}


def matchedExitStep(fromStep, toStep, targetStepId, allSteps):    
    if targetStepId >= 0:
        # Exact match
        return toStep is not None and toStep.id == targetStepId
    elif targetStepId < 0:
        # Going from a step in the workflow to out of the workflow
        # AND we're set to exit to the archive.
        # In this case, we match if the step was the last step in the workflow        
        return (fromStep is not None) and (toStep is None) and (allSteps[-1] == fromStep)


def matchesEntryStep(step, targetStep, endStep):
    " Returns true if step is an 'entry' step for a lead time calc given targetStepId"    
    if step != None and step.id == targetStep.id:
        # Normal case of moving into an entry step.
        return True

    # Sometimes, the entry step is skipped.  In those cases if the step is between the entry and the exit
    # we count it.  The endStep could be None if we going to the archive, in that case, we can ignore the end step
    # order check.
    if step != None and step.order > targetStep.order and ( (endStep == None) or (step.order < endStep.order) ):
        return True


    return False


def updateStartDate(stories, storyId, fromStep, toStep, created, startStep, endStep):    
    update = False
    entry = stories[storyId]    
    if entry["enter"] == None and matchesEntryStep(toStep, startStep, endStep):        
        # Normal case: We didn't have an entry, and this step matches our entry criteria
        update = True
    if not update:
        return
    entry["enter"] = created

def updateEndDate(stories, storyId, fromStep, toStep, created, endStepId, allSteps):
    update = False
    entry = stories[storyId]    
    if entry["exit"] == None and matchedExitStep(fromStep, toStep, endStepId, allSteps):        
        # Normal case: We didn't have an entry, and this step matches our entry criteria
        update = True
    if not update:
        return
    entry["exit"] = created

def generateIntervalKey(intervalType, value):
    if intervalType == 2:
        c = math.floor(value/3)
        return ("%d-%d" % (c*3+1,(c+1)*3) ,c, c*3+1,(c+1)*3)
    elif intervalType == 4:
        # Powers of 2...
        if value == 0:
            return ("0",0,0,0)
        c = math.floor(math.log(value, 2))
        l = math.pow(2,c)
        h = math.pow(2,c+1) - 1
        c += 1
        if l == 1:
            return ("1",c,1,1)
        else:
            return ("%d-%d" % (l,h),c,l,h)
    else:
        return (str(value),value,value,value)



def calculateLeadTime(project,
                      workflow,
                      startStepID,
                      endStepID,
                      interval,
                      assignee,
                      tag,
                      category,
                      epic,
                      generateDetail=False,
                      startdate=None,
                      enddate=None,
                      forReport=True,
                      cached=False):

    redis = get_redis_connection('default')
    cacheFields = (project.slug, workflow.id, startStepID, endStepID, interval, assignee, tag, category, epic, generateDetail, startdate, enddate)
    cacheFields = [str(f) for f in cacheFields]
    cacheKey = "LTH3-" + "-".join(cacheFields)

    if cached:
        previous = redis.get(cacheKey)
        if previous:
            if redis.ttl(cacheKey) < THREE_DAYS:
                tasks.generateCachedLTH.delay(project, workflow, startStepID, endStepID, interval, assignee, tag, category, epic, generateDetail, startdate, enddate)
            return json.loads(previous)

    movements = getMovements(workflow, assignee, tag, category, epic)
    allSteps = list( workflow.steps.all().order_by("order"))
    # stories[id] = {enter:date or None, exit:date or None}
    stories = {}
    detail = []
    maxDuration = 0
    archive_storyIds = []

    if startdate:
        startdate = parseDate(startdate)

    if enddate:
        enddate = parseDate(enddate)
        enddate += datetime.timedelta(days=1)  # things on the end date count, so add one


    startStep = WorkflowStep.objects.get(id=startStepID)
    if endStepID < 0:
        endStep = None
    else:
        endStep = WorkflowStep.objects.get(id=endStepID)

    archive_iteration = Iteration.objects.filter(project=project, iteration_type=Iteration.ITERATION_TRASH)
    if len(archive_iteration) > 0:
        archive_storyIds.extend(list(map(int, archive_iteration[0].stories.all().values_list('id', flat=True))))

    for movement in movements:
        if not int(movement.story_id) in archive_storyIds: # exclude archive story from report
            storyId = movement.story_id
            storyNumber = movement.story.local_id
            createIfMissing(stories, storyId, storyNumber)
        fromStep = movement.step_from
        toStep = movement.step_to
        created = movement.created
        try:
            # check is we get storyId here
            updateStartDate(stories, storyId, fromStep, toStep, created, startStep, endStep)
            updateEndDate(stories, storyId, fromStep, toStep, created, endStepID, allSteps)
        except UnboundLocalError:
            pass

    # logger.debug(stories)
    # At this point, we have a list of entry/exit dates for stories. 
    # Time to generate a sorted list of lengths.
    data = []
    for storyId in stories:
        entry = stories[storyId]
        if entry["enter"] == None or entry["exit"] == None:
            continue

        if startdate is not None and entry["exit"] < startdate:
            continue  # Before our date range

        if enddate is not None and entry["exit"] > enddate:
            continue  # after our date range

        duration = max(0, (entry["exit"] - entry["enter"]).days )
        entry['duration'] = duration 

        maxDuration = max(maxDuration, duration)

        data.append(entry)

        if generateDetail:
            story = Story.objects.get(id=storyId)
            detail.append([storyId,
                           "%s-%d %s" % (project.prefix, story.local_id, story.summary), 
                           duration,
                           entry["enter"].strftime("%Y-%m-%d %H:%M"),
                           entry["exit"].strftime("%Y-%m-%d %H:%M")
                           ])

    data_graph = []
    sorted_duration = sorted(data, key=itemgetter('duration'))
    for key, group in itertools.groupby(sorted_duration, key=lambda x:x['duration']):
        # We should group stories by duration
        # e.g {1: [{'duration': 1, 'story_id': 1}], 2: [{'duration': 2, 'story_id': 12}]}
        q = {key: list(group)}
        data_graph.append(q)

    get_durations = [x.keys().pop() for x in data_graph] # Get durations from list
    total = sum(get_durations) # Sum of total durations

    #return stories leadtime data to calculate
    #project aging threshold recommended values
    if forReport == False:
        return get_durations
    
    result = []
    lastInterval = -1    
    current = None

    if len(data) > 0:
        median = get_durations[int(math.floor(len(get_durations)/2))]
        mean = total / len(get_durations)
    else:
        median = 0
        mean = 0

    if interval == -1:
        # We should calculate interval based on data in this case.
        if maxDuration < 10:
            interval = 1
        elif maxDuration < 30:
            interval = 2
        else:
            interval = 4

    foundMean = False

    for entry in data_graph:
        duration = entry.keys().pop()
        intervalKey, intervalColumn, low, high = generateIntervalKey(interval, duration)
        total += int(duration) 

        for k,v in entry.iteritems():
            cards = [d['story_number'] for d in v]

        if intervalKey != lastInterval:
            lastInterval = intervalKey
            current = {"label":intervalKey, 
                       "count": len(cards), 
                       "column":intervalColumn,
                       "mean" : low <= mean <= high,
                       "median" : low <= median <= high,
                       "cards": cards
                       }
            result.append(current)
            foundMean = foundMean or current["mean"]

    if not foundMean:
        mean = int(mean)
        entry = {
            "label": str(mean),
            "count": 0,
            "column": mean,
            "mean": True,
            "median": False
        }
        result.append(entry)
    detail = sorted(detail, key=lambda d: d[2])

    result = {"data":result, "median":median, "mean":mean, "detail":detail }
    redis.setex(cacheKey, FIVEDAYS, json.dumps(result))
    return result


def calculateIncrementLeadTime(project, iteration_id):
    iteration = project.iterations.get(id=iteration_id)

    try:
        workflow = project.workflows.prefetch_related("steps").all().order_by("-flow_type", "name")[0]
        startdate = None if iteration.start_date is None else iteration.start_date.strftime('%Y-%m-%d')
        enddate = None if iteration.end_date is None else iteration.end_date.strftime('%Y-%m-%d')

        startStep = workflow.steps.all().order_by("order")[0]
        endStep = workflow.steps.all().order_by("-order")[0] 

        data = calculateLeadTime(project, workflow, startStep.id, endStep.id,
                        -1, None, None, None, None, generateDetail=False,
                        startdate=startdate, enddate=enddate)

        return data
    except:
        return {"mean": 0, "median": 0}


    

