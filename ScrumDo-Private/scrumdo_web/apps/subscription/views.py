# -*- coding: utf-8 -*-

# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.http import HttpResponse, Http404, HttpResponseRedirect
import django.template.defaultfilters as defaultfilters


from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.db import transaction
from django.conf import settings
from apps.stats.tasks import logEvent

from django.core.cache import cache

from apps.account.models import Account
from apps.account.templatetags.account_tags import realname
from apps.subscription.models import Cancelation, Subscription, SubscriptionStats, SubscriptionPlan, getSubscriptionPlan
from apps.subscription.spreedly import Spreedly
from apps.subscription.code_util import apply_subscription_code
from apps.organizations.util import invite_user
from apps.organizations.models import *
from apps.projects.models import *
from apps.projects.util import generateProjectPrefix
from apps.projects import signals as project_signals
from forms import OrganizationPlusProjectForm
from apps.activities.models import NewsItem
from apps.favorites.models import Favorite

from tutorial import createTutorialProject

import mixpanel

import random

import apps.projects.managers as projects_managers
import apps.kanban.managers as kanban_managers


import time
import logging
import traceback
import json
import sys
import datetime
logger = logging.getLogger(__name__)

from decimal import *

import apps.organizations.signals as organization_signals
from apps.organizations.views import handle_organization_create

import apps.projects.access as access

def test(request):
    return HttpResponse("Wheeee %d " % Project.objects.count())

@login_required
def subscription_redirect(request):
    organizations = Organization.getStaffOrganizationsForUser(request.user)
    count = organizations.count()
    if count == 0:
        return render_to_response("subscription/no_staff_orgs.html", context_instance=RequestContext(request) )
    if count > 1:
        return render_to_response("subscription/pick_sub.html", {"organizations":organizations}, context_instance=RequestContext(request) )
    return redirect("subscription_options", organization_slug=organizations[0].slug)


