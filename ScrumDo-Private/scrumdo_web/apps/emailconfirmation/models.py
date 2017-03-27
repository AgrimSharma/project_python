from datetime import datetime, timedelta
from random import random

from django.conf import settings
from django.db import models, IntegrityError
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from apps.emailconfirmation.signals import email_confirmed

import sys, traceback
import hashlib

import logging

logger = logging.getLogger(__name__)

# this code based in-part on django-registration

class EmailAddressManager(models.Manager):

    def add_email(self, user, email, autoConfirm = False):
        try:
            email_address = self.create(user=user, email=email)
            if autoConfirm is True:
                email_address.verified = True
                email_address.primary = True
                email_address.save()
            else:
                EmailConfirmation.objects.send_confirmation(email_address)
            return email_address
        except IntegrityError:
            return None

    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except EmailAddress.DoesNotExist:
            return None

    def get_users_for(self, email):
        """
        returns a list of users with the given email.
        """
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in EmailAddress.objects.filter(
            verified=True, email=email)]

class EmailAddress(models.Model):

    user = models.ForeignKey(User)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    primary = models.BooleanField(default=False)

    objects = EmailAddressManager()

    def set_as_primary(self, conditional=False):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        self.user.email = self.email
        self.user.save()
        return True

    def __unicode__(self):
        return u"%s (%s)" % (self.email, self.user)

    class Meta:
        verbose_name = _("e-mail address")
        verbose_name_plural = _("e-mail addresses")
        unique_together = (
            ("user", "email"),
        )


class EmailConfirmationManager(models.Manager):

    def confirm_email(self, confirmation_key):
        try:
            confirmation = self.get(confirmation_key=confirmation_key)
        except self.model.DoesNotExist:
            return None
        if not confirmation.key_expired():
            email_address = confirmation.email_address
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()
            email_confirmed.send(sender=self.model, email_address=email_address)
            return email_address

    def send_confirmation(self, email_address):
        salt = hashlib.sha1(str(random())).hexdigest()[:5]
        confirmation_key = hashlib.sha1(salt + email_address.email).hexdigest()
        current_site = Site.objects.get_current()
        # check for the url with the dotted view path
        try:
            path = reverse("apps.emailconfirmation.views.confirm_email",
                args=[confirmation_key])
        except NoReverseMatch:
            # or get path with named urlconf instead
            path = reverse(
                "apps.emailconfirmation_confirm_email", args=[confirmation_key])
        activate_url = u"%s%s" % (settings.SSL_BASE_URL, path)
        context = {
            "user": email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "confirmation_key": confirmation_key,
            "base_url" : settings.BASE_URL,
            'STATIC_URL': settings.STATIC_URL
        }

        try:
            logger.debug("Sending confirmation email to %s " % email_address.email)

            body = render_to_string("emailconfirmation/email_confirmation_message.html" , context )
            text_body = render_to_string("emailconfirmation/email_confirmation_message.txt", context)
        
            subject = "[ScrumDo] Verify Email Address"
        
            msg = EmailMultiAlternatives(subject,
                                         text_body,
                                         "ScrumDo Robot <support@scrumdo.com>",
                                         [email_address.email],
                                         headers={'format': 'flowed'})
            msg.attach_alternative(body, "text/html")
            msg.send()
        except:
            traceback.print_exc()
            logger.warn("Failed to send an email")

        return self.create(
            email_address=email_address,
            sent=datetime.now(),
            confirmation_key=confirmation_key)






    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()


class EmailConfirmation(models.Model):

    email_address = models.ForeignKey(EmailAddress)
    sent = models.DateTimeField()
    confirmation_key = models.CharField(max_length=40)

    objects = EmailConfirmationManager()

    def key_expired(self):
        expiration_date = self.sent + timedelta(
            days=settings.EMAIL_CONFIRMATION_DAYS)
        return expiration_date <= datetime.now()
    key_expired.boolean = True

    def __unicode__(self):
        return u"confirmation for %s" % self.email_address

    class Meta:
        verbose_name = _("e-mail confirmation")
        verbose_name_plural = _("e-mail confirmations")
