#!/usr/bin/env python

from apps.activities.models import NewsItem
from apps.projects.access import has_write_access
from django.core.management.base import BaseCommand, CommandError
import logging
import string
logger = logging.getLogger(__name__)

string_types = (string.ascii_lowercase, string.ascii_uppercase, string.digits)

class Command(BaseCommand):
    def handle(self, *args, **options):
        items = NewsItem.objects.exclude(project=None).exclude(user=None)
        c = 0
        for item in items:   
            if not has_write_access(item.project, item.user):
                logger.debug("%d" % item.id)
                c += 1
        logger.debug("%d problems" % c)
        
        
