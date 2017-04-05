import StringIO
import re
import os
import string, random
import xlrd
import xlwt
import csv

from datetime import timedelta, datetime
from django.utils import *
from utils import *
from django.db import connections

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import get_model
from django.core.mail import send_mail
from django.core.files.move import file_move_safe
from models import *
from xlsxwriter.workbook import Workbook
from privateviews.decorators import login_not_required
from service_centre.models import *
from location.models import ServiceCenter
from pickup.models import PickupRegistration
from track_me.models import RTOInstructionUpdate
from delivery.models import get_bag_history
from track_me.forms import GenericQueryForm, CallCentreEntryForm
from reports.report_api import ReportGenerator
from collections import OrderedDict

now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")


def shipment_historyinfo(shipment):
            upd_time = shipment.added_on
            monthdir = upd_time.strftime("%Y_%m")

            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            history = shipment_history.objects.filter(shipment=shipment).order_by("-id")
            if not history:
                 return HttpResponse("History for this shipment does not exists")
            history_latest=history.latest('updated_on')
            history_latest_inst=shipment_history.objects.filter(shipment=shipment, status__in=[11,16]).order_by("-updated_on")
            status_update=StatusUpdate.objects.filter(shipment=shipment).order_by("-id")
            if status_update:
                status_update=status_update[0]
            else:
                status_update=None

            try:
                complaint_status = Complaints.objects.get(shipment=shipment)
            except:
                complaint_status=None
        #else:
            history = None
            history_latest = None
            history_latest_inst = None

            status_update=None

            try:
                complaint_status = Complaints.objects.get(shipment=shipment)
            except:
                complaint_status=None


@csrf_exempt
def index(request):
    if request.GET:
        q = Q()
        awb = request.GET['awb']
        order = request.GET['order']
        reverse_pickup = True if request.GET.get('reverse_shipment') else False
        if awb =="" and order == "":
           return render_to_response("track_me/trackme.html",
                               context_instance=RequestContext(request))
        if request.user.employeemaster.user_type == "Customer":
               customer = Customer.objects.get(code=request.user.employeemaster.lastname)
               q = q & Q(pickup__customer_code=customer)
        if awb:
               q = q & Q(airwaybill_number = awb)
               #if isinstance(awb,int):
               #   q = q & Q(airwaybill_number = awb)
               #else:
               #   return HttpResponse("Incorrect Airwaybill Number")
        if not awb:
               q = q & Q(order_number=order)

        try:
            if reverse_pickup:
                        shipment = ReverseShipment.objects.get(airwaybill_number=awb)
            else:
                    shipment = Shipment.objects.filter(q).latest('id')
        except (Shipment.DoesNotExist, ReverseShipment.DoesNotExist):
                s = "Shipment Does Not Exist %s - %s " %(reverse_pickup,awb)
                return HttpResponse(s)

        if not reverse_pickup:
            upd_time = shipment.added_on
            monthdir = upd_time.strftime("%Y_%m")

            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            history = shipment_history.objects.filter(shipment=shipment).order_by("-updated_on")
            if not history:
                 return HttpResponse("History for this shipment does not exists")
            history_latest=history.latest('updated_on')
            history_latest_inst=shipment_history.objects.filter(shipment=shipment, status__in=[11,16]).order_by("-updated_on")
            status_update=StatusUpdate.objects.filter(shipment=shipment).order_by("-id")
            if status_update:
                status_update=status_update[0]
            else:
                status_update="not None"


            try:
                complaint_status = Complaints.objects.get(shipment=shipment)
            except:
                complaint_status=None
        else:
            rev_status = shipment.reason_code if shipment.reason_code else "Staff out for pickup"
            history = None
            history_latest = None
            history_latest_inst = None

            status_update=None

            try:
                complaint_status = Complaints.objects.get(shipment=shipment)
            except:
                complaint_status=None
        return render_to_response("track_me/trackme.html",locals(),
                               context_instance=RequestContext(request))

        return render_to_response("track_me/trackme.html",
                                  {'shipment':shipment,
                                   'history':history,
                                   'history_latest':history_latest,
                                   'history_latest_inst':history_latest_inst,
                                   'status_update':status_update,
                                   'complaint_status':complaint_status},
                               context_instance=RequestContext(request))

@csrf_exempt
def shipper_consignee(request):
    if request.GET:
        awb = request.GET['awb']
        order = request.GET['order']
        if awb =="" and order == "":
            return render_to_response("track_me/shipperconsignee.html",
                context_instance=RequestContext(request))

        if awb:
            shipment = Shipment.objects.get(airwaybill_number=awb)
        if order:
            shipment = Shipment.objects.filter(order_number=order).latest('id')
        upd_time = shipment.added_on
        monthdir = upd_time.strftime("%Y_%m")
        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
        history = shipment_history.objects.filter(shipment=shipment)
        history_latest=history.latest('updated_on')
        history_latest_inst=shipment_history.objects.filter(shipment=shipment, status__in=[11,16]).order_by("-updated_on")
        try:
            status_update=StatusUpdate.objects.get(shipment=shipment)
        except:
            status_update=""
        return render_to_response("track_me/shipperconsignee.html",
                                  {'shipment':shipment,
                                   'history':history,
                                   'history_latest':history_latest,
                                   'history_latest_inst':history_latest_inst,
                                   'status_update':status_update},
                               context_instance=RequestContext(request))

@csrf_exempt
def pickup_package(request):
    if request.GET:
        awb = request.GET['awb']
        order = request.GET['order']
        if awb =="" and order == "":
            return render_to_response("track_me/pickuppackageinfo.html",
                               context_instance=RequestContext(request))

        if awb:
            shipment = Shipment.objects.get(airwaybill_number=awb)
        if order:
            shipment = Shipment.objects.filter(order_number=order).latest('id')
        upd_time = shipment.added_on
        monthdir = upd_time.strftime("%Y_%m")
        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
        history = shipment_history.objects.filter(shipment=shipment)
        history_latest=history.latest('updated_on')
        history_latest_inst=shipment_history.objects.filter(shipment=shipment, status__in=[11,16]).order_by("-updated_on")
        try:
          status_update=StatusUpdate.objects.get(shipment=shipment)
        except:
          status_update=""
        return render_to_response("track_me/pickuppackageinfo.html",
                                  {'shipment':shipment,
                                   'history':history,
                                   'history_latest':history_latest,
                                   'history_latest_inst':history_latest_inst,
                                   'status_update':status_update},
                               context_instance=RequestContext(request))

@csrf_exempt
def comments(request):
    before = now - datetime.timedelta(days=0)
    if request.GET:
        awb = request.GET['awb']
        order = request.GET['order']
        if awb =="" and order == "":
            if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
                  instruction = BatchInstruction.objects.using("local_ecomm").filter(added_on__range=(before, now), employee_code__service_centre=request.user.employeemaster.service_centre).order_by('-id')
            else:
                   instruction = BatchInstruction.objects.using("local_ecomm").filter(added_on__range=(before, now)).order_by('-id')

            return render_to_response("track_me/commentsdetailentry.html",
                                      {'instruction':instruction},
                               context_instance=RequestContext(request))

        if awb:
            shipment = Shipment.objects.get(airwaybill_number=awb)
        if order:
            shipment = Shipment.objects.using("local_ecomm").filter(order_number=order).latest('id')
        upd_time = shipment.added_on
        monthdir = upd_time.strftime("%Y_%m")
        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
        history = shipment_history.objects.using("local_ecomm").filter(shipment=shipment)
        history_latest=history.latest('updated_on')
        history_latest_inst=shipment_history.objects.using("local_ecomm").filter(shipment=shipment, status__in=[11,16]).order_by("-updated_on")
        try:
          status_update=StatusUpdate.objects.get(shipment=shipment)
        except:
          status_update=""
    if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
        instruction = BatchInstruction.objects.using("local_ecomm").filter(added_on__range=(before, now), employee_code__service_centre=request.user.employeemaster.service_centre).order_by('-id')
    else:
        instruction = BatchInstruction.objects.using("local_ecomm").filter(added_on__range=(before, now)).order_by('-id')

    return render_to_response("track_me/commentsdetailentry.html",
                                 {'shipment':shipment,
                                   'history':history,
                                   'history_latest':history_latest,
                                   'history_latest_inst':history_latest_inst,
                                   'status_update':status_update,
                                   'instruction':instruction},
                               context_instance=RequestContext(request))

@csrf_exempt
def comments_entry(request):
    comment_type = request.POST['type']
    emp_code = request.POST['emp_code']
    emp_code = EmployeeMaster.objects.get(employee_code=emp_code)
    date = request.POST['date']
    time = request.POST['time']
    comments = request.POST['comments']
    instruction = BatchInstruction.objects.create(employee_code=emp_code)
    error_awbs = []
    # if it's a call centre comment
    if int(comment_type) == 2:
        awb = request.POST['awb'].strip()
        airwaybills = awb.split("\r\n")
        for awb in airwaybills:
            try:
                shipment = Shipment.objects.get(airwaybill_number=int(awb))
                cc_comment = CallCentreComment.objects.create(
                    employee_code=emp_code,
                    date=date, shipments=shipment,
                    comments=comments)
                upd_time = shipment.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model(
                    'service_centre', 'ShipmentHistory_%s' % (monthdir))
                status = 21
                shipment_history.objects.create(
                    shipment=shipment, status=status, 
                    employee_code=request.user.employeemaster, 
                    current_sc=request.user.employeemaster.service_centre, 
                    remarks=comments)
            except Shipment.DoesNotExist: 
                error_awbs.append(awb)
        return HttpResponseRedirect(
            '/track_me/comments/?awb=%d&order=%s' % (
                shipment.airwaybill_number, shipment.order_number))
    #-------------------------------
    if int(comment_type) == 0:
        altinstruction = AlternateInstruction.objects.create(
                instruction_type=comment_type, employee_code=emp_code, 
                date=date, time=time, comments=comments
        )
    awb = request.POST['awb'].strip()

    a = awb.split('\r\n')
    for awb in a:
      if awb:
         shipment = Shipment.objects.filter(airwaybill_number=int(awb))
         if shipment.exists():
             shipment = shipment[0]
         else:
            return HttpResponse('Airaybill number does not exist')
         if int(comment_type) == 0:
             altinstruction.shipments.add(shipment)

         biawb = BatchInstructionAWB.objects.create(
             batch_instruction=instruction, shipments=shipment)
         InstructionAWB.objects.create(
             batch_instruction=biawb, instruction = comments)

         upd_time = shipment.added_on
         monthdir = upd_time.strftime("%Y_%m")
         shipment_history = get_model(
                 'service_centre', 'ShipmentHistory_%s' % (monthdir))

         if int(comment_type) == 1:
              status = 16
         else:
             status = 11
         shipment_history.objects.create(
             shipment=shipment, status=status, 
             employee_code=request.user.employeemaster, 
             current_sc=request.user.employeemaster.service_centre, 
             remarks=comments)
    return HttpResponseRedirect(
            '/track_me/comments/?awb=%d&order=%s' % (
                shipment.airwaybill_number, shipment.order_number))


def multiple_airwaybill(request):
    if request.POST:
        book = xlwt.Workbook(encoding='utf8')
        default_style = xlwt.Style.default_style
        datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
        date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
        header_style = xlwt.XFStyle()
        category_style = xlwt.XFStyle()
        status_style = xlwt.XFStyle()
        rto_style=xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True

        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = 5
        #
        pattern1 = xlwt.Pattern()
        pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern1.pattern_fore_colour = 0x0A
   #
        pattern2 = xlwt.Pattern()
        pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern2.pattern_fore_colour = 0x0F
