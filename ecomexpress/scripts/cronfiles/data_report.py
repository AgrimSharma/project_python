import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import Shipment, get_internal_shipment_status
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
          'm_org':'',
          'o_dest':'original_dest__center_shortcode',
          'r_dest':'service_centre__center_shortcode',
          'shipper':'shipper__name',
          'pincode':'shipmentextension__original_pincode',
          'pickup_date':'added_on',
          'status':'status',
          'orig_expected_date':'shipmentextension__orig_expected_dod',  
          'remark':'remark',
          'rcode':'reason_code'


def data_report():
    csv_out = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/data_report.csv","wb")
    mywriter = csv.writer(csv_out)
    u = ("Air Waybill No","Product Type", "Item Description", "Chargeable Weight", "Vol Weight", "COD Amount",
             "Uploaded Origin", "Manifest Origin", "Original Destination", "Redirected Destination", "Shipper", "Orig Pincode",
             "P/U Date", "Status", "Original Expected Date", "Remarks", "Reason Code", "Misroute", "Delay Code", "New Air Waybill (RTS)",
             "RTS`d on", "RTS Status", "Updated On","Misroute")
    mywriter.writerow(u)
    current_date = datetime.datetime.now().date()
    todays_date = current_date.strftime('%Y-%m-%d')
    first_date = current_date.strftime('%Y-%m-01') 
  
    shipment = Shipment.objects.filter(added_on__range=(first_date, todays_date))
    shipment = Shipment.objects.filter(airwaybill_number__in=['731811579', '700603442']).values_list('airwaybill_number','pickup__service_centre__center_name','shipmentextension__original_pincode')
    print shipment
    for a in shipment.iterator():
        status = get_internal_shipment_status(a.shipmentextension.status_bk)
        awb = a.ref_airwaybill_number if a.ref_airwaybill_number else ""
        rts_awb = Shipment.objects.get(airwaybill_number=awb) if awb else ""
        rts_on=rts_awb.added_on if rts_awb else ""
        rts_upd = rts.updated_on if rts_awb else ""
        rts_status = get_internal_shipment_status(rts_awb.shipmentextension.status_bk) if rts_awb else ""  
        print a.airwaybill_number, a.pickup.service_centre, a.shipmentextension.original_pincode
        u = "" 
        u = a.airwaybill_number, a.product_type, a.item_description, a.chargeable_weight, a.volumetric_weight, a.collectable_value, a.pickup.service_centre, "", a.original_dest, a.service_centre, a.shipper, a.shipmentextension.original_pincode, a.added_on, status, a.shipmentextension.orig_expected_dod, a.remark, a.reason_code,  "", "", awb, rts_on, rts_status, rts_upd, ""  
        
        try:
             mywriter.writerow(u)
        except:
              mywriter.writerow(unicode_removal(u))

subject = "Data Report"
message = 'http://ecomm.prtouch.com/static/uploads/data_report.csv'
from_email = "support@ecomexpress.in"
to_email = ("samar@prtouch.com",)
#send_mail(subject,message,from_email,to_email)


data_report()
