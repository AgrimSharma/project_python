# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import url
from views import project_hook, story_hook

urlpatterns = (
    url(r'^hook$', project_hook),
    url(r'^story_hook$', story_hook)
)

