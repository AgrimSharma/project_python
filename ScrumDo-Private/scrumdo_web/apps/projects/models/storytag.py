from django.db import models


class StoryTag(models.Model):
    project = models.ForeignKey("projects.Project", related_name="tags")
    name = models.CharField('name', max_length=32)

    def __unicode__(self):
        return "[%s] %s" % ( self.project.name, self.name)

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_storytag"
