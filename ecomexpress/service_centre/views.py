import xlrd, xlwt
import traceback
import json
from math import ceil
from reports.report_api import ReportGenerator
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.db.models import *
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string
from jsonview.decorators import json_view
from django.conf import settings
from airwaybill.models import AirwaybillNumbers, ReversePickup
from customer.models import *
from delivery.models import update_bag_history, update_bag_remarks
from delivery.models import update_trackme_bagging_remarks
from ecomm_admin.models import *
from location.models import TransitMasterCutOff
from service_centre.models import *
from service_centre.transitmaster import get_expected_dod
from octroi.models import *
from service_centre.general_updates import update_shipment_pricing
from utils import history_update, price_updated, shipment_transit_time, developers_only
import re
from billing.jasper_update_new import update_jasper_awb
from operations.models import ConsolidatedBag, ConsolidatedBagConnection
from utils import *
from integration_services.utils import get_or_create_vendor
from airwaybill.models import AirwaybillCustomer

now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")
before = now - datetime.timedelta(days=14)

t8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
t3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)

book = xlwt.Workbook(encoding='utf8')
default_style = xlwt.Style.default_style
datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
header_style = xlwt.XFStyle()
category_style = xlwt.XFStyle()
font = xlwt.Font()
font.bold = True

pattern = xlwt.Pattern()
pattern.pattern = xlwt.Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = 5

borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
header_style.pattern = pattern
header_style.font = font
category_style.font = font
header_style.borders=borders
default_style.borders=borders


#not used
@csrf_exempt
def field_pickup_operation(request, pid=0):
    if request.POST:
      comp=request.POST['comp']
      if comp == "1":
          shipment = Shipment.objects.filter(pickup_id=pid, status_type=1, status=0)
          for a in shipment:
              a.status = 1
              a.status_type=0
              a.save()
              #history_update(shipment, 1, request)
              history_update(a, 1, request)
          shipment_check = Shipment.objects.filter(pickup_id=pid, status=0)
          if not shipment_check:
              pur = PickupRegistration.objects.get(id=pid)
              pur.status = 1
              pur.save()
          return HttpResponse("Success")
      else:
        awb=request.POST['awb']
        try:
          shipment=Shipment.objects.get(airwaybill_number=int(awb), status=0)
        except:
          return HttpResponse("2")
        if shipment.status_type == 0:
              shipment.status_type = 1#verified
              if shipment.pincode == 0:
                    shipment.status_type = 2
              try:
                 Pincode.objects.get(pincode=shipment.pincode)
              except:
                   shipment.status_type = 2
              if (shipment.product_type=="cod" and shipment.collectable_value == ""):
                    shipment.status_type = 3
              if (shipment.airwaybill_number == "") or (shipment.order_number == "") or ((shipment.product_type <> "ppd") and (shipment.product_type <>"cod")):
                    shipment.status_type = 4
              shipment.save()
              shipment = Shipment.objects.get(airwaybill_number=int(awb))
              counter=request.POST['counter']
              total_records = Shipment.objects.filter(pickup_id=pid, status=0).count()
              success_count = Shipment.objects.filter(pickup_id=pid, status_type=1, status=0).count()
              mismatch_count = Shipment.objects.filter(pickup_id=pid, status=0, status_type= 2 or 3 or 4).count()
              return render_to_response("service_centre/shipment_data.html",
                                  {'shipment':shipment,
                                   'counter':counter,
                                   'total_records':total_records,
                                   'success_count':success_count,
                                   'mismatch_count':mismatch_count},
                                   context_instance=RequestContext(request))
        return HttpResponse("1")


    else:
       if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
           pickups = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre)
       else:
           pickups = PickupRegistration.objects.filter()

       shipment=Shipment.objects.filter(pickup_id=pid, status=0).exclude(status_type=0)
       total_records = Shipment.objects.filter(pickup_id=pid, status=0).count()
       success_count = Shipment.objects.filter(pickup_id=pid, status_type=1, status=0).count()
       pikup = ""
       if pid <> 0:
           pikup = PickupRegistration.objects.get(id=int(pid))
       mismatch_count = Shipment.objects.filter(pickup_id=pid, status=0, status_type= 2 or 3 or 4).count()

    return render_to_response("service_centre/pickupoperation-servicecenter.html",
                              {'shipment':shipment,
                               'pid':pid,
                               'total':total_records,
                               'success':success_count,
                               'pickups':pickups,
                               'pikup':pikup,
                               'mismatch':mismatch_count},
                               context_instance=RequestContext(request))
