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
from service_centre.models import ServiceCenter, Shipment, ShipmentStatusMaster, StatusUpdate
from reports.report_api import ReportGenerator
import datetime
from django.db.models import get_model
from dateutil.relativedelta import relativedelta
#from reports.customer_emails import customer_emails_dict


def return_shipments():
        now=datetime.datetime.now()
        start_date=now.strftime('%Y-%m-01 00:00:01')
        name=now.strftime('%Y-%m-%d') 
        report = ReportGenerator('reverse_ships_{0}.xlsx'.format(name))
        month=now.month
        year= now.year
        col_heads = ("Air Waybill No","Order No", "Item Desctiption", "Added On", "Origin", "Destination", "Shipper", "Consignee", "Collectable Value", "Declared Value", "Reason code", "Reason","Reverse Charge","RTO Charge","SDD Charge","SDL Charge","VCHC CHarge","COD Charge","Freight Charge","Fuel Surcharge")
        data = list(Shipment.objects.using('local_ecomm')\
               .filter(added_on__month=month,added_on__year=year,reverse_pickup=True)\
               .values_list('airwaybill_number', 'order_number', 'item_description', 'added_on', 'pickup__service_centre__center_name', 'original_dest__center_name', 'shipper__name', 'consignee', 'collectable_value', 'declared_value', 'reason_code__code', 'reason_code__code_description','order_price__reverse_charge','order_price__rto_charge','order_price__sdd_charge','order_price__sdl_charge','order_price__valuable_cargo_handling_charge','codcharge__cod_charge','order_price__freight_charge','order_price__fuel_surcharge'))
        report.write_header(col_heads)
        path = report.write_body(data)
        #return path
        #print name
        #report = ReportGenerator('ndr_report_{0}.xlsx'.format(name))
        #print customer_emails_list
        #all_mails=['theonkar10@gmail.com','onkar@prtouch.com']
        all_mails =   ['rajivj@ecomexpress.in','prashanta@ecomexpress.in','onkar@prtouch.com']
        file_link = settings.ROOT_URL + 'static/uploads/reports/' +path
        subject = "Reverse  ships  Report for this month"
        from_email = "support@ecomexpress.in"
        email_msg = " Dear Team,\nReverse shipment Report can be access from %s"%(file_link)
        send_mail(subject,email_msg,from_email,all_mails)
        print "mail sent :) "
        return subject



return_shipments()
