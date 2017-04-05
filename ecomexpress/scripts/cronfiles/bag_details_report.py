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
from reports.report_api import ReportGenerator

import datetime

now = datetime.datetime.now()
before = now - datetime.timedelta(days=1)
request = None

bags = Bags.objects.filter(added_on__gte = before, added_on__lt = now, bag_status__gte=1)
report = ReportGenerator('bag_details_report-{0}.xlsx'.format(now.strftime('%Y-%m-%d'))
file_path = str(settings.FILE_UPLOAD_TEMP_DIR) + '/reports/' + str(report)
report.write_header(('Bag No', 'Hub', 'Dest', 'Runcode' , 'Flight num' ,'Flight Departure' ,'DC Inscan' ,'no of Shipments' ))
for b in bags:
    con = b.connection_set.all().order_by("-added_on")
    row_list =[]
    if con:
        con = con[0]
        print con
    else:
        con = ""
    if con:
        runcode = con.runcode_set.all()
    else: runcode=[]
    if runcode: 
        runcode = runcode[0]
        runcode_id = runcode.id
    else: 
        runcode = ""
        runcode_id = ""
    row_list =[b.id,b.hub, b.destination, runcode_id]
    if runcode:
        for ac in runcode.airportconfirmation_set.all():
            row_list.append(ac.flight_num)
    if runcode:    
        for ac in runcode.airportconfirmation_set.all():
            row_list.append(ac.atd)
    row_list.append(b.updated_on)
    row_list.append(b.ship_data.count())
    report.write_row(row_list)

file_name = report.manual_sheet_close()
path = 'http://billing.ecomexpress.in/static/uploads/reports/'+file_name
subject = "Bag Details"
email_msg = "Please find the link below for today`s Bag Report \n %s"%(path)
to_email = ("jaideeps@ecomexpress.in",  "jignesh@prtouch.com", "onkar@prtouch.com", "jinesh@prtouch.com")
#to_email = ("arun@prtouch.com","jinesh@prtouch.com")
from_email = "support@ecomexpress.in"
send_mail(subject,email_msg,from_email,to_email)


