#!/usr/bin/env python
from datetime import date, timedelta
from apps.projects.models import Project, Iteration, Story, PointsLog
from django.core.management.base import BaseCommand, CommandError

from apps.projects.calculation import calculateProject

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        for story in Story.objects.all().order_by("-id"):
            story.skip_haystack = True
            story.resetCounts()
            count+=1
            if (count % 100) == 0:
                print "%d stories processed..." % count
        print "%d stories processed..." % count