#not used
@csrf_exempt
def generate_exception(request, pid):
    if pid==0:
        return HttpResponse("Please select a Pickup from the dropdown.")
    shipment = Shipment.objects.filter(pickup_id=pid, status=0)
    pickup_info={}
    for a in shipment:
        if not pickup_info.get(a):
            if a.status_type == 2:
                pickup_info[str(a.airwaybill_number)]="Pincode Missing"
            elif a.status_type == 3:
                pickup_info[str(a.airwaybill_number)]="Value Missing"
            elif a.status_type == 4:
                pickup_info[str(a.airwaybill_number)]="Data Missing"

    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('Exceptions')
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
    header_style = xlwt.XFStyle()
    category_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 5
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    header_style.pattern = pattern
    header_style.font = font
    category_style.font = font
    header_style.borders=borders
    default_style.borders=borders
    sheet.col(1).width = 8000 # 3333 = 1" (one inch).
    sheet.col(2).width = 5000
    sheet.write(0, 1, "Exceptions", style=header_style)
    sheet.write(3, 1, "Air waybill Number", style=header_style)
    sheet.write(3, 2, "Reason", style=header_style)
    style = datetime_style

    subject = "Exception Report for Pickup ID "+str(pid)
    if pickup_info:
        email_msg = "Following Air Waybill were not verified into the system. Given below are the respective Air Waybill Number and their reason code:\n"+"\n".join(['%s: %s' % (key, value) for (key, value) in pickup_info.items()])
        to_email = "sravank@ecomexpress.in"
        from_email = "support@ecomm.com"
        send_mail(subject,email_msg,from_email,[to_email])

        row = 4
        col = 1
        for key, val in pickup_info.items():
                sheet.write(row, col, str(key), style=style)
                sheet.write(row, col+1, str(val), style=style)
                row+=1

        response = HttpResponse(mimetype='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=Exceptions.xls'
        book.save(response)
        return response

    return HttpResponseRedirect("/service-centre/field_pickup_operation/"+pid+"/")


#not used
@csrf_exempt
def inscan_shipment(request):
       pickups = PickupRegistration.objects.using('local_ecomm').filter(service_centre=request.user.employeemaster.service_centre)
      #if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
      #    pickups = PickupRegistration.objects.using('local_ecomm').filter(service_centre=request.user.employeemaster.service_centre)
      #else:
      #    pickups = PickupRegistration.objects.using('local_ecomm').filter()

       shipment=Shipment.objects.using('local_ecomm').filter(status__in=[0,1,2], pickup__in=pickups).exclude(status_type=0)
       total_records = Shipment.objects.using('local_ecomm').filter(status__in=[0,1,2], pickup__in=pickups).aggregate(Count('id'))
       total_records = total_records['id__count']
       success_count = Shipment.objects.using('local_ecomm').filter(status_type=1, status__in=[1,2], pickup__in=pickups).aggregate(Count('id'))
       success_count = success_count['id__count']
       mismatch_count = Shipment.objects.using('local_ecomm').filter(status__in=[0,1,2], pickup__in=pickups, status_type= 2 or 3 or 4).aggregate(Count('id'))
       mismatch_count = mismatch_count['id__count']

      #if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
      #    pickups = PickupRegistration.objects.using('local_ecomm').filter(service_centre=request.user.employeemaster.service_centre)
      #else:
      #    pickups = PickupRegistration.objects.using('local_ecomm').filter()

      #shipment=Shipment.objects.using('local_ecomm').filter(status__in=[0,1,2], pickup__in=pickups).exclude(status_type=0)
      #total_records = Shipment.objects.using('local_ecomm').filter(status__in=[0,1,2], pickup__in=pickups).count()
      #success_count = Shipment.objects.using('local_ecomm').filter(status_type=1, status__in=[1,2], pickup__in=pickups).count()
      #mismatch_count = Shipment.objects.using('local_ecomm').filter(status__in=[0,1,2], pickup__in=pickups, status_type= 2 or 3 or 4).count()

       return render_to_response("service_centre/inscan-servicecentre.html",
                              {'shipment':"",
                               'total':total_records,
                               'success':success_count,
                               'mismatch':mismatch_count},
                               context_instance=RequestContext(request))

def download_prn(request):
    pickups = PickupRegistration.objects.filter(pincode=Pincode.objects.get(service_center=request.user.employeemaster.service_centre))
    shipment=Shipment.objects.filter(status__in=[1,2], pickup__in=pickups).exclude(status_type=0)

    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename="awb_prn.prn"'
    writer = csv.writer(response)
    text = '''SIZE 101.6 mm, 50.8 mm
DIRECTION 0,0
REFERENCE 0,0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET TEAR ON
CLS
CODEPAGE 1252
'''

    prn_list = []
    prn_list = shipment

    if shipment.count()<=1:

             writer.writerow([text])
             writer.writerow(["TEXT 778,199,'ROMAN.TTF',180,1,10,'ORG: %s DST: %s'"%(prn_list[0].pickup.service_centre.center_shortcode,prn_list[0].service_centre.center_shortcode)])
             writer.writerow(["TEXT 777,47,'0',180,11,10,'DATE: %s'"%(prn_list[0].added_on.date())])
             writer.writerow(["TEXT 777,85,'0',180,10,10,'VALUE: %s'"%(prn_list[0].declared_value)])
             writer.writerow(["TEXT 777,123,'ROMAN.TTF',180,1,10,'CONSIGNEE: %s'"%(prn_list[0].consignee)])
             writer.writerow(["TEXT 778,161,'ROMAN.TTF',180,1,10,'SENDER: %s'"%(prn_list[0].shipper)])
             writer.writerow(["TEXT 709,395,'ROMAN.TTF',180,1,8,'Ecom Express Pvt Ltd'"])
             writer.writerow(["BARCODE 766,300,'39',53,0,180,2,5,'%s'"%(prn_list[0].airwaybill_number)])
             writer.writerow(["TEXT 737,329,'ROMAN.TTF',180,1,9,'%s'"%(prn_list[0].airwaybill_number)])
             writer.writerow(["PRINT 1,1"])

    else:
        for a in xrange(0,len(prn_list),2):
             writer.writerow([text])
             writer.writerow(["TEXT 778,199,'ROMAN.TTF',180,1,10,'ORG: %s DST: %s'"%(prn_list[0].pickup.service_centre.center_shortcode,prn_list[0].service_centre.center_shortcode)])
             writer.writerow(["TEXT 372,199,'ROMAN.TTF',180,1,10,'ORG: %s DST: %s'"%(prn_list[0].pickup.service_centre.center_shortcode,prn_list[0].service_centre.center_shortcode)])
             writer.writerow(["TEXT 777,47,'0',180,11,10,'DATE: %s'"%(prn_list[0].added_on.date())])
             writer.writerow(["TEXT 371,47,'0',180,11,10,'DATE: %s'"%(prn_list[0].added_on.date())])
             writer.writerow(["TEXT 777,85,'0',180,10,10,'VALUE: %s'"%(prn_list[0].declared_value)])
             writer.writerow(["TEXT 371,85,'0',180,10,10,'VALUE: %s'"%(prn_list[0].declared_value)])
             writer.writerow(["TEXT 777,123,'ROMAN.TTF',180,1,10,'CONSIGNEE: %s'"%(prn_list[0].consignee)])
             writer.writerow(["TEXT 371,123,'ROMAN.TTF',180,1,10,'CONSIGNEE: %s'"%(prn_list[0].consignee)])
             writer.writerow(["TEXT 778,161,'ROMAN.TTF',180,1,10,'SENDER: %s'"%(prn_list[0].shipper)])
             writer.writerow(["TEXT 372,161,'ROMAN.TTF',180,1,10,'SENDER: %s'"%(prn_list[0].shipper)])
             writer.writerow(["TEXT 709,395,'ROMAN.TTF',180,1,8,'Ecom Express Pvt Ltd'"])
             writer.writerow(["TEXT 303,395,'ROMAN.TTF',180,1,8,'Ecom Express Pvt Ltd'"])
             writer.writerow(["BARCODE 766,300,'39',53,0,180,2,5,'%s'"%(prn_list[a].airwaybill_number)])
             writer.writerow(["TEXT 737,329,'ROMAN.TTF',180,1,9,'%s'"%(prn_list[a].airwaybill_number)])
             writer.writerow(["BARCODE 360,300,'39',53,0,180,2,5,'%s'"%(prn_list[a+1].airwaybill_number)])
             writer.writerow(["TEXT 331,329,'ROMAN.TTF',180,1,9,'%s'"%(prn_list[a+1].airwaybill_number)])
             writer.writerow(["PRINT 1,1"])

    return response


def awb_add(request):
    if request.POST:
        pickup_id = request.POST['pup_num']
        pickup=PickupRegistration.objects.get(id=int(pickup_id))
        reverse_pickup=0
        if pickup.reverse_pickup ==1:
                reverse_pickup=1

        airwaybill_num = request.POST['airwaybill_number']
        order_num = request.POST['order_number']
        product_type = request.POST['product_code']
       # shipper = request.POST['customer']
        #shipper = Customer.objects.get(id=int(shipper))
        consignee = request.POST['consignee_name']
        consignee_address1 = request.POST['consignee_address1']
        consignee_address2 = request.POST['consignee_address2']
        consignee_address3 = request.POST['consignee_address3']
        consignee_address4 = request.POST['consignee_address4']
        destination_city = request.POST['dest']
        pincode = request.POST['pincode']
        mobile = request.POST['mobile']
        telephone = request.POST['telephone']
        pieces = request.POST['packages']
        actual_weight = request.POST['actual_weight']
        volumetric_weight = request.POST['dim_weight']
        length = request.POST['length']
        breadth = request.POST['breadth']
        height = request.POST['height']


        if length == "":
              length = 0.0
        if breadth == "":
           breadth = 0.0
        if height == "":
            height = 0.0
        if actual_weight == "":
             actual_weight = 0.0
        if volumetric_weight == "":
            volumetric_weight = 0.0
        if pincode == "":
            pincode = 0.0
        else:
            origin_pincode=pickup.pincode
            pincode1 = Pincode.objects.get(pincode=origin_pincode)
            origin_service_centre = pincode1.service_center
            sctmg = ServiceCenterTransitMasterGroup.objects.get(service_center=origin_service_centre)

            dest_pincode=Pincode.objects.get(pincode=pincode)
            dest_service_centre = dest_pincode.service_center
            try:
             transit_time = TransitMaster.objects.get(transit_master=sctmg.transit_master_group, dest_service_center=dest_service_centre)
             tt_duration=int(transit_time.duration)
             if pincode1.sdl:
                tt_duration=tt_duration+2
            except:
                a=0 #tt does not exists

        try:
          shipment = Shipment.objects.filter(airwaybill_number=airwaybill_num).update(order_number=int(order_num), product_type=product_type, shipper=pickup.customer_code, pickup=pickup, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, consignee_address4 = consignee_address4, destination_city=destination_city, pincode=pincode, mobile=mobile, telephone=telephone, pieces=pieces, actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height, current_sc = request.user.employeemaster.service_centre, service_centre=dest_service_centre)
          if shipment == 0:
             shipment = Shipment(airwaybill_number=int(airwaybill_num), order_number=int(order_num), product_type=product_type, pickup=pickup, shipper=pickup.customer_code, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, consignee_address4 = consignee_address4, destination_city=destination_city, pincode=pincode, mobile=mobile, telephone=telephone, pieces=pieces, actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height, service_centre=dest_service_centre)
             shipment.save()

          if tt_duration:
              expected_dod = shipment.added_on + datetime.timedelta(days=tt_duration)
              shipment.expected_dod=expected_dod
              shipment.save()
          history_update(shipment, 0, request)
        except:
             traceback.print_exc()
        return HttpResponseRedirect("/service-centre/")
    else:
       service_centre = ServiceCenter.objects.all()
       destination = City.objects.all()
       sub_vendor = Shipper.objects.all()
       customer = Customer.objects.all()
       return render_to_response("service_centre/AWBadd.html",
                                 {'destination':destination,
                                  'service_centre':service_centre,
                                  'sub_vendor':sub_vendor,
                                  'customer':customer},
                               context_instance=RequestContext(request))
@csrf_exempt
def awb_edit(request):
    awb = request.POST['awb_num']
    pincode = request.POST['pincode']
    if awb:
      try:
       shipment = Shipment.objects.get(airwaybill_number=awb, status__in=[0,1,2,11])
      except Shipment.DoesNotExist:
        return HttpResponse("Shipment Does not exist")
      pin = Pincode.objects.get(pincode = pincode)
      shipment.pincode = pincode
      shipment.service_centre = pin.service_center
      if shipment.status > 1:
         shipment.status = 1
      shipment.save()
      return HttpResponse("Shipment destination Updated successfully")


def upload_rev_file(request):
    subCustomers_list=[]
    dup_awb = []
    if request.POST:
            upload_file = request.FILES['upload_file']
            file_contents = upload_file.read()
            if file_contents:
                reverse_pickup_dict = {}
                import_wb = xlrd.open_workbook(file_contents=file_contents)
                import_sheet = import_wb.sheet_by_index(0)
                #TODO:check to be added if multiple shipper reject file?
                scustomer = import_sheet.cell_value(rowx=1, colx=22)
                scustomer = Shipper.objects.get(id=int(scustomer))
                customer= scustomer.customer
                rev_pickup = ReversePickupRegistration.objects.create(customer_code=customer,
                    pickup_date=now.date(), pickup_time=now.time(), added_by=request.user.employeemaster)
                for rx in range(1, import_sheet.nrows):
                    awb = import_sheet.cell_value(rowx=rx, colx=0)
                    if awb:
                        return HttpResponse("File contains awb, rejected !")
                    pincode = import_sheet.cell_value(rowx=rx, colx=9)
                    sub_customer_id = import_sheet.cell_value(rowx=rx, colx=22)
                    if Pincode.objects.filter(pincode=pincode):
                        pincode = Pincode.objects.get(pincode=pincode)
                        service_centre = pincode.service_center
                    if Shipper.objects.filter(id=sub_customer_id):
                        sub_customer = Shipper.objects.get(id=sub_customer_id)
                    if not reverse_pickup_dict.get(service_centre):
                          reverse_pickup_dict[service_centre] = {}
                    if not reverse_pickup_dict[service_centre].get(sub_customer):
                            pickup = PickupRegistration(
                                customer_code=customer, subcustomer_code=sub_customer,
                                pickup_time=now,pickup_date=now,mode_id=1,reverse_pickup=1,
                                customer_name=sub_customer.name,address_line1=sub_customer.address.address1,
                                address_line2=sub_customer.address.address2,pincode=service_centre.pincode_set.all()[0],
                                mobile=0,telephone=0,pieces=4,actual_weight=1.2,
                                volume_weight=2.1,service_centre=service_centre)
                            pickup.save()
                            rev_pickup.pickup.add(pickup)
                            reverse_pickup_dict[service_centre][sub_customer]=pickup

                for rx in range(1, import_sheet.nrows):
                    vendor = import_sheet.cell_value(rowx=rx, colx=22)
                    vendor = Shipper.objects.get(id=vendor)
                    #order = import_sheet.cell_value(rowx=rx, colx=1)
                    order_num = repr(import_sheet.cell_value(rowx=rx, colx=1))
                    if order_num.replace(".", "", 1).isdigit():
                       order= int(float(order_num))
                    else:
                       order = import_sheet.cell_value(rowx=rx, colx=1)
                    consignee = import_sheet.cell_value(rowx=rx, colx=4)
                    consignee_address1 = import_sheet.cell_value(rowx=rx, colx=5)
                    consignee_address2 = import_sheet.cell_value(rowx=rx, colx=6)
                    consignee_address3 = import_sheet.cell_value(rowx=rx, colx=7)

                    destination_city = import_sheet.cell_value(rowx=rx, colx=8)
                    pincode = import_sheet.cell_value(rowx=rx, colx=9)
                    state = import_sheet.cell_value(rowx=rx, colx=10)
                    mobile = import_sheet.cell_value(rowx=rx, colx=11)
                    telephone = import_sheet.cell_value(rowx=rx, colx=12)
                    item_description = import_sheet.cell_value(rowx=rx, colx=13)
                    pieces = import_sheet.cell_value(rowx=rx, colx=14)
                    collectable_value=import_sheet.cell_value(rowx=rx, colx=15)
                    declared_value=import_sheet.cell_value(rowx=rx, colx=16)
                    actual_weight = import_sheet.cell_value(rowx=rx, colx=17)
                    volumetric_weight = import_sheet.cell_value(rowx=rx, colx=18)
                    length = import_sheet.cell_value(rowx=rx, colx=19)
                    breadth = import_sheet.cell_value(rowx=rx, colx=20)
                    height = import_sheet.cell_value(rowx=rx, colx=21)

                    if length == "":
                       length = 0.0
                    if breadth == "":
                       breadth = 0.0
                    if height == "":
                       height = 0.0
                    if actual_weight == "":
                       actual_weight = 0.0
                    if volumetric_weight == "":
                       volumetric_weight = 0.0
                    if collectable_value == "":
                       collectable_value = 0.0
                    else:
                        try:
                            int(collectable_value)
                        except ValueError:
                            collectable_value = collectable_value.replace(",", "")
                    if declared_value == "":
                       declared_value = 0.0
                    else:
                       try:
                            int(declared_value)
                       except ValueError:
                            declared_value = declared_value.replace(",", "")
                    if mobile == "":
                       mobile = 0

                    if pincode == "":
                       pincode = 0.0
                    else:
                       dest_pincode=Pincode.objects.get(pincode=int(pincode))
                       service_centre = dest_pincode.service_center
                    #try:
                    rev_shipment = ReverseShipment(
                        reverse_pickup=rev_pickup, order_number=order, product_type="ppd",
                        shipper=vendor.customer, vendor=vendor,  pickup_consignee=consignee,
                        pickup_consignee_address1=consignee_address1,
                        pickup_consignee_address2=consignee_address2,
                        pickup_consignee_address3=consignee_address3,
                        pickup_pincode=int(pincode), state=state, mobile=mobile,
                        telephone=telephone, item_description=item_description,
                        pieces=pieces, collectable_value=collectable_value,
                        declared_value=declared_value, actual_weight=actual_weight,
                        volumetric_weight=volumetric_weight, length=length,
                        breadth=breadth, height=height)
                    rev_shipment.save()
                    rev_shipment.pickup = reverse_pickup_dict[service_centre][vendor]
                    rev_shipment.save()
                    rev_shipment.pickup.pieces = ReverseShipment.objects.filter(pickup=rev_shipment.pickup).count() #Need to be change
                    rev_shipment.pickup.save()

                    if pincode:
                        try:
                          pincode = Pincode.objects.get(pincode=pincode)
                          servicecentre = pincode.service_center
                          rev_shipment.pickup_service_centre = servicecentre
                          rev_shipment.save()
                        except:
                          pincode = ""
                    #awbs=AirwaybillNumbers.objects.using('local_ecomm').filter(airwaybill_number__istartswith=5,status=0).order_by('airwaybill_number')[0:1]
                    obj = ReversePickup.objects.create()
                    airwaybill_number = obj.id
                    awbs = AirwaybillNumbers.objects.create(airwaybill_number=airwaybill_number)
                    if airwaybill_number:
                       #awb=awbs[0].airwaybill_number
                       awb=airwaybill_number
                       #try:
                       awb_from_table = AirwaybillNumbers.objects.get(airwaybill_number=awb)
                       awb_from_table.status = 1
                       awb_from_table.save()
                       #except AirwaybillNumbers.DoesNotExist:
                       #     return HttpResponse('Airwaybill Not Generated')
                       #rev_shipment = r.ship
                       try:
                            origin_service_centre = rship.pickup.service_centre
                            sctmg = ServiceCenterTransitMasterGroup.objects.get(service_center=origin_service_centre)
                            t_service_centre = pincode.service_center
                            tt_duration = 0

                            transit_time = TransitMaster.objects.get(transit_master=sctmg.transit_master_group, dest_service_center=dest_service_centre)
                            cutoff = datetime.datetime.strptime(transit_time.cutoff_time,"%H%M")
                            tt_duration=int(transit_time.duration)
                       except:
                            tt_duration=0
                       rship=rev_shipment
                       pin=vendor.address.pincode
                       pin=Pincode.objects.get(pincode=pin)
                       ship = Shipment.objects.create(
                               pickup=rship.pickup,
                               reverse_pickup=True,
                               airwaybill_number=awb,
                               order_number=rship.order_number,
                               product_type=rship.product_type,
                               shipper=rship.shipper,
                               consignee=rship.pickup.subcustomer_code.name,
                               consignee_address1=rship.pickup.subcustomer_code.address.address1,
                               consignee_address2=rship.pickup.subcustomer_code.address.address2,
                               consignee_address3=rship.pickup.subcustomer_code.address.address3,
                               consignee_address4=rship.pickup.subcustomer_code.address.address4,
                               destination_city=rship.pickup.subcustomer_code.address.city,
                               pincode=rship.pickup.subcustomer_code.address.pincode,
                               current_sc=servicecentre,
                               state=rship.state,
                               mobile=rship.mobile,
                               telephone=rship.telephone,
                               item_description=rship.item_description,
                               pieces=rship.pieces,
                               collectable_value=rship.collectable_value,
                               declared_value=rship.declared_value,
                               actual_weight=rship.actual_weight,
                               volumetric_weight=rship.volumetric_weight,
                               length=rship.length,
                               breadth=rship.breadth,
                               height=rship.height,
                               status_type=rship.status_type,
                               status =31,
                               remark=rship.remark,
                               service_centre=pin.service_center,
                               original_dest=pin.service_center)
                       rship.shipment=ship
                       rship.save()
                       if tt_duration == 0:
                            tt_duration =3
                            expected_dod= ship.added_on + datetime.timedelta(days=tt_duration)
                            cutoff = datetime.datetime.strptime("1500","%H%M")
                       if tt_duration <> 0:
                           if ship.added_on.time() > cutoff.time():
                                 tt_duration+=1
                                 expected_dod = ship.added_on + datetime.timedelta(days=tt_duration)
                           try:
                                 HolidayMaster.objects.get(date=expected_dod.date())
                                 expected_dod = expected_dod + datetime.timedelta(days=1)
                           except:
                               pass
                           ship.expected_dod=expected_dod
                           ship.save()
                       history_update(ship,31, request)
                       rship.airwaybill_number=int(awb)
                       rship.reason_code = None
                       rship.save()
                pickup.status=1
                pickup.save()
            return HttpResponseRedirect('/pickup/')
    else:
        return render_to_response(
            'service_centre/upload_file.html',
            {'pid':0}, context_instance=RequestContext(request))


def auto_upload_file(request):
    from integration_services.utils import nearest_dc, get_dc_address
    pid=1
    dup_awb = []
    awb_overweight=[]
    subCustomers_list=[]
    awb_tuples={}
    if request.POST:
            upload_file = request.FILES['upload_file']
            file_contents = upload_file.read()
            if file_contents:
                import_wb = xlrd.open_workbook(file_contents=file_contents)
                import_sheet = import_wb.sheet_by_index(0)
                for a in range(1, import_sheet.nrows):
                   for field in [3,4,5,8,9,10,11,13,17,19,20,21]:
                       field_data = import_sheet.cell_value(rowx=a, colx=field)
                       val = field_data.encode('utf-8') if isinstance(field_data,unicode)  else field_data
                       if field == 17:
                          if float(val) <= 0.0:
                             return HttpResponse("Airwaybill with incorrect weight found %s-%s"%(a,field))
                       if not val:
                              return HttpResponse("Field left blank - file could not be uploaded %s-%s"%(a,field))
                   airwaybill_num = import_sheet.cell_value(rowx=a, colx=0)
                   coll_val = import_sheet.cell_value(rowx=a, colx=15)
                 #  return HttpResponse("Field left blank - file could not be uploaded %s-%s"%(airwaybill_num,coll_val))
                   if airwaybill_num:
                     if str(airwaybill_num)[0] in ['4','7','8','9'] and float(coll_val) <= 0.0:
                            return HttpResponse("COD shipment found with 0 collectible value")
                     if Shipment.objects.filter(airwaybill_number=airwaybill_num):
                       awb_num = Shipment.objects.get(airwaybill_number=airwaybill_num)
                       #if (awb_num.status <> 0 and awb_num.status <> 1 and awb_num.return_shipment <> 0):
                       if (awb_num.status >=2 or awb_num.return_shipment > 0):
                            return HttpResponse("Used Air waybill entered %s, please recheck file before uploading."%(airwaybill_num))
                       #return HttpResponse("-----%s" % (awb_num.return_shipment <> 0))
                   #except:
                   #     pass

                   if airwaybill_num not in dup_awb:
                          dup_awb.append(airwaybill_num)
                   else:
                       return HttpResponse("Recheck file, duplicate airwaybill number found")

                reverse_pickup=0
                sc_err = []
                for rx in range(1, import_sheet.nrows):
                    awb = int(import_sheet.cell_value(rowx=rx, colx=0))
                    awbc = AirwaybillCustomer.objects.filter(airwaybill_number__airwaybill_number = awb)
                    if not awbc:
                        return HttpResponse("AWB %s not found in the system" % int(awb))
                    else:
                        awbc = awbc[0]
                    customer_code = awbc.customer.code
                    if not import_sheet.cell_value(rowx=rx, colx=23) or not import_sheet.cell_value(rowx=rx, colx=25):
                        return HttpResponse("Vendor Pickup Details not found for awb %s" % int(awb))
                    pickup_name = import_sheet.cell_value(rowx=rx, colx=23)
                    pickup_address = import_sheet.cell_value(rowx=rx, colx=24)
                    pickup_pincode = import_sheet.cell_value(rowx=rx, colx=26)
                    pickup_phone = import_sheet.cell_value(rowx=rx, colx=25)
                    return_name = ""
                    return_address = ""
                    return_pincode = ""
                    return_phone = ""
                    if import_sheet.cell_value(rowx=rx, colx=27):
                        return_name = import_sheet.cell_value(rowx=rx, colx=27)
                        return_address = import_sheet.cell_value(rowx=rx, colx=28)
                        return_pincode = import_sheet.cell_value(rowx=rx, colx=30)
                        return_phone = import_sheet.cell_value(rowx=rx, colx=29)
                    #sub_customer_id  = get_vendor(name,address,phone,pincode,customer_code,return_pincode)
                    sub_customer_obj  = get_or_create_vendor( pincode = pickup_pincode, address = pickup_address, name = pickup_name, phone = pickup_phone, customer = awbc.customer)           
                    sub_customer_id  = sub_customer_obj.id
                    if return_name:
                        return_sub_customer_obj  = get_or_create_vendor( pincode = return_pincode, address = return_address, name = return_name, phone = return_phone, customer = Customer.objects.get(code=customer_code))           
                        return_sub_customer_id  = return_sub_customer_obj.id
                    else:
                        return_sub_customer_obj  = sub_customer_obj
                        return_sub_customer_id  = sub_customer_id
 
                    awb_tuples[awb] = (sub_customer_id, return_sub_customer_id)

                    #sub_customer_id = import_sheet.cell_value(rowx=rx, colx=22)
                   #if Shipper.objects.filter(alias_code=sub_customer_id):
                   #   sub_customer_id = Shipper.objects.filter(alias_code=sub_customer_id)[0].id
                    if Shipper.objects.filter(id=sub_customer_id):
                        sub_customer = Shipper.objects.get(id=sub_customer_id)
                        if not sub_customer.customer.activation_status:
                               return HttpResponse("Code Deactivated Soft data cannott be uploaded")
                        if not sub_customer in subCustomers_list:
                           # subCustomers_list.append(sub_customer)
                            subCustomers_list.append((sub_customer_id, return_sub_customer_id))
                    else:
                        sc_err.append(sub_customer_id)
                if sc_err:
                        return HttpResponse("Subcustomer %s not found! Please check again."%(str(sc_err)))

                pickup_dict = {}

                subCustomers_list = set(subCustomers_list)
                #return HttpResponse("%s--" % subCustomers_list)
                for subcust_tuple in subCustomers_list:
                     subcust = Shipper.objects.get(id=subcust_tuple[0])
                     return_subcust = Shipper.objects.get(id=subcust_tuple[1])
                     try:
                       pincode = Pincode.objects.get(pincode = int(subcust.address.pincode))
                       ret_pincode = Pincode.objects.get(pincode = int(return_subcust.address.pincode))
                       if ShipperMapping.objects.filter(shipper=subcust):
                          pinc = ShipperMapping.objects.get(shipper=subcust)
                          pincode = Pincode.objects.get(pincode = pinc.forward_pincode)
                     except:
                       return HttpResponse("Pincode does not exists for this subcustomer")
                     pickup = PickupRegistration(customer_code = subcust.customer,subcustomer_code=subcust,return_subcustomer_code=return_subcust,pickup_time=now,pickup_date=now,mode_id=1,customer_name=subcust.name,address_line1=subcust.address.address1,address_line2=subcust.address.address2,pincode=pincode.pincode,address_line3=subcust.address.address3,address_line4=subcust.address.address4,mobile=0,telephone=0,pieces=4,actual_weight=1.2,volume_weight=2.1,service_centre=pincode.service_center)
                     pickup.save()
                     pickup_dict[(subcust.id,return_subcust.id)] = pickup
                     subcus = pickup_dict.keys()
                     #code for matching with scheduled
                     scheduled_pickup = PickupSchedulerRegistration.objects.filter(status = 0, subcustomer_code=subcust)
                     for a in scheduled_pickup:
                         a.pickup = pickup
                         a.status =1
                         a.pickup =pickup
                         a.save()
                #return HttpResponse("### %s" % len(pickup_dict));
                for rx in range(1, import_sheet.nrows):
                    airwaybill_num = import_sheet.cell_value(rowx=rx, colx=0)
                    sub_customer_id = import_sheet.cell_value(rowx=rx, colx=22)
                    if Shipper.objects.filter(alias_code=sub_customer_id):
                       sub_customer_id = Shipper.objects.filter(alias_code=sub_customer_id)[0].id

                    pickup = pickup_dict[awb_tuples[int(airwaybill_num)]]
                    #return HttpResponse("### %s -- " % pickup)
                    try:
                       awb_num = AirwaybillNumbers.objects.get(airwaybill_number=airwaybill_num)
                       awb_num.status=1
                       awb_num.save()
                    except:
                        return HttpResponse("Wrong airwaybill Number")
                    order_num = import_sheet.cell_value(rowx=rx, colx=1)
                    product_type = import_sheet.cell_value(rowx=rx, colx=2)
                    product_type = product_type.lower()
                    if str(airwaybill_num)[0] in ["1","2","3"]:
                           product_type="ppd"
                    elif str(airwaybill_num)[0] in ["4","7","8","9"]:
                           product_type="cod"

                    shipper = import_sheet.cell_value(rowx=rx, colx=3)
                    shipper = pickup.customer_code
                    if awb_num.awbc_info.get().customer.code <> "32012":
                       if shipper <> awb_num.awbc_info.get().customer:
                         return HttpResponse("Airwaybill does not belong to this Customer, please recheck")

                    consignee = import_sheet.cell_value(rowx=rx, colx=4)
                    consignee_address1 = import_sheet.cell_value(rowx=rx, colx=5)
                    consignee_address2 = import_sheet.cell_value(rowx=rx, colx=6)
                    consignee_address3 = import_sheet.cell_value(rowx=rx, colx=7)

                    destination_city = import_sheet.cell_value(rowx=rx, colx=8)
                    pincode = import_sheet.cell_value(rowx=rx, colx=9)
                    state = import_sheet.cell_value(rowx=rx, colx=10)
                    mobile = import_sheet.cell_value(rowx=rx, colx=11)
                    telephone = import_sheet.cell_value(rowx=rx, colx=12)
                    item_description = import_sheet.cell_value(rowx=rx, colx=13)
                    pieces = import_sheet.cell_value(rowx=rx, colx=14)
                    collectable_value=import_sheet.cell_value(rowx=rx, colx=15)
                    declared_value=import_sheet.cell_value(rowx=rx, colx=16)
                    actual_weight = import_sheet.cell_value(rowx=rx, colx=17)
                    volumetric_weight = import_sheet.cell_value(rowx=rx, colx=18)
                    length = import_sheet.cell_value(rowx=rx, colx=19)
                    breadth = import_sheet.cell_value(rowx=rx, colx=20)
                    height = import_sheet.cell_value(rowx=rx, colx=21)
                    order_num = repr(import_sheet.cell_value(rowx=rx, colx=1))
                    if order_num.replace(".", "", 1).isdigit():
                       order_num = int(float(order_num))
                    elif 'e+' in str(order_num):
                       order_num = int(float(order_num))
                    else:
                       order_num = import_sheet.cell_value(rowx=rx, colx=1)

                    if length == "":
                       length = 0.0
                    if breadth == "":
                       breadth = 0.0
                    if height == "":
                       height = 0.0
                    if actual_weight == "":
                       actual_weight = 0.0
                    if not (isinstance(volumetric_weight, float) or isinstance(volumetric_weight, int)):
                      if volumetric_weight.strip() == "":

                         volumetric_weight = 0.0
                    if ((actual_weight > 10.0) or (volumetric_weight > 10.0)):
                            a = str(airwaybill_num)+"("+str(max(actual_weight,volumetric_weight))+"Kgs)"
                            awb_overweight.append(a)
                    if collectable_value == "":
                       collectable_value = 0.0
                    else:
                        try:
                            int(collectable_value)
                        except ValueError:
                            collectable_value = collectable_value.replace(",", "")
                    if declared_value == "":
                       declared_value = 0.0
                    else:
                       try:
                            int(declared_value)
                       except ValueError:
                            declared_value = declared_value.replace(",", "")
                    if mobile == "":
                       mobile = 0

                    if pincode == "":
                       pincode = 0.0
                       tt_duration = 0
                    else:

                        origin_pincode=pickup.pincode
                        if not Pincode.objects.filter(pincode=pincode):
                            pincode = 0.0
                            tt_duration = 0
                        try:
                            pincode1 = Pincode.objects.get(pincode=origin_pincode)
                            origin_service_centre = pickup.service_centre
                            sctmg = ServiceCenterTransitMasterGroup.objects.get(service_center=origin_service_centre)
                            #return HttpResponse(pincode)
                            dest_pincode=Pincode.objects.get(pincode=pincode)
                            dest_service_centre = dest_pincode.service_center
                            tt_duration = 0

                            transit_time = TransitMaster.objects.filter(transit_master=sctmg.transit_master_group,
                                                    dest_service_center=dest_service_centre)
                            if transit_time:
                                transit_time = transit_time[0]

                                transit_time_cutoff =  TransitMasterCutOff.objects.filter(transit_master_orignal=sctmg.transit_master_group,
                                                    transit_master_dest=dest_service_centre.servicecentertransitmastergroup_set.get())
                                if not transit_time_cutoff:
                                    cutoff = datetime.datetime.strptime(transit_time.cutoff_time,"%H%M")
                                else:
                                    cutoff = datetime.datetime.strptime(transit_time_cutoff[0].cutoff_time,"%H%M")

                                tt_duration=int(transit_time.duration)
                            else:
                                tt_duration=0
     #                           shipment_transit_time(airwaybill_num, "else1")
                        except ValueError as e:
                            tt_duration=0
    #                        shipment_transit_time(airwaybill_num, str(e))
                   #return HttpResponse(tt_duration)
                    servicecentre = None
                    if pincode:
                        try:
                          pincode_sc = Pincode.objects.get(pincode=pincode)
                          servicecentre = pincode_sc.service_center
                        except:
                          pincode = ""
                          servicecentre = None

                    ship_address = get_dc_address(consignee_address1, consignee_address2, consignee_address3, destination_city, state)
                    servicecentre_id = nearest_dc(ship_address)
                    if servicecentre_id:
                        servicecentre = ServiceCenter.objects.get(id=servicecentre_id)

                    expected_dod = None
                    if tt_duration == 0:
                         tt_duration =3
                         #cutoff="1500"
                         cutoff = datetime.datetime.strptime("1500","%H%M")
                    if tt_duration <> 0:
                         if now.time() > cutoff.time():
                             tt_duration+=1
                         expected_dod = now + datetime.timedelta(days=tt_duration)
                         try:
                             HolidayMaster.objects.get(date=expected_dod.date())
                             expected_dod = expected_dod + datetime.timedelta(days=1)
                         except:
                             pass
                    #else:
                       #tt_duration =3
                       #expected_dod = now + datetime.timedelta(days=tt_duration)
                       #try:
                           #HolidayMaster.objects.get(date=expected_dod.date())
                           #expected_dod = expected_dod + datetime.timedelta(days=1)
                       #except:
                           #pass
                    expected_dod = get_expected_dod(origin_service_centre, dest_service_centre, pickup.added_on, pickup.customer_code) 
                    try:
                     shipment = Shipment.objects.filter(airwaybill_number=airwaybill_num, status__in=[0,1]).update(order_number=str(order_num), current_sc=request.user.employeemaster.service_centre,product_type=product_type, shipper=shipper, pickup=pickup, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, state=state, mobile=mobile, telephone=telephone, item_description=item_description, pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height, service_centre = servicecentre, original_dest = servicecentre, expected_dod = expected_dod)
                     shipment = Shipment.objects.get(airwaybill_number=airwaybill_num)
                    except:
                      shipment = Shipment(airwaybill_number=int(airwaybill_num), current_sc=request.user.employeemaster.service_centre, order_number=str(order_num), product_type=product_type, shipper=shipper, pickup=pickup, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, state=state, mobile=mobile, telephone=telephone, item_description=item_description, pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height, service_centre = servicecentre, original_dest = servicecentre, expected_dod = expected_dod)
                      shipment.save()
                   # if pincode:
                   #     try:
                   #       pincode = Pincode.objects.get(pincode=shipment.pincode)
                   #       servicecentre = pincode.service_center
                   #       shipment.service_centre = servicecentre
                   #       shipment.original_dest = servicecentre
                   #       shipment.save()
                   #     except:
                   #       pincode = ""

                   # if tt_duration <> 0:
                   #      if shipment.added_on.time() > cutoff.time():
                   #          tt_duration+=1
                   #      expected_dod = shipment.added_on + datetime.timedelta(days=tt_duration)
                   #      try:
                   #          HolidayMaster.objects.get(date=expected_dod.date())
                   #          expected_dod = expected_dod + datetime.timedelta(days=1)
                   #      except:
                   #          pass
                   #      shipment.expected_dod=expected_dod
                   #      shipment.save()
                    if shipment:
                         history_update(shipment, 0, request)
                    tmp_count=Shipment.objects.filter(pickup=pickup.id).count()
                    pickup.pieces=tmp_count;
                    pickup.status=0
                    pickup.save()
            else:
              pass

            group = Group.objects.get(name="Customer Service")
            a=0
            if request.user.groups.filter(name="Customer Service").exists():
              pickup = PickupRegistration.objects.filter().order_by('-added_on')
              a=1
            if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
               pickup = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre, status=0)
            else:
               pickup = PickupRegistration.objects.filter(status=0).order_by('-added_on')
            msg = ""
            if awb_overweight:
              msg = "Following Air Waybills have weight more than 10 kgs, PLEASE CONFIRM !!!, and incase of mismatch re-upload the file:\n"+"\n".join(['%s' % ship for ship in awb_overweight])
            customer=Customer.objects.all()
            destination= ServiceCenter.objects.all()
            return render_to_response(
                "pickup/pickupdashboard.html",
                {'pickup':pickup, 'msg':msg, 'a':a, 'customer':customer, 'sc':destination},
                context_instance=RequestContext(request))
    else:
        return render_to_response(
            'pickup/auto_upload_file.html',
            {'pid':pid},context_instance=RequestContext(request))


