from django.dispatch import receiver
from django.db import models

import tasks
import apps.projects.signals as project_signals
from apps.projects.models import StoryComment, Note, NoteComment

import logging

logger = logging.getLogger(__name__)


@receiver(models.signals.post_save, sender=StoryComment, dispatch_uid="scrumdo_inbox")
def on_comment_posted(instance, **kwargs):
    try:
        tasks.on_comment_posted.delay(instance.id)
    except:
        logger.error("on_comment_posted")




@receiver(project_signals.epic_created, dispatch_uid='scrumdo_inbox')
def on_epic_created(**kwargs):
    try:
        tasks.on_epic_created.delay(kwargs["epic"].id, kwargs["user"].id)
    except:
        logger.error("on_epic_created")


@receiver(project_signals.epic_updated, dispatch_uid='scrumdo_inbox')
def on_epic_updated(**kwargs):
    try:
        tasks.on_epic_updated.delay(kwargs["epic"].id, kwargs["user"].id, kwargs['diffs'])
    except:
        logger.error("on_epic_updated")


@receiver(project_signals.project_created, dispatch_uid='scrumdo_inbox')
def on_project_created(**kwargs):
    try:
        tasks.on_project_created.delay(kwargs["project"].slug, kwargs["user"].id)
    except:
        logger.error("on_project_created")


@receiver(project_signals.story_updated, dispatch_uid='scrumdo_inbox')
def on_story_updated(**kwargs):
    try:
        tasks.on_story_updated.delay(kwargs["story"].id, kwargs["user"].id, kwargs["diffs"])
    except:
        logger.error("on_story_updated")



@receiver(project_signals.story_deleted, dispatch_uid='scrumdo_inbox')
def on_story_deleted(**kwargs):
    try:
        tasks.on_story_deleted.delay(kwargs["story"].id, kwargs["user"].id)
    except:
        logger.error("on_story_deleted")


@receiver(project_signals.story_created, dispatch_uid='scrumdo_inbox')
def on_story_created(**kwargs):
    try:
        tasks.on_story_created.delay(kwargs["story"].id, kwargs["user"].id)
    except:
        logger.error("on_story_created")


@receiver(project_signals.story_moved, dispatch_uid='scrumdo_inbox')
def on_story_moved(**kwargs):
    try:
        tasks.on_story_moved.delay(kwargs["story"].id, kwargs["user"].id, kwargs['diffs'])
    except:
        logger.error("on_story_moved")



@receiver(project_signals.task_created, dispatch_uid='scrumdo_inbox')
def on_task_created(**kwargs):
    try:
        tasks.on_task_created.delay(kwargs["task"].id, kwargs["user"].id)
    except:
        logger.error("on_task_created")



@receiver(project_signals.task_status_changed, dispatch_uid='scrumdo_inbox')
def on_task_status_changed(**kwargs):
    try:
        tasks.on_task_status_changed.delay(kwargs["task"].id, kwargs["user"].id)
    except:
        logger.error("on_task_status_changed")


@receiver(project_signals.task_updated, dispatch_uid='scrumdo_inbox')
def on_task_updated(**kwargs):
    try:
        tasks.on_task_updated.delay(kwargs["task"].id, kwargs["user"].id)
    except:
        logger.error("on_task_updated")


@receiver(project_signals.iteration_created, dispatch_uid='scrumdo_inbox')
def on_iteration_created(**kwargs):
    tasks.on_iteration_created.delay(kwargs["iteration"].id, kwargs["user"].id)


@receiver(project_signals.iteration_updated, dispatch_uid='scrumdo_inbox')
def on_iteration_updated(**kwargs):
    tasks.on_iteration_updated.delay(kwargs["iteration"].id, kwargs["user"].id, kwargs["hidden"])


@receiver(project_signals.attachment_added, dispatch_uid='scrumdo_inbox')
def on_attachment_added(**kwargs):
    try:
        tasks.on_attachment_added.delay(kwargs["story"].id, kwargs["user"].id, kwargs["fileData"])
    except:
        logger.error("on_attachment_added")

@receiver(project_signals.note_created, dispatch_uid="scrumdo_inbox")
def on_note_created(**kwargs):
    try:
        tasks.on_note_created.delay(kwargs["note"].id, False)
    except:
        logger.error("on_note_created")

@receiver(project_signals.note_updated, dispatch_uid="scrumdo_inbox")
def on_note_updated(**kwargs):
    try:
        tasks.on_note_created.delay(kwargs["note"].id, True)
    except:
        logger.error("on_note_updated")

@receiver(project_signals.note_deleted, dispatch_uid="scrumdo_inbox")
def on_note_deleted(**kwargs):
    try:
        tasks.on_note_deleted.delay(kwargs["note"].id)
    except:
        logger.error("on_note_deleted")

@receiver(models.signals.post_save, sender=NoteComment, dispatch_uid="scrumdo_inbox")
def on_note_comment_posted(instance, **kwargs):
    try:
        tasks.on_note_comment_posted.delay(instance.id)
    except:
        logger.error("on_note_comment_posted")

@receiver(project_signals.note_attachment_added, dispatch_uid='scrumdo_inbox')
def on_note_attachment_added(**kwargs):
    try:
        tasks.on_note_attachment_added.delay(kwargs["note"], kwargs["user"].id, kwargs["fileData"])
    except:
        logger.error("on_note_attachment_added")