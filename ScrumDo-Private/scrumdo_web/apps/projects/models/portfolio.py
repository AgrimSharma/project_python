from django.db import models


class Portfolio(models.Model):
    """Represents a group of projects grouped into a portfolio of related work"""
    root = models.ForeignKey("projects.Project", related_name="+")
    organization = models.ForeignKey("organizations.Organization", related_name="portfolios")

    time_period = models.CharField(default="Portfolio Increment", max_length=32)

    risk_type_1 = models.CharField(default='Business', max_length=32)
    risk_type_2 = models.CharField(default='Financial', max_length=32)
    risk_type_3 = models.CharField(default='Technical', max_length=32)
    risk_type_4 = models.CharField(default='', max_length=32)
    risk_type_5 = models.CharField(default='', max_length=32)
    risk_type_6 = models.CharField(default='', max_length=32)
    risk_type_7 = models.CharField(default='', max_length=32)


class PortfolioLevel(models.Model):
    """Represents one of the levels within a portfolio (value stream, program, team, etc.)"""
    name = models.CharField(max_length=48, default="Team")
    portfolio = models.ForeignKey(Portfolio, related_name="levels")
    level_number = models.SmallIntegerField(default=0)
    icon = models.CharField(max_length=32, default="fa-users")
    time_period = models.CharField(default="Iteration", max_length=32)
    work_item_name = models.CharField(max_length=32, default="Card")

    class Meta:
        ordering = ["level_number"]





