'''
Created on Oct 22, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('security.views',
                       url(r'^$','security'), 
                       url(r'^read_remarks/$', 'read_remarks'),
		       url(r'^add_remarks/$', 'add_remarks'),
		       url(r'^download_xcl/$', 'download_xcl'),
		       url(r'^add_remarks_details/$', 'add_remarks_details'),
)

