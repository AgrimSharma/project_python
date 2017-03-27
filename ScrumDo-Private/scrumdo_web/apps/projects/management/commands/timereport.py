#!/usr/bin/env python

# This is a test app to run the time report for a given project.


from apps.projects.time_report import generate_iteration_report
from apps.projects.models import Project, Iteration
from django.core.management.base import BaseCommand, CommandError

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        project_slug = args[0]
        iteration_id = int(args[1])
        w = generate_iteration_report(Project.objects.get(slug=project_slug),
                                  Iteration.objects.get(id=iteration_id))
        w.save("time_report.xls")