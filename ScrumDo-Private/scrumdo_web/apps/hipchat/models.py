# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.


from django.db import models

from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class HipChatMapping(models.Model):
    name = models.CharField(max_length=128)
    token = models.CharField(max_length=128)
    url = models.CharField(max_length=256)
    project = models.ForeignKey("projects.Project")
    errors = models.IntegerField(default=0)
    card_moved = models.BooleanField(default=True)
    card_created = models.BooleanField(default=True)
    card_modified = models.BooleanField(default=True)
    comment_created = models.BooleanField(default=True)
    task_moved = models.BooleanField(default=True)
    task_created = models.BooleanField(default=True)
    task_modified = models.BooleanField(default=True)

    class Meta:
        app_label = 'hipchat'


