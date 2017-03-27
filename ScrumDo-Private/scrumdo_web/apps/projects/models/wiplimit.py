from django.db import models


class TeamIterationWIPLimit(models.Model):
    team = models.ForeignKey("projects.project")

    # This iteration can either be in the project, or it can be an increment
    # of a parent project
    iteration = models.ForeignKey("projects.iteration")

    featureLimit = models.PositiveSmallIntegerField(default=0)
    featurePointLimit = models.PositiveSmallIntegerField(default=0)
    cardLimit = models.PositiveSmallIntegerField(default=0)
    cardPointLimit = models.PositiveSmallIntegerField(default=0)


