import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
import datetime
from django.core.mail import send_mail

from reports.noinfo_report import generate_noinfo_report

if __name__ == '__main__':
    today = (datetime.datetime.today() - datetime.timedelta(days=60)).strftime('%Y-%m-%d')
    file_name = generate_noinfo_report(0, today, today)
    print file_name
    send_mail('No-info Report',
              """Dear Team,\n Noinfo Report report has been generated. Please find the link below.\n 
              http://billing.ecomexpress.in/static/uploads/reports/{0}\n\n""".format(file_name),
           #   'support@ecomexpress.in', ['samar@prtouch.com','jinesh@prtouch.com','sravank@ecomexpress.in','jignesh@prtouch.com'])
              'support@ecomexpress.in', ['samar@prtouch.com',])

