'''
Created on Oct 19, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('track_me.views',
                       url(r'^$','index'),
                       url(r'^shipper_consignee/$','shipper_consignee'),
                       url(r'^pickup_package/$','pickup_package'),
                       url(r'^comments/$','comments'),
                       url(r'^multiple_airwaybill/$','multiple_airwaybill'),
                       url(r'^generic_query/$','generic_query'),
                       url(r'^generic_query_v2/$','generic_query_v2'),
                       url(r'^comments_entry/$','comments_entry'),
                       url(r'^complaints/$','complaints'),
                       url(r'^complaint_history/(?P<cid>\w+)/$','complaints_history'),
                       url(r'^complaint_updates/$','complaint_updates'),
                       url(r'^alternate_instruction/$','alternate_instruction'),
                       url(r'^alert/$','alert'),
                       url(r'^mis/$','mis'),
                       url(r'^alert/(?P<tid>\w+)/$','alert'),
                       url(r'^complaint_resolved/(?P<id>\w+)/$','complaint_resolved'),
                       url(r'^comments_reports_download/(?P<aid>\w+)/$','comments_reports_download'),
                       url(r'^scan_open/(?P<tid>\w+)/$','scan_open'),
                       url(r'^multipleawb_open/$','multipleawb_open'),
                       url(r'^customer_status/report_download/(?P<pid>\w+)/$','customer_reports_download'),
                       url(r'^customer_status/$','customer_status'),
                       url(r'^api/awb/$','xml_awb_details'),
                       url(r'^api/mawb/$','xml_multiple_airwaybill'),
                       url(r'^api/mawbd/$','xml_multiple_airwaybill_details'),
                       url(r'^api/mawb_unused/$','xml_multiple_airwaybill_unused'),
                       url(r'^tele/$','tele'),
                       url(r'^bag_history/$','bag_history'),
                       url(r'^mawb_api/$','mawb_api'),
                       url(r'^call_centre_report/$', 'call_centre_report'),
                       url(r'^comment/$', 'comment'),
		       url(r'^multiple_bag/$', 'multiple_bag'),
		       url(r'^multiplebag_detail/$', 'multiplebag_detail'),
)
