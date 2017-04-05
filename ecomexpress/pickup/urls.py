'''
Created on Sep 27, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *
from django.forms import ModelForm

urlpatterns = patterns('pickup.views',
                       url(r'^$','pickup_dashboard'),
                       url(r'^reverse/$','reverse_pickup_dashboard'),
                       url(r'^update_employee/$','update_employee'),
                       url(r'^reverse_shipment/rev_order_slip/(?P<sid>\w+)/$','reverse_order_slip'),
                       url(r'^reverse_shipment/$','reverse_shipment'),
                       url(r'^reverse_shipment_report/$','reverse_shipment_report'),
                       url(r'^reverse/download/(?P<pid>\w+)/(?P<tid>\w+)/$','reverse_pickup_download'),
#                       url(r'^pending_pickup/$','pending_pickup'),
 #                      url(r'^completed_pickup/$','completed_pickup'),
  #                     url(r'^request_pickup/$','request_pickup'),
                       url(r'^update_reverse_shipment/$','update_reverse_shipment'),
                       url(r'^bulk_pickup_registration/$','bulk_pickup_registration'),
                       url(r'^reverse_shipment/print/$','reverse_shipment_print'),
                       url(r'^get_single_barcode/(?P<awb>\d+)/$','reverse_shipment_single_print'),
                       url(r'^cancel_pickup/(?P<id>\w+)/$','cancel_pickup'),
                       url(r'^copy_pickup/(?P<id>\w+)/$','copy_pickup'),
                       url(r'^registration/$','pickup_registration'),
                       url(r'^volumetric_calculator/$','volumetric_calculator'),
                       url(r'^edit_pickup/(?P<id>\w+)/$','edit_pickup'),
                       url(r'^finders/$','finder_pincode_view'),
                       url(r'^pincode_view/$','pincode_view'),
                       url(r'^transit_time/$','transit_time'),
                       url(r'^update_reason_code/$','update_reason_code'),
                       url(r'^update_employee_code/$','update_employee_code'),
                       url(r'^reverse_ship/update_reason_code/$','rship_update_reason_code'),
                       url(r'^reverse_ship/update_employee_code/$','rship_update_employee_code'),
                       url(r'^reverse_ship/update_awb_number/$','rship_update_awb_number'),
                       url(r'^reverse_ship/update_length/$','rship_update_etc', {'param':'length'}),
                       url(r'^reverse_ship/update_height/$','rship_update_etc', {'param':'height'}),
                       url(r'^reverse_ship/update_breadth/$','rship_update_etc', {'param':'breadth'}),
                       url(r'^reverse_ship/update_vw/$','rship_update_etc', {'param':'volumetric_weight'}),
                       url(r'^reverse_ship/update_aw/$','rship_update_etc', {'param':'actual_weight'}),
                       url(r'^reverse_ship/revert/$','rship_revert'),
                       url(r'^pickup_sheet/$','text_pickup_sheet'),
                       url(r'^(?P<ptype>\w+)/$','pickup_dashboard'),
#                       url(r'^rev_pickup_download/(?P<pid>\w+)/$','reverse_pickup_download'),(?P<pid>\w+)/
                       url(r'^download_xcl/$', 'download_xcl'), 
		       url(r'^reverse_shipment/multiple_rvp/$','multiple_rvp'),
		       url(r'^reverse_shipment/multiple_rvp_remove/$','multiple_rvp_remove'),
                       )
