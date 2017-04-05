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

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
#import smtplib
#from email.mime.text import MIMEText as text

import datetime

now = datetime.datetime.now()
#before = now - datetime.timedelta(days=1)
request = None

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def cod_coll(reques, report_date_str):
    file_name = "/cod_collection_pod_%s.xlsx" % (now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save) 
    sheet = workbook.add_worksheet()
    sheet.write(0, 2, "COD Collection-POD Report")    

    sheet.write(3, 1, "AWB Number")
    sheet.write(3, 2, "Pickup Date")
    sheet.write(3, 3, "Origin")
    sheet.write(3, 4, "Shipper")
    sheet.write(3, 5, "Consignee")
    sheet.write(3, 6, "COD Due")
    sheet.write(3, 7, "COD Collected")
    sheet.write(3, 8, "COD Balance")
    sheet.write(3, 9, "Delivery Employee Code")
    sheet.write(3, 10, "Delivery Employee Name")
    sheet.write(3, 11, "Dest Centre")
    sheet.write(3, 12, "Reason")
    sheet.write(3, 13, "Updated on")
    sheet.write(3, 14, "Delivery Date")



    row = 3




    shipments = Shipment.objects.filter(statusupdate__added_on__gte='2013-12-01',statusupdate__added_on__lt = '2014-01-01', statusupdate__status = 2, reason_code=1, product_type = "cod").exclude(rts_status=1)
    for a in shipments.iterator():
            if 1==1:
                    if 1 == 1:
                        amount_collected_subtract=0
                        #awb = AirwaybillTally.objects.get(shipment=a)
                        upd_time = a.added_on
                        monthdir = upd_time.strftime("%Y_%m")
                        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                        if a.rts_status or a.rto_status:
                            amount_collected = "return"
                        else:
                            amount_collected = a.collectable_value



                        if a.statusupdate_set.all():
                          status_upda =  a.statusupdate_set.filter().latest("added_on")
                          try:                          
                             emp_code = status_upda.delivery_emp_code.employee_code
                             emp_firstname  = status_upda.delivery_emp_code.firstname
                          except:
                             emp_code = ""
                             emp_firstname = ""   
                        else:
                          emp_code = ""
                          emp_firstname  = ""
                          status_upd = ""
                          upd_date = ""
                        try:
                            history = shipment_history.objects.filter(shipment=a).exclude(status__in=[11,12,16]).latest('updated_on')
                            u = ("",a.airwaybill_number, a.pickup.pickup_date, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, amount_collected,a.collectable_value, emp_code, emp_firstname,a.service_centre, status_upda.reason_code, status_upda.added_on, str(status_upda.date)+" "+str(status_upda.time))
                        except:
                            u = ("",a.airwaybill_number, a.pickup.pickup_date, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, amount_collected,a.collectable_value, emp_code, emp_firstname,a.service_centre, "","")
                        row = row + 1
                        for col, val in enumerate(u, start=0):
                            style = datetime_style
                            try:
                              sheet.write(row, col, str(val))
                            except:
                              pass
    workbook.close()

    return "/home/web/ecomm.prtouch.com/ecomexpress/static/uploads%s"%(file_name)

gq = cod_coll(request, now.strftime('%Y%m%d'))
gq_split = gq.split('/ecomexpress')
gq_path = 'http://billing.ecomexpress.in'+gq_split[1]

subject = "COD Coll"
message = "Please find the link below of COD Coll \n %s"%(gq_path)
from_email = "support@ecomexpress.in"
to_email = ("samar@prtouch.com",)

#m = text(message)
#m['Subject'] = 'Generic Query'
#smtpObj.sendmail(sender, reciever, m.as_string())
send_mail(subject,message,from_email,to_email)
 
