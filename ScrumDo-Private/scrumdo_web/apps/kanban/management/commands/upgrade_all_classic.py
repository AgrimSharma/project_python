#!/usr/bin/env python

from django.core.management.base import BaseCommand

import logging
import datetime
import apps.classic.models as cmodels
from apps.subscription.decorators import isExpired
from apps.projects.models import Project, OfflineJob
from apps.kanban.tasks import convertClassicProject
import time
logger = logging.getLogger(__name__)

from django.contrib.auth.models import User

class Command(BaseCommand):
    def upgrade(self, project):
        logger.info("Upgrading %s" % project.slug)
        job = OfflineJob(organization=project.organization, owner=User.objects.get(username='mhughes'), completed=False, job_type="Auto Upgrading Project")
        job.save()
        convertClassicProject(project.id, 'perm', job.id)

    def shouldUpgrade(self, project, cutoff):
        # Criteria for upgrading.
        #
        # 1. The organization is active (subscription or trial)
        # 2. Has activity in the past 30 days
        # 3. Has at least one card in it
        # 4. The organization does not have a new project with the same name

        if project.organization is None:
            return False
        if isExpired(project.organization):
            # logger.debug('org is expired')
            return False
        if cmodels.NewsItem.objects.filter(created__gt=cutoff, project=project)[:1].count() == 0:
            # logger.debug('no news activity')
            return False
        if Project.objects.filter(organization=project.organization, name=project.name).count() > 0:
            # logger.debug('existing project with name')
            return False
        if cmodels.Story.objects.filter(project=project)[:1].count() == 0:
            # logger.debug('no cards in project')
            return False

        return True

    def handle(self, *args, **options):
        cutoff = datetime.date.today() - datetime.timedelta(days=30)
        upgraded = 0
        cards = 0
        error = 0
        for project in cmodels.Project.objects.filter(active=True).order_by("-created"):
            if self.shouldUpgrade(project, cutoff):
                logger.info("===============================================")
                try:
                    startTime = time.time()
                    self.upgrade(project)
                    c = cmodels.Story.objects.filter(project=project).count()
                    cards += c
                    logger.info("Took %d seconds" % (time.time() - startTime))
                    logger.info("%d cards %d newsitems" % (c,
                                                           cmodels.NewsItem.objects.filter(project=project).count()))
                except:
                    logger.error("*****************************************")
                    logger.error("Could not upgrade %s" % project.slug)
                    logger.error("*****************************************")
                    error += 1
                upgraded += 1

        logger.info("Upgraded %d projects" % upgraded)
        logger.info("Could not upgrade %d projects" % error)

