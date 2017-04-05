import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import csv
from reports.report_api import *
from service_centre.models import *
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from reports.ecomm_mail import ecomm_send_mail

#end_date=datetime.datetime.now().date()
#start_date=datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
#end_date=end_date.strftime("%Y-%m-%d")
#start_date=start_date.strftime("%Y-%m-%d")

def cust_loc_performnace_report():
        cust=[92006,11007,22092,88008,81013,69060,41107,80126,12016,34004,13010,96047,80108,96038,94020]
#        cust=[92006,11007,22092]
        #cust=[37042,16018]
        #cust=[92006]
        records=[]
        csv_out=open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/cust_loc{}.csv".format(datetime.datetime.now().strftime("%d-%m-%Y:%H-%M-%S")),"wb")
        #csv_out = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/cust_loc2.csv","wb")
        u = ("Customer","SC", "Total", "Del", "%Del", "Undel","%Undel","Rest","%Rest","Date")
        mywriter = csv.writer(csv_out)
        mywriter.writerow(u)
        end_date=datetime.datetime.now().date()
        start_date=datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
        #end_date=datetime.date(datetime.date.today().year, datetime.date.today().month, 5)
        day_count = (end_date - start_date).days + 1
        delta = datetime.timedelta(days = 1)
        while start_date <= end_date:
      #     print start_date, end_date , start_date + datetime.timedelta(days = 1) 
 #      report = ReportGenerator('customer_location_performance_report_{0}.xlsx'.format(today))
           for c in cust:
       #         print c
                sc=ServiceCenter.objects.using('local_ecomm').all()
                for s in sc.iterator():
        #            print s
                    #print c, s, start_date, start_date + datetime.timedelta(days = 1)
                    total_dcount = Shipment.objects.using('local_ecomm').filter(shipment_date__gte=start_date, shipment_date__lt=(start_date + datetime.timedelta(days = 1)),
                              service_centre=s,rts_status__in = [0, 2]).aggregate(Count('id'))
                    #print 'hi',total_dcount
                    deli=Shipment.objects.using('local_ecomm').filter(shipment_date__gte=start_date, shipment_date__lt=(start_date + datetime.timedelta(days = 1)),
                              service_centre=s,rts_status__in = [0, 2],status=9).aggregate(Count('id'))

                    delcount=deli['id__count'] if deli else 0
                    undeli=Shipment.objects.using('local_ecomm').filter(shipment_date__gte=start_date, shipment_date__lt=(start_date + datetime.timedelta(days = 1)),
                              service_centre=s,rts_status__in = [0, 2],status=8).aggregate(Count('id'))
                    totd = total_dcount['id__count'] if total_dcount else 0
                    undelicount=undeli['id__count']if undeli else 0
                    other=Shipment.objects.using('local_ecomm').filter(shipment_date__gte=start_date, shipment_date__lt=(start_date + datetime.timedelta(days = 1)),
                              service_centre=s,rts_status__in = [0, 2]).exclude(status__in=[8,9]).aggregate(Count('id'))
                    othercount=other['id__count']if other else 0
       #             print 'hi2',totd,delcount,undelicount,othercount
                    if totd <> 0:
                        deliv_perc=round((((float(delcount)/float(totd)))*100.0),2)
                        undel_perc=round((((float(undelicount)/float(totd)))*100.0),2)
                        others_perc=round((((float(othercount)/float(totd)))*100.0),2)
                    else:
                        deliv_perc=0
                        undel_perc=0
                        others_perc=0
                    cu=Customer.objects.get(code=c)
                    u=(cu.name,s.center_name,totd,delcount,deliv_perc,undelicount,undel_perc,othercount,others_perc,start_date.strftime('%d/%m/%Y'))
        #           print u'''
               #     u = (start_date, end_date, start_date + datetime.timedelta(days = 1))     
                    mywriter.writerow(u)
           start_date += delta
        subject = "Customer Location Performance Report "
        file_name = "cust_loc2.csv"
        full_path = 'http://billing.ecomexpress.in/static/uploads/'+file_name
        subject = "Customer Location Performance Report "

        s1 = smtplib.SMTP('i.prtouch.com', 26)

        email_msg = "Hi,\n\nCustomer performance report link follows:\n{0}".format(full_path)
        #email_msg = "Given below is CustomerPerformance Report :\n"+"\n".join(['%s, %s, %s, %s, %s,  %s, %s, %s' % (a[0], a[1], a[2], a[3],a[4],a[5],a[6],a[7]) for a in records])

        from_email = "support@ecomexpress.in"
        #to_email=["samar@prtouch.com", "onkar@prtouch.com"]
        to_email=["samar@prtouch.com","jignesh@prtouch.com", "onkar@prtouch.com","jaideeps@ecomexpress.in"]
        send_mail(subject,email_msg,from_email,to_email)


cust_loc_performnace_report()




