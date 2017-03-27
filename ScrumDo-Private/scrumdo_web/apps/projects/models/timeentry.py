from django.db import models
from django.contrib.auth.models import User

import time

from apps.organizations.models import Organization

from iteration import Iteration
from story import Story
from task import Task


class TimeEntry(models.Model):
    user = models.ForeignKey(User, related_name="time_entries", verbose_name='user')
    organization = models.ForeignKey(Organization)
    project = models.ForeignKey("projects.Project", null=True)
    iteration = models.ForeignKey(Iteration, null=True)
    story = models.ForeignKey(Story, null=True, on_delete=models.SET_NULL, related_name="time_entries")
    task = models.ForeignKey(Task, null=True, on_delete=models.SET_NULL)
    minutes_spent = models.PositiveIntegerField()
    notes = models.TextField()
    date = models.DateField()

    def timestamp(self):
        return int((time.mktime(self.date.timetuple()) - time.timezone)*1000)

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_timeentry"