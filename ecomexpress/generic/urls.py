'''
Created on Oct 19, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'generic.views',
    url(r'^getpincode_info/$', 'getpincode_info', name='getpincode-info'),
)
