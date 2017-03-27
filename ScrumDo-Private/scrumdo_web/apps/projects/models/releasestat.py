from django.db import models


class ReleaseStat(models.Model):
    release = models.ForeignKey("projects.Story", related_name='stats')

    date = models.DateField()

    cards_total = models.IntegerField(default=0)
    cards_completed = models.IntegerField(default=0)
    cards_in_progress = models.IntegerField(default=0)

    points_total = models.IntegerField(default=0)
    points_completed = models.IntegerField(default=0)
    points_in_progress = models.IntegerField(default=0)

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_releasestat"