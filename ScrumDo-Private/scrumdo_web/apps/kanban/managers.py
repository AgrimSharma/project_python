from collections import defaultdict
from django.db.models import Sum
from apps.projects.models import Iteration, Story, BoardAttributes, StoryAttributes, Label, Project
from apps.kanban.models import *

from .genericworkflows import generateGenericWorkflow

import apps.organizations.tz as tz
import logging

import datetime #import datetime, timedelta, date
import math
logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 600
DEFAULT_COLUMN_WIDTH = 300

def get_aging_info(story):
    """Returns a list of aging info tuples with each record consisting of
       0 - BoardCell
       1 - How many hours spent in that cell

    This information is calcualted from the CellMovement records of the story and is not
    a particularly quick operation since it may involve a few queries.
    """

    hours = defaultdict(lambda: 0)
    cells = set()
    last_cell = None

    for movement in CellMovement.objects.filter(story=story).order_by("created").select_related("cell_to__project"):
        if last_cell is not None:
            h = round( (movement.created - previous_ts).total_seconds() / 60 / 60 )
            hours[last_cell.id] += h
        previous_ts = movement.created
        last_cell = movement.cell_to
        cells.add(last_cell)

    # At the end, we're sitting in a cell somewhere.  That current cell gets time from it's movement until right now
    if last_cell:
        h = round((datetime.datetime.now() - previous_ts).total_seconds() / 60 / 60)
        hours[movement.cell_to_id] += h

    return ((cell, hours[cell.id], {"slug":cell.project.slug,"name":cell.project.name }) for cell in cells if cell is not None)


def reset_age_values(story):
    """Resets the last_moved and accumulated_hours values on a story based on it's CellMovement records
       We're using this initially when we introduce those fields to get initial values, not sure if this
       function will be useful beyond that.

       Does not save the story.
       """
    hours = 0
    last_cell = None

    for movement in CellMovement.objects.filter(story=story).order_by("created"):
        if last_cell is not None:
            h = (movement.created - previous_ts).total_seconds() / 60 / 60
            hours += h
        previous_ts = movement.created
        last_cell = movement.cell_to

    # At the end, we're sitting in a cell somewhere.  That current cell gets time from it's movement until right now
    if last_cell:
        story.last_moved = previous_ts
        story.accumulated_hours = round(hours)
    else:
        story.accumulated_hours = 0
        story.last_moved = None



def createDefaultSavedReports(project):

    # I'm not confident enough in creating default saved reports that are useful to release it yet.
    return

    try:
        iteration = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK)[0]
        workflow = Workflow.objects.filter(project=project, flow_type=Workflow.WORK_FLOW_TYPES.generated)[0]
        steps = list(workflow.steps.all().order_by('order'))
        start_step = steps[0]
        end_step = steps[-1]
    except IndexError:
        # No iteration...
        return
    today = datetime.date.today()
    one_month = today - datetime.timedelta(days=30)

    # Remove old generated reports.
    SavedReport.objects.filter(project=project, generated=True).delete()

    # Create a 1-month CFD
    SavedReport(project=project,
                name="Cumulative Flow",
                creator=project.creator,
                workflow=workflow,
                date_format=SavedReport.DATE_FORMAT_TYPES.relative,
                startdate=one_month,
                enddate=today,
                report_type='cfd',
                iteration=iteration,
                generated=True).save()

    # Create a Burn Up
    SavedReport(project=project,
                name="Burn Up Chart",
                creator=project.creator,
                workflow=workflow,
                date_format=SavedReport.DATE_FORMAT_TYPES.relative,
                report_type='burn',
                burn_type=2,
                iteration=iteration,
                generated=True).save()

    # Create a 1-month LTH
    SavedReport(project=project,
                name="Lead Time - 1 Month",
                creator=project.creator,
                workflow=workflow,
                lead_end_step=end_step,
                lead_start_step=start_step,
                date_format=SavedReport.DATE_FORMAT_TYPES.relative,
                startdate=one_month,
                enddate=today,
                report_type='lead',
                generated=True).save()



def getDefaultWorkflow(project):
    try:
        return project.workflows.get(default=True)
    except Workflow.DoesNotExist:
        pass

    try:
        workflows = project.workflows.filter(flow_type=Workflow.WORK_FLOW_TYPES.generated)
        if workflows.count() > 0:
            return workflows[0]
    except Workflow.DoesNotExist:
        pass
    
    try:
        return project.workflows.all()[0]
    except IndexError:
        # not found so create one
        generateGenericWorkflow(project)
        return project.workflows.all()[0]



def getCompletedStories(project):
    try:
        completedStories = list(getArchiveIteration(project).stories.all())
        completedStories += list(Story.objects.filter(project=project, iteration__iteration_type=1, cell__time_type=BoardCell.DONE_TIME).distinct())
        return completedStories
    except:
        return []