#
        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        header_style.pattern = pattern
        status_style.pattern = pattern1
        rto_style.pattern=pattern2
        header_style.font = font
        category_style.font = font
        header_style.borders=borders
        default_style.borders=borders

        shipments = []
        shipment_info = {}
        awba=request.POST['multipleawb']
        a = awba.split('\r\n')
        b = ""
        download_list = []
        if not awba:
            order = request.POST['multipleord']
            b = order.split('\r\n')
        if a:
          for awbq in a:
             try:
               if request.user.employeemaster.user_type == "Customer":
                  customer = Customer.objects.get(code=request.user.employeemaster.lastname)
                  shipment = Shipment.objects.get(airwaybill_number=int(awbq), pickup__customer_code=customer)
               else:
                  shipment=Shipment.objects.get(airwaybill_number=int(awbq))
               shipments.append(shipment.airwaybill_number)
             except:
              pass
          for awb in shipments:
            if awb:
                remarks = ""
                reason_code = ""
                reason_code_desc = ""
                updated_on = ""
                upd_time = ""
                shipment = Shipment.objects.get(airwaybill_number=int(awb))
                upd_time = shipment.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))

                try:
                    history = shipment_history.objects.filter(shipment=shipment).exclude(status__in=[11,12,16, 20]).latest('updated_on')
                except:
                    history = ""
                try:
                    expected_dod = shipment.expected_dod.strftime("%d-%m-%Y")
                except:
                    expected_dod = ""

                if history:
                   shipment_info[shipment] = history
                   remarks = history.remarks
                   if history.reason_code:
                       reason_code = history.reason_code.code
                       reason_code_desc = history.reason_code.code_description
                   updated_on = history.updated_on.strftime("%d-%m-%Y")
                   upd_time = history.updated_on.time()

                if shipment.statusupdate_set.all():
                   su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                   received_by = su.recieved_by
                   time  = su.time.strftime("%H:%m")
                   date  = su.date.strftime("%d-%m-%Y")
                else:
                   received_by = ""
                   time  = ""
                   date  = ""
                bags = list(shipment.bags_set.all())
                bag_num = ""
                if bags:
                     bags = bags[-1]
                     bag_num = bags.bag_number

                if history.status > 9:
                    val = history.status
                else:
                    val = shipment.status

                if str(val) == '0':
                   if history.remarks:
                         val ="Bagging Completed"
                   else:
                                         val="Shipment Uploaded"
                   if reason_code == 333:
                          val = "Lost"
                elif str(val)== '1':
                                           val='Pickup Complete / Inscan'
                elif str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                elif str(val)== '3':
                                   val='Bagging completed'
                elif str(val)== '4':
                                    val='Shipment at HUB'
                elif str(val)== '5':
                                       val='Bagging completed at Hub'
                elif str(val)== '6':
                                      val='Shipment at Delivery Centre'
                elif str(val)== '7':
                                     val='Outscan'
                elif str(val)== '8':
                                 val='Undelivered'
                elif str(val)==  '9':
                                  val='Delivered / Closed'
                elif str(val)== '11':
                                   val='Alternate Instruction given'
                elif str(val)==  '12':
                                      val='Complaint Registered'
                elif str(val)== '13':
                                   val='Assigned to Run Code'
                elif str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                elif str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                elif str(val)== '20':
                                 val='Undelivered'
                elif str(val) == "21":
                   #val="Comments/Remarks"
                    if shipment.reason_code: 
                       val = shipment.reason_code.code_description
                    else:
                       val =""
                elif str(val)== '26':
                    if history:
                        val=history.remarks
                    else:
                        val='Connected from Hub'
                elif str(val)== '27':
                    if history:
                        val=history.remarks
                    else:
                        val='Connected from SC'
                if (shipment.reason_code_id == 5 or shipment.return_shipment==2):
                                  val = "Returned"
                if history:
                    current_sc = history.current_sc
                else:
                    current_sc = shipment.current_sc
                #if shipment.ref_airwaybill_number:
                     #sref = Shipment.objects.filter(airwaybill_number = shipment.ref_airwaybill_number).values_list('id','status','rts_status','added_on')
                     #if sref:
                          #monthdir = sref[0][3].strftime("%Y_%m")
                          #shipment_history_rts = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                          #rts_history = shipment_history_rts.objects.filter(shipment=sref[0][0]).latest('updated_on')
                          #current_sc = rts_history.current_sc
                u = (shipment.airwaybill_number, shipment.order_number,shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value,  shipment.pickup.service_centre, shipment.service_centre,shipment.shipper, shipment.consignee, shipment.added_on.strftime("%d-%m-%Y"), val, expected_dod, str(updated_on)+" | "+str(upd_time), remarks, reason_code, reason_code_desc, received_by, date, time, shipment.current_sc, bag_num,shipment.rts_status,shipment.ref_airwaybill_number)
                download_list.append(u)
             #   except:
            #          return HttpResponse(shipment.status)
        if b:
            reason_code = ""
            reason_code_desc = ""
            for ord in b:
                if ord:
                    try:
                      shipment = Shipment.objects.filter(order_number=int(ord)).latest('id')
                    except:
                      continue
                    shipments.append(shipment)
                    upd_time = shipment.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    try:
                        history = shipment_history.objects.filter(shipment=shipment).exclude(status__in=[11,12,16, 20]).latest('updated_on')
                    except:
                        history = ""
                    if history:
                       shipment_info[shipment] = history
                       remarks = history.remarks
                       if history.reason_code:
                           reason_code = history.reason_code.code
                           reason_code_desc = history.reason_code.code_description
                       updated_on = history.updated_on.strftime("%d-%m-%Y")
                    else:
                       shipment_info[shipment] = history
                       remarks = ""
                       reason_code = ""
                       reason_code_desc = ""
                       updated_on = ""

                    if shipment.statusupdate_set.all():
                       su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                       received_by = su.recieved_by
                       time  = su.time.strftime("%H:%m")
                       date  = su.date.strftime("%d-%m-%Y")
                    else:
                       received_by = ""
                       date = ""
                       time = ""
                    bags = list(shipment.bags_set.all())
                    bag_num = ""
                    if bags:
                        bags = bags[-1]
                        bag_num = bags.bag_number

                    if shipment.expected_dod:
                          expd = shipment.expected_dod.strftime("%d-%m-%Y")
                    else:
                          expd = ""
                    if shipment.status:
                              val = shipment.status
                              if str(val) == '0':
                                         val="Shipment Uploaded"
                              if str(val)== '1':
                                           val='Pickup Complete / Inscan'
                              if str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                              if str(val)== '3':
                                   val='Bagging completed'
                              if str(val)== '4':
                                    val='Shipment at HUB'
                              if str(val)== '5':
                                       val='Bagging completed at Hub'
                              if str(val)== '6':
                                      val='Shipment at Delivery Centre'
                              if str(val)== '7':
                                     val='Outscan'
                              if str(val)== '8':
                                 val='Undelivered'
                              if str(val)==  '9':
                                  val='Delivered / Closed'
                              if str(val)== '11':
                                   val='Alternate Instruction given'
                              if str(val)==  '12':
                                      val='Complaint Registered'
                              if str(val)== '13':
                                   val='Assigned to Run Code'
                              if str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                              if str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                              if str(val)== '20':
                                 val='Undelivered'

                    if (shipment.reason_code_id == 5 or shipment.return_shipment==2):
                                  val = "Returned"

                    current_sc = history.current_sc
                    if shipment.ref_airwaybill_number:
                        sref = Shipment.objects.filter(airwaybill_number = shipment.ref_airwaybill_number).values_list('id','status','rts_status','added_on')
                        if sref:
                                monthdir = sref[0][3].strftime("%Y_%m")
                                shipment_history_rts = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                                rts_history = shipment_history_rts.objects.filter(shipment=sref[0][0]).latest('updated_on')
                                #current_sc = shipment.current_sc

                    u = (shipment.airwaybill_number, shipment.order_number, shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value,  shipment.pickup.service_centre, shipment.service_centre,shipment.shipper, shipment.consignee, shipment.added_on.strftime("%d-%m-%Y"), val, expd, str(updated_on)+" | "+str(history.updated_on.time()), remarks, reason_code, reason_code_desc, received_by, date, time, shipment.current_sc, bag_num,shipment.rts_status,shipment.ref_airwaybill_number)
                    download_list.append(u)


        #return HttpResponse("%s" % request.POST.get("download"))
        if request.POST.get("download"):
            sheet = book.add_sheet('multiple query')
            distinct_list = download_list
            sheet.write(0, 2, "Multiple AWB", style=header_style)
            for a in range(14):
                sheet.col(a).width = 6000
            sheet.col(8).width = 10000
            sheet.col(9).width = 6000
            sheet.write(3, 0, "Air Waybill No", style=header_style)
            sheet.write(3, 1, "Order No", style=header_style)
            sheet.write(3, 2, "Weight", style=header_style)
            sheet.write(3, 3, "Vol Weight", style=header_style)
            sheet.write(3, 4, "COD Amount", style=header_style)
            sheet.write(3, 5, "Declared Value", style=header_style)
            sheet.write(3, 6, "Origin", style=header_style)
            sheet.write(3, 7, "Destination", style=header_style)
            sheet.write(3, 8, "Shipper", style=header_style)
            sheet.write(3, 9, "Consignee", style=header_style)
            sheet.write(3, 10, "P/U Date", style=header_style)
            sheet.write(3, 11, "Status", style=header_style)
            sheet.write(3, 12, "Expected Date", style=header_style)
            sheet.write(3, 13, "Updated Date", style=header_style)
            sheet.write(3, 14, "Remarks", style=header_style)
            sheet.write(3, 15, "Reason Code", style=header_style)
            sheet.write(3, 16, "Reason", style=header_style)
            sheet.write(3, 17, "Received by", style=header_style)
            sheet.write(3, 18, "Delivery date", style=header_style)
            sheet.write(3, 19, "Delivery time", style=header_style)
            sheet.write(3, 20, "Current SC", style=header_style)
            sheet.write(3, 21, "Bag Number", style=header_style)
            style = datetime_style
            counter = 1

            for row, rowdata in enumerate(distinct_list, start=4):
                    #sheet.write(row, 0, str(counter), style=style)
                    #counter=counter+1
                    for col, val in enumerate(rowdata, start=0):
                    #    if col == 9:
                    #        if str(val)== '0':
                    #            val="Shipment Uploaded"
                    #        if str(val)== '1':
                    #            val='Pickup Complete / Inscan'
                    #        if str(val)== '2':
                    #            val='Inscan completion / Ready bor Bagging'
                    #        if str(val)== '3':
                    #            val='Bagging completed'
                    #        if str(val)== '4':
                    #            val='Shipment at HUB'
                    #        if str(val)== '5':
                    #            val='Bagging Completed at HUB'
                    #        if str(val)== '6':
                    #            val='Shipmentat Delivery Centre'
                    #        if str(val)== '7':
                    #            val='Outscan'
                    #        if str(val)== '8':
                    #            val='Undelivered'
                    #        if str(val)==  '9':
                    #            val='Delivered / Closed'
                            #sheet.write(row, col, str(val), style=style)
                        try:
                          sheet.write(row, col, str(val), style=style)
                        except:
                          pass
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=multiple_airway_details.xls'
            book.save(response)
            return response

        return render_to_response("track_me/multipleairwaybill.html",
                                  #{'shipments':shipments, 'shipment_info':shipment_info},
                                  {'shipments':download_list},
                               context_instance=RequestContext(request))
    else:
      return render_to_response("track_me/multipleairwaybill.html",
                               context_instance=RequestContext(request))


