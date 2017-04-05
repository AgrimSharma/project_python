import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import *
from billing.views import *
from track_me.views import *
import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from reports.ecomm_mail import ecomm_send_attach_mail, ecomm_send_mail

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

import datetime

now = datetime.datetime.now()

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def data_uploaded_status(report_date_str):
        q = Q()
        file_name = "/Data_uploaded.xlsx"
        path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
        workbook = Workbook(path_to_save)
    
        header_format = workbook.add_format()
        header_format.set_bg_color('yellow') 
        header_format.set_bold()
        header_format.set_border()
        plain_format = workbook.add_format()

        sheet = workbook.add_worksheet()
        sheet.set_column(0,8, 30)
        sheet.write(0, 2, "Data Uploaded")
        sheet.write(3, 0, "Air Waybill No", header_format)
        sheet.write(3, 1, "Origin", header_format)
        sheet.write(3, 2, "Customer Name", header_format)
        sheet.write(3, 3, "Updated Date", header_format)
        sheet.write(3, 4, "Updated Time", header_format)
        sheet.write(3, 5, "Collectable Value", header_format)
        sheet.write(3, 6, "Current SC", header_format)
        row = 3
        if report_date_str:
            report_date_str = datetime.datetime.strptime(report_date_str,"%Y%m%d").date()
            nextmonthdate = report_date_str +timedelta(days=1)
            nextmonth_date = nextmonthdate.strftime('%Y-%m-%d')
            report_date = report_date_str.strftime('%Y-%m-01')
            q = q & Q(added_on__range=(report_date,nextmonth_date))

        a=0
        stat ="0"
        msg = "Data-Uploaded"
        shipments = Shipment.objects.filter(q, status=stat).exclude(rts_status=1).exclude(shipper__code="32012").exclude(reason_code=53)
        download_list = []
        for a in shipments.iterator():
                upd_time = a.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                if not a.original_dest:
                    sc = a.service_centre
                else:
                    sc = a.original_dest
                try:
                    history = shipment_history.objects.filter(shipment=a).latest('updated_on')
                    updated_on = history.updated_on.strftime('%d-%m-%Y')
                except:
                    updated_on = ""
                    history=""
                u = (a.airwaybill_number, a.pickup.service_centre, a.shipper.name,history.updated_on.date(), history.updated_on.time(), a.collectable_value, history.current_sc)
                row = row + 1
                style = plain_format
                for col, val in enumerate(u, start=0):
                                sheet.write(row, col, str(val), style)
        workbook.close()
        return "/home/web/ecomm.prtouch.com/ecomexpress/static/uploads%s"%(file_name)

gq = data_uploaded_status(now.strftime('%Y%m%d'))
gq_split = gq.split('/ecomexpress')
gq_path = 'http://cs.ecomexpress.in'+gq_split[1]

subject = "Data uploaded status report"
message = "Please find the link below of shipments in this month \n %s"%(gq_path)
from_email = "support@ecomexpress.in"
to_email = ("krishnanta@ecomexpress.in","satyak@ecomexpress.in",'sanjeevs@ecomexpress.in','manjud@ecomexpress.in', "jaysinhr@ecomexpress.in", "jaideeps@ecomexpress.in", "jignesh@prtouch.com",  "narenders@ecomexpress.in","rakeshl@ecomexpress.in", "rameshw@ecomexpress.in", "lokeshr@ecomexpress.in", "lokanathanm@ecomexpress.in", "sanjeevs@ecomexpress.in", "chandrashekarb@ecomexpress.in", "onkar@prtouch.com", "anilku@ecomexpress.in","sandeepv@ecomexpress.in","pravinp@ecomexpress.in", "girishw@prtouch.com")
#to_email = ("samar@prtouch.com",)
ecomm_send_mail(subject,gq_path,to_email)

