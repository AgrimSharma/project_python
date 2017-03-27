import re

from django import forms
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


import hashlib

from mailer import send_mail
from django.core.mail import EmailMultiAlternatives

from django.contrib.auth import authenticate, login
from django.forms.models import ModelForm
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from apps.emailconfirmation.models import EmailAddress
from apps.account.models import Account

from apps.account.models import PasswordReset, RegistrationKey
from apps.account.signals import reset_password

import random

from django.contrib import messages # django 1.4

alnum_re = re.compile(r'^[\w-]+$')
import logging
import traceback

logger = logging.getLogger(__name__)

class LoginForm(forms.Form):

    username = forms.CharField(label=_("Username"), max_length=30, widget=forms.TextInput())
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
    remember = forms.BooleanField(label=_("Remember Me"), help_text=_("If checked you will stay logged in for 3 weeks"), required=False)

    user = None

    def clean(self):
        if self._errors:
            return        
        try:
            user = authenticate(username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        except:
            raise forms.ValidationError("Could not log in.  Did you sign up via a third party login below?")


        if user:
            account = Account.objects.get(user=user)

            if not account.approved:
                raise forms.ValidationError(_("This account is not yet approved."))
                
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_("This account is currently inactive."))
        else:
            raise forms.ValidationError(_("The username and/or password you specified are not correct."))
        return self.cleaned_data

    def login(self, request):
        if self.is_valid():
            login(request, self.user)            
            request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            return True
        return False


class SignupEmailForm(forms.Form):
    email = forms.EmailField(label=_("Email"), required=True, widget=forms.TextInput())

    def clean_email(self): 
        if self.cleaned_data["email"] == settings.REGISTRATION_TEST_EMAIL:
            return self.cleaned_data["email"]
        try:
            user = User.objects.get(email__iexact=self.cleaned_data["email"])
        except User.DoesNotExist:
            return self.cleaned_data["email"]
        except User.MultipleObjectsReturned:
            pass
        raise forms.ValidationError(_("The email address you have entered is already registered. Please choose another."))

    def save(self):
        email = self.cleaned_data['email']
        domain =  settings.BASE_URL if settings.DEBUG else settings.SSL_BASE_URL
        try:
            # delete existing keys with email address
            existing_keys = RegistrationKey.objects.filter(email=email)
            if existing_keys.count() > 10:
                for exist_key in existing_keys:
                    exist_key.delete()
            else:
                for exist_key in existing_keys:
                    exist_key.is_used = True
                    exist_key.save()
        except:
            pass
        confirmation = RegistrationKey.objects.create(email=email)
        confirmation.send_registration_email()
        return confirmation


