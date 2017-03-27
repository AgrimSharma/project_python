# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings
from django.core.exceptions import PermissionDenied

from django.contrib import messages # django 1.4
import random
import string
from apps.projects.limits import org_user_limit
from apps.projects.models import Project
from apps.organizations.forms import *
from apps.organizations.models import *
from django.contrib import messages # django 1.4
from apps.organizations.models import Team
import apps.projects.access as access
import sys, traceback
from apps.brake.decorators import ratelimit
from apps.account.forms import SignupForm

import mixpanel



import logging

logger = logging.getLogger(__name__)

def _isAdmin( user, organization ):
    return Organization.objects.filter( teams__members = user , teams__access_type="admin", teams__organization=organization).count() > 0

@login_required
def team_add_project(request, organization_slug, team_id ):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    team = get_object_or_404(Team, id=team_id)
    if team.organization != organization:
        raise PermissionDenied() # Shenanigans
    project_id = request.POST.get("project")
    project = get_object_or_404(Project, id=project_id)    
    if project.personal:
        raise PermissionDenied() # Shenanigans
        
    if project.organization != organization:
        raise PermissionDenied() # Shenanigans
    team.projects.add(project)
    return team_detail(request, organization_slug, team_id)


# def google_auth_team_accept(request, key):



@login_required
def logged_in_team_invite_accept(request, key):
    try:
        invite = TeamInvite.objects.get(key=key)
        team = invite.team
        team.members.add(request.user)
        mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
        mp.track(team.organization.slug, "Accept Invite on existing account")

        invite.delete()
        return HttpResponseRedirect(reverse("classic_picker"))
    except TeamInvite.DoesNotExist:
        return render_to_response("organizations/invite_missing.html", context_instance=RequestContext(request))


@ratelimit(rate='100/h', block=True, method=['POST'])
def team_invite_accept(request, key):
    try:
        invite = TeamInvite.objects.get(key=key)
        team = invite.team
        if request.method == "POST":
            form = SignupForm(request.POST)
            if form.is_valid():
                username, password = form.save()
                user = authenticate(username=username, password=password)
                auth_login(request, user)
                team.members.add(user)
                invite.delete()
                mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
                mp.track(team.organization.slug, "Accept Invite")
                return HttpResponseRedirect(reverse("classic_picker"))
        else:
            form = SignupForm(initial={'email': invite.email_address, 'company': 'invited'})
            mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
            mp.track(team.organization.slug, "View Invite")

        return render_to_response("organizations/invite_accept.html", {'invite':invite, "form": form}, context_instance=RequestContext(request))
    except TeamInvite.DoesNotExist:
        return render_to_response("organizations/invite_missing.html", context_instance=RequestContext(request))



@login_required
def team_remove_project(request, organization_slug, team_id, project_id):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    team = get_object_or_404(Team, id=team_id)
    if team.organization != organization:
        raise PermissionDenied()  # Shenanigans!
    project = Project.objects.get(id=project_id) 
    team.projects.remove(project)
    return HttpResponse("OK")

@login_required    
def team_remove_member(request, organization_slug, team_id, member_id):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    team = get_object_or_404(Team, id=team_id)
    if team.organization != organization:
        raise PermissionDenied() # Shenanigans!
    
    user = User.objects.filter(id=member_id)[0]
    if user == request.user and team.access_type=="staff":
        return HttpResponse("Can't remove yourself from the staff group.")
    else:
        team.members.remove(user);
        team.save()
    return HttpResponse("OK")
    
@login_required   
def team_summary(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    organizations = Organization.getOrganizationsForUser( request.user )
    if organization.hasStaffAccess(request.user):
        teams = organization.teams.all().order_by("name")
    else:
        teams = organization.teams.filter(members=request.user).order_by("name")
    
    if organization.projects.count() == 1:
        project = Project.objects.get(organization=organization)
        if not access.has_read_access(project,request.user):
            project = None
    else: project = None

    return render_to_response("organizations/organization_teams.html", {
        "organization": organization,
        "organizations": organizations,
        "project": project,
        "teams": teams
      }, context_instance=RequestContext(request))

@login_required   
@csrf_protect
def team_detail(request, organization_slug, team_id, message=""):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    team = get_object_or_404(Team, id=team_id)
    
    if not (organization.hasStaffAccess( request.user ) or team.hasMember(request.user) ):
        raise PermissionDenied()
    

    if team.organization != organization:
        raise PermissionDenied() # Shenanigans!
        
    organizations = Organization.getOrganizationsForUser( request.user )

    return render_to_response("organizations/organization_team.html", {
        "team": team,
        "organization": organization,
        "organizations": organizations,
        "message":message
      }, context_instance=RequestContext(request))


@login_required   
def team_delete(request, organization_slug, team_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    team = get_object_or_404(Team, id=team_id)
    if team.organization != organization:
        raise PermissionDenied()
    if team.access_type == 'staff' and organization.teams.filter(access_type='staff').count() < 2:
        messages.info(request, "Error. There should always be at least one staff team.")
    else: team.delete()
    return HttpResponseRedirect(reverse("team_summary",  kwargs={'organization_slug':organization.slug}))


@login_required   
def team_create(request, organization_slug, team_id=''):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if request.method == 'POST': # If the form has been submitted...
        if team_id: #if the user want to rename the team
            team = get_object_or_404(Team, id=team_id)
            form = EditTeamForm(request.POST, instance=team)
        else:
            form = TeamForm(request.POST)

        if form.is_valid(): # All validation rules pass
            team = form.save( commit=False )
            team.organization = organization
            team.save()
            if team_id:
                messages.success(request, "Team Updated.")
            else:
                messages.success(request, "Team Created.")
            return HttpResponseRedirect(reverse("team_summary",  kwargs={'organization_slug':organization.slug}))
    else:
        if team_id:
            team = get_object_or_404(Team, id=team_id)
            form = EditTeamForm(instance=team)
        else:
            form = TeamForm()

    organizations = Organization.getOrganizationsForUser( request.user )

    return render_to_response("organizations/create_team.html", {
        "form": form,
        "organization": organization,
        "organizations": organizations,
        "team_id": team_id,
      }, context_instance=RequestContext(request))

@login_required
def delete_team_invite_pending(request, invite_id, organization_slug, team_id):
    team = get_object_or_404(Team, id=team_id)
    team_invite = get_object_or_404(TeamInvite, pk=invite_id)
    team_invite.delete()
    return HttpResponseRedirect(reverse('team_detail', args=[organization_slug, team.id]))

