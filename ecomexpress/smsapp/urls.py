from django.conf.urls.defaults import *

urlpatterns = patterns('smsapp.views',
                       url(r'^$','process_queue'),
                       url(r'^add_awb/','add_awb'),
                       )   

