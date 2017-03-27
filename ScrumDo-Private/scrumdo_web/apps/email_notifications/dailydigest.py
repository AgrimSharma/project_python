from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from apps.organizations.models import Organization
from apps.projects.limits import org_email_limit
from apps.activities.models import NewsItem
from apps.favorites.models import *
from apps.projects.access import has_read_access
from apps.email_notifications.models import *

from django.template.loader import render_to_string

import datetime


import logging
import sys
import traceback

logger = logging.getLogger(__name__)


class DailyDigest:
    def __init__(self):
        pass

    def send(self):
        if settings.DEBUG:
            options = EmailOptions.objects.exclude(digest=0).exclude(user__email='').filter(user__username='mhughes')
        else:
            options = EmailOptions.objects.exclude(digest=0).exclude(user__email='')

        for option in options:
            user = option.user
            if option.digest == 1:
                projects = self.getWatchedProjects(user)
            else:
                projects = self.getProjects(user)

            if len(projects) > 0:
                try:
                    self.dailyDigest(user, projects)
                except:
                    logger.error("Could not send daily digest to %s" % user)
                    traceback.print_exc(file=sys.stdout)

    def getProjects(self, user):
        projects = []
        for organization in Organization.getOrganizationsForUser(user):
            if not org_email_limit.increaseAllowed(organization=organization):
                continue  # Not a subscriber
            for project in organization.projects.all():
                if has_read_access(project, user):
                    projects.append(project)
        return projects

    def getWatchedProjects(self, user):
        favorites = Favorite.objects.filter(favorite_type=1, user=user).exclude(project=None)
        # need to check access here in case they lost access since they watched.
        return [f.project for f in favorites if has_read_access(f.project, user)]

    def groupNotifications(self, notifications):
        """
            Returns notifications groups by either
              1. The story the notification was for
              2. All others
        """
        buckets = {}
        for notification in notifications:
            if notification.related_story is None:
                storyId = 'other'
            else:
                storyId = notification.related_story_id

            if storyId in buckets:
                buckets[storyId].append(notification)
            else:
                buckets[storyId] = [notification]
        return buckets

    def dailyDigest(self, user, projects):
        logger.debug("Sending daily digest to %s" % user)

        template = loader.get_template('activities/digest_header.html')
        context = Context({"user": user, "site_name": settings.SITE_NAME})
        body = template.render(context)
        domain = settings.BASE_URL

        email_address = user.email
        totalItems = 0

        for project in projects:
            if not project.active:
                continue
            today = datetime.date.today()
            mdiff = datetime.timedelta(hours=-24)
            daterange = today + mdiff
            news_items = NewsItem.objects.filter(project=project, created__gte=daterange).order_by("-created")
            totalItems += news_items.count()
            itemsByStory = self.groupNotifications(news_items)

            template = loader.get_template('activities/digest_project.html')
            context = Context({"project": project,
                               "news_items": news_items,
                               "domain": domain,
                               "static_url": settings.STATIC_URL,
                               'email_address': email_address,
                               "support_email": settings.CONTACT_EMAIL})

            body = "%s %s" % (body, template.render(context))

            for storyId, storyNotifications in itemsByStory.iteritems():
                if storyId == 'other':
                    story = None
                else:
                    story = Story.objects.get(id=storyId)

                body += render_to_string("activities/digest_story.html", {'notifications': storyNotifications,
                                                                          'story': story,
                                                                          "static_url": settings.STATIC_URL,
                                                                          'base_url': settings.BASE_URL,
                                                                          'static_url': settings.STATIC_URL})

        if totalItems == 0:
            # No longer sending empty digests
            return

        template = loader.get_template('activities/digest_footer.html')
        context = Context({"user": user,
                           "static_url": settings.STATIC_URL,
                           "domain": domain,
                           'email_address': email_address,
                           "support_email": settings.CONTACT_EMAIL})

        body = "%s %s" % (body, template.render(context))

        subject, from_email, to = 'ScrumDo Daily Digest', settings.AUTOMATED_EMAIL, email_address
        text_content = strip_tags(body)
        html_content = body
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to], headers={'format': 'flowed'})
        msg.attach_alternative(html_content, "text/html")
        msg.send()
