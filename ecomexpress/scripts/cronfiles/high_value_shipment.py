import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import *
from reports.views import *
import settings

import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives


import datetime

now = datetime.datetime.now()
before = now - datetime.timedelta(days=1)
request = None

high_val = high_value_shipments(request)
f = open(high_val,"r")
high_val_content = f.read()
f.close()
filename = high_val.split('uploads/')
attach = MIMEApplication(high_val_content, 'xlsx')
attach.add_header('Content-Disposition', 'attachment', filename = filename[1])
to_email = ("krishnanta@ecomexpress.in", "satyak@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in", "sravank@ecomexpress.in", "onkar@prtouch.com", "jignesh@prtouch.com")
s = smtplib.SMTP('i.prtouch.com', 26)
for a in to_email:
    msg = MIMEMultipart()
    msg['Subject'] = 'High Value Shipments Report'
    msg['From'] = "Reports <jignesh@prtouch.com>"
    plain_test_part = MIMEText("Dear Team, \nPlease find  attached High Value Shipments Report. \n\nRegards\n\nSupport Team", 'plain')
    msg.attach(plain_test_part)
    msg.attach(attach)
    msg['To']=a
    s.sendmail(msg['From'] , msg['To'], msg.as_string())
s.quit()
