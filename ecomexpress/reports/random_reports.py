
import sys
import re
import pdb
import xlrd
import datetime
from collections import defaultdict
from xlsxwriter.workbook import Workbook
#from openpyxl.reader.excel import load_workbook

from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Sum, Q, Count
from django.db.models.loading import get_model
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, send_mail

from service_centre.models import *
from service_centre.general_updates import update_shipment_pricing
from location.models import Pincode, ServiceCenter
from authentication.models import EmployeeMaster, Department
from airwaybill.models import AirwaybillCustomer, AirwaybillNumbers
from ecomm_admin.models import ShipmentStatusMaster, PickupStatusMaster
from reports.report_api import ReportGenerator, CSVReportGenerator, generate_zip
from reports.customer_emails import customer_emails_dict
from reports.ecomm_mail import ecomm_send_mail
from nimda.views import shipment_rts_creation
from customer.models import *
from billing.generate_bill_pdf import *
from billing.generate_bill_reports import *
from reports.ecomm_mail import ecomm_send_mail
from service_centre.models import *
from reports.models import Cluster,ClusterDCMapping,ClusterEmailMapping
from delivery.models import *
import csv

def update_rts_issues(awbs):
    for awb in awbs:
        s = Shipment.objects.get(airwaybill_number=awb)
        if s.rts_status == 2:
            print awb
            shipment_rts_creation(s)
        else:
            print 'not an rts 2 shipment ',awb
    print True

def data_main():
    a = []
    file_name = 'data_mainfeast.xlsx'
    report = ReportGenerator(file_name)
    col_heads = ("Date","Connection Id","Coloader Name", "Origin", "Destination", "Actual Weight", "Chargable Weight")
    report.write_header(col_heads)
#    con = Connection.objects.values_list('added_on','id','coloader__name','origin__center_name','destination__center_name','bags__shipments__actual_weight','bags__shipments__chargeable_weight').
    con = Connection.objects.filter(added_on__range=('2015-01-30 00:00:00','2015-01-31 23:59:59'))
    for c in con:
        data = Connection.objects.values_list('added_on','id','coloader','origin__center_name').filter(added_on__range=('2015-01-30 00:00:00','2015-02-02 23:59:59'))
        a.append(data)
        report.write_body(a)
    print file_name 
    
def bag_details(from_date, to_date):
    # get the connections for the given date range
    bag = Bags.objects.filter(
       added_on__range=(from_date + ' 00:00:00', to_date + ' 23:59:59'))
    # for each connection get the details required for reports
    #date #connection id #coloader name #origin #destination 
    #manifest weight (actual weight, chargeable weight)
    a = bag.count()
    report = ReportGenerator('Bag_details.xlsx')
    report.write_header(('Location', 'Count'))
#    for b in bag:
    row = bag.value_list('current_sc.center_shortcode')
    report.write_row(row)

    report.manual_sheet_close()
    print report.file_name

def holi_ships():
    i = []
    file_name = 'holi_mapping.xlsx'
    report = ReportGenerator(file_name)
    col_heads = ("Service Center","OFD","Delivered")
    report.write_header(col_heads)
    a = []
    def holi_punjab():
   # report.write_header(col_heads
        st=State.objects.get(state_name='Punjab')
        scs = ServiceCenter.objects.filter(city__state_id=st.id)
        for sc in scs:
            data = DeliveryOutscan.objects.filter(added_on__range=('2014-01-01 00:00:00','2014-01-03 23:59:59'), origin=sc)
            x=sc.center_shortcode, data.aggregate(ct=Count('shipments__id'))['ct'], data.filter(shipments__status=9).aggregate(ct=Count('id'))['ct']
            a.append(x)
    def holi_jk():
        sta=State.objects.get(state_name='Jammu and Kashmir')
        scsa = ServiceCenter.objects.filter(city__state_id=sta.id)
        for sc in scsa:
            data = DeliveryOutscan.objects.filter(added_on__range=('2014-01-01 00:00:00','2014-01-03 23:59:59'), origin=sc)
            y=sc.center_shortcode, data.aggregate(ct=Count('shipments__id'))['ct'], data.filter(shipments__status=9).aggregate(ct=Count('id'))['ct']
            a.append(y)
    holi_punjab()
    holi_jk() 
    report.write_body(a)   

def test_report():
      col_heads=('Airway Bill','PinCode','Service CN')
      report = ReportGenerator('test_report.xlsx')
      report.write_header(col_heads)
      ship = Shipment.objects.values_list('airwaybill_number','pincode','service_centre__center_shortcode').exclude(original_dest_id=None).filter(original_dest__city__city_name='MUMBAI',added_on__range=('2014-02-10','2014-02-25'))
      report.write_body(ship)
      filename = report.manual_sheet_close()
      return filename

def mapping_report():
    col_heads=('State Name','City Name','Service CN','Pincode')
#    file_name = 'city_mapping.xlsx'

    report = ReportGenerator('city_mapping.xlsx')
    report.write_header(col_heads)

    data = Pincode.objects.values_list('service_center__address__state__state_name','service_center__city__city_name',
                                   'service_center__center_name','pincode')
    report.write_body(data)
    filename = report.manual_sheet_close()
    return filename

def customer_list():
    report = ReportGenerator('customer_list.xlsx') #billing.ecomexpress.in/static/uploads/reports/file_name.xlx
    report.write_header(('id', 'code', 'name','address1', 'address2', 'address3','address4','city','state','pincode','phone'))
    customer = Customer.objects.values_list('id','code','name', 'address__address1', 'address__address2', 'address__address3','address__address4','address__city','address__state','address__pincode','address__phone')
    path = report.write_body(customer)
    print path

def zone_city_map():
    report = ReportGenerator('zone_city_map.xlsx') #billing.ecomexpress.in/static/uploads/reports/file_name.xlx
    report.write_header(['Zone', 'City'])
    zones = Zone.objects.all()
    data = zones.values_list('zone_name', 'city__city_name')
    path = report.write_body(data)
    print path

def all_customers():
    r=ReportGenerator('customers.xlsx')
    data = Customer.objects.values_list('id', 'code', 'name')
    path = r.write_body(data)
    print patawb, sh

def employee_master_report():
    report = ReportGenerator('employee_master.xlsx')
    print 'employee master report...'
    report.write_header(('Employee code', 'Name', 'Designation', 'Location','Customer'))
    data = EmployeeMaster.objects.filter(ebs=1).values_list('employee_code', 'firstname', 'lastname', 'department__name',
                'service_centre__center_shortcode','ebs_customer__name').exclude(staff_status=2)#.exclude(employee_code__istartswith='v')
    data = [ (d[0], d[1] + ' ' + d[2], d[3], d[4], d[5]) for d in data]
    path = report.write_body(data)
    print path

