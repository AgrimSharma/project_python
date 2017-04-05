
#===============================================================================
# Copyright, 2012, All Rights Reserved. 
# File Name:views.py
# Project Name:ecomm
# To create views for Location module 
# Revision: 1
# Developer: Vish Gite
#===============================================================================


from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('location.views',
    # Examples:
    url(r'^$', 'location', name='locations_home'),
    url(r'^add/$', 'add_location_details'),
    url(r'^update/$', 'update_table_field'),

    url(r'^add/zone/$', 'add_zone_details'),
    url(r'^add/state/$','add_state_details'),
    url(r'^add/city/$','add_city_details'),
    url(r'^add/branch/$','add_branch_details'),
    url(r'^add/area/$','add_area_details'),
    url(r'^add/center/$','add_center_details'),
    url(r'^add/pinroute/$','add_pinroutes_details'),
    url(r'^add/pincode/$','add_pincode_details'),

    #url(r'^delete/?P<loc_id>\d+/$','delete_record'),


    
#   url(r'^(?P<location_id>\d+)/$', 'customer.views.edit_customer', name='edit_customer'),
#    url(r'^(?P<location_id>\d+)/del/$', 'customer.views.delete_customer', name='delete_customer'),



)