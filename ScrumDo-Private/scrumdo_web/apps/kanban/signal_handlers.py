from apps.projects.models import Story
from apps.kanban.models import TagMovement
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Story, dispatch_uid="kanban_signal_handler_movements")
def check_movement_records(sender, **kwargs):
    story = kwargs.get("instance", None)
    if story is None:
        return
    changed = story.tracker.changed()
    if "tags_cache" in changed:
        movement = TagMovement(story=story, tags_cache=story.tags_cache)
        if story.epic_id:
            movement.epic_id = story.epic_id
        movement.related_iteration_id = story.iteration_id
        movement.label_ids = ",".join([str(label.id) for label in story.labels.all()])
        movement.assignee_ids = ",".join([str(assignee.id) for assignee in story.assignee.all()])
        movement.points_value = story.points_value()
        movement.save()
        movement.save()

    # if "cell_id" in changed:
    #     logger.info("CELL ID CHANGED")
