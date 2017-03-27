from Pubnub import Pubnub

from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.conf import settings
from django.dispatch import receiver
from django.db.models import Count, Sum, Q
from django.db import IntegrityError
from django.utils.html import strip_tags
from django.core.cache import cache

from apps.projects.models import Iteration, Project, Label, Story, StoryTag, StoryTagging, StoryBlocker, Epic, TeamIterationWIPLimit, ProgramIncrement
from apps.projects.org_backlog import set_project_parents
from apps.projects.util import generateProjectSlug, generateDeletedProjectPrefix, generateProjectPrefix, duplicatePrefix
from apps.projects.limits import org_project_limit, personal_project_limit, org_kanban
import apps.projects.tasks as projects_tasks
import apps.projects.systemrisks as systemrisks

import apps.projects.signals as signals

from apps.organizations.models import Organization

import apps.kanban.managers as kanban_managers
from apps.kanban.util import getChildEpics
from apps.kanban.models import BoardCell, Policy, KanbanStat
from apps.realtime.util import send_project_message

from apps.github_integration.models import GithubCredentials, GithubBinding, GithubLog
from apps.github_integration import utils as github_utils
from apps.favorites.models import Favorite
from apps.flowdock.models import FlowdockMapping, FlowdockUser
from apps.hipchat.models import HipChatMapping
from apps.slack.models import SlackMapping
from apps.realtime import util as realtime_util

from haystack import connections

import portfolio_managers

import hashlib
import datetime
import requests
from collections import defaultdict

import logging

logger = logging.getLogger(__name__)

pubnub = Pubnub(
    settings.PUBNUB_PUB_KEY,
    settings.PUBNUB_SUB_KEY,
    settings.PUBNUB_SEC_KEY,
    False
)


@receiver(pre_delete, sender=Story)
def remove_from_index(sender, instance, **kwargs):
    try:
        index = connections['default'].get_unified_index().get_index(sender)
        index.remove_object(instance)
    except:
        logger.error("Could not remove card from index on delete.")


def _remove_project_extras(project):
    #github
    credentials = GithubCredentials.objects.filter(project=project)
    gitBindings = GithubBinding.objects.filter(project=project)
    gitLogs = GithubLog.objects.filter(project=project)
    gitLogs.delete()
    for gbinding in gitBindings:
        github_utils.removeCallbacks(credentials[0].oauth_token, gbinding, project)
        gbinding.delete()

    #flowdock
    fdMappings = FlowdockMapping.objects.filter(project=project)
    flowdockUser = FlowdockUser.objects.filter(project=project)
    for fMapping in fdMappings:
        url = "https://api.flowdock.com/flows/{orgId}/{flowId}/sources/{sourceId}?access_token={token}"\
            .format(sourceId=fMapping.source_id, orgId=fMapping.org_slug, flowId=fMapping.flow_slug, token=flowdockUser[0].oauth_token)
        r = requests.delete(url)
        fMapping.delete()

    #hipchat
    hMapping = HipChatMapping.objects.filter(project=project)
    hMapping.delete()

    #slack
    sMapping = SlackMapping.objects.filter(project=project)
    sMapping.delete()


def _get_deleted_projects_org():
    try:
        organization = Organization.objects.get(slug="scrumdo_deleted_projects")
    except Organization.DoesNotExist:
        organization = Organization(name='ScrumDo Deleted Projects', slug='scrumdo_deleted_projects')
        user = User.objects.get(username='mhughes')
        organization.creator = user
        organization.save()
    return organization


def delete_project(project):
    #remove this project from all teams
    for team in project.organization.teams.all():
        if project in team.projects.all():
            team.projects.remove(project)
            rebuild_project_teams_cache_fn(project.organization, team)

    _remove_project_extras(project)
    portfolio_managers.rebuild_portfolio_nonroot_teams_cache(project)
    portfolio_managers.remove_project_from_portfolio(project)

    if project.project_type == 2:
        # A portfolio root project!
        portfolio_managers.rebuild_portfolio_projects_teams_cache(project)
        portfolio_managers.delete_portfolio(project)
    old_org = project.organization
    old_creator = project.creator

    organization = _get_deleted_projects_org()
    project.organization = organization
    project.active = False
    project.abandoned = True
    project.parents.clear()
    if not duplicatePrefix(project, organization):
        project.save()
    else:
        project.prefix = generateDeletedProjectPrefix(project)
        project.save()
    
    #update user project list cache
    projects_tasks.queueRebuildUserProjectListCache(old_org, old_creator)
    

    return project

