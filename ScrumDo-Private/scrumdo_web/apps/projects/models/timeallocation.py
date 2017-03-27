from django.db import models
from django.contrib.auth.models import User

from iteration import Iteration


class TimeAllocation(models.Model):
    project = models.ForeignKey("projects.Project")
    iteration = models.ForeignKey(Iteration, null=True)
    user = models.ForeignKey(User)
    minutes_allocated = models.IntegerField(default=0)

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_timeallocation"