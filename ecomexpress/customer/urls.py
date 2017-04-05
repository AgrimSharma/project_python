
#===============================================================================
# Copyright, 2012, All Rights Reserved. 
# File Name:views.py
# Project Name:ecomm
# To create views for customer 
# Revision: 1
# Developer: Vish Gite
#===============================================================================


from django.conf.urls.defaults import patterns, url
#from customer.views import *
# Uncomment the next two lines to enable the admin:
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'customer.views.customer_home', name='customer_home'),
    url(r'^add/$', 'customer.views.add_customer', name='add_customer'),
    url(r'^edit/(?P<c_id>\d+)/$', 'customer.views.edit_customer', name='edit_customer'),
    url(r'^shippers/(?P<c_id>\d+)/$', 'customer.views.sub_customer', name='sub_customer'),
    url(r'^shippers/upload/sub_customers/$', 'customer.views.update_subcustomers', name='upload-subcustomers'),
    url(r'^shippers/sub_customers/get_form/$', 'customer.views.subcustomers_upload_form', name='subcustomers-upload-form'),
    url(r'^price/(?P<c_id>\d+)/$', 'customer.views.price_customer', name='price_customer'),
    url(r'^pricematrix/(?P<c_id>\d+)/$', 'customer.views.pricematrix_customer', name='pricematrix_customer'),
    url(r'^branding/(?P<c_id>\d+)/$', 'customer.views.branding_customer', name='branding_customer'),
    #fs_customer
    url(r'^fs/(?P<c_id>\d+)/$', 'customer.views.fs_customer', name='fs_customer'),
    url(r'^cod/(?P<c_id>\d+)/$', 'customer.views.cod_customer', name='cod_customer'),
    url(r'^add_zone/(?P<fs_id>\d+)/$', 'customer.views.add_zone', name='add_zone'),
    url(r'^rates/update_rate_dates/$', 'customer.views.update_rate_dates',name='update_rate_dates'),
    url(r'^rates/update_customer/$', 'customer.views.update_customer',name='update_customer'),
    url(r'^(?P<c_id>\d+)/activate/$', 'customer.views.activate_customer', name='activate_customer'),
    url(r'^(?P<c_id>\d+)/deactivate/$', 'customer.views.deactivate_customer', name='deactivate_customer'),
    url(r'rates/download/','customer.views.download_rates',name='download_rates'),
#    url(r'^(?P<c_id>\d+)/$', 'customer.views.edit_customer', name='edit_customer'),
    url(r'^(?P<c_id>\d+)/del/$', 'customer.views.delete_customer', name='delete_customer'),


    
    url(r'^weightrate/$', 'customer.views.customer_weight_rate_home', name='cust_wr_home'),
#    url(r'^weightrate/(?P<c_id>\d+)/$', 'customer.views.edit_customer_weight_rate', name='edit_cust_wr_home'),
    url(r'^weightrate/(?P<customer_id>\d+)/add/$', 'customer.views.customer_rate_details', name='customer_rate_details'),
    url(r'^weightrate/(?P<customer_id>\d+)/edit/$', 'customer.views.edit_customer_rate_details', name='ed_customer_rate_details'),

    
#    url(r'^dimensionrate/$', 'customer.views.customer_dimension_rate_home', name='cust_dr_home'),


    url(r'^otherdetails/(?P<customer_id>\d+)/add/$', 'customer.views.add_customer_other_details', name='cust_other_det'),
    url(r'^otherdetails/(?P<customer_id>\d+)/edit/$', 'customer.views.edit_customer_other_details', name='cust_other_det_edit'),
    
    url(r'^otherdetailsrate/(?P<customer_id>\d+)/add/$', 'customer.views.add_customer_otherdetails_rate', name='add_cust_other_rates'),
    url(r'^otherdetailsrate/(?P<customer_id>\d+)/edit/$', 'customer.views.edit_customer_otherdetails_rate', name='edit_cust_other_rates'),

    url(r'^subcustomer_info/$', 'customer.views.subcustomer_info', name='customer_information'),
    

    url(r'^customer_subcustomer/(?P<cid>\d+)/$', 'customer.views.customer_subcustomer', name='customer_subcustomer'),
    url(r'^rates/(?P<c_id>\d+)/$', 'customer.views.customer_rates', name='customer_rates'),
    url(r'^rates/(?P<c_id>\d+)/v2/$', 'customer.views.customer_rates_v2', name='customer_rates_v2'),
    url(r'^rates/update_rate_dates/$', 'customer.views.update_rate_dates',name='update_rate_dates'),
    url(r'^rates/update_customer/$', 'customer.views.update_customer',name='update_customer'),
    url(r'^rates/percentage_hike/(?P<c_id>\d+)/$', 'customer.views.update_hike_ui', name='update_hike_ui'),


)
