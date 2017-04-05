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
print now,"ND",before
msr = monthly_awb_sales_report(request, before.strftime('%Y%m%d'), 2)
print msr
msr_split = msr.split('/ecomexpress')
msr_path = 'http://billing.ecomexpress.in'+msr_split[1]
print msr_path
subject = "Monthly Sales Report"
email_msg = "Please find the link below for today`s MSR \n %s"%(msr_path)
to_email = ("samar@prtouch.com",)
#to_email = ("satyak@ecomexpress.in", "jaideeps@ecomexpress.in", "nareshb@ecomexpress.in", "jitendrad@ecomexpress.in", "jignesh@prtouch.com", "onkar@prtouch.com", "jinesh@prtouch.com")
#to_email = ("samar@prtouch.com",)
from_email = "support@ecomexpress.in"
send_mail(subject,email_msg,from_email,to_email)
 
