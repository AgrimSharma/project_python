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
# License along with this library;  if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.core import serializers
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError

import apps.organizations.tz as tz
import apps.kanban.tasks as kanban_tasks
import apps.projects.tasks as projects_tasks
from apps.kanban.models import KanbanStat
from util import organizationOrNone, generateProjectSlug, generateProjectPrefix, duplicatePrefix
from apps.subscription.decorators import *
from apps.account.models import Account
import apps.github_integration.utils as github_utils

from apps.emailconfirmation.models import EmailAddress

import managers as managers
import apps.kanban.managers as kanban_managers

import signals as signals
from util import reduce_burndown_data
from util import getAllocationsForIteration

import portfolio_managers

import json
import requests
import mixpanel
import math
import logging
import time

from apps.projects.calculation import onDemandCalculateVelocity


logger = logging.getLogger(__name__)


from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from apps.projects.access import *
from apps.projects.models import TimeEntry, FileJob, OfflineJob
from apps.projects.forms import *

from apps.organizations.models import Organization

from apps.classic import models as classic_models

import datetime

from django.contrib import messages
from story_views import handleAddStory



botNames=['googlebot',
            'slurp',
            'twiceler',
            'msnbot',
            'kaloogabot',
            'yodaobot',
            'baiduspider',
            'bingbot',
            'speedy spider',
            'dotbot']




