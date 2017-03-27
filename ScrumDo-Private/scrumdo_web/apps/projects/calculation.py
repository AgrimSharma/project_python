from datetime import date, timedelta

from django.core.cache import cache
from django.db.models import Q
from django.conf import settings

import apps.organizations.tz as tz
from apps.projects.limits import on_demand_velocity
from apps.projects.models import *
from apps.projects.util import getStoryStatus
from apps.realtime.util import send_epic_patch, send_release_stat_patch
from apps.kanban.models import BoardCell
from apps.scrumdocelery import app

import logging
import math
logger = logging.getLogger(__name__)

from django_redis import get_redis_connection


def _projectCalcKey(projectId):
    return "calc-proj-%d" % projectId


def onDemandCalculateVelocity( project ):
    logger.info("onDemandCalculateVelocity")

    # The delay is causing issues... we need to set up different queues for different jobs
    # so this could happen quicker.
    if settings.USE_QUEUE:
        redis = get_redis_connection('default')
        redis.setex(_projectCalcKey(project.id), 300, True)
        delayedCalculateProject.apply_async((project.id,), countdown=180)
    else:
        calculateProject( project )


def _remove_duplicate_release_epics(release):
    for epic in Epic.objects.filter(releases=release, project__releases=release):
        epic.releases.remove(release)


def calculateMacroStats(storyId, previousEpicId, previousMilestoneId, previousReleaseId):
    try:
        story = Story.objects.get(id=storyId)
    except Story.DoesNotExist:
        return  # Story was deleted.
    if story.epic_id is not None:
        calculateEpicStats(story.epic)
    if previousEpicId is not None:
        calculateEpicStats(Epic.objects.get(id=previousEpicId))


def calculateAllEpics():
    c = 0
    for epic in Epic.objects.all():
        calculateEpicStats(epic, False)
        c += 1
        if c % 100 == 0:
            logger.info("Processed %d" % c)

class StatHolder(object):
    pass

def calculateReleaseStats(release, notifyClients=True):
    """
    Creates or updates a ReleaseStat record for today.
    :param release: The release (a story in a relase project) to calcualte
    :return: True if the stat was modified or created, false if nothing changed.
    """
    stat, created = ReleaseStat.objects.get_or_create(date=date.today(), release=release)
    before = (stat.cards_total, stat.cards_completed, stat.cards_in_progress,
              stat.points_total, stat.points_completed, stat.points_in_progress)
    stat.cards_total = 0
    stat.cards_completed = 0
    stat.cards_in_progress = 0
    stat.points_total = 0
    stat.points_completed = 0
    stat.points_in_progress = 0
    assignments = list(MilestoneAssignment.objects.filter(milestone=release))
    assignments_by_project_id = {assignment.assigned_project_id: assignment for assignment in assignments}

    for assignment in assignments:
        assignment.cards_total = 0
        assignment.cards_completed = 0
        assignment.cards_in_progress = 0
        assignment.points_total = 0
        assignment.points_completed = 0
        assignment.points_in_progress = 0

    unallocated = StatHolder()
    unallocated.cards_total = 0
    unallocated.cards_completed = 0
    unallocated.cards_in_progress = 0
    unallocated.points_total = 0
    unallocated.points_completed = 0
    unallocated.points_in_progress = 0

    for story in Story.objects.filter(Q(release=release) | (Q(release=None) & Q(epic__release=release))).select_related('iteration'):
        points = story.points_value()
        if story.project_id in assignments_by_project_id:
            assignment = assignments_by_project_id[story.project_id]
        else:
            assignment = unallocated

        stat.cards_total += 1
        assignment.cards_total += 1

        stat.points_total += points
        assignment.points_total += points

        if story.iteration.iteration_type == Iteration.ITERATION_ARCHIVE:
            # If it's in the archive we consider it done.
            stat.cards_completed += 1
            assignment.cards_completed += 1

            stat.points_completed += points
            assignment.points_completed += points
        elif story.cell_id is None:
            # If it doesn't have a cell, it's to do, this includes backlog items.
            pass
        elif story.cell.time_type in [BoardCell.SETUP_TIME, BoardCell.WORK_TIME]:
            stat.cards_in_progress += 1
            assignment.cards_in_progress += 1

            stat.points_in_progress += points
            assignment.points_in_progress += points
        elif story.cell.time_type == BoardCell.DONE_TIME:
            stat.cards_completed += 1
            assignment.cards_completed += 1

            stat.points_completed += points
            assignment.points_completed += points

    stat.save()
    for assignment in assignments:
        assignment.save()

    modified = created or before != (stat.cards_total, stat.cards_completed, stat.cards_in_progress,
                                 stat.points_total, stat.points_completed, stat.points_in_progress)

    if modified and notifyClients:
        send_release_stat_patch(release, stat)
    return modified


