import datetime
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')


from reports.ecomm_mail import ecomm_send_mail
from reports.pickup_report import pickup_report

today = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
file_name = pickup_report(today, today, cust_id=None, origin_id=None)

to_email = ("jinesh@prtouch.com", "sravank@ecomexpress.in")
file_link = settings.ROOT_URL + 'static/uploads/reports/' + file_name
ecomm_send_mail('Pickup Report', file_link, to_email)
