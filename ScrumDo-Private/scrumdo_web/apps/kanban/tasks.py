from django.template import defaultfilters
from django.utils.html import strip_tags
from django.conf import settings

import urlparse

from .models import *
from .managers import createDefaultSavedReports, checkCellMovements, moveStoryOntoCell, \
    moveStoryIntoSteps, generateGenericWorkflow, takeBacklogSnapshot, calculateStats, reset_age_values
from .boardcreator import createBoard
from .util import resetWorkflowReportData, conditionalGenerateCellReportData, resetTagReportData

import stats

from apps.projects.models import *
from apps.projects.calculation import calculateEpicStats
from apps.activities.models import NewsItem
from apps.projects import signals
from apps.favorites.models import Favorite
from apps.scrumdocelery import app
import sys, traceback

import classicconvert

import random
import string
import datetime
import os

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def scheduleRebuildStepMovements(project, user=None):
    job = RebuildMovementJob(project=project, initiator=user)
    job.save()
    if settings.DEBUG:
        countdown = 3
    else:
        countdown = 60
    rebuildStepMovements.apply_async((job.id,), countdown=countdown)  # schedule the job 1 minute in the future.


def scheduleConvertClassicProject(organization, projectId, user, mode):
    job = OfflineJob(organization=organization, owner=user, completed=False, job_type="Upgrading Project")
    job.save()
    convertClassicProject.apply_async((projectId, mode, job.id), countdown=3)

    # For Debugging:
    # convertClassicProject(projectId, mode, job.id)
    return job.id

@app.task
def generateCachedLTH(project,
                      workflow,
                      startStepID,
                      endStepID,
                      interval,
                      assignee,
                      tag,
                      category,
                      epic,
                      generateDetail,
                      startdate,
                      enddate):
    # This generates a new copy in our cache.
    logger.info('Regenerating a cached LTH for ' + project.slug)
    stats.calculateLeadTime(project, workflow, startStepID, endStepID, interval, assignee, tag, category, epic, generateDetail, startdate, enddate)

@app.task
def generateCachedBacklogCfd(project,
                            startDate,
                            endDate):
    # This generates a new copy in our cache.
    logger.info('Regenerating a cached Backlog CFD for ' + project.slug)
    stats.calculateBacklogCFD(project, startDate, endDate)


@app.task
def reset_project_age_values(project_slug):
    project = Project.objects.get(slug=project_slug)
    for story in project.stories.all():
        reset_age_values(story)
        story.skip_haystack = True
        story.save()

@app.task
def check_cell_movements():
    totalGood = 0
    totalBad = 0
    projects = Project.objects.filter(abandoned=False, active=True)

    for project in projects:
        stories = project.stories.all()
        days = 1
        if days > 0:
            beginning = datetime.date.today() - datetime.timedelta(days=days)
            stories = stories.filter(modified__gt=beginning)

        ok, bad = checkCellMovements(stories)
        totalGood += ok
        totalBad += bad
        if bad > 0:
            logger.info("Project %s had problems" % project.slug)
            scheduleRebuildStepMovements(project)

    if totalBad > 0:
        logger.warn("Total good: %d, bad: %d" % (totalGood, totalBad) )


@app.task
def record_all_project_stats():
    projects = Project.objects.filter(abandoned=False,
                                      active=True,
                                      project_type__in=[Project.PROJECT_TYPE_KANBAN, Project.PROJECT_TYPE_PORTFOLIO])

    today = datetime.date.today()
    mdiff = datetime.timedelta(days=-90)
    date_90days_ago = today + mdiff
    processed = 0
    skipped = 0
    errors = 0

    for project in projects:
        try:
            if project.newsItems.filter(created__gte=date_90days_ago).count() == 0:
                skipped = 0
                continue  # an old project with no activity recently.
            takeBacklogSnapshot(project)
            calculateStats(project)
            processed += 1
        except:
            errors += 1
            traceback.print_exc(file=sys.stdout)
            logger.error("Could not calculate project: %s" % project.slug)
    logger.info("Processed %d, Skipped %d, Errors %d" % (processed, skipped, errors))


# @app.task
# def autConvertClassicProjects():
#


