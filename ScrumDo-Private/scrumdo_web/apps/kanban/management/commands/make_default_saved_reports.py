#!/usr/bin/env python

from apps.projects.models import Project, Story
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

import sys, traceback
import getopt
import logging

import apps.kanban.managers as kanban_managers

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--project', '-p', dest='project_slug',  help='Help for the long options'),
        )
    args = "project"
    def handle(self, *args, **options):
        slug = options["project_slug"]
        if slug:
            projects = Project.objects.filter(slug=slug)
        else:
            projects = Project.objects.filter(abandoned=False, active=True, project_type__in=[Project.PROJECT_TYPE_KANBAN, Project.PROJECT_TYPE_PORTFOLIO])
        
        for project in projects:
            try:
                kanban_managers.createDefaultSavedReports(project)
            except:
                logger.warn("Could not calculate project: %s" % project.slug)


        
