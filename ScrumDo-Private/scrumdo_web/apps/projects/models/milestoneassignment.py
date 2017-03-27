from django.db import models
import model_utils


class MilestoneAssignment(models.Model):
    assigned_project = models.ForeignKey("projects.Project")
    milestone = models.ForeignKey("projects.Story")
    active = models.BooleanField(default=True)
    assigned_date = models.DateTimeField(auto_now_add=True)

    STATUS = model_utils.Choices(
        (0, 'Assigned'),
        (1, 'Scoped'),
        (2, 'Sized'),
        (3, 'Developing'),
        (4, 'Verification'),
        (5, 'Completed'))

    status = models.SmallIntegerField(default=0, choices=STATUS)

    cards_total = models.IntegerField(default=0)
    cards_completed = models.IntegerField(default=0)
    cards_in_progress = models.IntegerField(default=0)

    points_total = models.IntegerField(default=0)
    points_completed = models.IntegerField(default=0)
    points_in_progress = models.IntegerField(default=0)

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_milestone_assignment"
