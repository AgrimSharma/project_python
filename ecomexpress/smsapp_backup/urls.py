'''
Created on Sep 27, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('smsapp.views',
                       url(r'^$','process_queue'),
                       url(r'^add_awb/','add_awb'),
                       )
