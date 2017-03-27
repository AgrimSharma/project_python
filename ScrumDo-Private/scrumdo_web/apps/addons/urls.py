# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns('apps.addons.views',
    url(r'^$', "addons", name="addons"),
    url(r'^addons/$', TemplateView.as_view(template_name="addons/addons.html")),
    url(r'^basecamp/$', TemplateView.as_view(template_name='addons/basecamp.html')),
    url(r'^github/$', TemplateView.as_view(template_name='addons/github.html')),
    url(r'^jira/$', TemplateView.as_view(template_name='addons/jira.html')),
    url(r'^harvest/$', TemplateView.as_view(template_name='addons/harvest.html')),

)
