import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import *
from billing.views import *

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

pdsr = previous_day_sales_report(request, before.strftime('%Y%m%d'), 2)
f = open(pdsr,"r")
pdsr_content = f.read()
f.close()
filename = pdsr.split('uploads/')
attach = MIMEApplication(pdsr_content, 'xlsx')
attach.add_header('Content-Disposition', 'attachment', filename = filename[1])
#msg = MIMEMultipart()
#msg['Subject'] = 'Previous Day Sales Report'
#msg['From'] = "Reports <reports@prtouch.com>"
#to_email = ("samar@prtouch.com", "jignesh@prtouch.com", "krishananta@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in", "satyak@ecomexpress.in", "jitendrad@ecomexpress.in", "jaideeps@ecomexpress.in")
to_email = ("prashanta@ecomexpress.in","samar@prtouch.com", "jignesh@prtouch.com", "krishananta@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in", "satyak@ecomexpress.in", "jitendrad@ecomexpress.in", "jaideeps@ecomexpress.in")
#to_email = ("samar@prtouch.com", "jignesh@prtouch.com")
#plain_test_part = MIMEText("Dear Team, \nPlease find  attached Previous Day Sales Report. \n\nRegards\n\nSupport Team", 'plain')
#msg.attach(plain_test_part)
#msg.attach(attach)
s = smtplib.SMTP('localhost')
for a in to_email:
    msg = MIMEMultipart()
    msg['Subject'] = 'Previous Day Sales Report'
    msg['From'] = "Reports <jignesh@prtouch.com>"
    plain_test_part = MIMEText("Dear Team, \nPlease find  attached Previous Day Sales Report. \n\nRegards\n\nSupport Team", 'plain')
    msg.attach(plain_test_part)
    msg.attach(attach)
    msg['To']=a
    s.sendmail(msg['From'] , msg['To'], msg.as_string())
s.quit()

