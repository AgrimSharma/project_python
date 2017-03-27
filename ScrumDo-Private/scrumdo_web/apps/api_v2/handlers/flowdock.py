from .common import *

from django.conf import settings

from apps.projects.models import Project
import apps.flowdock.util as util
from apps.flowdock.models import *
from apps.flowdock.tasks import send_flowdock_message
import requests
import json

class FlowdockExtraHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None):
        try:
            return self._read_project(request, organization_slug, project_slug)
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                return {'configured': True, 'error': 'bad_credentials', 'auth_url': util.flowdock_auth_url(project_slug)}
            return {'error': 'could_not_load', 'auth_url': util.flowdock_auth_url(project_slug)}

    def _read_project(self, request, organization_slug, project_slug):
        organization = Organization.objects.get(slug=organization_slug)
        project = organization.projects.get(slug=project_slug)
        if not has_admin_access(project, request.user):
            raise PermissionDenied("Only admins can access this")
        try:
            credentials = FlowdockUser.objects.get(project=project)

            channels = requests.get("https://api.flowdock.com/flows?access_token=%s" % credentials.oauth_token).json()

            return {'configured': True,
                    'auth_url': util.flowdock_auth_url(project_slug),
                    'auth_user': credentials.flowdock_username,
                    'channels': channels,
                    'mappings': FlowdockMapping.objects.filter(project=project)
                    }
        except FlowdockUser.DoesNotExist:
            return {'configured': False, 'auth_url': util.flowdock_auth_url(project_slug)}

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, project_slug):
        project = Project.objects.get(slug=project_slug)
        return []


    def _addChannel(self, request, organization_slug, project_slug):
        """Add's a flow binding to a project"""
        data = request.data
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied('Only staff members can do this.')
        project = organization.projects.get(slug=project_slug)
        user = FlowdockUser.objects.get(project=project)

        url = "https://api.flowdock.com/flows/{orgId}/{flowId}/sources?access_token={token}".format(orgId=data['channel']['organization']['parameterized_name'], flowId=data['channel']['parameterized_name'], token=user.oauth_token)
        payload = {
            "name": "ScrumDo - {project_name}".format(project_name=project.name),
            "external_url": "{base_url}/projects/{project_slug}/board".format(base_url=settings.BASE_URL, project_slug=project.slug)
        }

        r = requests.post(url,
                          data=json.dumps(payload),
                          headers={'Content-Type': 'application/json'})
        result = r.json()

        mapping = FlowdockMapping(project=project,
                               flow_slug=data['channel']['parameterized_name'],
                               org_slug=data['channel']['organization']['parameterized_name'],
                               source_id=result['id'],
                               api_token=result['flow_token'],
                               channel_name=data['channel']['name'],
                               channel_id=data['channel']['id'],
                               card_moved=data['card_moved'],
                               card_created=data['new_card'],
                               card_modified=data['card_edited'],
                               comment_created=data['comment_created'])
        mapping.save()
        url = "{host}{url}".format(url=project.get_absolute_url(), host=settings.SSL_BASE_URL)
        # send_flowdock_message(mapping.id, "The ScrumDo project <{project_url}|{project_name}> is now configured to send messages here.".format(project_name=project.name, project_url=url))

        return self._read_project(request, organization_slug, project_slug)



    def _removeChannel(self, request, organization_slug, project_slug):
        """Removes a github repo binding from a project and deletes any webhooks."""
        data = request.data
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied('Only staff members can do this.')
        project = organization.projects.get(slug=project_slug)
        user = FlowdockUser.objects.get(project=project)
        mapping = FlowdockMapping.objects.get(project=project, id=data['channelId'])
        mapping.delete()

        url = "https://api.flowdock.com/flows/{orgId}/{flowId}/sources/{sourceId}?access_token={token}"\
            .format(sourceId=mapping.source_id, orgId=mapping.org_slug, flowId=mapping.flow_slug, token=user.oauth_token)

        r = requests.delete(url)


        return self._read_project(request, organization_slug, project_slug)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug=None):
        data = request.data
        if data['action'] == 'addChannel':
            return self._addChannel(request, organization_slug, project_slug)
        if data['action'] == 'removeChannel':
            return self._removeChannel(request, organization_slug, project_slug)
        return "ok"


