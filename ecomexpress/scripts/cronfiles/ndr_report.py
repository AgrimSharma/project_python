import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from service_centre.models import Customer
from reports.ndr import ndr
from reports.customer_emails import customer_emails_dict

def main():
     cust = customer_emails_dict.keys()
     cust.remove(92006)
     for c in cust:
          ndr(int(c))
     return "done"
main()
