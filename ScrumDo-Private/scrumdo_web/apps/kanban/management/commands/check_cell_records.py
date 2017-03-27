#!/usr/bin/env python

from apps.projects.models import Project, Story, Iteration, PointsLog
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from apps.kanban.managers import checkCellMovements
from apps.kanban.tasks import scheduleRebuildStepMovements

import logging

import datetime


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--project', '-p', dest='project_slug',  help='Help for the long options'),
            make_option('--all', action='store_true', dest='all', default=False, help='Rebuild all projects'),
            make_option('--days', action='store', dest='days', default=0, help='Number of days to look back'),
        )
    args = "project"
    def handle(self, *args, **options):
        allProjects = options["all"]
        totalGood = 0
        totalBad = 0
        if allProjects:
            projects = Project.objects.filter(abandoned=False, active=True)
        else:
            slug = options["project_slug"]
            try:
                projects = [Project.objects.get(slug=slug)]
            except Project.DoesNotExist:
                print "Could not find project."
                return

        for project in projects:
            stories = project.stories.all()
            days = int(options["days"])
            if days > 0:
                beginning = datetime.date.today() - datetime.timedelta(days=days)
                stories = stories.filter(modified__gt=beginning)

            ok, bad = checkCellMovements(stories)
            totalGood += ok
            totalBad += bad
            if bad > 0:
                logger.info("Project %s had problems" % project.slug)
                scheduleRebuildStepMovements(project)
        if totalBad > 0:
            logger.warn("Total good: %d, bad: %d" % (totalGood, totalBad) )