def archive_project(project):
    if project.project_type == 2:
        portfolio_managers.archive_portfolio_projects(project)

    project.active = False
    project.save()

def activate_project(project, remove_from_portfolio = None):
    if project.project_type == 2:
        portfolio_managers.activate_portfolio_projects(project)
    
    if remove_from_portfolio is not None:
        portfolio_managers.remove_project_from_portfolio(project)

    project.active = True
    project.save()

def add_project_to_organization(project, organization):
    logger.info("Adding project %s to organization %s" % (project.slug, organization.slug))
    project.organization = organization
    project.save()


def create_project(name,
                   organization,
                   creator,
                   personal,
                   team_ids,
                   project_type=Project.PROJECT_TYPE_KANBAN,
                   clone_project_id=0,
                   parent_ids=(),
                   work_item_name="Card",
                   folder_item_name="Epic",
                   icon="fa-cube"
                   ):
    project = Project(name=name,
                      organization=organization,
                      creator=creator,
                      personal=personal,
                      project_type=project_type,
                      work_item_name=work_item_name,
                      folder_item_name=folder_item_name,
                      icon=icon)

    slug = generateProjectSlug(project.name)
    prefix = generateProjectPrefix(project)
    project.slug = slug
    project.prefix = prefix
    
    if organization:
        creationAllowed = org_project_limit.increaseAllowed(organization=organization)
        if project.personal and not organization.allow_personal:
            creationAllowed = False
            # Can't make personal projects.
    else:
        creationAllowed = personal_project_limit.increaseAllowed(user=creator)

    if creationAllowed:

        try:
            project.save()
        except IntegrityError as e:
            project.prefix = generateProjectPrefix(project, True)
            project.save()


        if parent_ids is not None:
            parents = organization.projects.filter(id__in=parent_ids)
            set_project_parents(project, parents)


        if not personal:
            if (parent_ids is None or len(parent_ids) == 0) and project.project_type != Project.PROJECT_TYPE_BACKLOG_ONLY:
                # prevent portfolio and Backlog Project to be set as Favorite
                Favorite.setFavorite(1, project.id, creator, True)
            for team_id in team_ids:
                team = organization.teams.get(id=team_id)
                team.projects.add(project)


        add_project_to_organization(project, organization)

        if project.project_type == Project.PROJECT_TYPE_SCRUM:
            initScrumProject(project)
        elif project.project_type == Project.PROJECT_TYPE_KANBAN:
            kanban_managers.initKanbanProject(project)
        elif project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            kanban_managers.initBacklogProject(project)
        else:
            kanban_managers.initPortfolioProject(project)

        if not personal and clone_project_id is not None:
            clone_project_id = int(clone_project_id)
            if clone_project_id != 0:
                other = Project.objects.get(id=clone_project_id)
                if (other.organization == project.organization):
                    kanban_managers.copyProject(other, project)
                    kanban_managers.copyProjectSettings(other, project)

        signals.project_created.send(sender=project, project=project, user=creator)
        # update projects list cache for current user
        projects_tasks.queueRebuildUserProjectListCache(organization, creator)
        return project
    return None







def transferLabels(story, toProject):
    """Whem moving a card from one projct to another, we can't keep the same set of labels
       because those labels point to the old project.  We need to either use existing labels in the
       destination project (preferred), or we need to create a new label to use.  This method
       handles that logic."""
    newLabels = []
    for label in story.labels.all():
        try:
            newLabels.append(toProject.labels.get(name=label.name))
        except Label.DoesNotExist:
            l = Label(name=label.name, color=label.color, project=toProject)
            l.save()
            newLabels.append(l)
    story.labels = newLabels

def transferTags(story, toProject):
    """Whem moving a card from one projct to another, we can't keep the same set of tags
       because those tags point to the old project.  We need to either use existing tags in the
       destination project (preferred), or we need to create a new tag to use.  This method
       handles that logic."""
    newTags = []
    for tag in story.story_tags.all():
        try:
            newTags.append(toProject.tags.get(name=tag.name))
        except StoryTag.MultipleObjectsReturned:
            newTags.append(toProject.tags.filter(name=tag.name)[0])
        except StoryTag.DoesNotExist:
            tag = StoryTag(name=tag.name, project=toProject)
            tag.save()
            newTags.append(tag)
    StoryTagging.objects.filter(story=story).delete()
    for newTag in newTags:
        StoryTagging(tag=newTag, story=story).save()

