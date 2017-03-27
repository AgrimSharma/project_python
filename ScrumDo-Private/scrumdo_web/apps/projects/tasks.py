from django.conf import settings
from StringIO import StringIO
from django.core.files import File
from django.core.cache import cache
from django.contrib.auth.models import User
from apps.scrumdocelery import app
from apps.projects.models import Story, Iteration, Project, FileJob, SiteStats, Task, ProgramIncrementSchedule, ProgramIncrement
from apps.projects.calculation import onDemandCalculateVelocity, calculateReleaseStats, calculateProject
from apps.projects.access import write_access_or_403, rebuild_users_projects_cache
import apps.projects.systemrisks as systemrisks
from apps.organizations.models import OrganizationVelocityLog, Organization
import apps.organizations.tz as tz
from apps.activities.models import NewsItem
from apps.classic import models as classic_models


from apps.realtime import util as realtime_util
import apps.projects.import_export as import_export
import traceback
import sys
import mixpanel
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django_redis import get_redis_connection
from mailer import send_mail

from haystack import connections

import datetime
import signals
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)



def _storyCalcKey(storyId):
    return "calc-story-%d" % storyId


def _macroStatsCalcKey(storyId, previousReleaseId):
    if storyId is None:
        return "calc-stats-r-%d" % previousReleaseId

    return "calc-stats-%d" % storyId

def _storySolrKey(storyId):
    return "solr2-story-{0}".format(storyId)

def queueCalculateStoryRollUpTime(storyId):
    redis = get_redis_connection()
    redis.setex(_storyCalcKey(storyId), 300, True)
    calculateStoryRollUpTime.apply_async((storyId,), countdown=15)


def queueMacroStatsCalc(storyId, previousReleaseId=None):
    redis = get_redis_connection()
    redis.setex(_macroStatsCalcKey(storyId, previousReleaseId), 900, True)
    scheduledCalculateMacroStats.apply_async((storyId, previousReleaseId), countdown=3)


def queueUpdateSolr(storyId):
    # TODO: This updates our search index, we don't actually use SOLR anymore and it could use a rename
    #
    # We might have multiple calls to index a card all in a row.  When that happens,
    # we don't want to actually do it multiple times.  So we'll increment a redis key
    # and try updating the card in a few seconds.  That update decrements the counter.
    # If the counter=0, we delete the counter and do the update.
    redis = get_redis_connection()
    key = _storySolrKey(storyId)
    redis.incr(key)
    redis.expire(key, 60)
    updateSolr.apply_async((storyId,), countdown=5)

def queueUpdateStoryTagsLabel(story_Ids):
    for story_Id in story_Ids:
        resetStoryTagsLabel.apply_async((story_Id,), countdown=5)
        
def queueUpdateTaskTags(task_Ids):
    for task_Id in task_Ids:
        resetTaskTags.apply_async((task_Id,), countdown=5)

def queueRebuildTeamProjectListCache(org, team):
    for user in team.members.all():
        rebuildUserProjectListCache.apply_async((org,user), countdown=5)

def queueRebuildUserProjectListCache(org, user):
    rebuildUserProjectListCache.apply_async((org,user), countdown=5)

@app.task
def update_mixpanel():
    mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)

    today = datetime.date.today()
    mdiff = datetime.timedelta(days=-30)
    date_30days_Agoago = today + mdiff

    for organization in Organization.objects.filter(active=True).order_by("-id"):
        activity30day = NewsItem.objects.filter(created__gte=date_30days_Agoago, project__organization=organization).count()
        if activity30day == 0:
            continue  # old org with no activity in the past 30 days that we don't care about
        subscription = organization.subscription

        classicactivity30day = classic_models.NewsItem.objects.filter(created__gte=date_30days_Agoago, project__organization=organization).count()
        totalActivity = NewsItem.objects.filter(project__organization=organization).count()


        if subscription.expires is not None:
            expires = subscription.expires.strftime('%Y-%m-%d'),
        else:
            expires = ''

        email = organization.creator.email

        if totalActivity <= 3:
            activity_description = "None"
        elif totalActivity < 12:
            activity_description = "Minimal"
        elif totalActivity < 30:
            activity_description = "Adequate"
        else:
            activity_description = "Lots"

        g1 = str(organization.id % 2)
        g2 = str(organization.id % 3)
        g3 = str(organization.id % 4)
        g4 = str(organization.id % 5)
        mp.people_set_once(organization.slug,
                           {'Test Group 1 s': g1,
                            'Test Group 2 s': g2,
                            'Test Group 3 s': g3,
                            'Test Group 4 s': g4})

        mp.people_set(organization.slug, {
            'name':  organization.name,
            'slug':  organization.slug,
            'creator': organization.creator.email,
            '30 day activity': activity30day,
            '30 day classic activity': classicactivity30day,
            'total activity': totalActivity,
            'activity description': activity_description,
            'dashboard': "https://app.scrumdo.com/organization/%s/dashboard" % organization.slug,
            'classic dashboard': "https://www.scrumdo.com/organization/%s/dashboard" % organization.slug,
            'plan': subscription.planName(),
            'price': subscription.planPrice(),
            'projects': subscription.projectsUsed(),
            'classic projects': organization.classic_projects.filter(active=True).count(),
            'users': subscription.usersUsed(),
            'storage': subscription.storageUsed(),
            'is trial': subscription.is_trial,
            'paid': subscription.total_revenue > 0 and subscription.active,
            'expires': expires,
            'total revenue': float(subscription.total_revenue),
            'trial month': organization.created.strftime('%Y-%m'),
            'trial week': organization.created.strftime('%Y-%U'),
            'created': organization.created.strftime('%Y-%m-%dT%H:%M:%S'),
            'private projects': organization.projects.filter(active=True, private=True).count(),
            'private projects allowed': organization.allow_personal,
            'timezone': organization.timezone,
            'source': organization.source,
            '$email': email

        })
        logger.info(u'Logged %s' % organization.slug)


