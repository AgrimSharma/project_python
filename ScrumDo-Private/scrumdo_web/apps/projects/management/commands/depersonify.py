#!/usr/bin/env python

from apps.extras.models import ProjectExtraMapping, SyncronizationQueue
from apps.slack.models import SlackMapping
from apps.github_integration.models import GithubBinding, GithubCredentials, GithubOrganization, GithubUser
from apps.hipchat.models import HipChatMapping
from apps.flowdock.models import FlowdockMapping

from mailer.models import Message
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.DEBUG:
            logger.error("Can only run this on sites in debug mode (for safety!)")
            return

        confirm = raw_input("We're about to devestate this DB making it completely non-production worthy and destroy user data.  Type yes to continue.\n > ")
        if confirm != "yes":
            return

        logger.warn("Resetting user email addresses to %s and passwords to klug" % settings.CONTACT_EMAIL)
        User.objects.all().update(email=settings.CONTACT_EMAIL,
                                  password="sha1$d4f5f$2ccff0e66fe0090095add4d3e47343aa6b8009b7")
        logger.warn("Removing project<->extras mappings")
        # ExternalStoryMapping.objects.all().delete()
        # ExternalTaskMapping.objects.all().delete()
        ProjectExtraMapping.objects.all().delete()
        SyncronizationQueue.objects.all().delete()
        Message.objects.all().delete()
        SlackMapping.objects.all().delete()

        GithubBinding.objects.all().delete()
        GithubCredentials.objects.all().update(oauth_token='x')
        GithubOrganization.objects.all().update(oauth_token='x')
        GithubUser.objects.all().update(oauth_token='x')

        HipChatMapping.objects.all().delete()
        FlowdockMapping.objects.all().delete()

