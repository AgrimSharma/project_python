#!/usr/bin/env python
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from apps.organizations.models import Organization
from apps.activities.models import NewsItem
from apps.subscription.views import _updateOrganization
from django.core.management.base import BaseCommand, CommandError

import datetime

import logging

logger = logging.getLogger(__name__)


# Creates the intiial subscriptions for all organizations that previously existed.
class Command(BaseCommand):
  def handle(self, *args, **options):
      weekago = datetime.datetime.now() - datetime.timedelta(days=7)
      for organization in Organization.objects.exclude(subscription__token='').order_by("-id"):
          if organization.subscription.token != "":
              if _updateOrganization(organization):
                  # They were changed!
                  activity = NewsItem.objects.filter(created__gte=weekago, project__organization=organization).count()
                  logger.info("Org activity in last week: %d" % activity)
              # logger.info("--------------")

        