@app.task
def site_stats():
    stats = SiteStats()
    stats.project_count = Project.objects.count() + classic_models.Project.objects.count()
    stats.user_count = User.objects.count()
    stats.story_count = Story.objects.exclude(iteration__iteration_type=Iteration.ITERATION_TRASH).count() + classic_models.Story.objects.count()
    stats.save()


@app.task
def update_solr_1_hour():
    """Updates all cards modified in the past hour."""
    # TODO: This updates our search index, we don't actually use SOLR anymore and it could use a rename
    d = datetime.datetime.now() - datetime.timedelta(hours=1)
    index = connections['default'].get_unified_index().get_index(Story)
    for story in Story.objects.filter(modified__gt=d):
        index.update_object(story)


@app.task
def updateSolr(storyId):
    # TODO: This updates our search index, we don't actually use SOLR anymore and it could use a rename
    redis = get_redis_connection()
    key = _storySolrKey(storyId)
    v = redis.decr(key)
    if v <= 0:
        redis.delete(key)
        try:
            # logger.debug('Indexing %d' % storyId)
            story = Story.objects.get(id=storyId)

            index = connections['default'].get_unified_index().get_index(Story)
            index.update_object(story)
        except Story.DoesNotExist:
            return

@app.task
def scheduledCalculateMacroStats(storyId, previousReleaseId=None):
    """ Calculates stats bigger than a story, right now that's just the release stats.
    :param storyId:  The story that was modified
    :param previousReleaseId:  The previous releaseId for that story
    """
    redis = get_redis_connection()
    if redis.delete(_macroStatsCalcKey(storyId, previousReleaseId)) == 1:
        try:
            story = Story.objects.get(id=storyId)
            try:
                previousRelease = Story.objects.get(id=previousReleaseId)
                calculateReleaseStats(previousRelease)
            except Story.DoesNotExist:
                previousRelease = None  # did not have a previous release, or it's deleted

            currentRelease = story.release
            if currentRelease != previousRelease and currentRelease:
                # Only need to calcualte current release if the release for the story has changed.
                calculateReleaseStats(currentRelease)

        except Story.DoesNotExist:
            # Story may have since been deleted, if there was a previous release, we should
            # recalculate it so that story is removed from it.
            if previousReleaseId != None:
                previousRelease = Story.objects.get(id=previousReleaseId)
                calculateReleaseStats(previousRelease)



@app.task
def calculateStoryRollUpTime(storyId):
    redis = get_redis_connection()
    if redis.delete(_storyCalcKey(storyId)) == 1:
        total = 0
        story = Story.objects.get(id=storyId)
        for task in story.tasks.all():
            total += task.estimated_minutes
        if story.task_minutes != total:
            story.task_minutes = total
            story.save()


@app.task
def sendStoryAddedSignals(storyID, userID):
    try:        
        story = Story.objects.get(id=storyID)
        user = User.objects.get(id=userID)
                        
        story.skip_haystack = False
        story.resetCounts()

        write_access_or_403(story.project, user)
        # We have a weird bug where the wrong user shows up in a newsfeed.  This should catch it,
        # I hope, so we can figure it out why it is happening.
                
        signals.story_created.send(sender=story, story=story, user=user)

        realtime_util.send_story_created(story.project, story)

        onDemandCalculateVelocity(story.project)

    except Story.DoesNotExist:
        pass # sometimes, the story is deleted between being edited and getting here.  no big deal.
    except:
        e = sys.exc_info()[1]        
        stack = "\n".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        body = "%s %s %s" % (str(storyID), str(userID), stack)
        send_mail('Story index error', body, settings.DEFAULT_FROM_EMAIL, ["marc.hughes@gmail.com"], fail_silently=True)
    

