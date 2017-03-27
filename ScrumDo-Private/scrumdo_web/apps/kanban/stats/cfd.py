from ..models import StepMovement, BacklogHistorySnapshot, CellMovement
from ..util import getMovements, dateTimestamp, getLatestCellReportData, UnicodeReader, dateTimestamp, json_default
from ..tasks import generateCachedBacklogCfd
from dateutil.parser import parse as parseDate
from apps.projects.models import Iteration

from django.utils.html import strip_tags
from django_redis import get_redis_connection

import datetime
import math
import logging
import os
import traceback
import sys
import json

logger = logging.getLogger(__name__)

FIVEDAYS = 5 * 24 * 60 * 60
THREE_DAYS = 3 * 24 * 60 * 60

def _fillCFDBacklog(project, buckets, backlogIndex):
    lastCount = 0
    backlogIteration = project.get_default_iteration()

    for entry in buckets[backlogIndex]['values']:
        date = entry['date']
        try:
            snapshot = BacklogHistorySnapshot.objects.filter(backlog=backlogIteration,
                created__year=date.year,
                created__month=date.month,
                created__day=date.day,
                ).order_by("-created")[0]
            lastCount = snapshot.stories.count()
            stories =  snapshot.stories.all()
            for story in stories:
                entry['stories'].append(story.story.local_id)
        except:
            # No data found, use the last one.
            pass
        entry['y'] = lastCount


def _storySummaryJSON(story):
    summary = strip_tags(story.summary)
    summary = (summary[:50] + '...') if len(summary) > 52 else summary
    return "%s-%d %s" % (story.project.prefix, story.local_id, summary)
    # {
    #     "id": story.id,
    #     "summary": "#%d %s" % (story.local_id, summary)
    # }



def timestampHash(timestamp, bucketsize):
    """ Transforms a unix timestamp into a bucket ID we can use as a key
       to a dict to store the CFD data in.  Incidently, that bucket ID
       is also a timestamp representing the beginning of the bucket.
    :param timestamp: the datetime to use
    :param bucketsize: the size of each bucket, in seconds.
    """
    return (timestamp / bucketsize)


def passesFilter(story_id, step_id, trackedStories, iteration_id, assignees, tags, labels, epic_id,
                 filterIteration, filterAssignee,  filterTag,  filterLabel,  filterEpic):
    if filterIteration != 'ALL' and iteration_id != filterIteration:
        # We're filtering out this iteration... but there is a chance that
        # this is the special case where a card is in the archive, and that card was once in the
        # workflow, so we're are tracking it and we do car.
        return step_id == -1 and story_id in trackedStories
    if filterAssignee and not filterAssignee in assignees.split(","):
        return False
    if filterTag and not filterTag in tags.split(","):
        if filterTag in tags:
            pass
        return False
    if filterLabel and not filterLabel in labels.split(","):
        return False
    if filterEpic and not filterEpic in epic_id.split(","):
        return False

    return True


