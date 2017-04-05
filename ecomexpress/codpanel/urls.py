'''
Created on 2015-04-28

@author: Jinesh
'''
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'codpanel.views',
    url(r'^$','cod_panel', name='codpanel'),
    url(r'^trackme/$', 'trackme', 
        name='codpanel-trackme'),
    url(r'^remove_coddeposit/$', 'remove_coddeposit'),
    url(r'^coddeposit_shipments/$', 'coddshipments'),
    url(r'^report_search/$', 'report_search'),
    url(r'^show_report_form/$', 'show_report_form'),
    url(r'^submit_origin_report_form/$', 'submit_origin_report_form'),
    url(r'^excel_download/$', 'excel_download'),
    url(r'^ledger_name/$', 'ledger_name'),
)
