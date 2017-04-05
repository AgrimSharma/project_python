import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import Shipment, StatusUpdate, get_internal_shipment_status
import settings
import csv
import datetime
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives


def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def unicode_removal(u):
           r = []
           for c in u:
               try:
                  r.append(str(c))
               except UnicodeEncodeError:
                  r.append(removeNonAscii(c))
           return r


def data_params_dict(param):
    param_dict = {
          'awb':'airwaybill_number',
          'ptype':'product_type',
          'item_desc':'item_description',
          'ch_wt':'chargeable_weight',
          'v_wt':'volumetric_weight',
          'cod_amt':'collectable_value',
          'u_org':'pickup__service_centre__center_shortcode',
          'o_dest':'original_dest__center_shortcode',
          'r_dest':'service_centre__center_shortcode',
          'shipper':'shipper__name',
          'pincode':'shipmentextension__original_pincode',
          'pickup_date':'added_on',
          'status':'status',
          'orig_expected_date':'shipmentextension__orig_expected_dod',  
          'remark':'remark',
          'rcode':'reason_code',
        } 


def data_report(request=None, params=None):
    file_name = "/data_report.csv"
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    csv_out = open(path_to_save,"wb")
    mywriter = csv.writer(csv_out)
    u = ("Air Waybill No","Product Type", "Item Description", "Chargeable Weight", "Vol Weight", "COD Amount",
             "Uploaded Origin", "Manifest Origin", "Original Destination", "Redirected Destination", "Shipper", "Orig Pincode",
             "P/U Date", "Status", "Original Expected Date", "Remarks", "Reason Code", "Misroute", "Delay Code","First S/U Date", "New Air Waybill (RTS)",
             "RTS`d on", "RTS Status", "Updated On","Misroute")
    mywriter.writerow(u)
    current_date = datetime.datetime.now().date()
    todays_date = current_date.strftime('%Y-%m-%d')
    first_date = current_date.strftime('%Y-%m-01') 
    #print todays_date, first_date
    shipment = Shipment.objects.filter(added_on__range=('2014-02-01', '2014-03-01')).exclude(rts_status=1).values_list('airwaybill_number','reverse_pickup','product_type','item_description','chargeable_weight','volumetric_weight','collectable_value','shipext__origin__center_shortcode','original_dest__center_shortcode','shipper__name','shipext__original_pincode','added_on','status','shipext__orig_expected_dod','shipext__remarks','reason_code__code','shipext__misroute_code__code','shipext__delay_code__code','ref_airwaybill_number','service_centre__center_shortcode')
    for a in shipment:
        try:
          status = get_internal_shipment_status(a[12])
        except:
          print a[12] 
        awb = a[18]
        rts_awb = Shipment.objects.filter(airwaybill_number=awb).values_list('airwaybill_number','added_on','updated_on','shipext__status_bk','shipext__misroute_code__code') if awb else ""
        rts_on=rts_awb[0][1] if rts_awb else ""
        rts_upd = rts_awb[0][2] if rts_awb else ""
        try: 
           rts_status = get_internal_shipment_status(rts_awb[0][3]) if rts_awb else ""  
           rts_misroute = rts_awb[0][4]
        except:
           rts_status = "" 
           rts_misroute = ""
        try:
          #su = str(a.statusupdate_set.all()[0].added_on.date())
           su = str(StatusUpdate.objects.filter(shipment__airwaybill_number=a[0])[0].added_on.date())
        except:
          su = ""
        ptype = "REV" if a[1] else a[2]
        rem = "Delivered" if a[12] == 9 else a[14]
        rd = a[8] if awb else a[19]
       # if a.rto_status or a.rts_status:
       #  rd = a[8]
        u = a[0], ptype, a[3], a[4], a[5], a[6], a[7], "", a[8], rd, a[9], a[10], a[11].date(), status, a[13], rem, a[15],  a[16], a[17], su, awb, rts_on, rts_status, rts_upd, rts_misroute
        try:
             mywriter.writerow(u)
        except:
              mywriter.writerow(unicode_removal(u))

data_report()
os.system('cd /home/web/ecomm.prtouch.com/ecomexpress/static/uploads && zip data_report.zip data_report.csv')
subject = "Data Report"
message = 'http://billing.ecomexpress.in/static/uploads/data_report.zip'
from_email = "support@ecomexpress.in"
to_email = ("samar@prtouch.com","sravank@ecomexpress.in","anshula@ecomexpress.in","jignesh@prtouch.com","jinesh@prtouch.com","onkar@prtouch.com")
#to_email = ("samar@prtouch.com",)
send_mail(subject,message,from_email,to_email)



