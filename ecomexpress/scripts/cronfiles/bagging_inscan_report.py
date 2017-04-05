import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
#from django.db.models import Q
from django.conf import settings
#import reports.ecomm_mail
from reports.ecomm_mail import ecomm_send_mail
from django.core.mail import send_mail
#from django.db.models import Count
#import service_centre.models
from service_centre.models import ServiceCenter, Shipment, ShipmentStatusMaster, StatusUpdate
from reports.report_api import ReportGenerator
import datetime
from django.db.models import get_model


def ndr():
        now=datetime.datetime.now()
        #print now
        
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        #print  yesterday
        #print yesterday.day
        #print yesterday.month
        #print yesterday.year
        yday=yesterday.strftime('%Y-%m-%d')
        yday_start=yday+" 00:00:00"
        yday_end=yday+" 23:59:59"
        #print yday_start
        #print yday_end
        report = ReportGenerator('bagging_report_{0}.xlsx'.format(yesterday))
        sc=ServiceCenter.objects.all()
        monthdir = yesterday.strftime("%Y_%m")
        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
        #monthdir = upd_time.strftime("%Y_%m")
        download_list=[]
        # shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))thdir))
        for s in sc:
             hist=shipment_history.objects.using('local_ecomm').filter(updated_on__range=[yday_start,yday_end],current_sc=s)
             one_status=Shipment.objects.using('local_ecomm').filter(added_on__year=int(yesterday.year),added_on__month=int(yesterday.month),added_on__day=int(yesterday.day),pickup__service_centre=s).count()
             two_status=hist.filter(status=2).count()
             three_status=hist.filter(status=3).count()
             four_status=hist.filter(status=4).count()
             five_status=hist.filter(status=5).count()
             six_status=hist.filter(status=6).count()
             onefour_count=hist.filter(status=14).count()
             onefive_count=hist.filter(status=15).count()
             onesix_count=hist.filter(status=16).count()
             u=(s,one_status,two_status,three_status,four_status,five_status,six_status,int(onefour_count),int(onefive_count),int(onesix_count))
             download_list.append(u)
        #print shipment_history            
        #return now
        #code=92006
        col_heads=("Service Center","Soft data up loaded count","inscan operation completion","added to bag(service centre)","debag shipment(hub)","added to bag(hub)","debag shipment(delivery centre)","connected to destination(airport confirm from sc)","connected to destination(airport confirm from hub)","comments")
        report.write_header(col_heads)


        #download_list.append(u)
        path = report.write_body(download_list)
        all_mails =  ["krishnanta@ecomexpress.in","satyak@ecomexpress.in",'sanjeevs@ecomexpress.in','manjud@ecomexpress.in','sravan@ecomexpress.in','jaideeps@ecomexpress.in','jignesh@prtouch.com','onkar@prtouch.com']
        #all_mails = customer_emails_list +  ['jinesh@prtouch.com', 'onkar@prtouch.com']
    ##ndr(code)
    #file_name = generate_customer_report(code)
        file_link = settings.ROOT_URL + '/static/uploads/reports/' +path
        #ecomm_send_mail('NDR  Report '+ str(code), file_link, all_mails)
        subject = "Bagging Report for %s"%(yesterday)
        from_email = "support@ecomexpress.in"
        #to_email = ('arun@prtouch.com',"onkar@prtouch.com")
        #to_email = ("onkar@prtouch.com","sravank@ecomexpress.in","jignesh@prtouch.com")
        email_msg = "Dear Team,\n Bagging Tracking  Report for yesterday  can be access from %s"%(file_link)
        send_mail(subject,email_msg,from_email,all_mails)

ndr()
