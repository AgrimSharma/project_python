# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.


from django.template.loader import render_to_string
import sys

from models import *

from apps.activities.models import *
import apps.projects.limits as limits
import apps.projects.signals as signals
from apps.projects.models import StoryComment, Note
from apps.realtime.models import ChatMessage
from apps.projects.access import has_read_access
from tasks import sendMentionEmail, sendChatMentionEmail, sendNoteMentionEmail
import apps.projects.diffs as pdiffs

from django.dispatch import receiver
from django.core.urlresolvers import reverse

import re
import traceback
import logging

import apps.html2text as html2text

CACHE_TIMEOUT = 60

logger = logging.getLogger(__name__)


def _checkFieldForMention(oldValue, newValue, story, creator):    
    if hasattr(story, "skip_mentions"):
        return
    # logger.debug("Checking field for mention %s" % newValue)
    
    #texteditor insert &nbsp;after mentioned username and it becomes @username&nbsp;
    #remove html entities so @username can be identified
    oldValue = html2text.html2text(oldValue)
    newValue = html2text.html2text(newValue)
    
    old_usernames = re.findall("@([^<>\s]+)", oldValue)
    new_usernames = re.findall("@([^<>\s]+)", newValue)
    added_usernames = list(set(new_usernames).difference(set(old_usernames)))
    for username in added_usernames:
        try:
            user = User.objects.get(username=username)
            if not has_read_access(story.project, user):
                continue

            mention = StoryMentions(story=story, user=user, creator=creator)
            mention.save()
            sendMentionEmail.apply_async((mention.id,), countdown=3)
        except User.DoesNotExist:
            pass # that's fine, wasn't really a mention at all.

def _checkNoteFieldForMention(oldValue, newValue, note, creator):    

    #texteditor insert &nbsp;after mentioned username and it becomes @username&nbsp;
    #remove html entities so @username can be identified
    oldValue = html2text.html2text(oldValue)
    newValue = html2text.html2text(newValue)
    old_usernames = re.findall("@([^<>\s]+)", oldValue)
    new_usernames = re.findall("@([^<>\s]+)", newValue)
    added_usernames = list(set(new_usernames).difference(set(old_usernames)))
    for username in added_usernames:
        try:
            user = User.objects.get(username=username)
            if not has_read_access(note.project, user):
                continue

            mention = NoteMentions(note=note, user=user, creator=creator)
            mention.save()
            sendNoteMentionEmail.apply_async((mention.id,), countdown=3)
        except User.DoesNotExist:
            pass # that's fine, wasn't really a mention at all.

def _checkChatMessageForMention(message, project, creator):    
    #logger.debug("Checking field for mention %s" % message)
    new_usernames = re.findall("@([^<>\s]+)", message)
    added_usernames = list(set(new_usernames))

    for username in added_usernames:
        try:
            user = User.objects.get(username=username)
            if not has_read_access(project, user):
                continue

            mention = ChatMentions(project=project, user=user, message=message, creator=creator)
            mention.save()
            sendChatMentionEmail.apply_async((mention.id,), countdown=3)
        except User.DoesNotExist:
            pass # that's fine, wasn't really a mention at all.

def _checkDiffsForMention(diffs, story, creator):
    mention_fields = ["summary","detail","extra_1","extra_2","extra_3"]
    if diffs == None:
        return
    for k,v in diffs.iteritems():
        if k in mention_fields:
            _checkFieldForMention(v[0], v[1], story, creator)

def _checkNoteDiffsForMention(diffs, note, creator):
    mention_fields = ["body"]
    if diffs == None:
        return
    for k,v in diffs.iteritems():
        if k in mention_fields:
            _checkNoteFieldForMention(v[0], v[1], note, creator)


def _createStoryEmailQueueItem(queue_type,  **kwargs):
    try:
        logger.debug("_createStoryEmailQueueItem called")
        story = kwargs["story"]
        logger.debug("Story %d" % story.id)

        if hasattr(story, "skip_mentions"):
            # logger.debug("skipping because skip_mentions=true")
            return

        project = story.project

        if project.personal:
            # logger.debug("Skipping because personal project")
            return

        if project.project_type == Project.PROJECT_TYPE_SCRUM:
            return
        
        if project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        if not limits.org_email_limit.increaseAllowed(organization=project.organization):            
            # logger.debug("Skipping because license doesn't support email")
            return  # Only subscribers...
            
        user = kwargs["user"]
        diffs = kwargs.get("diffs",None)
        if diffs is None:
            diffs = {}
        else:
            _checkDiffsForMention(diffs, story, user)

        diffs = pdiffs.translate_diffs(diffs, project)

        if len(diffs) > 1 and "rank" in diffs:            
            del diffs["rank"]

        if queue_type != "story_created" and len(diffs) == 0 and queue_type != "story_deleted":
            logger.debug("Skipping because no diffs")
            return 

        item = EmailNotificationQueue(project=project, story=story, event_type=queue_type, originator=user)
        item.text = render_to_string("email_notifications/emails/%s.html" % queue_type, {'user':user,'story':story, 'diffs':diffs, 'base_url':settings.BASE_URL} )
        if queue_type == "story_deleted":
            item.story = None # otherwise this item is cascade deleted!
        item.save()
    except:
        logger.error("Could not create email queue item")
        traceback.print_exc(file=sys.stdout)