#for normal site login
@login_not_required
@csrf_exempt
def multipleawb_open(request):
	if request.method == 'GET':
             awb = request.GET.get('awb')
             order = request.GET.get('order')
             app = request.GET.get('app')  
             if not awb and not order:
                     return render_to_response("track_me/multipleawb_open.html",
                               context_instance=RequestContext(request))
             a = ""
             b = ""
             download_list = []
             if awb:
               	  a = awb.split('-')
                  for ship in a:
                    #if ship.isdigit():
                    try:
                          shipments = Shipment.objects.get(airwaybill_number=int(ship))
                    except Shipment.DoesNotExist:
                         if not app:
                            return HttpResponse("Air waybill not found, please recheck")
                         else:
                              response_dict = {} 
                              response_dict['awb_status']="Invalid"
                              return HttpResponse(simplejson.dumps(response_dict),content_type="application/json") 

                     #  if not download_list.get(shipments):
                    download_list.append(shipments.airwaybill_number)
             if order:
                     b = order.split('-')
                     for ship in b:
                       try:
                         shipments = Shipment.objects.filter(order_number=ship).latest('id')
                       except Shipment.DoesNotExist:
                         return HttpResponse("Incorrect Order/Reference Number")
               #          if not download_list.get(shipments):
                       download_list.append(shipments.airwaybill_number)
          #   return HttpResponse(download_list)
             shipobj_dict = OrderedDict()
             hist_list = []
	     hubname = ''
	     shipobj = ''
             for awb in download_list:
                if awb:
                    shipment = Shipment.objects.get(airwaybill_number=int(awb))
                    return_status = shipment.rts_status
                    failed_status = shipment.rto_status
                    upd_time = shipment.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    tmp_val = ''
                    ship_list = []
                    history = shipment_history.objects.filter(shipment=shipment).order_by('-updated_on')
                    for i,shistory in enumerate(history):
                        if tmp_val != shistory.status and shistory.status < 10:
		  	    if shistory.status == 0 and shipment.status != 0 and (i != (history.count() - 1)):
				continue	
			    if shistory.status == 9 and shipment.status != 9:
				continue
                            val = shistory.status
                            if val == 0 or val == 1:
                                 sc=shipment.pickup.service_centre.city.city_name
                                 #sc =  shipment.original_dest.center_name
                            elif (val ==2)and not shistory.reason_code:
                                 sc = shistory.current_sc.center_name
                                 #sc=shipment.pickup.service_centre.city.city_name
                            elif val == 3 :
                                 org_dest = shistory.current_sc.center_name
                                 if shistory.reason_code:
                                    org_dest = shistory.current_sc.center_name
                                 if re.search('Bag No',shistory.remarks):  
                                    bag_no = shistory.remarks[shistory.remarks.index("(Bag No. ")+8:shistory.remarks.rindex(")")] 
                                    bag_no = bag_no.strip()
                                 
                                    hublist = Bags.objects.filter(bag_number=bag_no).values_list('hub__center_name',flat=True)
                                    if len(hublist) > 0:
                                       hubname = hublist [0]
                                       if hubname is not None:
                                          hubname = hubname.split('-')[0]
                                          if (' ' in hubname) and len(hubname.split(' ')[1]) == 3:
                                               hubname = hubname.split(' ')[0]    
                                 org_dest = org_dest.split('-')[0]
                                 if(' ' in org_dest) and len(org_dest.split(' ')[1]) == 3:
                                       org_dest = org_dest.split(' ')[0]                               
                                 sc = [org_dest,hubname]
			    elif val == 8:
				 undel = ''
				 if shistory.reason_code:
					undel = '(Reason Code : '+str(shistory.reason_code)+')'
				 scenter = shistory.current_sc.center_name.split('-')[0]
                                 if (' ' in scenter) and len(scenter.split(' ')[1]) == 3:
                                      scenter = scenter.split(' ')[0]

				 sc = [scenter,undel]
                            elif (val == 13 or val == 14) and not shistory.reason_code:
                                 sc = shipment.destination_city
                            else:
                                 sc = shistory.current_sc.center_name
                            if val !=3 and val != 8:                                 
                                sc = sc.split('-')[0]                        
                                if (' ' in sc) and len(sc.split(' ')[1]) == 3:
                                    sc = sc.split(' ')[0]
                            updated_on = shistory.updated_on.strftime("%d-%m-%Y")
                            u = (shipment.airwaybill_number, shipment.order_number,sc, val, str(updated_on)+" | "+str(shistory.updated_on.time()),return_status,failed_status,shipment.consignee.title(),shipment.consignee_address1.title(),'Cash On Delivery',"{0:.2f}".format(shipment.collectable_value), shipment.product_type)
                            ship_list.append(u)
                            if val < 10 and shipment.airwaybill_number not in shipobj_dict: 
                                 shipobj_dict[shipment.airwaybill_number] = [val,return_status,failed_status]
                            tmp_val = val
             
                    if len(ship_list) > 0:
                        hist_list.append(ship_list)
             if len(shipobj_dict) > 0:
                 shipobj = ''
                 for key,ship_item in shipobj_dict.iteritems():
                     shipobj += '@'.join(str(x) for x in ship_item)
                     shipobj += '#'
                 shipobj = shipobj[:-1]
             if not app:
                 return render_to_response("track_me/multipleawb_open.html",
                                  {'shipment':hist_list,'shipobj_list':shipobj_dict.values(),'shipobj':shipobj,'r':hubname},
                               context_instance=RequestContext(request))
             else:
                 from reports.freq_reports import get_address
                 response_dict = {}
                 response_dict['awb_status']="Valid"
                 response_dict['status']=shipobj_dict
                 response_dict['hist']=hist_list
                 response_dict['shipment']=shipobj
                 response_dict['hubname']=hubname
                 response_dict['consignee']=shipment.consignee
                 response_dict['address']=get_address(shipment.airwaybill_number)

                 return HttpResponse(simplejson.dumps(response_dict),content_type="application/json") 
        else:
                return render_to_response("track_me/multipleawb_open.html",
                                  {},
                               context_instance=RequestContext(request))


def alternate_instruction(request):
    if request.POST:
          upload_file = request.FILES['upload_file']
          file_contents = upload_file.read()
          file_name = upload_file.name
          a = file_name.split('.')
          extension = a[1]
          upload_file = upload_file.temporary_file_path()
          b = file_name.replace(' ', '')

          newfilename = str(b)
          stra = newfilename.replace("upload",str(extension))
          path_to_save = settings.FILE_UPLOAD_TEMP_DIR+"/%s"%(stra)

          file_move_safe(upload_file, path_to_save, allow_overwrite=True)
          bi = BatchInstruction.objects.create(file_name = file_name, file_path = "/uploads/"+stra, employee_code=request.user.employeemaster)


          if file_contents:
            import_wb = xlrd.open_workbook(file_contents=file_contents)
            import_sheet = import_wb.sheet_by_index(0)
            for rx in range(1, import_sheet.nrows):
                airwaybill_num = import_sheet.cell_value(rowx=rx, colx=0)
                instruction = import_sheet.cell_value(rowx=rx, colx=1)
                shipment = Shipment.objects.get(airwaybill_number=int(airwaybill_num))
                upd_time = shipment.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
               # history = shipment_history.objects.filter(shipment=shipment)
               # history_latest=history.latest('updated_on')
               # history_latest.id=None
               # history_latest.employee_code=request.user.employeemaster
               # history_latest.remarks=instruction
               # history_latest.status=11
               # history_latest.save()
                shipment_history.objects.create(shipment=shipment, status=11, employee_code = request.user.employeemaster, current_sc = request.user.employeemaster.service_centre, remarks=instruction)
                biawb = BatchInstructionAWB.objects.create(batch_instruction=bi, shipments=shipment)

                InstructionAWB.objects.create(batch_instruction=biawb, instruction = instruction)

          return render_to_response("track_me/commentsdetailentry.html",
                              {'msg':"Instruction Successfully Updated"},
                               context_instance=RequestContext(request))



#          file_job = file_jobs(file_name=file_name, file_path=save_path)
#          file_job.save()
#          sbase_report = Ship_data_report.objects.get(id=id)
#          sbase_report.file_path.add(file_job)


def queryset_iterator(queryset, chunksize=1000):
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row


def generic_query(request):
    service_centre = ServiceCenter.objects.all()
    zone = Zone.objects.all()
    city = City.objects.all()
    client=Customer.objects.all()
    shipment_info={}
    download_list = []
    q=Q()


    if request.POST:
        file_name = "/Generic_Query_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s"))
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
        sheet.write(3, 4, "COD Amount", header_format)
        sheet.write(3, 5, "Declared Value", header_format)
        sheet.write(3, 6, "Origin", header_format)
        sheet.write(3, 7, "Destination", header_format)
        sheet.write(3, 8, "Vendor", header_format)
        sheet.write(3, 9, "Shipper", header_format)
        sheet.write(3, 10, "Consignee", header_format)
        sheet.write(3, 11, "Consignee Address", header_format)
        sheet.write(3, 12, "Contact Number", header_format)
        sheet.write(3, 13, "P/U Date", header_format)
        sheet.write(3, 14, "Status", header_format)
        sheet.write(3, 15, "Expected Date", header_format)
        sheet.write(3, 16, "Updated Date", header_format)
        sheet.write(3, 17, "Remarks", header_format)
        sheet.write(3, 18, "Reason Code", header_format)
        sheet.write(3, 19, "Reason", header_format)
        sheet.write(3, 20, "Received by", header_format)
        sheet.write(3, 21, "Del Date", header_format)
        sheet.write(3, 22, "Del Time", header_format)
        sheet.write(3, 23, "New Air Waybill (RTS)", header_format)
        sheet.write(3, 24, "Return Status", header_format)
        sheet.write(3, 25, "Updated on", header_format)
        sheet.write(3, 26, "PRUD_DATE", header_format)
        sheet.write(3, 27, "FRST_ATMPTD_UDSTATUS", header_format)
        sheet.write(3, 28, "FRST_ATMPT_DATE", header_format)
        row = 3
        origin = request.POST['origin']
        if origin:
            servicecentre=ServiceCenter.objects.get(id=origin)
            q = q & Q(pickup__service_centre=servicecentre)

        client_code = request.POST['client_code']
        if client_code:
            q = q & Q(shipper=client_code)

        consignee = request.POST['consignee']

        if consignee:
            q = q & Q(consignee__icontains=consignee)

        destination = request.POST['destination']
        if destination:
            q = q & Q(original_dest=destination)
        zone = request.POST['zone']
        if zone:
            q = q & Q(original_dest__city__zone=zone)
        city = request.POST['city']
        if city:
            q = q & Q(original_dest__city=city)
    #    reverse_pickup = request.POST['reverse_pickup']
    #    if reverse_pickup:
    #        q = q & Q(reverse_pickup=1)

        pickup_from = request.POST['pickup_from']
        pickup_to = request.POST['pickup_to']
        if not pickup_to:
              pickup_to="2050-12-12"
        else:
              t = datetime.datetime.strptime(pickup_to, "%Y-%m-%d") + datetime.timedelta(days=1)
              pickup_to = next_date = t.strftime("%Y-%m-%d")

        if (pickup_from and pickup_to):
            q = q & Q(added_on__range=(pickup_from,pickup_to))

        product = request.POST['product']
        if product:
          if (product == "cod" or product ==" ppd"):
            q = q & Q(product_type=(product))
          elif (product =="rts"):
            q = q & Q(rts_status=1)
          elif (product =="sdl"):
             pincode = Pincode.objects.filter(sdl = 1)
             pin = [a.pincode for a in pincode]
             q = q &Q(pincode__in=pin)
          elif (product == "rto"):
             q = q & Q(rto_status=1)
        delivered_status=request.POST['delivered_status']
        if delivered_status:
        	if delivered_status=="9":
                     q = q & Q(status=9)
                else:
                     q = q & (~Q(status = 9))
        shipments = Shipment.objects.filter(q).select_related('original_dest__center_name','service_centre__center_name','pickup','shipper__name').only('pickup__subcustomer_code__name','pickup__service_centre__center_name','reverse_pickup','airwaybill_number','order_number','product_type','shipper__name','consignee','consignee_address1','consignee_address2','consignee_address3','actual_weight','volumetric_weight','pickup__service_centre__center_name','original_dest__center_name','service_centre__center_name','mobile','added_on','status','expected_dod','return_shipment','rto_status','rts_status','ref_airwaybill_number','collectable_value','declared_value')

        if 1==1:
            for a in shipments.iterator():
		    print a.airwaybill_number
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
              #         hist_upd_time = history[2].time()
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
                          first_rc = first_su.reason_code
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
                    if shipment:
                              val = get_internal_shipment_status(shipment.status)
                    if shipment.status in [3,5]:
                            st = hist1.filter(status__in=[3,5]).order_by('-id')[0]
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
                       u = [shipment.airwaybill_number, shipment.order_number, shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value, pikup.service_centre, sc, vendor, shipment.shipper, shipment.consignee, shipment.consignee_address1+shipment.consignee_address2+shipment.consignee_address3 ,shipment.mobile, shipment.added_on.strftime("%d-%m-%Y"), val, shipment.expected_dod, str(updated_on)+" | "+str(hist_upd_time), remarks, reason_code, reason_code_desc, received_by, date, time, shipment.ref_airwaybill_number, rts_val, rts_updated_on, shipment.rts_status]
                    else:
                       u = [shipment.airwaybill_number, shipment.order_number, shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value, pikup.service_centre, sc, vendor, shipment.shipper, shipment.consignee, shipment.consignee_address1+shipment.consignee_address2+shipment.consignee_address3, shipment.mobile, shipment.added_on.strftime("%d-%m-%Y"), val, shipment.expected_dod, str(updated_on)+" | "+str(hist_upd_time), remarks, reason_code, reason_code_desc, received_by, date, time, "","","",shipment.rts_status]
                    row = row + 1
                    style = plain_format
                    if shipment.rto_status == 1:
                            style = rto_format
                    if shipment.rts_status == 1:
                            style = rts_format
                    if shipment.rtoinstructionupdate_set.exists():
                        remark = shipment.rtoinstructionupdate_set.all()[0].alternateinstruction.comments
                        u[17] = remark
                    for col, val in enumerate(u, start=0):
                         if col <> 29:
                              try:
                                sheet.write(row, col, str(val), style)
                              except:
                                pass
            workbook.close()
        if request.POST['submit'] == "Download":
                return HttpResponseRedirect("/static/uploads/%s"%(file_name))
        else:
            return render_to_response("track_me/genericquery_rev.html",
                                  {'service_centre':service_centre,
                                   'client':client,
                                   'shipments':shipments,
                                   'shipment_info':download_list},
                               context_instance=RequestContext(request))
    else:
      #  file_name = "/Generic_Query_%s.xlsx"%(now.strftime("%d%m%Y"))
      #  file_path = "http://eepl.ecomexpress.in/static/uploads%s"%(file_name)
        file_path = ''
        return render_to_response("track_me/genericquery.html",
                                  {'service_centre':service_centre,
                                   'zone':zone,
                                   'city':city,
                                   'client':client,
                                   'file_path':file_path },
                               context_instance=RequestContext(request))


