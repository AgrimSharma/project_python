from django.db import models
from django.contrib.auth.models import User
from model_utils import Choices


class InboxGroup(models.Model):
    """ let's explictly store information on groups of entries to make retrieval by page fast and easy.

        The Date will be determined by the organization's time zone (entry date/times in UTC)
    """
    organization = models.ForeignKey("organizations.organization")
    project = models.ForeignKey("projects.project", null=True)
    story = models.ForeignKey("projects.story", null=True)
    epic = models.ForeignKey("projects.epic", null=True)
    note = models.ForeignKey("projects.note", null=True)
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User)


class InboxEntry(models.Model):
    """Each entry within a group"""
    INBOX_STATUSES = Choices((0, 'unread', 'Unread'), (1, 'read', 'Read'), (2, 'archived', 'Archived'))
    group = models.ForeignKey(InboxGroup, related_name='entries')
    created = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=INBOX_STATUSES, default=INBOX_STATUSES.unread)
    subject = models.CharField(max_length=256)
    body = models.TextField()
