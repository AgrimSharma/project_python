'''
Created on Oct 19, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *


urlpatterns = patterns('apiv2.views',
                       #url(r'^$','index'),
                       #url(r'^get_pincodes/$','get_pincodes'),
                       url(r'^pincodes/$','get_pincodes_all'),
                       url(r'^pincodes_date/$','get_pincodes_date'),
                       url(r'^pincodes_state/$','get_pincodes_state'),
                       url(r'^fetch_awb/$','get_awb'),
                       url(r'^manifest_awb/$','api_manifest_awb_shipment'),
                       url(r'^cancel_awb/$','cancel_rto_awb'),
)
