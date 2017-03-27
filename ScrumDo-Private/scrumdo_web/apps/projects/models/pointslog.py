from django.db import models
import time


class PointsLog(models.Model):
    date = models.DateField()
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

    time_estimated = models.IntegerField(default=0)  # total of time of stories estimated.
    time_estimated_completed = models.IntegerField(default=0)  # total of estimates from compelted stories

    points_total = models.IntegerField()

    # content_type = models.ForeignKey(ContentType)
    # object_id = models.PositiveIntegerField()
    # related_object = generic.GenericForeignKey('content_type', 'object_id')
    iteration = models.ForeignKey("projects.Iteration", null=True, related_name='points_log')
    project = models.ForeignKey("projects.Project", null=True, related_name='points_log')


    def timestamp(self):
        return int((time.mktime(self.date.timetuple()) - time.timezone)*1000)

    class Meta:
        ordering = ["date"]
        app_label = 'projects'
        db_table = "v2_projects_pointslog"