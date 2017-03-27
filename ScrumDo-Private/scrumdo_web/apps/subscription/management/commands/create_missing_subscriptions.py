#!/usr/bin/env python
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from apps.organizations.models import Organization
from apps.subscription.models import Subscription


from django.core.management.base import BaseCommand, CommandError

# Creates the intiial subscriptions for all organizations that previously existed.
class Command(BaseCommand):
  def handle(self, *args, **options):
    for organization in Organization.objects.all():
      needs_sub = False
      try:
        if organization.subscription == None:
          needs_sub = True
      except:
        needs_sub = True
      
      if needs_sub:
        print "Creating subscription for %s" % organization.slug
        organization.subscription = Subscription.generateFreeSubscription(organization)
        
