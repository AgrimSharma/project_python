import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
#from django.db.models import Q
from django.conf import settings
#import reports.ecomm_mail
from reports.ecomm_mail import ecomm_send_mail
from django.core.mail import send_mail
#from django.db.models import Count
#import service_centre.models
from service_centre.models import Customer,ServiceCenter, Shipment, ShipmentStatusMaster, StatusUpdate
from reports.report_api import ReportGenerator
import datetime
from django.db.models import get_model
from reports.ndr import *
#from utils import *
from billing.charge_calculations import price_updated,rts_pricing


def ws_retail_report():   
   shipper=Customer.objects.get(code=22092)
   ships=Shipment.objects.filter(shipper=shipper,shipment_date__month=4,shipment_date__year=2014)
   report=ReportGenerator('april_2014_wsretails_details.xlsx')
   headers=("AWB","Pikcup data","Chargeable Weight","Pickup SC","Destination ","Pincode","RTS Status","RTO Status","Freight Charge","Fuel Charge","Reverse Charge","RTO Charge","SDD Charge","SDL Charge","VCHC Charge","COd Charge")
   awb_data=[]
   print ships.count()
   for s in ships:
      cod=s.codcharge_set.filter()
      if cod:
         codcharge=cod[0].cod_charge
      else:
         codcharge=0
      u=(s.airwaybill_number,s.added_on.strftime("%d-%m-%Y %H:%M"),s.chargeable_weight,s.pickup.service_centre,s.original_dest,s.pincode,s.rts_status,s.rto_status,s.order_price_set.get().freight_charge,s.order_price_set.get().fuel_surcharge,s.order_price_set.get().reverse_charge,s.order_price_set.get().rto_charge,s.order_price_set.get().sdd_charge,s.order_price_set.get().sdl_charge,s.order_price_set.get().valuable_cargo_handling_charge,codcharge)                     
      awb_data.append(u)
   report.write_header(headers)
   report.write_body(awb_data)
   return "hi"

def run_bacdated():
   codes=[16252]
   #codes=[13010,56200,96047]
   for c in codes:
        print c
        cust=Customer.objects.get(code=c)
        ships=Shipment.objects.filter(shipper=cust,shipment_date__year=2014,shipment_date__month=7)
        print cust,ships.count()
        for s in ships:
         print "updated",s.airwaybill_number
         try:
           if s.rts_status<>1:
              price_updated(s)
           else:
              rts_pricing(s)
         except:
             print "exception",s.airwaybill_number
         print s.airwaybill_number,s.shipper
      




def ws_retail_cod():
   ships=Shipment.objects.filter(shipment_date__month=6,shipment_date__year=2014,product_type="cod")
   for s in ships:
     try:
       cod_charge(s)
       print s.airwaybill_number
     except:
       pass
   
   report=ReportGenerator('june_wsretail.xlsx')   
   headers=("AWB","Coll Val","COD Charge")
   report.write_header(headers)
   data=[]
   for s in ships:
     try:
       cod=s.codcharge_set.get()
       u=(s.airwaybill_number,s.collectable_value,cod.cod_charge)
       data.append(u)
     except:
       pass
   report.write_body(data)


#ws_retail_cod()
#ws_retail_report()
#run_awb_bcakdated()
run_bacdated()
