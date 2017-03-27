#!/usr/bin/env python

from collections import defaultdict
from django.core.management.base import BaseCommand
from apps.classic import models as cmodels
from apps.kanban import models as kmodels
from apps.projects import models as pmodels
from datetime import timedelta
from apps.kanban.tasks import rebuildStepMovements
from apps.kanban.managers import moveStoryOntoCell


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
        logger.info("Attempting to copy cell locations from %s to %s" % (sourceSlug, destSlug))
        sourceProject = cmodels.Project.objects.get(slug=sourceSlug)
        destProject = pmodels.Project.objects.get(slug=destSlug)

        cells = {}
        cells[1] = destProject.boardCells.get(label='Todo')
        cells[4] = destProject.boardCells.get(label='In Progress')
        cells[7] = destProject.boardCells.get(label='Review')
        cells[8] = destProject.boardCells.get(label='Blocked')
        cells[6] = cells[5] = destProject.boardCells.get(label='Wait')
        cells[10] = destProject.boardCells.get(label='Done')

        for card in destProject.stories.filter(cell=None, iteration__iteration_type=1):
            logger.info(card.local_id)
            try:
                story = cmodels.Story.objects.get(project=sourceProject, local_id=card.local_id)
                if story.status in cells:
                    moveStoryOntoCell(card, cells[story.status], None)
            except cmodels.Story.DoesNotExist:
                pass

