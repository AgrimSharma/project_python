'''
Created on Oct 22, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'integration_services.views',
    url(r'^$','home'),
    url(r'^create_batch/$','create_batch'),
    url(r'^refresh_awb_fetch/$','refresh_awb_fetch'),
    url(r'^pickup_dashboard/$', 'pickup_dashboard', name='pickup-dashboard'),
    url(r'^pickup_enrolment/$', 'pickup_enrolment', name='pickup-enrolment'),
    url(r'^get_pincode_pickup_sc/$', 'get_pincode_pickup_sc', name='pincode-pickup_sc'),
    url(r'^get-vendors/$', 'get_vendors', name='get-vendors'),
    url(r'^get_vendor_address/$', 'get_vendor_address', name='get-vendor-address'),
    url(r'^dc_dashboard/$', 'dc_dashboard', name='dc-dashboard'),
    url(r'^update_pickup_enroll_status/$', 'update_pickup_enroll_status', name='pickup-enroll-status'),
    url(r'^multiple_pickup_enroll/$', 'multiple_pickup_enroll', name='multiple-pickup-enroll'),
    url(r'^get_awb_dc/$', 'get_awb_dc', name='get-awb-dc'),
    url(r'^download_xcl/$', 'download_xcl'),
)
