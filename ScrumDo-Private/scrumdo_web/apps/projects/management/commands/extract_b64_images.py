#!/usr/bin/env python

from apps.projects.util import extractInlineImagesForStory, stripInlineImages
from apps.extras.models import *
from apps.activities.models import NewsItem


from django.core.management.base import BaseCommand, CommandError

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for story in Story.objects.all().order_by("-id"):
            if extractInlineImagesForStory(story):
                # The story was modified.
                logger.info("Modified story /projects/story_permalink/{story.id}".format(story=story))
                story.save()
                for news in NewsItem.objects.filter(related_story=story):
                    news.text = stripInlineImages(news.text)
                    news.save()
