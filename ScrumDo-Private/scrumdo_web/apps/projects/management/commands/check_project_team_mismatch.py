#!/usr/bin/env python

# Checks Team <-> Project associations to make sure all projects in teams
# are part of the same organization.

from apps.projects.models import Project, Iteration, Story, PointsLog, SiteStats
from apps.extras.models import *
from mailer.models import Message
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.organizations.models import *
from apps.projects.models import Project

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        for team in Team.objects.all():
            for project in team.projects.all():
                if team.organization_id != project.organization_id:
                    logger.warn("MISMATCH %d %d %s" % (team.id, project.id, project.slug))