def auto_upload_file_v2(request):
    pid=1
    dup_awb = []
    awb_overweight=[]
    subCustomers_list=[]
    if request.POST:
            upload_file = request.FILES['upload_file']
            file_contents = upload_file.read()
            if file_contents:
                import_wb = xlrd.open_workbook(file_contents=file_contents)
                import_sheet = import_wb.sheet_by_index(0)
                for a in range(1, import_sheet.nrows):
                   for field in [3,4,5,8,9,10,11,13,17,19,20,21]:
                       field_data = import_sheet.cell_value(rowx=a, colx=field)
                       val = field_data.encode('utf-8') if isinstance(field_data,unicode)  else field_data
                       if field == 17:
                          if float(val) <= 0.0:
                             return HttpResponse("Airwaybill with incorrect weight found %s-%s"%(a,field))
                       if not val:
                              return HttpResponse("Field left blank - file could not be uploaded %s-%s"%(a,field))
                   airwaybill_num = import_sheet.cell_value(rowx=a, colx=0)
                   coll_val = import_sheet.cell_value(rowx=a, colx=15)
                 #  return HttpResponse("Field left blank - file could not be uploaded %s-%s"%(airwaybill_num,coll_val))
                   if airwaybill_num:
                     if str(airwaybill_num)[0] in ['4','7','8','9'] and float(coll_val) <= 0.0:
                            return HttpResponse("COD shipment found with 0 collectible value")
                     if Shipment.objects.filter(airwaybill_number=airwaybill_num):
                       awb_num = Shipment.objects.get(airwaybill_number=airwaybill_num)
                       #if (awb_num.status <> 0 and awb_num.status <> 1 and awb_num.return_shipment <> 0):
                       if (awb_num.status >=2 or awb_num.return_shipment > 0):
                            return HttpResponse("Used Air waybill entered %s, please recheck file before uploading."%(airwaybill_num))
                       #return HttpResponse("-----%s" % (awb_num.return_shipment <> 0))
                   #except:
                   #     pass

                   if airwaybill_num not in dup_awb:
                          dup_awb.append(airwaybill_num)
                   else:
                       return HttpResponse("Recheck file, duplicate airwaybill number found")
                #return HttpResponse(import_sheet.ncols)
                reverse_pickup=0
                sc_err = []
                #return HttpResponse(import_sheet.nrows)
                for rx in range(1, import_sheet.nrows):
                    #sub_customer_id = import_sheet.cell_value(rowx=rx, colx=22)
                    #if Shipper.objects.filter(alias_code=sub_customer_id):
                    #   sub_customer_id = Shipper.objects.filter(alias_code=sub_customer_id)[0].id
                    #if Shipper.objects.filter(id=sub_customer_id):
                    #    sub_customer = Shipper.objects.get(id=sub_customer_id)
                    #    if not sub_customer.customer.activation_status:
                    #           return HttpResponse("Code Deactivated Soft data cannott be uploaded")
                    #    if not sub_customer in subCustomers_list:
                    #        subCustomers_list.append(sub_customer)
                    #else:
                    #    sc_err.append(sub_customer_id)
                    customer_code = import_sheet.cell_value(rowx=rx, colx=22)
                    pickup_name = import_sheet.cell_value(rowx=rx, colx=23)
                    pickup_address = import_sheet.cell_value(rowx=rx, colx=24)
                    pickup_pincode = import_sheet.cell_value(rowx=rx, colx=25)
                    pickup_phone = import_sheet.cell_value(rowx=rx, colx=26)
                    
                    return_name = ""
                    return_address = ""
                    return_pincode = ""
                    return_phone = ""
                    if import_sheet.cell_value(rowx=rx, colx=27):
                        return_name = import_sheet.cell_value(rowx=rx, colx=27)
                        return_address = import_sheet.cell_value(rowx=rx, colx=28)
                        return_pincode = import_sheet.cell_value(rowx=rx, colx=29)
                        return_phone = import_sheet.cell_value(rowx=rx, colx=30)
                    #sub_customer_id  = get_vendor(name,address,phone,pincode,customer_code,return_pincode)
                    sub_customer_obj  = get_or_create_vendor( pincode = pickup_pincode, address = pickup_address, name = pickup_name, phone = pickup_phone, customer = Customer.objects.get(code=customer_code))           
                    sub_customer_id  = sub_customer_obj.id
                    if return_name:
                        return_sub_customer_obj  = get_or_create_vendor( pincode = return_pincode, address = return_address, name = return_name, phone = return_phone, customer = Customer.objects.get(code=customer_code))           
                        return_sub_customer_id  = return_sub_customer_obj.id
                    else:
                        return_sub_customer_obj  = sub_customer_obj
                        return_sub_customer_id  = sub_customer_id
                    #return HttpResponse(sub_customer)
                    if sub_customer_id:
                      if not sub_customer_id in subCustomers_list:
                         subCustomers_list.append(sub_customer_id)
                if sc_err:
                        return HttpResponse("Subcustomer %s not found! Please check again."%(str(sc_err)))
                #return HttpResponse(subCustomers_list)
                pickup_dict = {}
                subCustomers_list = set(subCustomers_list)
                #return HttpResponse(len(subCustomers_list))
                for subcust in subCustomers_list:
                     try:
                       subcust = Shipper.objects.get(id=subcust)
                       pincode = Pincode.objects.get(pincode = int(subcust.address.pincode))
                       if ShipperMapping.objects.filter(shipper=subcust):
                          pinc = ShipperMapping.objects.get(shipper=subcust)
                          pincode = Pincode.objects.get(pincode = pinc.forward_pincode)
                     except:
                          pincode = Pincode.objects.get(pincode=110075)
                          #subcusti
                          #u=get_subcustomer(subcust)
                          #pincode=u[1]
                          #pincode=Pincode.objects.get(pincode=int(pincode))
                          #pincode=Pincode.objects.get(pincode = int(subcust.address.pincode))
                        #return HttpResponse("Pincode does not exists for this subcustomer")
                     pickup = PickupRegistration(customer_code = subcust.customer,subcustomer_code=subcust,pickup_time=now,pickup_date=now,mode_id=1,customer_name=subcust.name,address_line1=subcust.address.address1,address_line2=subcust.address.address2,pincode=pincode.pincode,address_line3=subcust.address.address3,address_line4=subcust.address.address4,mobile=0,telephone=0,pieces=4,actual_weight=1.2,volume_weight=2.1,service_centre=pincode.service_center)
                     pickup.save()
                     pickup_dict[subcust.id] = pickup
                     subcus = pickup_dict.keys()
                     #code for matching with scheduled
                     scheduled_pickup = PickupSchedulerRegistration.objects.filter(status = 0, subcustomer_code=subcust)
                     for a in scheduled_pickup:
                         a.pickup = pickup
                         a.status =1
                         a.pickup =pickup
                         a.save()
                for rx in range(1, import_sheet.nrows):
                    airwaybill_num = import_sheet.cell_value(rowx=rx, colx=0)
                    sub_customer_id = import_sheet.cell_value(rowx=rx, colx=22) 
                    if Shipper.objects.filter(alias_code=sub_customer_id):
                       sub_customer_id = Shipper.objects.filter(alias_code=sub_customer_id)[0].id
                    customer_code = import_sheet.cell_value(rowx=rx, colx=22)
                    name = import_sheet.cell_value(rowx=rx, colx=23)
                    address = import_sheet.cell_value(rowx=rx, colx=24)
                    pincode = import_sheet.cell_value(rowx=rx, colx=25)
                    phone = import_sheet.cell_value(rowx=rx, colx=26)
                    return_pincode = import_sheet.cell_value(rowx=rx, colx=27)
                    sub_customer_id  = get_vendor(name,address,phone,pincode,customer_code,return_pincode)

                    pickup = pickup_dict[int(sub_customer_id)]
                    try:
                       awb_num = AirwaybillNumbers.objects.get(airwaybill_number=airwaybill_num)
                       awb_num.status=1
                       awb_num.save()
                    except:
                        return HttpResponse("Wrong airwaybill Number")
                    order_num = import_sheet.cell_value(rowx=rx, colx=1)
                    product_type = import_sheet.cell_value(rowx=rx, colx=2)
                    product_type = product_type.lower()
                    if str(airwaybill_num)[0] in ["1","2","3"]:
                           product_type="ppd"
                    elif str(airwaybill_num)[0] in ["4","7","8","9"]:
                           product_type="cod"

                    shipper = import_sheet.cell_value(rowx=rx, colx=3)
                    shipper = pickup.customer_code
                    if awb_num.awbc_info.get().customer.code <> "32012":
                       if shipper <> awb_num.awbc_info.get().customer:
                         return HttpResponse("Airwaybill does not belong to this Customer, please recheck")

                    consignee = import_sheet.cell_value(rowx=rx, colx=4)
                    consignee_address1 = import_sheet.cell_value(rowx=rx, colx=5)
                    consignee_address2 = import_sheet.cell_value(rowx=rx, colx=6)
                    consignee_address3 = import_sheet.cell_value(rowx=rx, colx=7)

                    destination_city = import_sheet.cell_value(rowx=rx, colx=8)
                    pincode = import_sheet.cell_value(rowx=rx, colx=9)
                    state = import_sheet.cell_value(rowx=rx, colx=10)
                    mobile = import_sheet.cell_value(rowx=rx, colx=11)
                    telephone = import_sheet.cell_value(rowx=rx, colx=12)
                    item_description = import_sheet.cell_value(rowx=rx, colx=13)
                    pieces = import_sheet.cell_value(rowx=rx, colx=14)
                    collectable_value=import_sheet.cell_value(rowx=rx, colx=15)
                    declared_value=import_sheet.cell_value(rowx=rx, colx=16)
                    actual_weight = import_sheet.cell_value(rowx=rx, colx=17)
                    volumetric_weight = import_sheet.cell_value(rowx=rx, colx=18)
                    length = import_sheet.cell_value(rowx=rx, colx=19)
                    breadth = import_sheet.cell_value(rowx=rx, colx=20)
                    height = import_sheet.cell_value(rowx=rx, colx=21)
                    order_num = repr(import_sheet.cell_value(rowx=rx, colx=1))
                    if order_num.replace(".", "", 1).isdigit():
                       order_num = int(float(order_num))
                    elif 'e+' in str(order_num):
                       order_num = int(float(order_num))
                    else:
                       order_num = import_sheet.cell_value(rowx=rx, colx=1)

                    if length == "":
                       length = 0.0
                    if breadth == "":
                       breadth = 0.0
                    if height == "":
                       height = 0.0
                    if actual_weight == "":
                       actual_weight = 0.0
                    if not (isinstance(volumetric_weight, float) or isinstance(volumetric_weight, int)):
                      if volumetric_weight.strip() == "":

                         volumetric_weight = 0.0
                    if ((actual_weight > 10.0) or (volumetric_weight > 10.0)):
                            a = str(airwaybill_num)+"("+str(max(actual_weight,volumetric_weight))+"Kgs)"
                            awb_overweight.append(a)
                    if collectable_value == "":
                       collectable_value = 0.0
                    else:
                        try:
                            int(collectable_value)
                        except ValueError:
                            collectable_value = collectable_value.replace(",", "")
                    if declared_value == "":
                       declared_value = 0.0
                    else:
                       try:
                            int(declared_value)
                       except ValueError:
                            declared_value = declared_value.replace(",", "")
                    if mobile == "":
                       mobile = 0

                    if pincode == "":
                       pincode = 0.0
                       tt_duration = 0
                    else:

                        origin_pincode=pickup.pincode
                        if not Pincode.objects.filter(pincode=pincode):
                            pincode = 0.0
                            tt_duration = 0
                        try:
                            pincode1 = Pincode.objects.get(pincode=origin_pincode)
                            origin_service_centre = pickup.service_centre
                            sctmg = ServiceCenterTransitMasterGroup.objects.get(service_center=origin_service_centre)
                            dest_pincode=Pincode.objects.get(pincode=pincode)
                            dest_service_centre = dest_pincode.service_center
                            tt_duration = 0

                            transit_time = TransitMaster.objects.filter(transit_master=sctmg.transit_master_group,
                                                    dest_service_center=dest_service_centre)
                            if transit_time:
                                transit_time = transit_time[0]

                                transit_time_cutoff =  TransitMasterCutOff.objects.filter(transit_master_orignal=sctmg.transit_master_group,
                                                    transit_master_dest=dest_service_centre.servicecentertransitmastergroup_set.get())
                                if not transit_time_cutoff:
                                    cutoff = datetime.datetime.strptime(transit_time.cutoff_time,"%H%M")
                                else:
                                    cutoff = datetime.datetime.strptime(transit_time_cutoff[0].cutoff_time,"%H%M")

                                tt_duration=int(transit_time.duration)
                            else:
                                tt_duration=0
     #                           shipment_transit_time(airwaybill_num, "else1")
                        except ValueError as e:
                            tt_duration=0
    #                        shipment_transit_time(airwaybill_num, str(e))
                   #return HttpResponse(tt_duration)
                    servicecentre = None
                    if pincode:
                        try:
                          pincode_sc = Pincode.objects.get(pincode=pincode)
                          servicecentre = pincode_sc.service_center
                        except:
                          pincode = ""
                          servicecentre = None
                    expected_dod = None
                    if tt_duration == 0:
                         tt_duration =3
                         #cutoff="1500"
                         cutoff = datetime.datetime.strptime("1500","%H%M")
                    if tt_duration <> 0:
                         if now.time() > cutoff.time():
                             tt_duration+=1
                         expected_dod = now + datetime.timedelta(days=tt_duration)
                         try:
                             HolidayMaster.objects.get(date=expected_dod.date())
                             expected_dod = expected_dod + datetime.timedelta(days=1)
                         except:
                             pass
                    #else:
                       #tt_duration =3
                       #expected_dod = now + datetime.timedelta(days=tt_duration)
                       #try:
                           #HolidayMaster.objects.get(date=expected_dod.date())
                           #expected_dod = expected_dod + datetime.timedelta(days=1)
                       #except:
                           #pass

                    try:
                     shipment = Shipment.objects.filter(airwaybill_number=airwaybill_num, status__in=[0,1]).update(order_number=str(order_num), current_sc=request.user.employeemaster.service_centre,product_type=product_type, shipper=shipper, pickup=pickup, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, state=state, mobile=mobile, telephone=telephone, item_description=item_description, pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height, service_centre = servicecentre, original_dest = servicecentre, expected_dod = expected_dod)
                     shipment = Shipment.objects.get(airwaybill_number=airwaybill_num)
                    except:
                      shipment = Shipment(airwaybill_number=int(airwaybill_num), current_sc=request.user.employeemaster.service_centre, order_number=str(order_num), product_type=product_type, shipper=shipper, pickup=pickup, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, state=state, mobile=mobile, telephone=telephone, item_description=item_description, pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height, service_centre = servicecentre, original_dest = servicecentre, expected_dod = expected_dod)
                      shipment.save()
                   # if pincode:
                   #     try:
                   #       pincode = Pincode.objects.get(pincode=shipment.pincode)
                   #       servicecentre = pincode.service_center
                   #       shipment.service_centre = servicecentre
                   #       shipment.original_dest = servicecentre
                   #       shipment.save()
                   #     except:
                   #       pincode = ""

                   # if tt_duration <> 0:
                   #      if shipment.added_on.time() > cutoff.time():
                   #          tt_duration+=1
                   #      expected_dod = shipment.added_on + datetime.timedelta(days=tt_duration)
                   #      try:
                   #          HolidayMaster.objects.get(date=expected_dod.date())
                   #          expected_dod = expected_dod + datetime.timedelta(days=1)
                   #      except:
                   #          pass
                   #      shipment.expected_dod=expected_dod
                   #      shipment.save()
                    if shipment:
                         history_update(shipment, 0,request,sc=pickup.service_centre)
                    tmp_count=Shipment.objects.filter(pickup=pickup.id).count()
                    pickup.pieces=tmp_count;
                    pickup.status=0
                    pickup.save()
            else:
              pass

            group = Group.objects.get(name="Customer Service")
            a=0
            if request.user.groups.filter(name="Customer Service").exists():
              pickup = PickupRegistration.objects.filter().order_by('-added_on')
              a=1
            if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
               pickup = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre, status=0)
            else:
               pickup = PickupRegistration.objects.filter(status=0).order_by('-added_on')
            msg = ""
            if awb_overweight:
              msg = "Following Air Waybills have weight more than 10 kgs, PLEASE CONFIRM !!!, and incase of mismatch re-upload the file:\n"+"\n".join(['%s' % ship for ship in awb_overweight])
            customer=Customer.objects.all()
            destination= ServiceCenter.objects.all()
            return render_to_response(
                "pickup/pickupdashboard.html",
                {'pickup':pickup, 'msg':msg, 'a':a, 'customer':customer, 'sc':destination},
                context_instance=RequestContext(request))
    else:
        return render_to_response(
            'pickup/auto_upload_file.html',
            {'pid':pid},context_instance=RequestContext(request))


