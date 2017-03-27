from .common import *

from django.conf import settings

from apps.projects.models import Project
import apps.hipchat.util as util
from apps.hipchat.models import *
from apps.hipchat.tasks import send_hipchat_message
import requests


class HipChatExtraHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None):
        try:
            return self._read_project(request, organization_slug, project_slug)
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                return {'configured': True, 'error': 'bad_credentials'}
            return {'error': 'could_not_load'}

    def _read_project(self, request, organization_slug, project_slug):
        organization = Organization.objects.get(slug=organization_slug)
        project = organization.projects.get(slug=project_slug)
        if not has_admin_access(project, request.user):
            raise PermissionDenied("Only admins can access this")
        return {'configured': True,
                'mappings': HipChatMapping.objects.filter(project=project)
                }

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, project_slug):
        project = Project.objects.get(slug=project_slug)
        return []


    def _addChannel(self, request, organization_slug, project_slug):
        data = request.data
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied('Only staff members can do this.')
        project = organization.projects.get(slug=project_slug)

        mapping = HipChatMapping(project=project,
                                 token=data['token'],
                                 name=data['name'],
                                 url=data['url'],
                                 card_moved=data['card_moved'],
                                 card_created=data['new_card'],
                                 card_modified=data['card_edited'],
                                 comment_created=data['comment_created'])
        mapping.save()

        url = "{host}{url}".format(url=project.get_absolute_url(), host=settings.SSL_BASE_URL)
        send_hipchat_message(mapping.id, "ScrumDo is configured to send messages here. {url}".format(url=url))
        # send_slack_message(mapping.id, "The ScrumDo project <{project_url}|{project_name}> is now configured to send messages here.".format(project_name=project.name, project_url=url))

        return self._read_project(request, organization_slug, project_slug)



    def _removeChannel(self, request, organization_slug, project_slug):
        """Removes a github repo binding from a project and deletes any webhooks."""
        data = request.data
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied('Only staff members can do this.')
        project = organization.projects.get(slug=project_slug)
        mapping = HipChatMapping.objects.get(project=project, id=data['channelId'])
        mapping.delete()
        return self._read_project(request, organization_slug, project_slug)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug=None):
        data = request.data
        if data['action'] == 'addChannel':
            return self._addChannel(request, organization_slug, project_slug)
        if data['action'] == 'removeChannel':
            return self._removeChannel(request, organization_slug, project_slug)
        return "ok"


