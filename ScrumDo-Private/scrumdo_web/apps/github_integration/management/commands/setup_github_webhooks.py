#!/usr/bin/env python

# This is a fix-app to set github tags for a given project.


from apps.projects.time_report import generate_iteration_report
from apps.github_integration.models import GithubBinding, GithubCredentials
from apps.github_integration.utils import setupCallbacks
from apps.projects.models import Project
from django.core.management.base import BaseCommand

from apps.github_integration.utils import add_github_tags

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        project_slug = args[0]
        project = Project.objects.get(slug=project_slug)
        token = GithubCredentials.objects.get(project=project).oauth_token
        for binding in GithubBinding.objects.filter(project=project):
            setupCallbacks(token, binding, binding.project)





