from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from apps.organizations.models import *
from functools import wraps
from django.conf import settings

from django.core.cache import cache
from apps.projects.models import Project
import datetime

SUBSCRIPTION_CACHE_CHECK_TIMEOUT_SECONDS = 14400 # 4 hours

import logging

logger = logging.getLogger(__name__)


def do_over_limit(request, organization, subscription):
    if subscription.grace_until == None:
        subscription.grace_until = datetime.date.today() + datetime.timedelta(days=7)
        subscription.save()    
    return redirectExpired(request.user, organization)    


def do_expired(request, organization, subscription):
    checkGrace(subscription)
    return redirectExpired(request.user, organization)        


def checkGrace(subscription):
    if subscription.grace_until is None:
        subscription.grace_until = datetime.date.today() + datetime.timedelta(days=5)
        subscription.save()
    return subscription.grace_until >= datetime.date.today()


def redirectExpired(user, organization):
    if organization.hasStaffAccess(user):
        return HttpResponseRedirect(reverse("staff_trial_expired", kwargs={'organization_slug':organization.slug}))
    else:
        return HttpResponseRedirect(reverse("user_trial_expired", kwargs={'organization_slug':organization.slug}))
    

def isExpired(organization):
    subscription = organization.subscription
    if subscription.grace_until != None and subscription.grace_until > datetime.date.today():
        return False # Currently in grace period, so let this view through.

    elif not subscription.is_trial and not subscription.active:
        if not checkGrace(subscription):
            return True

    elif subscription.is_trial and subscription.expires < datetime.date.today():
        if not checkGrace(subscription):
            return True

    elif subscription.usersUsed() > subscription.planUsers():
        if not checkGrace(subscription):
            return True
    elif subscription.projectsUsed() > subscription.planProjects():
        return True
    else:
        return False


# This one is to be used on a project view and only 
# kicks in if actually expired (past grace period)
def expired_subscription_check(func):
    def inner_decorator(request, *args, **kwargs):
        try:
            project_slug = None
            organization_slug = None
            if "organization_slug" in kwargs:
                organization_slug = kwargs['organization_slug']
            elif "project_slug" in kwargs:
                project_slug = kwargs["project_slug"]
            elif "group_slug" in kwargs:
                project_slug = kwargs["group_slug"]

            if organization_slug:
                organization = get_object_or_404(Organization, slug=organization_slug)
            elif project_slug:
                project = get_object_or_404(Project, slug=project_slug)
                organization = project.organization

            if organization:
                cache_key = "org_check_%s" % organization.slug
                if not cache.get(cache_key):
                    subscription = organization.subscription

                    if subscription.grace_until != None and subscription.grace_until > datetime.date.today():
                        # Currently in grace period, so let this view through.
                        cache.set(cache_key, True, SUBSCRIPTION_CACHE_CHECK_TIMEOUT_SECONDS)
                        return func(request, *args, **kwargs)
                    elif not subscription.is_trial and not subscription.active:
                        if not checkGrace(subscription):
                            return do_expired(request, organization, subscription)

                    elif subscription.is_trial and subscription.expires < datetime.date.today():
                        if not checkGrace(subscription):
                            return do_expired(request, organization, subscription)
                
                    elif subscription.usersUsed() > subscription.planUsers():
                        if not checkGrace(subscription):
                            return do_over_limit(request, organization, subscription)
                    elif subscription.projectsUsed() > subscription.planProjects():
                        return do_over_limit(request, organization, subscription)
                    else:
                        # At this point, the account is in good standing and everything is great.
                        cache.set(cache_key, True, SUBSCRIPTION_CACHE_CHECK_TIMEOUT_SECONDS)
                        # Let's make sure their grace period is reset in case they aren't in good standing in the future.
                        if subscription.grace_until is not None:
                            subscription.grace_until = None
                            subscription.save()



        except:
            logger.error("Could not check subscription")

        return func(request, *args, **kwargs)

    return wraps(func)(inner_decorator)


def premium_subscription_check(func):
    def inner_decorator(request, *args, **kwargs):
        org_slug = None
        if "organization_slug" in kwargs:
            org_slug = kwargs["organization_slug"]
        elif "group_slug" in kwargs:
            org_slug = kwargs["group_slug"]

        if org_slug:
            cache_key = "org_check_premium_%s" % org_slug
            if not cache.get(cache_key):
                organization = get_object_or_404(Organization, slug=org_slug)
                subscription = organization.subscription
                has_access = subscription.plan.premium_plan
                if has_access:
                    cache.set(cache_key, has_access, SUBSCRIPTION_CACHE_CHECK_TIMEOUT_SECONDS)
                else:
                    return HttpResponseRedirect(reverse("org_upgrade_premium", kwargs={'organization_slug': organization.slug}))

        return func(request, *args, **kwargs)

    return wraps(func)(inner_decorator)


def subscription_check(func):
    def inner_decorator(request, *args, **kwargs):
        org_slug = None
        if "organization_slug" in kwargs:
            org_slug = kwargs["organization_slug"]
        elif "group_slug" in kwargs:
            org_slug = kwargs["group_slug"]

        if org_slug:
            cache_key = "org_check_%s" % org_slug
            if not cache.get(cache_key):
                organization = get_object_or_404(Organization, slug=org_slug)
                subscription = organization.subscription
                if subscription.is_trial and subscription.expires < datetime.date.today():
                    return do_expired(request, organization, subscription)

                if not subscription.is_trial and not subscription.active:
                    return do_expired(request, organization, subscription)

                if subscription.usersUsed() > subscription.planUsers():
                    return do_over_limit(request, organization, subscription)

                if subscription.projectsUsed() > subscription.planProjects():
                    return do_over_limit(request, organization, subscription)

                # Everything is good with their subscription, so cache the fact so it's quicker next time.
                cache.set(cache_key, True, SUBSCRIPTION_CACHE_CHECK_TIMEOUT_SECONDS)



            
        return func(request, *args, **kwargs)

    return wraps(func)(inner_decorator)
