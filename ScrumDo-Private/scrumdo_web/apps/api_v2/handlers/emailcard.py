from .common import *

from apps.incoming_email.manager import project_email_address


class EmailCardExtraHandler(BaseHandler):
    allowed_methods = ('GET', )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        return {'address': project_email_address(project)}