class SignupForm(forms.Form):
    username = forms.CharField(label=_("Username"), min_length=4, max_length=30, widget=forms.TextInput(), help_text="This is a username for you, we'll set up your company in the next step.")
    fullname = forms.CharField(label=_("Full Name"), max_length=50, widget=forms.TextInput())
    password = forms.CharField(label=_("Password"), min_length=4, widget=forms.PasswordInput(render_value=False))
    email = forms.EmailField(label=_("Email"), required=True, widget=forms.HiddenInput())
    company = forms.CharField(label=_("Organization Name"), max_length=65, widget=forms.TextInput())

    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(_("Usernames can only contain letters, numbers and underscores."))
        try:
            user = User.objects.get(username__iexact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError(_("This username is already taken. Please choose another."))

    def clean(self):
        return self.cleaned_data
        
    def save(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        new_user = User.objects.create_user(username, email, password)
        # Auto confirm Email as we did Email verification Already
        EmailAddress.objects.add_email(new_user, email, autoConfirm = True)
        # sending welcome email
        self.send_welcome_email(new_user)
        try:
            names = self.cleaned_data["fullname"].split(" ")
            # This scheme handles mutiple first names well.
            new_user.first_name = " ".join(names[0:-1])  # Everything but last word is first name
            new_user.last_name = " ".join(names[-1:])    # Last word in list is last name
            new_user.save()
        except:
            logger.warn(u"Could not split name %s" % self.cleaned_data["fullname"])

        return username, password  # required for authenticate()

    
    def send_welcome_email(self, new_user):
        
        context = {
            "user": new_user,
            "base_url" : settings.BASE_URL,
            'STATIC_URL': settings.STATIC_URL
        }

        try:
            logger.debug("Sending Welcome email to %s " % new_user.email)

            body = render_to_string("account/welcome_to_scrumdo.html" , context )
            text_body = render_to_string("account/welcome_to_scrumdo.txt", context)
        
            subject = "[ScrumDo] Welcome to ScrumDo!"

            msg = EmailMultiAlternatives(subject,
                                         text_body,
                                         "ScrumDo Robot <support@scrumdo.com>",
                                         [new_user.email],
                                         headers={'format': 'flowed'})
            msg.attach_alternative(body, "text/html")
            msg.send()
        except:
            traceback.print_exc()
            logger.warn("Failed to send an email")

class OpenIDSignupForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput())

    if settings.ACCOUNT_REQUIRED_EMAIL or settings.ACCOUNT_EMAIL_VERIFICATION:
        email = forms.EmailField(
            label = _("Email"),
            required = True,
            widget = forms.TextInput()
        )
    else:
        email = forms.EmailField(
            label = _("Email (optional)"),
            required = False,
            widget = forms.TextInput()
        )

    def __init__(self, *args, **kwargs):
        # remember provided (validated!) OpenID to attach it to the new user
        # later.
        self.openid = kwargs.pop("openid", None)

        # pop these off since they are passed to this method but we can't
        # pass them to forms.Form.__init__
        kwargs.pop("reserved_usernames", [])
        kwargs.pop("no_duplicate_emails", False)

        super(OpenIDSignupForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(u"Usernames can only contain letters, numbers and underscores.")
        try:
            user = User.objects.get(username__iexact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError(u"This username is already taken. Please choose another.")


class UserForm(forms.Form):

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class UserNameForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name',)
    def clean_first_name(self):
        self.cleaned_data["first_name"] = self.cleaned_data["first_name"].replace(","," ").strip()
        return self.cleaned_data["first_name"]

    def clean_last_name(self):
        self.cleaned_data["last_name"] = self.cleaned_data["last_name"].replace(","," ").strip()
        return self.cleaned_data["last_name"]


class AccountForm(UserForm):

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        try:
            self.account = Account.objects.get(user=self.user)
        except Account.DoesNotExist:
            self.account = Account(user=self.user)


class AddEmailForm(UserForm):

    email = forms.EmailField(label=_("Email"), required=True, widget=forms.TextInput(attrs={'size':'30'}))

    def clean_email(self):
        try:
            EmailAddress.objects.get(user=self.user, email=self.cleaned_data["email"])
        except EmailAddress.DoesNotExist:
            return self.cleaned_data["email"]
        raise forms.ValidationError(_("This email address already associated with this account."))

    def save(self):
#        self.user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': self.cleaned_data["email"]})
        return EmailAddress.objects.add_email(self.user, self.cleaned_data["email"])


class ChangePasswordForm(UserForm):

    oldpassword = forms.CharField(label=_("Current Password"), widget=forms.PasswordInput(render_value=False))
    password1 = forms.CharField(label=_("New Password"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("New Password (again)"), widget=forms.PasswordInput(render_value=False))

    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_("Please type your current password."))
        return self.cleaned_data["oldpassword"]

    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]

    def save(self):
        self.user.set_password(self.cleaned_data['password1'])
        self.user.save()
#        self.user.message_set.create(message=ugettext(u"Password successfully changed."))
#        messages.add_message(request, "Password successfully changed.")



class SetPasswordForm(UserForm):

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(render_value=False))

    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]

    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()
