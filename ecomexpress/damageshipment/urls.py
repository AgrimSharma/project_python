#from django.conf.urls.defaults import *

#urlpatterns = patterns('damageshipment.views',
#                       url(r'^$','damageshipment'),
#                       url(r'airwaybill_search/$','airwaybill_search'),)

from django.conf.urls.defaults import *

urlpatterns = patterns('damageshipment.views',
                       url(r'^$','damageshipment'),
                       url(r'^airwaybill_search/$','airwaybill_search'),
                       url(r'^download_xcl/$', 'download_xcl'),
                       url(r'^shipment_sold/$', 'shipment_sold'),
                       url(r'^shipment_sold_details/$', 'shipment_sold_details'),
#                       url(r'^airwaybill_search/shipment_sold/$','shipment_sold'),
                       url(r'^airwaybill_search/shipment_sold/$','shipment_sold'),
		       url(r'^recovery_view/$', 'recovery_view'),
		       #url(r'^recovery_details/$', 'recovery_details'),
		       url(r'^airwaybill_search/recovery_view/$','recovery_view'),
                       #url(r'^airwaybill_search/recovery_details/$', 'recovery_details'),

)

