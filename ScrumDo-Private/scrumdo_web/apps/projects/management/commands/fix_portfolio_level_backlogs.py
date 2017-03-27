#!/usr/bin/env python
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from apps.projects.models import Project, Portfolio
from apps.projects import portfolio_managers, managers


import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        root_projects = Project.objects.filter(project_type=2, active=True)
        for root_project in root_projects:
            try:
                portfolio = Portfolio.objects.get(root=root_project)
                for level in portfolio.levels.all():
                    try:
                        backlog = level.projects.get(project_type = Project.PROJECT_TYPE_BACKLOG_ONLY)
                    except ObjectDoesNotExist:
                        logger.info("Creating Backlog Project in Potfolio %d -> level %d " % (portfolio.id, level.id))
                        backlog = portfolio_managers.add_portfolio_level_backlog(portfolio, level)
                    except MultipleObjectsReturned:
                        logger.info("Multiple Backlog Projects in Potfolio %d -> level %d " % (portfolio.id, level.id))
                        backlogs = level.projects.filter(project_type = Project.PROJECT_TYPE_BACKLOG_ONLY).order_by("id")
                        c = 1
                        for backlog in backlogs:
                            if c != 1:
                                managers.delete_project(backlog)
                            c +=1

            except ObjectDoesNotExist:
                pass