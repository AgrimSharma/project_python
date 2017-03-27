from .common import *

from apps.projects import signals
from apps.projects.models import Project, ProgramIncrement, ProgramIncrementSchedule, Iteration, Story, TeamIterationWIPLimit
from apps.projects import portfolio_managers
from apps.kanban.models import BoardCell
# from apps.projects import managers as project_managers
# from apps.projects.org_backlog import set_project_parents


# [                       // A list of increments
#   {                     // A single increment
#     id: 00,
#     name: '',           // name, start, end all come from the iteration the increment points to
#     iteration_id: 00,
#     start_date: 'xxx',
#     end_date: 'xxx',
#     schedule: [         // List of ProgramIncrementSchedule objects
#         {
#           start_date: 'xxxxx',
#           default_name: 'xxxx',
#           iterations: [
#              {                      // A list of summaries about the iterations/projects in the schedule
#                 id: 000,
#                 project_id: 000,
#                 project_slug: 'xxxx',
#                 project_name: 'xxxx'
#                 iteration_id: 000,
#                 iteration_name: 'xxxxx',
#                 cards_total: 55,
#                 cards_in_progress: 25,
#                 cards_completed: 10
#              },
#              {...},{...},{...}
#           ]
#         },
#         {...},
#     ]
#   }
# ]

class ProgramIncrementScheduleHandler(BaseHandler):
    model = ProgramIncrementSchedule
    allowed_methods = ('GET',)
    fields = (
        "id",
        "start_date",
        "default_name",
        "iterations"
    )

    @staticmethod
    def iterations(schedule):
        def _getIterationWip(iteration):
            project = iteration.project
            try:
                limit = TeamIterationWIPLimit.objects.get(team=project, iteration_id=iteration.id)
                return limit
            except TeamIterationWIPLimit.DoesNotExist:
                return None
                
        return [
            {
                "project_id": iteration.project_id,
                "project_slug": iteration.project.slug,
                "project_name": iteration.project.name,
                "project_icon": iteration.project.icon,
                "project_color": iteration.project.color,
                "iteration_id": iteration.id,
                "is_continuous": iteration.project.continuous_flow_iteration_id == iteration.id,
                "iteration_name": iteration.name,
                "start_date": iteration.start_date,
                "end_date": iteration.end_date,
                "mission": iteration.vision,
                "wip_limits": _getIterationWip(iteration)
            }
            for iteration in schedule.iterations.filter(hidden=False).select_related("project").order_by('id')
        ]

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, increment_id, schedule_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)

        if increment_id is not None:
            return ProgramIncrementSchedule.objects.get(increment_id=increment_id, id=schedule_id)
        else:
            return ProgramIncrementSchedule.objects.filter(increment_id=increment_id)


class ProgramIncrementHandler(BaseHandler):
    model = ProgramIncrement
    allowed_methods = ('GET', )
    fields = (
        "id",
        "name",
        "iteration_id",
        "start_date",
        "end_date",
        "schedule",
        "project_slug"
    )

    @staticmethod
    def project_slug(increment):
        return increment.iteration.project.slug

    @staticmethod
    def schedule(increment):
        return increment.schedule.filter(iterations__isnull = False).distinct().order_by('start_date')

    @staticmethod
    def name(increment):
        return increment.iteration.name

    @staticmethod
    def iteration_id(increment):
        return increment.iteration.id

    @staticmethod
    def start_date(increment):
        return increment.iteration.start_date

    @staticmethod
    def end_date(increment):
        return increment.iteration.end_date

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, increment_id=None, iteration_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)

        if iteration_id is not None:
            try:
                # This one will return the increment if the iteration is the root iteration for that increment
                # query on project to make sure it's not a malicious user trying to load an iteration for a project
                # they don't have access to.
                return ProgramIncrement.objects.get(iteration__project=project, iteration_id=iteration_id)
            except ProgramIncrement.DoesNotExist:
                return None
                # Update 10/13/16 - Just returning None here, we don't want this API call to return the parent's
                #                   increment anymore.
                #
                # This one will return the increment if the iteration is part
                # ProgramIncrement.objects.get(iteration__project=project, iteration_id=iteration_id)
                # schedule = Iteration.objects.get(id=iteration_id, project=project).program_increment_schedule
                # if schedule is not None:
                #     return schedule.increment
                # return None


        elif increment_id is not None:
            return ProgramIncrement.objects.get(iteration__project=project, id=increment_id)
        else:
            return ProgramIncrement.objects.filter(iteration__project=project).select_related("iteration",
                                                                                              "iteration__project")
