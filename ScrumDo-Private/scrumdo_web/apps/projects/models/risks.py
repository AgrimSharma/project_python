from django.db import models


class Risk(models.Model):
    portfolio = models.ForeignKey("projects.portfolio")
    description = models.TextField(max_length=512)

    cards = models.ManyToManyField("projects.story", related_name='risks')
    iterations = models.ManyToManyField("projects.iteration", related_name='risks')
    projects = models.ManyToManyField("projects.project", related_name='risks')

    probability = models.PositiveSmallIntegerField(default=0)

    severity_1 = models.PositiveSmallIntegerField(default=0)
    severity_2 = models.PositiveSmallIntegerField(default=0)
    severity_3 = models.PositiveSmallIntegerField(default=0)
    severity_4 = models.PositiveSmallIntegerField(default=0)
    severity_5 = models.PositiveSmallIntegerField(default=0)
    severity_6 = models.PositiveSmallIntegerField(default=0)
    severity_7 = models.PositiveSmallIntegerField(default=0)

