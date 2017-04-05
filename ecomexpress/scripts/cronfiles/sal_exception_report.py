#!/usr/bin/env python
import os
import sys

# Setup environ
os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import *
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
import datetime

now = datetime.datetime.now()
before = now - datetime.timedelta(days=1)

def sal_exception():
    s = []
    sal = ShipmentAtLocation.objects.filter(date__gte=before).order_by('-date', 'status')
    mismatch_sal = []
    for a in sal:
        if a.status == 0:
             stat = "Not Closed\t"
        elif a.status == 1:
             stat = "Closed\t"
        elif a.status == 2:
             stat = "%s/%s\t"%(len(a.scanned_shipments.all()),len(a.total_undelivered_shipment.all()))
        u = (a.id, a.date, stat, a.origin)
        s.append(a.origin_id)
        mismatch_sal.append(u)
    sc = ServiceCenter.objects.filter().exclude(id__in=s)
    for a in sc:
        u = ("", "", "SAL Not Created", a)
        mismatch_sal.append(u)
#    mismatch_sal=mismatch_sal.sort(  
    subject = "Exception Report for SAL - test"
    if sal:
         email_msg = "Given below are the mismatch SAL id and their service centre:\n\nSAL ID \tDate \t\t Status \t\t \t SC\n"+"\n".join(['%s \t %s \t %s \t  %s' % (a[0], a[1], a[2], a[3]) for a in mismatch_sal])
       # email_msg = "<html><body>Following airwaybill were not verified into the system:<br><table><tr><th>Air Waybill Number</tr></th></table></body></html>"
         to_email = (
	     "ruchin.sodhani@ecomexpress.in",
             "pravinp@ecomexpress.in",
	     "salima@ecomexpress.in",
             "sandeepv@ecomexpress.in",
             "ashishm@ecomexpress.in", 
             "pawant@ecomexpress.in", 
             "jinesh@prtouch.com", 
             "jignesh@prtouch.com", 
             "sravank@ecomexpress.in",
             "jagbirs@ecomexpress.in", 
             "narenders@ecomexpress.in",
             "jaideeps@ecomexpress.in", 
             "rameshw@ecomexpress.in", 
             "lokeshr@ecomexpress.in", 
             "lokanathanm@ecomexpress.in", 
             "sanjeevs@ecomexpress.in", 
             "chandrashekarb@ecomexpress.in")
         from_email = "support@ecomexpress.in"
         send_mail(subject,email_msg,from_email,to_email)

sal_exception()

