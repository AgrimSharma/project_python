from django.db import models

#from task import Task
from storytag import StoryTag


class TaskTagging(models.Model):
    tag = models.ForeignKey(StoryTag, related_name="tasks")
    task = models.ForeignKey("projects.Task", related_name="task_tags")

    @property
    def name(self):
        return self.tag.name

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_tasktagging"
