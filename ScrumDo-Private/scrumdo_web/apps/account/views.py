import datetime 

from django.conf import settings
from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages # django 1.4
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, View
from django.apps import apps

from apps.brake.decorators import ratelimit

from apps.projects.models import Task

from apps.organizations.models import Organization
from apps.organizations.mixins  import OrganizationMixin

from apps.account.utils import get_default_redirect
from apps.account.models import OtherServiceInfo, PasswordReset, RegistrationKey
from apps.account.forms import (
                            SignupForm,
                            LoginForm,
                            ResetPasswordForm,
                            TwitterForm,
                            ResetPasswordKeyForm, 
                            DeleteAccountForm,
                            SignupEmailForm
                        )

import logging
logger = logging.getLogger(__name__)

association_model = apps.get_model('django_openid', 'Association')
if association_model is not None:
    from apps.django_openid.models import UserOpenidAssociation


class SignUpView(TemplateView):
    """ Template view for register new users
    """
    template_name = 'account/register.html'
    context = {}
    form = SignupEmailForm

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('home'))

        self.context['form'] = self.form()
        self.context['is_registered'] = False
        self.context['STATIC_URL']= settings.STATIC_URL
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        form = self.form(self.request.POST)
        if form.is_valid():
            form.save()
            self.context['is_registered'] = True
        self.context['form'] = form
        return render(self.request, self.template_name, self.context)


class SignUpConfirmation(OrganizationMixin, TemplateView):
    template_name = 'account/signup.html'
    context = {}
    form = SignupForm

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('home'))
        registration_key = get_object_or_404(RegistrationKey, key=kwargs['registration_key'])
        today = datetime.datetime.now()
        registration_days = (today - registration_key.created).days
        if registration_days > settings.EMAIL_REGISTRATION_DAYS or registration_key.is_used:
            if registration_key.key != settings.EMAIL_DEBUG_REGISTRATION_KEY:
                self.context['key_expired'] = True 
        else:
            registration_key.is_used = True
            registration_key.save()
            self.context['key_expired'] = False 
        self.context['form'] = self.form(initial={'email': registration_key.email })
        self.context['welcome_screen'] = True 
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        form = self.form(self.request.POST)
        if form.is_valid():
            username, password = form.save()
            user = authenticate(username=username, password=password)
            auth_login(self.request, user)
            # setting up your organization
            organization = self.create_organization(form.cleaned_data['company'])
            self.set_trial(organization)
            self.create_teams(organization)
            self.add_source(organization)
            self.create_tutorial(organization)
            return HttpResponseRedirect(organization.get_absolute_url())
        else:
            self.context['form'] = form
            self.context['welcome_screen'] = False
        return render(self.request, self.template_name, self.context)


@login_required
@ensure_csrf_cookie
def default(request):
    return render_to_response("account/default.html", context_instance = RequestContext(request))


@csrf_exempt
@ratelimit(rate='150/h', block=True, method=['POST'])
@ensure_csrf_cookie
def login(request, form_class=LoginForm, template_name="account/login.html",
          success_url=None, associate_openid=False, openid_success_url=None,
          url_required=False, extra_context=None):
    if extra_context is None:
        extra_context = {}

    if success_url is None:
        success_url = get_default_redirect(request)

    if request.method == "POST" and not url_required:
        form = form_class(request.POST)
        if form.login(request):
            if associate_openid and association_model is not None:
                for openid in request.session.get('openids', []):
                    assoc, created = UserOpenidAssociation.objects.get_or_create(
                        user=form.user, openid=openid.openid
                    )
                success_url = openid_success_url or success_url
            
            success_url = "%s%s" % (settings.SSL_BASE_URL, success_url)

            response = HttpResponseRedirect(success_url)        
            response.delete_cookie('sdHideMessageSubscription')
            return response
    else:
        form = form_class()
    ctx = {
        "form": form,
        "url_required": url_required,
        "success_url": success_url,
        "signup_form":SignupForm()
    }
    ctx.update(extra_context)
    request.session['success_url'] = success_url
    return render_to_response(template_name, ctx,
        context_instance = RequestContext(request)
    )


def githubsignup(request):
    auth_url = "%s?client_id=%s&scope=repo,read:org,write:repo_hook,user,repo:status&redirect_uri=%s/github/login_callback" % (settings.GITHUB_AUTH_URL, settings.GITHUB_CLIENT_ID, settings.SSL_BASE_URL)
    return HttpResponseRedirect(auth_url)


