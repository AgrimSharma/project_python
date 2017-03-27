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


from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.template import defaultfilters
from django.contrib import messages # django 1.4
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings
from django.db import IntegrityError

import datetime as dt
from apps.subscription.decorators import *
from apps.subscription.spreedly import Spreedly
from apps.organizations.forms import *
from apps.organizations.models import *
import slumber
from apps.favorites.models import *
import apps.projects.access as access
from apps.projects.limits import org_project_limit, org_extra_limit
from apps.projects.util import generateProjectPrefix, duplicatePrefix
import apps.organizations.signals as signals
from apps.organizations.tasks import exportOrganization
from apps.activities.models import NewsItem

import json

import re
import logging

logger = logging.getLogger(__name__)


@login_required
def organization_points_breakdown(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasReadAccess( request.user ):
        raise PermissionDenied()    
    projects = organization.projects.filter(personal=False, active=True).order_by('category')
    data = []
    current_group = None
    current_group_name = "."
    group_by_project = False
    group_by_category = False
    group_by_people = False
    current_iterations = (request.GET.get("current","off") == "on")
    logger.debug(current_iterations);
    field = request.GET.get("field","projects")
    logger.debug("Grouping by %s" % field)
    if field == 'projects':
        group_by_project = True
    elif field == 'categories':
        group_by_category = True
    elif field == 'people':
        group_by_people = True
        people_map = {}    
    
    if group_by_people:
        for project in projects: 
            if not access.has_read_access(project, request.user):
                continue
            iterations = project.get_current_iterations() if current_iterations else project.iterations.all()
            for iteration in iterations:
                for story in iteration.stories.all():
                    if story.assignee.count() == 0:
                        un = "Unassigned"
                        if un in people_map:
                            current_group = people_map[un]
                        else:                        
                            current_group = {'name':un,'total':0,'markers':[0,0,0,0,0,0,0,0,0,0]}
                            people_map[un] = current_group
                            data.append(current_group);
                        
                        current_group['total'] += story.points_value()
                        current_group['markers'][story.status-1] += story.points_value()        

                    for assignee in story.assignee.all():
                        un = assignee.username
                        if un in people_map:
                            current_group = people_map[un]
                        else:                        
                            current_group = {'name':un,'total':0,'markers':[0,0,0,0,0,0,0,0,0,0]}
                            people_map[un] = current_group
                            data.append(current_group);
                        
                        current_group['total'] += story.points_value()
                        current_group['markers'][story.status-1] += story.points_value()        
    else:
        for project in projects:
            if not access.has_read_access(project, request.user):
                continue            
            pname = project.category if project.category else 'Uncategorized'
            if group_by_category and current_group_name != pname:
                current_group_name = pname
                current_group = {'name':pname,'total':0,'markers':[0,0,0,0,0,0,0,0,0,0]}
                data.append(current_group);
            elif group_by_project:
                current_group = {'name':project.name ,'total':0,'markers':[0,0,0,0,0,0,0,0,0,0]}
                data.append(current_group);
            total = 0
            completed = 0
            iterations = project.get_current_iterations() if current_iterations else project.iterations.all()
            for iteration in iterations:
                for story in iteration.stories.all():
                    current_group['total'] += story.points_value()
                    current_group['markers'][story.status-1] += story.points_value()
            
        
    data = [group for group in data if reduce(lambda a,b:a+b, group['markers'] ) > 0]
    data = sorted(data,key=lambda d:d['name'].lower())
    totals = [d['total'] for d in data]
    
    json_data = json.dumps({'max':max(totals + [0]),'data':data})
    return HttpResponse(json_data, content_type="application/json")

def _disablePersonalProjects(organization):
    for project in organization.projects.filter(personal=True, active=True):
        project.active = False
        project.save()


@login_required
def organization_edit( request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if organization.projects.count() == 1:
        project = Project.objects.get(organization=organization)
        if not access.has_read_access(project,request.user):
            project = None
    else: project = None
    if request.method == "POST" and organization.hasStaffAccess( request.user ):
        hadPersonal = organization.allow_personal
        form = UpdateOrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            messages.add_message(request,messages.INFO,message="Organization Updated")
            form.save()
            logger.debug("%s %s" % (hadPersonal, organization.allow_personal) )
            # if hadPersonal and not organization.allow_personal:
            #     _disablePersonalProjects(organization)
            return HttpResponseRedirect(reverse("organization_detail",  kwargs={'organization_slug':organization.slug}))
    else:
        form = UpdateOrganizationForm(instance=organization)
    organizations = Organization.getOrganizationsForUser( request.user )
    isStaffUser = organization.hasStaffAccess( request.user )
    return render_to_response("organizations/organization_form.html", {
        "organization": organization,
        "organizations": organizations,
        "project": project,
        "form":form,
        "isStaffUser":isStaffUser
      }, context_instance=RequestContext(request))

@login_required
def organization_delete(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if request.method != "POST":
        raise PermissionDenied()
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    
    for team in organization.teams.all():
        for member in team.members.all():
            member.teams.remove(team)
    
    spreedly = Spreedly()
    spreedly.stopAutoRenewForOrganization(organization)
    
    user = request.user
    item = NewsItem(user=user, project=None, icon='building_add' )
    item.text = render_to_string("activities/organization_deleted.txt", {'user':user,'organization':organization} )
    item.save()
    
    redirect_url = "%s" % (settings.SSL_BASE_URL)
    return HttpResponseRedirect(redirect_url)

@login_required
@premium_subscription_check
def organization_extras(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasReadAccess(request.user):
        raise PermissionDenied()

    return render_to_response("organizations/organization_extras.html", {
        "organization": organization
      }, context_instance=RequestContext(request))


@login_required
@expired_subscription_check
def organization_planning(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if organization.hasReadAccess(request.user):
        return render_to_response("organizations/organization_planning.html", {"organization": organization}, context_instance=RequestContext(request))
    else:
        raise PermissionDenied('You do not have access to this organization')

@login_required
@expired_subscription_check
def organization_redirect_to(request, organization_slug):
    # redirect user to project board if user has exactly 1 favorited project
    organization = get_object_or_404(Organization, slug=organization_slug)
    favorite_projects = Favorite.objects.filter(user=request.user, project__organization=organization, project__active=True)\
        .select_related('project').order_by("project__category","project__name")
    favorite_projects = [fav.project for fav in favorite_projects]
    try:
        if len(favorite_projects) is 1:
            return HttpResponseRedirect(reverse("kanban_board", kwargs={'project_slug': favorite_projects[0].slug}))
        else:
            return HttpResponseRedirect(reverse("organization_detail", kwargs={'organization_slug': organization_slug}))
    except:
        return HttpResponseRedirect(reverse("organization_detail", kwargs={'organization_slug': organization_slug}))

@login_required
@expired_subscription_check
def organization_dashboard(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    # Organization.objects.filter(slug=organization_slug).select_related('subscription')[0]
    count_projects = organization.projects.count()
    if count_projects == 1:
        project = Project.objects.get(organization=organization)
        if not access.has_read_access(project, request.user):
            project = None
    else: project = None
    # organizations = Organization.getOrganizationsForUser( request.user )

    if not organization.active:
        logger.info("Re-activating an old deactivated org!")
        organization.active = True
        organization.save()

    favorite_projects = Favorite.objects.filter(user=request.user, project__organization=organization).select_related('project').order_by("-project__active","project__category","project__name")
    favorite_projects = [fav.project for fav in favorite_projects]
    
    # stories = access.getAssignedStories(request.user, organization)
    
    show_first_time = not "seen-org-tip" in request.COOKIES

    now = dt.datetime.now()

    showIntro = (now - request.user.date_joined) < dt.timedelta(days=3)

    # old_free_plan = organization.subscription.plan_id in [1000,1001]
    subscription = organization.subscription

    expiresIn = None
    now = dt.date.today()
    if subscription.is_trial and (subscription.expires - now) < dt.timedelta(7):
        expiresIn = (subscription.expires - now).days + 1

    if not organization.hasReadAccess( request.user ):
        raise PermissionDenied()

    context = {
            "expiresIn": expiresIn,
            "organization": organization,
            # "organizations": organizations,
            "favorite_projects": favorite_projects,
            # "your_stories": stories,
            "show_first_time": show_first_time,
            "showIntro": showIntro,
            "return_type":"queue",
            # "old_free_plan": old_free_plan
            # "project": project
            # "members": members,
            # "projects": projects
          }

    if project:
        context['project'] = project
        
    return render_to_response("organizations/organization_dashboard.html", context, context_instance=RequestContext(request))
    

def handle_organization_create( form , request, projects):
    organization = form.save( commit=False )
    organization.creator = request.user
    
    slug = defaultfilters.slugify( organization.name )[:45]
    c = 0
    while True:
        try:
            Organization.objects.get(slug=slug)
            c += 1
            slug = "%s%d" % (defaultfilters.slugify( organization.name )[:45], c)
        except Organization.DoesNotExist:
            break # finally found a slug that doesn't exist
        
    organization.slug = slug
    organization.save()


    member_team = Team(organization = organization, name="Members", access_type="write")
    member_team.save()
    
    staff_team = Team(organization = organization, name="Account Owner", access_type="staff")
    staff_team.save()
    staff_team.members.add(request.user)
    
    
    # request.user.message_set.create(message="Organization Created.")
    
    try:
        # Store where this user came from via the google analytics tracking cookie.  Example values:
        # 183024036.1310791887.2.2.utmcsr=freshmeat.net|utmccn=(referral)|utmcmd=referral|utmcct=/projects/scrumdo; 
        # 183024036.1310842365.1.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=scrumdo%20harvest
        # 183024036.1311098060.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)
        # Adwords:
        # 37276784.1312040997.1.1.utmgclid=CPCFncq1qaoCFYne4AodhCvMWw|utmccn=(not%20set)|utmcmd=(not%20set)|utmctr=scrum
        
        cookie = request.COOKIES.get("__utmz")
        if re.search("utmgclid", cookie) == None:
            # Referrer based source
            source = re.search("utmcsr=([^|]+)",cookie).group(1)
            mode = re.search("utmcmd=([^|]+)",cookie).group(1)
            organization.source = "%s / %s" % (source, mode)
        else:
            # Adwords based source?
            source = re.search("utmgclid=([^|]+)",cookie).group(1)
            mode = re.search("utmctr=([^|]+)",cookie).group(1)
            organization.source = "Adwords / %s / %s" % (source, mode)
                
        organization.save()        
    except:
        organization.source = ""

    subscription = organization.subscription

    organization.subscription.plan_id = 3043  # 3043 = Premium 100 user plan
    organization.subscription.expires = dt.date.today() + dt.timedelta(days=30)
    organization.subscription.is_trial = True
    organization.subscription.had_trial = True
    organization.subscription.save()

    signals.organization_created.send( sender=request, organization=organization )    

    for project in projects:
        if request.POST.get("move_project_%d" % project.id):
            _move_project_to_organization(project, organization, member_team)
            # member_team.projects.add( project )

    return organization

def _move_project_to_organization(project, organization, member_team):
    project.teams.clear()
    project.organization = organization
    member_team.projects.add(project)
   
    member_team.save()
    if not duplicatePrefix(project, organization):
        project.save()
    else:
        project.prefix = generateProjectPrefix(project)
        project.save()

@login_required
@expired_subscription_check
def export_organization(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasReadAccess( request.user ):
        raise PermissionDenied()



    organizations = Organization.getOrganizationsForUser( request.user )

    if request.method == "POST":
        projects = []
        for key, value in request.POST.iteritems():
            m = re.match("proj_([0-9]+)",key)
            if m and value:
                projects.append(int(m.group(1)) )

        job = FileJob(organization=organization, file_type="org_export", owner=request.user, completed=False)
        job.save()

        exportOrganization.apply_async((job.id, organization.id, projects,
                                        request.POST.get("startDate", None),
                                        request.POST.get("endDate", None)), countdown=3)

        return HttpResponseRedirect(reverse("file_job_download", kwargs={"job_id": job.id}))


    return render_to_response("organizations/organization_export.html", {
        "organization":organization,
        "organizations":organizations,        
        "projects": organization.projects.filter(personal=False).order_by("category","name")
      }, context_instance=RequestContext(request))
    


@login_required
def delete_organization(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if request.method != "POST":
        return HttpResponse("Not Deleted")
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    signals.organization_deleted.send( sender=request, organization=organization )
    for project in organization.projects.all():
        project.organization = None
        project.save()
    for team in organization.teams.all():
        team.delete()
    organization.delete()
    return HttpResponse("Deleted")

@login_required
def track_time(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasReadAccess(request.user):
        raise PermissionDenied()
    return render_to_response("organizations/tracktime.html", {
        "organization":organization,
      }, context_instance=RequestContext(request))



@login_required
def play_getscrumban_game(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasReadAccess(request.user):
        raise PermissionDenied()
    has_access = org_extra_limit.increaseAllowed(organization=organization)
    # http://localhost:8000/api/freegame/createFreeGame
    if has_access:
        api = slumber.API(settings.GETSCRUMBAN_API, append_slash=True)
        result = api.freegame.zz.createFreeGame.post({'secret': 'DSF@#45641DFGkkk817dh7Rpvoi', 'organization_slug': organization.slug})
        url = "http://www.getscrumban.com/game/play/%s" % result['key']
    else:
        result = {}
        url = ""
    return render_to_response("organizations/getscrumban.html", {
        "url": url,
        "organization":organization,
        "game": result,
        "has_access": has_access
      }, context_instance=RequestContext(request))