def calculateStats(project):
    # logger.debug("Calculating kanban stats for %s" % project.slug)    
    completedStories = getCompletedStories(project)

    todayLeadTime = 0    
    todayStoryCount = 0
    todayWorkTime = 0

    systemStoryCount = 0
    systemLeadTime = 0
    systemWorkTime = 0

    completedPoints = 0
    lead_times = []

    for story in completedStories:
        leadTime = 0  # in minutes
        lastCell = None  # the last cell the story was in
        lastCellEntry = None  # the date the story entered that last cell
        times = [0, 0, 0, 0]
        storyFromToday = False
        storyWithin90Days = False
        foundMovement = False
        oneDayAgo = datetime.datetime.now() - datetime.timedelta(days=1)
        ninetyDaysAgo = datetime.datetime.now() - datetime.timedelta(days=90)
        completedPoints += story.points_value()



        for movement in CellMovement.objects.filter(story=story).order_by("created"):
            newCell = movement.cell_to
            foundMovement = True
            storyFromToday = storyFromToday or (movement.created > oneDayAgo)
            storyWithin90Days = storyWithin90Days or (movement.created > ninetyDaysAgo)
            if lastCell:                
                # Add the times we spent in the previous cell
                timeSpent = movement.created - lastCellEntry
                minutesSpent = timeSpent.days*24*60 + timeSpent.seconds/60
                # logger.debug("    Spent %d in %s" % (minutesSpent/60, lastCell.label))
                times[lastCell.time_type] += minutesSpent
                if lastCell.leadTime:
                    leadTime += minutesSpent
            lastCell = newCell
            lastCellEntry = movement.created        
        if not foundMovement:
            # This story never had a single movement on the board, it doesn't
            # get to affect our stats!  BAD STORY BAD BAD
            continue

        if storyWithin90Days:
            systemStoryCount += 1
            systemLeadTime += leadTime
            systemWorkTime += times[2]
            lead_times.append(leadTime)

        if storyFromToday:
            todayStoryCount += 1
            todayLeadTime += leadTime
            todayWorkTime += times[2]  # 2 = work time


    if len(lead_times) == 0:
        leadTime85 = 0
        leadTime65 = 0
    else:
        lead_times = sorted(lead_times)
        c = len(lead_times)
        leadTime85 = lead_times[int(math.floor(c * 0.85))]
        leadTime65 = lead_times[int(math.floor(c * 0.65))]

    logKanbanStats(todayLeadTime,
                   todayStoryCount,
                   todayWorkTime,
                   systemLeadTime,
                   systemStoryCount,
                   systemWorkTime,
                   len(completedStories),
                   completedPoints,
                   leadTime85,
                   leadTime65,
                   project)


def logKanbanStats(todayLeadTime,
                   todayStoryCount,
                   todayWorkTime,
                   systemLeadTime,
                   systemStoryCount,
                   systemWorkTime,
                   completedCards,
                   completedPoints,
                   leadTime85,
                   leadTime65,
                   project):
    today = tz.today(project.organization)
    try:
        stat = KanbanStat.objects.get(project=project, created=today)
    except KanbanStat.DoesNotExist:
        stat = KanbanStat(project=project, created=today)

    logger.debug("Calculated kanban stats for %s D: %d %d %d S: %d %d %d" % (project.slug, todayLeadTime, todayStoryCount, todayWorkTime, systemLeadTime, systemStoryCount, systemWorkTime))

    stat.cards_claimed = completedCards
    stat.points_claimed = completedPoints

    if todayStoryCount == 0:
        stat.daily_lead_time = 0
        stat.daily_flow_efficiency = -1
    else:
        stat.daily_lead_time = todayLeadTime / todayStoryCount
        if todayLeadTime == 0:
            stat.daily_flow_efficiency = 100
        else:
            stat.daily_flow_efficiency = min(100, int(100 * todayWorkTime / todayLeadTime))

    if systemStoryCount == 0:
        stat.system_lead_time = 0
        stat.system_flow_efficiency = -1
        stat.lead_time_85 = 0
        stat.lead_time_65 = 0
    else:
        stat.system_lead_time = systemLeadTime / systemStoryCount
        stat.lead_time_85 = leadTime85
        stat.lead_time_65 = leadTime65
        if systemLeadTime == 0:
            stat.system_flow_efficiency = 100
        else:
            stat.system_flow_efficiency = min(100, int(100 * systemWorkTime / systemLeadTime))
    stat.save()


def takeBacklogSnapshot(project):
    """ Note: We should not used this anymore.
              Backlog snapshot are created every start of the day
              and backlog stories are created every time card enter/leaves the backlog iteration.
    """
    iteration = project.get_default_iteration()
    snapshot = BacklogHistorySnapshot(backlog=iteration)
    snapshot.save()
    for story in iteration.stories.all():
        history = BacklogHistoryStories(snapshot=snapshot, story=story)
        history.save()


