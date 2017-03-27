#!/usr/bin/env python
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from apps.organizations.models import Organization
from apps.subscription.models import Subscription
from apps.activities.models import NewsItem

from django.core.management.base import BaseCommand, CommandError
import datetime

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        sixMonthsAgo = datetime.datetime.now() - datetime.timedelta(days=180)

        for organization in Organization.objects.filter(active=True, created__lte=sixMonthsAgo):
            subscription = organization.subscription

            if subscription.is_trial and subscription.expires >= datetime.date.today():
                continue  # Active Trial  (why is it so old?  Hmmm...)

            news = NewsItem.objects.filter(project__organization=organization).order_by("-created")[:1]
            if len(news) > 0 and news[0].created > sixMonthsAgo:
                continue  # There was news, so there is active use in the past 6 months.

            if subscription.token != '' and subscription.token is not None:
                continue  # anyone who paid, gets to stay

            # logger.debug("Might want to deactivate %s %s" % (organization.slug, news) )
            organization.active = False

            # Update: Don't want to do this, we'll just make code check for org active
            # for project in organization.projects.all():
            #     project.active = False

            organization.save()

