# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from datetime import datetime, date
import time
import re

from django.conf import settings

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.projects.models import Project, Iteration, Story
from apps.attachments.models import Attachment

from scrumdo_utils import cache as cache_decorator

from apps.subscription.spreedly import Spreedly

import django.dispatch
from django.db.models.signals import post_save, pre_delete, post_delete

import apps.subscription.usage as usage
import logging

logger = logging.getLogger(__name__)

from decimal import *

def getSubscriptionPlan(id):
    """Just returns a given subscription plan, but wraps it all in a nice big long cache"""
    cache_key = "sub_plan_g_%d" % id
    plan = cache.get(cache_key)
    if plan:
        return plan

    plan = SubscriptionPlan.objects.get(id=id)
    cache.set(cache_key, plan, 9000) # 2.5 hours    
    return plan


class SingleUseCode(models.Model):
    """Codes we can send to people for single-use purposes.  That purpose will be dependent
       and custom coded based on the campaign value.  Example: Using it for the old user re-activation
       email first."""
    campaign = models.CharField(max_length=32)
    code = models.CharField(max_length=32)
    expiration = models.DateField()
    user = models.ForeignKey(User)
    used = models.BooleanField(default=False)


class SubCode(models.Model):
    code = models.CharField(max_length=32)
    expiration = models.DateField()
    trial_days = models.IntegerField(default=0)


class SubCodeUsage(models.Model):
    organization = models.ForeignKey(Organization)
    create = models.DateTimeField(auto_now_add=True)
    code = models.ForeignKey(SubCode)


class Cancelation(models.Model):
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
    reason = models.TextField()
    user = models.ForeignKey(User)
    date = models.DateField(auto_now=True)


class SpreedlyInfo(models.Model):
    last_transaction_fetched = models.IntegerField(default=1)

class SubscriptionFeatureOverride(models.Model):
    feature = models.CharField(max_length=16)
    organization = models.ForeignKey(Organization, related_name="subscription_overrides")
    available = models.BooleanField(default=True)

class SubscriptionPlan(models.Model):
    # HEY! If you change the subscription plan schema, you should change the cache_key above or you'll 
    # get oddities when you deploy.
    name = models.CharField(max_length=16)
    tagline = models.CharField(max_length=50,default='',blank=True)
    active = models.BooleanField(default=False)
    show_in_grid = models.BooleanField(default=False)
    price = models.CharField(max_length=32)
    price_val = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    users = models.IntegerField()
    projects = models.IntegerField()
    storage = models.IntegerField()
    premium_integrations = models.BooleanField(default=False)
    order = models.IntegerField()
    spreedly_id = models.IntegerField()
    feature_level = models.CharField(max_length=24,default="",blank=True)
    featured_plan = models.BooleanField(default=False)
    planning_poker = models.BooleanField(default=True)
    epic_tool = models.BooleanField(default=True)
    emails = models.BooleanField(default=True)
    yearly = models.BooleanField(default=False)
    custom_status = models.BooleanField(default=False)
    time_tracking = models.BooleanField(default=False)
    special_allowed = models.BooleanField(default=False)
    kanban = models.BooleanField(default=False)
    live_updates = models.BooleanField(default=False)
    premium_plan = models.BooleanField(default=False)

    
    def isFree(self):
        return self.price_val == Decimal('0.00')


class SubscriptionStats(models.Model):
    date = models.DateField( auto_now=True)
    trial_orgs = models.IntegerField()
    recurring_orgs = models.IntegerField()
    paid_orgs = models.IntegerField()
    active_orgs = models.IntegerField()
    expected_monthly_revenue = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    trial_monthly_revenue = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def safe_revenue(self):
        return self.expected_monthly_revenue - self.trial_monthly_revenue
    

