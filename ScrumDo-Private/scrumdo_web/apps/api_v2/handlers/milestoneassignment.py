from .common import *

from haystack.query import SearchQuerySet
from apps.projects.models import Project, MilestoneAssignment, Story, Iteration


class AssigmentOptionsHandler(BaseHandler):
    allowed_methods = ('GET', )
    fields = (
        "iteration_id",
        "number",
        "id",
        "project_slug",
        "summary",
        "project_prefix"
    )

    @staticmethod
    def project_slug(story):
        return story.project.slug

    @staticmethod
    def number(story):
        return story.local_id

    @staticmethod
    def project_prefix(story):
        return story.project.prefix

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, story_id):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        userQueryText = request.GET.get('query')
        targetParentSlug = request.GET.get('parent')

        parent = org.projects.get(slug=targetParentSlug)

        # TODO: use the story_id field to prioritize results (BUT REMEMBER IT CAN BE -1)
        # story = project.stories.get(id=story_id)
        # iteration = story.iteration
        # parents = project.parents.all()

        query = SearchQuerySet()
        query = query.models(Story)

        query = query.filter(project_id=parent.id   )

        if userQueryText is not None and len(userQueryText)>0:
            query = query.filter(text=userQueryText)

        search_results = [result.object for result in query.order_by("rank").load_all()]

        return paginate(search_results, request, assignmentOptionsHandler)

assignmentOptionsHandler = AssigmentOptionsHandler()



class MilestoneAssignmentHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST')
    model = MilestoneAssignment
    fields = ("assigned_project",
              "milestone_id",
              "milestone_name",
              "milestone_project_slug",
              "active",
              "assigned_date",
              "status",
              "id",
              "cards_total",
              "cards_completed",
              "cards_in_progress",
              "points_total",
              "points_completed",
              "points_in_progress"
              )

    @staticmethod
    def milestone_project_slug(assignment):
        return assignment.milestone.project.slug

    @staticmethod
    def milestone_name(assignment):
        return assignment.milestone.summary

    @staticmethod
    def assigned_project(assignment):
        return {
            'name': assignment.assigned_project.name,
            'slug': assignment.assigned_project.slug
        }

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, milestone_id=None, iteration_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        if project.project_type == Project.PROJECT_TYPE_PORTFOLIO:
            if milestone_id:
                milestone = project.stories.get(id=milestone_id)
                return MilestoneAssignment.objects.filter(milestone=milestone)

            if iteration_id:
                return MilestoneAssignment.objects.filter(milestone__iteration_id=iteration_id)

            return MilestoneAssignment.objects\
                .exclude(milestone__iteration__iteration_type=Iteration.ITERATION_TRASH)\
                .filter(milestone__project=project)

        elif project.project_type == Project.PROJECT_TYPE_KANBAN:
            return MilestoneAssignment.objects\
                .exclude(milestone__iteration__iteration_type=Iteration.ITERATION_TRASH)\
                .filter(assigned_project=project)


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, milestone_id):
        assignment = MilestoneAssignment.objects.get(id=milestone_id)
        project = assignment.assigned_project
        if not has_write_access(project, request.user, True):
            raise PermissionDenied('You cant write to this project')
        data = request.data
        assignment.status = data['status']
        assignment.active = data['active']
        assignment.save()
        return assignment



    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, milestone_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        target_projects = set(request.data)
        milestone = project.stories.get(id=milestone_id)
        current_assignments = list(MilestoneAssignment.objects.filter(milestone=milestone))
        current_projects = {assignment.assigned_project.slug for assignment in current_assignments if assignment.active}
        projects_to_add = target_projects.difference(current_projects)
        projects_to_remove = current_projects.difference(target_projects)
        for slug in projects_to_add:
            project = org.projects.get(slug=slug)
            assignment, created = MilestoneAssignment.objects.get_or_create(milestone=milestone, assigned_project=project)
            # It's possible that we previously had an assignment, so we just need to set active.  Or it's possible
            # this is a brand new assignment.
            assignment.active = True
            assignment.save()
        for slug in projects_to_remove:
            assignment = MilestoneAssignment.objects.get(milestone=milestone, assigned_project__slug=slug)
            assignment.active = False
            assignment.save()

        # NOTE: this means assignments are created, but never deleted.  They're just set inactive.  That's good
        #       so we can tie stats to them later without having those stats get chain deleted
        return MilestoneAssignment.objects.filter(milestone=milestone)








