# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import *
import views

urlpatterns = (
    url(r'^webhook/(?P<project_slug>[-\w]+)/(?P<event_type>[-\w]+)$', views.github_webhook, name="github_webhook"),
    url(r'^auth_callback/(?P<project_slug>[-\w]+)$', views.auth_callback, name="auth_callback"),
    url(r'^org_auth_callback/(?P<organization_slug>[-\w]+)$', views.org_auth_callback, name="org_auth_callback"),
    url(r'^login$', views.github_login, name="github_login"),
    url(r'^login_callback$', views.github_login_callback, name="github_login_callback"),
    url(r'^login_associate_callback$', views.github_login_associate_callback, name="github_login_associate_callback"),
    url(r'^log/(?P<project_slug>[-\w]+)$', views.github_log, name="github_log"),
)