def employee_map():
    report = ReportGenerator('outsource_employee_master.xlsx')
    report.write_header(('Employee code', 'First Name', 'Last Name', 'Location'))
    data = EmployeeMaster.objects.filter(employee_code__istartswith='v').values_list('employee_code', 'firstname',
                   'lastname', 'service_centre__center_shortcode').exclude(staff_status=2)
    path = report.write_body(data)
    print path

def lost_shipments_report():
    col_heads=('AWB',  'updated_on')
    file_name = 'lost_shipments.xlsx'

    report = ReportGenerator(file_name)
    report.write_header(col_heads)

    ships = Shipment.objects.filter(reason_code__code=333).values_list('airwaybill_number', 'updated_on')
    data = list(ships)
    op = report.write_body(data)
    print op

def dc_codes():
    file_name = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/data.xls'
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_index(0)

    awbs = sh.col_values(0)[1:]
    data = []
    for awb in awbs:
        s = Shipment.objects.get(airwaybill_number=awbs)
        history = get_shipment_history(s)
        try:
            sh = history.objects.filter(shipment=s, reason_code__code__in=[206, 777]).latest('id').current_sc.center_name
            data.append((awb, dc))
        except:
            pass

    report = ReportGenerator('dc_codes.xlsx')
    report.write_header(('AWB', 'Redirected DC'))
    path = report.write_body(data)
    print path


def delivered_ships_tv18(start_date, end_date):
    ships = Shipment.objects.filter(shipper__id=7, status=9, shipment_date__range=(start_date, end_date)).exclude(rts_status=1)\
                    .values_list('airwaybill_number', 'order_number', 'added_on', 'collectable_value', 'original_dest__center_name')
    data = []
    for ship in ships:
        print ship[0]
        date = StatusUpdate.objects.filter(shipment__airwaybill_number=ship[0], reason_code__id=1).latest('id').date.strftime('%Y-%m-%d')
        data.append((ship[0], ship[1], ship[2], ship[3], 'Delivered', ship[4], date))

    report = ReportGenerator('delivered_ships_tv18.xlsx')
    report.write_header(('AWB', 'Order Number', 'Pickup Date', 'COD Amount', 'Status', 'Destination', 'Delivery Date'))
    path = report.write_body(data)
    print path

def unclosed_ships():
    col_heads = ("Air Waybill No","Order No", "Item Desctiption", "Added On", "Origin", "Destination", "Shipper", "Consignee", "Collectable Value", "Declared Value", "Reason code", "Reason")
    data = list(Shipment.objects.using('local_ecomm')\
            .filter(status__lte=8, added_on__range=('2014-04-01 00:00:00', '2014-04-30 23:59:59'))\
            .exclude(rts_status=2)\
            .exclude(shipper__code=32012)\
            .exclude(reason_code__code__in=[111, 777, 999, 888, 333, 310])\
            .values_list('airwaybill_number', 'order_number', 'item_description', 'added_on', 'pickup__service_centre__center_name', 'original_dest__center_name', 'shipper__name', 'consignee', 'collectable_value', 'declared_value', 'reason_code__code', 'reason_code__code_description'))

    report = ReportGenerator('open_ships_{0}.xlsx'.format('2014_04'))
    report.write_header(col_heads)
    path = report.write_body(data)
    ecomm_send_mail('Open Ships February', path, ['onkar@prtouch.com'])
    return files_list

def jasper_mar_ships():
    col_heads = ("Air Waybill No","S/D Origin", "Del Date", "Del Time", "1st OS", "1st RC")
    sh = Shipment.objects.using('local_ecomm').filter(added_on__range = ('2014-03-01','2014-04-01'), shipper__code = 92006).exclude(rts_status=1)
    csv_out = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/jsmar1.csv","wb")
    mywriter = csv.writer(csv_out)
    mywriter.writerow(col_heads)
    for a in sh:
          hist = a.shipmenthistory_2014_03_set.using('local_ecomm').filter(status__in=[0,6,7,8,9])
          org = hist[0].current_sc

          dc_date = hist.filter(status=6)[0].updated_on.date() if hist.filter(status=6) else ""
          dc_time = hist.filter(status=6)[0].updated_on.time() if hist.filter(status=6) else ""
          os = hist.filter(status=7)[0].updated_on.time() if hist.filter(status=7) else ""
          rc = hist.filter(status__in=[8,9])[0].reason_code if hist.filter(status__in=[8,9]) else ""
          u = (a.airwaybill_number, org, dc_date, dc_time, os, rc)
          mywriter.writerow(u)
    ecomm_send_mail('Jasper March 2014', "http://cs.ecomexpress.in/static/uploads/jsmar1.csv", ['samar@prtouch.com','sravank@ecomexpress.in','jignesh@prtouch.com'])

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def report_202():
    now = datetime.datetime.now()
    col_heads = ("AWB No","Order No","Pickup Date","Origin", "Destination","202 Updation Date", "Current Status Code", "Current Status Code Updation Date")
    sh = Shipment.objects.using('local_ecomm').filter(shipper__code = 11007, added_on__month = now.month, added_on__year = now.year)\
          .values_list('airwaybill_number','order_number','added_on','pickup__service_centre__center_shortcode','original_dest__center_shortcode',
                  'reason_code__code_description','shipext__updated_on')
    csv_out = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/report202.csv","wb")
    mywriter = csv.writer(csv_out)
    dt = ("MIS Date: " + str(now.date()),)
    mywriter.writerow(dt)
    mywriter.writerow(col_heads)
    for a in sh.iterator():
          hist1 = ShipmentHistory_2014_04.objects.using('local_ecomm').filter(shipment__airwaybill_number=a[0], reason_code__code = 202).values_list('updated_on')
          if hist1:
                 u = (a[0], a[1], a[2], a[3], a[4], hist1[0][0], a[5], a[6])
                 mywriter.writerow(u)
    #ecomm_send_mail('333/311 Report', "http://cs.ecomexpress.in/static/uploads/rep311.csv", ['samar@prtouch.com','sravank@ecomexpress.in','jignesh@prtouch.com'])
    ecomm_send_mail('Status Code 202 - Pod correction Report', "http://cs.ecomexpress.in/static/uploads/report202.csv", ["aakar.jain@homeshop18.com",
                    "abhay.kumar@homeshop18.com", "kunal.goel@homeshop18.com", "Roshan.Kumar@network18online.com",
                    "Ashok.Bisht@network18online.com", "Akhilesh.Srivastava@network18online.com", "balwinders@ecomexpress.in",
                    "sunainas@ecomexpress.in", "samar@prtouch.com", "jignesh@prtouch.com"])

