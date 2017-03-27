#!/usr/bin/env python

# We are currently in a situation where some stories didn't have a CellMovement record created for
# their last move (usually an iteration move outside the board).  This script will find any story
# that is in an iteration/cell but it's last CellMovement didn't put it there and create a neww
# CellMovement record.

from apps.kanban.models import CellMovement
from apps.kanban.tasks import scheduleRebuildStepMovements
from apps.kanban.managers import setCellMovementStoryProperties
from apps.projects.models import Project, Iteration, Story, PointsLog, SiteStats
from django.core.management.base import BaseCommand

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def __init__(self):
        self.count = 0

    def handle(self, *args, **options):
        for project in Project.objects.filter(project_type=Project.PROJECT_TYPE_KANBAN, active=True):
            self.processProject(project)
        print "%d records created" % self.count

    def processProject(self, project):
        createdRecord = False
        for story in project.stories.all():
            createdRecord = self.processStory(story) or createdRecord
        if createdRecord:
            scheduleRebuildStepMovements(project)

    def processStory(self, story):
        movements = CellMovement.objects.filter(story=story).order_by("-created")
        if movements.count() == 0:
            # There are no previous movements.  We should create the record if we're in a work iteration.
            if story.iteration.iteration_type == Iteration.ITERATION_WORK:
                # print "Creating record because there weren't any.  #%d (%d) %s" % (story.local_id, story.id, story.project.slug)
                self.createMissingRecord(story)
                return True
            return False
        lastMovement = movements[0]
        if (lastMovement.related_iteration_id != story.iteration_id) or (lastMovement.cell_to != story.cell):
            # print "Creating record because there is a mismatch.  #%d (%d) %s" % (story.local_id, story.id, story.project.slug)
            # print "iteration %s/%s  Cell %s/%s" % (lastMovement.related_iteration, story.iteration, lastMovement.cell_to, story.cell)
            self.createMissingRecord(story)
            return True
        return False

    def createMissingRecord(self, story):
        movement = CellMovement(story=story, cell_to=story.cell, related_iteration=story.iteration)
        setCellMovementStoryProperties(movement, story)
        movement.save()
        movement.created = story.modified  # created is auto-set, have to do it after creation.
        movement.save()
        self.count += 1
        print "%d, %d, %s" % (movement.id, story.id, story.project.slug)
