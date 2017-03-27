from django.db import models


class SiteStats(models.Model):
    user_count = models.IntegerField()
    project_count = models.IntegerField()
    story_count = models.IntegerField()
    date = models.DateField(auto_now=True)

    def __unicode__(self):
        return "%s %d/%d/%d" % (self.date, self.project_count, self.story_count, self.user_count)

    class Meta:
        app_label = 'projects'