import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from reports.ecomm_mail import ecomm_send_mail


today = datetime.date.today() - datetime.timedelta(days=1)
to_date = today.strftime('%Y-%m-%d')
from_date = today.strftime('%Y-%m-01')

from reports.bagging_report import *
file_name = generate_bagging_report(from_date, to_date)

to_email = ("jinesh@prtouch.com",  "sravank@ecomexpress.in")
file_link = "http://billing.ecomexpress.in/static/uploads/reports/" + file_name
ecomm_send_mail('Bagging Report {0}'.format(today.strftime('%Y-%m-%d')), file_link, to_email)
