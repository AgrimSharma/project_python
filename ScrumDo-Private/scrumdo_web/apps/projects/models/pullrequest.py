from django.db import models
from model_utils import Choices

from story import Story


class PullRequest(models.Model):
    STATUS = Choices((0, 'open', 'Open'), (1, 'closed', 'Closed'))
    state = models.IntegerField(choices=STATUS, default=STATUS.open)
    stories = models.ManyToManyField(Story, related_name="pull_requests")
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64, default="")
    full_text = models.TextField()
    link = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_pull_request"


