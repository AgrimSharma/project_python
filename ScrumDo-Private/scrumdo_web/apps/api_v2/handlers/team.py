from common import *
from apps.activities.models import NewsItem
from apps.organizations.models import Team, TeamInvite
from apps.organizations.util import team_invite
import apps.projects.tasks as projects_tasks
from apps.projects.access import team_admin_access_or_403
from apps.projects.managers import getTeamMembers
from django.contrib.auth.models import User


class TeamHandler(BaseHandler):
    model = Team
    allowed_methods = ('GET', 'PUT', 'POST', "DELETE")
    fields = ('members',
              'name',
              'id',
              'assignable',
              'access_type',
              ('projects', ('slug', 'name')))

    write_fields = ("name", "access_type", 'assignable')

    def _setFields(self, data, step):
        for field in TeamHandler.write_fields:
            if field in data:
                setattr(step, field, data[field])


    def _check_parents_access(self, organization, child, team):
        for parent in child.parents.all():
            if parent in team.projects.all():
                return True
            if self._check_parents_access(organization, parent, team):
                return True
        return False

    def _check_child_access(self, organization, parent, team):
        for child in parent.children.all():
            if child in team.projects.all():
                return True
            if self._check_child_access(organization, child, team):
                return True
        return False
    
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None):
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasReadAccess(request.user):
            raise PermissionDenied('You do not have access to view this')
        
        # return project specific teams for project settings page
        allTeams = {'parent_teams': [], 'child_teams': [], 'self_teams': []}
        trackTeams= {}
        if project_slug is not None:
            org, project = checkOrgProject(request, organization_slug, project_slug, True)
            teams = organization.teams.all().prefetch_related("projects", "members")
            
            for team in teams:
                if project in team.projects.all():
                    allTeams['self_teams'].append(team)
                    trackTeams[team.id] = team
                if self._check_parents_access(organization, project, team) and \
                team.id not in trackTeams:
                    allTeams['parent_teams'].append(team)
                    trackTeams[team.id] = team
                if self._check_child_access(organization, project, team) and \
                team.id not in trackTeams:
                    allTeams['child_teams'].append(team)
                    trackTeams[team.id] = team
                
            return allTeams

        if organization.hasStaffAccess(request.user):
            teams = organization.teams.all()
        else:
            teams = organization.teams.filter(members=request.user)

        return teams

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, team_id):
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied('You do not have access to do this')

        team = organization.teams.get(id=team_id)
        users = list(team.members.all())
        team.members.clear()
        team.projects.clear()
        team.delete()
        for user in users:
            projects_tasks.queueRebuildUserProjectListCache(organization, user)
        return {}


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, team_id=None):
        data = request.data
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied('You do not have access to do this')

        team = organization.teams.get(id=team_id)
        self._setFields(data, team)
        team.save()
        projects_tasks.queueRebuildTeamProjectListCache(organization, team)
        return team

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, team_id=None, action=None):
        data = request.data

        organization = Organization.objects.get(slug=organization_slug)
        # except user add/remove action
        # would chack for team admin access for these actions
        if not organization.hasStaffAccess(request.user) and action != 'inviteuser' and action != 'removeuser':
            raise PermissionDenied('You do not have access to do this')
        
        if team_id is not None and action != 'removeuserallteams':
            team = organization.teams.get(id=team_id)

        if action == 'addproject':
            return self.addProject(request, organization, team, data)

        if action == 'removeproject':
            return self.removeProject(request, organization, team, data)

        if action == 'removeuser':
            # check if user has admin access to all projects in this team
            team_admin_access_or_403(team, request.user,ignore_active=True)
            return self.removeUser(request, organization, team, data)
        
        if action == 'removeuserallteams':
            try:
                user_id = int(data['user_id'])
                user = User.objects.get(id=user_id)
            except  User.DoesNotExist: 
                return 'User not found'
            teams = organization.teams.filter(members=user)
            for team in teams:
                self.removeUser(request, organization, team, data)
            return 'ok'

        if action == 'inviteuser':
            # check if user has admin access to all projects in this team
            team_admin_access_or_403(team, request.user, ignore_active=True)
            return self.inviteUser(request, organization, team, data)

        return self.createTeam(request, organization, data)

    def removeProject(self, request, organization, team, data):
        project = organization.projects.get(slug=data['project_slug'])
        team.projects.remove(project)
        projects_tasks.queueRebuildTeamProjectListCache(organization, team)
        return team

    def addProject(self, request, organization, team, data):
        project = organization.projects.get(slug=data['project_slug'])
        team.projects.add(project)
        projects_tasks.queueRebuildTeamProjectListCache(organization, team)
        return team

    def removeUser(self, request, organization, team, data):
        user = team.members.get(id=data['user_id'])
        team.members.remove(user)
        projects_tasks.queueRebuildUserProjectListCache(organization, user)
        return team

    def inviteUser(self, request, organization, team, data):
        for user in data['users']:
            if len(user['name']) == 0:
                continue
            result, reason = team_invite(organization, team, user['name'], request.user)
            user['result'] = {'success': result, 'reason': reason}
        projects_tasks.queueRebuildTeamProjectListCache(organization, team)
        return {'users': data['users'], 'team': team}

    def createTeam(self, request, organization, data):
        team = Team(organization=organization, name=data['name'], access_type='write')
        team.save()
        item = NewsItem(user=request.user, icon='fa_users')
        item.text = "Team %s created" % data['name']
        item.save()
        return team


class ProjectTeamHandler(BaseHandler):
    allowed_methods = ('GET', )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if project.project_type == Project.PROJECT_TYPE_PORTFOLIO:
            # if Its is a Portfolio Show Staff Members also
            return getTeamMembers(project, include_staff = True)
        else:
            return getTeamMembers(project, include_staff = False)