def transferBlockers(story, toProject):
    """Whem moving a card from one projct to another, we also have to
       move the story existing blockers to destination project, for this
       we will just update the project_id of blocker to dest. project
    """
    for blocker in story.blocked_instances.all():
        blocker.project = toProject
        blocker.save()

def transferRelease(story, toProject):
    """Whem moving a card from one projct to another, we also have to
       update the card release if card is moved to a parent project
       of that relase project  
    """
    if story.release is None:
        return
    releaseProject = story.release.project
    if releaseProject not in toProject.parents.all() and toProject.project_type != Project.PROJECT_TYPE_BACKLOG_ONLY:
        story.release = None
    else:
        # story is moved to same level project so just leave as it is
        pass

def setRelativeRank(story, iteration, relativeRank):
    before_id = -1
    after_id = -1
    stories = list(iteration.stories.exclude(id=story.id).order_by("rank"))
    index = int(len(stories) * relativeRank / 100)
    if index > 0:
        logger.debug("Before: %s" % stories[index - 1].summary)
        before_id = stories[index - 1].id

    if index < (len(stories) - 1):
        logger.debug("After: %s" % stories[index].summary)
        after_id = stories[index].id

    logger.debug(
        "setRelativeRank len: %d rel: %d ind: %d before: %s after: %s" %
        (len(stories), relativeRank, index, before_id, after_id))

    return reorderStory(story, before_id, after_id, iteration)


def getReleaseProject(organization, user):
    try:
        releaseProject = Project.objects.get(organization=organization, project_type=Project.PROJECT_TYPE_PORTFOLIO)
    except Project.MultipleObjectsReturned:
        releaseProject = Project.objects.filter(organization=organization, project_type=Project.PROJECT_TYPE_PORTFOLIO)[0]
    except Project.DoesNotExist:
        releaseProject = Project(name=u"%s Releases" % (organization.name,),organization=organization, project_type=Project.PROJECT_TYPE_PORTFOLIO)
        releaseProject.slug = generateProjectSlug(releaseProject.name)
        releaseProject.prefix = generateProjectPrefix(releaseProject)
        releaseProject.creator = user
        releaseProject.save()
        initReleaseProject(releaseProject)
        releaseProject.save()
    return releaseProject


def enablePortfolioMode(organization, user):
    organization.planning_mode = Organization.PLANNING_MODES.portfolio
    releaseProject = getReleaseProject(organization, user)
    for project in organization.projects.filter(project_type=Project.PROJECT_TYPE_KANBAN, parents=None, active=True):
        project.parents.add(releaseProject)
        project.save()


def enableReleasesMode(organization, user):
    organization.planning_mode = Organization.PLANNING_MODES.release

    # First make sure there is a release project
    releaseProject = getReleaseProject(organization, user)

    # Then assign all projects in the organization to use that release project.
    for project in organization.projects.filter(project_type=Project.PROJECT_TYPE_KANBAN, parents=None, active=True):
        project.parents.add(releaseProject)
        project.save()


def initReleaseProject(project):
    Label(name='Product', color=0x34CC73, project=project).save()
    Label(name='Feature', color=0x9A59B5, project=project).save()
    Label(name='Initiative', color=0xBF392B, project=project).save()

    iteration = Iteration(name='Backlog',
                                  detail='',
                                  default_iteration=True,
                                  project=project,
                                  iteration_type=Iteration.ITERATION_BACKLOG)
    iteration.save()

    iteration = Iteration(name='In Progress',
                                  detail='',
                                  default_iteration=False,
                                  project=project,
                                  iteration_type=Iteration.ITERATION_WORK)
    iteration.save()

    iteration = Iteration(name='Archive',
                                  detail='',
                                  default_iteration=False,
                                  project=project,
                                  iteration_type=Iteration.ITERATION_ARCHIVE)

    rows = [{'name':''}]
    columns = [ {'name': 'Planning', 'color': "#747E89", 'style': 0, 'sub': ['Doing', 'Done']},
                {'name': 'In Progress', 'color': "#3898DB", 'style': 9, 'sub': ['Doing', 'Done']},
                {'name': 'Done', 'color': "#34CC73", 'style': 0, 'sub': ['Doing', 'Done']}]
    kanban_managers.wizard(project, {'rows': rows, 'columns': columns}, True)

    iteration.save()


