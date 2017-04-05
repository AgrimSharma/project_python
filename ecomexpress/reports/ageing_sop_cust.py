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


def ageing_sop_Location():
        now=datetime.datetime.now()
        name=now.strftime('%Y-%m-%d') 
        report = ReportGenerator('ageingsop_cust_ships_{0}.xlsx'.format(name))
        data=[]
        message='<html><body><p>Dear Team,</p><p>Ageing SOP Customerwise report <p>Summary of report follows</p><table  border="1" cellpadding="10"  cellspacing="0"><tr><th>Customer</th><th>7-10 Days</th><th>10-20 days</th><th>20-30 days</th><th>30+ days</th></tr>'
        #cust=Customer.objects.filter().exclude(code = 32012)
        cust=Customer.objects.filter(activation_status=True).exclude(code = 32012)
        report = ReportGenerator('ageingsop_cust_wise_20days{0}.xlsx'.format(name))
        sevendays=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=6)-datetime.timedelta(seconds=1)
        tendays=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=10)
        twentydays=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=20)
        thirtydays=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=30)
        print "7 days",sevendays,"10 days",tendays,"20 days",twentydays,"30 days",thirtydays
        print datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=7)-datetime.timedelta(seconds=1)
        #return "hello"
        #cust=Customer.objects.filter(code=92006)
        data=[]
        sd=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=7)
        for c in cust:
              totalcount=sevendayships=Shipment.objects.filter(added_on__range=("2014-01-01",sevendays),shipper=c,status__lte=8).exclude(status__in=[11,16,9]).exclude(reason_code__code__in=[200,310,888,999,777,111,333]).exclude(reason_code_id=1).exclude(rts_status=2)              
              #print tendays,sevendays
              sevendayships=Shipment.objects.filter(added_on__range=(tendays,sevendays),shipper=c,status__lte=8).exclude(status__in=[11,16,9]).exclude(reason_code__code__in=[200,310,888,999,777,111,333]).exclude(reason_code_id=1).exclude(rts_status=2)
              tendays=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=10)-datetime.timedelta(seconds=1)
              #print twentydays,tendays
              tendayships=Shipment.objects.filter(added_on__range=(twentydays,tendays),shipper=c,status__lte=8).exclude(reason_code__code__in=[200,310,888,999,777,111,333]).exclude(status__in=[11,16,9]).exclude(rts_status=2).exclude(reason_code_id=1)
              twentydays=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=20)-datetime.timedelta(seconds=1)              
              #print thirtydays,twentydays
              twentydayships=Shipment.objects.filter(added_on__range=(thirtydays,twentydays),shipper=c,status__lte=8).exclude(rts_status=2).exclude(reason_code__code__in=[200,310,888,999,777,111,333]).exclude(status__in=[11,16,9]).exclude(reason_code_id=1)
              thirtydays=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=30)-datetime.timedelta(seconds=1)
              #print thirtydays
              thirtydayships=Shipment.objects.filter(added_on__range=("2014-01-01",thirtydays),shipper=c,status__lte=8).exclude(rts_status=2).exclude(reason_code_id=1).exclude(reason_code__code__in=[200,310,888,999,777,111,333]).exclude(status__in=[11,16,9])
              #print c,"7 days",sevendayships,"10 days",tendayships,"10 days ",twentydayships,"30 +",thirt
              #return "hi"
              sevendayscount=sevendayships.count()
              tendayscount=tendayships.count()
              twentydayscount=twentydayships.count()
              thirtydayscount=thirtydayships.count()
              print c,"7 days",sevendayscount,"10 days",tendayscount," 20 days",twentydayscount," 30 days",thirtydayscount,"total",totalcount.count()
              if(sevendayscount<>0 or tendayscount<> 0 or twentydayscount<>0 or thirtydayscount<>0):
                 message=message+'<tr><td>'+c.name+'</td><td>'+str(sevendayscount)+'</td><td>'+str(tendayscount)+'</td><td>'+str(twentydayscount)+'</td><td>'+str(thirtydayscount)+'</td></tr>'
                 #u=(c,sevendayships,tendayships,twentydayships,thirtydayships)
                 #data.append(u)
        #sevendayships=Shipment.objects.filter(shipper__activation_status=True,added_on__range=(tendays,sevendays),status__lte=8).exclude(shipper__code = 32012).exclude(reason_code__code__in=[200,310,888,999,777,111,333]).exclude(reason_code_id=1).exclude(rts_status=2).count()
        #tendayships=Shipment.objects.filter(shipper__activation_status=True,added_on__range=(twentydays,tendays),status__lte=8).exclude(shipper__code = 32012).exclude(reason_code__code__in=[200,310,888,999,777,111,333]).exclude(rts_status=2).exclude(reason_code_id=1).count()
        #twentydayships=Shipment.objects.filter(shipper__activation_status=True,added_on__range=(thirtydays,twentydays),status__lte=8).exclude(shipper__code = 32012).exclude(rts_status=2).exclude(reason_code__code__in=[200,310,888,999,777,111,333]).exclude(reason_code_id=1)
        #thirtydayships=Shipment.objects.filter(shipper__activation_status=True,added_on__range=("2014-01-01",thirtydays),status__lte=8).exclude(rts_status=2).exclude(shipper__code = 32012).exclude(reason_code_id=1).exclude(reason_code__code__in=[200,310,888,999,777,111,333])
        #message=message+'<tr><td>'+"Grand Total"+'</td><td>'+str(sevendayships)+'</td><td>'+str(tendayships)+'</td><td>'+str(twentydayships.count())+'</td><td>'+str(thirtydayships.count())+'</td></tr>'
        #col_heads=("Customer",'7-10 Days','10-20 Days','20-30 Days','30+ Days')
        #report.write_header(col_heads)
        #path = report.write_body(data) 
        #print path
        #return path
        #print name
        #report = ReportGenerator('ndr_report_{0}.xlsx'.format(name))
        #print customer_emails_list
        #all_mails=["krishnanta@ecomexpress.in","satyak@ecomexpress.in",'sanjeevs@ecomexpress.in','manjud@ecomexpress.in','sravan@ecomexpress.in','jaideeps@ecomexpress.in','onkar@Prtouch.com','theonkar10@gmail.com']
        #all_mails =   ['onkar@prtouch.com','onkartonge@gmail.com']i
        for s in twentydayships:
           address=""
           if s.consignee_address1 is not None:
                address=address+s.consignee_address1
           if s.consignee_address2 is not None:
                 address=address+s.consignee_address2  
           if s.consignee_address3 is not None:
                 address=address+s.consignee_address3
           if s.consignee_address4 is not None:
                 address=address+s.consignee_address4
           u=(s.airwaybill_number,s.shipper,s.pickup.service_centre,s.added_on.strftime('%d-%m-%Y %H:%M'),s.item_description,s.original_dest,s.pincode,s.collectable_value,s.declared_value,s.reason_code,s.rts_status,s.rto_status,s.consignee,address)
           data.append(u)
           #print u
        col_heads=("AWB",'Shipper','Pickup SC','Added On','Item Description',"original dest",'pincode','coll value','declared value','reason code','rts status','rto status','consignee','consignee address')
        report.write_header(col_heads)
        path = report.write_body(data)
        string="20+ days report is "+settings.ROOT_URL + 'static/uploads/reports/' +path
        data=[]
        print thirtydayships.count(),string
        
        report = ReportGenerator('ageingsop_cust_wise_30days{0}.xlsx'.format(name))
        
        for s in thirtydayships:
           address=""
           if s.consignee_address1 is not None:
                address=address+s.consignee_address1
           if s.consignee_address2 is not None:
                 address=address+s.consignee_address2
           if s.consignee_address3 is not None:
                 address=address+s.consignee_address3
           if s.consignee_address4 is not None:
                 address=address+s.consignee_address4
           u=(s.airwaybill_number,s.shipper,s.pickup.service_centre,s.added_on.strftime('%d-%m-%Y %H:%M'),s.item_description,s.original_dest,s.pincode,s.collectable_value,s.declared_value,s.reason_code,s.rts_status,s.rto_status,s.consignee,address)
           data.append(u)
           #print u
        col_heads=("AWB",'Shipper','Pickup SC','Added On','Item Description',"original dest",'pincode','coll value','declared value','reason code','rts status','rto status','consignee','consignee address')
        report.write_header(col_heads)
        path = report.write_body(data)
        


        file_link = settings.ROOT_URL + 'static/uploads/reports/' +path
        subject = "Customerwise ageing SOP"
        from_email = "support@ecomexpress.in"
        print file_link
        message=message+"</table>"+string+" Download 30+ days report from " +file_link+"<p>Regards</p><p>Support Team</p></body></html>"
        print message
        msg = MIMEMultipart()
        msg['From'] = "Reports <support@ecomexpress.in>"
        s1 = smtplib.SMTP('i.prtouch.com', 26)
        #to_mail_ids=['theonkar10@gmail.com','onkar@prtouch.com']
        to_mail_ids =["krishnanta@ecomexpress.in","satyak@ecomexpress.in",'sanjeevs@ecomexpress.in','manjud@ecomexpress.in','sravan@ecomexpress.in','jaideeps@ecomexpress.in',"onkar@prtouch.com",'nitashaa@ecomexpress.in','sunainas@ecomexpress.in']
        #email_msg = " Dear Team,\nReverse shipment Report can be access from %s"%(file_link)
        email_msg=message
        html =message
        text =("Dear Team, \nPlease find customer wise ageing sop  Report. \n\nRegards\n\nSupport Team\n total=%s"%(message))
        msg = EmailMultiAlternatives('Customerwise ageing SOP  Report', text, msg['from'], to_mail_ids)
        msg.attach_alternative(html, "text/html")
        #msg.attach(attach)
        msg.send()
        print "7 days",sevendays,"10 days",tendays,"20 days",twentydays,"30 days",thirtydays
        #send_mail(subject,email_msg,from_email,all_mails)
        print "mail sent :) "
        return subject



ageing_sop_Location()
