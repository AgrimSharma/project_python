#!/usr/bin/env python
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.utils.html import strip_tags
from django.core.management.base import BaseCommand, CommandError
from apps.subscription.models import *
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from rollbardecorator import logexception

import datetime
import logging

logger = logging.getLogger(__name__)

PLAN_TO_USE = 3002  # the gold monthly plan

class Command(BaseCommand):

    @logexception
    def handle(self, *args, **options):
        today = datetime.datetime.now()
        mdiff = datetime.timedelta(hours=-2)
        date_2hours_ago = today + mdiff
        mdiff = datetime.timedelta(hours=-1)
        date_1hours_ago = today + mdiff

        for organization in Organization.objects.filter(created__gte=date_2hours_ago, created__lte=date_1hours_ago):
            sub = organization.subscription
            if not sub.had_trial and sub.plan.price_val == Decimal("0.0") and sub.token == "":
                self.setupAccount(organization, sub)
                self.sendEmail( organization )
                # self.logAction(organization)

    # def logAction( self, org ):
    #     # record_event(org.slug, "auto_trial")
    #     try:
    #         k = KM()
    #         k.identify(org.slug);
    #         k.set({'sub_mode' : 'auto_trial_2'})
    #         k.record('auto_trial')
    #     except:
    #         logger.error("could not update KM")


    def setupAccount(self, organization, sub):
        # plan = getSubscriptionPlan( PLAN_TO_USE )
        organization.subscription.plan_id = PLAN_TO_USE
        organization.subscription.expires = datetime.date.today() + datetime.timedelta(days=30)
        organization.subscription.is_trial = True
        organization.subscription.had_trial = True
        organization.subscription.save()


    def sendEmail(self, org ):
        logger.info("Sending email to %s " % org.creator.email)
        subject = "Set up your premium trial"        
        body = render_to_string("subscription/emails/default_trial.txt" , {"org_slug":org.slug} )
        text_body = strip_tags(body)
        msg = EmailMultiAlternatives(subject, text_body, "Ajay Reddy <support@scrumdo.com>" , [ probable_email(org.creator) ])        
        msg.attach_alternative(body, "text/html")        
        msg.send()
                


        