def upload_file(request, pid):
    if request.POST:
          upload_file = request.FILES['upload_file']
          file_contents = upload_file.read()
          if file_contents:
            import_wb = xlrd.open_workbook(file_contents=file_contents)
            import_sheet = import_wb.sheet_by_index(0)
            pickup_id = pid
            dup_awb =[]
            awb_overweight=[]
            pickup=PickupRegistration.objects.get(id=int(pickup_id))
            reverse_pickup=0
            if pickup.reverse_pickup ==1:
                reverse_pickup=1
            for a in range(1, import_sheet.nrows):
                for field in [3,4,5,8,9,10,11,13,17,19,20,21]:
                    field_data = import_sheet.cell_value(rowx=a, colx=field)
                    val = field_data.encode('utf-8') if isinstance(field_data,unicode)  else field_data
                    reason_code = import_sheet.cell_value(rowx=a, colx=25)
                    if not val and not reason_code:
                         return HttpResponse("Field left blank - file could not be uploaded")

                airwaybill_num = import_sheet.cell_value(rowx=a, colx=0)
                product_type = import_sheet.cell_value(rowx=a, colx=2)
                product_type = product_type.lower()
                if airwaybill_num:
                 if Shipment.objects.filter(airwaybill_number=airwaybill_num):
                   awb_num = Shipment.objects.get(airwaybill_number=airwaybill_num)
                   #if (awb_num.status <> 0 and awb_num.status <> 1 and awb_num.return_shipment <> 0):
                   if (awb_num.status >=2 or awb_num.return_shipment > 0):
                     return HttpResponse("Used Air waybill entered, please recheck file before uploading.")
                #except:
                #  pass
                   if airwaybill_num not in dup_awb:
                          dup_awb.append(airwaybill_num)
                   else:
                       return HttpResponse("Recheck file, duplicate airwaybill number found")

            for rx in range(1, import_sheet.nrows):
                airwaybill_num = import_sheet.cell_value(rowx=rx, colx=0)
                try:
                    reason_code = import_sheet.cell_value(rowx=rx, colx=25)
                    rev_shipment_id = import_sheet.cell_value(rowx=rx, colx=23)
                    if reason_code:
                       reason_code = int(reason_code)
                except:
                    reason_code = None
                    rev_shipment_id = None
               # reason_code = int(reason_code) if reason_code else reason_code
                # if airway bill is not present for the row, then check whether
                # reason code is given.
                if airwaybill_num in ['', None] and reason_code:
                    if rev_shipment_id in ['',None]:
                        return HttpResponse("Reason code is given but reverse shipment id is blank")
                    try:
                        reason_code_obj = PickupStatusMaster.objects.get(code=int(reason_code))
                        if reverse_pickup:
                            rev_shipment  = ReverseShipment.objects.get(id=int(rev_shipment_id))
                            rev_shipment.reason_code = reason_code_obj # updating the reason code
                            rev_shipment.save()
                    except PickupStatusMaster.DoesNotExist:
                        return HttpResponse("Invalid Reason code. Please verify the reason code - %s " % reason_code)
                    continue
                try:
                   awb_num = AirwaybillNumbers.objects.get(airwaybill_number=airwaybill_num)
                   awb_num.status=1
                   awb_num.save()
                except:
                    return HttpResponse("Wrong airwaybill Number")
                order_num = repr(import_sheet.cell_value(rowx=rx, colx=1))
                if order_num.replace(".", "", 1).isdigit():
                       order_num = int(float(order_num))
                else:
                       order_num = import_sheet.cell_value(rowx=rx, colx=1)
                product_type = import_sheet.cell_value(rowx=rx, colx=2)
                product_type = product_type.lower()
                if str(airwaybill_num)[0] in ["1","2","3"]:
                           product_type="ppd"
                elif str(airwaybill_num)[0] in ["7","8","9"]:
                           product_type="cod"
                shipper = import_sheet.cell_value(rowx=rx, colx=3)
                shipper = pickup.customer_code

            #    if shipper <> awb_num.awbc_info.get().customer:
             #            return HttpResponse("Airwaybill does not belong to this Customer, please recheck")
                if reverse_pickup:
                   consignee = pickup.subcustomer_code.name
                   consignee_address1 = pickup.subcustomer_code.address.address1
                   consignee_address2 = pickup.subcustomer_code.address.address2
                   consignee_address3 = pickup.subcustomer_code.address.address3

                   destination_city = pickup.subcustomer_code.address.city
                   pincode = pickup.subcustomer_code.address.pincode
                   state = ""
                   mobile = ""
                   telephone = ""
                else:

                   consignee = import_sheet.cell_value(rowx=rx, colx=4)
                   consignee_address1 = import_sheet.cell_value(rowx=rx, colx=5)
                   consignee_address2 = import_sheet.cell_value(rowx=rx, colx=6)
                   consignee_address3 = import_sheet.cell_value(rowx=rx, colx=7)

                   destination_city = import_sheet.cell_value(rowx=rx, colx=8)
                   pincode = import_sheet.cell_value(rowx=rx, colx=9)
                   state = import_sheet.cell_value(rowx=rx, colx=10)
                   mobile = import_sheet.cell_value(rowx=rx, colx=11)
                   telephone = import_sheet.cell_value(rowx=rx, colx=12)
                item_description = import_sheet.cell_value(rowx=rx, colx=13)
                pieces = import_sheet.cell_value(rowx=rx, colx=14)
                collectable_value=import_sheet.cell_value(rowx=rx, colx=15)
                declared_value=import_sheet.cell_value(rowx=rx, colx=16)
                actual_weight = import_sheet.cell_value(rowx=rx, colx=17)
                volumetric_weight = import_sheet.cell_value(rowx=rx, colx=18)
                length = import_sheet.cell_value(rowx=rx, colx=19)
                breadth = import_sheet.cell_value(rowx=rx, colx=20)
                height = import_sheet.cell_value(rowx=rx, colx=21)
                if length == "":
                   length = 0.0
                if breadth == "":
                   breadth = 0.0
                if height == "":
                   height = 0.0
                if actual_weight == "":
                   actual_weight = 0.0
                if not (isinstance(volumetric_weight, float) or isinstance(volumetric_weight, int)):
                  if volumetric_weight.strip() == "":
                   volumetric_weight = 0.0
                if ((actual_weight > 10.0) or (volumetric_weight > 10.0)):
                      a = str(airwaybill_num)+"("+str(max(actual_weight,volumetric_weight))+"Kgs)"
                      awb_overweight.append(a)
                if collectable_value == "":
                   collectable_value = 0.0
                else:
                    try:
                        int(collectable_value)
                    except ValueError:
                        collectable_value = collectable_value.replace(",", "")
                if declared_value == "":
                   declared_value = 0.0
                else:
                   try:
                        int(declared_value)
                   except ValueError:
                        declared_value = declared_value.replace(",", "")
                if mobile == "":
                   mobile = 0

                if pincode == "":
                   pincode = 0.0
                   tt_duration = 0
                else:

                    origin_pincode=pickup.pincode
                    if not Pincode.objects.filter(pincode=pincode):
                        pincode = 0.0
                        tt_duration = 0
                    try:
                        pincode1 = Pincode.objects.get(pincode=origin_pincode)
                        origin_service_centre = pickup.service_centre
                        sctmg = ServiceCenterTransitMasterGroup.objects.get(service_center=origin_service_centre)
                        dest_pincode=Pincode.objects.get(pincode=pincode)
                        dest_service_centre = dest_pincode.service_center
                        tt_duration = 0

                        transit_time = TransitMaster.objects.get(transit_master=sctmg.transit_master_group, dest_service_center=dest_service_centre)
                        transit_time_cutoff =  TransitMasterCutOff.objects.get(transit_master_orignal=sctmg.transit_master_group,
                                            transit_master_dest=dest_service_centre.servicecentertransitmastergroup_set.get())
                        if not transit_time_cutoff:
                            cutoff = datetime.datetime.strptime(transit_time.cutoff_time,"%H%M")
                        else:
                            cutoff = datetime.datetime.strptime(transit_time_cutoff[0].cutoff_time,"%H%M")

                        tt_duration=int(transit_time.duration)
                    except TransitMasterCutOff.DoesNotExist:
                        tt_duration=0
                try:
                 shipment = Shipment.objects.filter(airwaybill_number=airwaybill_num, status__in=[0,1]).update(order_number=str(order_num), current_sc=pickup.service_centre, product_type=product_type, shipper=shipper, pickup=pickup, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, state=state, mobile=mobile, telephone=telephone, item_description=item_description, pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, actual_weight=float(actual_weight), volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height)
                 shipment = Shipment.objects.get(airwaybill_number=airwaybill_num)
                except:
                  shipment = Shipment(airwaybill_number=int(airwaybill_num), order_number=str(order_num), current_sc=pickup.service_centre, product_type=product_type, shipper=shipper, pickup=pickup, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, state=state, mobile=mobile, telephone=telephone, item_description=item_description, pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height)
                  shipment.save()
                shipment.actual_weight = float(actual_weight)
                shipment.save()
              #  if pickup.id == 12942:
               #     return HttpResponse(shipment.actual_weight)
                if pincode:
                    try:
                      pincode = Pincode.objects.get(pincode=shipment.pincode)
                      servicecentre = pincode.service_center
                      shipment.service_centre = servicecentre
                      shipment.original_dest = servicecentre
                      shipment.save()
                    except:
                      pincode = ""
                if reverse_pickup:
                    try:
                        rev_shipment_id = import_sheet.cell_value(rowx=rx, colx=23)
                        rev_shipment  = ReverseShipment.objects.get(id=int(rev_shipment_id))
                        rev_shipment.shipment = shipment
                        if airwaybill_num:
                           rev_shipment.airwaybill_number = int(airwaybill_num)
                        if order_num:
                           rev_shipment.order_number=str(order_num)
                        rev_shipment.save()
                    except IndexError:
                        pass

                if tt_duration == 0:
                     tt_duration =3
                if tt_duration <> 0:
                     if shipment.added_on.time() > cutoff.time():
                         tt_duration+=1
                     expected_dod = shipment.added_on + datetime.timedelta(days=tt_duration)
                     try:
                         HolidayMaster.objects.get(date=expected_dod.date())
                         expected_dod = expected_dod + datetime.timedelta(days=1)
                     except:
                         pass
                     shipment.expected_dod=expected_dod

                     shipment.save()
                if shipment:
                   history_update(shipment, 0, request)
          else:
              pass

          if pickup.reverse_pickup:
                 piece = ReverseShipment.objects.filter(pickup=pickup, reason_code__isnull=False)
                 pickup.pieces=pickup.pieces - piece.count()
                 pickup.save()
          group = Group.objects.get(name="Customer Service")
          a=0
          if request.user.groups.filter(name="Customer Service").exists():
            pickup = PickupRegistration.objects.filter().order_by('-added_on')
            a=1
          if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
               pickup = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre, status=0)
          else:
               pickup = PickupRegistration.objects.filter(status=0).order_by('-added_on')
          msg = ""
          if awb_overweight:
              msg = "Following Air Waybills have weight more than 10 kgs, PLEASE CONFIRM !!!, and incase of mismatch re-upload the file:\n"+"\n".join(['%s' % ship for ship in awb_overweight])
          customer=Customer.objects.all()
          destination= ServiceCenter.objects.all()
          return render_to_response("pickup/pickupdashboard.html",
                              {'pickup':pickup,
                               'msg':msg,
                               'a':a,
                               'customer':customer,
                               'sc':destination},
                               context_instance=RequestContext(request))

    else:
     return render_to_response('service_centre/upload_file.html',
                               {'pid':pid,
                                },context_instance=RequestContext(request))

