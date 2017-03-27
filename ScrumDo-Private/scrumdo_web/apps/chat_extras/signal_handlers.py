from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver

from apps.projects.models import StoryComment
from apps.projects.signals import story_updated, story_created, attachment_added

from apps.slack.models import SlackMapping
import apps.slack.tasks as slack_tasks

from apps.flowdock.models import FlowdockMapping
import apps.flowdock.tasks as flowdock_tasks

from apps.hipchat.models import HipChatMapping
import apps.hipchat.tasks as hipchat_tasks


@receiver(models.signals.post_save, sender=StoryComment, dispatch_uid="chat_extras")
def on_comment_posted(sender, **kwargs):
    try:
        comment = kwargs.get('instance')
        created_flag = kwargs.get('created')
        if not created_flag:
            return

        if HipChatMapping.objects.filter(comment_created=True, project_id=comment.story.project_id).exists():
            hipchat_tasks.on_comment_posted.apply_async(args=(comment.id,), countdown=4)
        if SlackMapping.objects.filter(comment_created=True, project_id=comment.story.project_id).exists():
            slack_tasks.on_comment_posted.apply_async(args=(comment.id,), countdown=4)
        if FlowdockMapping.objects.filter(comment_created=True, project_id=comment.story.project_id).exists():
            flowdock_tasks.on_comment_posted.apply_async(args=(comment.id,), countdown=4)
    except:
        pass


@receiver(attachment_added, dispatch_uid="chat_extras")
def on_attachment_added(sender, **kwargs):
    try:
        story = kwargs.get('story')
        fileData = kwargs.get('fileData')
        user = kwargs.get('user')
        if SlackMapping.objects.filter(card_modified=True, project_id=story.project_id).exists():
            slack_tasks.on_attachment_added(story.id, fileData)
        if FlowdockMapping.objects.filter(card_modified=True, project_id=story.project_id).exists():
            flowdock_tasks.on_attachment_added(story.id, fileData, _format_author(user))
        if HipChatMapping.objects.filter(card_modified=True, project_id=story.project_id).exists():
            hipchat_tasks.on_attachment_added(story.id, fileData, _format_author(user))
    except:
        pass


@receiver(story_created, dispatch_uid="chat_extras")
def on_story_created(sender, **kwargs):
    try:
        # NOTE - this event comes in a celery task already, no need to delay any sending from it.
        story = kwargs.get('story')
        user = kwargs.get('user')
        slack_tasks.on_card_created(story.id)
        flowdock_tasks.on_card_created(story.id, _format_author(user))
        hipchat_tasks.on_card_created(story.id, _format_author(user))
    except:
        pass


def _author(sender):
    if hasattr(sender, "user"):
        return _format_author(sender.user)
    else:
        return {
            'name': "ScrumDo",
            "avatar": "http://scrumdo-cdn.s3.amazonaws.com/manual_uploads/logos/48.png"
        }


def _format_author(user):
    return {
            'name': user.username,
            'avatar': "{base}{url}".format(base=settings.BASE_URL,
                                           url=reverse('avatar_redirect',
                                                       kwargs={'size': 48, 'username': user.username}))
        }


@receiver(story_updated, dispatch_uid="chat_extras")
def on_story_updated(sender, **kwargs):
    try:
        diffs = kwargs.get('diffs')
        story = kwargs.get('story')
        card_moved = 'cell_id' in diffs

        if SlackMapping.objects.filter(project_id=story.project_id).exists():
            slack_tasks.on_card_modified.apply_async(args=(story.id, diffs), countdown=4)
            if card_moved:
                slack_tasks.on_card_moved.apply_async(args=(story.id, diffs['cell_id']), countdown=2)


        if FlowdockMapping.objects.filter(project_id=story.project_id).exists():
            if card_moved:
                flowdock_tasks.on_card_moved.apply_async(args=(story.id, diffs['cell_id'], _author(sender)), countdown=2)
            flowdock_tasks.on_card_modified.apply_async(args=(story.id, diffs, _author(sender)), countdown=4)

        if HipChatMapping.objects.filter(project_id=story.project_id).exists():
            if card_moved:
                hipchat_tasks.on_card_moved.apply_async(args=(story.id, diffs['cell_id'], _author(sender)), countdown=2)
            hipchat_tasks.on_card_modified.apply_async(args=(story.id, diffs, _author(sender)), countdown=4)
    except Exception as e:
        pass