@app.task
def indexStory(storyID):
    try:
        story = Story.objects.get(id=storyID)
        index = connections['default'].get_unified_index().get_index(Story)
        index.update_object(story)
    except Story.DoesNotExist:
        pass  # deleted before we got here?
    except:
        e = sys.exc_info()[1]        
        stack = "\n".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        send_mail('Story index error', stack, settings.DEFAULT_FROM_EMAIL, ["marc.hughes@gmail.com"], fail_silently=True)


@app.task
def exportIteration(iteration_id, organization_slug, job_id, format, file_name ):
    iteration = Iteration.objects.get(Q(id=iteration_id), ~Q(iteration_type=Iteration.ITERATION_TRASH))

    job = FileJob.objects.get(id = job_id)
    xlsf = import_export.exportIteration(iteration, organization_slug, format, file_name)
    job.attachment_file.save("%s.%s" % (file_name, format.lower()), xlsf)
    job.completed = True
    job.save()

@app.task
def exportProject(project_id, organization_slug, job_id, file_name):
    project = Project.objects.get(id=project_id)

    xlsf = File(StringIO())
    job = FileJob.objects.get(id = job_id)
    import_export.exportProject(project, organization_slug, file_name)\
                 .save(xlsf); xlsf.size = xlsf.tell()
    job.attachment_file.save("%s.xls" % file_name, xlsf)
    job.completed = True
    job.save()
    
@app.task
def exportTeamPlanning(iteration_id, team_project_id, organization_slug, job_id, file_name ):
    iteration = Iteration.objects.get(Q(id=iteration_id), ~Q(iteration_type=Iteration.ITERATION_TRASH))
    tean_project = Project.objects.get(id=team_project_id)
    
    xlsf = File(StringIO())
    job = FileJob.objects.get(id = job_id)
    import_export.exportTeamPlanning(iteration, tean_project, organization_slug, file_name)\
                        .save(xlsf); xlsf.size = xlsf.tell()
    job.attachment_file.save("%s.xls" % file_name, xlsf)
    job.completed = True
    job.save()

@app.task
def record_all_burnup_charts():
    today = datetime.date.today()
    mdiff = datetime.timedelta(days=-90)
    date_90days_ago = today + mdiff
    OrganizationVelocityLog.objects.filter(created__lte=date_90days_ago).delete()

    for project in Project.objects.filter(project_type=Project.PROJECT_TYPE_PORTFOLIO):
        for story in project.stories.all():
            calculateReleaseStats(story, False)

    processed = 0
    skipped = 0
    errors = 0

    projects = Project.objects.filter(active=True, organization__active=True)
    for project in projects:
        try:
            if project.newsItems.filter(created__gte=date_90days_ago).count() == 0:
                skipped += 1
                continue  # an old project with no activity recently.

            calculateProject(project)
            processed += 1
        except:
            errors += 1
            logger.error("Could not calculate project %s" % project.slug)
    logger.info("Processed %d, Skipped %d, Errors %d" % (processed, skipped, errors))

@app.task
def updateProjectIndexes(project_slug):
    project = Project.objects.get(slug=project_slug)
    backend = connections['default'].get_backend()
    index = connections['default'].get_unified_index().get_index(Story)

    indexname = settings.HAYSTACK_CONNECTIONS['default']['INDEX_NAME']

    # First, clear out existing index data in case we have inconsistent data in the index.
    existing = backend.conn.search(index=indexname,
                                   size=5000,
                                   doc_type='modelresult',
                                   fields="id",
                                   q="project_id:%d" % project.id)

    ids = [{"delete": {"_index": indexname, "_type": "modelresult", "_id": h['_id']}}
           for h in existing['hits']["hits"]]

    if len(ids) > 0:
        backend.conn.bulk(ids, index=indexname)

    backend.update(index, Story.objects.filter(project__slug=project_slug).exclude(iteration__iteration_type=Iteration.ITERATION_TRASH).order_by("-id") \
                        .select_related("release", "epic", "creator", "project", "cell") \
                        .prefetch_related('assignee', 'labels', 'tasks', 'comments'))

    logger.info(u"Completed indexing %s" % project.slug)