def generic_query_v2(request):
    if request.method == 'GET':
        form = GenericQueryForm()
        return render_to_response("track_me/genericquery_v2.html",
                {'form': form}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        form = GenericQueryForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            origin = cleaned_data.get('origin')
            shipper = cleaned_data.get('shipper')
            zone = cleaned_data.get('zone')
            city = cleaned_data.get('city')
            destination = cleaned_data.get('destination')
            pickup_date_from = cleaned_data.get('pickup_date_from')
            pickup_date_to = cleaned_data.get('pickup_date_to')
            product_type = cleaned_data.get('product_type')
            status = cleaned_data.get('status')
            q = Q()
            if origin:
                q = q & Q(origin=origin)
            if shipper:
                q = q & Q(customer=shipper)
            if destination:
                q = q & Q(destination=destination)
            if product_type:
                q = q & Q(product_type=product_type)
            if status:
                if str(status) == str(8):
                    q = q & Q(status="'Undelivered'")
                elif str(status) == str(9):
                    q = q & Q(status="'Delivered / Closed'")
                elif str(status) == str(10):
                    q = q & Q(status="'Returned'")
            year_month = pickup_date_from.strftime('%Y_%m')
            gq = get_model('reports', 'GenericQuery_%s'%(year_month))
            pickup_date_from = pickup_date_from.strftime('%Y-%m-%d 00:00:00')
            pickup_date_to = pickup_date_to.strftime('%Y-%m-%d 23:59:59')
            objects = gq.objects.filter(q).\
                        values_list('airwaybill_number', 'order_number', 'product_type__product_name',
                        'weight', 'vol_weight', 'cod_amount', 'declared_value', 'origin__center_name',
                        'destination__center_name','customer__name',
                        'consignee', 'contact', 'pickup_date', 'status', 'expected_date', 'updated_date',
                        'remarks', 'reason_code', 'reason', 'received_by', 'delivery_date', 'delivery_time',
                        'ref_airwaybill_number', 'return_status', 'return_updated_on', 'rts_status', 'rto_status',
                        'prud_date', 'first_attempt_status', 'first_attempt_date')

            header = """ select 'Airwaybill Number', 'Order Number', 'Product Type',
                        'Weight', 'Vol Weight', 'COD Amount', 'Declared Value', 'Origin',
                        'Destination','Customer', 'Consignee', 'Contact', 'Pickup Date', 
                        'Status', 'Expected Date', 'Updated Date', 'Remarks', 'Reason_Code', 
                        'Reason', 'Received by', 'Delivery Date', 'Delivery Time',
                        'Ref Airwaybill number', 'Return Status', 'Return Updated on', 
                        'Rts Status', 'Rto Status', 'Prud Date', 'First Attempt Status', 'First_Attempt_Date' union """

            cursor = connections['local_ecomm'].cursor()
            query1 = str(objects.query)
            now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') 
            csv_file_path = '/tmp/generic_query_{year_month}_{now}.csv'.format(year_month=year_month, now=now)
            if q:
                query = header + query1 + """ and `reports_genericquery_{year_month}`.`pickup_date` BETWEEN "{from_date}" and "{to_date}" 
                    INTO OUTFILE '{csv_file_path}'
                    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
                    LINES TERMINATED BY '\n'
                    """.format(year_month=year_month, from_date=pickup_date_from, to_date=pickup_date_to, csv_file_path=csv_file_path)
            else:
                query = header + query1 + """ WHERE `reports_genericquery_{year_month}`.`pickup_date` BETWEEN "{from_date}" and "{to_date}" 
                    INTO OUTFILE '{csv_file_path}'
                    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
                    LINES TERMINATED BY '\n'
                    """.format(year_month=year_month, from_date=pickup_date_from, to_date=pickup_date_to, csv_file_path=csv_file_path)
            
            cursor.execute(query)
            #cursor.fetchall()
            base_path = '/home/web/ecomm.prtouch.com/ecomexpress'
            zip_file_name = '/static/uploads/reports/generic/generic_query_2014_05_{now}.zip'.format(now=now)
            zip_file_path = base_path + zip_file_name
            os.system("zip -j {zip_file_path} {csv_file_path}".format(zip_file_path=zip_file_path, csv_file_path=csv_file_path))
            download_link = settings.ROOT_URL + zip_file_name
        else:
            download_link = ''
            return render_to_response("track_me/genericquery_v2.html",
                {'form': form, 'download_link':download_link}, context_instance=RequestContext(request))

@csrf_exempt
def complaints(request):
    msg = ""
#    if request.GET:
#       awb = request.GET['awb']
#       ref_id = request.GET['ref']
#       complaint = Complaints.objects.get(Q(awb_number=int(awb)) or Q(ref_id=int(ref_id)))
#       complaint_dict = {}
#       ch = ComplaintsHistory.objects.filter(complaint=complaint).reverse()[:1]
#       complaint_dict[complaint]=ch[0]
#       return render_to_response("track_me/complaints.html",
#                                  {"complaints":complaint_dict},
#                               context_instance=RequestContext(request))

    if request.POST:
        try:
            awb = request.POST['awb']
            shipment=Shipment.objects.get(airwaybill_number=int(awb))
        except:
            msg = "Incorrect Air waybill Number"
        if msg == "":
            name = request.POST['consignee_name']
            contact_number=request.POST['consignee_mobile']
            email_id=request.POST['consignee_email']
            complaint=request.POST['complaint']
            ref_id = "".join([random.choice(string.digits) for x in range(1,6)])

            complaint = Complaints.objects.create(ref_id=ref_id, awb_number=int(awb), shipment=shipment, shipper=shipment.shipper, consignee_name=name, contact_email=email_id, contact_mobile=contact_number, complaint=complaint, added_by=request.user.employeemaster)
            upd_time = shipment.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            history = shipment_history.objects.filter(shipment=shipment)
            history_latest=history.latest('updated_on')
            history_latest.id=None
            history_latest.employee_code=request.user.employeemaster
            history_latest.remarks=complaint
            history_latest.status=12
            history_latest.save()
            ComplaintsHistory.objects.create(complaint=complaint, remarks=complaint)

            subject = "Complaint for awb number %s, Refrence ID: %s"%(int(awb),ref_id)
            email_msg = "Dear "+str(name)+",Your Complaint has been sucessfully registered, our customer service representative will get back to you shortly, please not down your reference id for further communication %s"%(ref_id)
            to_email = email_id
            from_email = "support@ecomexpress.in"
            send_mail(subject,email_msg,from_email,[to_email])
            msg="Your Complaint has been registered, please not down your reference id for further communication %s"%(ref_id)
        complaint_dict = {}
        if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
            complaints = Complaints.objects.filter(added_by=request.user.employeemaster)
        else:
            complaints = Complaints.objects.all()
        for a in complaints:
                if not complaint_dict.get(a):
                    ch = ComplaintsHistory.objects.filter(complaint=a).reverse()[:1]
                    complaint_dict[a]=ch[0]

        return render_to_response("track_me/complaints.html",
                                  {'msg':msg,
                                   "complaints":complaint_dict},
                               context_instance=RequestContext(request))
    else:
        complaint_dict = {}
        complaints = Complaints.objects.all()
        for a in complaints:
            if not complaint_dict.get(a):
                ch = ComplaintsHistory.objects.filter(complaint=a).latest('updated_on')
                complaint_dict[a]=ch
        return render_to_response("track_me/complaints.html",
                                  {"complaints":complaint_dict},
                               context_instance=RequestContext(request))

@csrf_exempt
def complaints_history(request, cid):
       complaint = Complaints.objects.get(id=cid)
       complaint_hist=ComplaintsHistory.objects.filter(complaint=complaint)
       return render_to_response("track_me/complaints-details.html",
                                  {"complaint":complaint,
                                   "complaint_hist":complaint_hist},
                               context_instance=RequestContext(request))

def complaint_updates(request):
    complaint_id = request.POST['complaint_id']
    complaint = Complaints.objects.get(id=complaint_id)
    remarks = request.POST['remarks']
    ComplaintsHistory.objects.create(complaint=complaint, remarks=remarks, status=1, addressed_by=request.user.employeemaster)
    return HttpResponseRedirect('/track_me/complaint_history/'+complaint_id+'/')

def complaint_resolved(request, id):
    complaint = Complaints.objects.get(id=id)
    complaint.status=1
    complaint.save()
    return HttpResponseRedirect('/track_me/complaint_history/'+id+'/')



def alert(request, tid=1):
    book = xlwt.Workbook(encoding='utf8')
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
    date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
    header_style = xlwt.XFStyle()
    category_style = xlwt.XFStyle()
    status_style = xlwt.XFStyle()
    rto_style=xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True

    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 5
        #
    pattern1 = xlwt.Pattern()
    pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern1.pattern_fore_colour = 0x0A
   #
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = 0x0F
#
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    header_style.pattern = pattern
    status_style.pattern = pattern1
    rto_style.pattern=pattern2
    header_style.font = font
    category_style.font = font
    header_style.borders=borders
    default_style.borders=borders

    b = 0
    inst={}
    inst_download=[]
    altinstructiawb = InstructionAWB.objects.filter(batch_instruction__shipments__current_sc = request.user.employeemaster.service_centre, status = 0)
    for aawb in altinstructiawb:
            upd_time = aawb.batch_instruction.shipments.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            if shipment_history:
                history = shipment_history.objects.filter(shipment=aawb.batch_instruction.shipments)
                if history:
                    history_latest=history.latest('updated_on')
                    if (history_latest.current_sc == request.user.employeemaster.service_centre) and (history_latest.reason_code==None):
                        b = 1
                        instawb = aawb
                        inst[history_latest]=instawb
#                       inst.append(InstructionAWB.objects.get(batch_instruction=a))
                        u = (instawb.batch_instruction.shipments.airwaybill_number, instawb.added_on, instawb.instruction, instawb.batch_instruction.shipments.shipper, instawb.batch_instruction.shipments.consignee, instawb.batch_instruction.shipments.service_centre)
                        inst_download.append(u)

#   altinstruct = BatchInstructionAWB.objects.all()
#   for a in altinstruct:
#           upd_time = a.shipments.added_on
#           monthdir = upd_time.strftime("%Y_%m")
#           shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
#           if shipment_history:
#               history = shipment_history.objects.filter(shipment=a.shipments)
#               if history:
#                   history_latest=history.latest('updated_on')
#                   if (history_latest.current_sc == request.user.employeemaster.service_centre) and (history_latest.reason_code==None):
#                       b = 1
#                       instawb = InstructionAWB.objects.get(batch_instruction=a)
#                       inst[history_latest]=instawb
##                      inst.append(InstructionAWB.objects.get(batch_instruction=a))
#                       u = (instawb.batch_instruction.shipments.airwaybill_number, instawb.added_on, instawb.instruction, instawb.batch_instruction.shipments.shipper, instawb.batch_instruction.shipments.consignee, instawb.batch_instruction.shipments.service_centre)
#                       inst_download.append(u)
    if tid == '2':
            print "chk"
            sheet = book.add_sheet('Alert Report')
            distinct_list = inst_download
            sheet.write(0, 2, "Alert Report", style=header_style)

            for a in range(7):
                sheet.col(a).width = 6000
            sheet.write(3, 0, "Serial Number", style=header_style)
            sheet.write(3, 1, "AWB Number", style=header_style)
            sheet.write(3, 2, "Instruction Added On", style=header_style)
            sheet.write(3, 3, "Instruction", style=header_style)
            sheet.write(3, 4, "Shipper", style=header_style)
            sheet.write(3, 5, "Consignee", style=header_style)
            sheet.write(3, 6, "Destination", style=header_style)
            style = datetime_style
            counter = 1
            for row, rowdata in enumerate(distinct_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        sheet.write(row, col, str(val), style=style)
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Alert_Report.xls'
            book.save(response)
            return response
    else:

        return render_to_response("track_me/alert.html",
                              {"inst":inst},
                              context_instance=RequestContext(request))

def comments_reports_download(request, aid):
    book = xlwt.Workbook(encoding='utf8')
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
    date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
    header_style = xlwt.XFStyle()
    category_style = xlwt.XFStyle()
    status_style = xlwt.XFStyle()
    rto_style=xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True

    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 5
        #
    pattern1 = xlwt.Pattern()
    pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern1.pattern_fore_colour = 0x0A
   #
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = 0x0F
#
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    header_style.pattern = pattern
    status_style.pattern = pattern1
    rto_style.pattern=pattern2
    header_style.font = font
    category_style.font = font
    header_style.borders=borders
    default_style.borders=borders

    inst_download = []
    bi = BatchInstruction.objects.using("local_ecomm").get(id=int(aid))
    for a in bi.batchinstructionawb_set.all():
        for b in a.instructionawb_set.all():
            if b.status == "0":
               status = "unresolved"
            else:
               status = "resolved"
            upd_time = a.shipments.added_on
            monthdir = upd_time.strftime("%Y_%m")

            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            history = shipment_history.objects.using("local_ecomm").filter(shipment=a.shipments).order_by("-id")
            history_latest=history.latest('updated_on')
            val = history_latest.status
            if val == '0':
                     val="Shipment Uploaded"
            if str(val)== '1':
                     val='Pickup Complete / Inscan'
            if str(val)== '2':
                     val='Inscan completion / Ready for Bagging'
            if str(val)== '3':
                     val=str(history_latest.remarks)
            if str(val)== '4':
                     val='Shipment at HUB'
            if str(val)== '5':
                     val=str(history_latest.remarks)
            if str(val)== '6':
                     val='Shipment at Delivery Centre'
            if str(val)== '7':
                     val='Outscan, shipment assigned to Employee, %s %s'%(history_latest.employee_code.firstname, history_latest.employee_code.lastname)
            if str(val)== '8':
                     val='Undelivered'
            if str(val)==  '9':
                      val='Delivered / Closed'
            if str(val)== '11':
                     val='Alternate Instruction given, no action taken yet.'
            if str(val)==  '12':
                      val='Complaint Registered'
            if str(val)== '13':
                     val=str(history_latest.remarks)
            if str(val)==  '14':
                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
            if str(val)== '15':
                     val='Airport Confirmation Successfull, connected to destination via Hub'
            if str(val)==  '17':
                      val=str(history_latest.remarks)

            u = (a.shipments.airwaybill_number, b.added_on.date(), b.instruction, a.shipments.shipper, a.shipments.consignee, a.shipments.service_centre, status, val, history_latest.updated_on.date())
            inst_download.append(u)

    sheet = book.add_sheet('Alternate Instruction Report')
    distinct_list = inst_download
    sheet.write(0, 2, "Alternate Instruction Report", style=header_style)

    for a in range(1, 10):
          sheet.col(a).width = 7000
    sheet.write(3, 0, "Serial Number", style=header_style)
    sheet.write(3, 1, "AWB Number", style=header_style)
    sheet.write(3, 2, "Instruction Added On", style=header_style)
    sheet.write(3, 3, "Instruction", style=header_style)
    sheet.write(3, 4, "Shipper", style=header_style)
    sheet.write(3, 5, "Consignee", style=header_style)
    sheet.write(3, 6, "Destination", style=header_style)
    sheet.write(3, 7, "Status", style=header_style)
    sheet.write(3, 8, "Shipment status", style=header_style)
    sheet.write(3, 9, "Status updated on", style=header_style)

    style = datetime_style
    counter = 1
    for row, rowdata in enumerate(distinct_list, start=4):
           sheet.write(row, 0, str(counter), style=style)
           counter=counter+1
           for col, val in enumerate(rowdata, start=1):
                 sheet.write(row, col, str(val), style=style)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Alternate_Instruction_Report.xls'
    book.save(response)
    return response


@login_not_required
@csrf_exempt
def scan_open(request, tid):
    return HttpResponse(" ")
    if request.GET:
        awb = request.GET['awb']
        order = request.GET['order']
        if awb =="" and order == "":
           return render_to_response("track_me/trackme_open.html",
                               context_instance=RequestContext(request))
        if awb:
         try:
           shipment = Shipment.objects.get(airwaybill_number=awb)
         except:
           return HttpResponse("Air waybill not found, please recheck")

        if order:
         try:
          shipment = Shipment.objects.filter(order_number=int(order)).latest('id')
         except:
          return HttpResponse("Incorrect Order/Reference Number")
        upd_time = shipment.added_on
        monthdir = upd_time.strftime("%Y_%m")
        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
        history = shipment_history.objects.filter(shipment=shipment).order_by("-id")
        history_latest=history.latest('updated_on')
        history_latest_inst=shipment_history.objects.filter(shipment=shipment, status__in=[11,16]).order_by("-updated_on")
        try:
         status_update=StatusUpdate.objects.get(shipment=shipment)
        except:
         status_update=None
        try:
          complaint_status = Complaints.objects.get(shipment=shipment)
        except:
          complaint_status=None

        if tid == "1":
            t = "track_me/trackme_open.html"
        elif tid == "2":
            t ="track_me/trackme_open_2.html"
        else:
            t = "0"
        return render_to_response(t,
                                  {'shipment':shipment,
                                   'history':history,
                                   'history_latest':history_latest,
                                   'history_latest_inst':history_latest_inst,
                                   'status_update':status_update,
                                   'complaint_status':complaint_status},
                               context_instance=RequestContext(request))
    else:
        if tid == "1":
            t = "track_me/trackme_open.html"
        elif tid == "2":
            t ="track_me/trackme_open_2.html"
        else:
            t = "0"
        return render_to_response(t, {}, context_instance=RequestContext(request))

@csrf_exempt
def customer_status(request):
   yest = now - datetime.timedelta(days=3)
   #return HttpResponse(request.user.employeemaster.firstname)
   customer = Customer.objects.get(code=request.user.employeemaster.lastname)
   pickup = PickupRegistration.objects.filter(customer_code=customer, pickup_date__range=(yest,now)).order_by('-added_on')
   return render_to_response("track_me/customer_status.html",
                                  {'pickup':pickup,
                                   'customer':customer},
                               context_instance=RequestContext(request))


def customer_reports_download(request, pid):
    book = xlwt.Workbook(encoding='utf8')
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
    date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
    header_style = xlwt.XFStyle()
    category_style = xlwt.XFStyle()
    status_style = xlwt.XFStyle()
    rto_style=xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True

    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 5
        #
    pattern1 = xlwt.Pattern()
    pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern1.pattern_fore_colour = 0x0A
   #
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = 0x0F
#
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    header_style.pattern = pattern
    status_style.pattern = pattern1
    rto_style.pattern=pattern2
    header_style.font = font
    category_style.font = font
    header_style.borders=borders
    default_style.borders=borders

    shipment = Shipment.objects.filter(pickup=pid)
    download_list=[]
    if not shipment:
         return HttpResponse("No Shipment exists for this pickup")
    if shipment:
            for a in shipment:
                    remarks = ""
                    reason_code = ""
                    reason_code_desc = ""
                    updated_on = ""

                    shipment = a
                    upd_time = shipment.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))

                    try:
                        history = shipment_history.objects.filter(shipment=shipment).latest('updated_on')
                    except:
                        history = ""

                    if history:
                       remarks = history.remarks
                       updated_on = history.updated_on.strftime("%d-%m-%Y")
                       if history.reason_code:
                           reason_code = history.reason_code.code
                           reason_code_desc = history.reason_code.code_description

                    if shipment.statusupdate_set.all():
                       su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                       received_by = su.recieved_by
                       time  = su.time.strftime("%H:%m")
                       date  = su.date.strftime("%d-%m-%Y")
                    else:
                       received_by = ""
                       date = ""
                       time = ""

                    u = (shipment.airwaybill_number, shipment.order_number, shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value,  shipment.pickup.service_centre, shipment.service_centre,shipment.shipper, shipment.consignee, shipment.added_on.strftime("%d-%m-%Y"), shipment.status, shipment.expected_dod.strftime("%d-%m-%Y"), str(updated_on)+" | "+str(history.updated_on.time()), remarks, reason_code, reason_code_desc, received_by, date, time)
                    download_list.append(u)

            sheet = book.add_sheet('Customer Report')
            distinct_list = download_list
            sheet.write(0, 2, "Customer Report", style=header_style)
            for a in range(18):
                 sheet.col(a).width = 6000
            sheet.col(8).width = 10000
            sheet.col(9).width = 6000
            sheet.write(3, 0, "Air Waybill No", style=header_style)
            sheet.write(3, 1, "Order No", style=header_style)
            sheet.write(3, 2, "Weight", style=header_style)
            sheet.write(3, 3, "Vol Weight", style=header_style)
            sheet.write(3, 4, "COD Amount", style=header_style)
            sheet.write(3, 5, "Declared Value", style=header_style)
            sheet.write(3, 6, "Origin", style=header_style)
            sheet.write(3, 7, "Destination", style=header_style)
            sheet.write(3, 8, "Shipper", style=header_style)
            sheet.write(3, 9, "Consignee", style=header_style)
            sheet.write(3, 10, "P/U Date", style=header_style)
            sheet.write(3, 11, "Status", style=header_style)
            sheet.write(3, 12, "Expected Date", style=header_style)
            sheet.write(3, 13, "Updated Date", style=header_style)
            sheet.write(3, 14, "Remarks", style=header_style)
            sheet.write(3, 15, "Reason Code", style=header_style)
            sheet.write(3, 16, "Reason", style=header_style)
            sheet.write(3, 17, "Received by", style=header_style)
            sheet.write(3, 18, "Del Date", style=header_style)
            sheet.write(3, 19, "Del Time", style=header_style)

            style = datetime_style
            counter = 1

	    for row, rowdata in enumerate(distinct_list, start=4):
