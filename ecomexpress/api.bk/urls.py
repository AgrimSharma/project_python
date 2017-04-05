'''
Created on Oct 19, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('api.views',
                       #url(r'^$','index'),
                       url(r'^lastmile/get_dc_details/$','lastmile_outscan_details'),
                       url(r'^lastmile/update/$','lastmile_pod_update'),
                       url(r'^create_awb/$','create_shipment'),
                       url(r'^api_create_awb_xml/$','api_create_shipment'),
                       # url(r'^api_create_vendor_xml/$','create_update_vendor'), - replaced with create shipper
                       url(r'^api_create_vendor_xml/$','create_shipper'),
                       url(r'^test/$','api_form'), 
                       url(r'^test2/$','api_form2'),
                       url(r'^test3/$','api_form3'),
                       url(r'^create_vendor/$','vendor_form'),
                       url(r'^fetch_airwaybill/$','fetch_airwaybill'),
                       url(r'^api_create_order_to_awb_xml/$','api_create_awb_shipment'),
                       url(r'^api_create_rev_awb_xml/$','api_create_revawb_shipment'),

)
