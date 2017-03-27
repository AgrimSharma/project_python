from django import template
from apps.activities.models import NewsItem

register = template.Library()

import logging

logger = logging.getLogger(__name__)


@register.filter
def org_activity_count(org):
    return NewsItem.objects.filter(project__organization=org).count()

@register.filter
def last_activity(org):
    try:
        n = NewsItem.objects.filter(project__organization=org).order_by("-created")[0]
        return n.created
    except:
        return "never"

