'''
Created on Oct 22, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('octroi.views',
                       url(r'^$','octroi_billing_details', {'updated':False}, name='octroi-billing-details'),
                       url(r'^customer/add_billing/$','add_billing'),
                       url(r'^customer/(?P<cid>\d{1,3})/$','customer', name='octroi-customer'),
                       url(r'^customer/(?P<bid>\d+)/invoice_summary/$','invoice_summary'),
                       url(r'^customer/(?P<bid>\d+)/invoice_summary_without_header/$','invoice_summary_without_header'),
                       url(r'^customer/(?P<bid>\d+)/awb_pdf/$','awb_pdf'),
                       url(r'^customer/(?P<bid>\d+)/awb_excel/$','awb_excel'),
                       url(r'^unbilled_ships/(?P<cid>\d{1,3})/$','unbilled_ships'),
                       url(r'^custom_billing/$','custom_billing'),
                       #url(r'^reports/customer/','customer_wise'),
                       #url(r'^reports/bill/','bill_wise'),
                       url(r'^process_reports/','process_reports'),
                       #url(r'^octroi_process_reports/','octroi_process_reports'),
		       url(r'^octroi_cus_process_reports/','octroi_cus_process_reports'),
		       url(r'^octroi_charge_change/','octroi_charge_change'),
)
