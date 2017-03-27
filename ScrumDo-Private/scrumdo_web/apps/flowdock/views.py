# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.shortcuts import get_object_or_404, render_to_response, RequestContext
from django.http import HttpResponseRedirect


from django.contrib.auth.decorators import login_required

import sys
import requests
import traceback
from apps.projects.models import *
from apps.projects.access import *

from apps.extras.models import *
from django.contrib import messages
from django.conf import settings

from apps.flowdock.models import FlowdockUser
from apps.flowdock.util import flowdock_redirect_url

import json

logger = logging.getLogger(__name__)

EXTRA_SLUG = "slack"

FLOWDOCK_TOKEN_URL = "https://api.flowdock.com/oauth/token"

def _redeemOauthCode(code, projectSlug):
    payload = {
        'client_id': settings.FLOWDOCK_CLIENT_ID,
        'client_secret': settings.FLOWDOCK_CLIENT_SECRET,
        'code': code,
        'redirect_uri': flowdock_redirect_url(projectSlug),
        'grant_type': 'authorization_code'
    }
    req = requests.post(FLOWDOCK_TOKEN_URL, data=payload).json()
    return req




@login_required
def auth_callback(request):
    project_slug = request.GET.get("state")
    project = get_object_or_404( Project, slug=project_slug )
    admin_access_or_403(project, request.user)

    try:
        code = request.GET.get("code")
        o = _redeemOauthCode(code, project_slug)
        access_token = o['access_token']
        refresh_token = o['refresh_token']
        expires_in = o['expires_in']

        result = requests.get("https://api.flowdock.com/user?access_token=%s" % access_token).json()

        username = result['name']
        try:
            flowdockUser = FlowdockUser.objects.get(project=project)
        except FlowdockUser.DoesNotExist:
            flowdockUser = FlowdockUser(project=project)

        flowdockUser.user = request.user
        flowdockUser.flowdock_username = username
        flowdockUser.oauth_token = access_token
        flowdockUser.refresh_token = refresh_token
        flowdockUser.save()

    except:
        traceback.print_exc(file=sys.stdout)
        #request.user.message_set.create(message='Something went wrong with the authentication.')
        messages.add_message(request, messages.INFO, 'Something went wrong with the authentication.')

    return HttpResponseRedirect( "%s#/settings/extras/flowdock" % reverse('project_app', kwargs={'project_slug':project_slug}) )
