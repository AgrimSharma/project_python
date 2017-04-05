from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
#from customer.views import *
# Uncomment the next two lines to enable the admin:
# admin.autodiscover()

urlpatterns = patterns('nimda.views',
    # Examples:
    url(r'^$', direct_to_template, {'template': 'nimda/shipment_mass_updation.html'}),
    url(r'^shipment_update/$', 'shipment_update'),
    url(r'^shipment_update_weight/$', 'shipment_update_weight'),
    url(r'^individual_shipment_update/$', 'individual_shipment_update'),
    url(r'^coll_val/$','coll_val_update'),
    url(r'^sh_code/$','sh_code'),
    url(r'^password_reset/$','password_reset'),
    url(r'^rts_reversal/$','rts_reversal'),
    url(r'mark_ship_undelivered/$','mark_ship_undelivered'),
    url(r'update_as_lost/$','update_as_lost'),
    url(r'^update_pincode/$','update_pincode'),
    url(r'^mass_shipment_upload/$','mass_update_undelivered'),
#    url(r'^add/$', 'add_customer', name='nimda_customer'),

)