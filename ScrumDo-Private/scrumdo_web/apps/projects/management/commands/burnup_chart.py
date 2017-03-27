#!/usr/bin/env python
from datetime import date, timedelta
from apps.projects.models import Project, Iteration, Story, PointsLog, Release
from apps.organizations.models import *
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Sum
from apps.projects.calculation import calculateProject, calculateReleaseStats
from rollbardecorator import logexception

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    @logexception
    def handle(self, *args, **options):
        today = datetime.date.today()
        mdiff = datetime.timedelta(days=-120)
        date_120days_ago = today + mdiff
        OrganizationVelocityLog.objects.filter(created__lte=date_120days_ago).delete()

        for project in Project.objects.filter(project_type=Project.PROJECT_TYPE_PORTFOLIO):
            for story in project.stories.all():
                calculateReleaseStats(story, False)

        projects = Project.objects.filter(active=True, organization__active=True)
        for project in projects:
            try:
                if project.newsItems.count() == 0:
                    # logger.debug("Skipping project %s" % project.slug)
                    continue  # an old project with no activity recently.

                calculateProject(project)
            except:
                logger.error("Could not calculate project %s" % project.slug)

