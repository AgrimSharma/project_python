# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import *
import views

urlpatterns = (
    url(r'^auth_callback$', views.auth_callback, name="auth_callback"),
)
