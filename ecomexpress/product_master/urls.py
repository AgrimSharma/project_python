'''
Created on Dec 2, 2014

@author: prtouch
'''

from django.conf.urls.defaults import *
from product_master.views import ListPI

urlpatterns = patterns('product_master.views',
  url(r'^show_download_pim/$','show_download_pim'),
  url(r'^show_single_pim/$','show_single_pim'),
  url(r'^show_all_pims/$','show_all_pims'),
  url(r'^$', ListPI.as_view(), name='show_PIM'),
  url(r'^pim_add_update/$', 'pim_add_update'),
  url(r'^pim_update/$', 'pim_update'),
  url(r'^return_PIM/$','return_PIM'),
  )