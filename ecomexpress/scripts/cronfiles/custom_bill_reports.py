import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from django.core.mail import send_mail

from billing.generate_bill_reports import generate_awbexcel_report


def main():
    path = generate_awbexcel_report(543)
    msg = path
    send_mail('Billing report', msg, 'jignesh@prtouch.com',
                  ('jinesh@prtouch.com', 'samar@prtouch.com')) #'jaideeps@ecomexpress.in'))

if __name__ == "__main__":
    main()