@csrf_exempt
def shipment_orders(request):
         awb = request.POST['awb']
         try:
          pickups = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre)
          shipment = Shipment.objects.get(airwaybill_number=int(awb),status_type__in=[0,1], pickup__in=pickups, status__lt= 3)

          return HttpResponseRedirect("/service-centre/order_pricing/")
         except:
          return HttpResponse("Incorrect Airway Bill Number")

@csrf_exempt
def order_pricing(request, sh=None, type=0):
     awb= sh.airwaybill_number if sh else request.POST['awb']

     ship = Shipment.objects.filter(airwaybill_number=awb, status__in=[0,1,2]).select_related('pickup__service_centre__center_shortcode','shipper__name', 'shipper__code').only('shipper__code','shipper__name','airwaybill_number','consignee','pieces','pickup__service_centre__center_shortcode','added_on','id','expected_dod','status_type','status','return_shipment','rts_status','reason_code','inscan_date','product_type','collectable_value','order_number','service_centre','actual_weight','pincode').exclude(status=9).exclude(reason_code__code__in = [333, 888, 999]).exclude(rts_status = 2)
     if not ship:
         return HttpResponse("Incorrect Airway Bill Number")
     else:
          shipment = ship[0]

     status_type = 1#verified
     if not Pincode.objects.filter(pincode=shipment.pincode):
         status_type = 2
     #if (shipment.product_type=="cod" and shipment.collectable_value <= 0.0):
     #               status_type = 3
     if (shipment.order_number == "") or (shipment.service_centre == "") or (shipment.actual_weight <= 0.0):
                    status_type = 4
     ship.update(status_type=status_type)

     if status_type <> 1:
     #    order.save()
         return render_to_response("service_centre/shipment_data.html",
                                  {'a':ship[0],
                                   'status':"2"
       })
     if (shipment.rto_status == 1 or shipment.rts_status==1):
         ship.update(status=2, manifest_location = request.user.employeemaster.service_centre, current_sc=request.user.employeemaster.service_centre)
         if type == 1:
            history_update(shipment, 2, request, "Shipment Auto in-scan", shipment.reason_code)
         else:
            history_update(shipment, 2, request, "", shipment.reason_code)
