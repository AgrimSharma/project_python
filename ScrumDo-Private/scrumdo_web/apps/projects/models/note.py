from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Note(models.Model):
    title = models.CharField(max_length=512)
    body = models.TextField()
    iteration = models.ForeignKey("projects.Iteration", related_name="notes", null=True, blank=True)
    project = models.ForeignKey("projects.Project", related_name="notes")
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="notes_created")
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    active = models.BooleanField( default=True)

    def __unicode__(self):
        return "%s" % ( self.title)
    
    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_note"