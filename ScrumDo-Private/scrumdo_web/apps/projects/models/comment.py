from django.db import models
from django.contrib.auth.models import User


class StoryComment(models.Model):
    story = models.ForeignKey("projects.Story", related_name='comments')
    date_submitted = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, default=None)

    def __unicode__(self):
        return self.comment

    class Meta:
        ordering = ['-date_submitted']
        app_label = 'projects'
        db_table = "v2_projects_story_comment"

class NoteComment(models.Model):
    note = models.ForeignKey("projects.Note", related_name='comments')
    date_submitted = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, default=None)

    def __unicode__(self):
        return self.comment

    class Meta:
        ordering = ['-date_submitted']
        app_label = 'projects'
        db_table = "v2_projects_note_comment"
