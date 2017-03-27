from django.db import models
from django.contrib.auth.models import User

from apps.organizations.models import Organization


class OfflineJob(models.Model):
    organization = models.ForeignKey(Organization, related_name="offlineJobs")
    request_date = models.DateField(auto_now=True)
    owner = models.ForeignKey(User)
    completed = models.BooleanField(default=False)
    job_type = models.CharField(max_length=32)
    result = models.CharField(max_length=255, default='', blank=True, null=True)

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_offline_job"