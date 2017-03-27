from .common import *

from apps.projects.models import ProjectShare

import random
import string


class ProjectShareHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    fields = ('id', 'iteration_id', 'enabled', 'all_cards', 'tag', 'key',
                'assignee', 'summary', 'detail', 'custom1', 'custom2', 'custom3',
                'time_estimates', 'points', 'epic', 'business_value',
                'comments', 'tasks')
    write_fields = ('enabled', 'all_cards', 'tag', 'assignee', 'summary', 'detail',
                    'custom1', 'custom2', 'custom3', 'time_estimates',
                    'points', 'epic', 'business_value', 'comments', 'tasks')
    model = ProjectShare

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if not has_admin_access(project, request.user):
            raise PermissionDenied("You don't have admin access to that Project")

        return ProjectShare.objects.filter(project=project)


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, share_id):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        data = request.data

        if not has_admin_access(project, request.user):
            raise PermissionDenied("You don't have admin access to that Project")

        share = ProjectShare.objects.get(project=project, id=share_id)

        for field in ProjectShareHandler.write_fields:
            if field in data:
                setattr(share, field, data[field])

        share.save()
        return share


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, share_id):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if not has_admin_access(project, request.user):
            raise PermissionDenied("You don't have admin access to that Project")

        share = ProjectShare.objects.get(project=project, id=share_id)
        share.delete()

        return {}


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        data = request.data

        if not has_admin_access(project, request.user):
            raise PermissionDenied("You don't have admin access to that Project")

        share = ProjectShare(project=project)
        share.iteration = project.iterations.get(id=data['iteration_id'])
        for field in ProjectShareHandler.write_fields:
            if field in data:
                setattr(share, field, data[field])
        share.key = "".join(random.sample(string.lowercase + string.digits, 16))
        share.save()

        return share


