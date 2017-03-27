# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import patterns, url
import views

urlpatterns = (
    url(r'download/chat/(?P<message_id>[0-9]+)$', views.download_chat_attachment, name='download_chat_attachment'),
    url(r'(?P<project_slug>[-\w]+)/chat_callback$', views.chat, name='realtime_chat'),
    url(r'(?P<project_slug>[-\w]+)/chat_history$', views.chat_history, name='realtime_chat_history'),
    url(r'(?P<project_slug>[-\w]+)/chat_upload$', views.chat_upload, name='chat_upload'),
)
