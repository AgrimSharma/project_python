#http://justcramer.com/2008/08/23/logging-in-with-email-addresses-in-django/

from django.contrib.auth.backends import ModelBackend # default backend
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.db import transaction

class EmailOrUsernameModelBackend(object):
    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username
                      }
        else:
            kwargs = {'username': username}

        users = User.objects.filter(**kwargs)
        for user in users:
            User.objects.get(pk=user.id)
            if user.check_password(password):
                return user
            
        return None

    def get_user(self, user_id):
        try:
            with transaction.atomic():
                return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None