from django.db import models
from django.contrib.auth.models import User

import logging

logger = logging.getLogger(__name__)


class ExtraUserInfo(models.Model):
    """We're going to keep a reference to a user's full name so we can do fast lookups on it."""
    user = models.ForeignKey(User)
    full_name = models.CharField(max_length=128, blank=True)

    class Meta:
        app_label = 'projects'

