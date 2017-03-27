from .common import *
from django.conf import settings
from apps.projects.models import Project
from apps.github_integration.models import GithubOrganization, GithubTeam, GithubCredentials, GithubBinding
from apps.extras.manager import manager as extras_manager
from apps.extras.models import SyncronizationQueue
import apps.github_integration.utils as github_utils
import apps.github_integration.tasks as github_tasks
from apps.github_integration.models import GithubUser

from apps.organizations.models import Team

import slumber


class GithubAccountHandler(BaseHandler):
    allowed_methods = ('GET', 'DELETE')
    fields = ('github_username',)
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request):
        auth_url = "%s?client_id=%s&scope=repo,read:org,write:repo_hook,user,repo:status&redirect_uri=%s/github/login_associate_callback" % (settings.GITHUB_AUTH_URL, settings.GITHUB_CLIENT_ID, settings.SSL_BASE_URL)
        return {'login_url': auth_url,
                'accounts': GithubUser.objects.filter(user=request.user)}

    def delete(self, request, *args, **kwargs):
        user = GithubUser.objects.get(user=request.user)
        user.delete()
        return 'ok'


class GithubExtraHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None):
        if not project_slug:
            try:
                return self._read_organization(request, organization_slug)
            except slumber.exceptions.HttpClientError as e:
                if e.response.status_code == 401:
                    return {'configured': True, 'error': 'bad_credentials', 'auth_url': github_utils.org_auth_url(organization_slug)}
                return {'error': 'could_not_load', 'auth_url': github_utils.org_auth_url(organization_slug)}
        else:
            try:
                return self._read_project(request, organization_slug, project_slug)
            except slumber.exceptions.HttpClientError as e:
                if e.response.status_code == 401:
                    return {'configured': True, 'error': 'bad_credentials', 'auth_url': github_utils.project_auth_url(project_slug)}
                return {'error': 'could_not_load', 'auth_url': github_utils.project_auth_url(project_slug)}


    def _read_project(self, request, organization_slug, project_slug):
        organization = Organization.objects.get(slug=organization_slug)
        project = organization.projects.get(slug=project_slug)
        if not has_admin_access(project, request.user):
            raise PermissionDenied("Only admins can access this")
        try:
            credentials = GithubCredentials.objects.get(project=project)
            api = slumber.API("https://api.github.com", append_slash=False)
            github_organizations = api.user.orgs.get(access_token=credentials.oauth_token)

            github_repos = []
            github_repos += api.user.repos.get(access_token=credentials.oauth_token)

            for organization in github_organizations:
                github_org = api.orgs(organization['login']).get(access_token=credentials.oauth_token)
                repo_count = github_org['total_private_repos'] + github_org['public_repos']
                for page in xrange(1, repo_count, 100):
                    github_repos += api.orgs(organization['login']).repos.get(type='all',
                                                                              page=int(page/100)+1,
                                                                              per_page=100,
                                                                              access_token=credentials.oauth_token)



            github_repos = [{'name': repo['name'], 'full_name': repo['full_name']} for repo in github_repos]
            k = {}
            github_uniq_repos = []
            for r in github_repos:
                if r["name"] not in k: 
                    k[r["name"]] = True
                    github_uniq_repos.append(r)
                    
            github_repos = sorted(github_uniq_repos, key=lambda r: r['full_name'])

            existing_configs = GithubBinding.objects.filter(project=project)

            return {'configured': True,
                    'auth_url': github_utils.project_auth_url(project_slug),
                    'github_repos': github_repos,
                    'existing_configs': existing_configs}
        except GithubCredentials.DoesNotExist:
            return {'configured': False, 'auth_url': github_utils.project_auth_url(project_slug)}


    def _read_organization(self, request, organization_slug):
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied("Only admins can access this")
        try:
            gho = GithubOrganization.objects.get(organization=organization)
            ghoteams = GithubTeam.objects.filter(team__organization=organization)
            configured_teams = [{'team_name': team.team.name,
                      'last_sync': team.last_sync} for team in ghoteams]

            api = slumber.API("https://api.github.com", append_slash=False)
            github_organizations = api.user.orgs.get(access_token=gho.oauth_token)

            github_teams = []
            github_repos = []
            if gho.github_organization_name:
                teamHash = {team.github_team_id:team for team in ghoteams}
                # permission: "admin",
                # id
                # slug: "owners",
                # name: "Owners"
                github_org = api.orgs(gho.github_organization_name).get(access_token=gho.oauth_token)

                repo_count = github_org['total_private_repos'] + github_org['public_repos']

                github_teams = api.orgs(gho.github_organization_name).teams.get(access_token=gho.oauth_token)
                github_teams = [{'id':team['id'],
                                 'permission':team['permission'],
                                 'name':team['name'],
                                 'sync':team['id'] in teamHash} for team in github_teams]

                github_repos = []
                for page in xrange(1, repo_count, 100):
                    github_repos +=  api.orgs(gho.github_organization_name).repos.get(type='all',
                                                                                      page=int(page/100)+1,
                                                                                      per_page=100,
                                                                                      access_token=gho.oauth_token)

                github_repos = [{'name': repo['name'], 'full_name': repo['full_name']} for repo in github_repos]
                github_repos = sorted(github_repos, key=lambda r: r['full_name'])

            return {'configured': True,
                    'github_username': gho.github_username,
                    'github_organization_name': gho.github_organization_name,
                    'configured_teams': configured_teams,
                    'github_organizations': github_organizations,
                    'github_teams': github_teams,
                    'github_repos': github_repos,
                    'auth_url': github_utils.org_auth_url(organization_slug)
            }
        except GithubOrganization.DoesNotExist:
            return {'configured': False, 'auth_url': github_utils.org_auth_url(organization_slug)}


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug):
        organization = Organization.objects.get(slug=organization_slug)
        data = request.data
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied("Only admins can access this")
        gho = GithubOrganization.objects.get(organization=organization)
        gho.github_organization_name = data['github_organization_name']
        gho.save()
        for team in data['github_teams']:
            if team['sync']:
                self._setSync(team, organization, gho.github_organization_name)
            else:
                self._removeSync(team, organization)

        return self._read_organization(request, organization_slug)

    def _removeSync(self, team, organization):
        try:
            team = GithubTeam.objects.get(team__organization=organization, github_team_id=team['id'])
            team.delete()
        except GithubTeam.DoesNotExist:
            pass

    def _setSync(self, team, organization, github_organization_name):
        try:
            GithubTeam.objects.get(team__organization=organization, github_team_id=team['id'])
        except GithubTeam.DoesNotExist:
            newTeam = GithubTeam(github_team_id=team['id'])
            newTeam.github_organization_name = github_organization_name

            scrumdoTeam = Team(organization=organization, name="%s (GitHub)" % team['name'])
            if team['permission'] == 'admin':
                scrumdoTeam.access_type = 'admin'
            elif team['permission'] == 'pull':
                scrumdoTeam.access_type = 'read'
            else:
                scrumdoTeam.access_type = 'write'
            scrumdoTeam.save()
            newTeam.team = scrumdoTeam
            newTeam.save()

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, project_slug):
        project = Project.objects.get(slug=project_slug)
        return []

    def _importProject(self, request, organization_slug):
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied('Only staff members can do this.')
        data = request.data
        project = github_utils.importProject(request,
                                   request.user,
                                   organization,
                                   data['project_slug'],
                                   data['upload_issues'],
                                   data['download_issues'],
                                   data['close_on_delete'],
                                   data['commit_messages'])
        extras_manager.queueSyncAction("github", project, SyncronizationQueue.ACTION_INITIAL_SYNC)

    def _addRepo(self, request, organization_slug, project_slug):
        """Add's a github repo binding to a project and triggers an initial sync"""
        data = request.data
        organization = Organization.objects.get(slug=organization_slug)
        # if not organization.hasStaffAccess(request.user):
        #     raise PermissionDenied('Only staff members can do this.')
        project = organization.projects.get(slug=project_slug)
        if not has_read_access(project, request.user):
            raise PermissionDenied('Only admins can do this.')

        binding = GithubBinding(project=project, github_slug=data['repo'],
                                upload_issues=data['upload_issues'], download_issues=data['download_issues'],
                                delete_issues=data['close_on_delete'], log_commit_messages=data['commit_messages'],
                                commit_status_updates=data['commit_messages'])
        binding.save()
        credentials = GithubCredentials.objects.get(project=project)
        github_utils.setupCallbacks(credentials.oauth_token, binding, project)
        extras_manager.queueSyncAction("github", project, SyncronizationQueue.ACTION_INITIAL_SYNC)
        return self._read_project(request, organization_slug, project_slug)

    def _removeRepo(self, request, organization_slug, project_slug):
        """Removes a github repo binding from a project and deletes any webhooks."""
        data = request.data
        organization = Organization.objects.get(slug=organization_slug)
        project = organization.projects.get(slug=project_slug)

        if not has_read_access(project, request.user):
            raise PermissionDenied('Only admins can do this.')

        binding = GithubBinding.objects.get(project=project, id=data['binding'])
        credentials = GithubCredentials.objects.get(project=project)

        github_utils.removeCallbacks(credentials.oauth_token, binding, project)

        binding.delete()

        return self._read_project(request, organization_slug, project_slug)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug=None):
        data = request.data
        if data['action'] == 'forceSync':
            project = Project.objects.get(slug=project_slug)
            extras_manager.queueSyncAction('github', project, SyncronizationQueue.ACTION_SYNC_REMOTE)
        if data['action'] == 'importProject':
            self._importProject(request, organization_slug)
        if data['action'] == 'addRepo':
            return self._addRepo(request, organization_slug, project_slug)
        if data['action'] == 'removeRepo':
            return self._removeRepo(request, organization_slug, project_slug)
        github_tasks.syncronize_teams.delay(organization_slug)
        return "ok"


