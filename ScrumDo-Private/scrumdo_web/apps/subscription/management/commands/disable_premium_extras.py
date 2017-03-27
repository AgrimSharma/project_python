#!/usr/bin/env python
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

import datetime
from apps.organizations.models import Organization
from apps.subscription.models import Subscription
from apps.projects.models import Project

from django.contrib.auth.models import User

from django.core.management.base import BaseCommand, CommandError

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        organizations = Organization.objects.all() #filter(subscription__level__gte=1)
        for org in organizations:            
            if org.subscription.planPremiumExtras():
                continue
            
            for project in org.projects.all():
                logger.debug(project)
            
        
      
   
        