def first_undel():
    col_heads = ("Air Waybill No","P/U Date","Shipper","Pincode", "Destination", "1st OS Date", "1st RC", "Last RC", "Last RC Date", "Total OS")
    sh = Shipment.objects.using('local_ecomm').filter(added_on__range = ('2014-01-01','2014-05-01'))
    csv_out = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/first_undel.csv","wb")
    mywriter = csv.writer(csv_out)
    mywriter.writerow(col_heads)
    for a in sh.iterator():
          os = a.deliveryoutscan_set.all()
          rc = a.statusupdate_set.all()
          if os and rc:
              os_date = os[0].added_on.date()
              rcc = rc[0].reason_code
              if rcc.id == 1:
                  continue
              lrc = rc.latest('id')
              lrc_code = lrc.reason_code
              lrc_date = lrc.added_on.date()
              total_os = os.count()
          else:
             os = ""
             rc = ""
             lrc = ""
             lrc_code = ""
             lrc_date = ""
             total_os = ""
          u = (a.airwaybill_number, a.added_on, a.shipper, a.shipext.original_pincode, a.original_dest, os_date, rcc, lrc_code, lrc_date, total_os)
          mywriter.writerow(u)
    #ecomm_send_mail('333/311 Report', "http://cs.ecomexpress.in/static/uploads/rep311.csv", ['samar@prtouch.com','sravank@ecomexpress.in','jignesh@prtouch.com'])
    ecomm_send_mail('Undel Report', "http://cs.ecomexpress.in/static/uploads/first_undel.csv", ['samar@prtouch.com'])


def unclosed_ships_rev():
     csv_out = open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/unclosedmar.csv","wb")
     mywriter = csv.writer(csv_out)
     col_heads = ("Air Waybill No","Order No", "Item Description", "Added On", "Origin", "Current Destination", "Orig Destintion", "Shipper", "Consignee", "Collectable Value", "Declared Value", "Reason code", "Reason")
     mywriter.writerow(col_heads)
     shipments = Shipment.objects.using('local_ecomm')\
            .filter(status__lte=8, added_on__range=('2014-03-01', '2014-04-01'))\
            .exclude(rts_status=2)\
            .exclude(shipper__code=32012)\
            .exclude(reason_code__code__in=[111, 777, 999, 888, 333, 310])
     print shipments.count()
     for a in shipments:
                    upd_time = a.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    hist1 = shipment_history.objects.filter(shipment=a).exclude(status__in=[11,12,16])
                    if hist1.filter(reason_code__code__in = [111, 777, 999, 888, 333, 310]):
                          continue
                    try:
                      rc = a.reason_code if a.reason_code else hist1.filter(reason_code__isnull = False).latest('updated_on').reason_code
                    except:
                      print a.airwaybill_number
                      continue
                    u = (a.airwaybill_number, removeNonAscii(a.order_number), removeNonAscii(a.item_description), a.added_on, a.pickup.service_centre, a.service_centre, a.original_dest, a.shipper, removeNonAscii(a.consignee), a.collectable_value, a.declared_value, rc.code, rc.code_description)
                   # print u
                    mywriter.writerow(u)

     os.system('cd /home/web/ecomm.prtouch.com/ecomexpress/static/uploads && zip unclosedmar.zip unclosedmar.csv')
     ecomm_send_mail('Open Ships 2013', "http://cs.ecomexpress.in/static/uploads/unclosedmar.zip", ['samar@prtouch.com'])

def thane_details():
    report = ReportGenerator('thane_dc_details_in.xlsx')
    report.write_header(('AWB', 'Pickup Date', 'Shipper Name', 'Shipper Address', 'Consignee', 'Consignee Address', 'Invoice Number', 'Product Description', 'COD Amount', 'Declared Value', 'Actual Weight', 'Origin', 'Destination'))
    sc = ServiceCenter.objects.get(center_shortcode='THN')
    ships = Shipment.objects.filter(original_dest=sc)
    print ships.only('id').count()
    data = []
    count = 0
    for s in ships:
        p = Product.objects.get(product_name=s.product_type)
        try:
            s.shipext.product = p
            s.shipext.save()
        except ShipmentExtension.DoesNotExist:
            ShipmentExtension.objects.create(shipment=s, product=p)
        print s.airwaybill_number

    path = report.write_body(data)
    print path

def thane_details_out():
    report = ReportGenerator('thane_dc_details_out.xlsx')
    report.write_header(('AWB', 'Product Type', 'Pickup Date', 'Shipper Name', 'Shipper Address','Shipper Address','Shipper Address','Shipper Address', 'Consignee', 'Consignee Address', 'Consignee Address', 'Consignee Address', 'Consignee Address', 'Invoice Number', 'Product Description', 'COD Amount', 'Declared Value', 'Actual Weight', 'Origin', 'Destination'))
    sc = ServiceCenter.objects.get(center_shortcode='THN')
    data = Shipment.objects.filter(Q(original_dest=sc) | Q(pickup__service_centre=sc)).values_list('airwaybill_number', 'product_type','added_on', 'shipper__name', 'shipper__address__address1', 'shipper__address__address2', 'shipper__address__address3', 'shipper__address__address4', 'consignee', 'consignee_address1', 'consignee_address2', 'consignee_address3', 'consignee_address4', 'order_number', 'item_description', 'collectable_value', 'declared_value', 'actual_weight', 'pickup__service_centre__center_name', 'original_dest__center_name')
    path = report.write_body(data)
    print path

def billing_summary_report():
    bills = Billing.objects.all().values_list('id', 'billing_date', 'customer__name', 'total_payable_charge').order_by('id')
    report = ReportGenerator('billing_details.xlsx')
    report.write_header(('Sr. No', 'Bill No', 'Bill Date', 'Customer', 'Bill Amount'))
    data = [(i, v[0], v[1] if v[1] else '', v[2], round(v[3], 2)) for i, v in enumerate(bills, start=1)]
    path = report.write_body(data)
    print path

