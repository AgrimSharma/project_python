from django.db import models

from release import Release

import time


class ReleaseLog(models.Model):
    release = models.ForeignKey(Release, related_name="points_log")
    date = models.DateTimeField()
    points_status1 = models.IntegerField(default=0)
    points_status2 = models.IntegerField(default=0)
    points_status3 = models.IntegerField(default=0)
    points_status4 = models.IntegerField(default=0)
    points_status5 = models.IntegerField(default=0)
    points_status6 = models.IntegerField(default=0)
    points_status7 = models.IntegerField(default=0)
    points_status8 = models.IntegerField(default=0)
    points_status9 = models.IntegerField(default=0)
    points_status10 = models.IntegerField(default=0)

    stories_status1 = models.IntegerField(default=0)
    stories_status2 = models.IntegerField(default=0)
    stories_status3 = models.IntegerField(default=0)
    stories_status4 = models.IntegerField(default=0)
    stories_status5 = models.IntegerField(default=0)
    stories_status6 = models.IntegerField(default=0)
    stories_status7 = models.IntegerField(default=0)
    stories_status8 = models.IntegerField(default=0)
    stories_status9 = models.IntegerField(default=0)
    stories_status10 = models.IntegerField(default=0)

    points_total = models.IntegerField()
    story_count = models.IntegerField()
    total_time_spent = models.IntegerField()
    time_estimated = models.IntegerField(default=0)  # total of time of stories estimated.
    time_estimated_completed = models.IntegerField(default=0)  # total of estimates from compelted stories

    def points_in_progress(self):
        return self.points_status2 + \
            self.points_status3 + \
            self.points_status4 + \
            self.points_status5 + \
            self.points_status6 + \
            self.points_status7 + \
            self.points_status8 + \
            self.points_status9

    def timestamp(self):
        return int((time.mktime(self.date.timetuple()) - time.timezone)*1000)

    class Meta:
        app_label = 'projects'