@app.task
def resetStoryTagsLabel(story_id):
    story = Story.objects.get(id=story_id)
    story.resetTagsCache()
    story.save()
    
    labels = [{'name':label.name, 'color':label.color, 'id':label.id} for label in story.labels.all()]
    props = {'tags_list':story.story_tags_array(),'tags_cache':story.tags_cache,'tags':story.tags_cache, 'labels':labels}
    realtime_util.send_story_patch(story.project, story, props)
    queueUpdateSolr(story_id)

@app.task
def resetTaskTags(task_id):
    task = Task.objects.get(id=task_id)
    task.resetTagsCache()
    task.save()
    
    realtime_util.send_task_modified(task.story, task)

@app.task
def rebuildUserProjectListCache(org, user):
    rebuild_users_projects_cache(org, user)

@app.task
def rebuildIterationRisks(project, iteration_id):
    iteration = Iteration.objects.get(id=iteration_id)
    key = systemrisks.cacheKey(project, iteration, "iterationwip")
    cache.delete(key)
    systemrisks.iterationRisks(project, iteration)

@app.task
def rebuildIncrementRisks(team, iteration_id):
    iteration = Iteration.objects.get(id=iteration_id)
    project = iteration.project
    key = systemrisks.cacheKey(project, iteration, "incrementwip")
    cache.delete(key)
    systemrisks.incrementWipRisks(project, iteration)

@app.task
def rebuildCellHeaderRisks(project, iteration_id=None):
    if iteration_id is not None:
        iteration = Iteration.objects.get(id=iteration_id)
        key = systemrisks.cacheKey(project, iteration, "cellheaderwip")
        cache.delete(key)
        systemrisks.cellHeaderRisks(project, iteration)
    else:
        systemrisks.updateProjectRisks(project)

@app.task
def rebuildAgingRisks(project, iteration_id):
    iteration = Iteration.objects.get(id=iteration_id)
    key = systemrisks.cacheKey(project, iteration, "aging")
    cache.delete(key)
    systemrisks.agingRisks(project, iteration)

@app.task
def rebuildDueDateRisks(project, iteration_id):
    iteration = Iteration.objects.get(id=iteration_id)
    key = systemrisks.cacheKey(project, iteration, "duedate")
    cache.delete(key)
    systemrisks.dueDateRisks(project, iteration)

@app.task
def rebuildProjectsDuedateRisks():
    projects = Project.objects.filter(Q(portfolio_level__isnull=False) | Q(project_type=2), active=True)
    for project in projects:
        for iteration in project.iterations.filter(~Q(iteration_type = Iteration.ITERATION_WORK)):
            key = systemrisks.cacheKey(project, iteration, "duedate")
            cache.delete(key)
            systemrisks.dueDateRisks(project, iteration)

@app.task
def rebuildProjectsAgingRisks():
    projects = Project.objects.filter(Q(portfolio_level__isnull=False) | Q(project_type=2), active=True)
    for project in projects:
        for iteration in project.iterations.filter(~Q(iteration_type = Iteration.ITERATION_WORK)):
            key = systemrisks.cacheKey(project, iteration, "aging")
            cache.delete(key)
            systemrisks.agingRisks(project, iteration)

@app.task
def purgeIncrementSchedules():
    schedules = ProgramIncrementSchedule.objects.filter(iterations__isnull = True)
    for schedule in schedules:
        schedule.delete()

@app.task
def rebuildStoryRisks(project, iteration_id):
    rebuildCellHeaderRisks(project, iteration_id)
    rebuildIterationRisks(project, iteration_id)
    rebuildIncrementRisks(project, iteration_id)
    rebuildDueDateRisks(project, iteration_id)

@app.task
def auto_archive_past_iterations():
    projects = Project.objects.filter(active=True)
    for project in projects:
        auto_archive_days = project.auto_archive_iterations
        if auto_archive_days is not None and auto_archive_days > 0 and auto_archive_days != 999:
            today = tz.today(project.organization)
            past_date = today-datetime.timedelta(days=auto_archive_days)
            past_iterations = project.iterations.filter(hidden=False, end_date__isnull=False, end_date__lt=past_date)

            for iteration in past_iterations:
                clear_iteration_schedules(iteration)

                iteration.hidden = True
                iteration.save()

def clear_iteration_schedules(iteration):
    """
    will remove the iteration from parent iteration schedules
    will remove child iteration from this iteration schedules
    """
    # remove its child Iterations from its Increment Schedules
    try:
        increment = ProgramIncrement.objects.get(iteration_id=iteration.id)
        schedules = increment.schedule.all()

        for schedule in schedules:
            schedule.delete()

    except ObjectDoesNotExist:
        # no increment found for this Iteration
        pass
    # remove it from parent Iteration Schedules
    iteration.program_increment_schedule.clear()