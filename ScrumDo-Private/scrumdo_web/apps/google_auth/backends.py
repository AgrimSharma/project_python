# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

import slumber
import sys, traceback
from django.contrib.auth.models import User

from apps.django_openid.models import UserOpenidAssociation

from apps.emailconfirmation.models import EmailAddress
from django.core.mail import mail_admins

from models import *


import logging

logger = logging.getLogger(__name__)


class GoogleBackend:
    def authenticate(self, userinfo=None, access_token=None):
        try:
            if userinfo is None:
                return None

            googleid = userinfo['sub']

            try:
                # First, lets try to get an oauth user
                auth = GoogleAuth.objects.get(google_sub=googleid)
                user = auth.user
                return user
            except:
                logger.debug("No google auth user")


            try:
                # Next, let's try to migrate a google openid user
                openid = userinfo['openid_id']
                association = UserOpenidAssociation.objects.get(openid=openid)
                user = association.user

                # Create the auth object for next time
                auth = GoogleAuth(google_sub=googleid, user=user, google_email=userinfo['email'], openid_id=openid)
                auth.save()

                return user
            except Exception as e:
                # traceback.print_exc(file=sys.stdout)
                logger.debug("No google openid user")


            # Finally, we're to the point where this is most likely a brand new user logging in.
            # Two cases...
            #   1. A user accepting an invitation
            #   2. A user signing up for a new organization
            email = userinfo['email']

            user = User(email=email, username=self.get_username(email))
            user.save()

            address = EmailAddress(user=user, email=email, verified=True, primary=True)
            address.save()

            # Create the auth object for next time
            auth = GoogleAuth(google_sub=googleid, user=user, google_email=userinfo['email'])
            auth.save()

            return user
        except:
            mail_admins("ScrumDo Google Login Error", traceback.format_exc(), fail_silently=True)
            return None

    def get_username_num(self, username, num):
        if num > 99:
            return username

        u = "%s.%d" % (username[0:28], num)
        try:
            User.objects.get(username=u)
            return self.get_username_num(username, num+1)
        except User.DoesNotExist:
            return u

    def get_username(self, username):
        username = username[0:30]
        try:
            User.objects.get(username=username)
            return self.get_username_num(username, 1)
        except User.DoesNotExist:
            return username

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None