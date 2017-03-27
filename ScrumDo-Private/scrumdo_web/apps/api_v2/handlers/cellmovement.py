from .common import *
from apps.kanban.models import CellMovement


class CellMovementHandler(BaseHandler):
    fields = ("id",
              "user",
              "cell_to_id",
              "story_id",
              "created",
              "related_iteration_id")
    model = CellMovement
    allowed_methods = ('GET',)

    
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, story_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        story = project.stories.get(id=story_id)
        return CellMovement.objects.filter(story=story).order_by("-created")