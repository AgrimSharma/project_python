#!/usr/bin/env python

from apps.projects.models import categoryCardTypeToLabels
from datetime import date, timedelta
from apps.projects.models import Project, Iteration, Story, PointsLog
from django.core.management.base import BaseCommand, CommandError

from apps.projects.calculation import calculateProject

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):

        for story in Story.objects.all().select_related("project").order_by("-id"):
            categoryCardTypeToLabels(story)


