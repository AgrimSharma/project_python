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
from reports.views import performance_analysis_location

PROJECT_ROOT = '/home/web/ecomm.prtouch.com/ecomexpress'
root_url = 'http://ecomm.prtouch.com/'

def performance_location_report():
    #today = datetime.datetime.now().date()
    #yesterday = now - datetime.timedelta(days=1)
    file_name = performance_analysis_location(request = None, type=1) 
    send_mail('Performance Analysis Location Report',
              "Dear Team,\n Performance Analysis Location Report report has been generated. Please find the link below.\n http://cs.ecomexpress.in/static/uploads{0}\n\n".format(file_name),

              'support@ecomexpress.in', ['onkar@prtouch.com','sunainas@ecomexpress.in','sravank@ecomexpress.in','jignesh@prtouch.com', 'manjud@ecomexpress.in', 'krishnanta@ecomexpress.in', 'satyak@ecomexpress.in', 
'anila@ecomexpress.in'])
#           'support@ecomexpress.in',['samar@prtouch.com'])
if __name__ == '__main__':
    performance_location_report()
