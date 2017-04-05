import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Count, Sum
from django.core.mail import send_mail
from service_centre.models import Shipment, DeliveryOutscan
from reports.views import outscan_performance_report

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText


def del_perf_report():
    request = None
    file_name = outscan_performance_report(request, 1, 1)
    full_path = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/'+file_name
    f = open(full_path, "r")
#    to_mail_ids = ("samar@prtouch.com",)
    to_mail_ids = ("onkar@prtouch.com","prashanta@ecomexpress.in",'sanjeevs@ecomexpress.in', 'jaideeps@ecomexpress.in', 
                    'jignesh@prtouch.com', 'sravank@ecomexpress.in', 'sunainas@ecomexpress.in',
                    'rakeshl@ecomexpress.in','praveen.joshi@ecomexpress.in','rajivj@ecomexpress.in', 
                    'balwinders@ecomexpress.in','vedprakash@ecomexpress.in','Jyotirmayc@ecomexpress.in')
    subject = 'Delivery Attempt Report - EBS' 
    file_content = f.read()
 
    attach = MIMEApplication(file_content, 'xls')
    attach.add_header('Content-Disposition', 'attachment', filename=file_name)

    s1 = smtplib.SMTP('i.prtouch.com', 26)
    for mail in to_mail_ids:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = "Reports <support@ecomexpress.in>"
        plain_test_part = MIMEText("Dear Team, \nPlease find the attached Report. \n\nRegards\n\nSupport Team", 'plain')
        msg.attach(plain_test_part)
        msg.attach(attach)
        msg['To']=mail
        s1.sendmail(msg['From'] , msg['To'], msg.as_string())
    s1.quit()
    return True

    #ecomm_send_attach_mail('Delivery Attempt Report - EBS', opr, 'samar@prtouch.com')
  #  send_mail('Delivery Attempt Report - EBS',
   #           "Dear Team,\n Delivery attempt report has been generated. Please find the link below.\n http://billing.ecomexpress.in/static/uploads{0}\n\n".format(opr),
    #          'support@ecomexpress.in', ['samar@prtouch.com', 'sanjeevs@ecomexpress.in', 'jaideeps@ecomexpress.in', 'jignesh@prtouch.com'])
#           'support@ecomexpress.in',['samar@prtouch.com'])
if __name__ == '__main__':
    del_perf_report()
