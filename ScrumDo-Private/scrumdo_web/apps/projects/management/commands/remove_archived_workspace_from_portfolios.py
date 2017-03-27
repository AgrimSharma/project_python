#!/usr/bin/env python
from apps.projects.models import Project, Iteration, Story, PointsLog
from django.core.management.base import BaseCommand, CommandError
from apps.projects.portfolio_managers import remove_project_from_portfolio

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        projects = Project.objects.filter(active=False).exclude(portfolio_level=None)
        for project in projects:
            logger.info(project.slug)
            remove_project_from_portfolio(project)