def calculateEpicStats(epic, recursive=True):
    ids = epic.child_ids()
    ids.append(epic.id)

    before = (epic.cards_total, epic.cards_completed, epic.cards_in_progress,
              epic.points_total, epic.points_completed, epic.points_in_progress)

    epic.cards_total = 0
    epic.cards_completed = 0
    epic.cards_in_progress = 0
    epic.points_total = 0
    epic.points_completed = 0
    epic.points_in_progress = 0

    for story in Story.objects.filter(epic_id__in=ids).select_related('iteration'):
        points = story.points_value()
        epic.cards_total += 1
        epic.points_total += points
        if story.iteration.iteration_type == Iteration.ITERATION_ARCHIVE:
            # If it's in the archive we consider it done.
            epic.cards_completed += 1
            epic.points_completed += points
        elif story.cell_id is None:
            # If it doesn't have a cell, it's to do, this includes backlog items.
            pass
        elif story.cell.time_type in [BoardCell.SETUP_TIME, BoardCell.WORK_TIME]:
            epic.cards_in_progress += 1
            epic.points_in_progress += points
        elif story.cell.time_type == BoardCell.DONE_TIME:
            epic.cards_completed += 1
            epic.points_completed += points

    modified = before != (epic.cards_total, epic.cards_completed, epic.cards_in_progress,
                          epic.points_total, epic.points_completed, epic.points_in_progress)

    if modified:
        epic.skip_story_labels = True
        epic.skip_haystack = True
        epic.save()
        send_epic_patch(epic.project, epic, {'stats': {
            'cards_total': epic.cards_total,
            'cards_completed': epic.cards_completed,
            'cards_in_progress': epic.cards_in_progress,
            'points_total': epic.points_total,
            'points_completed': epic.points_completed,
            'points_in_progress': epic.points_in_progress,
        }})

    parent = epic.parent
    if recursive and parent is not None:
        modified |= calculateEpicStats(parent)

    return modified