def generateCFDFromCSV(filename, project, workflow,
                       backlog, filterAssignee, filterTag, filterLabel,
                       filterEpic, generateDetail, yaxis,
                       filterIteration, startdate, enddate):
    outputData = []
    steps = {}   # Key: stepId
    values = {}  # Key: stepId:bucket
    legends = []
    archive_storyIds = []

    # firstMovement = CellMovement.objects.filter(project=project).order_by("created")[0]
    try:
        lastMovement = CellMovement.objects.filter(story__project=project).order_by("-created")[0]
        firstMovement = CellMovement.objects.filter(story__project=project).order_by("created")[0]
        lastTimestamp = dateTimestamp(lastMovement.created)
    except IndexError:
        # no movements found
        return {"data": [], "detail": [], "legends":[]}

    archive_iteration = Iteration.objects.filter(project=project, iteration_type=Iteration.ITERATION_TRASH)    
    if len(archive_iteration) > 0:
        archive_storyIds.extend(list(map(int, archive_iteration[0].stories.all().values_list('id', flat=True))))
    if startdate is None:
        startdate = firstMovement.created
    else:
        startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")

    if enddate is None:
        # enddate = lastMovement.created
        enddate = datetime.datetime.now()
    else:
        enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d") + datetime.timedelta(days=1, seconds=-1)
        # Add (almost) one day so we go to the end of the day selected.

    if filterIteration != 'ALL':
        filterIteration = int(filterIteration)

    yaxis = int(yaxis)

    stepData = {"color": 0xB8C3A7, 'values': [], 'name': 'Archive'}
    legendData = {"color": 0xB8C3A7, 'name': 'Archive'}
    steps[-1] = stepData    # This is so we can quick-look it up

    outputData.append(stepData)  # This is the eventual output format
    legends.append(legendData)

    for step in workflow.steps.all().order_by("-order"):
        stepData = {"color": step.report_color, 'values': [], 'name': step.name}
        legendData = {"color": step.report_color, 'name': step.name}
        steps[step.id] = stepData    # This is so we can quick-look it up
        outputData.append(stepData)  # This is the eventual output format
        legends.append(legendData)

    dateRange = enddate - startdate

    if dateRange.days > 365:
        bucketsize = 7*24*60*60  # 7 day buckets
    elif dateRange.days > 13:
        bucketsize = 24*60*60  # 1 day buckets
    elif dateRange.days > 7:
        bucketsize = 12*60*60  # 12 hour
    elif dateRange.days > 2:
        bucketsize = 6*60*60  # 6 hour
    else:
        bucketsize = 60*60  # 1 hour

    # enddate += datetime.timedelta(seconds=bucketsize-1)

    trackedStories = set()
    output = {"data": outputData, "detail": [], "legends":legends}
    with open(filename, 'rb') as csvfile:
        reader = UnicodeReader(csvfile, delimiter='|', quotechar='\'')
        for row in reader:
            (story_id, iteration_id, step_id, enterTime, exitTime, assignees, tags, labels, epic_id, points, story_number, story_hours) = row

            if exitTime == '':
                # If the card never exited this record, we can assume it's still there and use enddate for it
                # since our report only goes that far and anything past that is moot
                exitTime = dateTimestamp(enddate) + bucketsize
            else:
                exitTime = int(exitTime)

            story_id = int(story_id)

            iteration_id = "-1" if iteration_id == '' else int(iteration_id)
            enterTime = int(enterTime)

            step_id = int(step_id)
            points = float(points)
            story_hours = float(int(story_hours)/60)

            if not passesFilter(story_id, step_id, trackedStories, iteration_id, assignees, tags, labels, epic_id,
                                filterIteration, filterAssignee,  filterTag,  filterLabel,  filterEpic):
                # We don't care about this one...
                continue

            step = steps[step_id]
            for bucket in range(timestampHash(enterTime, bucketsize), timestampHash(exitTime, bucketsize)):
                valueKey = "{step_id}:{bucket}".format(step_id=step_id, bucket=bucket)
                if not valueKey in values:
                    # This is the first entry for this step/date
                    # We need to make a bucket in every step so each step has the
                    # same number of buckets within it.
                    d = datetime.datetime.utcfromtimestamp(bucket*bucketsize)
                    if d < startdate or d > enddate:
                        if d > enddate:
                            logger.info("Skipping %s" % d)
                        continue
                    for oStepId, oStep in steps.iteritems():
                        oValueKey = "{step_id}:{bucket}".format(step_id=oStepId, bucket=bucket)
                        values[oValueKey] = {'date': d, 'y': 0, 'stories': []}
                        oStep['values'].append(values[oValueKey])

                if valueKey in values:

                    # remove archive stories from graph
                    if not story_id in archive_storyIds: 
                        values[valueKey]['stories'].append(story_number)
                        trackedStories.add(story_id)
                        if yaxis == 1:
                            values[valueKey]['y'] += 1
                        elif yaxis == 3:
                            values[valueKey]['y'] += story_hours
                        else:
                            values[valueKey]['y'] += points

    for valueList in steps.values():
        valueList['values'].sort(key=lambda obj: obj['date'])
        

    if backlog:
        v = [{'date': entry['date'], 'y': 0, 'stories': []} for entry in outputData[0]['values']]
        currentSeries = {'color':0xd0d0d0, 'name':"Backlog", 'values': v, 'stories': []}
        legendCurrentSeries = {'color':0xd0d0d0, 'name':"Backlog"}
        outputData.append(currentSeries)
        legends.append(legendCurrentSeries)
        _fillCFDBacklog(project, outputData, len(outputData)-1)

    # Finally, remove uninteresting series
    for series in outputData:
        interesting = False
        for entry in series['values']:
            if entry['y'] > 0:
                interesting = True
                break
        if not interesting:
            outputData.remove(series)
    for series in outputData:
        height=0
        for entry in series['values']:
            height=height+entry['y']
        try:
            series['avgHeight']=round(height/float(len(series['values'])),2)
        except ZeroDivisionError:
            series['avgHeight']=0
    return output


