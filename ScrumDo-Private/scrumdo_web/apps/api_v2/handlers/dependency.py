from .common import *
from apps.projects.models import *
from apps.projects.access import read_access_or_403
# Just to format the story the way we want for dependency calls.
class DependencyStory(BaseHandler):
    allowed_methods = ()
    fields = fields = ("id",
                "number",
                "rank",
                "category",
                "business_value",
                "detail",
                "comment_count",
                ("epic",("local_id","id")),
                "epic_label",
                "created",
                "modified",
                "iteration_id",
                "summary",
                "points",
                "extra_1",
                "extra_2",
                "extra_3",
                "points_value",
                "tags",
                "tags_list",
                "task_counts",
                "has_external_links",
                "assignee",
                "cell",
                ("labels", ("id", "name", "color")),
                "iteration",
                ("project", ("id", "name", "prefix", "slug")),
                "blocked",
                "time_criticality",
                "time_criticality_label",
                "risk_reduction",
                "risk_reduction_label",
                "wsjf_value",
                "business_value_label")
    @staticmethod
    def number(story):
        return story.local_id

dependencyStory = DependencyStory()


class IncrementDependencyHandler(BaseHandler):
    "Returns all dependencies in an increment."
    fields = ('from_story', 'to_story')
    
    def read(self, request, organization_slug, increment_id):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasReadAccess(request.user):
            raise PermissionDenied()
        increment = ProgramIncrement.objects.get(id=increment_id,
                                                 iteration__project__organization=org)
        iteration = increment.iteration
        project = iteration.project
        read_access_or_403(project, request.user)

        stories = Story.objects.filter(iteration__program_increment_schedule__increment=increment,
                                       dependency__isnull=False)

        result = []
        for story in stories:
            dependencies = story.dependency.filter(iteration__program_increment_schedule__increment=increment)
            result.extend([{'story': story.id, 'dependency': dep.id} for dep in dependencies])

        return result


class StoryDependencyHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')

    def _format_return(self, story):
        on = story.dependency.all()
        to = story.dependent_stories.all()
        for s in on:
            setattr(s, "apiMapper", dependencyStory)
        for s in to:
            setattr(s, "apiMapper", dependencyStory)
        return {
            "dependent_on": on,
            "dependent_to": to
        }

    def read(self, request, story_id):
        story = Story.objects.get(id=story_id)
        if not has_read_access(story.project, request.user):
            raise PermissionDenied()
        return self._format_return(story)


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, story_id):
        data = request.data
        story = Story.objects.get(id=story_id)
        if not has_read_access(story.project, request.user):
            raise PermissionDenied("You don't have access to that project.")
        dependencies = data["dependencies"]
        for newdependency in dependencies:
            dependencyId = newdependency['id']
            if dependencyId == story.id:
                continue
            dependentStory = Story.objects.get(id=dependencyId)
            if not has_read_access(dependentStory.project, request.user):
                raise PermissionDenied()
            story.dependency.add(dependentStory)
        return self._format_return(story)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, story_id, dependent_story_id):
        story = Story.objects.get(id=story_id)
        if not has_read_access(story.project, request.user):
            raise PermissionDenied()
        story.dependency.remove(Story.objects.get(id=dependent_story_id))
        return self._format_return(story)


class ProjectDependencyHandler(BaseHandler):

    allowed_methods = ('GET', )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        # stats = True
        # we need to find the parent and sibling dependencies count
        # used for portfolio tree structure
        stats = request.GET.get("stats", "false") == "true"
        sibling = request.GET.get("sibling", "false") == "true"
        parent_projects = project.parents.all()
        portfolio_level = project.portfolio_level

        if portfolio_level is not None and sibling is True:
            sibling_projects = Project.objects.filter(portfolio_level=portfolio_level).exclude(slug=project.slug)
        else:
            sibling_projects = None
            
        if stats is True:

            data = {"parent": {}, "sibling": {}}

            for p_project in parent_projects:
                total_cards = Story.objects.filter(project = p_project, dependent_stories__project = project).count()
                data["parent"][p_project.id] = total_cards
            
            if sibling_projects is not None:
                for s_project in sibling_projects:
                    total = Story.objects.filter(project = s_project, dependent_stories__project = project).count()
                    data["sibling"][s_project.id] = total
            
            return data
        else:
            stories = project.stories.filter(dependency__isnull=False)
            projects = [project]
            if sibling_projects is not None:
                projects.extend(sibling_projects)
            result = {"data": []}

            for story in stories:
                dependencies = story.dependency.filter(project__in=projects)
                result["data"].extend([{'story': story.id, 'dependency': dep.id} for dep in dependencies])
            
            if sibling_projects is not None:
                for s_project in sibling_projects:
                    stories = s_project.stories.filter(dependency__isnull=False)
                    for story in stories:
                        dependencies = story.dependency.filter(project__in=projects)
                        result["data"].extend([{'story': story.id, 'dependency': dep.id} for dep in dependencies])

            return result