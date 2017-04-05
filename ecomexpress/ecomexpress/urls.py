from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$','authentication.views.login_authenticate'),                   
    url(r'^access_denied/$','authentication.views.access_denied'),
    url(r'^track_shipment/$','track_me.views.track_shipment'),
    # Examples:
    # url(r'^$', 'ecomm.views.home', name='home'),
    url(r'^damageshipment/', include('damageshipment.urls')),
    url(r'^security/', include('security.urls')),
    url(r'^billing/', include('billing.urls')),
    url(r'^customer/', include('customer.urls')),
    url(r'^authentication/', include('authentication.urls')), 
    url(r'^pickup/', include('pickup.urls')),
    url(r'^location/', include('location.urls')),
    url(r'^airwaybill/', include('airwaybill.urls')),
    url(r'^service-centre/', include('service_centre.urls')),
    url(r'^track_me/', include('track_me.urls')),
    url(r'^delivery/', include('delivery.urls')),
    url(r'^hub/', include('hub.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^octroi/', include('octroi.urls')),
    url(r'^operations/',include('operations.urls')),
    url(r'^generic/',include('generic.urls')),
    url(r'^cod_panel/',include('cod_panel.urls')),
    url(r'product_master/',include('product_master.urls')),
    url(r'^dashboard/', include('dcdashboard.urls')),
    url(r'^shacti_api/',include('shacti_api.urls')),
    url(r'^amazon_api/',include('amazon_api.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^nimda_beta/', include('nimda.urls')),    
    #Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    #To load static files
    url(r'^static/uploads/(?P<path>.*)$', 'authentication.views.serve_file'),
    url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root': settings.STATIC_ROOT}),
)
