from django.db import models
from django.contrib.auth.models import User

from apps.organizations.models import Organization

import os

def attachment_upload(self, filename):
    return 'generated/%s/%s/%d/%s' % (self.organization.slug, self.file_type, self.id, filename)

class FileJob(models.Model):
    attachment_file = models.FileField('attachment', upload_to=attachment_upload, null=True)
    organization = models.ForeignKey(Organization, related_name="generatedFiles")
    file_type = models.CharField(max_length=100)
    request_date = models.DateField(auto_now=True)
    owner = models.ForeignKey(User)
    completed = models.BooleanField(default=False)

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]

    class Meta:
        app_label = 'projects'
