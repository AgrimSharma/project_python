from .common import *

from apps.projects.models import PointsLog


class BurndownHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ['date','points_total',] + list("points_status%d" % i for i in range(1,11))
    model = PointsLog

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if iteration_id is not None:
            return project.iterations.get(id=iteration_id).points_log.all().order_by("date")

        return project.points_log.all().order_by("date")