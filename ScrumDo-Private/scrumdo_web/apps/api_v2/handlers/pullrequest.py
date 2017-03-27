from .common import *

from apps.projects.models import PullRequest


class PullRequestHandler(BaseHandler):
    allowed_methods = ('GET', )
    fields = ("id", 'state', 'story', 'created', 'name', 'full_text', 'link')
    model = PullRequest

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, story_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        return project.stories.get(id=story_id).pull_requests
