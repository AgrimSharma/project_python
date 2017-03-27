from django.db import models


class BoardAttributes(models.Model):
    project = models.ForeignKey("projects.Project", related_name="extra_attributes")
    context = models.CharField(max_length=6)
    key = models.CharField(max_length=4)
    value = models.TextField()

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_boardattributes"
