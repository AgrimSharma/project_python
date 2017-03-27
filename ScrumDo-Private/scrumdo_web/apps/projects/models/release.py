from django.db import models

from apps.organizations.models import Organization

from project import Project
from story import Story
from epic import Epic


class Release(models.Model):
    name = models.CharField(max_length=128)
    start_date = models.DateField(help_text="Date that work on this release is planned to start.")
    delivery_date = models.DateField(help_text="Date that this release is expected to be delivered/completed.")
    organization = models.ForeignKey(Organization, related_name="releases")
    projects = models.ManyToManyField(Project, related_name="releases")
    stories = models.ManyToManyField(Story, related_name="releases")
    epics = models.ManyToManyField(Epic, related_name="releases")
    shared = models.BooleanField(default=False, help_text="Should a public page about this release be created?")
    key = models.CharField(max_length=32)
    calculating = models.BooleanField(default=False)
    order = models.IntegerField(default=1)

    class Meta:
        app_label = 'projects'
