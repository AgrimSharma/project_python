from django import template
from track_me.models import *
from django.db.models.loading import get_model

register = template.Library()
import datetime

@register.filter(name="dayssince")
def dayssince(value):
    if not value:
        return ""
    today = datetime.date.today()
    diff  = today - value.date()
    return diff.days

