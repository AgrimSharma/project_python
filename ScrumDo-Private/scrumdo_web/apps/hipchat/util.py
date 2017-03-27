from django.utils.html import strip_tags
from urllib2 import quote
from django.utils.text import Truncator
from django.conf import settings


FLOWDOCK_AUTH_URL = "https://www.flowdock.com/oauth/authorize"


def flowdock_redirect_url(projectSlug):
    return "%s/flowdock/auth_callback" % (settings.SSL_BASE_URL,)


def flowdock_auth_url(projectSlug):
    redirect_uri = flowdock_redirect_url(projectSlug)
    return "%s?client_id=%s&scope=integration flow profile&redirect_uri=%s&response_type=code&state=%s" % \
           (FLOWDOCK_AUTH_URL, settings.FLOWDOCK_CLIENT_ID, redirect_uri, projectSlug)


def format_story_summary(story, short=False):
    summary = strip_tags(story)
    if short:
        summary = Truncator(summary).words(20, truncate=' ...')
    return format_flowdock_message(summary)


def format_flowdock_html(html):
    text = strip_tags(html)
    return format_flowdock_message(text)


def format_flowdock_message(message):
    message.replace("<", "&lt;")
    message.replace(">", "&gt;")
    message.replace("&", "&amp;")
    return message