def initScrumProject(project):
    # And lets make the default backlog iteration with no start/end dates.
    default_iteration = Iteration( name='Backlog', detail='', default_iteration=True, project=project, iteration_type=Iteration.ITERATION_BACKLOG)
    default_iteration.save()
    project.iterations.add(default_iteration)



def broadcastIterationCounts(project):
    iterations = Iteration.objects.filter(project=project).exclude(iteration_type = Iteration.ITERATION_TRASH).annotate(story_count=Count('stories'))
    payload = {}
    message = {'client':'SERVER', 'type':'iterationCounts', 'payload':payload}

    for iteration in iterations:
        payload[iteration.id] = iteration.story_count

    send_project_message(project, message)


def reorderStory(story, before_id, after_id, iteration, field_name="rank"):
    """Reorders a story between two others.
    Returnes a tupple
      element 0: true if we had to change other stories ranks
      element 1: array of stories & ranks"""
    story_rank_before = 0
    story_rank_after = 99999999  # max value of the DB field
    modified = []

    # If there is a story that should be before this one, grab it's rank
    try:
        story_before = Story.objects.get(id=before_id)
        story_rank_before = story_before.__dict__[field_name]
    except:
        pass

    # If  there is a story that should be after this one, grab it's rank.
    try:
        story_after = Story.objects.get(id=after_id)
        story_rank_after = story_after.__dict__[field_name]
    except:
        pass

    # If the story is between them, don't do anything! "do no harm"
    current_rank = story.__dict__[field_name]
    if current_rank > story_rank_before and current_rank < story_rank_after:
        return (False, modified)

    diff = abs(story_rank_after - story_rank_before)
    # logger.debug("Before %d , after %d, diff %d" % (story_rank_after, story_rank_before, diff) )
    try:
        if diff > 1:
            # It fits between them.. try to find a slot not already occupied
            target_rank = int(round(diff / 2) + story_rank_before)
            try:
                Story.objects.get(iteration=iteration, rank=target_rank)
                logger.debug(
                    "Found target rank, but a story was already there.")
            except Story.DoesNotExist:
                # A story with that rank didn't exist, so it fits.
                story.__dict__[field_name] = target_rank
                modified.append([story.id, target_rank])
                logger.debug(
                    "Reordering fit %d %d %d" %
                    (story_rank_before,
                     story.__dict__[field_name],
                        story_rank_after))
                return False, modified
    except:
        # do an emergency re-order below if things are falling out of bounds.
        pass

    # It doesn't fit!  reorder everything!
    stories = iteration.stories.all().order_by(field_name)

    rank = 50000
    for other_story in stories:
        if other_story == story:
            continue
        if other_story.__dict__[field_name] == story_rank_after:
            # We should always have a story_rank_after if we get here.
            story.__dict__[field_name] = rank
            modified.append([story.id, rank])
            rank += 10000
        other_story.__dict__[field_name] = rank
        modified.append([other_story.id, rank])
        other_story.skip_haystack = True
        other_story.skip_announcements = True
        other_story.save()
        rank += 10000

    if story_rank_after == 999999:
        # weird case for when we run-off the max rank
        story.rank = rank
        story.save()

    return True, modified

def create_blocker(story, data, user):
    blocker = StoryBlocker(card=story, project=story.project, blocker=user)
    blocker.reason = data["reason"]
    blocker.external = data["external"]
    blocker.blocked_date = datetime.datetime.now()
    blocker.save()
    return blocker

def remove_blocker(blocker, resolution, user):
    blocker.resolution = resolution
    blocker.unblocker = user
    blocker.unblocked_date = datetime.datetime.now()
    blocker.resolved = 1
    blocker.save()
    return blocker

def blocker_report_data(project,
                        assignee,
                        tag,
                        label,
                        epic,
                        startdate,
                        enddate,
                        iteration
                        ):
    """
    First we will filter the blockers based on query recieved,
    then group blockers by reason and create two list:
    one for 9 top most common blockers and 2nd for other blockers
    """
    blockers = StoryBlocker.objects.filter(project=project).select_related("card__iteration__name")

    blockers = _filter_blockers(blockers, assignee, tag, label, epic, startdate, enddate, iteration)

    blockers = _group_by_reason(blockers)
    return {'blockers': blockers}

    