def _create_story_history(story):
    """ Create backlog history for story """
    backlog = story.project.get_default_iteration()
    today = datetime.date.today()

    snapshot = BacklogHistorySnapshot.objects.filter(backlog=backlog,
                                    created__year=today.year,
                                    created__month=today.month,
                                    created__day=today.day)
    if snapshot.exists():
        snapshot = snapshot.first()
    else:
        snapshot = BacklogHistorySnapshot.objects.create(backlog=backlog)
    BacklogHistoryStories.objects.create(snapshot=snapshot, story=story)
    logger.info("BacklogHistoryStories created") 


def _remove_story_history(story):
    """ Remove backlog history for story """
    backlog = story.project.get_default_iteration()
    latest_snapshot = BacklogHistorySnapshot.objects.filter(backlog=backlog).order_by('-created')
    if latest_snapshot.exists():
        snapshot = latest_snapshot.first()
        story_history = BacklogHistoryStories.objects.filter(snapshot=snapshot, story=story)
        if story_history.exists():
            story_history.first().delete()
            logger.info("BacklogHistoryStories deleted") 


def _policyKey(policy, iteration_id):
    return "pol-%d-%d" % (policy.id, iteration_id)


def _calculateAge(policy, iteration_id):
    stories = []
    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes=policy.related_value)
    ages = PolicyAge.objects.filter(policy=policy, exited=None)
    for age in ages:
        ageAmount = now - age.entered
        # logger.debug("%s - %s %s %s" % (policy.name, ageAmount, delta, ageAmount>delta))
        if ageAmount > delta:
            stories.append(age.story_id)
    return {'count':len(stories), 'stories':stories}

def _calculateWIP(policy, iteration_id):
    # The project criteria is uneccessary, but speeds up the sql query by 700x so don't remove it
    return Story.objects.filter(iteration_id=iteration_id, project=policy.project, cell__policies=policy).count()

def _calculatePoints(policy, iteration_id):
    v = 0
    # The project criteria is uneccessary, but speeds up the sql query by 700x so don't remove it
    for story in Story.objects.filter(iteration_id=iteration_id, project=policy.project, cell__policies=policy):
        v += story.points_value()
    return v

def getArchiveIteration(project):
    try:
        return project.iterations.filter(iteration_type=Iteration.ITERATION_ARCHIVE)[0]
    except IndexError:
        return None

def deleteWorkflow(workflow):
    workflow.delete()

def deletePolicy(policy):
    policy.delete()

def deleteCell(cell):
    for story in cell.stories.all():
        story.cell = None
        story.skip_announcements = True
        story.skip_haystack = True
        story.save()
    cell.delete()



def _hexColorToInt(color):
    try:
        return int(color.replace("#", ""), 16)
    except:
        logger.warn("Could not convert color %s" % color)


def autoConvertScrumProject(project, boardConfig):
    rows = []
    columns = []
    colors = [
        "#444444",
        "#777777",
        "#1F1581",
        "#448CCA",
        "#0D7D5B",
        "#FFC54A",
        "#ff7f0e",
        "#A60D05",
        "#818B16",
        "#8dc73e"
    ]


    for row in boardConfig['rows']:
        if row['type'] == 3:
            continue
        rowTitle = row['title'] if ("title" in row) else ""
        r = {'name': rowTitle, 'color': 0xf0f0f0}
        if row['type'] == 2:
            r['tag'] = row['tag']
        rows.append(r)

    statuses = list(project.statuses())
    for i in xrange(0, 10):
        column = boardConfig['columns'][i]
        if statuses[i] == '':
            continue  # No status name
        # {'name':'Todo', 'color':"#444444",'style':0, 'sub':['Doing','Done']},
        c = {
            'name': statuses[i],
            'color': colors[i],
            'status': i+1,
            'style': {  # Mapping from old column types to new styles
                0: 0,  # Standard cell
                1: 0,
                2: 1,  # Split cell
                3: 2,  # Tasks cell
                4: 0   # Hidden -> Standard
            }[column],
            'sub': boardConfig['splitNames']
        }
        columns.append(c)

    wizard(project, {'rows': rows, 'columns': columns}, True)
    try:
        backlog = Iteration.objects.get(project=project, default_iteration=True)
        backlog.iteration_type = Iteration.ITERATION_BACKLOG
    except Iteration.DoesNotExist:
        archive = Iteration(project=project, iteration_type=Iteration.ITERATION_BACKLOG, name='Backlog')
        archive.save()
    except Iteration.MultipleObjectsReturned:
        pass

    try:
        Iteration.objects.get(project=project, iteration_type=Iteration.ITERATION_ARCHIVE)
    except Iteration.DoesNotExist:
        archive = Iteration(project=project, iteration_type=Iteration.ITERATION_ARCHIVE, name='Archive')
        archive.save()

    project.project_type = Project.PROJECT_TYPE_KANBAN
    project.save()




