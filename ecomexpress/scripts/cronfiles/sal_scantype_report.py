#!/usr/bin/env python
import os
import sys

# Setup environ
os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import *
from django.core.mail import send_mail
import datetime

now = datetime.datetime.now()
before = now - datetime.timedelta(days=1)

def sal_exception():
    s = []
    sal = SALScanType.objects.filter(added_on__gte=before, scan_type=1).order_by('sc', '-added_on')
    mismatch_sal = []
    for a in sal:
        u = (a.shipment.airwaybill_number, a.sc, a.added_on, a.emp)
        mismatch_sal.append(u)
    subject = "SAL Report for shipments not entered through barcode scanner"
    if sal:
         email_msg = "Given below are shipments and their service centre:\n\nAWB \t\t\tSC \t\t Added On \t\t\t Employee\n"+"\n".join(['%s \t %s \t %s \t %s' % (a[0], a[1], a[2], a[3]) for a in mismatch_sal])
         to_email = ("ashishm@ecomexpress.in", "salima@ecomexpress.in", "praveen.joshi@ecomexpress.in","sbabaria@ecomexpress.in", "praveen.joshi@ecomexpress.in","rameshw@ecomexpress.in", "rakeshp@ecomexpress.in", "lokeshr@ecomexpress.in", "chandrashekarb@ecomexpress.in","jagbirs@ecomexpress.in", "pawant@ecomexpress.in","mohinderk@ecomexpress.in","rakeshl@ecomexpress.in", "yogeshk@ecomexpress.in", "himanshum@ecomexpress.in", "umeshm@ecomexpress.in",
                     "sanjeevs@ecomexpress.in","Sanjeev.chopra@ecomexpress.in", "geetub@ecomexpress.in","onkar@prtouch.com","jignesh@prtouch.com","sravank@ecomexpress.in","jaideeps@ecomexpress.in",
                     "pawant@ecomexpress.in", "mohinderk@ecomexpress.in",  "cs-all@ecomexpress.in", "veenav@ecomexpress.in" , "shalinia@ecomexpress.in","sandeepv@ecomexpress.in","pravinp@ecomexpress.in","deepakt@ecomexpress.in")
         from_email = "support@ecomexpress.in"
         send_mail(subject,email_msg,from_email,to_email)

sal_exception()

