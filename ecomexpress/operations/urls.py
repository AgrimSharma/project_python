'''
Created on Oct 19, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'operations.views',
    url(r'^list/$','consolidated_bags', name='cbags'),
    url(r'^dashboard/$','dashboard', name='cbags'),
    url(r'^cbag/create/$','create_consolidated_bag', name='create-cbag'),
    url(r'^cbag/include_bag/$','cbag_include', name='cbag-include'),
    url(r'^cbag/remove_bag/$','cbag_remove', name='cbag-remove'),
    url(r'^cbag/details/$','cbag_details', name='cbag-details'),
    url(r'^cbag/close/$','cbag_close', name='cbag-close'),
    url(r'^cbag/inscan/$','cbag_inscan', name='cbag-inscan'),
)
