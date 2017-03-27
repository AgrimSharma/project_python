from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from story import Story
from project import Project

import datetime

class StoryBlocker(models.Model):
    card = models.ForeignKey( Story, related_name="blocked_instances")
    reason = models.TextField()
    resolution = models.TextField()
    blocked_date = models.DateTimeField(_('blocked_date'), auto_now=False)
    unblocked_date = models.DateTimeField(_('unblocked_date'), auto_now=False, null=True)
    blocker = models.ForeignKey(User, related_name="blocked_stories", verbose_name=_('blocker'))
    unblocker = models.ForeignKey(User, related_name="unblocked_stories", verbose_name=_('unblocker'), null = True)
    project = models.ForeignKey( Project, related_name="blocked_reasons")
    resolved = models.BooleanField(default=False)
    external = models.BooleanField(default=False)
    
    @property
    def age(self):
        if self.unblocked_date:
            end = self.unblocked_date
        else:
            end = datetime.datetime.now()
        return round((end - self.blocked_date).total_seconds() / 60 / 60 / 24 )
    
    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_story_blocker"