def status_print():
    file_name = '/tmp/book1.xls'
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_name('Sheet1')
    report = ReportGenerator('item_descr.xlsx')
   # report.write_header(('AWB', 'status'))
    report.write_header(('AWB', 'Order No','Weight','Origin','Destination','Shipper', 'Consignee','status','Expected DOD'))
    awbs = sh.col_values(0)[1:]
    count = 1
    for awb in awbs:
        print count
        count += 1
        ship = Shipment.objects.get(airwaybill_number=awb)
        status = ship.status
        status_name = get_internal_shipment_status(status)
        report.write_row((awb,ship.order_number,ship.actual_weight,ship.pickup.service_centre.center_name,
            ship.original_dest.center_name,ship.shipper.name,ship.consignee,status_name,ship.expected_dod))

    sh = wb.sheet_by_name('Sheet2')
    awbs = sh.col_values(0)[1:]
    for awb in awbs:
        print count
        count += 1
        ship = Shipment.objects.get(airwaybill_number=awb)
        status = ship.status
        status_name = get_internal_shipment_status(status)
        report.write_row((awb,ship.order_number,ship.actual_weight,ship.pickup.service_centre.center_name,
            ship.original_dest.center_name,ship.shipper.name,ship.consignee,status_name,ship.expected_dod))
    sh = wb.sheet_by_name('Sheet3')
    awbs = sh.col_values(0)[1:]
    for awb in awbs:
        print count
        count += 1
        ship = Shipment.objects.get(airwaybill_number=awb)
        status = ship.status
        status_name = get_internal_shipment_status(status)
        report.write_row((awb,ship.order_number,ship.actual_weight,ship.pickup.service_centre.center_name,
            ship.original_dest.center_name,ship.shipper.name,ship.consignee,status_name,ship.expected_dod))

    file_name = report.manual_sheet_close()
    path = 'http://billing.ecomexpress.in/static/uploads/reports/'+file_name
    print path

def tv18_patna():
    report = ReportGenerator('tv18_patna.xlsx')
    report.write_header(('AWB', 'Order No','Pickup Date', 'Actual Weight', 'Chargeable Weight', 'Cod Amount', 'Origin','Destination','Shipper', 'Sub customer','Consignee','Expected DOD'))
    data = Shipment.objects.filter(shipment_date__range=('2014-03-01','2014-03-31'), original_dest__center_shortcode__in=['PAA', 'PAB']).values_list('airwaybill_number', 'order_number', 'added_on', 'actual_weight', 'chargeable_weight', 'collectable_value', 'pickup__service_centre__center_name', 'original_dest__center_name', 'shipper__name', 'pickup__subcustomer_code__name', 'consignee', 'expected_dod')
    report.write_body(data)

def bill_report(year,month):
    report = ReportGenerator('bill_summary_report.xlsx')
    report.write_header(('Bill_id', 'Customer Name','Invoice Summary','Invoice Summary(headless)',
        'Awb Excel','Awb Pdf'))
    bills = Billing.objects.filter(billing_date__year=year,billing_date__month =month )
    for bill in bills:
        bill_id = bill.id
        in_summary_url = get_filename(bill_id, 'bill_wise', 'pdf')
        in_summary ='http://billing.ecomexpress.in/static/uploads/billing/'+str(month)+'/'+os.path.split(in_summary_url)[1]

        in_summary_with_header_url = get_filename(bill_id, 'bill_wise_without_header', 'pdf')
        in_summary_with_header ='http://billing.ecomexpress.in/static/uploads/billing/'+str(month)+'/'+os.path.split(in_summary_with_header_url)[1]
        customer_name = bill.customer.name
        print bill_id
        gen_awb = GenerateAwbPdf(bill_id)
        awb_pdf_url = gen_awb.get_filename('awb_wise', 'pdf')
        awb_pdf ='http://billing.ecomexpress.in/static/uploads/billing/'+str(month)+'/'+os.path.split(awb_pdf_url)[1]
        awb_excel_url = gen_awb.get_filename('awb_excel', 'xlsx')
        awb_excel ='http://billing.ecomexpress.in/static/uploads/billing/'+str(month)+'/'+os.path.split(awb_excel_url)[1]
        report.write_row((bill_id,customer_name,in_summary,in_summary_with_header,awb_excel,awb_pdf))
    file_name = report.manual_sheet_close()
    path = 'http://billing.ecomexpress.in/static/uploads/reports/'+file_name
    print path

def jasper_billing_report():
    report = ReportGenerator('jasper_invoice_april_2014.xlsx')
    report.write_header(('Forward Waybill number','RTO Waybill number','Sub-order / Refrence number','Order date',
        'Origin City','Destination City','Payment Mode','TYPE','Zone/Lanes','1 st slab rate/500gm','Next slab rate/500gm',
        'Product bill value','COD Amount','Amount collected','Delivery status','Dead Weight (gms)',
        'L','B','H','VOL WT IN GMS','Billed WT Type','Billed Wt (gms)','FORWARD FRT Charges','FSC Charges',
        'RTO Charges','COD Charges','Net Amount','S tax','Grand Total'))
    cust=Customer.objects.get(code=92006)
    ships=Shipment.objects.filter(shipment_date__month=3,shipment_date__year=2014,shipper=cust)[2:]
    for ship in ships:
        print ship.airwaybill_number,'  start'
        if ship.rto_status == 1:
            ship_type = 'RTO'
        elif ship.rts_status:
            ship_type = 'RTS'
        else:
            ship_type ='FRWRD'
        first_slab = 0
        next_slab = 0
        if ship.pickup.service_centre.city_id==21:
            fs=FreightSlabDestZone.objects.filter(customer=cust,dest_zone=ship.original_dest.city.zone,city_org=ship.pickup.service_centre.city)
            for f in fs:
                first_slab = f.rate_per_slab
                next_slab = f.rate_per_slab
        elif ship.original_dest.city_id==21:
            fs = FreightSlabOriginZone.objects.filter(customer=cust,org_zone=ship.pickup.service_centre.city.zone,city_dest__id=21)
            for f in fs:
                first_slab = f.rate_per_slab
                next_slab = f.rate_per_slab
        else:
            fs=FreightSlab.objects.filter(customer=cust)
            if fs:
                fsz=FreightSlabZone.objects.filter(freight_slab=fs[0],zone_org=ship.pickup.service_centre.city.zone,zone_dest=ship.original_dest.city.zone)
                if fsz:
                    first_slab = fsz[0].rate_per_slab
                fsz=FreightSlabZone.objects.filter(freight_slab=fs[1],zone_org=ship.pickup.service_centre.city.zone,zone_dest=ship.original_dest.city.zone)
                if fsz:
                    next_slab = fsz[0].rate_per_slab

        order = ship.order_price_set.get()

        net_amount = order.freight_charge+order.fuel_surcharge+order.rto_charge+ship.collectable_value
        s_tax = net_amount*(1.1236/100)
	g_total = net_amount + s_tax

        value_li = []
        value_li.append(ship.airwaybill_number) # Forward Waybill number
        value_li.append(ship.ref_airwaybill_number) # RTO Waybill number
        value_li.append(ship.order_number) # Sub-order / Refrence number
        value_li.append(ship.added_on) # Order date
        value_li.append(ship.pickup.service_centre.city) # Origin City
        value_li.append(ship.original_dest.city) # Destination City
        value_li.append(ship.product_type) # Payment Mode
        value_li.append(ship_type) # TYPE
        value_li.append(ship.pickup.service_centre.city.zone) # Zone/Lanes

        value_li.append(first_slab) # 1 st slab rate/500gm
        value_li.append(next_slab) # Next slab rate/500gm

        value_li.append(ship.declared_value) # Product bill value
        value_li.append(ship.collectable_value) # COD Amount

        value_li.append(ship.collectable_value) # Amount collected ****
        value_li.append(ship.reason_code.code_description) # Delivery status
        value_li.append(ship.actual_weight) # Dead Weight (gms)
        value_li.append(ship.length) # L
        value_li.append(ship.breadth) # B
        value_li.append(ship.height) # H
        value_li.append(ship.volumetric_weight) # VOL WT IN GMS

        value_li.append('') # Billed WT Type***
        value_li.append(ship.chargeable_weight) # Billed Wt (gms)

        value_li.append(order.freight_charge) # FORWARD FRT Charges
        value_li.append(order.fuel_surcharge) # FSC Charges
        value_li.append(order.rto_charge) # RTO Charges
        value_li.append(ship.collectable_value) # COD Charges
    
        value_li.append(net_amount) # Net 
        value_li.append(s_tax) # S tax
        value_li.append(g_total) # Grand Total
        value = tuple(value_li)
	print ship.airwaybill_number

        report.write_row(value)
    file_name = report.manual_sheet_close()
    path = 'http://billing.ecomexpress.in/static/uploads/reports/'+file_name
    print path


