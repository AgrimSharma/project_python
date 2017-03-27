from django.db import models


class ProjectShare(models.Model):
    project = models.ForeignKey("projects.Project")
    iteration = models.ForeignKey("projects.Iteration")
    enabled = models.BooleanField(default=False)
    all_cards = models.BooleanField(default=False)
    tag = models.CharField(default='public', max_length=64)
    key = models.CharField(max_length=16)
    assignee = models.BooleanField( default=True )
    summary = models.BooleanField( default=True )
    detail = models.BooleanField( default=True )
    custom1 = models.BooleanField( default=True )
    custom2 = models.BooleanField( default=True )
    custom3 = models.BooleanField( default=True )
    time_estimates = models.BooleanField( default=True )
    points = models.BooleanField( default=True )
    epic = models.BooleanField( default=True )
    business_value = models.BooleanField( default=True )
    comments = models.BooleanField( default=True )
    tasks = models.BooleanField( default=True )
    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_project_share"