def _createAttachmentEmailQueueItem(queue_type,  **kwargs):
    try:
        story = kwargs["story"]
        fileData = kwargs["fileData"]
        user = kwargs["user"]
        project = story.project

        if project.personal:
            return

        if project.project_type == Project.PROJECT_TYPE_SCRUM:
            return

        if project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        if not limits.org_email_limit.increaseAllowed(organization=project.organization):            
            # logger.debug("Skipping because license doesn't support email")
            return  # Only subscribers...
        
        item = EmailNotificationQueue(project=project, story=story, event_type=queue_type, originator=user)
        item.text = render_to_string("email_notifications/emails/%s.html" % queue_type, {'user':user,'story':story, 'base_url':settings.BASE_URL, 'fileData':fileData} )
        item.save()
    except:
        logger.error("Could not create email queue item")
        traceback.print_exc(file=sys.stdout)

    
def _createEpicEmailQueueItem(queue_type,  **kwargs):
    try:
        epic = kwargs["epic"]

        if epic.project.personal:
            return

        if epic.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        if not limits.org_email_limit.increaseAllowed(organization=epic.project.organization):            
            return # Only subscribers...

        user = kwargs["user"]
        diffs = kwargs.get("diffs",None)

        diffs = pdiffs.translate_epic_diffs(diffs, epic.project)

        item = EmailNotificationQueue(project=epic.project, epic=epic, event_type=queue_type )
        item.text = render_to_string("email_notifications/emails/%s.html" % queue_type, {'user':user,'epic':epic, 'diffs':diffs, 'base_url':settings.BASE_URL} )
        item.save()
    except:
        logger.error("Could not create email queue item")
        traceback.print_exc(file=sys.stdout)

def _createTaskEmailQueueItem(queue_type,  **kwargs):
    try:
        task = kwargs["task"]
        project = task.story.project

        if project.personal:
            return

        if project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        if not limits.org_email_limit.increaseAllowed(organization=project.organization):            
            return # Only subscribers...

        user = kwargs["user"]
        diffs = kwargs.get("diffs",None)


        item = EmailNotificationQueue(project=project, task=task, event_type=queue_type, originator=user)
        item.text = render_to_string("email_notifications/emails/%s.html" % queue_type, {'user':user,'task':task, 'base_url':settings.BASE_URL} )
        if queue_type == "task_deleted":
            item.task = None # otherwise this item is cascade deleted!
        item.save()
    except:
        logger.error("Could not create email queue item")
        traceback.print_exc(file=sys.stdout)

def _createNoteEmailQueueItem(queue_type,  **kwargs):
    try:
        note = kwargs["note"]

        if note.project.personal:
            return

        if note.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        if not limits.org_email_limit.increaseAllowed(organization=note.project.organization):            
            return # Only subscribers...

        user = kwargs["user"]
        diffs = kwargs.get("diffs",None)
        iteration = note.iteration
        
        _checkNoteDiffsForMention(diffs, note, user)

        diffs = pdiffs.translate_note_diffs(diffs, note.project)

        if queue_type == "note_edited" and len(diffs) == 0:
            logger.debug("Skipping because no diffs")
            return 

        url = '{}#/iteration/{}/notes/{}'.format(reverse('project_app', kwargs={'project_slug':project.slug}), iteration.id, note.id)

        item = EmailNotificationQueue(project=note.project, note=note, event_type=queue_type, originator=user)
        item.text = render_to_string("email_notifications/emails/%s.html" % queue_type, 
                {'user':user,'note':note, 'diffs':diffs, 'base_url':settings.BASE_URL, 'url':url} )
        item.save()
    except:
        logger.error("Could not create email queue item")
        traceback.print_exc(file=sys.stdout)


@receiver(signals.story_created, dispatch_uid="email_signal_hookup")
def onStoryCreated(sender, **kwargs):    
    _createStoryEmailQueueItem("story_created", **kwargs)


@receiver(signals.story_updated, dispatch_uid="email_signal_hookup")
def onStoryUpdated(sender, **kwargs):    
    diffs = kwargs.get("diffs",None)

    if "modified" in diffs:
        del diffs['modified']
        # of course the modified date is chaning, all the time.
    
    if len(diffs) == 0:
        return  # no differences.

    _createStoryEmailQueueItem("story_edited", **kwargs)


