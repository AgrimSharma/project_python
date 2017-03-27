from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import  User
from apps.projects.models import Story
import apps.projects.signals as projects_signals

import datetime
import logging

logger = logging.getLogger(__name__)

class ProjectEmailSubscription(models.Model):
    project = models.ForeignKey("projects.Project")
    user = models.ForeignKey(User,related_name="email_subscriptions")

    def __unicode__(self):
        return "Subscription: %s %s" % (self.user, self.project)

class NewsItem(models.Model):
    created = models.DateTimeField(_('created'), default=datetime.datetime.now)
    user = models.ForeignKey(User,related_name="newsItems", null=True, blank=True)
    project = models.ForeignKey("projects.Project", related_name="newsItems", null=True, blank=True)
    text = models.TextField()
    icon = models.CharField(max_length=24)
    feed_url = models.CharField(max_length=75, null=True, blank=True)
    related_story = models.ForeignKey(Story, null=True, blank=True, db_index=True)
    @staticmethod
    def purgeOld(days=180):
        today = datetime.date.today()
        mdiff = datetime.timedelta(days=-days)
        date_30days_Agoago = today + mdiff
        NewsItem.objects.filter(created__lte=date_30days_Agoago).delete()
    def save(self, *args, **kwargs):
        super(NewsItem, self).save(*args, **kwargs) # Call the "real" save() method.
        if self.project is not None:
            projects_signals.news_posted.send(sender=self, news_item=self)
    
    class Meta:
        ordering = ['-created']
        db_table = "v2_activities_newsitem"
