import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

#from reports.sunday_delivery import generate_sunday_report
from reports.daily_delivery import generate_sunday_report
from reports.ecomm_mail import ecomm_send_mail

import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import csv
from zipfile import ZipFile
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
#

def main():
    today = datetime.date.today()

    file_name = generate_sunday_report()
    fname = file_name
    f = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/reports/"+file_name,"r")
    file_name = "http://billing.ecomexpress.in/static/uploads/reports/"+str(file_name)

    msg = MIMEMultipart()

    dc_report = f.read()
    f.close()
    
    attach = MIMEApplication(dc_report, 'xlsx')
    attach.add_header('Content-Disposition', 'attachment', filename = ''+fname+ '')
    msg = MIMEMultipart()
    msg['From'] = "Reports <support@ecomexpress.in>"
    s1 = smtplib.SMTP('i.prtouch.com', 26)
    to_mail_ids = ("krishnanta@ecomexpress.in", "satyak@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in", "jitendrad@ecomexpress.in", "jaideeps@ecomexpress.in", "jinesh@prtouch.com", "nareshb@ecomexpress.in", "arun@prtouch.com", "sravan@ecomexpress.in")
    msg = EmailMultiAlternatives('DC Daily Delivery Report', "Dear All\n, Please find Report attached with this mail.\nRegs\nSupport", msg['from'], to_mail_ids)
    #msg.attach_alternative(message, "text/html")
    msg.attach(attach)
    msg.send()




#    print file_name
    #to_email = ("krishnanta@ecomexpress.in", "satyak@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in", "jitendrad@ecomexpress.in", "jaideeps@ecomexpress.in", "jinesh@prtouch.com", "nareshb@ecomexpress.in", "arun@prtouch.com", "sravan@ecomexpress.in")
#    to_email = ("arun@prtouch.com","jinesh@prtouch.com")
    #ecomm_send_mail('DC Daily Delivery Report', file_name, to_email)

main()