@receiver(signals.story_deleted,dispatch_uid="email_signal_hookup")
def onStoryDeleted(sender, **kwargs):
    _createStoryEmailQueueItem("story_deleted", **kwargs)         


@receiver(signals.attachment_added, dispatch_uid="email_signal_hookup")
def onAttachmentAdded(sender, **kwargs):
    _createAttachmentEmailQueueItem("attachment_added", **kwargs)


@receiver(models.signals.post_save, sender=StoryComment, dispatch_uid="email_signal_hookup")
def onCommentPosted(sender, **kwargs):
    t_comment = kwargs['instance']
    if hasattr(t_comment,"skip_announcements"):
        return

    try:
        story = t_comment.story
        if story.project.personal:
           return
        
        if story.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        if hasattr(story, "skip_mentions"):
            return

        if not limits.org_email_limit.increaseAllowed(organization=story.project.organization):
            # Only subscribers...
            return

        _checkFieldForMention("", t_comment.comment, story, t_comment.user)
        item = EmailNotificationQueue(project=story.iteration.project, event_type="story_comment", story=story, originator=t_comment.user )
        item.text = render_to_string("email_notifications/emails/story_comment.html", {'user':t_comment.user,
                                                                                       'story':story,
                                                                                       'item':t_comment,
                                                                                       'base_url':settings.BASE_URL} )
        item.save()
    except:
        logger.error("Could not create email queue item")
        traceback.print_exc(file=sys.stdout)


@receiver(models.signals.post_save, sender=NoteComment, dispatch_uid="email_signal_hookup")
def onNoteCommentPosted(sender, **kwargs):
    t_comment = kwargs['instance']
    if hasattr(t_comment,"skip_announcements"):
        return

    try:
        note = t_comment.note
        if note.project.personal:
           return

        if note.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        if not limits.org_email_limit.increaseAllowed(organization=note.project.organization):
            # Only subscribers...
            return

        _checkNoteFieldForMention("", t_comment.comment, note, t_comment.user)

        item = EmailNotificationQueue(project=note.project, note=note, event_type="note_comment", originator=t_comment.user)
        item.text = render_to_string("email_notifications/emails/note_comment.html", { 'user':t_comment.user,
                                                                                       'note':note,
                                                                                       'item':t_comment,
                                                                                       'base_url':settings.BASE_URL} )
        item.save()
    except:
        logger.error("Could not create email queue item")
        traceback.print_exc(file=sys.stdout)

@receiver(models.signals.post_save, sender=ChatMessage, dispatch_uid="email_signal_hookup")
def onChatMessage(sender, **kwargs):
    t_message = kwargs['instance']
    try:
        project = t_message.project
        if project.personal:
            return
        
        if project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        if not limits.org_email_limit.increaseAllowed(organization=project.organization):
            # Only subscribers...
            return
        _checkChatMessageForMention(t_message.message, project, t_message.author)
    except:
        pass

@receiver(signals.note_created, dispatch_uid="email_signal_hookup")
def onNoteCreated(sender, **kwargs):
    _createNoteEmailQueueItem('note_created', **kwargs)

@receiver(signals.note_updated, dispatch_uid="email_signal_hookup")
def onNoteUpdated(sender, **kwargs):
    _createNoteEmailQueueItem('note_edited', **kwargs)

@receiver(signals.epic_created, dispatch_uid="email_signal_hookup")
def onEpicCreated(sender, **kwargs):
    _createEpicEmailQueueItem('epic_created', **kwargs)


@receiver(signals.epic_updated, dispatch_uid="email_signal_hookup")
def onEpicChanged(sender, **kwargs):
    _createEpicEmailQueueItem('epic_edited', **kwargs)


@receiver(signals.epic_deleted, dispatch_uid="email_signal_hookup")
def onEpicDeleted(sender, **kwargs):
    _createEpicEmailQueueItem('epic_deleted', **kwargs)


@receiver(signals.task_created, dispatch_uid="email_signal_hookup")
def onTaskCreated(sender, **kwargs):
    _createTaskEmailQueueItem("task_created", **kwargs)


@receiver(signals.task_status_changed, dispatch_uid="email_signal_hookup")
def onTaskStatusChange(sender, **kwargs):
    _createTaskEmailQueueItem('task_status', **kwargs)    


@receiver(signals.task_updated, dispatch_uid="email_signal_hookup")
def onTaskUpdated(sender, **kwargs):
    _createTaskEmailQueueItem('task_edited', **kwargs)    


@receiver(signals.task_deleted, dispatch_uid="email_signal_hookup")
def onTaskDeleted(sender, **kwargs):
    _createTaskEmailQueueItem('task_deleted', **kwargs)    