#        self.user.message_set.create(message=ugettext(u"Password successfully set."))
#        messages.success(request, _("Password successfully set.") # django 1.4


class ResetPasswordForm(forms.Form):

    email = forms.EmailField(label=_("Email"), required=True, widget=forms.TextInput(attrs={'size':'30'}))

    def clean_email(self):
        count = EmailAddress.objects.filter(email__iexact=self.cleaned_data["email"]).count()
        self.cleaned_data["email_count"] = count
        if count == 0:
            raise forms.ValidationError(_("Email address not verified for any user account"))
        return self.cleaned_data["email"]

    def save(self):
        for address in EmailAddress.objects.filter(email__iexact=self.cleaned_data["email"], user__is_active=True):
            user = address.user

            temp_key = hashlib.sha1("%s%s%d" % (
                settings.SECRET_KEY,
                address.email,
                random.randint(0, 32000),
            )).hexdigest()

            # save it to the password reset model
            password_reset = PasswordReset(user=user, temp_key=temp_key)
            password_reset.save()

            domain =  settings.BASE_URL if settings.DEBUG else settings.SSL_BASE_URL

            #send the password reset email
            subject = _("Password reset email sent")
            message = render_to_string("account/password_reset_key_message.txt", {
                "user": user,
                "temp_key": temp_key,
                "domain": domain,
            })

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [address.email], priority="high")
        return self.cleaned_data["email"]


class ResetPasswordKeyForm(forms.Form):

    password1 = forms.CharField(label=_("New Password"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("New Password (again)"), widget=forms.PasswordInput(render_value=False))
    temp_key = forms.CharField(widget=forms.HiddenInput)

    def clean_temp_key(self):
        temp_key = self.cleaned_data.get("temp_key")
        if PasswordReset.objects.filter(temp_key=temp_key, reset=False).count() == 0:
            raise forms.ValidationError(_("Temporary key is invalid."))
        return temp_key

    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]

    def save(self):
        # get the password_reset object
        temp_key = self.cleaned_data.get("temp_key")
        reset_records = PasswordReset.objects.filter(temp_key__exact=temp_key, reset=False)
        if len(reset_records) > 0:
            password_reset = reset_records[0]
        else:
            raise forms.ValidationError(_("Could not find that password reset key"))

        # now set the new user password
        user = User.objects.get(passwordreset__exact=password_reset)
        user.set_password(self.cleaned_data["password1"])
        user.save()
#        user.message_set.create(message=ugettext(u"Password successfully changed."))
        # messages.add_message(request, "Password successfully changed.") # django 1.4

        # change all the password reset records to this person to be true.
        for password_reset in PasswordReset.objects.filter(user=user):
            password_reset.reset = True
            password_reset.save()



# @@@ these should somehow be moved out of account or at least out of this module

from apps.account.models import OtherServiceInfo, other_service, update_other_services

class TwitterForm(UserForm):
    username = forms.CharField(label=_("Username"), required=True)
    password = forms.CharField(label=_("Password"), required=True,
                               widget=forms.PasswordInput(render_value=False))

    def __init__(self, *args, **kwargs):
        super(TwitterForm, self).__init__(*args, **kwargs)
        self.initial.update({"username": other_service(self.user, "twitter_user")})

    def save(self):
        from microblogging.utils import get_twitter_password
        update_other_services(self.user,
            twitter_user = self.cleaned_data['username'],
            twitter_password = get_twitter_password(settings.SECRET_KEY, self.cleaned_data['password']),
        )
#        self.user.message_set.create(message=ugettext(u"Successfully authenticated."))


class DeleteAccountForm(forms.ModelForm):
    username = forms.CharField(label=_("Username"), required=True, widget=forms.HiddenInput())
    password1 = forms.CharField(label=_("Enter Password"), widget=forms.PasswordInput(render_value=False))
    
    class Meta:
        model = User
        fields = ('username',)