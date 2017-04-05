import os
import sys
import calendar
import datetime
os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')


from django.db.models import Count
from service_centre.models import * 
from reports.report_api import ReportGenerator
from datetime import datetime, timedelta
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from django.core.mail import EmailMultiAlternatives
def generate_sunday_report():
    now = datetime.today() - timedelta(days=1)
    print now.strftime('%Y-%m-%d')
    print now.year
    print now.month
    print now.day
    daily_list=[]
    message='<html><body><p>Dear Team,</p><p>Daily Delivery Report <p>Summary of report follows</p><table  border="1" cellpadding="10"  cellspacing="0"><tr><th>Service Center</th><th>Delivered Shipments</th></tr>'
    dos=DeliveryOutscan.objects.filter(added_on__day=now.day,added_on__month=now.month,added_on__year=now.year)
    print dos.count()
    sc=ServiceCenter.objects.all()
    for s in sc:
         dos_list=[]
         scdos=dos.filter(origin=s)
         for t in scdos:
               doss= DOShipment.objects.filter(status=1,deliveryoutscan=t)
               for d in doss:
                   daily_list.append(d.shipment.airwaybill_number)
                   dos_list.append(d.shipment.airwaybill_number)
         if dos_list:
          message=message+'<tr><td>'+s.center_shortcode+"</td><td>"+str(len(set(dos_list)))+"</td></tr>"
          print s,len(set(dos_list))
    message=message+'<tr><td>'+"Grand Total"+"</td><td>"+str(len(set(daily_list)))+"</td></tr>"
    message=message+"</table>"+"<p>Regards</p><p>Support Team</p></body></html>"
    print message
    msg = MIMEMultipart()
    msg['From'] = "Reports <support@ecomexpress.in>"
    s1 = smtplib.SMTP('i.prtouch.com', 26)
    #to_mail_ids=['theonkar10@gmail.com','onkar@prtouch.com']
    to_mail_ids =["krishnanta@ecomexpress.in","satyak@ecomexpress.in",'sanjeevs@ecomexpress.in','manjud@ecomexpress.in','prashanta@ecomexpress.in','rajivj@ecomexpress.in','sravan@ecomexpress.in','jaideeps@ecomexpress.in',"onkar@prtouch.com"]
    email_msg=message
    html =message
    text =("Dear Team, \nPlease find Daily Delivery  Report. \n\nRegards\n\nSupport Team\n total=%s"%(message))
    msg = EmailMultiAlternatives('Daily Delivery  Report', text, msg['from'], to_mail_ids)
    msg.attach_alternative(html, "text/html")
    msg.send()

    #repora = ReportGenerator('daily_delivery_report_{0}.xlsx'.format(now.strftime('%Y-%m-%d')))
    #col_list =['Service Center']
    #year = now.year
    #month = now.month
    #day = now.day
    #date_list = [day]
    #body = []
    #d = str(year)+'-'+str(month)+'-'+str(day)
    #col_list.append(d)
    #col_heads = tuple(col_list)
    #st_up = StatusUpdate.objects.filter(added_on__year=year, added_on__day=day, added_on__month=month, status=2)
    #data = st_up.values('origin__center_name', 'date').annotate(ct=Count('id'))
    #service_list = ServiceCenter.objects.all()
    #count_li =[0 for i in date_list]
    #sc_dict ={}
    #for se in service_list:
    #    lis = [se.center_name] + count_li
    #    sc_dict[se.center_name] = lis
    #for d in data:
    #    da = d['date']
    #	if da.day == day:
     #        index = date_list.index(da.day) + 1
     #   	sc_dict[d['origin__center_name']][index] = d['ct']
    #for se in service_list:
    #    body.append(sc_dict[se.center_name])
    #report.write_header(col_heads)
    #path = report.write_body(body)
    #print path
    #return patih
    return now


generate_sunday_report()	
