#!/usr/bin/env python
from apps.projects.models import Project, Iteration, Story, PointsLog
from django.core.management.base import BaseCommand, CommandError
from haystack import site

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        rank = 5000
        for story in Story.objects.filter(project__slug=args[0]).order_by("rank"):
            logger.info("%d %d->%d" % (story.id, story.rank, rank))
            story.rank = rank
            story.skip_haystack = True
            rank += 5000
            story.save()
        logger.info("---")
        rank = 5000
        for story in Story.objects.filter(project__slug=args[0]).order_by("epic_rank"):
            logger.info("%d %d->%d" % (story.id, story.epic_rank, rank))
            story.epic_rank = rank
            story.skip_haystack = True
            rank += 5000
            story.save()
