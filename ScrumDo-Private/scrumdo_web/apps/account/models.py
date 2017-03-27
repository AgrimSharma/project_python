import sys
from uuid import uuid4
from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.db.models.signals import post_save
from django.utils.translation import get_language_from_request, ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

import traceback
import logging

logger = logging.getLogger(__name__)

from apps.emailconfirmation.models import EmailAddress, EmailConfirmation

# from timezones.fields import TimeZoneField

from apps.emailconfirmation.signals import email_confirmed

from apps.projects.templatetags.projects_tags import probable_email

class Account(models.Model):
    CLASSIC_MODE_NONE = 0
    CLASSIC_FORCE_CLASSIC = 1
    CLASSIC_FORCE_NEW = 2

    user = models.OneToOneField(User, verbose_name=_('user'), related_name="account")
    # user = models.ForeignKey(User, unique=True, verbose_name=_('user'), related_name="account")

    timezone = models.CharField(_('timezone'), max_length=100, default="US/Eastern")
    language = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    approved = models.BooleanField(default=True)

    classic_mode = models.SmallIntegerField(default=0)
    
    def email(self):
        return probable_email(self.user)

    def __unicode__(self):
        return self.user.username


class OtherServiceInfo(models.Model):

    # eg blogrss, twitter_user, twitter_password

    user = models.ForeignKey(User, verbose_name=_('user'))
    key = models.CharField(_('Other Service Info Key'), max_length=50)
    value = models.TextField(_('Other Service Info Value'))

    class Meta:
        unique_together = [('user', 'key')]

    def __unicode__(self):
        return u"%s for %s" % (self.key, self.user)

def other_service(user, key, default_value=""):
    """
    retrieve the other service info for given key for the given user.

    return default_value ("") if no value.
    """
    try:
        value = OtherServiceInfo.objects.get(user=user, key=key).value
    except OtherServiceInfo.DoesNotExist:
        value = default_value
    return value

def update_other_services(user, **kwargs):
    """
    update the other service info for the given user using the given keyword args.

    e.g. update_other_services(user, twitter_user=..., twitter_password=...)
    """
    for key, value in kwargs.items():
        info, created = OtherServiceInfo.objects.get_or_create(user=user, key=key)
        info.value = value
        info.save()

def create_account(sender, instance=None, **kwargs):
    if instance is None:
        return
    account, created = Account.objects.get_or_create(user=instance)


post_save.connect(create_account, sender=User)


# @@@ move to emailconfirmation app?
def superuser_email_address(sender, instance=None, **kwargs):
    if instance is None:
        return
    # only run when we are in syncdb or createsuperuser to be as unobstrusive
    # as possible and reduce the risk of running at inappropriate times
    if "syncdb" in sys.argv or "createsuperuser" in sys.argv:
        defaults = {
            "user": instance,
            "verified": True,
            "primary": True,
        }
        EmailAddress.objects.get_or_create(email=instance.email, **defaults)

post_save.connect(superuser_email_address, sender=User)


class AnonymousAccount(object):
    def __init__(self, request=None):
        self.user = AnonymousUser()
        self.timezone = settings.TIME_ZONE
        if request is not None:
            self.language = get_language_from_request(request)
        else:
            self.language = settings.LANGUAGE_CODE

    def __unicode__(self):
        return "AnonymousAccount"


class PasswordReset(models.Model):

    user = models.ForeignKey(User, verbose_name=_('user'))

    temp_key = models.CharField(_('temp_key'), max_length=100)
    timestamp = models.DateTimeField(_('timestamp'), default=datetime.now)
    reset = models.BooleanField(_('reset yet?'), default=False)

    def __unicode__(self):
        return "%s (key=%s, reset=%r)" % (self.user.username, self.temp_key, self.reset)


class RegistrationKey(models.Model):
    """ User Registration confirmation key
    """
    email = models.EmailField(max_length=254)
    key = models.CharField(max_length=32, null=True, blank=True)
    is_used = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s-%s" % (self.email, self.key)

    def save(self, *args, **kwargs):
        if not self.id:
            self.key = self._generate_key()
        return super(RegistrationKey, self).save(*args, **kwargs)

    def _generate_key(self):
        return uuid4().hex

    def send_registration_email(self):
        try:
            logger.debug("Sending Registration email to %s " % self.email)

            domain =  settings.BASE_URL if settings.DEBUG else settings.SSL_BASE_URL
            context = {
                "confirmation_key": self.key,
                "domain": domain,
                'STATIC_URL': settings.STATIC_URL
            }
            subject = _("[ScrumDo] Signup Verification.")
            html_content = render_to_string("account/register_confirmation_link.html" , context)
            text_body = render_to_string("account/register_confirmation_link.txt", context)
            msg = EmailMultiAlternatives(subject,
                                        text_body,
                                        "ScrumDo Robot <support@scrumdo.com>",
                                        [self.email],
                                        headers={'format': 'flowed'})
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except:
            traceback.print_exc()
            logger.warn("Failed to send an email")


def mark_user_active(sender, instance=None, **kwargs):
    user = kwargs.get("email_address").user
    user.is_active = True
    user.save()

email_confirmed.connect(mark_user_active, sender=EmailConfirmation)
