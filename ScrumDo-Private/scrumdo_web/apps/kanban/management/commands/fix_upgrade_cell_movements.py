#!/usr/bin/env python

from collections import defaultdict
from django.core.management.base import BaseCommand
from apps.classic import models as cmodels
from apps.kanban import models as kmodels
from apps.projects import models as pmodels
from datetime import timedelta
from apps.kanban.tasks import rebuildStepMovements


import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def printHelp(self):
        logger.info("Usage:")
        logger.info("  fix_upgrade_cell_movements sourceSlug destSlug")
        logger.info("  Source is a CLASSIC project")
        logger.info("  Destination is a V2 project")

    def handle(self, *args, **options):
        if len(args) != 2:
            self.printHelp()
            return
        sourceSlug = args[0]
        destSlug = args[1]
        logger.info("Attempting to copy CellMovement created date from %s to %s" % (sourceSlug, destSlug))
        sourceProject = cmodels.Project.objects.get(slug=sourceSlug)
        destProject = pmodels.Project.objects.get(slug=destSlug)
        destMovements = kmodels.CellMovement.objects.filter(story__project=destProject).order_by('created')

        conversionDate = destMovements[0].created + timedelta(minutes=30)  # We'll assume the conversion took less than 30 minutes.

        destMovements = kmodels.CellMovement.objects.filter(story__project=destProject, created__lt=conversionDate).order_by('created','id')
        sourceMovements = cmodels.CellMovement.objects.filter(story__project=sourceProject, created__lt=conversionDate).order_by('created', 'id')

        logger.info("%d source movements, %d destination movements" % (sourceMovements.count(), destMovements.count()))
        sourceStories = defaultdict(list)
        destStories = defaultdict(list)

        fixed = 0

        for source in sourceMovements:
            sourceStories[source.story.local_id].append(source)
        for dest in destMovements:
            destStories[dest.story.local_id].append(dest)

        for story_id, destMovements in destStories.iteritems():
            sourceMovements = sourceStories[story_id]
            logger.info("Story %d (%d/%d) (source/dest)" % (story_id, len(sourceMovements), len(destMovements)))
            for destMovement in destMovements:
                destKey = "%s %s %s %s" % (destMovement.user,
                                        destMovement.story.local_id,
                                        getattr(destMovement.cell_to, "label", "-"),
                                        getattr(destMovement.related_iteration, "name", "-"))
                for sourceMovement in sourceMovements:
                    sourceKey = "%s %s %s %s" % (sourceMovement.user,
                                        sourceMovement.story.local_id,
                                        getattr(sourceMovement.cell_to, "label", "-"),
                                        getattr(sourceMovement.related_iteration, "name", "-"))
                    if sourceKey == destKey:
                        # The first record that matches and we can probably use it's created date.
                        destMovement.created = sourceMovement.created
                        destMovement.save()
                        logger.info("   Setting %s to %s" % (destKey, sourceMovement.created))
                        sourceMovements.remove(sourceMovement)
                        fixed += 1
                        break  # get out of the sourceMovements loop since we only want to update the record once.
            logger.info("Source Records not used:")
            for sourceMovement in sourceMovements:
                logger.info("    x %s %s %s %s" % (sourceMovement.user,
                                    sourceMovement.story.local_id,
                                    getattr(sourceMovement.cell_to, "label", "-"),
                                    getattr(sourceMovement.related_iteration, "name", "-")))


        logger.info("Fixed %d records" % fixed)
        job = kmodels.RebuildMovementJob(project=destProject, initiator=None)
        job.save()
        rebuildStepMovements(job.id)

