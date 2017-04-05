'''
Created on Oct 22, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('hub.views',
                       url(r'^$','inscan_bag'),
                       #url(r'^lite/$', 'inscan_bag_lite'),
                       url(r'^bagging/$','bagging'),
                       url(r'^add-bagging/$','add_bagging'),
                       url(r'^inscan_shipment/$','inscan_shipment'),
                       url(r'^mass_updation/$','mass_updation'),
                       url(r'^connection/$','connection'),
                       url(r'^connection_tallied/$','connection_tallied'),
                       url(r'^octroi/$','octroi'),
                       url(r'^redirection/$','redirection'),
                       url(r'^delink_shipment_oct/(?P<oid>\d+)/$','delink_shipment_oct'),
                       url(r'^bag_count/(?P<bid>\w+)/$','bag_count'),
                       url(r'^octroi_summary/(?P<oid>\d+)/$','octroi_summary'),
		       url(r'^octroi_summary_edit/(?P<oid>\d+)/$','octroi_summary_edit'),
                       url(r'^octroi_manifest/(?P<oid>\d+)/(?P<stat>\d+)/$','octroi_manifest'),
                       url(r'^update_octroi/$','update_octroi'),
                       url(r'^run_code/$','run_code'),
                       url(r'^close_octroi/$','close_octroi'),
                       url(r'^nform/$','nform'),
                       url(r'^flat_update_octroi/$','flat_update_octroi'),
                       url(r'^delink_shipment_nform/(?P<oid>\d+)/$','delink_shipment_nform'),
                       url(r'^nform_manifest/(?P<oid>\d+)/$','nform_manifest'),
                       url(r'^octroi_reciept_edit/(?P<oid>\d+)/$','octroi_reciept_edit'),
                       url(r'^update_reciepts/(?P<oid>\d+)/$','update_reciepts'),
                       url(r'^run_code/$','run_code'),
                       url(r'^close_nform/$','close_nform'),
                       #url(r'^wb_entry_tax/$','wb_entry_tax'),
                       url(r'^close_connection/$','close_connection'),
                       url(r'^airport_confirmation/$','airport_confirmation'),
                       url(r'^connection_bags/(?P<cid>\w+)/$','connection_bags'),
                       url(r'^bag_tallied/$','bag_tallied'),
                       url(r'^dash_board/$','dash_board'),
                       url(r'^dash_board_bag/(?P<pid>\w+)/$', 'dash_board_bag'),
                       url(r'^cbags/',include('operations.urls')),
)
