from django.db import models

from story import Story


class StoryAttributes( models.Model ):
    story = models.ForeignKey( Story, related_name="extra_attributes")
    context = models.CharField(max_length=6)
    key = models.CharField(max_length=4)
    value = models.CharField(max_length=10)

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_storyattributes"