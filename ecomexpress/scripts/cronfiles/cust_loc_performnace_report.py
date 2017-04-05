import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')


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

today=datetime.datetime.now().date()
first=datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
today=today.strftime("%Y-%m-%d")
first=first.strftime("%Y-%m-%d")
#from reports.ecomm_mail import *
#today=first
def cust_loc_performnace_report():
        cust=[92006,11007,22092,88008,81013,69060,41107,80126,12016,34004,13010,96047,80108,96038,94020]
        #cust=[37042,16018]
	records=[]
 	report = ReportGenerator('customer_location_performance_report_{0}.xlsx'.format(today))
 	d=datetime.date.today()
        dt=d
        year=d.year
        month=d.month
	report.write_header(('Customer Name', 'Service Center','Total','Delivered','%ge Delivered','Undelivered','% Undelivered',"Rest",'% Rest','Date'))
        for c in cust:
                sc=ServiceCenter.objects.all()
                for s in sc:
                        d=datetime.date.today()
                        for i in range(1, d.day):
                                if dt:
                                        prev=dt
                                else:
                                        prev=first
                                dt=datetime.date(year, month, i).strftime('%Y-%m-%d')
                                sh=Shipment.objects.filter(shipper__code=c,shipment_date__range=(prev,dt),service_centre=s).exclude(rts_status=1)
                        #print sh     
                                cus=Customer.objects.get(code=c)
                                total=sh.count()
                                if total<>0:
                                        delivered=sh.filter(status=9).count()
                                        undelivered=sh.filter(status=8).count()
                                        others=sh.exclude(status__in=[8,9]).count()
                                        deliv_perc= round((((float(delivered)/float(total)))*100.0),2)
                                        undel_perc=round((((float(undelivered)/float(total)))*100.0),2)
                                        others_perc=round((((float(others)/float(total)))*100.0),2)
                                        u=(cus.name,s.center_name,total,delivered,deliv_perc,undelivered,undel_perc,others,others_perc,prev)
                                        records.append(u)
                                else:
                                        u=(cus.name,s.center_name,0,0,0,0,0,0,0,prev)
                                        records.append(u)

	
        subject = "Customer Location Performance Report "
	file_name = report.write_body(records)
        full_path = 'http://billing.ecomexpress.in/static/uploads/reports/'+file_name
        subject = "Customer Location Performance Report "
	f = open('/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/reports/' + file_name,"r")
	file_content = f.read()
	f.close()

	attach = MIMEApplication(file_content, 'xlsx')
	attach.add_header('Content-Disposition', 'attachment', filename=file_name)

	s1 = smtplib.SMTP('i.prtouch.com', 26)

        email_msg = "Hi,\n\nCustomer performance report link follows:\n{0}".format(full_path)
        #email_msg = "Given below is CustomerPerformance Report :\n"+"\n".join(['%s, %s, %s, %s, %s,  %s, %s, %s' % (a[0], a[1], a[2], a[3],a[4],a[5],a[6],a[7]) for a in records])

        from_email = "support@ecomexpress.in"
	to_email=["onkar@prtouch.com"]
        #to_email=["samar@prtouch.com","jignesh@prtouch.com", "onkar@prtouch.com","jaideeps@ecomexpress.in"]
        send_mail(subject,email_msg,from_email,to_email)


cust_loc_performnace_report()
