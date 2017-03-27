# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns('apps.affiliates.views',
    url(r'^$', "affilates", name="affilates_home"),
    url(r'^admin/$', "affilates_admin", name="affilates_admin"),
    url(r'^pay/$', "affilates_admin_pay", name="affilates_admin_pay"),
    url(r'^terms/$', TemplateView.as_view(template_name="affiliates/agreement.html")),
    url(r'^about/$', TemplateView.as_view(template_name='affiliates/affiliates_home.html')),
    url(r'^faq/$', TemplateView.as_view(template_name='affiliates/faq.html')),
)
