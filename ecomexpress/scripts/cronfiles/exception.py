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

def exception():
    s = []
    sh = Shipment.objects.filter(date__gte=before, status__gte=2).order_by('product_type', 'inscan_date')
    mismatch = []
    for a in sh:
        if a.order_price_set.filter.count() > 1:
             s.append(a)
    subject = "Duplicate pricing calculation"
    if mismatch:
         email_msg = "Given below are airwaybills whose pricing was calculated more than once:\n\nAWB"+"\n".join(['%s' % (a for a in mismatch])
         to_email = ("onkar@prtouch.com", "jignesh@prtouch.com")
         from_email = "support@ecomexpress.in"
        # send_mail(subject,email_msg,from_email,to_email)

exception()

