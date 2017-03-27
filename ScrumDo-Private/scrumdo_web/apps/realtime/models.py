# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from datetime import datetime, date, timedelta
import time
import re
import string
from django.contrib.auth.models import User
from django.db import models
from apps.projects.models import Project
from apps.attachments.models import Attachment

import logging
logger = logging.getLogger(__name__)

def attachment_upload(self, filename):
    attachmentdir = "attachments"
    return '%s/chat/%s/%s/%s' % (
                   attachmentdir,
                   self.project.slug,
                   self.pk,
                   filename)

class ChatMessage( models.Model ):
    MESSAGE_TYPE_CHAT = 0
    MESSAGE_TYPE_FILE = 1
    MESSAGE_TYPE_SYSTEM = 2
    author = models.ForeignKey(User, null=True, blank=True)
    project = models.ForeignKey(Project)
    timestamp = models.DateTimeField( auto_now=True )
    message = models.TextField()
    message_type = models.PositiveSmallIntegerField(default=0)



    attachment_file = models.FileField('attachment', upload_to=attachment_upload, null=True)

    class Meta:
        db_table = "v2_realtime_chatmessage"

    