def blocker_freq_data(project,
                    assignee,
                    tag,
                    label,
                    epic,
                    startdate,
                    enddate,
                    iteration
                    ):
    blockers = StoryBlocker.objects.filter(project=project).select_related("card__iteration__name")
        
    blockers = _filter_blockers(blockers, assignee, tag, label, epic, startdate, enddate, iteration)
    return blockers
    
def _filter_blockers(blockers, 
                    assignee=None, tag=None, 
                    label=None, epic=None, 
                    startdate=None, enddate=None, 
                    iteration='ALL'):

    if startdate is not None:
        startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
        blockers = blockers.filter(blocked_date__gte=startdate)
    if enddate is not None:
        enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d")
        enddate = enddate + datetime.timedelta(days=1)
        blockers = blockers.filter(blocked_date__lt=enddate)
    if assignee is not None and assignee != "":
        blockers = blockers.filter(card__assignee__id__in=assignee.split(","))
    if tag is not None:
        blockers = blockers.filter(card__story_tags__tag__name=tag)
    if label is not None:
        blockers = blockers.filter(card__labels__id=label)
    if epic is not None:
        # Generate a list of sub epics.
        epics = getChildEpics(Epic.objects.get(id=epic))
        blockers = blockers.filter(card__epic_id__in=epics)
    if iteration != 'ALL':
        blockers = blockers.filter(card__iteration_id=iteration)
    return blockers

def _group_by_reason(items, categorized = True):
    v = defaultdict(list)
    blockers = []
    for blocker in items:
        reason = "%s (%s)" % (blocker.reason, "External" if blocker.external else "Internal")
        v[reason].append(blocker)
    blockers = [{'reason': k, 'blockers': v[k], 'total':len(v[k]), 'external': _is_external_blocker(v[k]),
        'age': _blockers_age(v[k])} for k in sorted(v, key=lambda k: len(v[k]), reverse=True)]
    if categorized == False:
        return blockers
    common = blockers[:25]
    others = blockers[25:]
    return {'common': common, 'others': others}

def _blockers_age(blockers):
    age = 0
    average = 0
    for blocker in blockers:
       age += blocker.age
    return {'total':age, 'average': age/len(blockers)}

def _is_external_blocker(blockers):
    external = False
    for blocker in blockers:
        if blocker.external is True:
            external = True
    return external

def story_by_blocker_reason(project, reason, assignee, tag, label, epic, startdate, enddate, iteration):
    results = []
    keys = []
    if reason is not None:
        v = defaultdict(list)
        blockers = StoryBlocker.objects.filter(project=project, reason=reason)
        blockers = _filter_blockers(blockers, assignee, tag, label, epic, startdate, enddate, iteration)

        for blocker in blockers:
            if blocker.card.id not in keys:
                keys.append(blocker.card.id)
                results.append(blocker)
    return results


def blocker_report_list_data(project,
                        assignee,
                        tag,
                        label,
                        epic,
                        startdate,
                        enddate,
                        iteration
                        ):
    blockers = StoryBlocker.objects.filter(project=project).order_by("blocked_date").select_related("card__iteration__name")
    blockers = _filter_blockers(blockers, assignee, tag, label, epic, startdate, enddate, iteration)
    return blockers


def remove_project_from_teams(project):
    for team in project.organization.teams.all():
        if project in team.projects.all():
            team.projects.remove(project)
            rebuild_project_teams_cache_fn(project.organization, team)
    portfolio_managers.rebuild_portfolio_nonroot_teams_cache(project)


def delete_iteration(project, iteration, request):
    defaultIteration = project.iterations.filter(iteration_type=Iteration.ITERATION_BACKLOG)[0]

    signals.iteration_deleted.send(sender=request, iteration=iteration, user=request.user)

    for story in iteration.stories.all():
        story.iteration = defaultIteration
        kanban_managers.moveStoryOntoCell(story, None, request.user)
        signals.story_moved.send(sender=request, story=story, user=request.user,
                                 diffs={"iteration_id": [iteration.id, defaultIteration.id]})
        story.save()

    iteration.delete()

def rebuild_project_teams_cache(project):
    # rebuild projects cache for team users
    if project.project_type != Project.PROJECT_TYPE_PORTFOLIO:
        if project.portfolio_level is not None:
            # this is a portfolio project, so update cache 
            # for all teams belongs to all project in potfolio
            portfolio_managers.rebuild_portfolio_nonroot_teams_cache(project)
        else:
            teams = project.organization.teams.filter(projects=project)
            for team in teams:
                rebuild_project_teams_cache_fn(project.organization, team)
    else:
        portfolio_managers.rebuild_portfolio_projects_teams_cache(project)

