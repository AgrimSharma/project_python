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
from django.utils import simplejson
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
#import smtplib
#from email.mime.text import MIMEText as text

import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder

now = datetime.datetime.now()
#before = now - datetime.timedelta(days=1)
request = None

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)



#def billing_reconciliation_stmt_home(request):
#    customers = Customer.objects.all()
#    html = render_to_string('billing/input_form.html',
#            {'url': reverse('billing-reconciliation-report'),
#             'customers': customers^M
#            }
#    )

 #   data = {'html':html}
 #   json = simplejson.dumps(data)
 #   return HttpResponse(json, mimetype='application/json')





def json_sh():
    shipments = Shipment.objects.filter(added_on__month=now.year, added_on__month=7).values_list('pickup__subcustomer_code__name','pickup__service_centre__center_name','length','breadth','height','reverse_pickup','airwaybill_number','order_number','product_type','shipper__name','consignee','actual_weight','volumetric_weight','pickup__service_centre__center_name','original_dest__center_name','service_centre__center_name','mobile','added_on','status','expected_dod','return_shipment','rto_status','rts_status','ref_airwaybill_number','collectable_value','declared_value')
    prices_json = json.dumps(list(shipments), cls=DjangoJSONEncoder)    

#from django.utils import simplejson

#people = People.objects.all().values_list('name', 'id')
#simplejson.dumps(list(people))
#Sometimes when the json output is very complex we usually use a json template with the *render_to_string* function, for example:

#context = {'people': People.objects.all().values('name', 'id')}
#render_to_string('templates/people.json', context, context_instance=RequestContext

def generic_query(reques, report_date_str):
    shipment_info={}
    download_list = []    
    q=Q()


    if 1==1:
        file_name = "/Generic_Query_%s.xlsx"%(now.strftime("%d%m%Y"))
#        file_name = "/Generic_Query_31082013.xlsx"
        path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
        workbook = Workbook(path_to_save)

        header_format = workbook.add_format()
        header_format.set_bg_color('yellow')
        header_format.set_bold()
        header_format.set_border()

        rts_format = workbook.add_format()
        rts_format.set_bg_color('red')
        rts_format.set_border()

        rto_format = workbook.add_format()
        rto_format.set_bg_color('#d2e9fa')
        rto_format.set_border()

        plain_format = workbook.add_format()

        sheet = workbook.add_worksheet()
        sheet.set_column(0,26, 30)
        sheet.write(0, 2, "Generic query")
        sheet.write(3, 0, "Air Waybill No", header_format)
        sheet.write(3, 1, "Order No", header_format)
        sheet.write(3, 2, "Weight", header_format)
        sheet.write(3, 3, "Vol Weight", header_format)
        sheet.write(3, 4, "Length", header_format)
        sheet.write(3, 5, "Breadth", header_format)
        sheet.write(3, 6, "Height", header_format)
        sheet.write(3, 7, "COD Amount", header_format)
        sheet.write(3, 8, "Declared Value", header_format)
        sheet.write(3, 9, "Origin", header_format)
        sheet.write(3, 10, "Destination", header_format)
        sheet.write(3, 11, "Vendor", header_format)
        sheet.write(3, 12, "Shipper", header_format)
        sheet.write(3, 13, "Consignee", header_format)
        sheet.write(3, 14, "Contact Number", header_format)
        sheet.write(3, 15, "P/U Date", header_format)
        sheet.write(3, 16, "Status", header_format)
        sheet.write(3, 17, "Expected Date", header_format)
        sheet.write(3, 18, "Updated Date", header_format)
        sheet.write(3, 19, "Remarks", header_format)
        sheet.write(3, 20, "Reason Code", header_format)
        sheet.write(3, 21, "Reason", header_format)
        sheet.write(3, 22, "Received by", header_format)
        sheet.write(3, 23, "Del Date", header_format)
        sheet.write(3, 24, "Del Time", header_format)
        sheet.write(3, 25, "New Air Waybill (RTS)", header_format)	
        sheet.write(3, 26, "Return Status", header_format)
        sheet.write(3, 27, "Updated on", header_format)
        row = 3
        if report_date_str:
            report_date_str = datetime.datetime.strptime(report_date_str,"%Y%m%d").date()
            nextmonthdate = report_date_str +timedelta(days=1)
            nextmonth_date = nextmonthdate.strftime('%Y-%m-%d')
            report_date = report_date_str.strftime('%Y-%m-01')
            q = q & Q(added_on__range=('2013-08-01','2013-09-01'))

        shipments = Shipment.objects.filter(q).select_related('original_dest__center_name','service_centre__center_name','pickup','shipper__name').only('pickup__subcustomer_code__name','pickup__service_centre__center_name','length','breadth','height','reverse_pickup','airwaybill_number','order_number','product_type','shipper__name','consignee','actual_weight','volumetric_weight','pickup__service_centre__center_name','original_dest__center_name','service_centre__center_name','mobile','added_on','status','expected_dod','return_shipment','rto_status','rts_status','ref_airwaybill_number','collectable_value','declared_value')

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

                    try:
                          hist1 = shipment_history.objects.filter(shipment=shipment).exclude(status__in=[11,12,16]).values_list('reason_code__code','reason_code__code_description','updated_on','remarks', 'current_sc__center_shortcode')
                          history = hist1.latest('updated_on')
                    except:
                        history = ""

                    if shipment.expected_dod:
                       shipment.expected_dod = shipment.expected_dod.strftime("%d-%m-%Y")
                    else:
                       shipment.expected_dod = ""
                    if history:
                       remarks = history[3]
                       updated_on = history[2].strftime("%d-%m-%Y")
                       hist_upd_time = history[2].time()
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
                    else:
                       received_by = ""
                       date = ""
                       time = "" 
                    if shipment:
                              val = get_internal_shipment_status(shipment.status)
                    if shipment.status in [3,5]:
                            st = hist1.filter(status=3).order_by('-id')[0]
                            bag = st[3].split('. ')[1][0:3]
                            val = "Shipment Connected to %s from %s"%(bag, st[4])

                    if (shipment.reason_code_id == 5 or shipment.return_shipment==3 or shipment.rto_status == 1 or shipment.rts_status == 1 or shipment.rts_status == 2):
                                  val = "Returned"
                    try:
                      pikup = shipment.pickup
                      vendor = str(pikup.subcustomer_code) +" - "+str(pikup.subcustomer_code.id) 
                    except:
                      vendor = ""      
                    if shipment.ref_airwaybill_number: 
                     sref = Shipment.objects.filter(airwaybill_number = shipment.ref_airwaybill_number).values_list('id','status','rts_status','added_on')
                     if sref:
                       try:
                          monthdir = sref[0][3].strftime("%Y_%m")
                          shipment_history_rts = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                          rts_history = shipment_history_rts.objects.filter(shipment=sref[0][0]).values_list('updated_on').latest('updated_on')

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
                       u = (shipment.airwaybill_number, shipment.order_number, shipment.actual_weight, shipment.volumetric_weight, shipment.length, shipment.breadth, shipment.height, shipment.collectable_value, shipment.declared_value, pikup.service_centre, sc, vendor, shipment.shipper, shipment.consignee,shipment.mobile, shipment.added_on.strftime("%d-%m-%Y"), val, shipment.expected_dod, str(updated_on)+" | "+str(hist_upd_time),remarks, reason_code, reason_code_desc, received_by, date, time, shipment.ref_airwaybill_number, rts_val, rts_updated_on, shipment.rts_status)
                    else:	
                       
                       u = (shipment.airwaybill_number, shipment.order_number, shipment.actual_weight, shipment.volumetric_weight, shipment.length, shipment.breadth, shipment.height, shipment.collectable_value, shipment.declared_value, pikup.service_centre, sc, vendor, shipment.shipper, shipment.consignee, shipment.mobile, shipment.added_on.strftime("%d-%m-%Y"), val, shipment.expected_dod, str(updated_on)+" | "+str(hist_upd_time), remarks, reason_code, reason_code_desc, received_by, date, time, "","","",shipment.rts_status)
                    row = row + 1
                    style = plain_format
                    if shipment.rto_status == 1:
                            style = rto_format
                    if shipment.rts_status == 1:
                            style = rts_format 
                    for col, val in enumerate(u, start=0):
                         if col <> 28:
                              try:   
                                sheet.write(row, col, str(val), style)    
                              except:
                                sheet.write(row, col, removeNonAscii(val), style)
            workbook.close()
        return "/home/web/ecomm.prtouch.com/ecomexpress/static/uploads%s"%(file_name)
