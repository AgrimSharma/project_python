# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import *

import views

urlpatterns = (
    url(r'^$', views.staff_home),
    url(r'^kanbanstats$', views.kanbanstats, name="kanbanstats"),
    url(r'^scrumstats', views.scrumstats, name="scrumstats"),
    url(r'^recentstats', views.recentstats, name="recentstats"),
    url(r'^subscribers$', views.subscribers, name="subscribers"),
    url(r'^trialusers', views.trialusers, name="trialusers"),
    url(r'^stats$', views.sitestats, name="sitestats"),
    url(r'^stats_data$', views.stats_data),
    url(r'^userlookup$', views.userlookup, name="staffuserlookup")
)
