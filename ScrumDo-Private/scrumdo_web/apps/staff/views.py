from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Max
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core import serializers
from django.db import connection

from apps.projects.models import Project, SiteStats
from apps.organizations.models import Organization
from apps.subscription.models import SubscriptionStats, Subscription
from apps.emailconfirmation.models import EmailAddress

import datetime
import time
import json

import logging

logger = logging.getLogger(__name__)

@staff_member_required
def subscribers(request):
    organizations = Organization.objects.filter(subscription__is_trial=False,
                                                subscription__total_revenue__gt=0,
                                                subscription__active=True).order_by("-created")
    organizations = [o for o in organizations if o.subscription.plan.price_val > 0]
    return render_to_response('staff/subscribers.html', {'title': 'Recent Signups', 'organizations': organizations}, context_instance=RequestContext(request))

@staff_member_required
def recentstats(request):
    twoweeksago = datetime.date.today() - datetime.timedelta(days=14)
    organizations = Organization.objects.filter(created__gte=twoweeksago).order_by("-created")

    return render_to_response('staff/recent_stats.html', {'title': 'Recent Signups', 'organizations': organizations}, context_instance=RequestContext(request))

@staff_member_required
def trialusers(request):
    organizations = Organization.objects.filter(
                                                subscription__is_trial=True,
                                                subscription__active=True,
                                                subscription__expires__gte=datetime.date.today()
                                                ).order_by("-created")
    return render_to_response('staff/recent_stats.html', {'title': 'Trial Users', 'organizations': organizations}, context_instance=RequestContext(request))


@staff_member_required
def userlookup(request):
    email = request.POST.get('email')
    emails = EmailAddress.objects.filter(email__contains=email)
    users = [e.user for e in emails]
    logger.info("%s searched for %s" % (request.user.username, email))
    return render_to_response('staff/user_details.html', {'users': users}, context_instance=RequestContext(request))


@staff_member_required
def staff_home(request):
    try:
        lastStat = SubscriptionStats.objects.all().order_by("-date")[0]
    except IndexError:
        lastStat = {'paid_orgs':0, 'safe_revenue':0}
    trials = Subscription.objects.filter(is_trial=True, active=True, expires__gte=datetime.date.today()).count()
    return render_to_response('staff/staff_home.html', {'trials': trials, 'lastStat': lastStat}, context_instance=RequestContext(request))

@staff_member_required
def scrumstats(request):
    topProjects = Project.objects.\
        filter(project_type=Project.PROJECT_TYPE_SCRUM, active=True).\
        annotate(num_stories=Count('stories')).\
        filter(num_stories__gt=0, organization__subscription__is_trial=False).\
        order_by("-num_stories")[:50]
    return render_to_response('staff/scrum_stats.html', {'top_projects': topProjects}, context_instance=RequestContext(request))


@staff_member_required
def kanbanstats(request):
    topProjects = Project.objects.\
        filter(project_type=Project.PROJECT_TYPE_KANBAN, active=True).\
        annotate(num_stories=Count('stories')).\
        filter(num_stories__gt=0, organization__subscription__is_trial=False).\
        order_by("organization__slug", "-num_stories")
    return render_to_response('staff/kanban_stats.html', {'top_projects': topProjects}, context_instance=RequestContext(request))


@staff_member_required
def sitestats(request):
    cursor = connection.cursor()
    cursor.execute("select count(*) as story_count, p.*  from projects_project as p join projects_story as s on s.project_id=p.id group by p.id order by story_count DESC limit 50")
    topProjects = cursor.fetchall()
    return render_to_response('staff/site_stats.html' , {'top_projects':topProjects}, context_instance=RequestContext(request))

@staff_member_required
def stats_data(request):
    stats = SiteStats.objects.all()
    user_data = []
    user_stats = { "label":"Users", "data":user_data}
    project_data = []
    project_stats = { "label":"Projects", "data":project_data}
    # story_data = []
    # story_stats = { "label":"Stories", "data":story_data, "yaxis": 2}
    for stat in stats:
        stat_time = int((time.mktime(stat.date.timetuple()) - time.timezone)*1000)
        user_data.append( [stat_time, stat.user_count] );
        project_data.append( [stat_time, stat.project_count] );
        # story_data.append( [stat_time, stat.story_count] );

    json_serializer = serializers.get_serializer("json")()
    result = json.dumps([user_stats,project_stats])
    return HttpResponse(result) #, mimetype='application/json'