# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.
from django.template import loader
from django import template
from django.conf import settings
from django.db import models
from apps.avatar.templatetags.avatar_tags import avatar_url
from apps.account.templatetags.account_tags import realname
import sys, traceback
import urllib
import logging

from apps.realtime.util import channelName

import random
import json

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def realtime_channel(project):
    return channelName(project)

@register.filter
def realtime_uuid(user):
    result = {
        'avatar':avatar_url(user, 48),
        'username': user.username,
        'realname': realname(user),
        'hidden': user.is_staff,
        'n':random.randint(0,5000)
    }


    return json.dumps(result)