#                        sheet.write(row, 0, str(counter), style=style)
#                        counter=counter+1
                        for col, val in enumerate(rowdata, start=0):
                            if col == 11:

                              if str(val) == '0':
                                         val="Shipment Uploaded"
                              if str(val)== '1':
                                           val='Pickup Complete / Inscan'
                              if str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                              if str(val)== '3':
                                   val='Bagging completed'
                              if str(val)== '4':
                                    val='Shipment at HUB'
                              if str(val)== '5':
                                       val='Bagging completed at Hub'
                              if str(val)== '6':
                                      val='Shipment at Delivery Centre'
                              if str(val)== '7':
                                     val='Outscan'
                              if str(val)== '8':
                                 val='Undelivered'
                              if str(val)==  '9':
                                  val='Delivered / Closed'
                              if str(val)== '11':
                                   val='Alternate Instruction given'
                              if str(val)==  '12':
                                      val='Complaint Registered'
                              if str(val)== '13':
                                   val='Assigned to Run Code'
                              if str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                              if str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                              sheet.write(row, col, str(val), style=style)
                            if col <> 11:
                                try:
                                    sheet.write(row, col, str(val), style=style)
                                except:
                                   pass
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=customer_report.xls'
            book.save(response)
            return response



#### Folowing are api to fetch details
@login_not_required
@csrf_exempt
def xml_awb_details(request):
    if request.GET or request.POST:
        if request.GET.get('awb'):
            awb = request.GET['awb']
            order = request.GET['order']
        if request.POST.get('awb'):
            awb = request.POST['awb']
            order = request.POST['order']
        customer_api = api_auth(request)
        if not customer_api:
            return HttpResponse("You are not authorised!")

        if awb =="" and order == "":
           return render_to_response("track_me/trackme.html",
                               context_instance=RequestContext(request))

        if awb:
            try:
               shipment = Shipment.objects.get(airwaybill_number=awb, shipper=customer_api.customer)
            except Shipment.DoesNotExist:
               return HttpResponse("Invalid Shipment")
        if order:
            shipment = Shipment.objects.filter(order_number=order, shipper=customer_api.customer).latest('id')
        upd_time = shipment.added_on
        monthdir = upd_time.strftime("%Y_%m")

        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
        history = shipment_history.objects.filter(shipment=shipment).order_by("-id")
        history_latest=history.latest('updated_on')
        history_latest_inst=shipment_history.objects.filter(shipment=shipment, status__in=[11,16]).order_by("-updated_on")
        try:
         status_update=StatusUpdate.objects.get(shipment=shipment)
        except:
         status_update=None
        try:
          complaint_status = Complaints.objects.get(shipment=shipment)
        except:
          complaint_status=None
        return render_to_response("track_me/api/xml_awb_details.html",
                                  {'shipment':shipment,
                                   'history':history,
                                   'history_latest':history_latest,
                                   'history_latest_inst':history_latest_inst,
                                   'status_update':status_update,
                                   'complaint_status':complaint_status},
                               mimetype="application/xhtml+xml")

