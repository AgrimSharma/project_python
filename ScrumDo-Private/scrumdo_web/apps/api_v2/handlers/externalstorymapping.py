from common import *
from apps.extras.models import ExternalStoryMapping


class ExternalStoryMappingHandler(BaseHandler):
    model = ExternalStoryMapping
    allowed_methods = ('GET',)
    fields = ('id',
              'story_id',
              'external_url',
              'extra_slug',
              'external_id',
              'external_extra'
              )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, story_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        result = ExternalStoryMapping.objects.filter(story__project=project)

        if story_id:
            result = result.filter(story_id=story_id)

        return result
