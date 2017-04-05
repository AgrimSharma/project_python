import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Count, Sum
from django.core.mail import send_mail
from service_centre.models import Shipment, DeliveryOutscan
from reports.views import ageing_sop

PROJECT_ROOT = '/home/web/ecomm.prtouch.com/ecomexpress'
root_url = 'http://ecomm.prtouch.com/'

def ageing_sop_report():
    #today = datetime.datetime.now().date()
    #yesterday = now - datetime.timedelta(days=1)
    file_name = ageing_sop(request = None, type=1) 
    send_mail('Ageing SOP Report',
              "Dear Team,\n Ageing SOP report has been generated. Please find the link below.\n http://cs.ecomexpress.in/static/uploads{0}\n\n".format(file_name),
              'support@ecomexpress.in', ['nitashaa@ecomexpress.in','onkar@prtouch.com','veenav@ecomexpress.in','shalinia@ecomexpress.in','sunainas@ecomexpress.in','sravank@ecomexpress.in','jignesh@prtouch.com','sandeepv@ecomexpress.in','pravinp@ecomexpress.in','pawant@ecomexpress.in','mohinderk@ecomexpress.in','deepakt@ecomexpress.in'])
 #             'support@ecomexpress.in', ['samar@prtouch.com',])
#           'support@ecomexpress.in',['samar@prtouch.com'])
if __name__ == '__main__':
    ageing_sop_report()
