# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.


from django.db import models

from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class FlowdockUser(models.Model):
    user = models.ForeignKey(User, related_name="+")
    flowdock_username = models.CharField(max_length=64, default="")
    oauth_token = models.CharField(max_length=64)
    project = models.ForeignKey("projects.Project", related_name="+")

    class Meta:
        app_label = 'flowdock'


class FlowdockMapping(models.Model):
    flow_slug = models.CharField(max_length=128)
    org_slug = models.CharField(max_length=128)
    source_id = models.IntegerField(default=0)
    project = models.ForeignKey("projects.Project")
    channel_name = models.CharField(max_length=128)
    channel_id = models.CharField(max_length=128)
    errors = models.IntegerField(default=0)
    api_token = models.CharField(max_length=128)
    card_moved = models.BooleanField(default=True)
    card_created = models.BooleanField(default=True)
    card_modified = models.BooleanField(default=True)
    comment_created = models.BooleanField(default=True)
    task_moved = models.BooleanField(default=True)
    task_created = models.BooleanField(default=True)
    task_modified = models.BooleanField(default=True)

    class Meta:
        app_label = 'flowdock'