#         pickups = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre)
#         total_records = Shipment.objects.filter(status__in=[0,1,2], pickup__in=pickups).count()
#         success_count = Shipment.objects.filter(status_type=1, status__in=[1,2], pickup__in=pickups).count()
#         mismatch_count = Shipment.objects.filter(status__in=[0,1,2], pickup__in=pickups, status_type__in= [2,3,4]).count()
         return render_to_response("service_centre/shipment_data.html",
                                      {'a':ship[0],
                                       'status':"2",
                                       'total_records':0,
                                       'sucess_count':0,
                                       'mismatch_count':0
           })
     if not shipment.inscan_date:
         ship.update(inscan_date=now)
    #     order.inscan_date = now #orig inscan date
    # order.save()
     price_updated(ship[0])
 #    shipment = order
     if status_type == 1:
        ship.update(status=2, manifest_location = request.user.employeemaster.service_centre, current_sc=request.user.employeemaster.service_centre)
     if type == 1:
            history_update(shipment, 2, request, "Shipment Auto in-scan", shipment.reason_code)
     else:
          history_update(shipment, 2, request, "", shipment.reason_code)
     #pickups = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre)
     #total_records = Shipment.objects.filter(status__in=[0,1,2], pickup__in=pickups).count()
     #success_count = Shipment.objects.filter(status_type=1, status__in=[1,2], pickup__in=pickups).count()
     #mismatch_count = Shipment.objects.filter(status__in=[0,1,2], pickup__in=pickups, status_type__in= [2,3,4]).count()
     return render_to_response("service_centre/shipment_data.html",
                                  {'a':ship[0],
                                   'status':"2",
                                   'total_records':0,
                                   'sucess_count':0,
                                   'mismatch_count':0
       })



def bagging(request):
    #before = now - datetime.timedelta(days=2)
    if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
        bags = Bags.objects.using('local_ecomm').filter(
            bag_status__in=[0,1,2], added_on__range=(before, now),
            origin=request.user.employeemaster.service_centre
        ).exclude(bag_status__in=[9,10,11]).order_by('-id')
    else:
        bags = Bags.objects.using('local_ecomm').filter(
            bag_status__in=[0,1,2], added_on__range=(before, now)
        ).exclude(bag_status__in=[9,10,11]).order_by("-id")

    service_centre = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response(
        "service_centre/bagging.html",
        {'bags':bags, 'service_centre':service_centre,
            'origin_sc':request.user.employeemaster.service_centre},
        context_instance=RequestContext(request))

@json_view
def check_bagging(request):
    if request.method == "GET":
        if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
            bags = Bags.objects.using('local_ecomm').filter(
                employee_code=request.user.employeemaster
            , bag_status = 0).order_by('-id')
            if bags:
                return {'success': True,'message':'Please close bag first!'}
            else:
                return {'success': False}
       #else:
       #    bags = Bags.objects.using('local_ecomm').filter(
       #        bag_status__in=[1,6]
       #    ).exclude(bag_status__in=[9,10,11]).order_by("-id")
       #if bags:
       #    bags_closed = Bags.objects.using('local_ecomm').filter(bag_status__in=[1,6])
       #    if not bags_closed:
       #        return {'success': True,'message': 'Please close bag first!'}
       #    else:
       #        return {'success': False}
        else:
            return {'success': False}

@json_view
@csrf_exempt
def add_bagging(request):
    bag_type = request.POST['bag_type']
    bag_size = request.POST['bag_size']
    bag_number = request.POST['bag_num']
    hub = request.POST['hub']
    destination = request.POST['dest']

    if Bags.objects.filter(bag_number=bag_number).exists():
        return {'success': False, 'message': 'Bag number already exists'}

    origin = request.user.employeemaster.service_centre 
    if int(hub):
        hub = ServiceCenter.objects.get(id=int(hub))
    else:
        hub = None

    if int(destination):
        destination = ServiceCenter.objects.get(id=int(destination))
    else:
        destination = None

    bag = Bags.objects.create(
        bag_number=bag_number, bag_type=bag_type, bag_size=bag_size,
        origin=origin, hub=hub, destination=destination, current_sc=origin, employee_code=request.user.employeemaster)

    update_bag_history(
        bag, employee=request.user.employeemaster, action="created",
        content_object=bag, sc=request.user.employeemaster.service_centre,
        status=1)

    html = render_to_string(
        "service_centre/bag_data.html", {'a':bag},
        context_instance=RequestContext(request))

    return {'success': True, 'html': html}

@csrf_exempt
def include_shipment(request, bid):
    bags = Bags.objects.get(id=bid)
    if request.POST:
        if bags.bag_status in [1, 6]:
            return HttpResponse("Bag is already closed")
        awb_number= request.POST['awb']
        if bags.bag_type == "mixed":
            try:
                shipment = Shipment.objects.filter(airwaybill_number=awb_number)\
                    .exclude(status=9)\
                    .exclude(reason_code__code__in = [333, 888, 999])\
                    .exclude(rts_status = 2)
                if not shipment:
                    return HttpResponse("Soft Data not Uploaded")
                if not Pincode.objects.filter(pincode=shipment[0].pincode):
                    return HttpResponse("Non Serviceable pincode")

                if shipment[0].status in [3, 5]:
                    bag = shipment[0].bags_set.all()
                    if bag.exists():
                        return HttpResponse("Shipment already bagged in bag number %s"%(bag[0].bag_number))
                shipment = shipment.get(status__in=[0,1,2,4])
            except:
                return HttpResponse("Incorrect Shipment Number")
        else:
            try:
                shipment = Shipment.objects.filter(
                    airwaybill_number=awb_number
                ).exclude(status=9).exclude(
                    reason_code__code__in = [333, 888, 999]
                ).exclude(rts_status = 2)
                if not shipment:
                    return HttpResponse("Soft Data not Uploaded")
                if not Pincode.objects.filter(pincode=shipment[0].pincode):
                    return HttpResponse("Non Serviceable pincode")
                shipment = shipment.get(service_centre=bags.destination, status__in=[0,1,2,4])
            except:
               return HttpResponse("Incorrect Shipment Number")

        if shipment.status in [0,1]:
            order_pricing(request, shipment, 1)
        if shipment.status_type in [0,1]:
            bag_no = bags.bag_number if bags.bag_number else bags.id
            if shipment.status in [0,1,2]:
                Shipment.objects.filter(id=shipment.id).update(status_type=0, status=3)
                if bags.hub:
                     dst = bags.hub
                else:
                     dst = bags.destination
                history_update(shipment, 3, request, "Shipment connected to %s (Bag No. %s)"%(dst, bag_no))
            elif shipment.status == 4:
                Shipment.objects.filter(id=shipment.id).update(status_type=0, status=5)
                history_update(shipment, 5, request, "Shipment connected from HUB (Bag No. %s)"%(bag_no))

            bags.shipments.add(shipment)
            bags.ship_data.add(shipment)
            return render_to_response(
                "service_centre/shipment_bagging_data.html",
                {'shipment':shipment},
                context_instance=RequestContext(request)
            )
        else:
            return HttpResponse('Invalid Airwaybill number')
    else:
        shipment = bags.shipments.filter()
        shipment_count = shipment.count()
        return render_to_response(
            "service_centre/include_shipment.html",
            {'bags':bags, 'shipment':shipment,
                'shipment_count':shipment_count, 'bid':bid},
            context_instance=RequestContext(request)
        )


@csrf_exempt
def delink_shipment(request, bid):
    bags = Bags.objects.get(id=bid)
    if request.POST:
       if bags.bag_status in [1, 6]:
           return HttpResponse("bag already closed")
       awb_number= request.POST['awb']
       try:
           shipment = Shipment.objects.get(airwaybill_number=awb_number)
           bag_no = bags.bag_number if bags.bag_number else bags.id
           if shipment.status == 3:
               shipment.status_type=1
               shipment.status=2
               history_update(shipment, 2,request, "Shipment disconnected from PPC (Bag No. %s)"%(bag_no))
           elif shipment.status == 5:
               shipment.status_type=1
               shipment.status=4
               history_update(shipment, 4,request, "Shipment disconnected from HUB (Bag No. %s)"%(bag_no))
           shipment.save()
           bags.shipments.remove(shipment)
           bags.ship_data.remove(shipment)
           return HttpResponse("Shipment removed Sucessfully")
       except:
           return HttpResponse("Incorrect Shipment Number")
    else:
        shipment = bags.shipments.all()
        shipment_count = shipment.count()
        return render_to_response("service_centre/delink_shipment.html",
            {'bags':bags, 'shipment':shipment, 'shipment_count':shipment_count,
             'bid':bid}, context_instance=RequestContext(request))

def generate_manifest(request, bid):

     bags=Bags.objects.get(id=bid)
     shipment = bags.shipments.all()
     for a in shipment:
         a.save()
     order_info={}
     shipment_sum = ""
     shipment_sum  =  bags.shipments.aggregate(Sum('actual_weight'))
     shipment_sum  =  shipment_sum['actual_weight__sum']
     user=request.user.employeemaster.employee_code

     print_no = request.GET.get('print', 0)
     if not int(print_no):
        return render_to_response("service_centre/manifest.html",
                                  {'bags':bags,
                                   'shipment':shipment,
                                   'bid':bid,
                                   'user':user,
                                   'total_weight':shipment_sum},
                                   context_instance=RequestContext(request))


     elif int(print_no) == 1:
        text = render_to_string("service_centre/manifest_txt.html",
                                  {'bags':bags,
                                   'shipment':shipment,
                                   'bid':bid,
                                   'user':user,
                                   'total_weight':shipment_sum},
                                   context_instance=RequestContext(request))
        response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename=delivery_manifest.txt'
        return response
     elif int(print_no) == 2:
        return render_to_response("service_centre/manifest_lazer.html",
                                  {'bags':bags,
                                   'shipment':shipment,
                                   'bid':bid,
                                   'user':user,
                                   'total_weight':shipment_sum},
                                   context_instance = RequestContext(request))

@csrf_exempt
def pup_data(request):
    pid = request.POST['pup_num']
    pickup = PickupRegistration.objects.get(id=pid)
    pickup_info = {}

    for k, v in pickup.get_fields():
        pickup_info[k]=v

    pickup_json = json.dumps(pickup_info)
    return HttpResponse(pickup_json)

@csrf_exempt
def awb_data(request):
    awb = request.POST['awb_num']
    shipment = Shipment.objects.get(airwaybill_number=awb)
    shipment_info = {}

    for k, v in shipment.get_fields():
        shipment_info[k]=v

    shipment_json = json.dumps(shipment_info)
    return HttpResponse(shipment_json)

@csrf_exempt
@json_view
def close_bagging(request):
    if not request.method == 'POST':
        return {'success': False, 'message':'Not an authorized request'}

    bag_id = request.POST['bag_id']
    #bag_number = request.POST['bag_number']
    #match = re.match(r'\w+$', bag_number)
    #if not match:
        #return {'success': False, 'message':'Invalid Bag number. Only Alapha numerals allowed.'}
    #bag_number = match.group()

    bag = Bags.objects.get(id=bag_id)
    if bag.bag_status in [1, 6]:
        return {'success': False, 'message': 'Bag already closed.'}

    #if Bags.objects.filter(bag_number=bag_number).exists():
        #return {'success': False, 'message': 'Bag number already exists'}

    weight_sum =  bag.shipments.aggregate(Sum('actual_weight'))['actual_weight__sum']

    if bag.bag_status == 5:
        bag_status = 6
    else:
        bag_status = 1

    Bags.objects.filter(id=bag_id).update(
        bag_status=bag_status, actual_weight=weight_sum
    )
    bag = Bags.objects.get(id=bag_id)
    update_bag_history(
        bag, employee=request.user.employeemaster,
        action="closed (No. of Shipments - %s)"%(bag.shipments.count()),
        content_object=bag, sc=request.user.employeemaster.service_centre,
        status=2)
    update_bag_remarks(bag.bag_number, 1)
    update_trackme_bagging_remarks(bag.bag_number)
    return {'success': True, 'message': 'Bag closed'}

