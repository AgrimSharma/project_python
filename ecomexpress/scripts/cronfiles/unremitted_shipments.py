import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from django.conf import settings
from reports.unremitted_shipments_report import generate_report_for_all_customers
from reports.ecomm_mail import ecomm_send_mail

def main():
    yester_day = datetime.date.today() - datetime.timedelta(days=1)
    date_to = yester_day.strftime('%Y-%m-%d')

    reports = generate_report_for_all_customers(date_to)
    reports_list = [settings.ROOT_URL + 'static/uploads/reports/'+file_name for file_name in reports]
    reports_list_str = '\n'.join(reports_list)
    to_email = ("jinesh@prtouch.com", "nareshb@ecomexpress.in", "samar@prtouch.com",
                      "jignesh@prtouch.com", "karishmar@ecomexpress.in", "murarikp@ecomexpress.in")
    #to_email = ("jinesh@prtouch.com", "samar@prtouch.com")
    ecomm_send_mail('Unremitted Shipments Report', reports_list_str, to_email)

main()
