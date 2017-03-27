from django.db import models


class StoryTagging(models.Model):
    tag = models.ForeignKey("projects.StoryTag", related_name="stories")
    story = models.ForeignKey("projects.Story", related_name="story_tags")

    @property
    def name(self):
        return self.tag.name

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_storytagging"