def wizard(project, data, moveCards=False):
    logger.debug(u"Wizard ran on %s" % project.slug)
    reset(project)
    rows = data['rows']
    columns = data['columns']
    y = 0

    for row in rows:
        if row["name"] == '' and y > 0:
            continue
        y += _createRow(project, row, columns, y, moveCards, len(rows) > 1)

    if project.labels.count() == 0:
        # Create some default labels to use.
        if project.project_type == Project.PROJECT_TYPE_PORTFOLIO:
            Label(name='Differentiators', color=0xA60D05, project=project).save()
            Label(name='Cost Reducers', color=0x8DC73E, project=project).save()
            Label(name='Table Stakes', color=0x9A59B5, project=project).save()
            Label(name='Spoilers', color=0x34CC73, project=project).save()
        else:
            Label(name='User Story', color=0x34CC73, project=project).save()
            Label(name='Feature', color=0x9A59B5, project=project).save()
            Label(name='Bug', color=0xBF392B, project=project).save()

    for cell in project.boardCells.all():
        setFullCellName(project, cell)
        cell.skip_haystack = True
        cell.save()

    generateGenericWorkflow(project)


def setFullCellName(project, boardCell):
    headers = project.headers.filter(sx__lte=boardCell.x, ex__gte=(boardCell.x+boardCell.width), sy=boardCell.y-25)
    if len(headers) > 0:
        hl = headers[0].label.strip()
        l = boardCell.label.strip()
        if len(hl) > 0:
            boardCell.full_label = ("%s/%s" % (hl, l))[:100]
        else:
            boardCell.full_label = l
        logger.debug(boardCell.full_label)
    else:
        boardCell.full_label = boardCell.label


def _createSplitCell(column, project, x, y, color, height, status, time_type=None, policy_text=None):
    header = BoardHeader(project=project, sx=x, sy=y, ey=y+25, ex=x+(DEFAULT_COLUMN_WIDTH*2), background=color, label=column['name'])
    header.save()
    if policy_text is not None:
        header.policy_text=policy_text
        header.save()
    
    try:
        if column['sub_layout'] is not None:
            firstCellLayout = column['sub_layout'][0]
        else:
            firstCellLayout = 0
    except KeyError:
        firstCellLayout = 0

    return [
        _createStandardCell(column['sub'][0], project, x, y+25, 0xF5F5F5, height-25, status, time_type=time_type, layout= firstCellLayout),
        _createStandardCell(column['sub'][1], project, x+DEFAULT_COLUMN_WIDTH, y+25, 0xF5F5F5, height-25, status, time_type=BoardCell.WAIT_TIME)
    ]

def _createVerticalSplitCell(column, project, x, y, color, height, status, policy_text=None, time_type=None):
    header = BoardHeader(project=project, sx=x, sy=y, ey=y+25, ex=x+(DEFAULT_COLUMN_WIDTH), background=color, label='')
    header.save()
    return [
        _createStandardCell(column['name'], project, x, y+25, color, (height-25)/2, status, policy_text=policy_text, time_type=time_type),
        _createStandardCell(column['sub'][0], project, x, y+25+((height-25)/2), color, height/2, status,time_type=BoardCell.DONE_TIME)
    ]

def _createTaskCell(column, project, x, y, color, height, status):
    cell = _createStandardCell(column['name'], project, x, y, color, height, status)
    cell.width = 800
    cell.layout = BoardCell.LAYOUT_TASKS
    cell.save()
    return [cell]


def _createStandardCell(name, project, x, y, color, height, status, autoSave=True, doubleWidth=False, layout=BoardCell.LAYOUT_NORMAL,\
                        policy_text=None, time_type=None):
    cell = BoardCell(wipLimit=0,
                     pointLimit=0,
                     project=project,
                     label=name,
                     headerColor=color,
                     layout=layout,
                     x=x,
                     y=y,
                     height=height,
                     width=DEFAULT_COLUMN_WIDTH*2 if doubleWidth else DEFAULT_COLUMN_WIDTH)
    if policy_text is not None:
        cell.policy_text = policy_text
    
    if time_type is not None:
        cell.time_type = time_type
        
    setFullCellName(project, cell)
    if autoSave:
        cell.save()
    return cell


def setCellMovementStoryProperties(movement, story):
    if story.epic_id:
        movement.epic_id = story.epic_id
    movement.label_ids = ",".join([str(label.id) for label in story.labels.all()])
    movement.assignee_ids = ",".join([str(assignee.id) for assignee in story.assignee.all()])
    if story.tags_cache is None:
        movement.tags = ''
    else:
        movement.tags = story.tags_cache[:256]
    movement.points_value = story.points_value()