def invice_customer_save():
    file_name = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/cuname.xls'
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_index(0)
    rowSize = sh.nrows-1
    for rownum in range(sh.nrows):
        if rownum ==1: 
            pass
        elif rownum ==0:
            pass
        else:
            data = sh.row_values(rownum)
            try:
                customer = Customer.objects.get(code = int(data[1]))
                CustomerReportNames.objects.create(customer = customer, invoice_name = data[3],cash_tally_name = data[2])
            except Customer.DoesNotExist:               
                pass

def ebs_product():
    report = ReportGenerator('ebs_shipments_report.xlsx')
    report.write_header(('AWB', 'Orgin', 'Destination','Actual weight','Chargeable Weight','Pickup Date','Employee Code'))
    shipments = Shipment.objects.filter(added_on__month=04,added_on__year=2014,shipext__product__product_name__in=['ebsppd','ebscod'])
    data = []
    for ship in shipments:
       delivery_emp_id = ''
       for su in ship.statusupdate_set.all():
           delivery_emp_id = su.delivery_emp_code_id
       print ship.airwaybill_number
       data.append((ship.airwaybill_number,ship.pickup.service_centre,ship.original_dest,ship.shipext.original_act_weight,ship.chargeable_weight,ship.added_on.date(),delivery_emp_id))
    report.write_body(data)


