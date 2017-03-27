from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class PointScale(models.Model):
    project = models.ForeignKey("projects.Project", related_name="pointscale")
    value = models.TextField(_('value'), blank=True, null=True, default="")
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="pointscale_created")
    
    def __unicode__(self):
        return "%s" % ( self.value)
    
    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_pointscale"