import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from reports.customer_daily_shipments_count_report import generate_report
from reports.ecomm_mail import ecomm_send_attach_mail

file_name = generate_report()

#to_email =('arun@prtouch.com',)

to_email = ("pankajj@ecomexpress.in","prashanta@ecomexpress.in",
    "sanjeevc@ecomexpress.in", "Manjud@ecomexpress.in","rajivj@ecomexpress.in",
    "jaideep@prtouch.com",
    "jignesh@prtouch.com", "jinesh@prtouch.com", "onkar@prtouch.com")
ecomm_send_attach_mail("Daily Shipments Count Report", file_name, to_email)

