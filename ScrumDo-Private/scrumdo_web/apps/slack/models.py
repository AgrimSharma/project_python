# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.


from django.db import models

from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class SlackUser(models.Model):
    user = models.ForeignKey(User, related_name="+")
    slack_username = models.CharField(max_length=64, default="")
    oauth_token = models.CharField(max_length=255)
    project = models.ForeignKey("projects.Project")

    class Meta:
        app_label = 'slack'


class SlackMapping(models.Model):
    """Mapping of scrumdo<->github organizations when using the organization level extra
       to keep authentication info in sync."""
    project = models.ForeignKey("projects.Project")
    channel_name = models.CharField(max_length=128)
    channel_id = models.CharField(max_length=16)
    errors = models.IntegerField(default=0)
    card_moved = models.BooleanField(default=True)
    card_created = models.BooleanField(default=True)
    card_modified = models.BooleanField(default=True)
    comment_created = models.BooleanField(default=True)
    task_moved = models.BooleanField(default=True)
    task_created = models.BooleanField(default=True)
    task_modified = models.BooleanField(default=True)

    class Meta:
        app_label = 'slack'

