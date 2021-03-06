from django import template
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.utils.html import escape
from apps.activities.models import NewsItem
from apps.organizations.models import Organization
import apps.projects.access as access

import string

register = template.Library()

import logging

logger = logging.getLogger(__name__)

@register.inclusion_tag('activities/news_feed.html',takes_context=True)
def news_feed(context):
    cont = "project" in context
    user = context["user"]
    request = context["request"]
    if "project" in context and request.path[1:13] != "organization":
        project = context["project"]
        if access.has_read_access(project,user):
            news_items = NewsItem.objects.select_related('user').filter(project=project).order_by("-created")
        else:
            news_items = []
    else:
        organization = context["organization"]
        if organization.hasStaffAccess(user):
            # The user can see app projects in the org.
            news_items = NewsItem.objects.select_related('user').filter(project__organization=organization).order_by("-created")
            logger.debug("staff access news")
        else:
            # NOTE: We need to watch this query to make sure it performs ok.
            news_items = NewsItem.objects.select_related('user').filter(project__organization=organization, project__teams__members=user).distinct().order_by("-created")
            logger.debug("normal access news")


    return {'newsitems':news_items, "request":request}
    


def iteration_name(iteration):
    if iteration.name == "Backlog":
        return "Backlog"
    else:
        if iteration.name.startswith("Iteration") or iteration.name.startswith("Sprint"):
            return iteration.name
        else:
            return "Iteration %s" % iteration.name

def iteration_uri(iteration, project):
    return reverse("iteration", args=[project.slug, iteration.id])

def iteration_link(iteration, project):
    return ("<a href='%s'>" % iteration_uri(iteration, project)) + iteration_name(iteration) + "</a>"

def story_link(s, project):
    url = iteration_uri(s.iteration, project)
    summary = escape(smart_truncate(s.summary,length=40))
    return "<a title='%s' href='%s#story_%s'> %s-%d %s</a>" % (escape(s.summary),url, s.id, project.prefix, s.local_id, summary )


def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

@register.filter
def absolute_url(value):    
    return string.replace(value,'href="/','href="%s/' % settings.BASE_URL)

@register.filter
def subscription_checkbox(project , subscription_list):
    try:
        if project.id in subscription_list:
            return "<input type=\"checkbox\" name=\"subscriptions\" value=\"%d\" checked=\"checked\"> " % project.id
        else:
            return "<input type=\"checkbox\" name=\"subscriptions\" value=\"%d\"> " % project.id
    except:
        return ""

