from .common import *


class AllUsersHandler(BaseHandler):
    allowed_methods = ('GET')
    # fields = ('id', 'html', 'date_submitted_since', 'date_submitted', 'comment', 'user_id', 'user_name', 'user', 'parent_id')

    def read(self, request, organization_slug):
        org = Organization.objects.get(slug=organization_slug)
        if org.hasStaffAccess(request.user):
            return org.members()
        else:
            return org.members(request.user)
