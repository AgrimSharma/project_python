#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import logging
import mixpanel
import datetime
from apps.kanban.models import KanbanStat
from apps.organizations.models import Organization
from apps.activities.models import NewsItem

from apps.classic import models as classic_models

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)

        today = datetime.date.today()
        mdiff = datetime.timedelta(days=-7)
        date_30days_Agoago = today + mdiff

        for organization in Organization.objects.filter(active=True).order_by("-id"):
            activity30day = NewsItem.objects.filter(created__gte=date_30days_Agoago, project__organization=organization).count()
            totalActivity = NewsItem.objects.filter(project__organization=organization).count()
            if activity30day == 0:
                continue  # old org with no activity in the past 30 days that we don't care about
            subscription = organization.subscription


            classicactivity30day = classic_models.NewsItem.objects.filter(created__gte=date_30days_Agoago, project__organization=organization).count()
            # for project in organization.projects.filter(active=True):
            #     try:
            #         stat = KanbanStat.objects.filter(project=project).order_by("-created")[0]
            #     except:
            #         pass
            if subscription.expires is not None:
                expires = subscription.expires.strftime('%Y-%m-%d'),
            else:
                expires = ''

            email = organization.creator.email

            if totalActivity <= 3:
                activity_description = "None"
            elif totalActivity < 12:
                activity_description = "Minimal"
            elif totalActivity < 30:
                activity_description = "Adequate"
            else:
                activity_description = "Lots"



            g1 = str(organization.id % 2)
            g2 = str(organization.id % 3)
            g3 = str(organization.id % 4)
            g4 = str(organization.id % 5)
            mp.people_set_once(organization.slug,
                               {'Test Group 1 s': g1,
                                'Test Group 2 s': g2,
                                'Test Group 3 s': g3,
                                'Test Group 4 s': g4})

            mp.people_set(organization.slug, {
                'name':  organization.name,
                'slug':  organization.slug,
                'creator': organization.creator.email,
                '30 day activity': activity30day,
                '30 day classic activity': classicactivity30day,
                'total activity': totalActivity,
                'activity description': activity_description,
                'dashboard': "https://app.scrumdo.com/organization/%s/dashboard" % organization.slug,
                'classic dashboard': "https://www.scrumdo.com/organization/%s/dashboard" % organization.slug,
                'plan': subscription.planName(),
                'price': subscription.planPrice(),
                'projects': subscription.projectsUsed(),
                'classic projects': organization.classic_projects.filter(active=True).count(),
                'users': subscription.usersUsed(),
                'storage': subscription.storageUsed(),
                'is trial': subscription.is_trial,
                'paid': subscription.total_revenue > 0 and subscription.active,
                'expires': expires,
                'total revenue': float(subscription.total_revenue),
                'trial month': organization.created.strftime('%Y-%m'),
                'trial week': organization.created.strftime('%Y-%U'),
                'created': organization.created.strftime('%Y-%m-%dT%H:%M:%S'),
                'private projects': organization.projects.filter(active=True, private=True).count(),
                'private projects allowed': organization.allow_personal,
                'timezone': organization.timezone,
                'source': organization.source,
                '$email': email

            })
            logger.info(u'Logged %s' % organization.slug)

