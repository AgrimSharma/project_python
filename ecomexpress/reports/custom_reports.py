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


def jk_patna_gaya_lkoships():
        now=datetime.datetime.now()
        start_date=now.strftime('%Y-%m-01 00:00:01')
        name=now.strftime('%Y-%m-%d') 
        report = ReportGenerator('jk_patna_gaya_lkoships_{0}.xlsx'.format(name))
        month=now.month
        dddyear= now.year
        col_heads=('Customer','Service Center',"Count")
        todays=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=7)
        print todays
        data=[]
        year=[2014]
        month=[]
        month=[1,2,3,4,5,6,7,8,9,10,11,12]
        ships=Shipment.objects.filter(added_on__lte=todays,status__gte=2).exclude(reason_code__in=[999,111,333]).exclude(status__in=[11,16,9]).exclude(rts_status=2)
        cust=[]
        cust=Customer.objects.filter(activation_status=True).exclude(code = 32012)
        sc=ServiceCenter.objects.filter().exclude(type=1)
        for c in cust:
            cships=ships.filter(shipper=c)
            for s in sc:
             count=cships.filter(current_sc=s)
            #for s in month:
             #count=cships.filter(shipment_date__month=s,shipment_date__year=2014)
             u=(c,s.center_shortcode,count.count())
             if count.count()<>0:
                data.append(u)
                print u
        print report
        report.write_header(col_heads)
        path = report.write_body(data)
        print path
        print "mail sent :) "
        return subject

def regionwise_cust_outbound_pickup():
    zones=[1,4,5]
    for z  in zones:
        zone=Zone.objects.get(id=z)

jk_patna_gaya_lkoships()