def _moveCards(project, cells, row, columnName):
    status = project.reverseStatus(columnName)
    if status == -1:
        status = 1  # This can happen when a story has a status set that has been removed from the project.

    stories = project.stories.filter(iteration__iteration_type=Iteration.ITERATION_WORK, status=status)
    if "tag" in row:
        stories = stories.filter(story_tags__tag__name__iexact=row['tag'])
    else:
        # Tagged rows get priority...
        #
        # If it's a tagged row, we let it override any previous cell
        # But if it's not a tagged row, we only move cards into it if
        # the story didn't have a cell set already.
        #
        # Notice that we don't filter on cell=None above.
        #
        stories = stories.filter(cell=None)

    # logger.info(u"_moveCards %d->%s" % (stories.count(), columnName))
    for story in stories:
        if len(cells) == 2:  # A "split" cell
            attributes = StoryAttributes.objects.filter(story=story, context="SCSB", key="SC%d" % story.status)
            column = 0
            if len(attributes) > 0:
                column = 0 if attributes[0].value == 'a' else 1
            story.cell = cells[column]
        else:
            story.cell = cells[0]
        story.skip_announcements = True
        story.skip_haystack = True
        story.save()

        # Create a cell movement so we have a consistent history to generate a CFD from.
        cellMovement = CellMovement(user=story.creator, story=story, cell_to=story.cell, related_iteration=story.iteration)
        setCellMovementStoryProperties(cellMovement, story)
        cellMovement.save()


def _createRow(project, row, columns, y, moveCards=False, createWorkflow=False):
    if row['name'] == '':
        workflowName = 'Normal'
    else:
        workflowName = row['name']
        y += 25


    if createWorkflow:
        workflow = Workflow(project=project, name=workflowName)
        workflow.save()
    else:
        workflow = None

    x = 0
    i = 0
    height = 400
    lastCells = None
    for column in columns:
        if column['name'] == '':
            continue

        color = _hexColorToInt(column['color'])


        if "status" in column:
            status = column['status']
        else:
            status = -1

        if createWorkflow:
            step = WorkflowStep(workflow=workflow, order=i, name=column['name'], report_color=color, mapped_status=status)
            step.save()

        # Cell style
        # 0 = standard
        # 1 = split
        # 2 = tasks
        # 8 = v-split
        # 9 = team assignment
        column['style'] = int(column['style'])

        try:
            policy_text = column['policy_text']
        except KeyError:
            policy_text = None
        try:
            time_type = column['time_type']
        except KeyError:
            time_type = None

        if column['style'] == 0:
            cells = [_createStandardCell(column['name'], project, x, y, color, height, status, policy_text=policy_text, time_type=time_type)]
        elif column['style'] == 1 and "tag" in row:
            # In the old superboard, for tagged rows, we never had split cells.
            # I guess it made sense for "Blocked"... not sure why we always did it that way.
            # but putting this check in here so the boards come out the same.
            cells = [_createStandardCell(column['name'], project, x, y, color, height, status, doubleWidth=True,\
                    policy_text=policy_text, time_type=time_type)]
        elif column['style'] == 1:
            cells = _createSplitCell(column, project, x, y, color, height, status, time_type=time_type, policy_text=policy_text)
        elif column['style'] == 2:
            cells = _createTaskCell(column, project, x, y, color, height, status)
        elif column['style'] == 8:
            cells = _createVerticalSplitCell(column, project, x, y, color, height, status, policy_text=policy_text, time_type=time_type)
        elif column['style'] == 9:
            cells = [_createStandardCell(column['name'], project, x, y, color, height, status, doubleWidth=False,\
                    layout=BoardCell.LAYOUT_TEAM, policy_text=policy_text, time_type=time_type)]
        else:
            logger.error("Invalid cell style")
            continue

        if moveCards:
            _moveCards(project, cells, row, column['name'])

        lastCells = cells
        if column['style'] == 8:
            x += DEFAULT_COLUMN_WIDTH
        else:
            x += sum(cell.width for cell in cells)
        for cell in cells:
            if createWorkflow:
                step.cells.add(cell)
        i += 1

    if lastCells is not None:
        for cell in lastCells:
            cell.time_type = BoardCell.DONE_TIME
            cell.save()

    if row['name'] != '':
        height += 25
        header = BoardHeader(project=project, sx=0, sy=y-25, ey=y, ex=x, background=0x666666, label=row['name'])
        header.save()

    return height


def reset(project):
    """
     Resets board structure to the initial blank state.
    """
    for policy in project.policies.all():
        deletePolicy(policy)
    for workflow in project.workflows.all():
        workflow.steps.all().delete()
        deleteWorkflow(workflow)
    for header in project.headers.all():
        header.delete()
    for cell in project.boardCells.all():
        deleteCell(cell)