@csrf_exempt
def connection(request):
    before1 = now - datetime.timedelta(days=3)
    if request.POST:
        destination = request.POST['dest']
        coloader = request.POST['coloader']
        vehicle_num = request.POST['vehicle']
        origin_sc = request.POST['origin_sc']

        coloader = Coloader.objects.get(id=int(coloader))
        destination = ServiceCenter.objects.get(id=int(destination))
        origin = ServiceCenter.objects.get(id=int(origin_sc))
        connection = Connection.objects.create(
            coloader=coloader, destination=destination,
            vehicle_number=vehicle_num, origin=origin
        )
        return render_to_response("service_centre/connection_data.html",
                        {"a":connection},
                        context_instance=RequestContext(request))
    else:
        if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
            connection = Connection.objects.filter(
                 connection_status__in=[0,1], added_on__range=(before1, now),
                 origin=request.user.employeemaster.service_centre
            ).order_by('-id')
        else:
            connection = Connection.objects.filter(
                connection_status__in=[0,1], added_on__range=(before1, now)
            ).order_by('-id')

        coloader = Coloader.objects.all()
        service_centre = ServiceCenter.objects.all()

        return render_to_response("service_centre/connection.html",
            {
                "connection":connection, 'coloader':coloader,
                'service_centre':service_centre,
                'origin_sc':request.user.employeemaster.service_centre
            },
            context_instance=RequestContext(request))

@csrf_exempt
def run_code(request):
    if request.POST:

     #destination=ServiceCenter.objects.get(id=int(destination))
     vehicle_num=request.POST['vehicle']
     coloader=request.POST['coloader']
     coloader=Coloader.objects.get(id=int(coloader))
     origin_sc = request.user.employeemaster.service_centre
     runcode = RunCode.objects.create(coloader=coloader, vehicle_number=vehicle_num, origin=origin_sc)
     destination=request.POST['dest']
     destination = [int(x) for x in destination.split(",")]
     for a in destination:
         destination=ServiceCenter.objects.get(id=a)
         runcode.destination.add(destination)
     return render_to_response("service_centre/runcode_data.html",
                               {"a":runcode},
                               context_instance=RequestContext(request))

    else:
        coloader = Coloader.objects.all()
        service_centre = ServiceCenter.objects.all()
        run_code = RunCode.objects.filter(runcode_status__in=[0,1], added_on__range=(before, now),origin=request.user.employeemaster.service_centre).order_by('-id')
        return render_to_response("service_centre/run_code.html",
                                  {'coloader':coloader,
                                   'service_centre':service_centre,
                                   'run_code':run_code
                                    },
                                  context_instance=RequestContext(request))


def connection_include_bag(bag_number, cid, emp):
    user_sc = emp.service_centre
    connection = Connection.objects.get(id=cid)
    destination = connection.destination
    try:
        hub_dest = HubServiceCenter.objects.filter(hub=destination).values_list('sc')
        if hub_dest:
            bag = Bags.objects.get(
                Q(bag_number=bag_number) & Q(bag_status__in =[1,3,6]),
                Q(current_sc=user_sc) | Q(origin=user_sc),
                Q(destination__in=hub_dest) | Q(hub=destination),
            )
        else:
            bag = Bags.objects.get(
                Q(bag_number=bag_number) & Q(bag_status__in =[1,3,6]) &
                (Q(destination=destination) | Q(hub=destination)) &
                (Q(origin=user_sc) | Q(current_sc=user_sc))
            )
    except Bags.DoesNotExist:
        return None

    if bag.bag_status == 6:
         bag_status=7
    else:
         bag_status=2
    
    Bags.objects.filter(bag_number=bag_number).update(bag_status=bag_status)
    bag = Bags.objects.get(bag_number=bag_number)
    connection.bags.add(bag)

    return True


@json_view
def get_connection_bags(request):
    cid = request.GET.get('cid')
    connection = Connection.objects.get(id=cid)
    bags = connection.bags.all()
    cbags = ConsolidatedBagConnection.objects.filter(connection=connection)
    all_bags = list(bags) + [bag.consolidated_bag for bag in cbags]
    html = render_to_string(
        "service_centre/connection_include_bags.html", {'bags':all_bags})
    return {'success': True, 'html': html, 'cid': cid}


@json_view
def include_bags_connection(request):
    if request.method == 'POST':
        cid = request.POST.get('cid')
        bag_number= request.POST.get('bag_num')
        connection = Connection.objects.get(id=cid)
        emp = request.user.employeemaster
        user_sc = emp.service_centre
        try:
            bag = Bags.objects.get(bag_number=bag_number)
            success = connection_include_bag(bag_number, cid, emp)

            if not success:
                return {'success': False, 'message': 'This bag cant be included'}
            else:
                update_bag_history(
                    bag, employee=emp, action="connected to %s"%(connection.destination),
                    content_object=connection, sc=user_sc, status=6)
                ship_count = bag.shipments.aggregate(ct=Count('id'))['ct']
                ship_count = ship_count if ship_count else 0
                html = render_to_string(
                    "service_centre/connection_bag_row.html", {'bag':bag})
                return {'success': True, 'html': html, 'ship_count': ship_count}
        except Bags.DoesNotExist:
            try:
                cbag = ConsolidatedBag.objects.get(bag_number=bag_number)
                cbag_connection = cbag.add_to_connection(cid)
                if cbag_connection: 
                    html = render_to_string(
                        "service_centre/connection_bag_row.html", 
                        {'bag':cbag_connection.consolidated_bag})
                    ship_count = cbag.get_ship_count
                    return {'success': True, 'html': html, 'ship_count': 1}
                else:
                    return {
                        'success': False, 
                        'message': 'Bag {0} already added'.format(bag_number)}
            except ConsolidatedBag.DoesNotExist:
                return {'success': False, 'message': 'This bag cant be included'}


@csrf_exempt
def include_bags(request, cid):
    connection = Connection.objects.get(id=cid)
    if request.POST:
       bag_number= request.POST['bag_num']
       try: 
           destination = connection.destination
           hub_dest = HubServiceCenter.objects.filter(hub=destination).values_list('sc')
           if hub_dest:
               bag = Bags.objects.filter(
                   bag_number=bag_number, bag_status__in =[1,3,6]
               ).filter(
                   Q(current_sc=request.user.employeemaster.service_centre) | Q(origin=request.user.employeemaster.service_centre)
               ).filter(Q(destination__in=hub_dest) | Q(hub=destination))
               bag = bag[0]
           else:
               bag = Bags.objects.get(
                   Q(bag_number=bag_number) & Q(bag_status__in =[1,3,6]) &
                   (Q(destination=connection.destination) | Q(hub=connection.destination)) &
                   # added by jignesh
                   (Q(origin=request.user.employeemaster.service_centre) | Q(current_sc=request.user.employeemaster.service_centre)),
                  # origin=request.user.employeemaster.service_centre
                   )

         # destination = connection.destination
         # hub_dest = HubServiceCenter.objects.filter(hub=destination).values_list('sc')
         # if hub_dest:
         #     bag = Bags.objects.filter(bag_number=bag_number,
         #         bag_status__in =[1,3,6], current_sc=request.user.employeemaster.service_centre
         #     ).filter(Q(destination__in=hub_dest) | Q(hub=destination)  )
         #     bag = bag[0]
         # else:
         #     bag = Bags.objects.get(
         #         Q(bag_number=bag_number) & Q(bag_status__in =[1,3,6]) &
         #         (Q(destination=connection.destination) | Q(hub=connection.destination)), 
         #         current_sc=request.user.employeemaster.service_centre)
       except:
           return HttpResponse("Incorrect Bag Number")

       shipment_sum  =  bag.shipments.aggregate(Sum('actual_weight'))['actual_weight__sum']

       if bag.bag_status == 6:
            bag.bag_status=7
            bag.save()
            connection.bags.add(bag)
       else:
            bag.bag_status=2
            bag.save()
            connection.bags.add(bag)

       update_bag_history(
           bag, employee=request.user.employeemaster,
           action="connected to %s"%(connection.destination),
           content_object=connection,
           sc=request.user.employeemaster.service_centre, status=6)
       return render_to_response(
           "service_centre/connection_bags_data.html", {'a':bag})
    else:
        bags = connection.bags.all()
        bag_count = bags.count()
        return render_to_response(
            "service_centre/include_bags.html",
            {'connection':connection, 'bags':bags, 'bag_count':bag_count, 'cid':cid},
            context_instance=RequestContext(request))


@csrf_exempt
def delink_bags(request, cid):
    connection = Connection.objects.get(id=cid)
    if request.POST:
       bag_number= request.POST['bag_num']
       try:
           bag = Bags.objects.get(bag_number=bag_number)
           if bag.bag_status == 7:
               bag.bag_status=6
           else:
               bag.bag_status=1
           bag.save()
           connection.bags.remove(bag)

           update_bag_history(bag, employee=request.user.employeemaster, action="delinked from connection",
              content_object=connection, sc=request.user.employeemaster.service_centre,
              status=5
           )
           return HttpResponse("Bag removed Sucessfully")

       except:
           return HttpResponse("Incorrect Bag Number")
    else:
        bags = connection.bags.all()
        bag_count = bags.count()
        return render_to_response("service_centre/delink_bags.html",
                                  {'connection':connection,
                                   'bags':bags,
                                   'bag_count':bag_count,
                                   'cid':cid,},
                                   context_instance=RequestContext(request))

def generate_challan(request, cid):
     connection=Connection.objects.get(id=cid)
     bags = connection.bags.all()
     order_info={}
     for a in bags:
        if not order_info.get(a):
            order_info[a]=a.shipments.all().count()
     user=request.user.employeemaster
     print_no = request.GET.get('print', 0)
     if not int(print_no):
        return render_to_response("service_centre/challan.html",
                                  {'connection':connection,
                                   'bags':bags,
                                   'order_info':order_info,
                                   'user':user
                                   },
                                   context_instance=RequestContext(request))
     elif int(print_no) == 1:
        text =  render_to_string("service_centre/challan_txt.html",
                                  {'connection':connection,
                                   'bags':bags,
                                   'order_info':order_info,
                                   'user':user
                                   },
                                   context_instance=RequestContext(request))
        response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename=challan.txt'
        return response
     elif int(print_no) == 2:
        return render_to_response("service_centre/challan_lazer.html",
                                  {'connection':connection,
                                   'bags':bags,
                                   'order_info':order_info,
                                   'user':user
                                   },
                                   context_instance = RequestContext(request))

@csrf_exempt
def close_connection(request):
    connection_id=request.POST['connection_id']
    connection = Connection.objects.get(id=connection_id)
    # following function to be updated async
    octroi_update_for_connection(connection)
    connection.connection_status = 1
    connection.save()
    ConnectionQueue.objects.create(connection=connection, employee=request.user.employeemaster)
    return HttpResponse("Sucess")

@csrf_exempt
def close_runcode(request):
    runcode_id=request.POST['runcode_id']
    runcode = RunCode.objects.get(id=runcode_id)

    try:
      for connection in runcode.connection.all():
        conn = Connection.objects.get(id=connection.id)
        for bags in conn.bags.all():
            bag = Bags.objects.get(id=bags.id)
            for shipment in bag.shipments.filter().exclude(status=9).exclude(reason_code__code__in = [333, 888, 999]).exclude(rts_status = 2):
                history_update(shipment,13,request, "Bag ready for connection (Run Code: %s)"%(runcode_id))
    except:
        pass
    runcode.runcode_status = 1
    runcode.save()
    return HttpResponse("Sucess")

@csrf_exempt
def include_connection(request, rid):
    runcode = RunCode.objects.get(id=rid)
    if request.POST:
       connection_number= request.POST['connection_num']
       try:
           connection = Connection.objects.get(id=int(connection_number), connection_status__in=[1,2,4])
       except:
           return HttpResponse("Incorrect Connection")
       if connection.runcode_set.all():
            return HttpResponse("Already Included")
       connection.actual_weight = request.POST['actual_weight']
       connection.save()
       if connection.connection_status == 1:
            connection.connection_status=2
            connection.save()
       if connection.connection_status == 4:
            connection.connection_status=5
            connection.save()
       if connection.connection_status == 3:
            connection.connection_status=5
            connection.save()
       runcode.connection.add(connection)

       connection = Connection.objects.get(id=int(connection_number))
       bags = connection.bags.all()
       #for bag in bags:
           #update_bag_history(bag, employee=request.user.employeemaster, action="connection added to runcode",
            #        content_object=runcode, sc=request.user.employeemaster.service_centre)
       return render_to_response("service_centre/runcode_connection_data.html",
                                 {'a':connection
                                  },)
    else:
        connection = runcode.connection.all()
        connection_count = connection.count()
        return render_to_response("service_centre/include_connection.html",
                                  {'runcode':runcode,
                                   'connection':connection,
                                   'connection_count':connection_count,
                                   'rid':rid,},
                                   context_instance=RequestContext(request))

@csrf_exempt
def delink_connection(request, rid):
    runcode = RunCode.objects.get(id=rid)
    if request.POST:
       connection_number= request.POST['connection_num']
       connection = Connection.objects.get(id=int(connection_number))
       connection.save()
       if connection.connection_status == 2:
            connection.connection_status=1
            connection.save()
       if connection.connection_status == 5:
            connection.connection_status=4
            connection.save()
       runcode.connection.remove(connection)

       bags = connection.bags.all()
       #for bag in bags:
           #update_bag_history(bag, employee=request.user.employeemaster, action="connection removed from runcode",
            #        content_object=runcode, sc=request.user.employeemaster.service_centre)
       return HttpResponse("Bag removed Sucessfully")

    else:
        connection = runcode.connection.all()
        connection_count = connection.count()
        return render_to_response("service_centre/delink_connection.html",
                                  {'runcode':runcode,
                                   'connection':connection,
                                   'connection_count':connection_count,
                                   'rid':rid,},
                                   context_instance=RequestContext(request))


