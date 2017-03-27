#!/usr/bin/env python

# This is a fix-app to set github tags for a given project.


from apps.projects.time_report import generate_iteration_report
from apps.projects.models import Project, Iteration
from django.core.management.base import BaseCommand, CommandError

from apps.github_integration.utils import add_github_tags

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        project_slug = args[0]
        project = Project.objects.get(slug=project_slug)
        for story in project.stories.all():
            add_github_tags(story)
            story.save()



