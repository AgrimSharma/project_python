from django.conf.urls.defaults import *

urlpatterns = patterns('dcdashboard.views',
                       url(r'^$','dashboard'),
                       url(r'^fetch_awb/$', 'fetch_awb'),
)