@app.task
def calculateReleasePoints(releaseID):
    logger.info("Calculating release points")
    release = Release.objects.get(id=releaseID)
    story_ids = []
    points_claimed = [0,0,0,0,0,0,0,0,0,0]
    stories_claimed = [0,0,0,0,0,0,0,0,0,0]    
    points_total = 0
    story_count = 0
    time_estimated = 0
    time_claimed = 0
    _remove_duplicate_release_epics(release)
    release_epics = list(release.epics.all())
    
    projects = release.projects.all()
    for project in projects:
        for epic in project.epics.all():
            if epic in release_epics:
                logger.info("Removing epic because it's in a release.")
                release.epics.remove(epic) # This removes epics that are both manually in the release, and in the release via a project.                
            points_total += epic.normalized_points_value()
            points_claimed[0] += epic.normalized_points_value()            
            
        for story in project.stories.all():
            try:
                storyStatus = getStoryStatus(story, project)
                story_points = story.points_value()
                points_total += story_points
                points_claimed[storyStatus-1] += story_points
                stories_claimed[storyStatus-1] += 1
                story_count += 1
                story_ids.append(story.id)
                time_estimated += (story.estimated_minutes + story.task_minutes)
                if storyStatus == Story.STATUS_DONE:
                    time_claimed += story.estimated_minutes
                if story.task_minutes > 0:
                    for task in story.tasks.all():
                        if task.status == Story.STATUS_DONE:
                            time_claimed += task.estimated_minutes
            except ValueError:
                pass # probably ? or infinity
                
    logger.info("%d project stories" % story_count)
    logger.info(release.epics.count())
    for epic in release.epics.all():
        project = epic.project
        if project in projects:
            continue
        points_total += epic.normalized_points_value()
        points_claimed[0] += epic.normalized_points_value()
        for story in epic.stories.all():
            try:
                storyStatus = getStoryStatus(story,project)
                story_count += 1
                story_points = story.points_value()
                points_total += story_points
                points_claimed[storyStatus-1] += story_points
                stories_claimed[storyStatus-1] += 1
                story_ids.append(story.id)
                time_estimated += (story.estimated_minutes + story.task_minutes)
                if storyStatus == Story.STATUS_DONE:
                    time_claimed += story.estimated_minutes
                if story.task_minutes > 0:
                    for task in story.tasks.all():
                        if task.status == Story.STATUS_DONE:
                            time_claimed += task.estimated_minutes
            except ValueError:
                pass # probably ? or infinity
    
    logger.info("%d epic stories" % story_count)
    today = tz.today(release.organization)
    try:
        log = ReleaseLog.objects.get(date=today, release=release)
    except ReleaseLog.DoesNotExist:
        log = ReleaseLog(date=today, release=release)


    log.points_total = points_total
    log.points_status1 = math.ceil(points_claimed[0])
    log.points_status2 = math.ceil(points_claimed[1])
    log.points_status3 = math.ceil(points_claimed[2])
    log.points_status4 = math.ceil(points_claimed[3])
    log.points_status5 = math.ceil(points_claimed[4])
    log.points_status6 = math.ceil(points_claimed[5])
    log.points_status7 = math.ceil(points_claimed[6])
    log.points_status8 = math.ceil(points_claimed[7])
    log.points_status9 = math.ceil(points_claimed[8])
    log.points_status10 = math.ceil(points_claimed[9])

    log.stories_status1 = stories_claimed[0]
    log.stories_status2 = stories_claimed[1]
    log.stories_status3 = stories_claimed[2]
    log.stories_status4 = stories_claimed[3]
    log.stories_status5 = stories_claimed[4]
    log.stories_status6 = stories_claimed[5]
    log.stories_status7 = stories_claimed[6]
    log.stories_status8 = stories_claimed[7]
    log.stories_status9 = stories_claimed[8]
    log.stories_status10 = stories_claimed[9]

    log.story_count = story_count
    log.time_estimated = time_estimated
    log.time_estimated_completed = time_claimed
    log.total_time_spent = _calculateReleaseTotalSpentTime(story_ids)
    log.save()
    release.calculating = False
    release.save()
    cache_key = "release_page_%s" % str(release.id)
    cache.delete(cache_key)


def _calculateReleaseTotalSpentTime(story_ids):
    logger.info("Calculating release total time spent")
    total_minutes = 0
    for entry in TimeEntry.objects.filter(story__in=story_ids):
        total_minutes += entry.minutes_spent
    logger.info("%d minutes total" % total_minutes)
    return total_minutes


@app.task
def delayedCalculateProject(projectID):
    redis = get_redis_connection('default')
    if redis.delete(_projectCalcKey(projectID)) == 1:
        # The key exists, so another delayedCalculateProject instance hasn't
        # come around and done it already.
        project = Project.objects.get(id=projectID)
        calculateProject(project)


def calculatePoints(stories, epics):
    points_claimed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    points_total = 0
    time_estimated = 0
    time_claimed = 0
    project = None
    for story in stories:
        if project is None:
            project = story.project
        try:
            time_estimated += (story.estimated_minutes + story.task_minutes)
            storyStatus = getStoryStatus(story, project)
            if storyStatus == Story.STATUS_DONE:
                time_claimed += story.estimated_minutes
            if story.task_minutes > 0:
                for task in story.tasks.all():
                    if task.status == Story.STATUS_DONE:
                        time_claimed += task.estimated_minutes

            story_points = story.points_value()
            points_total += story_points
            points_claimed[storyStatus-1] += story_points

        except ValueError:
            pass # probably ? or infinity

    for epic in epics:
        try:
            points_total += epic.normalized_points_value()
        except ValueError:
            pass

    return [points_total] + points_claimed + [time_estimated, time_claimed]


