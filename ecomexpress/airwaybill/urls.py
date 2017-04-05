'''
Created on Oct 8, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('airwaybill.views',
                       url(r'^airwaybill_search/$','airwaybill_search'),
                       url(r'^airwaybill_generate/$','generate_airwaybills'),
                       url(r'^airwaybill_download/(?P<aid>\w+)/(?P<tid>\w+)/$','airwaybill_download'),
                       )
