# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models


class UnsubscribeRequest(models.Model):
    email = models.CharField(max_length=100)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    ip = models.GenericIPAddressField()
    reason = models.TextField()


class AddressPulled(models.Model):
    """ We'll track every time we pull an email address. """
    email = models.CharField(max_length=100)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    newsletter = models.CharField(max_length=100)
    user = models.ForeignKey(User, null=True, blank=True, default=None)


class NewsletterSent(models.Model):
    """ We'll track every time we send a mass mailing. """
    email = models.CharField(max_length=100)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    newsletter = models.CharField(max_length=100)