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
import csv
from zipfile import ZipFile
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
#import smtplib
#from email.mime.text import MIMEText as text

import datetime

now = datetime.datetime.now()
#before = now - datetime.timedelta(days=1)
request = None


def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def unicode_removal(u):
           r = []
           for c in u:
               try:
                  r.append(str(c))
               except UnicodeEncodeError:
                  r.append(removeNonAscii(c))
           return r

def generic_query(reques, report_date_str):
    shipment_info={}
    download_list = []
    q=Q()
    report_date_str_name = report_date_str

    if report_date_str:
        report_date_str = datetime.datetime.strptime(report_date_str,"%Y%m%d").date()

    if 1==1:
      #  file_name = "/Generic_Query_%s.xlsx"%(now.strftime("%d%m%Y%H"))
        file_name = "/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/lost_missing_"+report_date_str_name+ ".xlsx"
        csv_out = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/lost_missing_"+report_date_str_name+ ".csv","wb")
        workbook = Workbook(file_name)
        sheet = workbook.add_worksheet()

        header_format = workbook.add_format()
        header_format.set_bg_color('yellow')
        header_format.set_bold()
        header1_format = workbook.add_format()
        header1_format.set_bg_color('blue')
        header1_format.set_bold()
        header2_format = workbook.add_format()
        header2_format.set_bg_color('red')
        header2_format.set_bold()
        plain_format = workbook.add_format()

        sheet.write(0, 3, "311 shortage/208 contain missing ", header_format)
        #sheet.set_column(2, 2, 25) # set column width

        sheet.write(1, 0, "Date ", header_format)
        sheet.write(1, 1, report_date_str_name)
        col_heads = ("Air Waybill No","Order No", "Product Type", "Weight", "Vol Weight", "COD Amount", "Declared Value",
             "Origin", "Destination", "Vendor", "Shipper", "Consignee", "Contact Number", "P/U Date", "Status", "Expected Date",
             "Updated Date", "Remarks", "Reason Code", "Reason", "Received by", "Del Date", "Del Time", "New Air Waybill (RTS)",
             "Return Status", "Updated on", "RTS Status", "RTO Status","PRUD_DATE", "FRST_ATMPTD_UDSTATUS", "FRST_ATMPT_DATE")

        for ind, col in enumerate(col_heads):
            sheet.write(3, ind, col, header_format)

        mywriter = csv.writer(csv_out)
        u = ("Air Waybill No","Order No", "Product Type", "Weight", "Vol Weight", "COD Amount", "Declared Value",
             "Origin", "Destination", "Vendor", "Shipper", "Consignee", "Contact Number", "P/U Date", "Status", "Expected Date",
             "Updated Date", "Remarks", "Reason Code", "Reason", "Received by", "Del Date", "Del Time", "New Air Waybill (RTS)",
             "Return Status", "Updated on", "RTS Status", "RTO Status","PRUD_DATE", "FRST_ATMPTD_UDSTATUS", "FRST_ATMPT_DATE")
        mywriter.writerow(u)
        row = 4
        if report_date_str:
            nextmonthdate = report_date_str +timedelta(days=1)
            nextmonth_date = nextmonthdate.strftime('%Y-%m-%d')
            report_date = report_date_str.strftime('%Y-%m-01')
            q = q & Q(added_on__lte=report_date)
            q = q & Q(reason_code__code__in=[311,208])

        shipments = Shipment.objects.using('local_ecomm').filter(q).select_related('original_dest__center_name','service_centre__center_name','pickup','shipper__name').only('pickup__subcustomer_code__name','pickup__service_centre__center_name','length','breadth','height','reverse_pickup','airwaybill_number','order_number','product_type','shipper__name','consignee','actual_weight','volumetric_weight','pickup__service_centre__center_name','original_dest__center_name','service_centre__center_name','mobile','added_on','status','expected_dod','return_shipment','rto_status','rts_status','ref_airwaybill_number','collectable_value','declared_value')


        if 1==1:
            for a in shipments.iterator():
                    remarks = ""
                    reason_code = ""
                    reason_code_desc = "In Transit"
                    updated_on = ""
                    rto_status = 0
                    rem_status = 0
                    rts_status = 0
                    rts_rts_status = 0
                    shipment = a
                    upd_time = shipment.added_on
                    hist_upd_time = ""
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    rts_status = 0
                    prod_type = shipment.product_type
                    if str(shipment.airwaybill_number)[0] ==  '3':
                        prod_type = 'ebsppd'
                    elif str(shipment.airwaybill_number)[0] ==  '4':
                        prod_type = 'ebscod'
                    elif str(shipment.airwaybill_number)[0] ==  '5':
                        prod_type = 'ebsrev'
                    try:
                          hist1 = shipment_history.objects.using('local_ecomm').filter(shipment=shipment).exclude(status__in=[11,12,16]).values_list('reason_code__code','reason_code__code_description','updated_on','remarks', 'current_sc__center_shortcode')
                          history = hist1.latest('updated_on')
                    except:
                        history = ""
                    if shipment:
                              val = get_internal_shipment_status(shipment.status)
                    if shipment.status in [3,5]:
                            st = hist1.filter(status__in=[3,5]).order_by('-id')[0]
                            bag = st[3].split('. ')[1][0:3]
                            remarks = "Shipment Connected to %s from %s"%(bag, st[4])

                    if (shipment.reason_code_id == 5 or shipment.return_shipment==3 or shipment.rto_status == 1 or shipment.rts_status == 1 or shipment.rts_status == 2):
                                  val = "Returned"

                    if shipment.expected_dod:
                       shipment.expected_dod = shipment.expected_dod.strftime("%d-%m-%Y")
                    else:
                       shipment.expected_dod = ""
                    if history:
                       if history[0] in [206, 200, 311, 302, 333, 888]:
                           remarks = val
                           val = history[3]
                       else:
                           remarks = history[3]
                       updated_on = history[2].strftime("%d-%m-%Y")
                       #hist_upd_time = history[2].time()
                       if history[0]:
                           reason_code = history[0]
                           reason_code_desc = history[1]
                    if not shipment.original_dest_id:
                         sc = shipment.service_centre
                    else:
                         sc = shipment.original_dest
                    supd = shipment.statusupdate_set.filter()
                    if supd:
                       su = supd.order_by("-date","-time")[:1][0]
                       received_by = su.recieved_by
                       time  = su.time.strftime("%H:%m")
                       date  = su.date.strftime("%d-%m-%Y")
                       if su.status == 2:
                          remarks = "Delivered"
                       else:
                          remarks = su.remarks
		       if su.reason_code_id:
	                       reason_code = su.reason_code.code
        	               reason_code_desc = su.reason_code.code_description
		       else:
			       reason_code = ""
			       reason_code_desc =""
                       if supd.count() > 1:
                          prud_su = supd.order_by("-date","-time")[:2][1]
                          prud_date = prud_su.date.strftime("%d-%m-%Y")
                          first_su = supd.order_by("date","time")[0]
                          first_rc = str(first_su.reason_code.code) + first_su.reason_code.code_description
                          first_date = first_su.date.strftime("%d-%m-%Y")
                       else:
                         prud_date = date
                         first_rc = reason_code
                         first_date = date

                    else:
                       received_by = ""
                       date = ""
                       time = ""
                       prud_date = ""
                       first_rc = ""
                       first_date = ""

                    try:
                      pikup = shipment.pickup
                      vendor = str(pikup.subcustomer_code.name) +" - "+str(pikup.subcustomer_code.id)
                    except:
                      vendor = ""
                    if shipment.ref_airwaybill_number:
                     sref = Shipment.objects.using('local_ecomm').filter(airwaybill_number = shipment.ref_airwaybill_number).values_list('id','status','rts_status','added_on')
                     if sref:
                       try:
                          monthdir = sref[0][3].strftime("%Y_%m")
                          shipment_history_rts = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                          rts_history = shipment_history_rts.objects.using('local_ecomm').filter(shipment=sref[0][0]).values_list('updated_on').latest('updated_on')

                       except:
                          rts_history = ""
                       if rts_history:
                          rts_updated_on = rts_history[0].strftime("%d-%m-%Y")
                       else:
                          rts_updated_on = ""
                       if sref[0]:
                              rts_val = sref[0][1]
                              rts_val = get_internal_shipment_status(rts_val)
                       if sref[0][2]==2:
                                  rts_val = "Returned"
                       #no_of_attempts = shipment.deliveryoutscan_set.all().count()
                       u = (shipment.airwaybill_number, shipment.order_number, prod_type, shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value, pikup.service_centre.center_name, sc.center_name, vendor, shipment.shipper.name, shipment.consignee,shipment.mobile, shipment.added_on.strftime("%d-%m-%Y"), val, shipment.expected_dod, str(updated_on),remarks, reason_code, reason_code_desc, received_by, date, time, shipment.ref_airwaybill_number, rts_val, rts_updated_on, shipment.rts_status, shipment.rto_status, prud_date, first_rc, first_date)
                    else:

                       #no_of_attempts = shipment.deliveryoutscan_set.all().count()
                       u = (shipment.airwaybill_number, shipment.order_number, prod_type, shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value, pikup.service_centre.center_name, sc.center_name, vendor, shipment.shipper.name, shipment.consignee, shipment.mobile, shipment.added_on.strftime("%d-%m-%Y"), val, shipment.expected_dod, str(updated_on), remarks, reason_code, reason_code_desc, received_by, date, time, "","","",shipment.rts_status, shipment.rto_status, prud_date,  first_rc, first_date)
                    try:
                       mywriter.writerow(u)
                    except:
                       mywriter.writerow(unicode_removal(u))

                    col = 0
                    print "$$$$",sc.center_name
                    for val  in u:
                       print "----",val
                       sheet.write(row, col, val) 
                       col += 1

                    row += 1

        workbook.close()
        return "/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/lost_missing_"+report_date_str_name+ ".csv"

