from .common import *

from django.conf import settings

from apps.projects.models import Project
import apps.slack.util as util
from apps.slack.models import *
from apps.slack.tasks import send_slack_message
import requests


class SlackExtraHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None):
        try:
            return self._read_project(request, organization_slug, project_slug)
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                return {'configured': True, 'error': 'bad_credentials', 'auth_url': util.slack_auth_url(project_slug)}
            return {'error': 'could_not_load', 'auth_url': util.slack_auth_url(project_slug)}

    def _read_project(self, request, organization_slug, project_slug):
        organization = Organization.objects.get(slug=organization_slug)
        project = organization.projects.get(slug=project_slug)
        if not has_admin_access(project, request.user):
            raise PermissionDenied("Only admins can access this")
        try:
            credentials = SlackUser.objects.get(project=project)

            result = requests.get("https://slack.com/api/channels.list?token=%s" % credentials.oauth_token).json()
            if not result['ok']:
                return {'configured': True, 'error': 'bad_credentials', 'auth_url': util.slack_auth_url(project_slug)}

            channels = result['channels']
            groups = requests.get("https://slack.com/api/groups.list?token=%s" % credentials.oauth_token).json()['groups']
            channels = channels + groups

            return {'configured': True,
                    'auth_url': util.slack_auth_url(project_slug),
                    'auth_user': credentials.slack_username,
                    'channels': channels,
                    'mappings': SlackMapping.objects.filter(project=project)
                    }
        except SlackUser.DoesNotExist:
            return {'configured': False, 'auth_url': util.slack_auth_url(project_slug)}

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, project_slug):
        project = Project.objects.get(slug=project_slug)
        return []


    def _addChannel(self, request, organization_slug, project_slug):
        """Add's a github repo binding to a project and triggers an initial sync"""
        data = request.data
        organization = Organization.objects.get(slug=organization_slug)
        project = organization.projects.get(slug=project_slug)
        if not has_admin_access(project, request.user):
            raise PermissionDenied('Only staff members and project admins can do this.')

        mapping = SlackMapping(project=project,
                               channel_name=data['channel']['name'],
                               channel_id=data['channel']['id'],
                               card_moved=data['card_moved'],
                               card_created=data['new_card'],
                               card_modified=data['card_edited'],
                               comment_created=data['comment_created'])
        mapping.save()
        url = "{host}{url}".format(url=project.get_absolute_url(), host=settings.SSL_BASE_URL)
        send_slack_message(mapping.id, "The ScrumDo project <{project_url}|{project_name}> is now configured to send messages here.".format(project_name=project.name.encode("UTF-8"), project_url=url))

        return self._read_project(request, organization_slug, project_slug)



    def _removeChannel(self, request, organization_slug, project_slug):
        """Removes a github repo binding from a project and deletes any webhooks."""
        data = request.data
        organization = Organization.objects.get(slug=organization_slug)
        project = organization.projects.get(slug=project_slug)
        if not has_admin_access(project, request.user):
            raise PermissionDenied('Only staff members and project admins can do this.')
        mapping = SlackMapping.objects.get(project=project, id=data['channelId'])
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