#smtpObj = smtplib.SMTP('localhost', 25) 
#smtpObj = smtplib.SMTP('i.prtouch.com', 26)
#sender = "support@prtouch.com"
#reciever = ["jignesh@prtouch.com", "samar@prtouch.com"]
#reciever = ["sunainas@ecomexpress.in", "jaideeps@ecomexpress.in", "jignesh@prtouch.com", "samar@prtouch.com", "sravank@ecomexpress.in"]

#gq = generic_query(request, now.strftime('%Y%m%d'))
#gq_split = gq.split('/ecomexpress')
#gq_path = 'http://cs.ecomexpress.in'+gq_split[1]

#subject = "Generic Query"
#message = "Please find the link below of Generic Query for shipments in this month \n %s"%(gq_path)
#from_email = "support@ecomexpress.in"
#to_email = ("sunainas@ecomexpress.in", "jaideeps@ecomexpress.in", "jignesh@prtouch.com", "samar@prtouch.com", "sravank@ecomexpress.in", "rajeshwars@ecomexpress.in", "vaibhavk@ecomexpress.in", "rsinha@ecomexpress.in", "balwinders@ecomexpress.in", "kavitac@ecomexpress.in", "gauravk@ecomexpress.in", "mukundh@ecomexpress.in")
#to_email = ("samar@prtouch.com",)

#m = text(message)
#m['Subject'] = 'Generic Query'
#smtpObj.sendmail(sender, reciever, m.as_string())
#send_mail(subject,message,from_email,to_email)
 
#to_email = ("krishnanta@ecomexpress.in", "satyak@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in", "jitendrad@ecomexpress.in", "jaideeps@ecomexpress.in", "jignesh@prtouch.com", "nareshb@ecomexpress.in", "samar@prtouch.com")
#s = smtplib.SMTP('i.prtouch.com', 26)
#for a in to_email:
#    msg = MIMEMultipart()
#    msg['Subject'] = 'Daily Sales Report'
#    msg['From'] = "Reports <jignesh@prtouch.com>"
#    plain_test_part = MIMEText("Please find the link below of Generic Query for shipments in this month \n %s"%(gq_path), 'plain')
#    msg.attach(plain_test_part)
#    msg['To']=a
#    s.sendmail(msg['From'] , msg['To'], msg.as_string())
#s.quit()




