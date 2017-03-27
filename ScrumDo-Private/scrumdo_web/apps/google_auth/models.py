from django.contrib.auth.models import User
from django.db import models

class GoogleAuth(models.Model):
    user = models.ForeignKey(User)
    google_sub = models.CharField(max_length=64)
    google_email = models.CharField(max_length=255)
    openid_id = models.CharField(max_length=255, null=True, default=None)