def copyProjectSettings(source, destination):
    #Lablels
    for label in source.labels.filter():
        label.pk = None
        label.project = destination
        label.save()
    #other settings
    destination.use_extra_1 = source.use_extra_1
    destination.use_extra_2 = source.use_extra_2
    destination.use_extra_3 = source.use_extra_3
    destination.extra_1_label = source.extra_1_label
    destination.extra_2_label = source.extra_2_label
    destination.extra_3_label = source.extra_3_label
    destination.velocity_type = source.velocity_type
    destination.point_scale_type = source.point_scale_type
    destination.category = source.category
    destination.render_mode = source.render_mode
    destination.task_status_names = source.task_status_names
    destination.save()
    
def copyProject(source, destination):
    """Copies the board structure from one project to another."""
    reset(destination)
    workflowMapping = {}
    stepMapping = {}
    policyMapping = {}

    # Workflows
    for workflow in source.workflows.filter():
        sourceId = workflow.id
        workflow.pk = None
        workflow.project = destination
        workflow.save()
        workflowMapping[sourceId] = workflow.id
    # Then policies
    for policy in source.policies.all():
        sourceId = policy.id
        policy.pk = None
        policy.project = destination
        policy.save()
        policyMapping[sourceId] = policy
    # Then workflow steps
    for workflow in Workflow.objects.filter(project=source).all():
        for step in workflow.steps.all():
            sourceId = step.id
            step.pk = None
            step.workflow_id = workflowMapping[workflow.id]
            step.save()
            stepMapping[sourceId] = step
            step.save()
    # Then cells
    for cell in source.boardCells.all():
        policies = cell.policies.all()
        wip_policy = cell.wip_policy
        steps = cell.steps.all()
        cell.pk = None                
        cell.project = destination        
        if wip_policy:
            cell.wip_policy = policyMapping[wip_policy.id]
        cell.save()        
        for step in steps:
            if step.id in stepMapping:
                # The default workflow doesn't get in, so not all steps count
                cell.steps.add(stepMapping[step.id])
        cell.save()

        for policy in policies:
            cell.policies.add(policyMapping[policy.id])

    # And then graphics
    for graphic in source.graphics.all():
        graphic.pk = None
        if graphic.policy:
            graphic.policy = policyMapping[graphic.policy.id]
        graphic.project = destination
        graphic.save()
        
    for header in source.headers.all():
        header.pk = None
        if header.policy:
            header.policy = policyMapping[header.policy.id]
        header.project = destination
        header.save()

    # Lastly images
    for image in source.images.all():
        image.pk = None
        image.project = destination
        image.save()


def initPortfolioProject(project):
    initKanbanProject(project)
    project.card_types = "Feature             Epic                                              Bug                           "
    # set contnuous flow iteration for portfolio root project
    try:
        continuous_iteration = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK)[0]
        continuous_iteration.name = "Continuous"
        continuous_iteration.start_date = None
        continuous_iteration.end_date = None
        continuous_iteration.save()
        project.continuous_flow_iteration = continuous_iteration 
    except IndexError, e:
        pass

    project.save()


def initKanbanProject( project, defaultBoard=True):
    # Kanban projects have 3 iterations.
    default_iteration = Iteration( name='Backlog', detail='', default_iteration=True, project=project, iteration_type=Iteration.ITERATION_BACKLOG)
    default_iteration.save()


    current_iteration = Iteration(name='Iteration #1',
                                  detail='',
                                  project=project,
                                  start_date=datetime.date.today(),
                                  end_date=datetime.date.today() + datetime.timedelta(days=14),
                                  iteration_type=Iteration.ITERATION_WORK)

    current_iteration.save()

    archive_iteration = Iteration( name='Archive', detail='', project=project, iteration_type=Iteration.ITERATION_ARCHIVE)
    archive_iteration.save()

    project.project_type = Project.PROJECT_TYPE_KANBAN
    project.save()

    createDefaultSavedReports(project)

    return [default_iteration, current_iteration, archive_iteration]


def initBacklogProject( project, defaultBoard=True):
    # backlog projects have 2 iterations.
    default_iteration = Iteration( name='Uncommitted', detail='', default_iteration=True, project=project, iteration_type=Iteration.ITERATION_BACKLOG)
    default_iteration.save()

    archive_iteration = Iteration( name='Archive', detail='', project=project, iteration_type=Iteration.ITERATION_ARCHIVE)
    archive_iteration.save()

    project.project_type = Project.PROJECT_TYPE_BACKLOG_ONLY
    project.save()

    return [default_iteration, archive_iteration]

def _lastMovementIterationMatches(story):
    """
    Checks if the story's last movement record put it into it's current iteration.

    So if we move a story into "Iteration 1" and create a CellMovement record, then later call
    _lastMovementIterationMatches(story)

    If the story.iteration == "Iteration 1" we return True
    Otherwise, we return False

    This is used in moveStoryOntoCell to check and see if we need to create a movement record,
    or if it would be redundant.

    :param story: The story to check
    :return: True if the last movement moved us into the story's current iteration.
    """
    movements = CellMovement.objects.filter(story=story).order_by("-created")
    if movements.count() == 0:
        return False  # didn't have any previous movements, so we don't match.
    lastMovement = movements[0]
    return lastMovement.related_iteration_id == story.iteration_id


