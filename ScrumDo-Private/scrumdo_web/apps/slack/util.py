from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.conf import settings

import apps.html2text as html2text

SLACK_AUTH_URL = "https://slack.com/oauth/authorize"


def slack_redirect_url(projectSlug):
    return "%s/slack/auth_callback/%s" % (settings.SSL_BASE_URL, projectSlug)


def slack_auth_url(projectSlug):
    redirect_uri = slack_redirect_url(projectSlug)
    return "%s?client_id=%s&scope=identify,client&state=init&redirect_uri=%s" % \
           (SLACK_AUTH_URL, settings.SLACK_CLIENT_ID, redirect_uri)


def format_story_summary(story, short=False):
    summary = strip_tags(story)
    summary = html2text.html2text(summary)
    if short:
        summary = Truncator(summary).words(20, truncate=' ...')
    return format_slack_message(summary)


def format_slack_html(html, short=False):
    text = strip_tags(html)
    text = html2text.html2text(text)
    if short:
        text = Truncator(text).words(20, truncate=' ...')
    return format_slack_message(text)


def format_slack_message(message):
    message.replace("<", "&lt;")
    message.replace(">", "&gt;")
    message.replace("&", "&amp;")
    return message
