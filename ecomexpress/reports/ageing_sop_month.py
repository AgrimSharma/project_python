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
        start_date=now.strftime('%Y-%m-01 00:00:01')
        name=now.strftime('%Y-%m-%d') 
        report = ReportGenerator('ageingsop_jan.xlsx')
        month=now.month
        year= now.year
        col_heads=('AWB','reasoncode')
        todays=datetime.datetime.strptime(name, "%Y-%m-%d") - datetime.timedelta(days=6)
        print todays
        #return "hi"
        data=[]
        year=[2014]
        month=[]
        month=[1,2,3,4,5]
        ships=Shipment.objects.filter(shipper__activation_status=True,added_on__lte=todays,status__lte=8).exclude(shipper__code=32012).exclude(reason_code__code__in=[200,310,888,999,777,111,333]).exclude(status__in=[11,16,9]).exclude(rts_status=2)
        cust=[]
        jantotal=0
        febtotal=0
        marchtotal=0
        apriltotal=0
        maytotal=0
        junetotal=0
        grandtotal=0
        message='<html><body><p>Dear Team,</p><p>Monthwise Ageing SOP report <p>Summary of report follows</p><table  border="1" cellpadding="10"  cellspacing="0"><tr><th>Customer</th><th>Jan </th><th>Feb</th><th>March</th><th>April</th><th>May</th><th>June</th><th>Total</th></tr>'

        cust=Customer.objects.filter(activation_status=True).exclude(code = 32012)
        sc=ServiceCenter.objects.filter().exclude(type=1)
        for c in cust:
            year=2014
            cships=ships.filter(shipper=c,shipment_date__year=year)
            #year=2014
            janships=cships.filter(shipment_date__month=1).count()
            febships=cships.filter(shipment_date__month=2).count()
            marships=cships.filter(shipment_date__month=3).count()
            aprships=cships.filter(shipment_date__month=4).count()
            mayships=cships.filter(shipment_date__month=5).count()
            #js=cships.filter(shipment_date__month=6)
            #for s in js:
            #  print "june shipemnt",s.airwaybill_numberi
            #jantotal=jantotal+janships
            #febtotal=febtotal+febships
            #marchtotal
            juneships=cships.filter(shipment_date__month=6).count()
            if(janships<>0 or febships<>0 or marships<>0 or aprships<>0 or mayships<>0 or juneships<>0):
                message=message+'<tr><td>'+c.name+'</td><td>'+str(janships)+'</td><td>'+str(febships)+'</td><td>'+str(marships)+'</td><td>'+str(aprships)+'</td><td>'+str(mayships)+'</td><td>'+str(juneships)+'</td><td>'+str(cships.count())+'</td></tr>'
            #cships=ships.filter(shipment_date__year=year)
            #janships=cships.filter(shipment_date__month=1).count()
            #febships=cships.filter(shipment_date__month=2).count()
            #marships=cships.filter(shipment_date__month=3).count()
            #aprships=cships.filter(shipment_date__month=4).count()
            #mayships=cships.filter(shipment_date__month=5).count()
        janships=ships.filter(shipment_date__month=1).count()
        febships=ships.filter(shipment_date__month=2).count()
        marships=ships.filter(shipment_date__month=3).count()
        aprships=ships.filter(shipment_date__month=4).count()
        mayships=ships.filter(shipment_date__month=5).count()
        js=ships.filter(shipment_date__month=6).count()
        total=ships.count()  
        data=[]
        #janships=ships.filter(shipment_date__month=1)
        #for s in janships:
        #    u=(s.airwaybill_number,s.reason_code)
        #    data.append(u)
        #janships=ships.filter(shipment_date__month=1).count()
        message=message+'<tr><td>'+'Grand Total'+'</td><td>'+str(janships)+'</td><td>'+str(febships)+'</td><td>'+str(marships)+'</td><td>'+str(aprships)+'</td><td>'+str(mayships)+'</td><td>'+str(js)+"</td><td>"+str(total)+'</td></tr>'

        #report.write_header(col_heads)
        #path = report.write_body(data)
        #file_link = settings.ROOT_URL + 'static/uploads/reports/' +path
        #message=message+"</table>"+" Jan Report "+file_link
        #data=[]
        #report = ReportGenerator('ageingsop_feb.xlsx')
        #report.write_body(col_heads)
        #febships=ships.filter(shipment_date__month=2)
        #for s in febships:
         # u=(int(s.airwaybill_number),s.reason_code)
          #data.append(u)
        #path = report.write_body(data)
        #data=[]
        #file_link = settings.ROOT_URL + 'static/uploads/reports/' +path
        #message=message+" Feb Report"+path
        #report = ReportGenerator('ageingsop_mar.xlsx')
        #report.write_body(col_heads)
        #marships=ships.filter(shipment_date__month=3)
        #for s in marships:
         # u=(str(s.airwaybill_number),s.reason_code)
         # data.append(u)
        #path = report.write_body(data)
        #file_link = settings.ROOT_URL + 'static/uploads/reports/' +path
        #message=message+" March Report"+path



        #print path
        cust=Customer.objects.filter(activation_status=True).exclude(code = 32012)
        #return path
        subject = "Monthwise Customerwise ageing SOP"
        from_email = "support@ecomexpress.in"
        message=message+"</table><p>Regards</p><p>Support Team</p></body></html>"
        print message
        msg = MIMEMultipart()
        msg['From'] = "Reports <support@ecomexpress.in>"
        s1 = smtplib.SMTP('i.prtouch.com', 26)
        #to_mail_ids=['jaideeps@ecomexpress.in','onkar@prtouch.com','theonkar10@gmail.com']
        to_mail_ids =["krishnanta@ecomexpress.in","satyak@ecomexpress.in",'sanjeevs@ecomexpress.in','manjud@ecomexpress.in','sravan@ecomexpress.in','jaideeps@ecomexpress.in',"onkar@prtouch.com",'sunainas@ecomexpress.in','nitashaa@ecomexpress.in']
        
        email_msg=message
        html =message
        text =("Dear Team, \nPlease find monthwise wise ageing sop  Report. \n\nRegards\n\nSupport Team\n total=%s"%(message))
        msg = EmailMultiAlternatives('Monthwise Ageing SOP report', text, msg['from'], to_mail_ids)
        msg.attach_alternative(html, "text/html")
        #msg.attach(attach)
        msg.send()

        print "mail sent :) "
        return subject



ageing_sop_Location()
