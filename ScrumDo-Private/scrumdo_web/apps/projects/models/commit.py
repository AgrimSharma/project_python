from django.db import models

from story import Story


class Commit(models.Model):
    story = models.ForeignKey(Story, related_name="commits")
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=24, default="")
    full_text = models.TextField()
    link = models.CharField(max_length=200)

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_commit"
        unique_together = ('story', 'link')
