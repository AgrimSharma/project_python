#!/usr/bin/env python
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from apps.organizations.models import Organization
from apps.subscription.models import Subscription
from apps.subscription.views import _updateOrganization

from django.core.management.base import BaseCommand, CommandError

import logging
from apps.subscription.spreedly import *

logger = logging.getLogger(__name__)

# Creates the intiial subscriptions for all organizations that previously existed.
class Command(BaseCommand):
  def handle(self, *args, **options):
    # m = {"bronze":11073, "silver":11074, "gold":11075}
    
    s = Spreedly()
    
    for organization in Organization.objects.filter(slug="inblau"):
        # organization = Organization.objects.get(slug=organization_slug)
        logger.debug(organization.slug)
        logger.debug(organization.subscription.plan.feature_level)
        
        # s.updateSubscriptionPlan(organization, 26020)
        
    

# https://spreedly.com/api/v4/meresheep/subscribers/44/change_subscription_plan.xml