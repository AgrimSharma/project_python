#!/usr/bin/env python
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

import datetime
from apps.organizations.models import Organization
from apps.subscription.models import Subscription
from apps.projects.models import Project
from apps.activities.models import NewsItem

from apps.subscription.spreedly import Spreedly

from django.contrib.auth.models import User

from django.core.management.base import BaseCommand, CommandError

import elementtree.ElementTree as ET


import logging

logger = logging.getLogger(__name__)

def _getText(nodelist):
  rc = []
  for node in nodelist.childNodes:
      if node.nodeType == node.TEXT_NODE:
          rc.append(node.data)
  return ''.join(rc)


class Command(BaseCommand):
    def handle(self, *args, **options):
        
        # spreedly = Spreedly()
        # subscribers_result = spreedly.getSubscribers()
        # subscribers = subscribers_result.getElementsByTagName("subscriber")
        # for subscriber in subscribers:
        #     if _getText(subscriber.getElementsByTagName("active")[0]) == "true":
        #         try:
        #             Organization.objects.get(slug=_getText(subscriber.getElementsByTagName("screen-name")[0]))
        #         except Organization.DoesNotExist:
        #             print "!!! %s" % _getText(subscriber.getElementsByTagName("screen-name")[0])
        #         
        # return
        
        organizations = Organization.objects.all() #filter(subscription__level__gte=1)
        t = datetime.datetime.today() - datetime.timedelta(days=30)
        for org in organizations:            
            users = org.subscription.usersUsed()
            projects = org.subscription.projectsUsed()
            storage = org.subscription.storageUsed()
            
            # if len(lu) > 0:
            #     print "%s %s" % (lu[0].date, t)

            # last_update = org.subscription
            if users > org.subscription.planUsers() or projects > org.subscription.planProjects():
                lu = NewsItem.objects.filter(project__organization=org).order_by("-created")[:1]
                if len(lu) > 0 and lu[0].created > t:
                    print "%s %d\t\t%s\t%d\t%d" % (str(org).ljust(45).decode("utf-8"),projects, org.subscription.plan.name, users,org.subscription.planUsers())
            
        
      
   
        