#### Folowing are api to fetch details
@login_not_required
@csrf_exempt
def xml_multiple_airwaybill(request):
    if request.POST or request.GET:
        awba = ""
        shipments = []
        shipment_info = {}
        customer_api = api_auth(request)
        #return HttpResponse("%s!" % request.GET["password"])
        if not customer_api:
            return HttpResponse("You are not authorised!")
        if request.POST.get('awb'):
            awba=request.POST['awb']
        elif request.GET.get('awb'):
            awba=request.GET['awb']

        a = awba.split(',')
        b = ""
        download_list = []
        if not awba:
            if request.POST.get('order'):
                order=request.POST['order']
            elif request.GET.get('order'):
                order=request.GET['order']

            b = order.split(',')
        if a:
          for awbq in a:
             try:
              shipment=Shipment.objects.get(airwaybill_number=int(awbq), shipper=customer_api.customer)
              shipments.append(shipment.airwaybill_number)
             except:
              pass
          for awb in shipments:
            if awb:
                remarks = ""
                reason_code = ""
                reason_code_desc = "In Transit"
                updated_on = ""
                shipment = Shipment.objects.get(airwaybill_number=int(awb))
                upd_time = shipment.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))

                try:
                    history = shipment_history.objects.filter(shipment=shipment).latest('updated_on')
                except:
                    history = ""
                try:
                    expected_dod = shipment.expected_dod.strftime("%d-%m-%Y")
                except:
                    expected_dod = ""

                if history:
                   shipment_info[shipment] = history
                   remarks = history.remarks
                   if history.reason_code:
                       reason_code = history.reason_code.code
                       reason_code_desc = history.reason_code.code_description
                   updated_on = history.updated_on.strftime("%d-%m-%Y")


                if shipment.statusupdate_set.all():
                   su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                   received_by = su.recieved_by
                   time  = su.time.strftime("%H:%m")
                   date  = su.date.strftime("%d-%m-%Y")
                else:
                   received_by = ""
                   time  = ""
                   date  = ""

                val = shipment.status
                if str(val) == '0':
                                         val="Shipment Uploaded"
                if str(val)== '1':
                                           val='Pickup Complete / Inscan'
                if str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                if str(val)== '3':
                                   val='Bagging completed'
                if str(val)== '4':
                                    val='Shipment at HUB'
                if str(val)== '5':
                                       val='Bagging completed at Hub'
                if str(val)== '6':
                                      val='Shipment at Delivery Centre'
                if str(val)== '7':
                                     val='Outscan'
                if str(val)== '8':
                                 val='Undelivered'
                if str(val)==  '9':
                                  val='Delivered / Closed'
                if str(val)== '11':
                                   val='Alternate Instruction given'
                if str(val)==  '12':
                                      val='Complaint Registered'
                if str(val)== '13':
                                   val='Assigned to Run Code'
                if str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                if str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                if (shipment.reason_code_id == 5 or shipment.return_shipment==2):
                                  val = "Returned"
           #     try:
                u = (shipment.airwaybill_number, shipment.order_number, shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value,  shipment.pickup.service_centre, shipment.service_centre,shipment.shipper, shipment.consignee, shipment.added_on.strftime("%d-%m-%Y"), val, expected_dod, str(updated_on)+" | "+str(history.updated_on.time()), remarks, reason_code, reason_code_desc, received_by, date, time)
                download_list.append(u)
             #   except:
            #          return HttpResponse(shipment.status)
        if b:
            for ord in b:
                if ord:
                    shipment = Shipment.objects.filter(order_number=int(ord),  shipper=customer_api.customer).latest('id')
                    shipments.append(shipment)
                    upd_time = shipment.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    try:
                        history = shipment_history.objects.filter(shipment=shipment).latest('updated_on')
                    except:
                        history = ""
                    if history:
                       shipment_info[shipment] = history
                       remarks = history.remarks
                       reason_code = history.reason_code.code
                       reason_code_desc = history.reason_code.code_description
                       updated_on = history.updated_on.strftime("%d-%m-%Y")
                    else:
                       shipment_info[shipment] = history
                       remarks = ""
                       reason_code = ""
                       reason_code_desc = ""
                       updated_on = ""

                    if shipment.statusupdate_set.all():
                       su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                       received_by = su.recieved_by
                       time  = su.time.strftime("%H:%m")
                       date  = su.date.strftime("%d-%m-%Y")
                    else:
                       received_by = ""
                       date = ""
                       time = ""
                    if shipment.status:
                              val = shipment.status
                              if str(val) == '0':
                                         val="Shipment Uploaded"
                              if str(val)== '1':
                                           val='Pickup Complete / Inscan'
                              if str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                              if str(val)== '3':
                                   val='Bagging completed'
                              if str(val)== '4':
                                    val='Shipment at HUB'
                              if str(val)== '5':
                                       val='Bagging completed at Hub'
                              if str(val)== '6':
                                      val='Shipment at Delivery Centre'
                              if str(val)== '7':
                                     val='Outscan'
                              if str(val)== '8':
                                 val='Undelivered'
                              if str(val)==  '9':
                                  val='Delivered / Closed'
                              if str(val)== '11':
                                   val='Alternate Instruction given'
                              if str(val)==  '12':
                                      val='Complaint Registered'
                              if str(val)== '13':
                                   val='Assigned to Run Code'
                              if str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                              if str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                    if (shipment.reason_code_id == 5 or shipment.return_shipment==2):
                                  val = "Returned"

        return render_to_response("track_me/api/xmlmultipleairwaybill.html",
                                  {'shipments':shipments, 'shipment_info':shipment_info},
                               context_instance=RequestContext(request),
                               mimetype="application/xhtml+xml")
    else:
      return HttpResponse("False")

@login_not_required
@csrf_exempt
def xml_multiple_airwaybill_details(request):
    if request.POST or request.GET:
        awba = ""
        shipments = []
        shipment_info = {}
        customer_api = api_auth(request)
        if not customer_api:
            return HttpResponse("You are not authorised!")
        if request.POST.get('awb'):
            awba=request.POST['awb']
        elif request.GET.get('awb'):
            awba=request.GET['awb']

        a = awba.split(',')
        b = ""
        download_list = []
        if not awba:
            if request.POST.get('order'):
                order=request.POST['order']
            elif request.GET.get('order'):
                order=request.GET['order']

            b = order.split(',')
        if a:
          for awbq in a:
             try:
              shipment=Shipment.objects.get(airwaybill_number=int(awbq), shipper=customer_api.customer)
              shipments.append(shipment.airwaybill_number)
             except:
              pass
          for awb in shipments:
            if awb:
                remarks = ""
                reason_code = ""
                reason_code_desc = "In Transit"
                updated_on = ""
                shipment = Shipment.objects.get(airwaybill_number=int(awb))
                upd_time = shipment.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))

                try:
                    history = shipment_history.objects.filter(shipment=shipment).exclude(status__in=[11,12,16,20]).order_by('-updated_on')
                except:
                    history = ""
                try:
                    expected_dod = shipment.expected_dod.strftime("%d-%m-%Y")
                except:
                    expected_dod = ""

                if history:
                   shipment_info[shipment] = history
                   remarks = history[0].remarks
                   if history[0].reason_code:
                       reason_code = history[0].reason_code.code
                       reason_code_desc = history[0].reason_code.code_description
                   updated_on = history[0].updated_on.strftime("%d-%m-%Y")


                if shipment.statusupdate_set.all():
                   su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                   received_by = su.recieved_by
                   time  = su.time.strftime("%H:%m")
                   date  = su.date.strftime("%d-%m-%Y")
                else:
                   received_by = ""
                   time  = ""
                   date  = ""

                val = shipment.status
                if str(val) == '0':
                                         val="Shipment Uploaded"
                if str(val)== '1':
                                           val='Pickup Complete / Inscan'
                if str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                if str(val)== '3':
                                   val='Bagging completed'
                if str(val)== '4':
                                    val='Shipment at HUB'
                if str(val)== '5':
                                       val='Bagging completed at Hub'
                if str(val)== '6':
                                      val='Shipment at Delivery Centre'
                if str(val)== '7':
                                     val='Outscan'
                if str(val)== '8':
                                 val='Undelivered'
                if str(val)==  '9':
                                  val='Delivered / Closed'
                if str(val)== '11':
                                   val='Alternate Instruction given'
                if str(val)==  '12':
                                      val='Complaint Registered'
                if str(val)== '13':
                                   val='Assigned to Run Code'
                if str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                if str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                if (shipment.reason_code_id == 5 or shipment.return_shipment==2):
                                  val = "Returned"
           #     try:
                u = (shipment.airwaybill_number, shipment.order_number, shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value,  shipment.pickup.service_centre, shipment.service_centre,shipment.shipper, shipment.consignee, shipment.added_on.strftime("%d-%m-%Y"), val, expected_dod, str(updated_on)+" | "+str(history[0].updated_on.time()), remarks, reason_code, reason_code_desc, received_by, date, time)
                download_list.append(u)
             #   except:
            #          return HttpResponse(shipment.status)
        if b:
            for ord in b:
                if ord:
                    shipment = Shipment.objects.filter(order_number=int(ord),  shipper=customer_api.customer).latest('id')
                    shipments.append(shipment)
                    upd_time = shipment.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    try:
                        history = shipment_history.objects.filter(shipment=shipment).exclude(status__in=[11,12,16]).order_by('-updated_on')
                    except:
                        history = ""
                    if history:
                       shipment_info[shipment] = history
                       remarks = history[0].remarks
                       reason_code = history[0].reason_code.code
                       reason_code_desc = history[0].reason_code.code_description
                       updated_on = history[0].updated_on.strftime("%d-%m-%Y")
                    else:
                       shipment_info[shipment] = history
                       remarks = ""
                       reason_code = ""
                       reason_code_desc = ""
                       updated_on = ""

                    if shipment.statusupdate_set.all():
                       su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                       received_by = su.recieved_by
                       time  = su.time.strftime("%H:%m")
                       date  = su.date.strftime("%d-%m-%Y")
                    else:
                       received_by = ""
                       date = ""
                       time = ""
                    if shipment.status:
                              val = shipment.status
                              if str(val) == '0':
                                         val="Shipment Uploaded"
                              if str(val)== '1':
                                           val='Pickup Complete / Inscan'
                              if str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                              if str(val)== '3':
                                   val='Bagging completed'
                              if str(val)== '4':
                                    val='Shipment at HUB'
                              if str(val)== '5':
                                       val='Bagging completed at Hub'
                              if str(val)== '6':
                                      val='Shipment at Delivery Centre'
                              if str(val)== '7':
                                     val='Outscan'
                              if str(val)== '8':
                                 val='Undelivered'
                              if str(val)==  '9':
                                  val='Delivered / Closed'
                              if str(val)== '11':
                                   val='Alternate Instruction given'
                              if str(val)==  '12':
                                      val='Complaint Registered'
                              if str(val)== '13':
                                   val='Assigned to Run Code'
                              if str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                              if str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                    if (shipment.reason_code_id == 5 or shipment.return_shipment==2):
                                  val = "Returned"

        return render_to_response("track_me/api/xmlmultipleairwaybill_details.html",
                                  {'shipments':shipments, 'shipment_info':shipment_info},
                               context_instance=RequestContext(request),
                               mimetype="application/xhtml+xml")
    else:
      return HttpResponse("False")

