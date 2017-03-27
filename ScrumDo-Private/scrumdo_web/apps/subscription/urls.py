# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.conf.urls import patterns, url

import retarget_views
import views

urlpatterns = (
    url(r'^retarget_org$', retarget_views.retarget_org_choose, name="retarget_org_choose"),
    url(r'^retarget_upgrade$', retarget_views.retarget_upgrade, name="retarget_upgrade"),

    url(r'^register$', views.register, name='register'),
    url(r'^stats_data$', views.stats_data),
    url(r'^spreedly_web_hook$', views.spreedly_web_hook),
    url(r'^stats$', views.stats, name="spreedly_stats"),
    url(r'^stats2$', views.stats_charts, name="stats_charts"),
    
    url(r'^sub$', views.subscription_redirect),

    url(r'^completed/(?P<organization_slug>[-\w]+)$', views.subscription_completed, name="subscription_completed"),
    # url(r'^survey$', "survey"),
    url(r'^(?P<organization_slug>[-\w]+)/invoices$', views.invoices, name="invoices"),

    url(r'^start_trial/(?P<organization_slug>[-\w]+)/(?P<plan_id>[0-9]+)$',views.start_trial,name="start_trial"),
    url(r'^expired/(?P<organization_slug>[-\w]+)$',views.user_trial_expired, name='user_trial_expired'),
    url(r'^expired/(?P<organization_slug>[-\w]+)/staff$',views.staff_trial_expired, name='staff_trial_expired'),
    url(r'^free_plan/(?P<organization_slug>[-\w]+)$',views.set_free_plan, name='set_free_plan'),
    
    url(r'^special/(?P<organization_slug>[-\w]+)/(?P<plan_id>[0-9]+)$',views.special_offer, name='special_offer'),
    url(r'^special/(?P<organization_slug>[-\w]+)/(?P<offer_name>[a-z]+)$',views.special_offer_named, name='special_offer_named'),

    # url(r'^offers/(?P<organization_slug>[-\w]+)$', views.special_offers, name="special_offers"),
    url(r'^(?P<organization_slug>[-\w]+)/cancel$', views.subscription_cancel, name="subscription_cancel"),
    url(r'^(?P<organization_slug>[-\w]+)/premium$', views.org_upgrade_premium, name="org_upgrade_premium"),
    url(r'^(?P<organization_slug>[-\w]+)$', views.subscription_options, name="subscription_options"),
    url(r'^(?P<organization_slug>[-\w/]+)/(?P<invoice_token>[-\w]+)$', views.invoice, name="invoice"),
)

