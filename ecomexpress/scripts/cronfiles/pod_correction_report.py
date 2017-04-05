import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import csv

from django.db.models import get_model

from service_centre.models import *
from reports.ecomm_mail import ecomm_send_mail

def report_202():
    now = datetime.datetime.now()
    year = now.year
    month =  now.strftime("%m")
    col_heads = ("AWB No","Order No","Pickup Date",
        "Origin", "Destination","202 Updation Date", 
        "Current Status Code", "Current Status Code Updation Date")
    sh = Shipment.objects.using('local_ecomm').filter(shipper__code=11007, added_on__month=now.month, added_on__year=now.year)\
          .values_list('airwaybill_number','order_number','added_on',
            'pickup__service_centre__center_shortcode','original_dest__center_shortcode',
            'reason_code__code_description','shipext__updated_on')
    csv_out = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/reports/report202.csv","wb")
    mywriter = csv.writer(csv_out)
    dt = ("MIS Date: " + str(now.date()),)
    mywriter.writerow(dt)
    mywriter.writerow(col_heads)
    year_month = '{0}_{1}'.format(year, month)
    print year_month
    #exit(0)
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(year_month))
    print shipment_history
    for a in sh.iterator():
          hist1 = shipment_history.objects.using('local_ecomm').filter(
                shipment__airwaybill_number=a[0], reason_code__code = 202).values_list('updated_on')
          if hist1:
                 u = (a[0], a[1], a[2], a[3], a[4], hist1[0][0], a[5], a[6])
                 mywriter.writerow(u)
    to_emails = ["aakar.jain@homeshop18.com",
        "abhay.kumar@homeshop18.com", "kunal.goel@homeshop18.com", "Roshan.Kumar@network18online.com",
        "Ashok.Bisht@network18online.com", "Akhilesh.Srivastava@network18online.com", "balwinders@ecomexpress.in",
        "nandkishor@limeroad.com","sreekanth@limeroad.com", "ankush@limeroad.com",
        "sunainas@ecomexpress.in", "samar@prtouch.com", "jignesh@prtouch.com", "sravank@ecomexpress.in"]
    #to_emails = ["jinesh@prtouch.com"]
    ecomm_send_mail('Status Code 202 - Pod correction Report', 
        "http://cs.ecomexpress.in/static/uploads/reports/report202.csv", to_emails )

report_202()
