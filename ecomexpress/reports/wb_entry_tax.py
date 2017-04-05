import datetime
from service_centre.models import Shipment,Bags
from reports.report_api import ReportGenerator

def generate_wbtax_report(date_from,date_to,customer):
   now=datetime.datetime.now()
   awbs = []
   if customer == 0 or customer == "0":
     bags=Bags.objects.filter(destination__city__state__state_shortcode='WB',added_on__range=(date_from,date_to))
     for b in bags:
         for a in b.ship_data.filter().exclude(status__in=[6,7,8,9]):
             awbs.append(a)
     #awbs = Shipment.objects.filter(original_dest__city__state__state_shortcode='WB', shipment_date__range=(date_from,date_to))
   else:
     bags=Bags.objects.filter(destination__city__state__state_shortcode='WB',added_on__range=(date_from,date_to))
     for b in bags:
          for a in b.ship_data.filter(shipper__id=customer).exclude(status__in=[6,7,8,9]):
             awbs.append(a)
     #awbs = Shipment.objects.filter(original_dest__city__state__state_shortcode='WB', shipment_date__range=(date_from,date_to),shipper__id=customer)
   tmp=date_from+date_to+customer
   awbs= set(awbs)
   report = ReportGenerator('wb_entry_tax_{0}.xlsx'.format(tmp)) 
   col_heads=("Consignment Note No","C/Note Date","Import Date","Consignor Name","Consignor Address","Consignee Name","Consignee Address","Invoice No","Invoice Date","Invoice Value","Entry Tax [@ 1%]","Commodity","Quantity","Packages")
   awb_list=[]
   for a in awbs:
       address=""
       if a.consignee_address1 is not None:  
          address=address+a.consignee_address1
       if a.consignee_address2 is not None:
          address=address+a.consignee_address2  
       if a.consignee_address3 is not None:
          address=address+a.consignee_address3
       if a.consignee_address4 is not None:
          address=address+a.consignee_address4
       address=address[:99]
       if a.expected_dod is None:
          exp=now.strftime("%d/%m/%Y")
       else:
          exp=a.expected_dod.strftime("%d/%m/%Y")
       cust_address=str(a.pickup.subcustomer_code.address)
       cust_address=cust_address[:99]
       tax_value=float(a.declared_value*1.0/100.00)
       tax_value=round(tax_value,2)
       u=(a.airwaybill_number,a.added_on.strftime("%d/%m/%Y"),exp,str(a.pickup.subcustomer_code),cust_address,a.consignee,address,a.order_number,a.pickup.pickup_date.strftime("%d/%m/%Y"),a.declared_value,tax_value,"",1,1)
       awb_list.append(u)
   
   #if customer == 0 or customer == "0":
   #     awbs = Shipment.objects.filter(pickup__service_centre__city__state__state_shortcode='WB',  shipment_date__range=(date_from,date_to),rts_status=1)
   #else:
   #    awbs = Shipment.objects.filter(pickup__service_centre__city__state__state_shortcode='WB',  shipment_date__range=(date_from,date_to),rts_status=1,shipper__id=customer)
   #for a in awbs:
   #    address=""
   #    if a.consignee_address1 is not None:
   #        address=address+a.consignee_address1
   #    if a.consignee_address2 is not None:
   #       address=address+a.consignee_address2
   #    if a.consignee_address3 is not None:
   #       address=address+a.consignee_address3
   #    if a.consignee_address4 is not None:
   #       address=address+a.consignee_address4
   #    address=address[:99]
   #    if a.expected_dod is None:
   #        exp=now.strftime("%d/%m/%Y")
   #    else:
   #        exp=a.expected_dod.strftime("%d/%m/%Y") 
   #    cust_address=str(a.pickup.subcustomer_code.address)
   #    cust_address=cust_address[:99]
   #    tax_value=float(a.declared_value*1.0/100.00)
   #    tax_value=round(tax_value,2)
   #    u=(a.airwaybill_number,a.added_on.strftime("%d/%m/%Y"),exp,str(a.pickup.subcustomer_code),cust_address,a.consignee,address,a.order_number,a.pickup.pickup_date.strftime("%d/%m/%Y"),a.declared_value,tax_value,"",1,1)
   #    awb_list.append(u)
   report.write_header(col_heads)
   path=report.write_body(awb_list)
   return path
