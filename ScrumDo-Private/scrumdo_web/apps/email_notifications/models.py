# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from datetime import datetime, date
import time
import re

from django.conf import settings

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from apps.projects.models import *
import logging

logger = logging.getLogger(__name__)

class EmailNotificationQueue(models.Model):    
    project = models.ForeignKey(Project)
    iteration = models.ForeignKey(Iteration, null=True)
    story = models.ForeignKey(Story, null=True)
    task = models.ForeignKey(Task, null=True)
    epic = models.ForeignKey(Epic, null=True)
    note = models.ForeignKey(Note, null=True)
    text = models.TextField()
    event_type = models.CharField(max_length=32)
    originator = models.ForeignKey(User, null=True, default=None)

    class Meta:
        db_table = "v2_email_notifications_emailnotificationqueue"
        app_label = 'email_notifications'


class StoryMentions(models.Model):
    story = models.ForeignKey(Story)
    user = models.ForeignKey(User, related_name="mentioned_in_story")
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name="story_mentioned_users", default=None)

    class Meta:
        db_table = "v2_email_notifications_storymentions"
        app_label = 'email_notifications'
        
class ChatMentions(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User, related_name="mentioned_in_chat")
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    creator = models.ForeignKey(User, related_name="chat_mentioned_users", default=None)

    class Meta:
        db_table = "v2_email_notifications_chatmentions"
        app_label = 'email_notifications'

class NoteMentions(models.Model):
    note = models.ForeignKey(Note)
    user = models.ForeignKey(User, related_name="mentioned_in_note")
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name="note_mentioned_users", default=None)

    class Meta:
        db_table = "v2_email_notifications_notementions"
        app_label = 'email_notifications'


class EmailOptions( models.Model ):
    PROJECT_OPTION_CHOICES = [(0, "Never"), (1, "Watched Projects"), (2, "All Projects")]
    STORY_OPTION_CHOICES = [(0, "Never"), (1, "Watched Projects"), (2, "All Projects"), (3, 'Assigned To You')]
    MENTION_OPTIONS=[(0, "Never"), (2, "Always")]
    user = models.ForeignKey(User, verbose_name=_('user'))
    
    digest = models.PositiveSmallIntegerField(help_text="Daily digest of activity in projects", choices=PROJECT_OPTION_CHOICES, default=0)
    iteration_summary = models.PositiveSmallIntegerField(help_text="End of iteration report", choices=PROJECT_OPTION_CHOICES, default=0)
    iteration_scope = models.PositiveSmallIntegerField(help_text="Story added to current iteration", choices=PROJECT_OPTION_CHOICES, default=0)
    
    story_assigned = models.PositiveSmallIntegerField(help_text="A Story is (re)assigned", choices=STORY_OPTION_CHOICES, default=0)
    story_status = models.PositiveSmallIntegerField(help_text="A Story's status changes", choices=STORY_OPTION_CHOICES, default=0)
    story_edited = models.PositiveSmallIntegerField(help_text="A Story is edited", choices=STORY_OPTION_CHOICES, default=0)
    story_created = models.PositiveSmallIntegerField(help_text="A Story is created", choices=STORY_OPTION_CHOICES, default=0)
    story_deleted = models.PositiveSmallIntegerField(help_text="A Story is deleted", choices=STORY_OPTION_CHOICES, default=0)
    story_comment = models.PositiveSmallIntegerField(help_text="A Story is commented on", choices=STORY_OPTION_CHOICES, default=0)

    epic_created = models.PositiveSmallIntegerField(help_text="An Epic is created", choices=PROJECT_OPTION_CHOICES, default=0)
    epic_edited = models.PositiveSmallIntegerField(help_text="An Epic is edited", choices=PROJECT_OPTION_CHOICES, default=0)
    epic_deleted = models.PositiveSmallIntegerField(help_text="An Epic is deleted", choices=PROJECT_OPTION_CHOICES, default=0)

    task_created = models.PositiveSmallIntegerField(help_text="A Task is created", choices=STORY_OPTION_CHOICES, default=0)
    task_edited = models.PositiveSmallIntegerField(help_text="A Task is edited", choices=STORY_OPTION_CHOICES, default=0)
    task_deleted = models.PositiveSmallIntegerField(help_text="A Task is deleted", choices=STORY_OPTION_CHOICES, default=0)
    task_status = models.PositiveSmallIntegerField(help_text="A Task's status changes", choices=STORY_OPTION_CHOICES, default=0)

    mention = models.PositiveSmallIntegerField(help_text="You are explicitly mentioned by username", choices=MENTION_OPTIONS, default=2)
    
    scrumlog = models.PositiveSmallIntegerField(help_text="A scrum log is posted", choices=PROJECT_OPTION_CHOICES, default=0)

    project_events = models.PositiveSmallIntegerField(help_text="A Project Event", choices=PROJECT_OPTION_CHOICES, default=1)
    
    marketing = models.BooleanField(help_text="News and updates about ScrumDo", default=True)

    class Meta:
        app_label = 'email_notifications'
