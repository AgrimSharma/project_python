from .common import *
from apps.projects.models import Iteration
from apps.kanban.stats.cfd import calculateCFD
from apps.kanban.models import Workflow


class IterationStatsHandler(BaseHandler):
    fields = ('id',
              'total_cards',
              'completed_cards',
              'in_progress_cards',
              'locked',
              'total_points',
              'total_business_value',
              'daysLeft',
              'completed_points',
              'in_progress_points',
              'waiting_cards',
              'blocked_cards',
              'chart')
    allowed_methods = ('GET',)

    @staticmethod
    def total_cards(iteration):
        return iteration.stories.count()

    @staticmethod
    def completed_cards(iteration):
        if iteration.iteration_type == Iteration.ITERATION_ARCHIVE:
            return iteration.stories.all().count()
        if iteration.iteration_type == Iteration.ITERATION_BACKLOG:
            return 0
        return iteration.stories.filter(cell__time_type=3).count()


    @staticmethod
    def in_progress_cards(iteration):
        return iteration.stories.filter(cell__time_type=2).count()
    
    @staticmethod
    def waiting_cards(iteration):
        return iteration.stories.filter(cell__time_type=0).count()
    
    @staticmethod
    def blocked_cards(iteration):
        return iteration.stories.filter(blocked=True).count()


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)

        mapper = IterationStatsHandler

        if iteration_id is None:
            iterations = list(project.iterations.all().prefetch_related('stories', 'project', 'project__organization'))
            for iteration in iterations:
                setattr(iteration, "apiMapper", mapper)
        else:
            iterations = project.iterations.get(id=iteration_id)
            setattr(iterations, "apiMapper", mapper)

        return iterations


