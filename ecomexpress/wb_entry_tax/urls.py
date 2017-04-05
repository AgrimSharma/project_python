from django.conf.urls.defaults import *

urlpatterns = patterns('wb_entry_tax.views',
                        url(r'^tax_manifest_summary/(?P<oid>\d+)/$','tax_manifest'),
                       url(r'^wb_entry_tax','wb_entry_tax',name='wb_entry_tax'),
                       url(r'^billing/customer/(?P<cid>\d+)/$','mycustomer', name='wb-entry-tax-customer'),
                       url(r'^wbetax_billing_details','wbetax_billing_details'),
                       url(r'^wb_entry_tax/(?P<oid>\d+)/(?P<stat>\d+)/$','wbtax_manifest'),
                       url(r'^entry_tax','entry_tax'),
                       url(r'^billing/','wb_entry_tax_billing_details'),
                       url(r'^customer/add_billing/$','add_billing'),
                       #url(r'^billing/customer/(?P<cid>\d{1,3})/$','customer', name='octroi-customer'),
                       #url(r'^customer/(?P<bid>\d+)/invoice_summary/$','invoice_summary'),
                       url(r'^customer/(?P<bid>\d+)/invoice_summary/$','invoice_summary'),
                       url(r'^customer/(?P<bid>\d+)/invoice_summary_without_header/$','invoice_summary_without_header'),
                       url(r'^customer/(?P<bid>\d+)/awb_pdf/$','awb_pdf'),
                       url(r'^customer/(?P<bid>\d+)/awb_excel/$','awb_excel'),
                       #url(r'^unbilled_ships/(?P<cid>\d{1,3})/$','unbilled_ships'),
                       url(r'^custom_billing/$','custom_billing'),
                       url(r'^process_reports/','process_reports'),
                       #url(r'^customer/(?P<bid>\d+)/customer/(?P<bid>\d+)/$','myysample_billing')
)

