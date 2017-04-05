import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from reports.ecomm_mail import ecomm_send_mail
from reports.sales_comparison_report_without_rev import SalesComparisonReport 

#from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives


from django.core.mail import send_mail
import datetime
from billing.misc_reports import write_sales_comparison_to_excel

today = datetime.datetime.today() - datetime.timedelta(days=1)
date_str = today.strftime('%Y-%m-%d')
#file_name = write_sales_comparison_to_excel(date_str)
report = SalesComparisonReport(date_str)
file_name = report.generate_excel()

fpath = 'http://billing.ecomexpress.in/static/uploads/reports/'+file_name

f = open('/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/reports/' + file_name,"r")
file_content = f.read()
f.close()

attach = MIMEApplication(file_content, 'xlsx')
attach.add_header('Content-Disposition', 'attachment', filename=file_name)

s1 = smtplib.SMTP('i.prtouch.com', 26)

to_email = ("jinesh@prtouch.com", "sunainas@ecomexpress.in","jaideeps@ecomexpress.in","arun@prtouch.com")
for mail in to_email:
    msg = MIMEMultipart()
    msg['Subject'] = 'Sales Comparison Report'
    msg['From'] = "Reports <jignesh@prtouch.com>"
    plain_test_part = MIMEText("Dear Team, \nPlease find  attached Sales Comparison Report. \n\nRegards\n\nSupport Team", 'plain')
    msg.attach(plain_test_part)
    msg.attach(attach)
    msg['To']=mail
    s1.sendmail(msg['From'] , msg['To'], msg.as_string())
s1.quit()

