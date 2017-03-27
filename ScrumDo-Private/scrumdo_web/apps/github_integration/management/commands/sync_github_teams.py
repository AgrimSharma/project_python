#!/usr/bin/env python
from django.core.management.base import BaseCommand

from apps.github_integration.models import *
from apps.github_integration.tasks import syncronize_teams

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for ghorganization in GithubOrganization.objects.all():
            syncronize_teams(ghorganization.organization.slug)


