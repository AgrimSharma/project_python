# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

import sys
import urllib2
import requests
import traceback
from apps.projects.models import *
from apps.projects.access import *

from apps.extras.models import *
from django.contrib import messages
from django.conf import settings

from apps.slack.models import SlackUser
from apps.slack.util import slack_redirect_url

import json

logger = logging.getLogger(__name__)

EXTRA_SLUG = "slack"

SLACK_TOKEN_URL = "https://slack.com/api/oauth.access"

def _redeemOauthCode(code, projectSlug):
    redirect_uri = slack_redirect_url(projectSlug)
    url = "%s?client_id=%s&client_secret=%s&code=%s&redirect_uri=%s" % (SLACK_TOKEN_URL,
                                                        settings.SLACK_CLIENT_ID,
                                                        settings.SLACK_CLIENT_SECRET,
                                                        code,
                                                        redirect_uri)
    req = urllib2.Request(url)
    # req.get_method = lambda: 'POST'
    result = urllib2.urlopen(req).read()
    return json.loads(result)



@login_required
def auth_callback(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    admin_access_or_403(project, request.user)

    try:
        code = request.GET.get("code")
        o = _redeemOauthCode(code, project_slug)

        access_token = o['access_token']
        result = requests.get("https://slack.com/api/auth.test?token=%s" % access_token).json()

        username = result['user']
        try:
            slackUser = SlackUser.objects.get(project=project)
        except SlackUser.DoesNotExist:
            slackUser = SlackUser(project=project)

        slackUser.user = request.user
        slackUser.slack_username = username
        slackUser.oauth_token = access_token
        slackUser.save()


        # api = slumber.API("https://slack.com/api", append_slash=False)
        # user_info = api['auth.test'].get(token=access_token)
        #
        # if "name" in user_info:
        #     github_name = user_info['name']
        # else:
        #     github_name = user_info['login']
        #
        # github_username = user_info['login']
        #
        # # let's cheat and grab the person's full name if github knows it and we don't!
        # if request.user.first_name == '' and request.user.last_name == '':
        #     try:
        #         names = github_name.split(" ")
        #         if len(names) == 2:
        #             request.user.first_name = names[0]
        #             request.user.last_name = names[1]
        #             request.user.save()
        #     except:
        #         logger.debug("Could not snag users' name")
        #
        # try:
        #     c = GithubCredentials.objects.get(project=project)
        #     c.oauth_token = access_token
        #     c.github_username = github_username
        #     c.save()
        # except GithubCredentials.DoesNotExist:
        #     c = GithubCredentials(project=project, user=request.user, oauth_token=access_token, failure_count=0, github_username=github_username)
        #     c.save()
        # ProjectExtraMapping.objects.get_or_create(project=project, extra_slug='github')


    except:
        # traceback.print_exc(file=sys.stdout)
        #request.user.message_set.create(message='Something went wrong with the authentication.')
        messages.add_message(request, messages.INFO, 'Something went wrong with the authentication.')

    return HttpResponseRedirect( "%s#/settings/extras/slack" % reverse('project_app', kwargs={'project_slug':project_slug}) )
