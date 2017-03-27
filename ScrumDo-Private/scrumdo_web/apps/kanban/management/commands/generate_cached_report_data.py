#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError

import logging
import datetime
import os

from apps.kanban.models import Workflow
from apps.kanban.util import conditionalGenerateCellReportData
from apps.projects.models import Project


logger = logging.getLogger(__name__)

# Generates new cached report data for all projects with activity in the last 7 days
class Command(BaseCommand):
    def handle(self, *args, **options):
        sevenDaysAgo = datetime.datetime.now() - datetime.timedelta(days=7)
        for project in Project.objects.all():
            if project.newsItems.filter(created__gt=sevenDaysAgo).count() > 0:
                for workflow in Workflow.objects.filter(project=project):
                    logger.info("Generating {project.slug}, {workflow.id}".format(project=project, workflow=workflow))
                    filename = conditionalGenerateCellReportData(project, workflow)
                    if filename:
                        os.unlink(filename)


