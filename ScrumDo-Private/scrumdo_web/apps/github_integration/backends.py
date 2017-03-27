# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

import slumber
import sys, traceback
from django.contrib.auth.models import User
from apps.github_integration.models import *
from apps.emailconfirmation.models import EmailAddress
from django.core.mail import mail_admins
from django.db import transaction

class GithubBackend:
    @transaction.atomic
    def authenticate(self, access_token=None, **kwargs):
        if access_token is None:
            return None

        try:
            api = slumber.API("https://api.github.com", append_slash=False)
            user_info = api.user.get(access_token=access_token)
            emails = api.user.emails.get(access_token=access_token)
            github_username = user_info['login']
    
            try:
                with transaction.atomic():
                    gh_user = GithubUser.objects.get(github_username=github_username)
                    gh_user.oauth_token = access_token
                    gh_user.save()
                    user = gh_user.user
                    self.setDetails(user, user_info, emails)
                    return gh_user.user
            except GithubUser.DoesNotExist:
                logger.debug("GH User not found, creating new one.")


            try:
                username = github_username
                with transaction.atomic():
                    User.objects.get(username__iexact=username)
                    c = 1
                    while True:
                        username ="%s.%d" % (github_username, c)
                        User.objects.get(username__iexact=username)
                        c+=1
            except User.DoesNotExist:

                pass # Found a username not used yet!
                            
            user = User(username=username, is_active=True)

            self.setDetails(user, user_info, emails)


            gh_user = GithubUser(github_username=github_username, user=user, oauth_token=access_token)
            gh_user.save()
            return user
    
        except:
            return None

    def setDetails(self, user, user_info, emails):
            # Attempt to get first/last name
            try:
                names = user_info["name"].split(" ")
                if len(names) == 2:
                    user.first_name = names[0] if user.first_name == "" else user.first_name
                    user.last_name = names[1] if user.last_name == "" else user.last_name
            except:
                # No big deal...
                # logger.debug("Could not snag users' name")
                pass

            if user.email == "":
                for email in emails:
                    if email['primary']:
                        user.email = email['email']
                        user.save()
                        # saving user to db before creatng entry for emailaddress model
                        try:
                            with transaction.atomic():
                                add = EmailAddress(verified=True, user=user, email=email['email'], primary=email['primary'])
                                add.save()
                        except:
                            pass


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None