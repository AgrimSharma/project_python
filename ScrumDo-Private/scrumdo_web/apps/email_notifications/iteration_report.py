# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from apps.activities.templatetags.activity_tags import absolute_url
from apps.favorites.models import *
from apps.email_notifications.models import *
from apps.activities.models import NewsItem
from apps.inbox.managers import create_iteration_end_item

import datetime
import logging
import sys
import traceback

logger = logging.getLogger(__name__)


class IterationReport:
    def __init__(self):
        pass

    def send(self):
        today = datetime.date.today()
        yesterday = today + datetime.timedelta(days=-1)
        for iteration in Iteration.objects.filter(end_date=yesterday):
            self.markOnTimeline(iteration)
            self.doIterationReport(iteration)

    def markOnTimeline(self, iteration):
        item = NewsItem(project=iteration.project, text="Iteration %s has ended." % iteration.name, icon='iteration_end')
        item.save()
        create_iteration_end_item(iteration)

    def doIterationReport(self, iteration):
        project = iteration.project
        for member in project.all_members():
            try:
                options = EmailOptions.objects.get(user=member)
                if options.iteration_summary == 0:
                    continue  # user doesn't want summaries
                if options.iteration_summary == 1:
                    # User wants summaries on watched projects.
                    if Favorite.getFavorite(member, project) is None:
                        continue  # user does not watch this project
                try:
                    self.iterationReport(member, iteration)
                except:
                    logger.error("Could not send iteration report to %s" % member)
                    traceback.print_exc(file=sys.stdout)
            except :
                pass # member does not want this report

    def iterationReport(self, user, iteration):
        template = loader.get_template('email_notifications/emails/iteration_report.html')

        stories = iteration.stories.all().order_by("cell__time_type", "cell__y", "cell__x")

        context = Context({"stories": stories, "user": user, "site_name": settings.SITE_NAME, "iteration": iteration, 'base_url':settings.BASE_URL, 'static_url':settings.STATIC_URL} )
        body = absolute_url(template.render(context))

        email_address = user.email

        subject, from_email, to = 'ScrumDo Iteration Report %s' % iteration, settings.AUTOMATED_EMAIL, email_address
        text_content = strip_tags(body)
        html_content = body
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to], headers={'format': 'flowed'})
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.debug("Sending iteration report to %s" % email_address)