@login_required
@ensure_csrf_cookie
def user_trial_expired(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    staff_teams = organization.teams.filter(access_type="staff")
    owners = []
    subscription = organization.subscription
    
    over_users = subscription.usersUsed() > subscription.planUsers()
    over_projects = subscription.projectsUsed() > subscription.planProjects()
    
    for team in staff_teams:
        owners += team.members.all()
    is_grace = subscription.grace_until != None and subscription.grace_until >= datetime.date.today()    
    organization_name = organization.name
    
    if not is_grace:
        organization = None

    return render_to_response("subscription/subscription_expired_user.html",  
        {"organization":organization, 
         "organization_name": organization_name,
         "owners":owners, 
         "is_grace":is_grace, 
         "subscription":subscription } ,context_instance=RequestContext(request) )


@login_required
@ensure_csrf_cookie
def staff_trial_expired(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess(request.user) :
        raise PermissionDenied()
    
    subscription = organization.subscription
    today = datetime.date.today()
    is_expired = (subscription.is_trial and subscription.expires < today) or (not subscription.is_trial and not subscription.active)

    is_grace = subscription.grace_until != None and subscription.grace_until >= today
    bad_organization_subscription = not is_grace

    grid_plans = SubscriptionPlan.objects.filter(active=True, show_in_grid=True).order_by("order")
    yearly_plans = SubscriptionPlan.objects.filter(active=True, yearly=True).order_by("order")
    free_plan = SubscriptionPlan.objects.get(active=True,feature_level="free")
    current_plan = getSubscriptionPlan(subscription.plan_id)

    over_users = subscription.usersUsed() > subscription.planUsers()
    over_projects = subscription.projectsUsed() > subscription.planProjects()
    
    members = organization.members()
    members = sorted(members, key=str)
    
    projects = organization.activeProjects()
    
    if not (is_expired or over_projects or over_users):
        # They should be here...
        return HttpResponseRedirect(reverse("organization_dashboard", kwargs={'organization_slug':organization_slug}))

    return render_to_response("subscription/subscription_expired_staff.html",  {  "hide_free_box":True,
                                                                                  "grid_plans":grid_plans,
                                                                                  "free_plan":free_plan,
                                                                                  "yearly_plans":yearly_plans,
                                                                                  "current_plan":current_plan,
                                                                                  "trial_available":False,
                                                                                  "is_trial": subscription.is_trial,
                                                                                  "first_time": False,
                                                                                  "spreedly_path":settings.SPREEDLY_PATH, 
                                                                                  "organization":organization,
                                                                                  "is_expired":is_expired,
                                                                                  "is_grace":is_grace,
                                                                                  "bad_organization_subscription" : bad_organization_subscription,
                                                                                  "over_users":over_users,
                                                                                  "over_projects":over_projects,
                                                                                  "members":members,
                                                                                  "projects": projects,
                                                                                  "plan_projects": subscription.planProjects(),
                                                                                  "plan_users": subscription.planUsers(),
                                                                                  "subscription":subscription} ,context_instance=RequestContext(request) )


def special_offer_named(request, organization_slug, offer_name):
    offers = {
        "oldfree": [2002,2003,2004]
    }
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess(request.user) :
        raise PermissionDenied()
    plans = SubscriptionPlan.objects.filter(id__in=offers[offer_name])
    return render_to_response("subscription/special_offer.html",  {
                                            "organization": organization,
                                            "plans" : plans,
                                            "spreedly_path":settings.SPREEDLY_PATH
                                            },context_instance=RequestContext(request) )


@login_required
@ensure_csrf_cookie
def special_offer(request, organization_slug, plan_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess(request.user) :
        raise PermissionDenied()
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    if not plan.special_allowed:
        raise Http404()
    return render_to_response("subscription/special_offer.html",  {
                                            "organization": organization,
                                            "plans" : [plan],
                                            "spreedly_path":settings.SPREEDLY_PATH
                                            },context_instance=RequestContext(request) )




@login_required
@ensure_csrf_cookie
def start_trial(request, organization_slug, plan_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess(request.user) :
        raise PermissionDenied()
    plan = getSubscriptionPlan(int(plan_id) )
    organization.subscription.plan_id = plan.id
    if organization.subscription.expires == None:
        organization.subscription.expires = datetime.date.today() + datetime.timedelta(days=30)
    organization.subscription.is_trial = True
    organization.subscription.had_trial = True
    organization.subscription.save()
    if organization.projects.count() == 1:
        project = organization.projects.all()[0]
        return HttpResponseRedirect(reverse("project_detail", kwargs={"group_slug":project.slug}))
    else:
        return HttpResponseRedirect(reverse("organization_dashboard", kwargs={"organization_slug":organization_slug}))


def _alias_user(request, organization):
    try:
        mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
        orig = request.POST.get("distinct_id", None)
        if orig is not None:
            try:
                Organization.objects.get(slug=orig)
            except Organization.DoesNotExist:
                # Only do the alias if the distinct ID was auto-generated and not an organization slug
                mp.alias(organization.slug, orig)
                g1 = str(organization.id % 2)
                g2 = str(organization.id % 3)
                g3 = str(organization.id % 4)
                g4 = str(organization.id % 5)
                mp.people_set_once(organization.slug,
                                   {'Test Group 1 s': g1,
                                    'Test Group 2 s': g2,
                                    'Test Group 3 s': g3,
                                    'Test Group 4 s': g4})
    except:
        pass


def _generateSlug(projectName):
    slug = defaultfilters.slugify( projectName )[:45]
    c = 1
    while True:
        try:
            Project.objects.get(slug=slug)
            c += 1
            slug = "%s%d" % (defaultfilters.slugify(projectName)[:45], c)
        except Project.DoesNotExist:
            return slug  # finally found a slug that doesn't exist

@login_required
@transaction.non_atomic_requests
@ensure_csrf_cookie
def register(request):
    projects = []  # won't be any on registering.
    if request.method == 'POST': # If the form has been submitted...
        if request.POST.get("skip","0") == "1":
            return HttpResponseRedirect("/")
        form = OrganizationPlusProjectForm(request.POST)
        if form.is_valid():  # All validation rules pass
            logger.info("Creating organization")
            organization = handle_organization_create(form, request, projects)
            transaction.commit()

            try:
                account = Account.objects.get(user=request.user)
                account.classic_mode = Account.CLASSIC_FORCE_NEW
                account.save()
            except:
                pass


            project = Project()
            project.name = form.cleaned_data['project_name']
            # if settings.KANBAN_ALLOWED:
            project.project_type = Project.PROJECT_TYPE_KANBAN  #int( form.cleaned_data['project_type'] )
            project.organization = organization
            slug = _generateSlug(project.name)



            project.slug = slug
            project.prefix = generateProjectPrefix(project)
            project.creator = request.user

            project.save()

            project_signals.project_created.send(sender=request, project=project, user=request.user)



            if project.project_type == Project.PROJECT_TYPE_SCRUM:
                projects_managers.initScrumProject(project)
            else:
                kanban_managers.initKanbanProject(project)
            transaction.commit()

            members_team = organization.teams.get(access_type="write")
            members_team.projects.add(project)

            for address in form.cleaned_data['project_members'].split("\n"):
                invite_user(address.rstrip(), members_team, request.user)

            user = request.user

            item = NewsItem(user=user, project=project, icon='building_add' )
            item.text = render_to_string("activities/organization_created.txt", {'user':user,'organization':organization} )
            item.save()

            # item = NewsItem(user=user, project=project, icon='server_add' )
            # item.text = render_to_string("activities/project_created.txt", {'user':user,'project':project} )
            # item.save()

            transaction.commit()


            Favorite.setFavorite(1, project.id, user, True)

            _alias_user(request, organization)

            tut = createTutorialProject(organization, request.user)
            project_signals.project_created.send(sender=request, project=tut, user=request.user)
            transaction.commit()

            if len(form.cleaned_data['sub_code']) > 0:
                try:
                    apply_subscription_code(organization, form.cleaned_data['sub_code'])
                except:
                    pass  # Ignore these


            try:
                mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
                mp.people_set(organization.slug, {'name':  organization.name})
                mp.track(organization.slug, 'Create Project')
            except:
                logger.info('Could not set MixPAnel properties.')

            return HttpResponseRedirect(reverse("organization_dashboard",  kwargs={'organization_slug': organization.slug}) )
    else:
        form = OrganizationPlusProjectForm()

    return render_to_response("subscription/register.html",  { "form":form } ,context_instance=RequestContext(request) )



    # <invoice>
    #   <response-message nil="true"></response-message>
    #   <response-client-message nil="true"></response-client-message>
    #   <response-customer-message nil="true"></response-customer-message>
    #   <closed type="boolean">true</closed>
    #   <updated-at type="datetime">2012-06-03T13:08:52Z</updated-at>
    #   <created-at type="datetime">2012-06-03T13:05:31Z</created-at>
    #   <token>8160410b365b68b7696764ac0eac518436bd3a4b</token>
    #   <price>$28.00</price>
    #   <amount type="decimal">28.0</amount>
    #   <currency-code>USD</currency-code>
    #   <metadata>SuperPro</metadata>
    #   <line-items type="array">
    #     <line-item>
    #       <amount type="decimal">28.0</amount>
    #       <notes nil="true"></notes>
    #       <currency-code>USD</currency-code>
    #       <description>Every 1 month</description>
    #       <price>$28.00</price>
    #       <feature-level>SuperPro</feature-level>
    #       <metadata>SuperPro</metadata>
    #     </line-item>
    #   </line-items>


@login_required
@ensure_csrf_cookie
def invoice(request, organization_slug, invoice_token):
    logger.debug(organization_slug)
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess(request.user) :
        raise PermissionDenied()
    spreedly = Spreedly()
    invoices = spreedly.getSubscriptionForOrganization(organization)["invoices"]
    invoice = None

    sub = Subscription.objects.get(organization=organization)
    bill_to = organization.bill_to
    if bill_to == "" or bill_to == None:
        bill_to = "%s\n%s\n%s" % (organization.name,
                realname(organization.creator), 
                organization.creator.email)



    for i in invoices:
        logger.debug(i)
        if i["token"] == invoice_token:
            invoice = i


    
    return render_to_response("subscription/invoice.html",  { "bill_to":bill_to, "organization":organization, "invoice":invoice } ,context_instance=RequestContext(request) )


@login_required
@ensure_csrf_cookie
def invoices(request, organization_slug):
    logger.debug("Displaying invoices.")
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess(request.user) :
        raise PermissionDenied()
    spreedly = Spreedly()
    invoices = spreedly.getSubscriptionForOrganization(organization)["invoices"]
    
    return render_to_response("subscription/invoices.html",  { "organization":organization, "invoices":invoices } ,context_instance=RequestContext(request) )

@login_required
@ensure_csrf_cookie
def stats_charts(request):    

    if not request.user.is_staff:
        raise PermissionDenied()
    
    return render_to_response("subscription/stats.html",  {"sources":[], "levels":{}, "total":0, "organizations":[],"subscribers":[] } , context_instance=RequestContext(request) )


@login_required
def stats(request):    

    if not request.user.is_staff:
        raise PermissionDenied()
    
    spreedly = Spreedly()
    
    # logger.debug(spreedly.getPlans().toprettyxml())

    subscribers_result = spreedly.getSubscribers()
    subscribers = subscribers_result.getElementsByTagName("subscriber")
    levels = {}
    r_subs = []
    total = 0
    for subscriber in subscribers:
        if( _getText(subscriber.getElementsByTagName("active")[0]) == "true" ):            
            level = _getText(subscriber.getElementsByTagName("feature-level")[0])
            plan = SubscriptionPlan.objects.get(feature_level=level)
            trial_user = ("true" == _getText(subscriber.getElementsByTagName("on-trial")[0]) )
            recurring = ("true" == _getText(subscriber.getElementsByTagName("recurring")[0]) )
            name = _getText(subscriber.getElementsByTagName("screen-name")[0])
            if not level in levels:
                levels[level] = {"active":0, "trial":0, "recurring":0, "value":0}
            level_obj = levels[level]
            level_obj["active"] += 1
                        
            if trial_user:
                level_obj["trial"] += 1
            if recurring:
                level_obj["recurring"] += 1
                total += plan.price_val
                level_obj["value"] += plan.price_val
            try:
                organization = Organization.objects.get(slug=name)
            except:
                organization = None
            r_subs.append({"name":name,"org":organization,"level":level,"trial":trial_user,"recurring":recurring,"s":subscriber})

    # levels["bronze"]["value"] = levels["bronze"]["recurring"] * Subscription.BRONZE_LEVEL["price_val"]
    # levels["silver"]["value"] = levels["silver"]["recurring"] * Subscription.SILVER_LEVEL["price_val"]
    # levels["gold"]["value"] = levels["gold"]["recurring"] * Subscription.GOLD_LEVEL["price_val"]
    # levels["platinum"]["value"] = levels["platinum"]["recurring"] * Subscription.PLATINUM_LEVEL["price_val"]
    
    r_subs = sorted(r_subs, lambda x,y: cmp(x["level"], y["level"])  )
    #total = levels["bronze"]["value"] + levels["silver"]["value"] + levels["gold"]["value"] + levels["platinum"]["value"]    
    orgs = Organization.objects.filter(subscription__level__gt=0).order_by("-subscription__level")
    
    sources = {}
    for sub in Subscription.objects.all():
        if sub.total_revenue > 0:
            source = sub.organization.source
            if source in sources:
                sources[source] += sub.total_revenue
            else:
                sources[source] = sub.total_revenue
    
    return render_to_response("subscription/stats.html",  {"sources":sources, "levels":levels, "total":total, "organizations":orgs,"subscribers":r_subs } , context_instance=RequestContext(request) )


@login_required
def stats_data(request):

    if not request.user.is_staff:
        raise PermissionDenied()
    stats = SubscriptionStats.objects.all();
    revenue_data = []
    revenue = { "label":"Total Monthly $",  "data":revenue_data}
    sub_data = []
    sub_stats = { "label":"Trial Monthly $", "data":sub_data}
    exp_data = []
    exp_stats = { "label":"Safe Monthly $", "data":exp_data}
    
    for stat in stats:
        stat_time = int((time.mktime(stat.date.timetuple()) - time.timezone)*1000)
        revenue_data.append( [stat_time, int(stat.expected_monthly_revenue) ] )
        sub_data.append( [stat_time, int(stat.trial_monthly_revenue)] )
        exp_data.append( [stat_time, int(stat.expected_monthly_revenue) - int(stat.trial_monthly_revenue)] )

    json_serializer = serializers.get_serializer("json")()
    result = json.dumps([revenue,sub_stats,exp_stats])
    return HttpResponse(result) #, mimetype='application/json'


@csrf_exempt
def spreedly_web_hook(request):
    """Gets called whenever a cutomer updates their spreedly subscription.  We get a list of
       subscription id's (they correspond to organization id's).  Our web app then uses the
       spreedly API to fetch information about the user's subscription and updates our system. """

    if request.method != "POST":
        logger.error("Recieved a spreedly web hook GET request! ") # should only be post
        raise Http404()
    id_string = request.POST.get("subscriber_ids")
    logger.info("Spreedly callback for: %s" % id_string)
    ids = id_string.split(",")
    ids = map(lambda x: int(x), ids) # turn the id's to integers
    for id in ids:
        organization = None
        try:
            organization = Organization.objects.get( id = id)
            _updateOrganization( organization )
        except:
            if organization:
                logger.error("Failed to update spreedly subscription %s" % organization.slug)
            else:
                logger.error("Failed to update spreedly subscription %d" % id)

    return HttpResponse("OK")


@login_required
@ensure_csrf_cookie
def subscription_completed(request, organization_slug):
    """ When a user finished on the spreedly site, they end up here.  We'll use the
        sreedly API to request their subscription info and update it, then pass them along to
        the subscription page.  Strictly speaking, it shouldn't be neccessary to do the
        update here because the web_hook above should have already fired.  But, if the
        hook is delayed for any reason it'd be a shame for the user to not see their
        updated subscription right away. """
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess(request.user):
        raise PermissionDenied()

    _updateOrganization( organization )
    
    return render_to_response("subscription/subscription_completed.html",  { "organization":organization, "subscription":organization.subscription } ,context_instance=RequestContext(request) )
    # return HttpResponseRedirect( reverse("organization_detail", kwargs={"organization_slug":organization.slug} ) )


def _updateOrganization(organization):
    """ Calls the spreedly API to get the status of the subscription, and
        updates that status for us. """
    spreedly = Spreedly()
    # logger.info(u"updateOrganization %s" % organization.slug)
    try:
        details = spreedly.getSubscriptionForOrganization( organization )
    except:
        logger.error("Could not retrieve spreedly info for %s" % organization.slug)
        return

    try:
        subscription = organization.subscription
    except:
        # no subscription existed.
        subscription = Subscription.generateFreeSubscription(organization)


    old_plan = subscription.plan

    account_type = details['account_type']
    plan_id = int(details['plan_id'])

    # logger.info("Spreedly plan id = %s" % plan_id)
    # logger.info("Current plan = %s/%s" % (old_plan.id, old_plan.feature_level))

    if account_type == "":
        account_type = "free"
    
    if not details['account_active']:
        account_type = "free"


    if subscription.is_trial and subscription.expires >= datetime.date.today() and account_type == "free":
        # logger.debug("Bailing because we don't want to end the trial")
        # user is on a trial and had no spreedly plan, so leave them on their trial
        return
    
    if subscription.active and details['account_active'] and (subscription.plan.spreedly_id == plan_id) and not subscription.is_trial:
        # logger.debug("Bailing because we have an account already")
        # Special case... If a customer has a plan, we should
        # grandfather that plan instead of moving them to the newest version of that
        # plan.  "do no harm"
        return
    
    # subscription_num = Subscription.SUBSCRIPTION_MAP[account_type]

    try:
        plan = SubscriptionPlan.objects.get(spreedly_id=plan_id)
    except (SubscriptionPlan.MultipleObjectsReturned, SubscriptionPlan.DoesNotExist):
        try:
            # logger.info(u"Resorting to a default plan for %s/%s" % (account_type, organization.slug))
            plan = SubscriptionPlan.objects.filter(feature_level=account_type).order_by("-active")[:1][0]  # The sort and weird indexing is to prefer active plans, but allow inactive
        except:
            logger.error("Could not find subscription plan for %s" % account_type)
            return

    try:
        if details['account_active'] and old_plan.price_val == Decimal("0.00") and plan.price_val > Decimal("0.00"):
            logEvent.delay(organization.slug, "new subscription", {'value':str(plan.price_val), 'plan level':plan.feature_level, 'source':organization.source} )
        elif details['account_active'] and old_plan.price_val < plan.price_val:
            logEvent.delay(organization.slug, "upgraded", {'value':str(plan.price_val), 'plan level':plan.feature_level, 'source':organization.source} )
        elif plan.price_val == Decimal('0.00') and old_plan.price_val > Decimal("0.00"):
            logEvent.delay(organization.slug, "expired", {'value':str(plan.price_val), 'source':organization.source, 'reason':'Unknown'})
        elif old_plan.price_val > plan.price_val:
            logEvent.delay(organization.slug, "downgraded", {'value':str(plan.price_val), 'plan level':plan.feature_level, 'source':organization.source} )
    except:
        print "\n".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))

    changed = False
    if details['account_active'] and subscription.plan_id != plan.id:
        logger.info(u"Updating plan ID for %s" % organization.slug)
        logger.info(u"Old plan: %s/%s/%s" % (old_plan.id, old_plan.feature_level, old_plan.name))
        logger.info(u"New plan: %s/%s/%s" % (plan.id, plan.feature_level, plan.name))
        changed = True
        subscription.plan_id = plan.id
    subscription.level = plan.id
    subscription.is_trial = False
    subscription.had_trial = True
    subscription.grace_until = None
    if subscription.active != details['account_active']:
        logger.info(u"Updating active flag (%s) for %s" % (details['account_active'], organization.slug))
        changed = True
    subscription.active = details['account_active']
    subscription.token = details['token']
    subscription.save()
    return changed


def plans_test(request):
    return render_to_response("plans_test.html",  {  } ,context_instance=RequestContext(request) )
    

def plans(request, template="plans.html"):
    # grid_plans = SubscriptionPlan.objects.filter(active=True, show_in_grid=True, yearly=False).order_by("order")
    # yearly_plans = SubscriptionPlan.objects.filter(active=True, yearly=True).order_by("order")
    # free_plan = SubscriptionPlan.objects.get(active=True,price_val=0)
    return render_to_response("plans.html", {}, context_instance=RequestContext(request) )


@login_required
@ensure_csrf_cookie
def set_free_plan(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess(request.user) :
        raise PermissionDenied()
    subscription = organization.subscription
    
    spreedly = Spreedly()
    spreedly.stopAutoRenewForOrganization( organization )
    
    plan = SubscriptionPlan.objects.get(active=True, price_val=0)
    subscription.plan_id = plan.id
    subscription.level = 0
    subscription.active = True
    subscription.is_trial = False
    # subscription.had_trial = True
    subscription.expires = None
    subscription.active = True
    subscription.grace_until = None
    subscription.token = ""
    subscription.save()
    cache_key = "org_check_%s" % organization_slug
    cache.delete(cache_key)
    return HttpResponseRedirect(reverse("organization_dashboard",kwargs={'organization_slug':organization_slug}))


@login_required
@ensure_csrf_cookie
def subscription_cancel(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess(request.user):
        raise PermissionDenied()

    if request.method != 'POST':
        raise PermissionDenied()

    if organization.subscription.is_trial:
        Subscription.generateFreeSubscription(organization)
    else:
        spreedly = Spreedly()
        spreedly.stopAutoRenewForOrganization(organization)
        Cancelation(organization=organization, reason=request.POST.get("reason"), user=request.user).save()

    return HttpResponse('goodbye')


@login_required
@ensure_csrf_cookie
def org_upgrade_premium(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not organization.hasStaffAccess(request.user):
        return render_to_response("subscription/subscription_non_admin.html",  {"organization":organization},context_instance=RequestContext(request) )

    subscription = organization.subscription
    organizations = Organization.getOrganizationsForUser( request.user )
    grid_plans = SubscriptionPlan.objects.filter(active=True, show_in_grid=True).order_by("order")
    yearly_plans = SubscriptionPlan.objects.filter(active=True, yearly=True).order_by("order")
    current_plan = getSubscriptionPlan(subscription.plan_id)
    free_plan = SubscriptionPlan.objects.get(active=True,feature_level="free")

    return render_to_response("subscription/subscription_premium.html",  context={"organizations":organizations,
                                                                          "grid_plans":grid_plans,
                                                                          "free_plan":free_plan,
                                                                          "yearly_plans":yearly_plans,
                                                                          "current_plan":current_plan,
                                                                          "is_trial": subscription.is_trial,
                                                                          "spreedly_path":settings.SPREEDLY_PATH,
                                                                          "organization":organization } ,context_instance=RequestContext(request) )


@login_required
@ensure_csrf_cookie
def subscription_options(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not organization.hasStaffAccess(request.user):
        raise PermissionDenied()

    subscription = organization.subscription
    organizations = Organization.getOrganizationsForUser(request.user )
    grid_plans = SubscriptionPlan.objects.filter(active=True, show_in_grid=True).order_by("order")
    yearly_plans = SubscriptionPlan.objects.filter(active=True, yearly=True).order_by("order")
    current_plan = getSubscriptionPlan(subscription.plan_id)
    free_plan = SubscriptionPlan.objects.get(active=True,feature_level="free")

    return render_to_response("subscription/subscription_options.html",  context={"organizations":organizations,
                                                                          "grid_plans":grid_plans,
                                                                          "free_plan":free_plan,
                                                                          "yearly_plans":yearly_plans,
                                                                          "current_plan":current_plan,
                                                                          "is_trial": subscription.is_trial,
                                                                          "spreedly_path":settings.SPREEDLY_PATH,
                                                                          "organization":organization },
                                                                         context_instance=RequestContext(request) )


def _getText(nodelist):
  rc = []
  for node in nodelist.childNodes:
      if node.nodeType == node.TEXT_NODE:
          rc.append(node.data)
  return ''.join(rc)