def rebuild_staff_teams_cache(org):
    staff_users = org.staff_members()
    for user in staff_users:
        projects_tasks.queueRebuildUserProjectListCache(org, user)

def rebuild_project_teams_cache_fn(org, team):
    projects_tasks.queueRebuildTeamProjectListCache(org, team)

def rebuild_project_owner_cache(organization, user):
    projects_tasks.queueRebuildUserProjectListCache(organization, user)


def get_child_increments(project_slug, level_number, parent_increments):
    """
    return child ProgramIncrements for a project in Portfolio 
    w.r.t given parentIncrement and its level  
    """
    project = Project.objects.get(slug=project_slug)
    portfolio_level = project.portfolio_level.level_number
    all_level = project.portfolio_level.portfolio.levels.all().count()
    # if its level 1 then return root Increment
    if portfolio_level == 1:
        return parent_increments

    child_increments = ProgramIncrement.objects.filter(iteration__program_increment_schedule__increment__in = parent_increments)
    if level_number == portfolio_level-1:
        return child_increments
    else:
        level_number += 1
        return get_child_increments(project_slug, level_number, child_increments)

def get_child_releases(project_slug, level_number, parent_releases):
    """
    return child Releases for a project in Portfolio   
    """
    project = Project.objects.get(slug=project_slug)
    portfolio_level = project.portfolio_level.level_number

    # if its level 1 then return root Increment
    if portfolio_level == 1:
        return parent_releases
    child_releases = Story.objects.filter(release__in = parent_releases)
    if level_number == portfolio_level-1:
        return child_releases
    else:
        level_number += 1
        return get_child_releases(project_slug, level_number, child_releases)

def get_level_releases(portfolio_level, level_number, parent_releases):
    """
    return child Releases for a portfolio_level in Portfolio   
    """
     # if its level 1 then return root Increment
    if portfolio_level == 1:
        return parent_releases
    child_releases = Story.objects.filter(release__in = parent_releases)
    if level_number == portfolio_level-1:
        return child_releases
    else:
        level_number += 1
        return get_level_releases(portfolio_level, level_number, child_releases)

def get_level_increments(portfolio_level, level_number, parent_increments):
    """
    return child ProgramIncrements for a portfolio_level in Portfolio 
    w.r.t given parentIncrement and its level  
    """
    # if its level 1 then return root Increment
    if portfolio_level == 1:
        return parent_increments

    child_increments = ProgramIncrement.objects.filter(iteration__program_increment_schedule__increment__in = parent_increments)
    if level_number == portfolio_level-1:
        return child_increments
    else:
        level_number += 1
        return get_level_increments(portfolio_level, level_number, child_increments)


def get_kanban_stats(project):
    CACHE_SECONDS = 43200 # one day long
    cache_key = "project_kstats_%d" % (project.id)
    cached_value = cache.get(cache_key)
    
    if not cached_value:
        story_count = project.stories.exclude(iteration__iteration_type = Iteration.ITERATION_TRASH).count()
        stories_completed = project.stories.filter(cell__time_type=BoardCell.DONE_TIME).count() + \
                            project.stories.filter(iteration__iteration_type=Iteration.ITERATION_ARCHIVE).count()
        stories_in_progress = project.stories.filter(cell__time_type=BoardCell.WORK_TIME).count()

        pstats = {}
        pstats['story_count'] = story_count
        pstats['stories_completed'] = stories_completed
        pstats['stories_in_progress'] = stories_in_progress
        # pstats['business_value_completed'] = project.stories.filter(cell__time_type=BoardCell.WORK_TIME).count()
        try:
            stats = KanbanStat.objects.filter(project=project).order_by("-created")[0]
            pstats['daily_lead_time'] = stats.daily_lead_time
            pstats['daily_flow_efficiency'] = stats.daily_flow_efficiency
            pstats['system_lead_time'] = stats.system_lead_time
            pstats['system_lead_time_85'] = stats.lead_time_85
            pstats['system_lead_time_65'] = stats.lead_time_65
            pstats['system_flow_efficiency'] = stats.system_flow_efficiency
            pstats['cards_claimed'] = stats.cards_claimed
            pstats['points_claimed'] = stats.points_claimed
        except:
            pstats['daily_lead_time'] = -1
            pstats['daily_flow_efficiency'] = -1
            pstats['system_lead_time'] = -1
            pstats['system_flow_efficiency'] = -1
            pstats['cards_claimed'] = -1
            pstats['points_claimed'] = -1
            pstats['system_lead_time_85'] = -1
            pstats['system_lead_time_65'] = -1
        cache.set(cache_key, pstats, CACHE_SECONDS)
        return pstats
    else:
        return cached_value