#### Folowing are api to fetch details
@login_not_required
@csrf_exempt
def xml_multiple_airwaybill_unused(request):
    if request.POST or request.GET:
        awba = ""
        shipments = []
        shipment_info = {}
        customer_api = api_auth(request)
        if not customer_api:
            return HttpResponse("You are not authorised!")
        if request.POST.get('awb'):
            awba=request.POST['awb']
        elif request.GET.get('awb'):
            awba=request.GET['awb']

        a = awba.split(',')
        b = ""
        download_list = []
        if not awba:
            if request.POST.get('order'):
                order=request.POST['order']
            elif request.GET.get('order'):
                order=request.GET['order']

            b = order.split(',')
        shipment_not_found = []
        if a:
          for awbq in a:
             try:
              shipment=Shipment.objects.get(airwaybill_number=int(awbq), shipper=customer_api.customer)
              shipments.append(shipment.airwaybill_number)
             except:
              shipment_not_found.append(awbq)
          for awb in shipments:
            if awb:
                remarks = ""
                reason_code = ""
                reason_code_desc = "In Transit"
                updated_on = ""
                shipment = Shipment.objects.get(airwaybill_number=int(awb))
                upd_time = shipment.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))

                try:
                    history = shipment_history.objects.filter(shipment=shipment).latest('updated_on')
                except:
                    history = ""
                try:
                    expected_dod = shipment.expected_dod.strftime("%d-%m-%Y")
                except:
                    expected_dod = ""

                if history:
                   shipment_info[shipment] = history
                   remarks = history.remarks
                   if history.reason_code:
                       reason_code = history.reason_code.code
                       reason_code_desc = history.reason_code.code_description
                   updated_on = history.updated_on.strftime("%d-%m-%Y")


                if shipment.statusupdate_set.all():
                   su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                   received_by = su.recieved_by
                   time  = su.time.strftime("%H:%m")
                   date  = su.date.strftime("%d-%m-%Y")
                else:
                   received_by = ""
                   time  = ""
                   date  = ""

                val = shipment.status
                if str(val) == '0':
                                         val="Shipment Uploaded"
                if str(val)== '1':
                                           val='Pickup Complete / Inscan'
                if str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                if str(val)== '3':
                                   val='Bagging completed'
                if str(val)== '4':
                                    val='Shipment at HUB'
                if str(val)== '5':
                                       val='Bagging completed at Hub'
                if str(val)== '6':
                                      val='Shipment at Delivery Centre'
                if str(val)== '7':
                                     val='Outscan'
                if str(val)== '8':
                                 val='Undelivered'
                if str(val)==  '9':
                                  val='Delivered / Closed'
                if str(val)== '11':
                                   val='Alternate Instruction given'
                if str(val)==  '12':
                                      val='Complaint Registered'
                if str(val)== '13':
                                   val='Assigned to Run Code'
                if str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                if str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                if (shipment.reason_code_id == 5 or shipment.return_shipment==2):
                                  val = "Returned"
           #     try:
                u = (shipment.airwaybill_number, shipment.order_number, shipment.actual_weight, shipment.volumetric_weight, shipment.collectable_value, shipment.declared_value,  shipment.pickup.service_centre, shipment.service_centre,shipment.shipper, shipment.consignee, shipment.added_on.strftime("%d-%m-%Y"), val, expected_dod, str(updated_on)+" | "+str(history.updated_on.time()), remarks, reason_code, reason_code_desc, received_by, date, time)
                download_list.append(u)
             #   except:
            #          return HttpResponse(shipment.status)
        if b:
            for ord in b:
                if ord:
                    shipment = Shipment.objects.filter(order_number=int(ord),  shipper=customer_api.customer).latest('id')
                    shipments.append(shipment)
                    upd_time = shipment.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    try:
                        history = shipment_history.objects.filter(shipment=shipment).latest('updated_on')
                    except:
                        history = ""
                    if history:
                       shipment_info[shipment] = history
                       remarks = history.remarks
                       reason_code = history.reason_code.code
                       reason_code_desc = history.reason_code.code_description
                       updated_on = history.updated_on.strftime("%d-%m-%Y")
                    else:
                       shipment_info[shipment] = history
                       remarks = ""
                       reason_code = ""
                       reason_code_desc = ""
                       updated_on = ""

                    if shipment.statusupdate_set.all():
                       su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                       received_by = su.recieved_by
                       time  = su.time.strftime("%H:%m")
                       date  = su.date.strftime("%d-%m-%Y")
                    else:
                       received_by = ""
                       date = ""
                       time = ""
                    if shipment.status:
                              val = shipment.status
                              if str(val) == '0':
                                         val="Shipment Uploaded"
                              if str(val)== '1':
                                           val='Pickup Complete / Inscan'
                              if str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                              if str(val)== '3':
                                   val='Bagging completed'
                              if str(val)== '4':
                                    val='Shipment at HUB'
                              if str(val)== '5':
                                       val='Bagging completed at Hub'
                              if str(val)== '6':
                                      val='Shipment at Delivery Centre'
                              if str(val)== '7':
                                     val='Outscan'
                              if str(val)== '8':
                                 val='Undelivered'
                              if str(val)==  '9':
                                  val='Delivered / Closed'
                              if str(val)== '11':
                                   val='Alternate Instruction given'
                              if str(val)==  '12':
                                      val='Complaint Registered'
                              if str(val)== '13':
                                   val='Assigned to Run Code'
                              if str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                              if str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                    if (shipment.reason_code_id == 5 or shipment.return_shipment==2):
                                  val = "Returned"

        return render_to_response("track_me/api/xmlmultipleairwaybill_unusedawb.html",
                                  {'shipments':shipments, 'shipment_info':shipment_info, 'shipment_not_found':shipment_not_found},
                               context_instance=RequestContext(request),
                               mimetype="application/xhtml+xml")
    else:
      return HttpResponse("False")

def mis(request):
    if request.method == 'POST':
        # read the excel file and get the airwaybill numbers from sheet
        mis_file = request.FILES['mis_file']
        content = mis_file.read()
        wb = xlrd.open_workbook(file_contents=content)
        sheetnames = wb.sheet_names()
        sh = wb.sheet_by_name(sheetnames[0])
        awbs = sh.col_values(0)[1:]
        awbs = [x for x in awbs if x]
        # get the shipments for the given airwaybill numbers and update the
        # alternate instructions(rto instructions)
        shipments = Shipment.objects.filter(airwaybill_number__in=awbs, status=8)
        for shipment in shipments:
            altinstruction = AlternateInstruction.objects.filter(shipments=shipment).order_by('-date')
            if altinstruction.exists():
                a = altinstruction[0]
                a.comments = "Shipment Undelivered/ Process for RTO"
                a.save()
                # create history/making records of for the objects.using('local_ecomm') updations.
            else:
                a = AlternateInstruction.objects.create(comments="Shipment Undelivered/ Process for RTO",
                                            instruction_type=1, employee_code=request.user.employeemaster, date=datetime.date.today(),
                                            time=datetime.datetime.now().time())
                a.shipments = [shipment]
                a.save()
            RTOInstructionUpdate.objects.create(shipment=shipment, modified_by=request.user, alternateinstruction=a)
            #shipment_history = get_shipment_history(shipment)
            #shipment_history.objects.create(shipment=shipment,
                    #employee_code=request.user.employeemaster,
                    #current_sc=request.user.employeemaster.service_centre,
                    #remarks="Shipment Undelivered/ Process for RTO")
        return HttpResponseRedirect('/track_me/comments/?awb=&order=')

def tele(request):
  if request.method == 'POST':
    tele_file = request.FILES['tele_file']
    content = tele_file.read()
    wb = xlrd.open_workbook(file_contents=content)
    sheetnames = wb.sheet_names()
    sh = wb.sheet_by_name(sheetnames[0])
    awbn = sh.col_values(0)[1:]
    comment= sh.col_values(1)[1:]
    shipment_not_found = {}
    for i in range(len(awbn)):
      try:
        shipment=Shipment.objects.get(airwaybill_number=int(awbn[i]))
        if shipment.status == 9:
          shipment_not_found[int(awbn[i])] = "Delivered"
        else:
          user = request.user
          TeleCallingReport.objects.create(shipment=shipment,comments=comment[i],updated_by =user.employeemaster )
          upd_time = shipment.added_on
          monthdir = upd_time.strftime("%Y_%m")
          shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
          shipment_history.objects.create(shipment=shipment, employee_code = request.user.employeemaster, current_sc = request.user.employeemaster.service_centre, expected_dod=shipment.expected_dod, status=20,remarks=comment[i])
      except Shipment.DoesNotExist:
        shipment_not_found[int(awbn[i])] = "Not Found"
    return render_to_response("track_me/telereport.html",{'errors':shipment_not_found},
                               context_instance=RequestContext(request))

  return HttpResponseRedirect('/track_me/comments/?awb=&order=')


@login_not_required
@csrf_exempt
def track_shipment(request):
    if request.GET:
        awb = request.GET['awb']
        order = request.GET['order']
        if awb =="" and order == "":
           return render_to_response("track_me/trackme_open.html",
                               context_instance=RequestContext(request))
        if awb:
         try:
           shipment = Shipment.objects.get(airwaybill_number=awb)
         except:
           return HttpResponse("Air waybill not found, please recheck")

        if order:
         try:
          shipment = Shipment.objects.filter(order_number=int(order)).latest('id')
         except:
          return HttpResponse("Incorrect Order/Reference Number")
        upd_time = shipment.added_on
        monthdir = upd_time.strftime("%Y_%m")
        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
        history = shipment_history.objects.filter(shipment=shipment).order_by("-id")
        history_latest=history.latest('updated_on')
        history_latest_inst=shipment_history.objects.filter(shipment=shipment, status__in=[11,16]).order_by("-updated_on")
        try:
         status_update=StatusUpdate.objects.get(shipment=shipment)
        except:
         status_update=None
        try:
          complaint_status = Complaints.objects.get(shipment=shipment)
        except:
          complaint_status=None

        t = "track_me/trackme_open.html"
        return render_to_response(t,
                                  {'shipment':shipment,
                                   'history':history,
                                   'history_latest':history_latest,
                                   'history_latest_inst':history_latest_inst,
                                   'status_update':status_update,
                                   'complaint_status':complaint_status},
                               context_instance=RequestContext(request))
    else:
        t = "track_me/trackme_open.html"
        return render_to_response(t, {}, context_instance=RequestContext(request))

