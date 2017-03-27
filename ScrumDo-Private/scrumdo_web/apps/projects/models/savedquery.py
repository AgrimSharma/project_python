from django.db import models
from django.contrib.auth.models import User


class SavedQuery(models.Model):
    creator = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    query = models.CharField(max_length=255)

    class Meta:
        app_label = 'projects'
