'''
Created on Oct 19, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *
from shacti_api  import views
from privateviews.decorators import login_not_required
urlpatterns = patterns('',
                       #url(r'^$','index'),
                       #url(r'^get_pincodes/$','get_pincodes'),
                       url(r'^update_weight/$',login_not_required(views.add_to_history)),
                       url(r'^api/$','add_to_history'),
                       #url(r'^pincodes/$',views.get_pincodes),
                       url(r'success_csv/$',login_not_required(views.success_csv)),
                       url(r'failed_csv/$',login_not_required(views.failed_csv)),
)