def getTeamMembers(project, include_staff = True):
    members = []
    rmembers = []
    for team in project.teams.all():
        for member in team.members.all():
            if not member in members:
                members.append(member)
                rmembers.append({"email": member.email, 
                                "username": member.username, 
                                "first_name": member.first_name, 
                                "last_name": member.last_name, 
                                "id": member.id,
                                "access_type": team.access_type})

    if project.organization and include_staff is True:
        for team in project.organization.teams.filter(access_type="staff").prefetch_related("members"):
            for member in team.members.all():
                if not member in members:
                    members.append(member)
                    rmembers.append({"email": member.email, 
                                    "username": member.username, 
                                    "first_name": member.first_name, 
                                    "last_name": member.last_name, 
                                    "id": member.id,
                                    "access_type": team.access_type})

    if project.personal:
        if not project.creator in members:
            members.append(project.creator)
            rmembers.append({"email": project.creator.email, 
                            "username": project.creator.username, 
                            "first_name": project.creator.first_name, 
                            "last_name": project.creator.last_name, 
                            "id": project.creator.id,
                            "access_type": "admin"})

    return sorted(rmembers, key=lambda user: (u"%s%s" % (user["last_name"], user["username"])).lower())


def addContinuousFlowIteration(request, project, c_iteration_id, d_iteration_id):
    """
    Update Projet To Continuous Flow, 
    project: Project itself
    c_iteration_id: Continuous Flow Iteration Id
    d_iteration_id: Iteration to which All cards will be moved
    """
    source_iterations = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK,\
                                                hidden = False).exclude(id = c_iteration_id)
    destinationIteration = project.iterations.filter(id = d_iteration_id)[0]

    for iteration in source_iterations:
        stories = iteration.stories.all()
        moveOutOfCell = False

        for story in stories:
            story.iteration = destinationIteration

            moveOutOfCell = moveOutOfCell or (destinationIteration.iteration_type != Iteration.ITERATION_WORK)

            if moveOutOfCell:
                kanban_managers.moveStoryOntoCell(story, None, request.user)

            signals.story_moved.send(sender=request, story=story, user=request.user,
                                    diffs={"iteration_id": [iteration.id, destinationIteration.id]})
            story.save()

            # Moved within a project, update the iteration and cell
            realtime_util.send_story_patch(project, story, {'iteration_id': story.iteration_id})
            projects_tasks.queueUpdateSolr(story.id)
        
        # rebuild Cell Related System Risks Cache
        projects_tasks.rebuildCellHeaderRisks.apply_async((project, destinationIteration.id), countdown=5)
        projects_tasks.rebuildCellHeaderRisks.apply_async((project, iteration.id), countdown=5)

        iteration.hidden = True
        iteration.save()
    
    broadcastIterationCounts(project)

def get_newsitem_cache_key(org, user, project_slug, iteration_id, start_day, end_day):
    if project_slug is not None:
        if iteration_id is not None:
            key = "newsitems_project_itr_%s_%d_%d_%d" % (project_slug, int(iteration_id), int(start_day), int(end_day))
        else:
            key = "newsitems_project_%s_%d_%d" % (project_slug , int(start_day), int(end_day))
    else:
        key = "newsitems_org_%d_%d_%d_%d" % (org.id, user.id, int(start_day), int(end_day))
    
    return key

def clearNewsItemsCache(org, project_slug):
    try:
        if project_slug is not None:
            # delete project level cache
            project_key = "newsitems_project_%s*" % (project_slug, )
            for key in cache.keys(project_key):
                cache.delete(key)

            # delete iteration level cache
            iteration_key = "newsitems_project_itr_%s*" % (project_slug, )
            for key in cache.keys(iteration_key):
                cache.delete(key) 

        # delete org level cache
        org_key = "newsitems_org_%d*" % (org.id, )
        for key in cache.keys(org_key):
            cache.delete(key)
    except:
        logger.error("got issue while deleting NewsItem Cache")
