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
from location.models import City
from service_centre.models import ServiceCenter, Shipment, ShipmentStatusMaster, StatusUpdate
from reports.report_api import ReportGenerator
import datetime
from service_centre.models import *
from django.db.models import get_model
from dateutil.relativedelta import relativedelta
#from reports.customer_emails import customer_emails_dict
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from django.core.mail import EmailMultiAlternatives
from service_centre.models import *
from datetime import date,timedelta,datetime
import calendar
import datetime

def outscan_report():
        now=datetime.datetime.now()
        start_date=now.strftime('%Y-%m-01 00:00:00')
        name=now.strftime('%Y-%m-%d') 
        col_heads=('City','Service Center',"Total Outscan","Delivered","undelivered")
        message='<html><body><p>Dear Team,</p><p>NCR,Mumbai and Bangalore Outscan Report <p>Summary of report follows</p><table  border="1" cellpadding="10"  cellspacing="0"><tr><th>City</th><th>Service Center</th><th>Total Outscan</th><th>Delivered</th><th>% Delivered</th><th>Undelivered</th><th>% Undelivered</th><th>Month to date Outscan</th><th>Month to date Undelivered</th></tr>'
        yday=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=1)
        #print yday
        data=[]
        #city=[12,1,38]
        zone=[4,8,7]        
        d2=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(seconds=1)
        #d2=d2.strftime('%Y-%m-%d')
        #print d2
        #ds=d2.split('-')
        #year=ds[0]
        #day=ds[2]
        #month=ds[1]
        total_deli=0
        total_undeli=0
        gt_total=0
        mtd_total=0
        mtd_undeli_total=0
        for z in zone:
         zone=Zone.objects.get(id=z)
         city=City.objects.filter(zone=zone)
         city_total=0
         city_deli=0
         city_mtd=0
         city_undeli_mdt=00
         for c in city:
           sc=ServiceCenter.objects.filter(city=c).exclude(type=1).exclude(id=194)
           for s in sc:
                awbs=[]
                deli_awbs=[]
                undeli_awbs=[]
                           #23may changes  start#
                #print "dates are",yday,d2i
                #d2="2014-05-01 23:59:59"
                #print "daily range",yday,d2
                #print "dates are",yday,d2,start_date
                mtd_awbs=[]
                mtd_deli=[]
                mtd_dos=DeliveryOutscan.objects.filter(added_on__range=(start_date,name),origin=s)
                for m in mtd_dos:
                    mtd_totals=DOShipment.objects.filter(deliveryoutscan=m)
                    mtd_deli_total=DOShipment.objects.filter(status=1,deliveryoutscan=m)   
                    for a1 in mtd_totals:
                           mtd_awbs.append(a1.shipment.airwaybill_number)
                    for a2 in mtd_deli_total:
                           mtd_deli.append(a2.shipment.airwaybill_number)
                print "mtd data",len(list(set(mtd_awbs))),len(list(set(mtd_deli))),s
                #print Shipment.objects.filter(added_on__range=(start_date,d2),original_dest=s,status=9).exclude(rts_status=2).count()
                #mtd_ships=Shipment.objects.filter(added_on__range=(start_date,d2),original_dest=s,status__gte=7).exclude(rts_status=2).count()
                #mtd_undeli_ships=Shipment.objects.filter(added_on__range=(start_date,d2),service_centre=s,status=8).exclude(rts_status=2).exclude(reason_code_id__in=[111, 777, 999, 888, 333, 310]).count()
                #print mtd_ships,mtd_undeli_ships,s
                #return "hi"
                ot=DeliveryOutscan.objects.filter(added_on__range=(start_date,d2),origin=s)                 
                  #23 may changse end here #
                #ot=DeliveryOutscan.objects.filter(added_on__range=(yday,d2),origin=s)
                for o in ot:
                    deli=DOShipment.objects.filter(status=1,deliveryoutscan=o)
                    undel=DOShipment.objects.filter(deliveryoutscan=o).exclude(status=1)
                    total=DOShipment.objects.filter(deliveryoutscan=o)
                    #print "total is ",total.count()
                    for d in total:
                             awbs.append(d.shipment.airwaybill_number)
                    for d in undel:
                             undeli_awbs.append(d.shipment.airwaybill_number)
                    for d in deli:
                             deli_awbs.append(d.shipment.airwaybill_number)

                    #total_deli=total_deli+deli.count()
                    #total_undeli=total_undeli+undel.count()
                    #gt_total=gt_total+total.count()
                #total_deli = StatusUpdate.objects.filter(added_on__year=year, added_on__day=day, added_on__month=month,origin=s, status=2).count()
                #total_undeli = StatusUpdate.objects.filter(added_on__year=year, added_on__day=day, added_on__month=month,origin=s).exclude( status=2).count()
                #gt_total=StatusUpdate.objects.filter(added_on__year=year, added_on__day=day, added_on__month=month,origin=s).count()
                #print c,s,total_deli,total_undeli,gt_total
                #print len(awbs),len(deli_awbs),len(undeli_awbs)
                total=len(list(set(awbs)))
                deli_count=len(list(set(deli_awbs)))
                undeli_count=total-deli_count
                if total<>0:
                  deli_perc=float((deli_count)/float(total))*100.00
                  deli_perc=round(deli_perc,2)
                  undeli_perc=100-deli_perc
                else:
                  deli_perc=0
                  undeli_perc=0
                gt_total=gt_total+total
                total_deli=deli_count+total_deli
                total_undeli=total_undeli+undeli_count
                city_total=city_total+total
                city_deli=city_deli+deli_count
                city_undeli_mdt=city_undeli_mdt+len(mtd_awbs)-len(mtd_deli)
                print "len of mtd",len(mtd_awbs)
                print mtd_awbs    
                mtd_total=mtd_total+len(mtd_awbs)
                mtd_undeli_total=len(mtd_awbs)-len(mtd_deli)
                city_mtd=city_mtd+len(mtd_awbs)
                print "mtd_ttoal is ",mtd_total,"mtd undeli",mtd_undeli_total
                print c,'\t',s,'\t',total,'\t',deli_count,'\t',deli_perc,'\t',undeli_count,'\t',undeli_perc,gt_total,total_deli
                message=message+'<tr><td>'+c.city_name+'</td><td>'+str(s.center_shortcode)+'</td><td>'+str(total)+'</td><td>'+str(deli_count)+'</td><td>'+str(deli_perc)+'</td><td>'+str(undeli_count)+'</td><td>'+str(undeli_perc)+'</td><td>'+str(mtd_total)+'</td><td>'+str(mtd_undeli_total)+'</td></tr>'
           print c,city_deli,city_total
         city_undeli=city_total-city_deli
         if city_total<>0:
             city_perc=float(city_deli)/float(city_total)*100.00
         else:
             city_perc=0
         city_perc=round(city_perc,2)
         city_undeli_perc=100-city_perc
         zone=Zone.objects.get(id=z)
         name=zone.zone_name
         message=message+'<tr><td><b>'+name+'</b></td><td><b>'+'TOTAL'+'<b></td><td><b>'+str(city_total)+'</b></td><td><b>'+str(city_deli)+'</b></td><td><b>'+str(city_perc)+'</b></td><td><b>'+str(city_undeli)+'</b></td><td><b>'+str(city_undeli_perc)+'</b></td><b>'+str(city_mtd)+'</b></td><td><b>'+str(city_undeli_mdt)+'</b></td></tr>'
        print total_deli,gt_total
        if gt_total<>0:
           deli_perc=float((total_deli)/float(gt_total))*100.00
        else:
           deli_perc=0
        deli_perc=round(deli_perc,2)
        undeli_perc=100-deli_perc
        message=message+'<tr><td>'+""+'</td><td>'+'Grand Total'+'</td><td>'+str(gt_total)+'</td><td>'+str(total_deli)+'</td><td>'+str(deli_perc)+'</td><td>'+str(total_undeli)+'</td><td>'+str(undeli_perc)+'</td><td>'+str(mtd_total)+'</td><td>'+str(mtd_undeli_total)+'</td></tr>'
        message=message+"</table><p>Regards</p><p>Support Team</p></body></html>"
        print message
        msg = MIMEMultipart()
        msg['From'] = "Reports <support@ecomexpress.in>"
        s1 = smtplib.SMTP('i.prtouch.com', 26)
        #to_mail_ids=["krishnanta@ecomexpress.in","satyak@ecomexpress.in",'sanjeevs@ecomexpress.in','manjud@ecomexpress.in','sravan@ecomexpress.in','jaideeps@ecomexpress.in',"onkar@prtouch.com",'theonkar@gmail.com']
        to_mail_ids=['onkar@prtouch.com','theonkar10@gmail.com','samar@prtouch.com']
        email_msg=message
        html =message
        text =("Dear Team, \nPlease find NCR,Bangalore,Mumbai Outscan  Report. \n\nRegards\n\nSupport Team\n total=%s"%(message))
        msg = EmailMultiAlternatives('NCR,Bangalore,Mumbai Outscan  report', text, msg['from'], to_mail_ids)
        msg.attach_alternative(html, "text/html")
        #msg.attach(attach)
        msg.send()

        print "mail sent :) "
        return "hi"



outscan_report()