@csrf_exempt
def airport_confirmation(request):
    if request.POST:
      date=request.POST['date']
      run_code=request.POST['run_code']
      run_code = RunCode.objects.get(id=int(run_code))
      flight_num=request.POST['flight_num']
      std=request.POST['std']
      atd=request.POST['atd']
      num_bags=request.POST['num_bags']
      cnote=request.POST['connection']
      status_code=request.POST['status_code']
      airport_confirm = AirportConfirmation(date=date, run_code=run_code, flight_num=flight_num, std=std, atd=atd, num_of_bags=num_bags, cnote=cnote, status_code=status_code,  origin=request.user.employeemaster.service_centre)
      airport_confirm.save()
      mum_sc = ServiceCenter.objects.filter(city__city_shortcode="MUM").exclude(id__in=[180, 178, 179, 192, 205, 206, 211])
      outer_mum_sc = ServiceCenter.objects.filter(id__in=[180, 178, 179, 192, 205, 206, 211])
      try:
       status = ShipmentStatusMaster.objects.get(id=status_code)
       for connection in run_code.connection.all():
        conn = Connection.objects.get(id=connection.id)
        for bags in conn.bags.all():
            bag = Bags.objects.get(id=bags.id)
            update_bag_history(bag, employee=request.user.employeemaster,
                        #action="runcode airport confirmation completed", content_object=airport_confirm,
                        action="intransit (Airport confirmation: %s, Run Code: %s)"%(airport_confirm.id, run_code.id), content_object=airport_confirm,
                        sc=request.user.employeemaster.service_centre, reason_code = status)
            bag.updated_on = now
            bag.save()
            for shipment in bag.shipments.filter().exclude(status=9).exclude(reason_code__code__in = [333, 888, 999]).exclude(rts_status = 2):
                if not bag.hub:
                  if (shipment.pickup.service_centre not in mum_sc) and (shipment.service_centre in mum_sc):
                      OctroiAirportConfirmation.objects.create(airportconfirmation=airport_confirm, shipment=shipment, origin=request.user.employeemaster.service_centre)
                if (shipment.service_centre in outer_mum_sc):
                      NFormAirportConfirmation.objects.create(airportconfirmation=airport_confirm, shipment=shipment, origin=request.user.employeemaster.service_centre)
                history_update(shipment, 14, request, "", status)

      except:
        pass
      return render_to_response("service_centre/airportconfir_data.html",
                                {'a':airport_confirm},
                               context_instance=RequestContext(request))
    else:
      coloader=Coloader.objects.all()
      reason_code = ShipmentStatusMaster.objects.filter().exclude(code__in=[999,777])
      airport_confirm = AirportConfirmation.objects.filter(origin=request.user.employeemaster.service_centre, added_on__range=(before, now)).order_by("-id")
      return render_to_response("service_centre/airportconfir.html",
                                {'coloader':coloader,
                                 'reason_code':reason_code,
                                 'airport_confirm':airport_confirm},
                               context_instance=RequestContext(request))

@csrf_exempt
def reason_code(request):
    reason_code_id=request.POST['reason_code']
    reason_code=ShipmentStatusMaster.objects.get(id=int(reason_code_id))
    return HttpResponse(reason_code.code_description)

@csrf_exempt
def delete_bags(request):
    bag_id=request.POST['bag_num']
   # bag = Bags.objects.get(bag_number=bag_id)
   # if bag.shipments.count() == 0:
    bag = Bags.objects.filter(bag_number=bag_id)
    if bag:
	bag = bag[0]
	if not bag.shipments.all():
           update_bag_history(bag, employee=request.user.employeemaster,
                        action="deleted", content_object=bag,
                        sc=request.user.employeemaster.service_centre)
           bag.bag_status = 11
           bag.save()
           return HttpResponse("Sucess")
    return HttpResponse("1")

@csrf_exempt
def awb_query(request):
    awb=request.POST['awb']
    ship = Shipment.objects.get(airwaybill_number=awb)
    try:
      a = list(ship.bags_set.all())
      bag = a[-1]
    except:
        bag = "Shipment Debagged"
    return HttpResponse(bag)

def download_xcl(request, dtype):
    inscan_list = []
    if dtype == '2':
        shipments = Shipment.objects.filter(status=4, current_sc=request.user.employeemaster.service_centre)
        for a in shipments:
            if a.status_type == 0:#verified
                status = "unverified"
            if a.status_type == 1:#verified
                status = "verified"
            if a.status_type == 2:
                status = "pincode missing"
            if a.status_type == 3:
                status = "value missing"
            if a.status_type == 4:
                status = "data missing"
            if a.status_type == 5:
                status = "extra"
            u = (a.shipper.code, a.consignee, a.destination_city, a.pincode, a.pieces, a.actual_weight, a.airwaybill_number, a.order_number, status)
            inscan_list.append(u)
    elif dtype=='1':
        pickups = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre)
        shipment = Shipment.objects.filter(status__in=[1,2], pickup__in=pickups)
        for a in shipment:
            if a.status_type == 0:#verified
                status = "unverified"
            if a.status_type == 1:#verified
                status = "verified"
            if a.status_type == 2:
                status = "pincode missing"
            if a.status_type == 3:
                status = "value missing"
            if a.status_type == 4:
                status = "data missing"
            if a.status_type == 5:
                status = "extra"

            u = (a.shipper.code, a.consignee, a.destination_city, a.pincode, a.pieces, a.actual_weight, a.airwaybill_number, a.order_number, status)
            inscan_list.append(u)
    elif dtype=='3':
        shipment = Shipment.objects.filter(status = 6, current_sc = request.user.employeemaster.service_centre)
        #return HttpResponse(shipment)
        for a in shipment:
            if a.status_type == 0:#verified
                status = "unverified"
            if a.status_type == 1:#verified
                status = "verified"
            if a.status_type == 2:
                status = "pincode missing"
            if a.status_type == 3:
                status = "value missing"
            if a.status_type == 4:
                status = "data missing"
            if a.status_type == 5:
                status = "extra"
            if not a.shipper:
                u = ("","","","","","",a.airwaybill_number)
            else:
                u = (a.shipper.code, a.consignee, a.destination_city, a.pincode, a.pieces, a.actual_weight, a.airwaybill_number, a.order_number, status, a.added_on.strftime("%d-%m-%Y %H:%M:%S"))
            inscan_list.append(u)
    sheet = book.add_sheet('Inscan')
    sheet.col(1).width = 8000 # 3333 = 1" (one inch).
    for a in range(10):
        sheet.col(a).width = 6000

    sheet.write(3, 1, "Shipper", style=header_style)
    sheet.write(3, 2, "Consignee", style=header_style)
    sheet.write(3, 3, "Destination", style=header_style)
    sheet.write(3, 4, "Pincode", style=header_style)
    sheet.write(3, 5, "Pieces", style=header_style)
    sheet.write(3, 6, "Actual Weight", style=header_style)
    sheet.write(3, 7, "Airwaybill Number", style=header_style)
    sheet.write(3, 8, "Order Number", style=header_style)
    sheet.write(3, 9, "Status", style=header_style)
    style = datetime_style

    for row, rowdata in enumerate(inscan_list, start=4):
        for col, val in enumerate(rowdata, start=1):
                     style = datetime_style
                     sheet.write(row, col, str(val), style=style)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Inscan_report.xls'
    book.save(response)
    return response

def rts_report(request):
        inscan_list = []
        shipment = Shipment.objects.filter(return_shipment=3, current_sc = request.user.employeemaster.service_centre)
        for a in shipment:
            if a.status_type == 0:#verified
                status = "unverified"
            if a.status_type == 1:#verified
                status = "verified"
            if a.status_type == 2:
                status = "pincode missing"
            if a.status_type == 3:
                status = "value missing"
            if a.status_type == 4:
                status = "data missing"
            if a.status_type == 5:
                status = "extra"

            u = (a.shipper.code, a.consignee, a.destination_city, a.pincode, a.pieces, a.actual_weight, a.airwaybill_number, a.order_number, status)
            inscan_list.append(u)
        sheet = book.add_sheet('RTS')
        sheet.col(1).width = 8000 # 3333 = 1" (one inch).
        for a in range(10):
            sheet.col(a).width = 6000

        sheet.write(3, 1, "Shipper", style=header_style)
        sheet.write(3, 2, "Consignee", style=header_style)
        sheet.write(3, 3, "Destination", style=header_style)
        sheet.write(3, 4, "Pincode", style=header_style)
        sheet.write(3, 5, "Pieces", style=header_style)
        sheet.write(3, 6, "Actual Weight", style=header_style)
        sheet.write(3, 7, "Airwaybill Number", style=header_style)
        sheet.write(3, 8, "Order Number", style=header_style)
        sheet.write(3, 9, "Status", style=header_style)
        style = datetime_style

        for row, rowdata in enumerate(inscan_list, start=4):
           for col, val in enumerate(rowdata, start=1):
                             style = datetime_style
                             sheet.write(row, col, str(val), style=style)
        response = HttpResponse(mimetype='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=RTS_report.xls'
        book.save(response)
        return response

@csrf_exempt
def run_code_bags(request):
    runcode = RunCode.objects.get(id=int(request.POST['run_code']))
    count=0
    for connection in runcode.connection.all():
        conn = Connection.objects.get(id=connection.id)
        count = count + conn.bags.all().count()
    return HttpResponse(count)


@developers_only
def shipment_update(request):
  if request.method == 'POST':
    ship_file = request.FILES['ship_file']
    content = ship_file.read()
    wb = xlrd.open_workbook(file_contents=content)
    sheetnames = wb.sheet_names()
    sh = wb.sheet_by_name(sheetnames[0])
    awbn = sh.col_values(0)[1:]
    weight= sh.col_values(1)[1:]
    awb_wt = zip(awbn, weight)
    shipment_not_found = []
    count =0
    for awb, wt in awb_wt:
        s = Shipment.objects.filter(airwaybill_number=awb).update(actual_weight=wt, volumetric_weight=wt, chargeable_weight=wt)
        if s:
            update_shipment_changelog(Shipment.objects.get(airwaybill_number=awb), 'actual_weight',request.user, wt, '')
            count = count+1
            update_shipment_pricing(awb, revision=False)
        else:
            shipment_not_found.append(int(awb))
    return render_to_response("service_centre/shipment_update.html",{'warnings':shipment_not_found,'count':count},
                                   context_instance=RequestContext(request))
  return render_to_response("service_centre/shipment_update.html",
                                   context_instance=RequestContext(request))


@developers_only
def shipment_lbh_update(request):
  if request.method == 'POST':
    ship_file = request.FILES['ship_file']
    content = ship_file.read()
    wb = xlrd.open_workbook(file_contents=content)
    sheetnames = wb.sheet_names()
    sh = wb.sheet_by_name(sheetnames[0])
    awbn = sh.col_values(0)[1:]
    weight= sh.col_values(1)[1:]
    length = sh.col_values(2)[1:]
    breadth = sh.col_values(3)[1:]
    height = sh.col_values(4)[1:]
    awb_wt = zip(awbn, weight,length,breadth,height)
    shipment_not_found = []
    count =0
    for awb, wt, le, bre, hei in awb_wt:
      s = Shipment.objects.filter(airwaybill_number=awb)\
                .update(actual_weight=wt, length=le, breadth=bre, height=hei, volumetric_weight=0)
      if s:
        count = count+1
        update_shipment_pricing(awb, revision=False)
        update_shipment_changelog(Shipment.objects.get(airwaybill_number=awb), 'length', request.user, le, '')
        update_shipment_changelog(Shipment.objects.get(airwaybill_number=awb), 'breadth', request.user, bre, '')
        update_shipment_changelog(Shipment.objects.get(airwaybill_number=awb), 'height', request.user, hei, '')
      else:
        shipment_not_found.append(int(awb))
    return render_to_response("service_centre/shipment_update.html",{'warnings':shipment_not_found,'count':count},
                                   context_instance=RequestContext(request))
  return render_to_response("service_centre/shipment_update.html",
                                   context_instance=RequestContext(request))

def redirection(request):
    if request.method == 'GET':
        reason_code = ShipmentStatusMaster.objects.filter(code__in=[207, 230])
        service_centre = ServiceCenter.objects.all()
        return render_to_response('service_centre/redirection.html',
            {'reason_code':reason_code, 'service_centre':service_centre},
            context_instance = RequestContext(request))

@csrf_exempt
def download_connection(request):
   if request.method == 'POST':
       data=[]
       conn_id = request.POST['connection_id']
       connection = Connection.objects.get(id=conn_id)
       bags = connection.bags.all()
       for b in bags:
            ships=b.shipments.all()
            for s in ships:
              u=(str(b.bag_number),s.airwaybill_number,s.item_description,s.consignee,s.declared_value)
              data.append(u)
       header=("Bag No","AWB","Item Description","Consignee","Declared Value")
       report= ReportGenerator("connection_{0}.xlsx".format(conn_id))
       report.write_header(header)
       path=report.write_body(data)
       path = settings.ROOT_URL + 'static/uploads/reports/' +path
       return HttpResponse(path)

import csv
from os import getcwd
from itertools import islice
import simplejson as sj

def read_csv(filename):
    #pathname = getcwd()+'/'+filename
    with open(filename, 'r') as csff:
        csfff = csv.reader(csff)
        for line in csfff:
            yield line

def make_class(filename, object_type=None):
    params = read_csv(filename)
    data = [entry for entry in islice(params, 1, None)]
#    update or create class code goes here.
    return sj.dumps(data)

def get_csv_file(request):
	return render_to_response("service_centre/upload-csv.html",
					context_instance=RequestContext(request))

def get_csv(request):
    HttpResp = None
    #if request.GET:
    upload_file_1 = request.FILES['upload_successes']
    upload_file_2 = request.FILES['upload_failures']
    file_contents_1 = upload_file_1.read()
    file_contents_2 = upload_file_2.read()
    if file_contents_1 and file_contents_2:
                #data = make_class(upload_file)
                #if data:
        HttpResp='Upload succeeded'
    else:
         HttpResp='Upload failed'
    return HttpResponse(HttpResp)



def auto_upload_file_updated(request):
    if request.POST:
         #resp="file uploaded"
        upload_file = request.FILES['upload_file']
        file_contents = upload_file.read()  
        if file_contents:
            import_wb = xlrd.open_workbook(file_contents=file_contents)
            import_sheet = import_wb.sheet_by_index(0)
            for a in range(1, import_sheet.nrows):
               #for field in [3,4,5,8,9,10,11,13,17,19,20,21]:
                 resp = import_sheet.nrows
                 resp = import_sheet.ncols
                 for field in range(resp):
                    field_data = import_sheet.cell_value(rowx=a, colx=field)
                    resp = field_data
                    #awb = validate_awb(field_data,shipper,)
    else:
         resp="file upload failed"  
    return HttpResponse(resp)
