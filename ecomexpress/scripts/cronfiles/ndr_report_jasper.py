import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from service_centre.models import Customer
from reports.ndr import *
from reports.customer_emails import customer_emails_dict

def main():
     #cust=Customer.objects.all()
     #cust = customer_emails_dict.keys()
     #cust.remove(92006)
     #for c in cust:
     ndr(92006)
     #return "done"
main()