gq = generic_query(request, now.strftime('%Y%m%d'))
msg = MIMEMultipart()
report_date_str_name = now.strftime('%Y%m%d')
gq_split = gq.split('/ecomexpress')
gq_path = 'http://cs.ecomexpress.in'+gq_split[1]
os.system('cd /home/web/ecomm.prtouch.com/ecomexpress/static/uploads && zip lost_missing_'+report_date_str_name+ '.csv.zip lost_missing_'+report_date_str_name+ '.csv')
#os.system('cd /home/web/ecomm.prtouch.com/ecomexpress/static/uploads && zip gq_cur_acto.zip gq_cur_acto.csv')
#os.system('cd /home/web/ecomm.prtouch.com/ecomexpress/static/uploads && zip gq_cur_ws.zip gq_cur_ws.csv')
#os.system('cd /home/web/ecomm.prtouch.com/ecomexpress/static/uploads && zip gq_cur_tv18.zip gq_cur_tv18.csv')
#os.system('cd /home/web/ecomm.prtouch.com/ecomexpress/static/uploads && zip gq_cur_jasp.zip gq_cur_jasp.csv')

subject = "311 shortage/208 contain missing"
message = '''Please find the link below of Missing/Shortage for shipments for March.The shipments marked as 1 in rts status are secondary airwaybills (the one that are marked as red in original sheet) whereas those marked as 2 are primary airwaybills and 0 are normal airwaybills, similarly shipments marked as 1 in rto status are rto airwaybills(marked as blue), and 0 are normal. \n Consolidated: http://cs.ecomexpress.in/static/uploads/lost_missing_'''+report_date_str_name+ '.xlsx \n Also, it has been attached here.'
from_email = "support@ecomexpress.in"
#to_email = ("sunainas@ecomexpress.in","shilpaa@ecomexpress.in","veenav@ecomexpress.in", "jaideeps@ecomexpress.in", "jignesh@prtouch.com", "sravank@ecomexpress.in", "rajeshwars@ecomexpress.in", "vaibhavk@ecomexpress.in", "rsinha@ecomexpress.in", "balwinders@ecomexpress.in", "kavitac@ecomexpress.in", "gauravk@ecomexpress.in", "mukundh@ecomexpress.in", "shantia@ecomexpress.in", "shalinia@ecomexpress.in", "shwethaj@ecomexpress.in", "onkar@prtouch.com", "samar@prtouch.com", "jinesh@prtouch.com", "sandeepc@ecomexpress.in")
#to_email = ("sunainas@ecomexpress.in","shilpaa@ecomexpress.in","veenav@ecomexpress.in", "jaideeps@ecomexpress.in", "jignesh@prtouch.com", "sravank@ecomexpress.in", "rajeshwars@ecomexpress.in", "vaibhavk@ecomexpress.in", "rsinha@ecomexpress.in", "balwinders@ecomexpress.in", "kavitac@ecomexpress.in", "gauravk@ecomexpress.in", "mukundh@ecomexpress.in", "shantia@ecomexpress.in", "shalinia@ecomexpress.in", "shwethaj@ecomexpress.in", "onkar@prtouch.com", "samar@prtouch.com", "jinesh@prtouch.com", "sandeepc@ecomexpress.in")
#to_email= ("krishnanta@ecomexpress.in",  "sanjeevs@ecomexpress.in", "jaideeps@ecomexpress.in", "jignesh@prtouch.com", "sanjeev.chopra@ecomexpress.in" )
#to_email = ( "jaideeps@ecomexpress.in", "jignesh@prtouch.com")
#to_email = ("samar@prtouch.com","jinesh@prtouch.com", "sravank@ecomexpress.in")
to_email = ("samar@prtouch.com","jignesh@prtouch.com")
#to_mail_ids = ("samar@prtouch.com","jignesh@prtouch.com")
to_mail_ids = ("manjud@ecomexpress.in","krishnanta@ecomexpress.in",  "sanjeevs@ecomexpress.in", "jaideeps@ecomexpress.in", "jignesh@prtouch.com", "sanjeev.chopra@ecomexpress.in","sunily@ecomexpress.in","sravank@ecomexpress.in")


f = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/lost_missing_"+report_date_str_name+ ".xlsx","r")
missing_shipment = f.read()
f.close()

attach = MIMEApplication(missing_shipment, 'xlsx')
attach.add_header('Content-Disposition', 'attachment', filename = 'lost_missing_'+report_date_str_name+ '.xlsx')
msg = MIMEMultipart()
msg['From'] = "Reports <support@ecomexpress.in>"
s1 = smtplib.SMTP('i.prtouch.com', 26)
msg = EmailMultiAlternatives('311 shortage/208 contain missing', message, msg['from'], to_mail_ids)
#msg.attach_alternative(message, "text/html")
msg.attach(attach)
msg.send()
#send_mail(subject,message,from_email,to_email)
