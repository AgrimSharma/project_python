from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from apps.emailconfirmation.models import EmailAddress
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import login, authenticate
import requests
import random
import json
from hashlib import sha256
import jwt
import logging

from apps.organizations.models import Team


logger = logging.getLogger(__name__)


def auth_callback(request):
    # http://local.scrumdo.com:8000/googleauth/oauth2callback?
    # state=883710662fed2e0a91e600513fdcb8ebdf985298&
    # code=4/wdnvioIJowaK4SkSlxAdLEqi7ZiUNmCOpdP8LjDqg3c.YtZMukBsjXAVJvIeHux6iLZ3BBFbmAI&
    # authuser=0&
    # num_sessions=2&
    # prompt=consent&
    # session_state=2c33aeac93d5e7797053fa26dd5d016029008997..3247
    if request.GET.get("error", None) is not None:
        return render_to_response("google_auth/auth_error.html", {'errorText': request.GET.get("error") }, context_instance=RequestContext(request))

    # logger.info(request.session.get("OAUTH_STATE"))

    payload = {
        'code': request.GET.get('code'),
        'client_id': settings.GOOGLE_OAUTH['CLIENT_ID'],
        'client_secret': settings.GOOGLE_OAUTH['CLIENT_SECRET'],
        'redirect_uri': settings.GOOGLE_OAUTH['REDIRECT_URI'],
        'grant_type': 'authorization_code'
    }
    r = requests.post("https://www.googleapis.com/oauth2/v3/token", data=payload)
    # POST /oauth2/v3/token HTTP/1.1
    # Host: www.googleapis.com
    # Content-Type: application/x-www-form-urlencoded
    #
    # code=4/P7q7W91a-oMsCeLvIaQm6bTrgtp7&
    # client_id=8819981768.apps.googleusercontent.com&
    # client_secret={client_secret}&
    # redirect_uri=https://oauth2-login-demo.appspot.com/code&
    # grant_type=authorization_code
    #
    # response:
    #     {
    #   "access_token":"1/fFAGRNJru1FTz70BzhT3Zg",
    #   "expires_in":3920,
    #   "token_type":"Bearer"
    # }

    response = json.loads(r.text)

    if "error" in response:
        return render_to_response("google_auth/auth_error.html", {'errorText': response['error_description']}, context_instance=RequestContext(request))

    access_token = response['access_token']

    # logger.info(response['id_token'])
    id_token = response['id_token']
    userinfo = jwt.decode(id_token, verify=False)

    user = authenticate(userinfo=userinfo, access_token=access_token)
    login(request, user)
    logger.debug(request.session)

    if 'success_url' in request.session:
        result = HttpResponseRedirect(request.session['success_url'])
        del request.session['success_url']
        return result

    if Team.objects.filter(members=user).count() == 0:
        # New users, who are in no teams, go to register.
        return HttpResponseRedirect(reverse('register'))
    else:
        # Existing users go through the classic picker flow
        return HttpResponseRedirect(reverse('classic_picker'))





def login_redirect(request):
    # https://accounts.google.com/o/oauth2/auth?
    #      client_id=424911365001.apps.googleusercontent.com&
    #      response_type=code&
    #      scope=openid%20email&
    #      redirect_uri=https://oa2cb.example.com/&
    #      state=security_token%3D138r5719ru3e1%26url%3Dhttps://oa2cb.example.com/myHome&
    #      login_hint=jsmith@example.com&
    #      openid.realm=example.com&
    #      hd=example.com
    state = sha256("%d%s" % (random.randint(0, 100000), settings.SECRET_KEY)).hexdigest()
    request.session['OAUTH_STATE'] = state

    if request.GET.get('next', None) is not None:
        request.session['success_url'] = request.GET.get('next')

    url = "https://accounts.google.com/o/oauth2/auth?" + \
          "client_id=%s&" % settings.GOOGLE_OAUTH['CLIENT_ID'] + \
          "response_type=code&" + \
          "scope=openid%20email%20profile&" + \
          "redirect_uri=%s&" % settings.GOOGLE_OAUTH['REDIRECT_URI'] + \
          "state=%s&" % state + \
          "openid.realm=%s&" % settings.GOOGLE_OAUTH['OPENID_REALM']

    return HttpResponseRedirect(url)