def moveStoryOntoDefaultCell(story, project, user, force=False):
    if not force:
        if (story.cell_id is not None) or (story.iteration.iteration_type != Iteration.ITERATION_WORK):
            return  # No need to do this.
    default_cell = project.default_cell
    if default_cell is None:
        try:
            default_cell = project.boardCells.order_by("y", "x")[0]
        except IndexError:
            pass  # No cell to get, oh well.
    if default_cell is not None:
        moveStoryOntoCell(story, default_cell, user)


def moveStoryOntoCell(story, cell, user):    
    currentCell = story.cell

    if story.iteration.iteration_type != Iteration.ITERATION_WORK:
        cell = None  # Now forcing no cell for both backlog and archive.

        if story.iteration.iteration_type == Iteration.ITERATION_BACKLOG:
            _create_story_history(story) # Create backlog snapshot

    if currentCell is None:
        currentSteps = []
        _remove_story_history(story) # Remove backlog snapshot

    else:
        currentSteps = currentCell.steps.all()

    if cell is None:
        targetSteps = []
    else:
        targetSteps = cell.steps.all()

    if (currentCell == cell) and _lastMovementIterationMatches(story):
        return
        
    iteration = story.iteration
    moveStoryIntoSteps(story, currentSteps, targetSteps, user, iteration)

    if story.last_moved is not None:
        a = datetime.datetime.now()
        b = story.last_moved
        story.accumulated_hours += round((datetime.datetime.now() - story.last_moved).total_seconds() / 60 / 60)

    if cell is not None and cell.time_type != BoardCell.DONE_TIME:
        story.last_moved = datetime.datetime.now()
    else:
        # We're either in a done cell or no cell at all, so we want a null timestamp
        story.last_moved = None

    if iteration.iteration_type != Iteration.ITERATION_WORK:
        # We reset on backlog/archive
        story.last_moved = None

    story.cell = cell
    story.save()
    cellMovement = CellMovement(user=user, story=story, cell_to=cell, related_iteration=iteration)
    setCellMovementStoryProperties(cellMovement, story)
    cellMovement.save()
    return cellMovement



def moveStoryIntoSteps(story, currentSteps, targetSteps, user, iteration, targetDate=None, updateSteps=True):
    accountedFor = []
    # logger.debug("moveStoryIntoSteps")

    # First, we create records where there is a clear from->to step mapping
    for targetStep in targetSteps:
        for currentStep in currentSteps:
            if currentStep.workflow_id == targetStep.workflow_id:
                createMovementRecord(story, currentStep, targetStep, user, iteration, targetDate)
                accountedFor.append(currentStep.id)
                accountedFor.append(targetStep.id)

    # Next, create records where a story is moved into cell that doesn't have a step 
    # in the same workflow as a step it was moved from.  ie. The step->None records
    for currentStep in currentSteps:
        if currentStep.id in accountedFor:
            continue        
        createMovementRecord(story, currentStep, None, user, iteration, targetDate)

    # Next, create records where a story is moved from cell that doesn't have a step 
    # in the same workflow as a step it was moved to.  ie. The None->Step records
    for targetStep in targetSteps:
        if targetStep.id in accountedFor:
            continue        
        createMovementRecord(story, None, targetStep, user, iteration, targetDate)

    if updateSteps:
        story.steps = targetSteps



def createMovementRecord(story, currentStep, targetStep, user, iteration, targetDate = None):
    # logger.debug("createMovementRecord %d %s %s" % (story.local_id, currentStep, targetStep) )
    if currentStep:
        workflow = currentStep.workflow
    else:
        workflow = targetStep.workflow

    # # BUG!!! the movement might also cross iteration boundries.
    # if currentStep == targetStep:
    #     # logger.info("Null movment, skipping")
    #     return

    fromName = currentStep.name if currentStep else "NULL"
    toName = targetStep.name if targetStep else "NULL"


    # logger.info("Creating step movement #%d %s %s->%s" % (story.local_id,workflow.name,fromName,toName) )
    record = StepMovement(story=story, 
                          workflow=workflow, 
                          step_from=currentStep, 
                          step_to=targetStep, 
                          user=user,
                          related_iteration=iteration
                          )
    record.save()
    if targetDate:
        record.created = targetDate
        record.save()


def handleStepsRemovedFromCell(removed, cell):
    # See https://github.com/ScrumDoLLC/ScrumDo-Private/wiki/Report-Testing
    for stepRemoved in removed:
        for story in cell.stories.all():        
            movement = StepMovement(story=story, 
                                    step_from=stepRemoved, 
                                    step_to=None, 
                                    workflow = stepRemoved.workflow,
                                    related_iteration=story.iteration
                                    )
            movement.save()
            

