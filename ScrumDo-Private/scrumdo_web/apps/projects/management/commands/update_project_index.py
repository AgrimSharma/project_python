#!/usr/bin/env python
from apps.projects.models import Project, Story
from apps.projects.tasks import updateProjectIndexes
from django.core.management.base import BaseCommand
from django.conf import settings
from haystack import connections
from elasticsearch.exceptions import NotFoundError
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('project_slug', nargs='+', type=str)

    def handle(self, *args, **options):
        count = 0
        self.backend = connections['default'].get_backend()
        self.index = connections['default'].get_unified_index().get_index(Story)
        slug = options['project_slug'][0]
        if slug == 'ALL':
            for project in Project.objects.filter(active=True, abandoned=False).order_by("-id"):
                self.update_project(project.slug)
                count += 1
        else:
            self.update_project(slug)

    def update_project(self, project_slug):
        updateProjectIndexes.delay(project_slug)
