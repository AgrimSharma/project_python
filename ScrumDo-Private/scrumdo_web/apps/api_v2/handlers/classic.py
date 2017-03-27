from django.http import Http404

from .common import *
from apps.kanban.tasks import scheduleConvertClassicProject
import apps.classic.models as cmodels


class ClassicProjectHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    fields = ('slug', 'name', 'category', 'personal', 'active', 'project_type', 'id')
    model = cmodels.Project

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def create(self, request, organization_slug):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasStaffAccess(request.user):
            raise PermissionDenied("Only staff members can do this.")

        project = cmodels.Project.objects.get(organization=org, slug=request.data.get("project_slug"))
        if request.data.get("action") == 'upgrade':
            jobId = scheduleConvertClassicProject(org, project.id, request.user, request.data.get("mode"))
            return {'job_id':jobId}

        raise Http404


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasStaffAccess(request.user):
            return []
        return cmodels.Project.objects.filter(organization=org, active=True).order_by("category","name")
