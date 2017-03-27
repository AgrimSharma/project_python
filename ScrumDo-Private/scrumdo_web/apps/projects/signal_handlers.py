# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


from django.db import models
from django.dispatch import receiver

from apps.extras.models import ExternalStoryMapping
from apps.projects.tasks import queueCalculateStoryRollUpTime, queueUpdateSolr, clear_iteration_schedules
from apps.projects.models import *

from apps.realtime.util import send_story_patch

import sys, traceback
import logging

logger = logging.getLogger(__name__)


@receiver(models.signals.post_save, sender=ExternalStoryMapping, dispatch_uid="projects_models_integrity")
@receiver(models.signals.post_delete, sender=ExternalStoryMapping, dispatch_uid="projects_models_integrity")
def mapping_callback(sender,instance,**kwargs):
    try:
        story = instance.story
        story.resetExternalLinksCount()
        story.save()
    except:
        logger.error("Could not update external link counts")


@receiver(models.signals.post_save, sender=Task, dispatch_uid="projects_models_integrity")
@receiver(models.signals.post_delete, sender=Task, dispatch_uid="projects_models_integrity")
def task_callback(sender,instance,**kwargs):
    """When a task is created or deleted, we update the number of tasks in the associated story"""
    try:
        story = instance.story
        story.resetTaskCount()
        story.save()
        send_story_patch(story.project, story, {'task_counts': story.taskCountsArray(), 'task_count': story.task_count})
        queueCalculateStoryRollUpTime(story.id)
        queueUpdateSolr(story.id)
    except Story.DoesNotExist as e:
        pass
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        logger.error("Could not update task counts")


@receiver(models.signals.post_save, sender=Epic, dispatch_uid="projects_models_integrity")
@receiver(models.signals.post_delete, sender=Epic, dispatch_uid="projects_models_integrity")
def epic_callback(sender, instance, **kwargs):
    try:
        if hasattr(instance, "skip_story_labels"):
            # We can opt-out of this in time sensitive operations where we know
            # the label didn't change by setting skip_story_labels on epic before
            # saving it.
            return

        newLabel = instance.short_name()[-32:]
        for story in instance.stories.all():
            if story.epic_label != newLabel:
                story.epic_label = newLabel
                story.save()
    except:
        traceback.print_exc(file=sys.stdout)
        logger.error("Could not update epic counts")


@receiver(models.signals.post_save, sender=Iteration, dispatch_uid="projects_models_integrity")
def iteration_callback(sender, instance, **kwargs):
    try:
        iteration = instance
        if iteration.hidden is True:
            clear_iteration_schedules(iteration)
    except:
        traceback.print_exc(file=sys.stdout)
        logger.error("Could not clear Iteration Schedules")