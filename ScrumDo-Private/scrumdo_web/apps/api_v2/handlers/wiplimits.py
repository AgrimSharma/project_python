from .common import *

from apps.projects.models import TeamIterationWIPLimit
import apps.projects.tasks as project_tasks


class WIPLimitHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    fields = (
        "featureLimit",
        "featurePointLimit",
        "cardLimit",
        "cardPointLimit"
    )
    model = TeamIterationWIPLimit

    def _update_properties(self, limit, data):
        limit.featureLimit = data.get('featureLimit', 0)
        limit.featurePointLimit = data.get('featurePointLimit', 0)
        limit.cardLimit = data.get('cardLimit', 0)
        limit.cardPointLimit = data.get('cardPointLimit', 0)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, iteration_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        (limit, created) = TeamIterationWIPLimit.objects.get_or_create(team=project, iteration_id=iteration_id)
        self._update_properties(limit, data)
        limit.save()
        # rebuild Iteration Related System Risks Cache
        project_tasks.rebuildIterationRisks.apply_async((project, iteration_id), countdown=5)
        project_tasks.rebuildIncrementRisks.apply_async((project, iteration_id), countdown=8)
        return limit

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, iteration_id):
        return self.create(request, organization_slug, project_slug, iteration_id)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, iteration_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        try:
            limit = TeamIterationWIPLimit.objects.get(team=project, iteration_id=iteration_id)
            limit.delete()
        except TeamIterationWIPLimit.DoesNotExist:
            pass

        return "deleted"

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        try:
            limit = TeamIterationWIPLimit.objects.get(team=project, iteration_id=iteration_id)
            return limit
        except TeamIterationWIPLimit.DoesNotExist:
            return {
                "featureLimit": 0,
                "featurePointLimit": 0,
                "cardLimit": 0,
                "cardPointLimit": 0
            }
