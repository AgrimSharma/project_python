# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import *

import views

urlpatterns = (
    url(r'^$', views.unsubscribe_home),
    url(r'^robot$',views.unsubscribe_robot),
    url(r'confirm$', views.unsubscribe_confirm, name="unsubscribe_confirm"),
)
