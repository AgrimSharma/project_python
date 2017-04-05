'''
Created on Oct 19, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('amazon_api.views',
                      url(r'^$','get_pincodes_txt'),
                      url(r'^a_m$','amazon_manifest'),
)