@ratelimit(rate='100/h', block=True, method=['POST'])
@ensure_csrf_cookie
def signup(request, form_class=SignupForm,
        template_name="account/signup.html", success_url=None):

    if request.POST.get("next", None) == None:
        success_url = "/subscription/register"  #get_default_redirect(request, default_redirect_to=success_url)
    else:
        success_url = request.POST.get("next")
        
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username, password = form.save()
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    return render_to_response(template_name, {
        "form": form,
        "success_url":success_url
    }, context_instance=RequestContext(request))



@ratelimit(rate='55/h', block=True, method=['POST'])
@ensure_csrf_cookie
def password_reset(request, form_class=ResetPasswordForm,
        template_name="account/password_reset.html",
        template_name_done="account/password_reset_done.html"):
    if request.method == "POST":
        password_reset_form = form_class(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.save()
            return render_to_response(template_name_done, {
                "email": email,
                "email_count": password_reset_form.cleaned_data["email_count"]
            }, context_instance=RequestContext(request))
    else:
        password_reset_form = form_class()
    
    return render_to_response(template_name, {
        "password_reset_form": password_reset_form,
    }, context_instance=RequestContext(request))


@ratelimit(rate='55/h', block=True, method=['POST'])
@ensure_csrf_cookie
def password_reset_from_key(request, key, form_class=ResetPasswordKeyForm,
        template_name="account/password_reset_from_key.html"):
    if request.method == "POST":
        password_reset_key_form = form_class(request.POST)
        if password_reset_key_form.is_valid():
            password_reset_key_form.save()
            password_reset_key_form = None
    else:
        password_reset_key_form = form_class(initial={"temp_key": key})
    
    return render_to_response(template_name, {
        "form": password_reset_key_form,
    }, context_instance=RequestContext(request))


@login_required
@ensure_csrf_cookie
def other_services(request, template_name="account/other_services.html"):
    from microblogging.utils import twitter_verify_credentials
    twitter_form = TwitterForm(request.user)
    twitter_authorized = False
    if request.method == "POST":
        twitter_form = TwitterForm(request.user, request.POST)
        
        if request.POST['actionType'] == 'saveTwitter':
            if twitter_form.is_valid():
                from microblogging.utils import twitter_account_raw
                twitter_account = twitter_account_raw(
                    request.POST['username'], request.POST['password'])
                twitter_authorized = twitter_verify_credentials(
                    twitter_account)
                if not twitter_authorized:
                    messages.success(request, "Twitter authentication failed")
                else:
                    twitter_form.save()
    else:
        from microblogging.utils import twitter_account_for_user
        twitter_account = twitter_account_for_user(request.user)
        twitter_authorized = twitter_verify_credentials(twitter_account)
        twitter_form = TwitterForm(request.user)
    return render_to_response(template_name, {
        "twitter_form": twitter_form,
        "twitter_authorized": twitter_authorized,
    }, context_instance=RequestContext(request))

@login_required
def other_services_remove(request):
    # TODO: this is a bit coupled.
    OtherServiceInfo.objects.filter(user=request.user).filter(
        Q(key="twitter_user") | Q(key="twitter_password")
    ).delete()
    messages.add_message(request, "Removed twitter account information successfully.") # django 1.4
    return HttpResponseRedirect(reverse("acct_other_services"))


@login_required
@csrf_protect
def delete_account(request, template_name="account/delete_account.html"):
    """
    User able to delete there own account
    """

    is_delete = False
    delete_form = DeleteAccountForm(instance=request.user)
    if request.method == "POST":
        delete_form = DeleteAccountForm(request.POST, instance=request.user)
        if delete_form.is_valid():
            account = authenticate(username=request.user.username, password=request.POST['password1'])
            if account:
                if not Organization.objects.filter(creator=request.user):
                    is_delete = True
                    request.user.is_active = False
                    request.user.email = ''
                    request.user.save()
                    for password_reset in PasswordReset.objects.filter(user=request.user):
                        password_reset.delete()

                    for task in Task.objects.filter(assignee=request.user):
                        task.assignee = None
                        task.save()

                    if "subscription" in settings.INSTALLED_APPS:
                        from apps.email_notifications.models import EmailOptions
                        for email_subscription in EmailOptions.objects.filter(user=request.user):
                            email_subscription.delete()

                    for user_openid in UserOpenidAssociation.objects.filter(user=request.user):
                        user_openid.delete()
                    return HttpResponseRedirect(reverse('acct_logout'))
                else:                    
                    messages.success(request,("You need to delete your organizations before you able to delete your account."))
            else:
                # request.user.message_set.create(message="Incorrect password")
                messages.success(request,("Incorrect Password"))

    return render_to_response(template_name, {
                                              'form': delete_form,
                                              'is_delete': is_delete,
    }, context_instance=RequestContext(request))


    

