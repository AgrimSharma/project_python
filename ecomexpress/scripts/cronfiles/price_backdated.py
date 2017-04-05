#!/usr/bin/env python
import os
import sys

# Setup environ
os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import *
from utils import price_updated, rts_pricing

def first_10_rts():
    sh = Shipment.objects.filter(shipment_date__gte='2013-11-01', shipment_date__lt = '2013-11-11', rts_status=1)

    for a in sh.iterator():
        rts_pricing(a)
    return True 
 
def first_20_rts():
    sh = Shipment.objects.filter(shipment_date__gte='2013-11-11', shipment_date__lt = '2013-11-21', rts_status=1)
    for a in sh.iterator():
        rts_pricing(a)
    return True


def rate_calc():
    emailmsg = ""
    a = first_10_rts()
    if a :
       emailmsg = "First 10 rts done"
    subject = "Pricing for shipment not having original destination(Original Dest Updated)"
    from_email = "support@ecomexpress.in"
    to_email = ("samar@prtouch.com")
    send_mail(subject,email_msg,from_email,to_email) 

if __name__ == '__main__':
    rate_calc()