def calculateCFD(project,
                 workflow,
                 backlog,
                 assignee,
                 tag,
                 label,
                 epic,
                 generateDetail=False,
                 yaxis=1,
                 iteration="ALL",
                 startdate=None,
                 enddate=None):

    filename = getLatestCellReportData(project, workflow)
    try:
        r = generateCFDFromCSV(filename, project, workflow, backlog, assignee, tag, label, epic, generateDetail, yaxis, iteration, startdate, enddate)
        return r
    except:
        logger.error("\n".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
        return {'error': True}
    finally:
        os.unlink(filename)


def calculateBacklogCFD(project, startdate=None, enddate=None, cached=False):
    redis = get_redis_connection('default')
    cacheFields = (project.slug, )
    cacheFields = [str(f) for f in cacheFields]
    cacheKey = "BACKLOGCFD-" + "-".join(cacheFields)
    
    if cached:
        previous = redis.get(cacheKey)
        if previous:
            if redis.ttl(cacheKey) < THREE_DAYS:
                generateCachedBacklogCfd.delay(project, startdate, enddate)
            return json.loads(previous)

    outputData = []
    legends = []
    output = {"data": outputData, "detail": [], "legends":legends}

    lastMovement = CellMovement.objects.filter(story__project=project).order_by("-created").first()
    firstMovement = CellMovement.objects.filter(story__project=project).order_by("created").first()

    if firstMovement is None:
        return output

    if startdate is None:
        startdate = firstMovement.created
    else:
        startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")

    if enddate is None:
        enddate = datetime.datetime.now()
    else:
        enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d") + datetime.timedelta(days=1, seconds=-1)
        # Add (almost) one day so we go to the end of the day selected.

    dateRange = enddate - startdate

    if dateRange.days > 365:
        bucketsize = 7*24*60*60  # 7 day buckets
    elif dateRange.days > 13:
        bucketsize = 24*60*60  # 1 day buckets
    elif dateRange.days > 7:
        bucketsize = 12*60*60  # 12 hour
    elif dateRange.days > 2:
        bucketsize = 6*60*60  # 6 hour
    else:
        bucketsize = 60*60  # 1 hour

    v  = []

    for bucket in range(timestampHash(dateTimestamp(startdate), bucketsize), timestampHash(dateTimestamp(enddate), bucketsize)):
        d = datetime.datetime.utcfromtimestamp(bucket*bucketsize)
        v.extend([{'date': d, 'y': 0, 'stories': []}])
    
    series = {'color':0xd0d0d0, 'name':"Backlog", 'values': v, 'stories': []}
    legendSeries = {'color':0xd0d0d0, 'name':"Backlog"}
    outputData.append(series)
    legends.append(legendSeries)
    _fillCFDBacklog(project, outputData, len(outputData)-1)

    redis.setex(cacheKey, FIVEDAYS, json.dumps(output, default=json_default))
    return output 