@app.task
def convertClassicProject(projectId, mode, jobId):
    job = OfflineJob.objects.get(id=jobId, completed=False)
    try:
        project = classicconvert.convertClassicProject(projectId, mode)
        job.result = "Project Upgraded!"

        job2 = RebuildMovementJob(project=project, initiator=None)
        job2.save()
        rebuildStepMovements(job2.id)  # makes the step movements.

        signals.project_created.send(sender=None, project=project, user=job.owner)
        if job.owner:
            Favorite.setFavorite(1, project.id, job.owner, True)

    except Exception as e:
        logger.info("Conversion failed.")
        traceback.print_exc(file=sys.stdout)
        job.result = "Could not upgrade project."

    job.completed = True
    job.save()


@app.task
def rebuildStepMovements(jobid):
    logger.debug("Rebuilding step movements v3")
    job = RebuildMovementJob.objects.get(id=jobid)
    if RebuildMovementJob.objects.filter(project=job.project, created__gt=job.created).count() > 0:
        # We don't want to run this job multiple times at once.  So we check if a later request
        # was made.
        logger.info("Started rebuilding step movements, but there was a later job scheduled.  Aborting.")
        job.delete()
        return

    generateGenericWorkflow(job.project)

    for workflow in job.project.workflows.all():
        resetWorkflowReportData(job.project, workflow)

    previousCell = {}
    previousIteration = {}
    records = 0

    # Get rid of old step movements.
    StepMovement.objects.filter(story__project=job.project).delete()

    for cellMovement in CellMovement.objects.filter(story__project=job.project).select_related("story", "cell_to").order_by("created"):
        story = cellMovement.story
        cell = cellMovement.cell_to
        iteration = cellMovement.related_iteration
        currentCell = previousCell.get(story.id, None)
        currentIteration = previousIteration.get(story.id, None)

        if currentCell is None:
            currentSteps = []
        else:
            currentSteps = currentCell.steps.all()

        if cell is None:
            targetSteps = []
        else:
            targetSteps = cell.steps.all()

        moveStoryIntoSteps(story, currentSteps, targetSteps, cellMovement.user, cellMovement.related_iteration, cellMovement.created, False)
        previousCell[story.id] = cell
        previousIteration[story.id] = cellMovement.related_iteration
        records += 1

    logger.info("%d records processed" % records)

    resetTagReportData(job.project)
    for workflow in job.project.workflows.all():
        resetWorkflowReportData(job.project, workflow)
        filename = conditionalGenerateCellReportData(job.project, workflow)
        logger.info(u"Report data generated for %s" % workflow.name)
        if filename:
            os.unlink(filename)

    # We should also recalculate the epic stats since changing the structure of the project board
    # can alter those.
    for epic in job.project.epics.all():
        calculateEpicStats(epic, False)

    createDefaultSavedReports(job.project)
    #job.delete()
    # delete all job related to this project
    RebuildMovementJob.objects.filter(project=job.project).delete()



def _duplicateNewsFeed(sourceProject, destProject, storyMap):
    for newsitem in sourceProject.newsItems.all():
        n = NewsItem(created=newsitem.created,
                     user=newsitem.user,
                     project=destProject,
                     text=strip_tags(newsitem.text),
                     icon=newsitem.icon,
                     feed_url=newsitem.feed_url
                     )
        if newsitem.related_story:
            if newsitem.related_story_id in storyMap:
                n.related_story_id = storyMap[newsitem.related_story_id]
        n.save()
    n = NewsItem(user=None,
                 project=destProject,
                 text="Project converted to Scrumban",
                 icon="icon-trello"
                 )
    n.save()


def _duplicateEpic(epic, sourceProject, destProject, epicMap):
    e = Epic(local_id=epic.local_id,
             summary=epic.summary,
             detail=epic.detail,
             points=epic.points,
             project=destProject,
             order=epic.order,
             archived=epic.archived
             )
    if epic.parent:
        e.parent_id = epicMap[epic.parent_id]
    e.save()
    epicMap[epic.id] = e.id
    for child in epic.children.all():
        _duplicateEpic(child, sourceProject, destProject, epicMap)


