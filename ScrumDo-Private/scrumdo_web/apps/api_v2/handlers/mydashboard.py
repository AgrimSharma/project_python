import apps.projects.access as access
from apps.kanban.models import KanbanStat
from apps.projects.models import Project, Story, Task, Iteration
from apps.organizations.models import Organization
from apps.favorites.models import Favorite

from .common import *

import datetime
import logging

logger = logging.getLogger(__name__)



class MyDashboardHandler(BaseHandler):
    """Returns data that we need to construct the "my dashboard"""
    allowed_methods = ('GET',)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug ):
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that Organization")
        return myDashboardInfo(request.user, organization)


def _getAssignedStories(user, organization):
    # Stories directly assigned
    # Also, ignoring stories more than 6 months old
    sixmonthsago = datetime.date.today() - datetime.timedelta(days=6*30)
    directAssigned = Story.objects.filter(iteration__iteration_type=Iteration.ITERATION_WORK, modified__gt=sixmonthsago, project__organization=organization, assignee=user).select_related("epic","creator","project").prefetch_related("story_tags__tag","assignee","extra_attributes")
    taskAssigned = Story.objects.filter(iteration__iteration_type=Iteration.ITERATION_WORK, modified__gt=sixmonthsago, project__organization=organization, tasks__assignee=user).select_related("epic","creator","project").prefetch_related("story_tags__tag","assignee","extra_attributes")
    assigned = set( list(directAssigned) + list(taskAssigned) )
    # logger.debug("Found %d directly assigned stories" % directAssigned.count())
    # logger.debug("Found %d task assigned stories" % taskAssigned.count())
    # logger.debug("Total of %d stories (may have had dupes)" % len(assigned))    
    return assigned


def myDashboardInfo(user, organization):
    # Things that show up on your dashboard.
    # 1. Watched Projects
    # 2. Scrum Projects where you have a story assigned in a current iteration
    # 3. Scrum Projects where you have a task assigned in a current iteration
    # 4. Kanban Projects where you have a task assigned in a not-done cell
    # 5. Kanban Projects where you have a story assigned in a not-done cell
    rv = {'projects': [], 'stories':[], 'recent_stories': [], 'interesting':False}
    favorites = list(Favorite.objects.filter(user=user))

    assignedStories = _getAssignedStories(user, organization)

    for project in organization.projects.filter(active=True).order_by("name"):
        if access.has_read_access(project, user):
            _processScrumProject(rv, project, user, organization, favorites, assignedStories)
            # if project.project_type == Project.PROJECT_TYPE_SCRUM:
            #
            # else:
            #     _processKanbanProject(rv, project, user, organization, favorites, assignedStories)

    if len(rv['projects']) == 0:
        # This user had no assigned stories, and no watched projects.
        # let's find a few for them to look at.
        _appendInterestingProjects(rv, organization, user)
        rv['interesting'] = len(rv['projects']) != organization.projects.count()

    rv['stories_completed'] = Story.objects.filter(project__organization=organization, status=10, assignee=user).count()
    rv['tasks_completed'] = Task.objects.filter(story__project__organization=organization, status=10, assignee=user).count()

    return rv


class MiniFavorite:
    def __init__(self, project_id):
        self.project_id = project_id


def _appendInterestingProjects(rv, organization, user):
    count = 0    
    projects = []
    for story in Story.objects.filter(project__organization=organization).order_by("-modified").select_related("epic","creator","project").prefetch_related("story_tags__tag","assignee","extra_attributes")[:500]:
        project = story.project
        if not access.has_read_access(project, user):
            continue
        if not project in projects:
            projects.append(project)            
            summary = _projectSummary(project)

            fav = MiniFavorite(project.id)
            _processScrumProject(rv, project, user, organization, [fav], [])
            _addKanbanStats(project, summary)
            summary['assigned_story'] = False
            rv['projects'].append(summary)


        

        rv['recent_stories'].append(story)
        count += 1
        if count >= 20:
            return


def _projectSummary(project):
    fields = ['id', 'name', 'project_type', 'slug']
    r = {}
    for f in fields:
        r[f] = getattr(project,f)
    r['statuses'] = list(project.status_choices())
    r['task_statuses'] = list(project.task_status_choices())
    return r


def _processStories(rv, stories, user):
    # this used to be more complex, but then we started pre-loading assigned stories
    # and not passing them all.
    foundStory = False

    for story in stories:        
        rv['stories'].append(story)
        foundStory = True

    return foundStory
        

def _inFavorites(project, favorites):
    for fav in favorites:
        if fav.project_id == project.id:
            return True
    return False

def _processScrumProject(rv, project, user, organization, favorites, assignedStories):
    addProject = False
    assignedStory = False

    if _inFavorites(project, favorites):
        addProject = True

    iterations = []

    currentIterations = project.get_current_iterations(organization)

    if len(currentIterations) == 0:
        # No current, let's show the last one.
        currentIterations = project.iterations.filter(default_iteration=False, iteration_type=Iteration.ITERATION_WORK).order_by("-end_date")[:1]

    for iteration in currentIterations:

        if (not addProject) and (iteration.end_date is not None) and (iteration.end_date < datetime.date.today() - datetime.timedelta(days=30)):
            continue

        stories = [story for story in assignedStories if story.iteration_id==iteration.id]
        # iteration.stories.all().select_related("epic","creator","project").prefetch_related("story_tags__tag","assignee","extra_attributes")
        v = _processStories(rv, stories, user)        
        if addProject and not v:
            for story in iteration.stories.all().order_by("-modified").select_related("epic","creator","project").prefetch_related("story_tags__tag","assignee","extra_attributes")[:5]:
                rv['recent_stories'].append(story)
        addProject = addProject or v
        assignedStory = assignedStory or v
        iterations.append(iteration)

    if addProject:
        summary = _projectSummary(project)
        _addKanbanStats(project, summary)
        summary['iterations'] = iterations
        summary['assigned_story'] = assignedStory
        rv['projects'].append( summary)


def _addKanbanStats(project, projectSummary):
    projectSummary['current_stories'] = Story.objects.filter(project=project, iteration__iteration_type=1).count()
    try:
        stats = KanbanStat.objects.filter(project=project).order_by("-created")[0]
        projectSummary['daily_lead_time'] = stats.daily_lead_time
        projectSummary['daily_flow_efficiency'] = stats.daily_flow_efficiency
        projectSummary['system_lead_time'] = stats.system_lead_time
        projectSummary['system_flow_efficiency'] = stats.system_flow_efficiency
    except:
        projectSummary['daily_lead_time'] = -1
        projectSummary['daily_flow_efficiency'] = -1
        projectSummary['system_lead_time'] = -1
        projectSummary['system_flow_efficiency'] = -1


        

def _processKanbanProject(rv, project, user, organization, favorites, assignedStories):
    addProject = _inFavorites(project, favorites)
    stories = [story for story in assignedStories if (story.project == project) and (story.iteration.iteration_type == 1)]
    v = _processStories(rv, stories, user)            
    if addProject and not v:
        # We're supposed to include this project, but didn't find any assigned stories
        for story in Story.objects.filter(project=project, iteration__iteration_type=1).order_by("-modified").select_related("epic","creator","project").prefetch_related("story_tags__tag","assignee","extra_attributes")[:5]:
            rv['recent_stories'].append(story)
    assignedStory = v
    addProject = addProject or v  # add the project if it was a favorite (checked above) or if stories assigned.

    if addProject:
        projectSummary = _projectSummary(project)
        projectSummary['assigned_story'] = assignedStory
        _addKanbanStats(project, projectSummary)
        rv['projects'].append( projectSummary )