def handleStepsAddedToCell(added, cell):
    for stepAdded in added:
        for story in cell.stories.all():        
            movement = StepMovement(story=story, 
                                    step_from=None, 
                                    step_to=stepAdded, 
                                    workflow = stepAdded.workflow,
                                    related_iteration=story.iteration
                                    )
            movement.save()


def checkCellMovements(stories):
    """ Runs through a list of stories to make sure the last cell movement matches the current state of the story. """
    ok = 0
    bad = 0
    for story in stories:
        createRecord = False
        try:
            lastMovement = CellMovement.objects.filter(story=story).order_by('-created')[0]
            if (lastMovement.cell_to_id != story.cell_id) or (lastMovement.related_iteration_id != story.iteration_id):
                # Record doesn't match
                logger.warn("Story %d didn't match [%d]" % (story.id, story.iteration.iteration_type))
                createRecord = True
            if (story.iteration.iteration_type != Iteration.ITERATION_WORK) and (story.cell is not None):
                logger.warn("Story %d not in a work iteration, but has a cell" % story.id)
                story.cell = None
                story.save()
                createRecord = True
        except IndexError:
            if story.iteration.iteration_type != Iteration.ITERATION_BACKLOG:
                # Didn't have a last movement, but we're not in the backlog which is the only time that should happen.
                createRecord = True
                logger.warn("Story %d didn't have a movement record" % story.id)
        if createRecord:
            bad += 1
            movement = CellMovement(story=story, related_iteration=story.iteration, cell_to=story.cell)
            setCellMovementStoryProperties(movement, story)
            movement.save()
        else:
            ok += 1
    if bad > 0:
        logger.warn("Checked Cell Movments - %d good records, %d bad" % (ok, bad))
    return ok, bad


def discardedStories(iterations):
    """ Run through the Trash Bin Iteration and find id any story was part of give Iterations """
    discardedStories = []
    for iteration in iterations:
        try:
            project = iteration.project
            trashIteration = project.iterations.filter(iteration_type=Iteration.ITERATION_TRASH)[0]
            trashStories = trashIteration.stories.all()
            cellMovementsStories = CellMovement.objects.filter(related_iteration=iteration).values('story_id').distinct()

            for story in trashStories:
                if {'story_id': story.id} in cellMovementsStories:
                    discardedStories.append(story)
        except:
            pass

    return discardedStories


def get_story_cell_time(story):
    """ Run through the cell movements and find time spent in each cell type """
    hours = defaultdict(lambda: 0)
    last_cell = None

    for movement in CellMovement.objects.filter(story=story).order_by("created").select_related("cell_to__project"):
        if last_cell is not None:
            h = round( (movement.created - previous_ts).total_seconds() / 60 / 60 )
            hours[last_cell.time_type] += h
        previous_ts = movement.created
        last_cell = movement.cell_to

    # At the end, we're sitting in a cell somewhere.  That current cell gets time from it's movement until right now
    if last_cell:
        h = round((datetime.datetime.now() - previous_ts).total_seconds() / 60 / 60)
        hours[movement.cell_to.time_type] += h

    return hours

def get_iteration_flow_efficiency(iteration):
    """
        WAIT_TIME = 0
        SETUP_TIME = 1
        WORK_TIME = 2
        DONE_TIME = 3   
    """
    stories = iteration.stories.all()
    story_time = 0
    for story in stories:
        aging_info = get_story_cell_time(story)
        aging_info_items = aging_info.items()
        setup_doing = 0
        total = 0
        for cell_type, t in aging_info_items:
            if cell_type in [1,2]:
                setup_doing += t
                total += t
            else:
                total += t
        try:
            story_time = setup_doing/total
        except:
            pass 
    
    try:
        return story_time/len(stories)
    except:
        return story_time

def get_iteration_cumulative_throughput(iteration):
    res = 0
    if iteration.start_date is not None:
        previous_iterations = iteration.project.iterations.filter( start_date__lt = iteration.start_date)
        iteration_stories = iteration.stories.filter(cell__time_type=3)
        previous_stories = Story.objects.filter(iteration__in = previous_iterations, cell__time_type=3)
        res = len(iteration_stories) + len(previous_stories)
    return res 

def initContinousProject(project):
    """
    will convert new created project to continuous flow
    will set the iteration to continous iteration
    only for new created kanban projects
    """
    try:
        work_iteration = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK, hidden=False)[0]
        work_iteration.end_date = None
        work_iteration.name = "Continuous"
    except KeyError:
        work_iteration = Iteration(name='Continuous',
                                    detail='',
                                    project=project,
                                    start_date=datetime.date.today(),
                                    end_date=None,
                                    iteration_type=Iteration.ITERATION_WORK)
    work_iteration.save()
    project.continuous_flow_iteration = work_iteration
    project.save()