def bag_history(request):
    if not request.GET:
        data = {}
        return render_to_response('track_me/bag_history.html',
            data, context_instance=RequestContext(request))
    else:
        bag_number = request.GET.get('bag_number')
        try:
            bag = Bags.objects.get(bag_number=bag_number)
            message =  None
            history = get_bag_history(bag)
        except Bags.DoesNotExist:
            bag = None
            history = []
            message = '{0} Does Not exist'.format(bag_number)

        data = {'history':history, 'message': message, 'bag': bag}
        return render_to_response('track_me/bag_history.html',
                data, context_instance=RequestContext(request))

@login_not_required
@csrf_exempt
def mawb_api(request):
    if not request.POST:
       return render_to_response('track_me/api_form.html')
    else:
        capi =  api_auth(request)
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")

        if not request.FILES.get('upload_file'):
                return HttpResponse("%s"%"Invalid Request")

        shipments = request.FILES['upload_file']
        data = [row for row in csv.reader(shipments.read().splitlines())]
        file_name = "/airwaybill_status_%s.csv"%(now)
        path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
        csv_out = open(path_to_save,"wb")
        mywriter = csv.writer(csv_out)
        u = ("Docket Number","Origin", "Destination", "Docket Status", "First Scan at Org Date", "First Scan at Org Time",
             "First Scan at Org Status", "Last Scan at Org Date", "Last Scan at Org Time", "Last Scan at Origin Status",
             "First Scan at Dest Date", "First Scan at Dest Time", "First Scan at Dest Status", "Latest Scan Date",
             "Latest Scan Time", "Latest Scan Status", "Latest Scan Location","First OS Date", "Latest Undel Reason",
             "No. of OS")
        mywriter.writerow(u)

#        with open(shipments, 'rb') as csvfile:
        for row in data[1:]:
            # read = csv.reader(csvfile)
            # for row in read:
                 sh = Shipment.objects.using('local_ecomm').filter(airwaybill_number__in = row, shipper = capi.customer)
                 if sh:
                   shipment = sh[0]
                   upd_time = shipment.added_on
                   monthdir = upd_time.strftime("%Y_%m")
                   shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))

                   hist = shipment_history.objects.using('local_ecomm').\
                          filter(shipment=shipment, status__in=[0,14,6,7,8]).\
                          values_list('status','updated_on')
                   sh_hist = {}

                   for r in hist:
                       if not sh_hist.get(r[0]):
                             sh_hist[r[0]] = (r[0],r[1])
                   first_scan_org_date = sh_hist[0][1].date() if 0 in sh_hist else ""
                   first_scan_org_time = sh_hist[0][1].time() if 0 in sh_hist else ""
                   first_scan_org_status = get_internal_shipment_status(sh_hist[0][0]) if 0 in sh_hist else ""

                   last_scan_org_date = sh_hist[14][1].date() if 14 in sh_hist else ""
                   last_scan_org_time = sh_hist[14][1].time() if 14 in sh_hist else ""
                   last_scan_org_status = get_internal_shipment_status(sh_hist[14][0]) if 14 in sh_hist else ""
                                         
                   first_scan_dest_date = sh_hist[6][1].date() if 6 in sh_hist else ""
                   first_scan_dest_time = sh_hist[6][1].time() if 6 in sh_hist else ""
                   first_scan_dest_status = get_internal_shipment_status(sh_hist[6][0]) if 6 in sh_hist else ""

                   first_os_date = sh_hist[7][1].date() if 7 in sh_hist else ""
                   first_undel_reason = hist.filter(status=8).values_list('reason_code__code_description').latest('updated_on')[0] if 8 in sh_hist else ""
                   no_of_os = hist.filter(status=7).count()     

                   u = (shipment.airwaybill_number, shipment.pickup.service_centre, shipment.service_centre,
                       get_internal_shipment_status(shipment.status), first_scan_org_date, first_scan_org_time, 
                       first_scan_org_status, last_scan_org_date, last_scan_org_time, last_scan_org_status, first_scan_dest_date, 
                       first_scan_dest_time, first_scan_dest_status, shipment.shipext.updated_on.date(), 
                       shipment.shipext.updated_on.time(), get_internal_shipment_status(shipment.status), shipment.current_sc,
                       first_os_date, first_undel_reason, no_of_os)

                   mywriter.writerow(u)
        return HttpResponseRedirect("/static/uploads/%s"%(file_name))

          
def generate_call_center_report(sdate):
    cc_comments = CallCentreComment.objects.filter(date=sdate)
    report = ReportGenerator('call_center_report_{0}.xlsx'.format(sdate))
    report.write_header(('AWB', 'Origin','Destination','Employee','Comment'))
    for cc_comment in cc_comments:
        s = cc_comment.shipments 
        awbno = s.airwaybill_number
        origin = s.pickup.service_centre.center_name
        destination = s.original_dest.center_name
        employee = cc_comment.employee_code.employee_code
        comment = cc_comment.comments
        report.write_row((awbno, origin, destination, employee, comment))

    file_name = report.manual_sheet_close()
    path = 'http://billing.ecomexpress.in/static/uploads/reports/' + file_name    
    return file_name

def call_centre_report(request):
    if request.method == 'GET':
        sdate = request.GET.get("cdate")
        file_name = generate_call_center_report(sdate)    
        return HttpResponseRedirect('/static/uploads/reports/' + file_name)
    else:
        return HttpResponse("error...")

def comment(request):
    if request.method == 'POST':
        user = request.user
        emp = EmployeeMaster.objects.get(user=user)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        # read the excel file and get the airwaybill numbers from sheet
        comment_file = request.FILES['comment_file']
        content = comment_file.read()
        workbook = xlrd.open_workbook(file_contents=content)
        sheet_name = workbook.sheet_by_index(0)
        error_awbs = []
        # reading row by row
        for i in range(sheet_name.nrows):
            row = sheet_name.row_slice(i)
            awbno = row[0].value
            comment = row[1].value
            # if there is no comment dont update
            if not comment:
                error_awbs.append(awb)
                continue
            try:
                shipment = Shipment.objects.get(airwaybill_number=int(awbno))
                cc_comment = CallCentreComment.objects.create(
                        employee_code=emp,
                        date=today, shipments=shipment,
                        comments=comment
                )
                upd_time = shipment.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model(
                    'service_centre', 'ShipmentHistory_%s' % (monthdir)
                )
                status = 21
                shipment_history.objects.create(
                    shipment=shipment, status=status, 
                    employee_code=request.user.employeemaster, 
                    current_sc=request.user.employeemaster.service_centre, 
                    remarks=comments
                )
            except Shipment.DoesNotExist: 
                error_awbs.append(awb)
        return HttpResponseRedirect(
            '/track_me/comments/?awb=%d&order=%s' % (
                shipment.airwaybill_number, shipment.order_number
                )
        )

@csrf_exempt
def multiple_bag(request):
    return render_to_response("track_me/multiplebag.html",context_instance=RequestContext(request))

@csrf_exempt
def multiplebag_detail(request):
    status_dict = {
        0:'bag creation at service center',
        1:'bag closed', 
        2:'bag connected', 
        3:'bag at hub', 
        5:'bag creation at hub', 
        6:'bag closed at hub', 
        7:'bag connected at hub', 
        8:'delivery inscan',
        9:'debagged at hub, all shipments delinked', 
       10:'debagged at delivery, all shipments delinked', 
       11:'deleted'}
    if request.method == 'POST':
        if request.POST.get('submit'):
            bag_number = request.POST.get('multipleawb')
            bag_val = bag_number.split('\r\n')
            data_dict = {}
            for bag_id in bag_val:
                try:
                     bag_data = Bags.objects.get(bag_number=bag_id)
                # for bag_data in bag:
                     data_dict[bag_data.bag_number] = {'no_of_shipments': bag_data.ship_data.count(), 
                'bag_status': status_dict[bag_data.bag_status], 
                'connection_id': bag_data.connection_set.values_list('id',flat = True)[0], 
                'origin': bag_data.origin.center_name, 'destination':bag_data.destination.center_name, 
                'current_sc':bag_data.current_sc, 
                'awbs': bag_data.ship_data.values_list('airwaybill_number', flat=True)}
                except Bags.DoesNotExist:
                    pass
            return render_to_response('track_me/multiplebag.html',
                {'data_dict':data_dict}, context_instance=RequestContext(request))
    if request.POST.get("download"):
        row = 4
        #download_list = []
        file_name = "/Multiplebag_detail.xlsx"
        path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
        workbook = Workbook(path_to_save)
        sheet = workbook.add_worksheet()
 #       sheet.write(0, 0, "Sr")
        sheet.write(3,0,"Bag Number")
        sheet.write(3,1,"No Of Shipment")
        sheet.write(3,2,"Bag Status")
        sheet.write(3,3,"Connection Id")
        sheet.write(3,4,"Origin")
        sheet.write(3,5,"Destination")
        sheet.write(3,6,"Current Service Center")
#        sheet.write(0, 1, "AWB Number")
        bag_number = request.POST.get('multipleawb')
        bag_val = bag_number.split('\r\n')
        for bag_id in bag_val:
            try:
                bag_detail = Bags.objects.get(bag_number=bag_id)
                u = (bag_detail.bag_number,bag_detail.ship_data.count(),
                 status_dict[bag_detail.bag_status],bag_detail.connection_set.values_list('id',flat = True)[0],
                 bag_detail.origin.center_name,bag_detail.destination.center_name,bag_detail.current_sc)
                #download_list.append(u) 
            except:
                pass
            row = row + 1
            
            for col, val in enumerate(u, start=0):
                try:      #   val = val.encode('utf-8') if isinstance(val,unicode)  else val^M
                    sheet.write(row, col, str(val))
                except:
                    pass
        workbook.close()
         # added to remove return redirection issue
        excel = open(path_to_save, "rb")
        output = StringIO.StringIO(excel.read())
        out_content = output.getvalue()
        output.close()
 
        response = HttpResponse(out_content,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename={0}".format(file_name)
        return response
        
'''        download_list = []
    if request.POST.get("download"):
        book = xlwt.Workbook(encoding='utf8')
        datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
        date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
        header_style = xlwt.XFStyle()
        bag_number = request.POST.get('multipleawb')
        bag_val = bag_number.split('\r\n')
        for bag_id in bag_val:
            try:
                bag_detail = Bags.objects.get(bag_number=bag_id)
        #        return HttpResponse(bag_detail.bag_number)
               # for bag_detail in bag_data:
                u = (bag_detail.bag_number,bag_detail.ship_data.count(),
                status_dict[bag_detail.bag_status],bag_detail.connection_set.values_list('id',flat = True)[0],
                bag_detail.origin.center_name,bag_detail.destination.center_name,bag_detail.current_sc)
                download_list.append(u) 
               # return HttpResponse(download_list)
            except:
                pass
        sheet = book.add_sheet('Multiple Bag')
        distinct_list = download_list
        sheet.write(0,2,"Multibag Bag Detail", style = header_style)
        for a in range(10):
            sheet.col(a).width = 6000
        sheet.write(3,0,"Bag Number", style = header_style)         
        sheet.write(3,1,"No Of Shipment", style = header_style)         
        sheet.write(3,2,"Bag Status", style = header_style)         
        sheet.write(3,3,"Connection Id", style = header_style)         
        sheet.write(3,4,"Origin", style = header_style)         
        sheet.write(3,5,"Destination", style = header_style)         
        sheet.write(3,6,"Current Service Center", style = header_style)
        style = datetime_style
        counter = 1
        for row,rowdata in enumerate(distinct_list,start = 4):
            for col, val in enumerate(rowdata,start = 0):     
                try:
                    sheet.write(row,col,str(val),style = style)
                except:
                    pass
        response = HttpResponse(mimetype = 'application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename = multiple_bag.xls'
        book.save(response)
        return response  ''' 
    
        
       # return render_to_response('track_me/multiplebag.html',
        #        {'data_dict':data_dict}, context_instance=RequestContext(request))
