#!/usr/bin/env python

from apps.projects.models import Epic, Project, Iteration, Story, PointsLog, SiteStats
from apps.activities.models import NewsItem
from apps.extras.models import *
from apps.organizations.models import *
from apps.email_notifications.models import *
from apps.realtime.models import ChatMessage
from mailer.models import Message
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from apps.emailconfirmation.models import EmailAddress

from postmonkey import PostMonkey, MailChimpException

from processing import Process, Queue
import logging
import string
import random
import datetime
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        pm = PostMonkey(settings.MAILCHIMP_KEY, timeout=10)
        
        
        # First, process unsubscribe requests across all sent campaigns.
        campaigns = pm.campaigns()
        for campaign in campaigns['data']:
            if campaign['status'] == "sent":
                unsubscribes = pm.campaignUnsubscribes(cid=campaign['id'])
                for unsub in unsubscribes['data']:
                    email = unsub['email']
                    users = User.objects.filter(email=email)
                    for user in users:
                        options = EmailOptions.objects.filter(user=user)
                        if len(options) == 0:
                            o = EmailOptions(user=user, marketing=False)
                            print "Created new option for %s" % email
                            o.save()
                        else:
                            for o in options:                                
                                if o.marketing == True:
                                    print "Set marketing=false for %s" % email
                                    o.marketing = False
                                    o.save()
                        
                            
                    
        
        
        
        # Then, add all users who've logged in over the past 30 days who don't have marketing emails turned off.
        batch = []
        past_month = datetime.date.today() - datetime.timedelta(days=30)
        for user in User.objects.filter(last_login__gte=past_month):
            if user.email and user.email != "":
                try:
                    options = EmailOptions.objects.get(user=user)
                    if not options.marketing:
                        continue
                except:
                    pass
                
                if "scholastic" in user.email:
                    continue
        
                if "tomsnyder" in user.email:
                    continue
                
                batch.append({"EMAIL":user.email,"EMAIL_TYPE":"HTML"})
        try:
            for i in xrange(0, len(batch), 500):
                print pm.listBatchSubscribe(id="8d857d257e", email_address=user.email, double_optin=False, batch=batch[i:i+500])                                    
        except MailChimpException, e:
            print e
            print "Could not add"
        
                

        
       