def outscan_performance_report():
      type=0
      ebs = 0
      q = Q()
      ebsq = Q()
      ebsq1 = Q()
      if ebs:
         ebsq = (Q(shipments__airwaybill_number__startswith = 3) | Q(shipments__airwaybill_number__startswith = 4))
         ebsq1 = (Q(shipment__airwaybill_number__startswith = 3) | Q(shipment__airwaybill_number__startswith = 4))
      if type == 1:
         end_date = datetime.datetime.now().date()
         start_date = now.date() - datetime.timedelta(days=1)
      else:
         date_from = "2014-04-1"
         date_to = "2014-04-30"
         start_date = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
         end_date = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()

      report = CSVReportGenerator("/outscan_del_%s.csv"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s")))
      report.write_row(("Date", "Employee Code", "Employee Name", "Service Centre", "OFD", "Delivered", "%", "MTD OFD", "MTD Delivered", "%"))

      while start_date <= end_date:
            em = EmployeeMaster.objects.using('local_ecomm').filter(user_type = "Staff").exclude(staff_status=2).filter(q).order_by('service_centre')
            for emp in em:
                total_dcount = DeliveryOutscan.objects.using('local_ecomm').filter(ebsq, added_on__gte=start_date, added_on__lt=(start_date + datetime.timedelta(days = 1)),
                              employee_code=emp,shipments__rts_status__in = [0], shipments__reverse_pickup__in=[0]).values('employee_code__employee_code').annotate(Count('shipments'))
                totd = total_dcount[0]['shipments__count'] if total_dcount else 0
                os_tot = DeliveryOutscan.objects.using('local_ecomm').filter(added_on__gte=start_date, added_on__lt=(start_date + datetime.timedelta(days = 1)),
                              employee_code=emp)

                total_mcount = DeliveryOutscan.objects.using('local_ecomm').filter(ebsq, added_on__month=start_date.month, added_on__lt=(start_date + datetime.timedelta(days = 1)),
                              employee_code=emp,shipments__rts_status__in = [0], shipments__reverse_pickup__in=[0]).values('employee_code__employee_code').annotate(Count('shipments'))
                totm = total_mcount[0]['shipments__count'] if total_mcount else 0
                if totm == 0:
                   continue
                os_mom = DeliveryOutscan.objects.using('local_ecomm').filter(added_on__month=start_date.month, added_on__lt=(start_date + datetime.timedelta(days = 1)),
                              employee_code=emp)

                deld_dcount = DOShipment.objects.using('local_ecomm').filter(ebsq1, added_on__gte=start_date, added_on__lt=(start_date + datetime.timedelta(days = 1)),status=1, deliveryoutscan__employee_code=emp, shipment__rts_status__in = [0], shipment__reverse_pickup__in=[0], deliveryoutscan__in=os_tot).values('deliveryoutscan__employee_code__employee_code').annotate(Count('id'))
                deldd = deld_dcount[0]['id__count'] if deld_dcount else 0
                deld_mcount = DOShipment.objects.using('local_ecomm').filter(ebsq1, added_on__month=start_date.month, added_on__lt=(start_date + datetime.timedelta(days = 1)),status=1, deliveryoutscan__employee_code=emp, shipment__rts_status__in = [0], shipment__reverse_pickup__in=[0], deliveryoutscan__in=os_mom).values('deliveryoutscan__employee_code__employee_code').annotate(Count('id'))
                deldm = deld_mcount[0]['id__count'] if deld_mcount else 0
                perc = round(float((deldd * 100)/totd),2) if totd else 0
                mtd_perc = round(float((deldm * 100)/totm),2) if totm else 0
                if not emp.service_centre:
                    continue

                report.write_row((str(start_date), str(emp.employee_code), str(emp.firstname), str(emp.service_centre.center_shortcode), totd, deldd,
                    perc, totm, deldm, mtd_perc))
            start_date += delta
            file_name = report.manual_sheet_close()
            path = 'http://billing.ecomexpress.in/static/uploads/reports/'+file_name
            print path

def reverse_shipment_report():
    col_heads = [
      'Airwaybill Number',
      'Order ID',
      'Reverse Pickup ID',
      'Reverse Shipment ID',
      'Registered Date',
      'Pickup Location',
      'Destination',
      'Customer Name',
      'Shipper Name',
      'Shipper Address',
      'Phone Number',
      'Item Description',
      'Current Status',
      'Reason Code',
      'Remark']

    customer = 6
    date_from = '2014-04-01'
    date_to = '2014-05-30'
    origin = 0
    q = Q()
    q = q & Q(shipper__id = int(customer))
    if date_from and date_to:
      t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
      date_to = t.strftime("%Y-%m-%d")
      q = q & Q(added_on__range=(date_from, date_to))

    reverse_shipments = ReverseShipment.objects.filter(q)

    report = CSVReportGenerator("reverse_shipment_reprt.csv")
    report.write_row(col_heads)
    for row, reverse_shipment in enumerate(reverse_shipments, start=3):
      ad1 = reverse_shipment.pickup_consignee_address1 if reverse_shipment.pickup_consignee_address1 else u''
      ad2 = reverse_shipment.pickup_consignee_address2 if reverse_shipment.pickup_consignee_address2 else u''
      ad3 = reverse_shipment.pickup_consignee_address3 if reverse_shipment.pickup_consignee_address3 else u''
      ad4 = reverse_shipment.pickup_consignee_address4 if reverse_shipment.pickup_consignee_address4 else u''
      address = ad1 + ad2 + ad3 + ad4

      if reverse_shipment.reason_code:
          desc = str(reverse_shipment.reason_code)
      else:
          desc = ''
      added_date = reverse_shipment.added_on.strftime('%Y/%m/%d') if reverse_shipment.added_on else ''
      if reverse_shipment.vendor:
          try:
             dest = Pincode.objects.get(pincode=reverse_shipment.vendor.address.pincode).service_center.center_name
          except:
             dest = ''
      else:
          dest = ''
      rsc = reverse_shipment.pickup_service_centre.center_name if reverse_shipment.pickup_service_centre else ''
      cs = 'Pending' if reverse_shipment.status == 0 else 'Completed'

      row = (reverse_shipment.airwaybill_number, reverse_shipment.order_number, reverse_shipment.reverse_pickup.id, reverse_shipment.id,
 added_date, rsc, dest, reverse_shipment.pickup_consignee, reverse_shipment.shipper.name, address, reverse_shipment.mobile,
 reverse_shipment.item_description, cs, desc, reverse_shipment.remark)
      report.write_row(row)
    ecomm_send_mail('Reverse Shipment Report', 'http://billing.ecomexpress.in/static/uploads/reports/reverse_shipment_report.csv', ['sravank@ecomexpress.in', 'jinesh@prtouch.com'])


def update_ships():
    file_name = '/tmp/ibibo.xls'
    print file_name
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_index(0)

    awbs = sh.col_values(0)[1:]
    ord_num = sh.col_values(1)[1:]
    name = sh.col_values(2)[1:]
    address = sh.col_values(3)[1:]
    pincode = sh.col_values(4)[1:]
    phone = sh.col_values(5)[1:]
    item_description = sh.col_values(6)[1:]
    pieces= sh.col_values(7)[1:]
    collectable_value = sh.col_values(8)[1:]
    declared_value = sh.col_values(9)[1:]

    t = zip(awbs, ord_num, name, address, pincode, phone, item_description, pieces, collectable_value, declared_value)
    for i in t:
        print i
        Shipment.objects.filter(airwaybill_number=i[0]).\
            update(order_number=i[1], consignee=i[2], consignee_address1=i[3], pincode=i[4], mobile=i[5],
                item_description=i[6], pieces=i[7], collectable_value=i[8], declared_value=i[9])


def cluster_dcmapping(file_name):
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_index(0)
    cl_name = sh.col_values(0)[1:]
    dc = sh.col_values(1)[1:]
    cl_dc_list = []
    cluster_dc = zip(cl_name,dc)
    for cl_dc in cluster_dc:
        try:
            cl = Cluster.objects.get(cluster_name=cl_dc[0])
            sc = ServiceCenter.objects.get(center_shortcode=cl_dc[1])
            cl_dcmap = ClusterDCMapping.objects.create(cluster=cl,dc_code=sc)
        except ServiceCenter.DoesNotExist:
           cl_dc_list.append(cl_dc)
    return cl_dc_list


def cluster_emailmapping(file_name):
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_index(0)
    cl_name = sh.col_values(0)[1:]
    email = sh.col_values(1)[1:]
    cl_dc_list = []
    cluster_dc = zip(cl_name,email)
    for cl_dc in cluster_dc:
        try:
            cl_emailmap = ClusterEmailMapping.objects.create(cluster=Cluster.objects.get(cluster_name=cl_dc[0]),email=cl_dc[1])
        except Cluster.DoesNotExist:
            cl_dc_list.append(cl_dc)
    return cl_dc_list


def awb_details():
    # get airwaybill list from excel file
    file_name = '/tmp/awbs.xls'
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_index(0)
    awbs = sh.col_values(0)[1:]
    # create report object from reportgenerator class
    report = ReportGenerator('shipment_details.xlsx')
    # write header
    report.write_header(('Awb', 'Order Number', 'Customer Name','Cod Amount', 'Delivary Date', 'Rts No'))
    # get data matrix from shipment table
    data = Shipment.objects.filter(airwaybill_number__in=awbs)\
            .values_list('airwaybill_number', 'order_number', 'shipper__name', 'collectable_value', 'shipext__delivered_on', 'rts_status')
    # write body to report
    path = report.write_body(data)

def fashionara_update():
    file_name = '/tmp/data.xls'
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_index(0)
    awbs = sh.col_values(0)[1:]
    awbs = [int(a) for a in awbs]
    origin = ServiceCenter.objects.get(center_shortcode='DEP')

    report = CSVReportGenerator('bag_details.csv')
    # write header
    report.write_row(('Air Waybill No',  'Baggin at Origin Date',  'Bag Inscan Date at DEP',  'Bag Inscan Time at DEP',  'Bagging Completion at DEP', 'Bag Inscan at delivery Center'))
    #awbs = [707455355, 706845464]
    #pdb.set_trace()
    for awb in awbs:
        s = Shipment.objects.get(airwaybill_number=awb)
        bags = s.shipment_data.all().order_by('id')
        if not bags:
            continue
        first_bag = bags[0]
        fbag_history = BaggingHistory_2014_06.objects.filter(bag=first_bag, remarks__contains="closed")
        if fbag_history:
            bagging_at_origin = fbag_history[0].updated_on.strftime('%Y-%m-%d')
        else:
            bagging_at_origin = ''

        # bag inscan date and time at dep
        inscan_at_dep = BaggingHistory_2014_06.objects.filter(bag__in=bags, bag_sc=origin, remarks__contains='debagged')
        if inscan_at_dep:
            bag_inscan_date = inscan_at_dep[0].updated_on.strftime('%Y-%m-%d')
            bag_inscan_time = inscan_at_dep[0].updated_on.strftime('%H:%m')
        else:
            bag_inscan_date = ''
            bag_inscan_time = ''

        # bagging completion at dep
        bagging_completion_dep = BaggingHistory_2014_06.objects.filter(bag__in=bags, bag_sc=origin, remarks__contains='closed')
        if bagging_completion_dep:
            bag_completion_at_dep = bagging_completion_dep[0].updated_on
        else:
            bag_completion_at_dep = ''

        # bag inscan at delivery center
        dc_inscan = BaggingHistory_2014_06.objects.filter(bag__in=bags, remarks__in='scanned at DC')
        if dc_inscan:
            inscan_at_dc = dc_inscan[0].updated_on
        else:
            inscan_at_dc = ''

        #print 'bagging_at_origin:{0} bag_inscan_date:{1} bag_inscan_time:{2} bag_completion_at_dep:{3} inscan_at_dc{4}'.format(bagging_at_origin, bag_inscan_date, bag_inscan_time, bag_completion_at_dep, inscan_at_dc)
        report.write_row((awb, bagging_at_origin, bag_inscan_date, bag_inscan_time, bag_completion_at_dep, inscan_at_dc))

def ebs_ships():
    ships = Shipment.objects.filter(
        shipment_date__range=('2014-06-01', '2014-06-30'), 
        shipext__product__product_name__in=['ebsppd', 'ebscod']
    ).values_list(
        'airwaybill_number', 
        'added_on',
        'pickup__service_centre__center_name',
        'original_dest__center_name',
        'actual_weight',
        'chargeable_weight'
    )
    report = ReportGenerator('ebs_june_shipments.xlsx')
    report.write_header(('AWB', 'Pickup Date', 'Origin', 'Destination', 'Act. Wt', 'Chargeable Wt'))
    report.write_body(ships)

def pwp(end_date, end_month, end_year):
    report = ReportGenerator('weekly_performance_monitor - MTD '+str(end_date)+'.xlsx')
    
    #today = str(end_year)+"-"+str(end_month)+"-"+str(end_day)
    enddate = datetime.date(end_year, end_month, end_date)
    #print type(end_date)
    startdate = today - datetime.timedelta(7)
    #print type(start_date)
    MTD_start_date = datetime.date(end_year, end_month, 1)

    # 09/02-15/02 "2015-02-09"

    start_date = startdate.strftime("%Y-%m-%d")
    end_date = enddate.strftime("%Y-%m-%d")
    MTD_start_date = MTD_start_date.strftime("%Y-%m-%d")
    week = 'Week : '+startdate.strftime("%d-%m")+"-"+enddate.strftime("%d-%m")
    #awbs = sh.col_values(0)[1:]"
    col_heads = ('Particulars', week, 'MTD-Gross', 'Proj-Gross Mth' )
    report.write_header(col_heads)
    
    weekly_shipments = Shipment.objects.using('local_ecomm').filter(shipment_date__range=[start_date, end_date])
    MTD_gross_shipments = Shipment.objects.using('local_ecomm').filter(shipment_date__range=[MTD_start_date, end_date])
    #Proj-Gross_Mth = 
    
    # Table rows start from here
    # Calculate sales using collectable_value
    # Populate Row 1
    Sales_PPD_INR_Mn =  weekly_shipments.aggregate(cv=Sum("collectable_value")).get('cv')
    Sales_PPD_INR_Mn_MTD =  MTD_gross_shipments.aggregate(cvm=Sum("collectable_value")).get('cvm')
    ROW1 = [ 'Sales-PPD (INR-Mn)', Sales_PPD_INR_Mn, Sales_PPD_INR_Mn_MTD]

    # Populate Row 2
    Sales_COD_INR_Mn = weekly_shipments.aggregate(cvc=Sum("collectable_value")).get('cvc')
    Sales_COD_INR_Mn_MTD = MTD_gross_shipments.aggregate(cvcm=Sum("collectable_value")).get('cvcm')
    ROW2 = [ 'Sales-COD (INR-Mn)', Sales_COD_INR_Mn, Sales_COD_INR_Mn_MTD]

    # Populate Row 3
    Total_INR_Mn = Sales_PPD_INR_Mn + Sales_COD_INR_Mn
    Total_INR_Mn_MTD = Sales_PPD_INR_Mn_MTD + Sales_COD_INR_Mn_MTD
    ROW3 = [ 'Total', Total_INR_Mn, Total_INR_Mn_MTD]

    # Calculate PPD, COD volumes
    # Populate Row 4
    Volumes_PPD = weekly_shipments.filter(product_type='ppd').count()
    Volumes_PPD_MTD = MTD_gross_shipments.filter(product_type='ppd').count()
    ROW4 = [ 'Volumes-PPD', Volumes_PPD, Volumes_PPD_MTD]
    
    # Populate Row 5
    Volumes_COD = weekly_shipments.filter(product_type='cod').count()
    Volumes_COD_MTD = MTD_gross_shipments.filter(product_type='cod').count()
    ROW5 = [ 'Volumes-COD', Volumes_COD, Volumes_COD_MTD]

    # Populate Row 6
    Volumes_Total = Volumes_PPD + Volumes_COD
    Volumes_Total_MTD = Volumes_PPD_MTD + Volumes_COD_MTD
    ROW6 = [ 'Total', Volumes_Total, Volumes_Total_MTD ]
    
    # Populate Row 7
    Yield_per_Shipt_PPD_INR = Sales_PPD_INR_Mn/Volumes_PPD
    Yield_per_Shipt_PPD_INR_MTD = Sales_PPD_INR_Mn_MTD/Volumes_PPD_MTD
    ROW7 = [ 'Yield/Shipt-PPD-INR', Yield_per_shipt_PPD_INR,  Yield_per_shipt_PPD_INR_MTD] 

    # Populate Row 8 
    Yield_per_Shipt_COD_INR = Sales_COD_INR_Mn/Volumes_PPD
    Yield_per_Shipt_COD_INR_MTD = Sales_COD_INR_Mn_MTD/Volumes_PPD_MTD
    ROW8 = [ 'Yield/Shipt-COD-INR', Yield_per_Shipt_COD_INR, Yield_per_Shipt_COD_INR_MTD]
    
    # Populate Row 9
    #Total = 
    #ROW9= Total

    # Populate Row 10
    Sales_Ratio_PPD =  "Sales-PPD-INR-Mn/"
    Sales_Ratio_PPD_MTD =  "Sales-PPD-INR-Mn-MTD/"
    ROW10= [ 'Sales Ratio_PPD', Sales_Ratio_PPD, Sales_Ratio_PPD_MTD]
    
    # Populate Row 11
    Sales_Ratio_COD = "Sales-COD-INR-Mn/"
    Sales_Ratio_COD_MTD = "Sales-COD-INR-Mn-MTD/"
    ROW11= [ 'Sales Ratio-COD', Sales_Ratio_COD_MTD, Sales_Ratio_COD_MTD]

    # Populate Row 12
    Volumes_Ratio_PPD =  Volumes_PPD/weekly_shipments
    Volumes_Ratio_PPD_MTD =  Volumes_PPD_MTD/MTD_gross_shipments
    ROW12 = [ 'Volumes Ratio-PPD', Volumes_Ratio_PPD, Volumes_Ratio_PPD ]
    
    # Populate Row 13
    Volumes_Ratio_COD =  Volumes_COD/weekly_shipments
    Volumes_Ratio_COD_MTD =  Volumes_COD_MTD/MTD_gross_shipments
    ROW13 = [ 'Volumes Ratio-COD', Volumes_Ratio_PPD, Volumes_Ratio_PPD  ]

    # Populate Row 14
    No_of_Towns = weekly_shipments.values('original_dest__city').distinct().count()
    ROW14 = [ 'No of Towns', 0, No_of_Towns ]

    # Populate Row 15
    No_of_DCs =  weekly_shipments.values('original_dest').distinct().count()
    ROW15 = [ 'No of DCs', 0, No_of_DCs ]

    # Populate Row 16
    No_of_Pincodes =  weekly_shipments.values('pincode').distinct().count()
    ROW16 = [ 'No of Towns', 0, No_of_Towns ]

    report_body = [ROW1, ROW2, ROW3, ROW4, ROW5, ROW, ROW7, ROW8, ROW9, ROW10, ROW11, ROW12, ROW13, ROW14, ROW15, ROW1]
    
    '''
    for i in xrange(1, 17):
        j = "ROW"+str(i)
        report_body.append(j)
    
    for awb in awbs:
        print awb
        data = Shipment.objects.get(airwaybill_number=awb)
        row_data = (data.airwaybill_number, data.deliveryoutscan_set.filter().count())
        report.write_row(row_data)
    '''

    report.write_body(report_body)
    report.manual_sheet_close()
    #return file_name

def bagging():
    file_name = 'bagging.xlsx'
    report = ReportGenerator(file_name)
    col_heads = ("Dc Code","Count")
    report.write_header(col_heads)
#    scs = ServiceCenter.objects.all()
#    bag = Bags.objects.filter(added_on__gte='2014-09-01', origin=sc)
 #   for sc in scs:
  #      bag = Bags.objects.filter(added_on__gte='2014-09-01', origin=sc)
   #     row=[ sc.center_shortcode, Bags.objects.filter(added_on__gte='2014-09-01', origin=sc).count()]
    #    report.write_row(row)
    data = Bags.objects.filter(added_on__gte='2014-09-01').values('origin').annotate(ct=Count('id')).values_list('origin__center_shortcode', 'ct')
    for row in data:
        report.write_row(row)
    report.manual_sheet_close()
    print report.file_name


def details():
    #File generation for report
    col_heads=('Awbs', 'Declared Val','Collectable Val','Collectable Amount','Emp Code')
    file_name = 'Details_data.xlsx'

    report = ReportGenerator(file_name)
    report.write_header(col_heads)
    #reading from file
    file_name = '/tmp/details.xls'
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_index(0)
    awbs = sh.col_values(0)[1:]
 
    clean_awbs = [int(i) for i in awbs if i]

    for a in clean_awbs:
        s = Shipment.objects.get(airwaybill_number=a)
        row = [a,s.declared_value,s.collectable_value,s.shipext.collected_amount,get_shipment_history(s).objects.filter(shipment=s, status=0)[0].employee_code.employee_code]
        report.write_row(row)
    # write header
    report.manual_sheet_close()
    print report.file_name

def ppc_shipment_count():
    col_heads=('Month','PPC','Count')
    file_name='PPC_Report.xlsx'
    report = ReportGenerator(file_name)
    report.write_header(col_heads)
    year_months = [(2014, m) for m in range(9, 13)] + [(2015, m) for m in range(1, 4)]
    ppc = ['HNP','MRP','BML','MAP','HYP','PNQ','BOP','BHP','DEP','OKP','DLM','GGP','PPP','LKP','AHH']
    for year, month in year_months:
        for sc in ppc:
            row =[month,year,sc,Shipment.objects.filter(service_centre__center_shortcode=sc,shipment_date__month=month,shipment_date_year=year).aggregate(Count('id'))]
            report.write_row(row)
    report.manual_sheet_close()
    print report.file_name


def pickup_dashbaord():
     file_name = 'pickup_format.xlsx'
     report = ReportGenerator(file_name)
     col_heads = ('Air Waybill number','Order Number','Product','Shipper','Consignee','Consignee Address1','Consignee Address2','Consignee Address3','Destination City','Pincode','State','Mobile','Telephone','Item Description','Pieces','Collectable Value','Declared value','Actual Weight','Volumetric Weight','Length(cms)','Breadth(cms)','Height(cms)','sub customer id','Pickup name','Pickup Address','Pickup Phone','Pickup Pincode','Return name','Return Address','Return Phone','Return Pincode')
     report.write_header(col_heads)
     report.manual_sheet_close()