def calculateProjectVelocity(project, total_project_points, points_todo):
    today = tz.today(project.organization) # date.today()
    # Loop through all completed iterations and gather info
    iteration_points = []
    for iteration in project.iterations.filter(end_date__lte=today, iteration_type=Iteration.ITERATION_WORK):
        points = 0
        for story in iteration.stories.all():
            storyStatus = getStoryStatus(story, project)
            if storyStatus == Story.STATUS_DONE:
                try:
                    points += story.points_value()
                except ValueError:
                    pass # probably ? or infinity
        iteration_points.append(points)
            # logger.info("Including %s / %d" % (iteration.name, points) )

    velocity = 0
    if project.velocity_type == project.VELOCITY_TYPE_AVERAGE:
        velocity = calculateAverage(iteration_points)
    elif project.velocity_type == project.VELOCITY_TYPE_AVERAGE_5:
        velocity = calculateAverageLastN(iteration_points, 5)
    elif project.velocity_type == project.VELOCITY_TYPE_AVERAGE_3:
        velocity = calculateAverageLastN(iteration_points, 3)
    else:
        velocity = calculateMedian(iteration_points)

    project.velocity = round(velocity)
    if project.velocity > 0:
        project.iterations_left = int(points_todo / project.velocity)

    project.save()


def calculateMedian(iteration_points):
    if len(iteration_points) == 0:
        return 0
    sorted_list = sorted( iteration_points )
    return sorted_list[ int(len( iteration_points ) / 2 ) ]



def calculateAverageLastN( iteration_points , n):
    if len(iteration_points) <= n:
        return calculateAverage( iteration_points )
    total = sum( iteration_points[-n:] )
    return total / n



def calculateAverage( iteration_points ):
    if len( iteration_points ) == 0:
        return 0
    total = sum( iteration_points )
    #print "%d / %d" % (total, len(iteration_points))
    return total / len( iteration_points )


def logPoints( related_object, points, today):
    # today = date.today()
    # logger.info("%s %d %f" % (related_object, points_claimed, points_total) )
    try:
        log = related_object.points_log.get(date=today)
        # logger.debug("logPoints found a previous record.")
    except:
        if hasattr(related_object, "project_id"):
            log = PointsLog(date=today, iteration=related_object)
        else:
            log = PointsLog(date=today, project=related_object)

    log.points_total = points[0]
    log.points_status1 = points[1]
    log.points_status2 = points[2]    
    log.points_status3 = points[3]
    log.points_status4 = points[4]
    log.points_status5 = points[5]
    log.points_status6 = points[6]                
    log.points_status7 = points[7]
    log.points_status8 = points[8]
    log.points_status9 = points[9]
    log.points_status10 = points[10]
    log.time_estimated = points[11]               
    log.time_estimated_completed = points[12]
    log.save()


def calculateProject(project):
    if not project.active:
        return

    stories = project.stories.all()
    epics = project.epics.all().exclude(archived=True)

    points = calculatePoints(stories, epics)

    total_project_points = points[0]
    points_todo = points[0] - points[1]

    today = tz.today(project.organization)  #date.today()

    logPoints(project, points, today)

    yesterday = today - timedelta( days=1 )
    tomorrow = today +  timedelta( days=1 )
    points_total = 0

    calculateProjectVelocity(project, total_project_points, points_todo)

    for iteration in project.iterations.filter( start_date__lte=tomorrow, end_date__gte=yesterday):
        if( iteration != project.get_default_iteration() ):
            points = calculatePoints(iteration.stories.all(), [])
            if points[0] > 0:  # only logging active iterations with stuff in them
                logPoints(iteration, points, today)
