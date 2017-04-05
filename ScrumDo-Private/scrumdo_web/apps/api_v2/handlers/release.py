from .common import *
from django.db.models import Count
from apps.projects.models import Project, ReleaseStat, Story, ProgramIncrement, Iteration
from apps.kanban.models import BoardCell
from .story import StoryHandler, MiniStoryHandler

class ReleaseHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', "DELETE")

class ProjectReleaseHandler(MiniStoryHandler):
    """
    This is used to get Release Stories having children for Project
    project_slug: Project Slug
    return: MiniStories 
    """
    allowed_methods = ('GET',)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        
        include_archived = request.GET.get("archived", "false") == "true"

        iteration_types = [Iteration.ITERATION_BACKLOG, Iteration.ITERATION_WORK]
        if include_archived:
            iteration_types.append(Iteration.ITERATION_ARCHIVE)
        
        return project.stories.filter(iteration__iteration_type__in = iteration_types,
                                story__isnull=False, 
                                story__iteration__iteration_type=Iteration.ITERATION_BACKLOG,
                                iteration__hidden=False).distinct()


class ReleaseStatHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = ReleaseStat
    fields = (
        'release_id',
        'date',
        'cards_total',
        'cards_completed',
        'cards_in_progress',
        'points_total',
        'points_completed',
        'points_in_progress'
    )

    def read(self, request, organization_slug, release_id=None, project_slug=None, iteration_id=None, scope=None):
        org = Organization.objects.get(slug=organization_slug)
        
        if not org.hasReadAccess(request.user):
            raise PermissionDenied('You do not have access to that organization')

        if release_id is None:
            if iteration_id is not None:
                project = Project.objects.get(slug=project_slug)
                iteration = project.iterations.get(id=iteration_id)
                releases = Story.objects.filter(project__organization=org,
                                                iteration=iteration,
                                                project=project)
            elif project_slug is None:
                releases = Story.objects.filter(project__organization=org,
                                            project__project_type=Project.PROJECT_TYPE_PORTFOLIO)
            else:
                project = Project.objects.filter(slug=project_slug)
                releases = Story.objects.filter(project__organization=org,
                                            project=project)
            rv = []
            # TODO: DANGER DANGER: This will not perform well if someone makes a lot of releases.
            for release in releases:
                try:
                    rv.append(release.stats.order_by("-date")[0])
                except IndexError:
                    rv.append({'release_id': release.id,
                                'date': '',
                                'cards_total': 0,
                                'cards_completed': 0,
                                'cards_in_progress': 0,
                                'points_total': 0,
                                'points_completed': 0,
                                'points_in_progress': 0} )

            return rv

        if scope == 'all':
            return Story.objects.get(project__organization=org,
                                     id=release_id).stats.order_by("date")
        else:
            return Story.objects.get(project__organization=org,
                                     id=release_id).stats.order_by("-date")[0]


class ReleaseStoriesHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, release_id, project_slug):

        org, project = checkOrgProject(request, organization_slug, project_slug)

        return Story.objects.filter(project__organization=org, release_id=release_id)

class ReleaseStoriesStatsHandler(BaseHandler):
    fields = ("totalcards","id")
    allowed_methods = ('GET',)
    
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, release_id, project_slug, load_child = 0):

        org, project = checkOrgProject(request, organization_slug, project_slug)

        if int(release_id) != -1:
            if int(load_child) != 0 :
                return Story.objects.filter(project__organization=org, 
                                            release_id=release_id).annotate(totalcards=Count('story'))
            else:
                stories = Story.objects.filter(project__organization=org, release_id=release_id).count()
                return [{"totalcards": stories, "id":release_id}]
        else:
            return Story.objects.filter(project__organization=org, project=project).annotate(totalcards=Count('story'))


class ReleasesChildStatsHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id, type=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        iteration = project.iterations.get(id=iteration_id)
        childstories = Story.objects.filter(release__iteration=iteration)
        data = {}
        for story in childstories:
            try:
                data[story.release.id].append(story.iteration_id)
            except:
                data[story.release.id] = [story.iteration_id]

        return data


class ReleaseTeamsStatsHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id, release_id):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        teams = project.children.filter(stories__release_id = release_id).distinct()
        data = {}

        for team in teams:
            total_cards = Story.objects.filter(project_id=team.id, \
                                                release_id=release_id,\
                                                iteration__program_increment_schedule__increment__iteration_id = iteration_id)\
                                                .select_related('cell')

            in_progress = total_cards.filter(cell__time_type=BoardCell.WORK_TIME).count()
            completed =  total_cards.filter(cell__time_type=BoardCell.DONE_TIME).count()
            data[team.slug] = {"cards_total": total_cards.count(), 
                            "cards_in_progress": in_progress, 
                            "cards_completed": completed}
        
        return data