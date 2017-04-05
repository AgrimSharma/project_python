import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import calendar
import datetime
from django.db.models import Q
from django.conf import settings
from reports.ecomm_mail import ecomm_send_mail
from django.core.mail import send_mail
#from django.db.models import Count
from customer.models import Customer
from service_centre.models import *
from reports.report_api import ReportGenerator
import datetime
from django.db.models import get_model
from dateutil.relativedelta import relativedelta
#from reports.customer_emails import customer_emails_dict





def get_address(awb):
    a=Shipment.objects.get(airwaybill_number=awb)
    address=""
    if a.consignee_address1 is not None:
       address=address+a.consignee_address1
    if a.consignee_address2 is not None:
       address=address+a.consignee_address2
    if a.consignee_address3 is not None:
       address=address+a.consignee_address3
    if a.consignee_address4 is not None:
      address=address+a.consignee_address4
    return address