@login_required
@ensure_csrf_cookie
def milestones(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    read_access_or_403(project, request.user)
    return render_to_response("projects/milestones.html", {
       "project": project,
       "organization": project.organization
    }, context_instance=RequestContext(request))

@login_required
def wait_job(request, job_id, template="projects/job_wait.html"):
    job = OfflineJob.objects.get(id=job_id)
    if job.owner != request.user:
        raise PermissionDenied()
    return render_to_response(template, {"job": job,
                                         "url": request.GET.get("redirect_url")},
                              context_instance=RequestContext(request))

@login_required
@ensure_csrf_cookie
def story_queue(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user)
    return render_to_response("projects/story_queue.html", {
       "project": project,
       "organization": project.organization
    }, context_instance=RequestContext(request))

@login_required
def project_tips(request, organization_slug, project_slug=None):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasReadAccess(request.user):
        raise PermissionDenied('You do not have access to that organization')

    if project_slug is None:
        project = None
    else:
        project = get_object_or_404( Project, slug=project_slug )


    return render_to_response("projects/tips.html", {
       "project": project,
       "organization": organization
    }, context_instance=RequestContext(request))

@login_required
@ensure_csrf_cookie
def classic_picker(request):
    return HttpResponseRedirect(reverse('home'))
    # # If a user.account.classic_mode == CLASSIC_FORCE_CLASSIC - go to www
    # # If a user.account.classic_mode == CLASSIC_FORCE_NEW - go to org picker
    # # If a user has no new projects and does have classic projects, redirect to classic WWW immiediately.
    # # If a user has no active classic projects and does have new projects, redirect to normal homepage
    # # If a user has both, display a page prompting which they would prefer to see
    # user = request.user
    # account = Account.objects.get(user=user)
    #
    # # if account.classic_mode == Account.CLASSIC_FORCE_CLASSIC:
    # #     return HttpResponseRedirect(settings.CLASSIC_SITE_URL)
    #
    # if account.classic_mode == Account.CLASSIC_FORCE_NEW:
    #     return HttpResponseRedirect(reverse('home'))
    # 
    # newProjects = 0
    # classicProjects = 0
    # for team in Team.objects.filter(members=request.user, access_type='staff'):
    #     newProjects += Project.objects.filter(organization=team.organization, active=True).count()
    #     classicProjects += classic_models.Project.objects.filter(organization=team.organization, active=True).count()
    #
    # newProjects += Project.objects.filter(teams__members=request.user, active=True).count()
    # classicProjects += classic_models.Project.objects.filter(classic_teams__team__members=request.user, active=True).count()
    #
    # # if newProjects == 0 and classicProjects > 0:
    # #     return HttpResponseRedirect(settings.CLASSIC_SITE_URL)
    #
    # if newProjects > 0 and classicProjects == 0:
    #     return HttpResponseRedirect(reverse('home'))
    #
    # return render_to_response('classic_picker.html', context_instance=RequestContext(request) )

@login_required
@ensure_csrf_cookie
def test_page(request):
    organizations = Organization.getOrganizationsForUser(request.user)
    projects = getProjectsForUser(request.user, organizations[0])
    return render_to_response('test_page.html',{
       "my_organizations": organizations[0],
       "project": projects[1].slug
      }, context_instance=RequestContext(request) )

@login_required
@ensure_csrf_cookie
def home(request, template_name="unauthenticated_homepage_2014_09.html", force_org_view=False):
    fov = request.GET.get('force_org_view', False)

    organizations = Organization.getOrganizationsForUser(request.user)
    if not force_org_view and not fov and len(organizations) == 1:
        return HttpResponseRedirect(organizations[0].redirect_to_url())

    return render_to_response("homepage.html", {
       "my_organizations": organizations,
       "now": datetime.datetime.now()
      }, context_instance=RequestContext(request))


@staff_member_required
@ensure_csrf_cookie
def user_details_by_email(request, email):
    emails = EmailAddress.objects.filter(email__contains=email)

    users = [e.user for e in emails]
    return render_to_response("projects/user_list_details.html",
                              {
                                "users":users
                              },
                              context_instance=RequestContext(request))

@staff_member_required
@ensure_csrf_cookie
def user_details_staff(request, username):
    user = User.objects.get(username=username)
    teams = user.teams.all().order_by("organization__name")
    return render_to_response("projects/user_details.html",
                              {
                                "target_user":user,
                                "teams":teams
                              },
                              context_instance=RequestContext(request))

@login_required
@ensure_csrf_cookie
def planning(request, group_slug, sub_tool="iteration"):
    planningUrl = '{}#/planning/planningcolumn'.format(
                    reverse('project_app', kwargs={'project_slug':group_slug}))
    return HttpResponseRedirect(planningUrl)



@login_required
@ensure_csrf_cookie
def activate( request, group_slug, remove_from_portfolio = None):
    project = get_object_or_404( Project, slug=group_slug )
    admin_access_or_403(project, request.user, ignore_active=True)
    if project.portfolio_level is None and project.project_type != Project.PROJECT_TYPE_PORTFOLIO:
        # non-portfolio project
        project.active = True
        project.save()
    else:
        # protfolio project
        managers.activate_project(project, remove_from_portfolio)
    
    managers.rebuild_project_teams_cache(project)
    managers.rebuild_project_owner_cache(project.organization, project.creator)

    #clear newsitem cache
    managers.clearNewsItemsCache(project.organization, project.slug)
    
    return HttpResponseRedirect( reverse("project_detail", kwargs={"group_slug":project.slug} ) )

@login_required
@ensure_csrf_cookie
def activate_portfolio( request, group_slug ):
    project = get_object_or_404( Project, slug=group_slug )
    if project.project_type != 2:
        #got a portfolio mid level project
        project = project.portfolio_level.portfolio.root

    admin_access_or_403(project, request.user, ignore_active=True)
    managers.activate_project(project)
    managers.rebuild_project_teams_cache(project)
    managers.rebuild_project_owner_cache(project.organization, project.creator)

    #clear newsitem cache
    managers.clearNewsItemsCache(project.organization, project.slug)
    
    return HttpResponseRedirect( reverse("project_detail", kwargs={"group_slug":project.slug} ) )
    
# The project admin page, this is where you can change the title, description, etc. of a project.
@login_required
@ensure_csrf_cookie
def project_admin( request, group_slug ):
    project = get_object_or_404( Project, slug=group_slug )

    admin_access_or_403(project, request.user )

    form = ProjectOptionsForm(instance=project)
    logger.debug(request.POST)
    if request.method == 'POST': # If one of the three forms on the page has been submitted...
        if request.POST.get("action") == "rebuildReports":
            kanban_tasks.scheduleRebuildStepMovements(project, request.user)

        if request.POST.get("action") == "updateIndexes":
            projects_tasks.updateProjectIndexes.delay(project.slug)

        if request.POST.get("action") == "resetBurnup":
            points = project.points_log.all().order_by("-date")
            if len(points) > 0:
                project.burnup_reset = points[0].points_status10
                project.burnup_reset_date = tz.today(project.organization)
                project.save()
            #

        if request.POST.get("action") == "updateProject":
            form = ProjectOptionsForm( request.POST, instance=project)
            logger.debug("updateProject")
            if form.is_valid(): # All validation rules pass
                form.save()
                onDemandCalculateVelocity(project)
                # logger.debug("if form.is_valid() == True")
                #request.user.message_set.create(message="Project options Saved.")
                messages.add_message(request, messages.INFO, "Project options Saved.")
                return HttpResponseRedirect(reverse("project_detail",kwargs={'group_slug':project.slug}))
            else:
                logger.debug("if form.is_valid() == False"); logger.debug(form.errors);
        if request.POST.get("action") == "moveToOrganization":
            organization = get_object_or_404( Organization, id=request.POST.get("organization_id",""))
            user = project.creator
            org = project.organization
            if project.project_type == 2:
                portfolio_managers.move_portfolio_to_org(project, organization)
            else:
                if project.organization:
                    managers.remove_project_from_teams(project)
                project.organization = organization
                project.prefix = generateProjectPrefix(project)
                if duplicatePrefix(project, organization):
                    project.prefix = generateProjectPrefix(project)
                project.save()
                portfolio_managers.remove_project_from_portfolio(project)
                portfolio_managers.clear_story_releases(project)
            owners = organization.getOwnersGroup()
            if owners:
                owners.projects.add(project)
                # update owners project list cache
                managers.rebuild_project_teams_cache(project)
            #request.user.message_set.create(message="Project moved to organization")
            # update user project list cache
            managers.rebuild_staff_teams_cache(organization)
            managers.rebuild_project_owner_cache(org, user)
            
            #clear newsitem cache
            managers.clearNewsItemsCache(org, project.slug)
            managers.clearNewsItemsCache(organization, project.slug)

            messages.add_message(request, messages.INFO, "Project moved to organization")
            return HttpResponseRedirect(reverse("organization_detail",kwargs={'organization_slug':organization.slug}))

        if request.POST.get("action") == "archiveProject":
            managers.archive_project(project)
            # update user project teams cache
            managers.rebuild_project_teams_cache(project)
            # update user project list cache
            managers.rebuild_project_owner_cache(project.organization, project.creator)
            #clear newsitem cache
            managers.clearNewsItemsCache(project.organization, project.slug)
            return HttpResponseRedirect( reverse("project_detail", kwargs={"group_slug":project.slug} ) )

    return HttpResponseRedirect(reverse("project_detail",kwargs={'group_slug':project.slug}))

# Returns a JSON feed for a given project/iteration that can be transformed with some javascript
# into a burn up, burn down, or stacked chart.
@login_required
@ensure_csrf_cookie
def iteration_burndown(request, group_slug, iteration_id):
    project = get_object_or_404( Project, slug=group_slug )
    read_access_or_403(project, request.user )
    iteration = get_object_or_404( Iteration, id=iteration_id )
    try:
        if iteration.start_date:
            start_date_timestamp = int((time.mktime(iteration.start_date.timetuple()) - time.timezone)*1000)
        if iteration.end_date:
            end_date_timestamp = int((time.mktime(iteration.end_date.timetuple()) - time.timezone)*1000)
    except:
        # An invalid date, nothing more we can do.
        return HttpResponse("");

    has_startdate_data = False
    has_enddate_data = False
    highest_total_points = 0
    last_total_points = 0


    points = [[],[],[],[],[],[],[],[],[],[],[],[],[]]

    for log in iteration.points_log.all():

        if iteration.start_date:
            if log.timestamp() > start_date_timestamp and not has_startdate_data and start_date_timestamp != 0:
                # If the first day isn't filled out, give it 0's
                for i in range(13):
                    points[i].append( [start_date_timestamp, 0])

        has_startdate_data = True
        last_total_points = log.points_total
        if iteration.end_date:
            if log.timestamp() == end_date_timestamp :
                has_enddate_data = True
        if highest_total_points < log.points_total:
            highest_total_points = log.points_total
        points[0].append( [log.timestamp(), log.points_total] );
        points[1].append( [log.timestamp(), log.points_status1] );
        points[2].append( [log.timestamp(), log.points_status2] );
        points[3].append( [log.timestamp(), log.points_status3] );
        points[4].append( [log.timestamp(), log.points_status4] );
        points[5].append( [log.timestamp(), log.points_status5] );
        points[6].append( [log.timestamp(), log.points_status6] );
        points[7].append( [log.timestamp(), log.points_status7] );
        points[8].append( [log.timestamp(), log.points_status8] );
        points[9].append( [log.timestamp(), log.points_status9] );
        points[10].append( [log.timestamp(), log.points_status10] );
        points[11].append( [log.timestamp(), log.time_estimated] );
        points[12].append( [log.timestamp(), log.time_estimated_completed] );

    entries = TimeEntry.objects.filter(iteration=iteration).order_by("date")
    entries_series = []
    last_day = None
    last_count = 0
    for entry in entries:
        if entry.timestamp() != last_day:
            if last_day:
                entries_series.append([last_day, last_count]);
            last_day = entry.timestamp()
            # last_count = 0 don't reset so we get cumulative counts for the charts...
        last_count += entry.minutes_spent
    if last_day:
        entries_series.append([last_day, last_count]);

    allocations = getAllocationsForIteration(project, iteration)
    allocated_time = reduce(lambda total,allocation:total+allocation.minutes_allocated, allocations, 0)

    if allocated_time != 0:
        allocated_series = [[e[0],int((allocated_time-e[1])/60)] for e in entries_series]
    else:
        allocated_series = []

    entries_series = [[e[0], int(e[1]/60)] for e in entries_series]

    if not has_enddate_data and iteration.end_date:
        points[0].append( [end_date_timestamp, last_total_points])

    # TODO - filter out time entries not in date ranges.


    # Filter out stuff too early
    if iteration.start_date:
        for i in range(13):
            points[i] = filter(lambda x:x[0]>=start_date_timestamp, points[i])
            entries_series = filter(lambda x:x[0]>=start_date_timestamp, entries_series)

    # Filter out stuff too late
    if iteration.end_date:
        for i in range(13):
            points[i] = filter(lambda x:x[0]<=end_date_timestamp, points[i])
            entries_series = filter(lambda x:x[0]<=end_date_timestamp, entries_series)


    labels = project.statuses()
    labels = ["Total Points"] + list(labels) + ["Estimated Hours", "Completed"]

    # logger.debug( filter(lambda x:x[1]>0,points[11]))
    # logger.debug( filter(lambda x:x[1]>0,points[12]))


    # Convert minutes to hours
    points[11] = [ [d[0],d[1]/60] for d in points[11]]
    points[12] = [ [d[0],d[1]/60] for d in points[12]]

    data = [0] * 15
    for i in range(13):
        data[i] = {"label":labels[i], "data":reduce_burndown_data(points[i])}

    data[11]["hourseries"] = True
    data[12]["hourseries"] = True

    for i in range(1,11):
        data[i]["stack"] = True
        data[i]["statusType"] = i - 1


    # yaxis = 2 = the hourly axis
    data[11]["yaxis"] = 2;
    data[12]["yaxis"] = 2;
    data[13] = {"hourseries":True,"yaxis":2, "label":"Hours Spent", "data":entries_series, "lines":{ "show": True, "fill": False, "opacity":0.5 }, "points":{"radius":2}}
    data[14] = {"hourseries":True,"yaxis":2, "label":"Hours Left", "data":allocated_series, "lines":{ "show": True, "fill": False, "opacity":0.5 }, "points":{"radius":2}}

    json_serializer = serializers.get_serializer("json")()
    result = json.dumps(data)

    if highest_total_points == 0:
        return HttpResponse("[]")

    return HttpResponse(result) #, mimetype='application/json'


# Returns a JSON feed for a given project that can be transformed with some javascript
# into a burn up chart.
@login_required
@ensure_csrf_cookie
def project_burndown(request, group_slug):
    project = get_object_or_404( Project, slug=group_slug )
    read_access_or_403(project, request.user )
    total_points = [];
    claimed_points = [];
    if project.burnup_reset_date == None:
        points_log = project.points_log.all()
    else:
        points_log = project.points_log.filter(date__gte=project.burnup_reset_date)

    for log in points_log:
        total_points.append( [log.timestamp(), max(0,log.points_total - project.burnup_reset)] );
        claimed_points.append( [log.timestamp(), max(0,log.points_status10 - project.burnup_reset)] );

    total_stats = { "label":"Total Points", "data":reduce_burndown_data(total_points)}
    claimed_stats = { "label":"Claimed Points", "data":reduce_burndown_data(claimed_points)}


    json_serializer = serializers.get_serializer("json")()
    result = json.dumps([ total_stats , claimed_stats ])
    return HttpResponse(result) #, mimetype='application/json'



# Form and handler for creating a new project.
@login_required
@ensure_csrf_cookie
def create(request, group_slug, form_class=ProjectForm, template_name="projects/create.html", project_type="standard"):
    organization = get_object_or_404(Organization, slug=group_slug)

    personal = (project_type == "personal")

    if not (organization.hasStaffAccess(request.user) or personal):
        raise PermissionDenied()

    team_options = [(team.id, team.name) for team in organization.teams.all()]
    project_options = [(project.id, project.name) for project in organization.projects.all().filter(personal=False, project_type=1)]
    workflow_options = [('continuous', 'Continuous'), ('iterative', 'Iterative')]
    if project_options:
        project_options.insert(0,(0, 'None'))
    project_form = form_class(request.POST or None, 
                                team_options=team_options, 
                                project_options=project_options, 
                                personal=personal,
                                workflow_options=workflow_options)

    admin_organizations = Organization.getOrganizationsForUser( request.user ) # The user can create projects in organizations the user is an admin in.
    if project_form.is_valid():
        project = managers.create_project(project_form.cleaned_data['name'],
                                   organization,
                                   request.user,
                                   personal,
                                   project_form.cleaned_data.get('Teams',None),
                                   Project.PROJECT_TYPE_KANBAN,
                                   project_form.cleaned_data.get('Workspace', None)
                                   )
        project_flow = project_form.cleaned_data.get('Workspace Flow', None)
        if project is not None and project_flow is not None and project_flow == 'continuous':
            kanban_managers.initContinousProject(project)

        if project is not None:
            mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
            mp.track(organization.slug, 'Create Project')

            managers.clearNewsItemsCache(organization, project.slug) 
            return HttpResponseRedirect(project.get_absolute_url())
        else:
            #request.user.message_set.create(message="This organization is over it's project limit.")
            messages.add_message(request, messages.INFO, "This organization is over it's project limit.")
            return HttpResponseRedirect( reverse("usage") )


    return render_to_response(template_name, {
        "project_form": project_form,
        "admin_organizations":admin_organizations,
        "organization":organization,
        "personal": personal
    }, context_instance=RequestContext(request))




@login_required
@ensure_csrf_cookie
def delete(request, group_slug=None, redirect_url=None):
    project = get_object_or_404(Project, slug=group_slug)
    project_slug = project.slug 
    org = project.organization
    admin_access_or_403(project, request.user )
    if not redirect_url:
        redirect_url = reverse('home')

    managers.delete_project(project)

    #clear newsitem cache
    managers.clearNewsItemsCache(org, project_slug) 
    #request.user.message_set.create(message=_("Project %(project_name)s deleted.") % {"project_name": project.name})
    messages.add_message(request, messages.INFO, _("Project %(project_name)s deleted.") % {"project_name": project.name})

    return HttpResponseRedirect(redirect_url)





@login_required
@expired_subscription_check
@ensure_csrf_cookie
def project_detail_picker(request, group_slug):
    """ The old project detail request, now just redirects to the board. """
    project = get_object_or_404(Project, slug=group_slug)
    read_access_or_403(project, request.user )
    return redirect("kanban_board",project_slug=group_slug)



@login_required
@expired_subscription_check
@ensure_csrf_cookie
def project(request, group_slug=None, form_class=ProjectUpdateForm,
        template_name="projects/project.html"):
    project = get_object_or_404(Project, slug=group_slug)
    read_access_or_403(project, request.user )
    if not request.user.is_authenticated():
        is_member = False
    else:
        is_member = project.user_is_member(request.user)

    action = request.POST.get("action")
    if action == "update":
        write_access_or_403(project, request.user )
        project_form = form_class(request.POST, instance=project)
        if project_form.is_valid():
            project = project_form.save()
    else:
        project_form = form_class(instance=project)

    add_story_form = handleAddStory(request, project)

    now = datetime.datetime.now()
    showIntro = (now - request.user.date_joined) < datetime.timedelta(days=3)
    kanban_stat = None

    if project.project_type == Project.PROJECT_TYPE_SCRUM:
        template_name = "projects/scrum_project.html"
    else:
        template_name = "projects/kanban_project.html"
        stats = KanbanStat.objects.filter(project=project).order_by("-created")[:1]
        logger.debug(stats)
        if len(stats) > 0:
            kanban_stat = stats[0]

    return render_to_response(template_name, {
        "project_form": project_form,
        "add_story_form": add_story_form,
        "project": project,
        "showIntro":showIntro,
        "organization": organizationOrNone(project),
        "group": project, # @@@ this should be the only context var for the project
        "is_member": is_member,
        "current_view":"project_page",
        "kanban_stat":kanban_stat
    }, context_instance=RequestContext(request))




# Drives the prediction page
# example: /projects/project/sch-r180-dashboards/project_prediction
@login_required
@ensure_csrf_cookie
def project_prediction(request, group_slug):
    project = get_object_or_404(Project, slug=group_slug)
    read_access_or_403(project, request.user )
    stories = project.get_default_iteration().stories.exclude(status=Story.STATUS_DONE).order_by("rank")

    # there is a form on the page with velocity, iteration length, and carry over.
    # IF they're filled out, we should override the default values.
    requested_velocity = request.GET.get("velocity","x");
    if requested_velocity.isdigit():
        velocity = int( requested_velocity )
    else:
        velocity = project.velocity
    if velocity == 0 or velocity == None:
        # A default velocity just in case this project doesn't have one yet.
        velocity = 25
    requested_length = request.GET.get("iteration_length","x")
    if requested_length.isdigit():
        iteration_length = int( requested_length )
    else:
        iteration_length = 14
    carry_over = (request.GET.get("carry_over","x") == "on")


    points_left = velocity
    temp_stories = []
    predictions = []
    iteration_number = project.iterations.count()
    start_date = datetime.date.today()
    current_iterations = project.get_current_iterations()
    unsized_stories = []
    total_points = 0

    # Find when the last scheduled iteration ends.
    for iteration in current_iterations:
        if iteration.end_date is not None and iteration.end_date > start_date:
            start_date = iteration.end_date

    total = 0
    for story in stories:
        total += story.points_value()

    if stories.count() > 0:
        average = int( request.GET.get('average',total / stories.count()) )
    else:
        average = 0

    # loop through the stories, and try to put them into a predicted iteration.
    for story in stories:
        if story.points == "?":
            points = average
        else:
            points = story.points_value()

        if points > points_left:
            record_prediction(predictions,temp_stories,iteration_number,start_date,iteration_length,points_left,average)
            iteration_number += 1
            if carry_over:
                points_left += velocity
            else:
                points_left = velocity
            temp_stories = []
            start_date += datetime.timedelta(days=iteration_length)
        if story.points == "?":
            unsized_stories.append(story)
        points_left -= int(points)
        total_points += points
        temp_stories.append(story)

    record_prediction(predictions,temp_stories,iteration_number,start_date,iteration_length,points_left,average)

    return render_to_response("projects/project_prediction.html", {
        "project": project,
        "predictions": predictions,
        "average": average,
        "velocity":velocity,
        "total_points":total_points,
        "ideal_iterations":int(math.ceil(total_points/velocity)),
        "predicted_iterations":len(predictions),
        "unsized_stories":unsized_stories,
        "carry_over": carry_over,
        "iteration_length":iteration_length,
        "iterations": project.iterations.all().order_by("-end_date")
    }, context_instance=RequestContext(request))


def record_prediction(predictions, stories,iteration_number,start_date,iteration_length,points_left, average):
    points = 0
    avgStories = 0
    for story in stories:
        if story.points == "?":
            p = average
            avgStories += 1
        else:
            p = story.points_value()
        points += p
    predictions.append( { "avgStories":avgStories, "carried":points_left, "stories":stories , "points":points, "num":iteration_number, "start":start_date, "end":(start_date +  datetime.timedelta(days=(iteration_length-1))) } )


@login_required
@ensure_csrf_cookie
def file_job_download(request, job_id, template="projects/job_download.html"):
    job = FileJob.objects.get(id=job_id)
    if job.owner != request.user:
        raise PermissionDenied()
    return render_to_response(template, { "job":job }, context_instance=RequestContext(request))

@login_required
def file_job_download_file(request, job_id):
    job = FileJob.objects.get(id=job_id)
    if job.owner != request.user:
        raise PermissionDenied()
    return HttpResponseRedirect( job.attachment_file.url )


@login_required
@ensure_csrf_cookie
def project_app(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    read_access_or_403(project, request.user)
    return render_to_response("projects/project.html",
                              {
                                  'project': project,
                                  'organization': project.organization,
                                  'can_write': has_write_access(project, request.user)
                              },
                              context_instance=RequestContext(request))