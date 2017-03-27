from django.conf.urls import patterns, url
from django.contrib import admin

import views

admin.autodiscover()


signup_view = "apps.account.views.signup"


urlpatterns = (
    url(r'^loginredirect$', views.login_redirect, name="google_login_redirect"),
    url(r'^oauth2callback', views.auth_callback, name="google_auth_callback"),
)