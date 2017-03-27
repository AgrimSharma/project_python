# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import patterns, url

import views


urlpatterns = (
        url(r'^add-dropzone/(?P<project_slug>[-\w]+)/(?P<story_id>[-]?\d+)/$', views.add_attachment_ajax),
        url(r'^add-dropzone/(?P<project_slug>[-\w]+)/note/(?P<note_id>[-]?\d+)/$', views.add_note_attachment_ajax),
)