class Subscription(models.Model):
    # These are the chargify statuses:
    SUBSCRIPTION_STATUSES = ["initial", "trialing", "assessing",
                             "active", "soft_failure", "past_due",
                             "suspended", "canceled", "unpaid", "expired"]

    SUBSCRIPTION_VALID_STATUSES = ["trialing", "assessing", "active"]
    SUBSCRIPTION_WARNING_STATUSES = ["soft_failure", "past_due"]
    SUBSCRIPTION_INVALID_STATUSES = ["suspended", "canceled", "unpaid", "expired"]

    organization = models.OneToOneField(Organization, related_name="subscription")
    
    total_revenue = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    plan_id = models.IntegerField(default=1000)  # Our default, legacy free plan in our fixtures has ID=1000
    level = models.IntegerField()
    active = models.BooleanField(default=False)
    token = models.CharField(max_length=100 , default="", null=True, blank=True)

    is_billed = models.BooleanField(default=False)
    is_trial = models.BooleanField(default=False)
    had_trial = models.BooleanField(default=False)
    expires = models.DateField(null=True, blank=True)   # The last day the subscription is good on, server time.
    grace_until = models.DateField(null=True, blank=True)   # after expiration or over quota, you get until this date to fix it.


    def __unicode__(self):
        return "Subscription %s %s" % (self.level, self.organization.slug)

    @staticmethod
    def generateFreeSubscription(organization):
        plan = SubscriptionPlan.objects.get(active=True, price_val=0)
        try:
            sub = organization.subscription
            sub.plan_id = plan.id
            sub.is_trial = False
            sub.save()
        except Subscription.DoesNotExist:
            sub = Subscription()
            sub.organization = organization
            sub.plan_id = plan.id
            sub.level = 0
            sub.active = True
            sub.save()
        return sub

    @staticmethod
    def getSubscriptionForObject( obj ):
        if isinstance(obj, Project):
            try:
                return obj.organization.subscription
            except:
                return None
        if isinstance(obj, Iteration) or isinstance(obj, Story):
            try:
                return obj.project.organization.subscription
            except:
                return None
        if isinstance(obj, Organization):
            try:
                return obj.subscription
            except:
                return None

    # Plans don't change (you create a new one).  I wanted long cached versions that didn't neccessarily go through the ORM
    # every time we needed to look 'em up.  So I've got the plan as an ID and this helper to get the 
    # actual (cached) plan object
    def _plan(self):
        return getSubscriptionPlan(self.plan_id)
    
    plan = property(_plan)
    
    def projectsUsed( self ):
        return usage.calculateProjectUsage( self.organization )

    def usersUsed( self ):
        return usage.calculateUserUsage( self.organization )

    def storageUsed(self):
        return usage.calculateStorageUsage( self.organization )

    @cache_decorator(3)
    def canUpload(self, add=0):
        return ((self.storageUsed() + add) < (self.planStorage() * (1024)))

    def getAccountURL(self):
        return "%s/subscriber_accounts/%s?return_url=http://www.scrumdo.com/subscription/completed/%s" % (settings.SPREEDLY_PATH, self.token, self.organization.slug)

    def planInstantCalculation(self):
        return self.plan.premium_integrations

    def planProjects(self):
        return self.plan.projects

    def planUsers(self):
        return self.plan.users

    def planStorage(self):
        return self.plan.storage

    def planPrice(self):
        return self.plan.price

    def planName(self):
        return self.plan.name

    def planPremiumExtras(self):
        return self.plan.premium_integrations
    
    def planEmail(self):
        return self.plan.emails

    def planPoker(self):
        return self.plan.planning_poker
    
    def planCustomStatus(self):
        return self.plan.custom_status
    
    def planTimeTracking(self):
        return self.plan.time_tracking

    def planKanban(self):
        return self.plan.kanban

    def planLiveUpdates(self):
        return self.plan.live_updates




class AttachmentsManager(models.Manager):
    def subscription_usage(self, subscription):
        return sum(self.filter(subscription=subscription).values_list("file_size", flat=True))

class AttachmentExtra(models.Model):
    file_size = models.PositiveIntegerField()
    subscription = models.ForeignKey(Subscription, related_name="subscription_files")
    old_version = models.ForeignKey(Attachment, null=True, related_name="attachment_old_version")
    # this is the original file that previous versions revise.
    related_id = models.PositiveIntegerField()
    # is this the latest revision?
    is_latest = models.BooleanField(default=True)
    attachment = models.OneToOneField(Attachment, related_name="extra")
    
    related_project = models.ForeignKey(Project, null=True)
    related_iteration = models.ForeignKey(Iteration, null=True)
    related_organization = models.ForeignKey(Organization, null=True)    

    objects = AttachmentsManager()

    class Meta:
        db_table = "v2_subscription_attachment_extra"
    

def add_attachment_extra(sender, instance, created, **kwargs):
    if created:
        # check if attachment is local of from remote services
        if instance.attachment_file:
            size = instance.attachment_file.size # this requires a call to s3, so store result locally
        else:
            size = 0
        # figure out what subscription this upload belongs to, based on what it was attached to
        subscription = Subscription.getSubscriptionForObject(instance.story)
        old_version = None # not doing versioning for now
        related_id = instance.pk # default to self, will be changed if this is part of a collection.

        # We're going to cheat here and save the related project, iteration, and organization with each attachment
        # extra to avoid length lookups on generic fields later.
        related_object = instance.story
        related_project = None
        related_iteration = None
        related_organization = None
        
        if isinstance( related_object, Project ):
            related_project = related_object
            related_organization = related_object.organization
        elif isinstance( related_object, Iteration ):
            related_project = related_object.project
            related_iteration = related_object
            related_organization = related_project.organization
        elif isinstance( related_object, Story ):
            related_project = related_object.iteration.project
            related_iteration = related_object.iteration
            related_organization = related_project.organization
        elif isinstance( related_object, Organization ):
            related_organization = related_object
        
        extra = AttachmentExtra(file_size=size, 
                                subscription=subscription, 
                                old_version=old_version, 
                                attachment=instance, 
                                related_id=related_id,
                                related_project=related_project,
                                related_iteration=related_iteration,
                                related_organization=related_organization)
        extra.save()

def organization_deleted(sender, instance, **kwargs):
    if instance.subscription == None:
        return
    if instance.subscription.plan.spreedly_id != -1:
        # Oh no, a paying subscriber is deleting their organization.  Time to act!
        spreedly = Spreedly()
        spreedly.stopAutoRenewForOrganization( instance )
        
        
    
def add_subscription(sender, instance, **kwargs):
    try:
        instance.subscription
    except Subscription.DoesNotExist:
        Subscription.generateFreeSubscription( instance )

def update_attachment_counts(sender,instance,**kwargs):
    try:
        instance.content_object.resetAttachmentCount()
        instance.content_object.save()
    except:
        logger.warn("Could not update attachment count on story")
    
post_save.connect(update_attachment_counts, sender=Attachment, dispatch_uid="subscription_models")
post_delete.connect(update_attachment_counts, sender=Attachment, dispatch_uid="subscription_models")

post_save.connect(add_attachment_extra, sender=Attachment, dispatch_uid="subscription_models2")
post_save.connect(add_subscription, sender=Organization, dispatch_uid="subscription_models")
pre_delete.connect(organization_deleted, sender=Organization, dispatch_uid="subscription_models")
