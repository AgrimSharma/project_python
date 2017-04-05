'''
Created on Sep 27, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('mobi_api.views',
                       url(r'^$','login_authenticate'),
#                       url(r'^shippments/(?P<id>\w+)','pickup_details'),
                       #url(r'^shippments/(?P<id>\d+)/(?P<uname>\w+)/(?P<pwd>\w+)/$','pickup_details'),
                       url(r'^details/','details'),
                       url(r'^get_awb_details','get_awb_details'),
                       url(r'^complete_pickup/','complete_pickup'),
                       url(r'^outscan_details/','outscan_details'),
                       url(r'^delivery_login/','delivery_login'),
                       url(r'^report/post/','pickup_report'),
                       url(r'^lastmile/update/$','lastmile_pod_update'),
                       url(r'^delivery_update/','delivery_update'),
                       url(r'^save_images/','save_images'),
                       url(r'^sample_response/','sample_response'),
                       url(r'^get_pending_pickups/','get_pending_pickups'),
                       )
