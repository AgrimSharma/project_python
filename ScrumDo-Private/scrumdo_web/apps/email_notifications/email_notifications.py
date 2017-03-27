
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from apps.favorites.models import Favorite
from apps.email_notifications.models import *

from apps.organizations.models import Team

import traceback
import logging

CACHE_TIMEOUT = 60
logger = logging.getLogger(__name__)


class EmailNotifications:
    def __init__(self):
        pass

    def send(self):
        # First, collect up all the notifications we want to email people about.
        notification_list = self.collectNotifications()
        for user in notification_list:
            self.sendEmail(user, notification_list[user])

    def groupNotifications(self, notifications):
        """
            Returns notifications groups by either
              1. The story the notification was for
              2. All others
        """
        buckets = {}
        for notification in notifications:
            if notification.task is not None:
                storyId = notification.task.story_id
            elif notification.story is None:
                storyId = 'other'
            else:
                storyId = notification.story_id

            if storyId in buckets:
                buckets[storyId].append(notification)
            else:
                buckets[storyId] = [notification]
        return buckets

    def sendEmail(self, user, notifications):
        """Actually sends the email to the user based on a list of collected notifications. """
        try:
            logger.debug("Sending email to %s " % user.email)
            all_notifications = sorted(notifications,
                                       key=lambda notification: "%s %s %s" % (notification.project, notification.story, notification.epic) )
            notifications = [notification for notification in all_notifications if notification.originator != user]

            if len(notifications) == 0:
                logger.debug("only self-notifications for %s" % user.username)
                return

            notifications = self.groupNotifications(notifications)

            for storyId, storyNotifications in notifications.iteritems():
                if storyId == 'other':
                    story = None
                else:
                    story = Story.objects.get(id=storyId)

                body = render_to_string("email_notifications/emails/email_shell.html", {
                    'notifications': storyNotifications,
                    'story': story,
                    'base_url': settings.BASE_URL,
                    'static_url': settings.STATIC_URL})
                text_body = strip_tags(body)

                if story is not None:
                    replyTo = settings.STORY_EMAIL_ADDRESS % (story.id, story.project.slug)
                else:
                    replyTo = "noreply@scrumdo.com"

                if len(storyNotifications) == 1:
                    subject = self.generateSubject(storyNotifications[0])
                elif story is not None:
                    subject = "[ScrumDo] - Card %s-%d (%s)" % (story.project.prefix, story.local_id, story.project.name)
                else:
                    subject = "[ScrumDo] multiple updates"

                msg = EmailMultiAlternatives(subject,
                                             text_body,
                                             settings.AUTOMATED_EMAIL,
                                             [user.email],
                                             headers={'Reply-To': replyTo, 'format': 'flowed'})
                msg.attach_alternative(body, "text/html")
                msg.send()
        except:
            traceback.print_exc()
            logger.warn("Failed to send an email")

    def generateSubject(self, source_notification):
        titles = {
            "iteration_summary": lambda notification: "[ScrumDo] - Iteration summary %s (%s)" % (notification.iteration.name, notification.project.name),
            "story_status": lambda notification: "[ScrumDo] - Card %s-%d status changed (%s)" % (notification.story.project.prefix, notification.story.local_id, notification.project.name),
            "story_edited": lambda notification: "[ScrumDo] - Card %s-%d modified (%s)" % (notification.story.project.prefix, notification.story.local_id, notification.project.name),
            "story_created": lambda notification: "[ScrumDo] - Card %s-%d created (%s)" % (notification.story.project.prefix, notification.story.local_id, notification.project.name),
            "story_deleted": lambda notification: "[ScrumDo] - Card deleted (%s)" % (notification.project.name),
            "story_comment": lambda notification: "[ScrumDo] - New comment on card %s-%d (%s)" % (notification.story.project.prefix, notification.story.local_id, notification.project.name),
            "epic_created": lambda notification: "[ScrumDo] - Epic #%d created (%s)" % (notification.epic.local_id, notification.project.name),
            "epic_edited": lambda notification: "[ScrumDo] - Epic #%d modified (%s)" % (notification.epic.local_id, notification.project.name),
            "epic_story": lambda notification: "[ScrumDo] - Epic #%d modified (%s)" % (notification.epic.local_id, notification.project.name),
            "task_created": lambda notification: "[ScrumDo] - Task created (%s)" % (notification.project.name),
            "task_edited": lambda notification: "[ScrumDo] - Task modified (%s)" % (notification.project.name),
            "task_deleted": lambda notification: "[ScrumDo] - Task deleted (%s)" % (notification.project.name),
            "task_status": lambda notification: "[ScrumDo] - Task status (%s)" % (notification.project.name),
            "epic_deleted": lambda notification: "[ScrumDo] - Epic #%d deleted (%s)" % (notification.epic.local_id, notification.project.name),
            "note_created": lambda notification: "[ScrumDo] - Note Created (%s)" % (notification.project.name,),
            "note_edited": lambda notification: "[ScrumDo] - Note modified (%s)" % (notification.project.name,),
            "note_comment": lambda notification: "[ScrumDo] - New Comment on Note (%s)" % (notification.project.name,),
            "attachment_added": lambda notification: "[ScrumDo] - Card %s-%d attachment added (%s)" % (notification.story.project.prefix, notification.story.local_id, notification.project.name),
        }

        if source_notification.event_type in titles:
            return titles[source_notification.event_type](source_notification)

        return "[ScrumDo] Update"

    def collectNotifications(self):
        """Creates a mapping of notifications to users"""
        notification_list = {}
        for notification in EmailNotificationQueue.objects.all():
            try:
                users = self._usersForEvent(notification.event_type, notification.project, notification.story,
                                            notification.task, notification.epic, notification.note)

                for user in users:
                    if user == notification.originator:
                        continue  # you shouldn't get notifications for comments you post.

                    if user in notification_list:
                        # This user already had a notification
                        notification_list[user].append(notification)
                    else:
                        # This user hasn't had one yet
                        notification_list[user] = [notification]
            except:
                traceback.print_exc()
                logger.warn("Failed to collect notification")
            notification.delete()
        return notification_list

    def _getUserOptions(self, user):
        """Returns the EmailOptions object for a user, automatically creating it if it
           doesn't exist and caching results"""
        recs = EmailOptions.objects.filter(user=user)
        if len(recs) > 0:
            rec = recs[0]
        else:
            rec = EmailOptions(user=user)
            rec.save()

        return rec

    def _getUserSetting(self, user, event_type):
        """Returns the value of a given setting for a given user"""
        settings = self._getUserOptions(user)
        if event_type == 'attachment_added':
            event_type = 'story_edited'
        if event_type == 'note_created' or event_type == 'note_edited' or event_type == 'note_comment':
            event_type = 'project_events'

        return getattr(settings, event_type)

    def _getCandidates(self, project):
        teams = Team.objects.filter(projects=project)
        candidates = []
        for team in teams:
            for user in team.members.all():
                candidates.append(user)

        for team in Team.objects.filter(access_type="staff", organization=project.organization):
            for user in team.members.all():
                candidates.append(user)

        return candidates

    def _usersForProjectEvent(self, event_type, project, candidates=None):
        if not candidates:
            candidates = self._getCandidates(project)
        result = []
        for user in candidates:
            if user in result:
                continue  # already in our result from another team.

            setting = self._getUserSetting(user, event_type)
            if setting == 1:
                # only watched projects
                if Favorite.getFavorite(user, project):
                    result.append(user)
            elif setting == 2:
                result.append(user)
        return result

    def _usersForEpicEvent(self, event_type, project, epic):
        # Since there is no assignment in epics, this is the same list as the project list
        return self._usersForProjectEvent(event_type, project)

    def _usersForStoryEvent(self, event_type, project, story):
        candidates = self._getCandidates(project)
        result = self._usersForProjectEvent(event_type, project)
        # Plus the assigned story option...
        for user in candidates:
            if user in result:
                continue  # already in our result
            setting = self._getUserSetting(user, event_type)
            if setting == 3 and story:
                if user in story.assignees:
                     result.append(user)

        return result

    def _usersForTaskEvent(self, event_type, project, task):
        candidates = self._getCandidates(project)
        result = self._usersForProjectEvent(event_type, project)
        # Plus the assigned story option...
        for user in candidates:
            if user in result:
                continue  # already in our result
            setting = self._getUserSetting(user, event_type)
            if setting == 3 and task:
                if task.assignee == user:
                    result.append(user)

        return result

    def _usersForNoteEvent(self, event_type, project, note):
        return self._usersForProjectEvent(event_type, project)

    def _usersForEvent(self, event_type, project, story=None, task=None, epic=None, note=None):
        """Returns a list of users that should be notified for a given event."""
        story_events = ('scrumlog', 'iteration_scope', 'story_status', 'story_edited', 'story_created',
                        'story_deleted', 'story_comment', 'attachment_added')
        epic_events = ('epic_deleted', 'epic_created', 'epic_edited', 'epic_story')
        task_events = ('task_created', 'task_edited', 'task_deleted', 'task_status')
        note_events = ('note_created', 'note_edited', 'note_comment')
        if event_type in story_events:
            return self._usersForStoryEvent(event_type, project, story)
        if event_type in epic_events:
            return self._usersForEpicEvent(event_type, project, epic)
        if event_type in task_events:
            return self._usersForTaskEvent(event_type, project, task)
        if event_type in note_events:
            return self._usersForNoteEvent(event_type, project, note)