def _duplicateTask(task, destStory):
    t = Task(story=destStory,
             summary=task.summary,
             assignee=task.assignee,
             order=task.order,
             tags_cache=task.tags_cache,
             status=task.status
             )
    t.save()


def _duplicateComments(sourceStory, destStory):
    for comment in StoryComment.objects.filter(story=sourceStory).order_by("date_submitted"):
        c = StoryComment(story=destStory,
                         user=comment.user,
                         date_submitted=comment.date_submitted,
                         comment=comment.comment)
        c.skip_announcements = True
        c.save()


def _duplicateTasks(sourceStory, destStory):
    for task in sourceStory.tasks.all():
        _duplicateTask(task, destStory)


def _duplicateStory(story, destProject, epicMap, backlog, current, archive, cellMap, storyMap, user):
    s = Story(rank=story.rank,
              summary=story.summary,
              local_id=story.local_id,
              detail=story.detail,
              creator=story.creator,
              created=story.created,
              modified=story.modified,
              points=story.points,
              project=destProject,
              status=1,
              category=story.category,
              extra_1=story.extra_1,
              extra_2=story.extra_2,
              extra_3=story.extra_3,
              epic=story.epic,
              task_counts=story.task_counts,
              comment_count=story.comment_count,
              has_attachment=story.has_attachment,
              has_commits=story.has_commits,
              tags_cache=story.tags_cache,
              epic_label=story.epic_label,
              assignees_cache=story.assignees_cache
              )
    s.skip_mentions = True
    if story.status == 10:
        s.iteration = archive
    else:
        oldIteration = story.iteration
        if oldIteration.isCurrent():
            s.iteration = current
            s.save()
            if story.status in cellMap:
                moveStoryOntoCell(story, cellMap[story.status], user)
                # s.cell_id = cellMap[story.status].id
            else:
                moveStoryOntoCell(story, cellMap[1], user)
                # s.cell_id = cellMap[1].id
        else:
            s.iteration = backlog

    if story.epic:
        s.epic_id = epicMap[story.epic_id]

    s.save()
    storyMap[story.id] = s.id

    for assignee in story.assignee.all():
        s.assignee.add(assignee)

    _duplicateTasks(story, s)
    _duplicateComments(story, s)


def _duplicateStories(sourceProject, destProject, epicMap, backlog, current, archive, cellMap, user):
    storyMap = {}
    storyCount = 0
    for story in sourceProject.stories.all():
        _duplicateStory(story, destProject, epicMap, backlog, current, archive, cellMap, storyMap, user)
        storyCount += 1
    logger.debug("copied %d stories" % storyCount)
    return storyMap


def _duplicateEpics(sourceProject, destProject):
    epicMap = {}
    for epic in sourceProject.epics.filter(parent=None):
        _duplicateEpic(epic, sourceProject, destProject, epicMap)
    return epicMap


def _duplicateProject(sourceProject):
    destProject = Project(
        project_type=Project.PROJECT_TYPE_KANBAN,
        name="%s (Continuous Flow)" % sourceProject.name[:70],
        creator=sourceProject.creator,
        description=sourceProject.description,
        active=True,
        private=sourceProject.private,
        use_extra_1=sourceProject.use_extra_1,
        use_extra_2=sourceProject.use_extra_2,
        use_extra_3=sourceProject.use_extra_3,
        extra_1_label=sourceProject.extra_1_label,
        extra_2_label=sourceProject.extra_2_label,
        extra_3_label=sourceProject.extra_3_label,
        task_status_names=sourceProject.task_status_names,
        status_names=sourceProject.status_names,
        card_types="Story                                                                                               ",
        point_scale_type=sourceProject.point_scale_type,
        organization=sourceProject.organization,
        category=sourceProject.category,
        categories=sourceProject.categories,
        token="".join(random.sample(string.lowercase + string.digits, 7))
    )
    slug = destProject.slug
    c = 0
    while True:
        try:
            Project.objects.get(slug=slug)
            c += 1
            slug = "%s%d" % (defaultfilters.slugify(destProject.name)[:45], c)
        except Project.DoesNotExist:
            break  # finally found a slug that doesn't exist
    destProject.slug = slug
    destProject.save()
    return destProject

