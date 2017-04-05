# enter your views here
import requests
import json
import cgi
import ho.pisa as pisa
import cStringIO as StringIO
from copy import deepcopy
import dateutil.parser
from decimal import Decimal
from xlsxwriter.workbook import Workbook
from collections import OrderedDict

from django.db.models import *
from django.shortcuts import render_to_response
from django.template.loader import render_to_string, get_template
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.template import Context
from django.db.models import datetime, Sum
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from jsonview.decorators import json_view

from track_me.models import *
from service_centre.models import *
from airwaybill.models import AirwaybillNumbers
from ecomm_admin.models import update_changelog
from utils import (
    rts_pricing, history_update, sdl_charge, 
    price_updated, shipment_mail, update_sdl_billing
)
from nimda.views import rto_reversal
from delivery.models import (
    DashboardVisiblity, update_bag_history, get_expected_dod,
    cashtally_deliveryoutscan_details, cashtally_shipment_details
)


from smsapp.models import *
from smsapp.views import *
from reports.report_api import ReportGenerator
from .models import UpdateCardPaymentModified, CreditPaymentAwbDetails
from .return_redirection import update_rts_shipment

now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")
before = now - datetime.timedelta(days=3)

@csrf_exempt
def inscan_bag(request):
    '''Inscan Bag operation'''
    dest = request.user.employeemaster.service_centre_id
    if request.POST:
        bag_number = request.POST['bag_id']
        #bag = Bags.objects.filter(bag_number=bag_number, bag_status__in=[2, 3, 7, 8])
        bag = Bags.objects.filter(bag_number=bag_number, bag_status__in=[1,2, 3, 6, 7, 8])
        if not bag:
            return HttpResponse("This bag can't be scanned.")
        if bag[0].destination_id != dest:
            status_type = 3
        else:
            status_type = 1
        
        #connection = bag[0].connection_set.all()[0]
        connection = bag[0].connection_set.all()
        if connection: connection = connection[0]
        else: connection = None
        
        bag.update(bag_status=8, status_type=status_type, updated_on=now, current_sc=dest)
        bag[0].shipments.filter().exclude(status__in=[7,8,9]).exclude(
      	    reason_code__code__in=[333, 888, 999]
      	).exclude(rts_status = 2).update(status=5, updated_on=now, current_sc=dest)
        update_bag_history(
      	    bag[0], employee=request.user.employeemaster, action="scanned at DC",
      	    content_object=bag[0], sc=request.user.employeemaster.service_centre,
            status=14)
        ships = bag[0].shipments.exclude(status__in=[7,8,9]).exclude(
      	    reason_code__code__in=[333, 888, 999]).exclude(rts_status=2)
        for ship in ships:
            history_update(ship, 55, request, "Bag ({0}) scanned at DC".format(bag_number))

        sucess_bags = ""
        mismatch_bags = ""
        return render_to_response("hub/inscan_bag_data.html",
		    {"bag":bag[0], "connection":connection, 
		    'sucess_bags':sucess_bags, 'mismatch_bags':mismatch_bags},
		    context_instance = RequestContext(request))
    else:
        # bags to show in bag report area
        scanned_bags = Bags.objects.filter(
            destination_id=dest, added_on__gte=before, bag_status=8
        ).annotate(num_shipments=Count('shipments')).filter(
            num_shipments__gt=0).order_by('-id')
        # connections to show in connection area
        conn = Connection.objects.filter(
            destination_id=dest, added_on__gte=before, 
            connection_status__in=[1,4]
        ).annotate(num_bags=Count('bags')).filter(num_bags__gt=0)
        conn_bags = {}
        for cid in conn:
            c = Connection.objects.filter(id=cid.id).annotate(
                ship_count=Count('bags__shipments')).filter(ship_count__gt=0)
            if c:
		conn_bags[c[0]]=c[0].ship_count
    
    return render_to_response(
        "delivery/inscan_bag.html",
       {"bags":scanned_bags, "connection":conn, "conn_bags":conn_bags},
       context_instance = RequestContext(request))

def bag_tallied(request):
    connection = Connection.objects.filter(
        destination=request.user.employeemaster.service_centre, 
        added_on__gte=before, connection_status=1).only('id')
    for conn in connection:
        bags = conn.bags.filter(bag_status=8).exclude(status_type=3)
        # update shortage bags
        bags.annotate(num_shipments=Count('shipments'))\
	    .filter(num_shipments__gt=0).update(status_type=2)
        # update closed bags
        bags.annotate(num_shipments=Count('shipments'))\
	    .filter(status_type=1, num_shipments=0).update(bag_status=10)
    scanned_bags = Bags.objects.filter(
        destination=request.user.employeemaster.service_centre, 
        #added_on__gte=before, bag_status=8).annotate(
        updated_on__gte = before, bag_status=8).annotate(
        num_shipments=Count('shipments')).filter(num_shipments__gt=0).order_by('-id')
    return render_to_response(
        "hub/bag_tallied.html", {"bags":scanned_bags},
        context_instance=RequestContext(request))

def connection_tallied(request):
    connection = Connection.objects.filter(
        destination=request.user.employeemaster.service_centre, 
        added_on__gte=before, connection_status__in=[1, 4]).only('id')
    conn_bags = {}
    for conn in connection:
        bags = conn.bags.filter(bag_status=8).exclude(status_type=3)
        # update shortage bags
        bags.annotate(num_shipments=Count('shipments'))\
            .filter(num_shipments__gt=0).update(status_type=2)
        # update closed bags
        bags.annotate(num_shipments=Count('shipments'))\
            .filter(status_type=1, num_shipments=0).update(bag_status=10)
        unscaned_bags = conn.bags.filter(bag_status=2).exclude(status_type=3).values_list('bag_number', flat=True)
        if unscaned_bags:
            conn_bags[conn.id] = ', '.join(unscaned_bags)
    return render_to_response(
        "hub/connection_tallied.html", {"conn_bags":conn_bags},
        context_instance=RequestContext(request))

@csrf_exempt
def inscan_shipment(request):
    '''DeBagging Shipments'''
    dest = request.user.employeemaster.service_centre_id
    if request.POST:
        awb_num = request.POST['awb_num']
        try:
            int(awb_num)
        except ValueError:
           return HttpResponse("1")
        ship = Shipment.objects.filter(airwaybill_number=int(awb_num)).select_related(
               'service_centre__center_name','shipper__name').only('id','added_on',
               'expected_dod','status','airwaybill_number','order_number','inscan_date',
               'shipper__name','shipper__code','consignee','actual_weight',
               'service_centre__center_name','pincode','pieces','collectable_value','status_type'
        ).exclude(rts_status=2).exclude(status=9).exclude(reason_code__code__in = [333, 888, 999]).exclude(status__in=[31,33])
        if not ship:
            return HttpResponse("1")
        shipment = ship[0]
        if (shipment.status in [7,8,9,32]) :
            if shipment.reason_code:
                if shipment.reason_code.code not in [311]:
                    return HttpResponse("Shipment at Outscan/Status Update, cannot be inscanned!!")
            else: 
                return HttpResponse("Shipment at Outscan/Status Update, cannot be inscanned!!")
        if not shipment.order_price_set.filter():
            if not shipment.inscan_date:
                ship.update(inscan_date=now)
            price_updated(shipment)
        
        bags = list(shipment.bags_set.all())
        bag_num = ""
        if bags:
           bags = bags[-1]
           bag_num = bags.bag_number
        status_type=0
        if shipment.service_centre_id <> dest:
                status_type = 5
        else:
                status_type = 1
        if not bags:
            if shipment.status <> 6:
                  status_type = 5
        
        s = ship.update(status=6, status_type=status_type, current_sc = dest, updated_on = now)
        #if status_type == 1 and bags.bag_status in [2,7]:
        if bags and status_type != 5 and bags.bag_status in [1,2,6,7]:
            Bags.objects.filter(pk=bags.id).update(bag_status=8)
            
        if s:
           history_update(shipment, 6, 
                     request, "Debag Shipment at Delivery Centre from Bag Number %s"%(bag_num))
        else:
           return HttpResponse("Shipment not updated, please contact site admin")
        if shipment.status_type <> 5:
            if bags:
               if bags.shipments.all():
                  bags.shipments.remove(shipment)
               if not bags.shipments.all():
                  Bags.objects.filter(pk=bags.id).update(bag_status=10)
                  update_bag_history(bags, employee=request.user.employeemaster, 
                       action="shipments debagged at Destination SC (Shipments Scanned: %s)"%(bags.ship_data.count()),
                       content_object=bags, sc=request.user.employeemaster.service_centre, status=17)

        shipment = ship[0]
       # total_records = Shipment.objects.filter(status__in=[5,6], current_sc_id=dest).count()
       # success_count = Shipment.objects.filter(current_sc_id=dest, status=6, status_type=1).count()

       # mismatch_count = Shipment.objects.filter(current_sc_id=dest, status=6, status_type__in=[2,3,4,5]).count()
        total_records = ""
        success_count = ""
        mismatch_count = ""
        return render_to_response("service_centre/shipment_data.html",
                                  {'a':shipment,
                                   'status':"2",
                                   'total_records':total_records,
                                   'sucess_count':success_count,
                                   'mismatch_count':mismatch_count
              })
    else:
        shipment = Shipment.objects.filter(
            status=6, current_sc_id=dest
        ).exclude(status_type=0).exclude(rts_status=2).exclude(shipper_id=12).exclude(
            reason_code__code__in=[333, 888, 999]).select_related(
            'service_centre__center_name', 'shipper__name'
        ).only(
            'airwaybill_number','order_number','shipper__name',
            'shipper__code','consignee','actual_weight','service_centre__center_name',
            'pincode','pieces','collectable_value','status_type'
        )
        total_records = Shipment.objects.using('local_ecomm').filter(status__in = [5,6], current_sc_id = dest).count()
        success_count = Shipment.objects.using('local_ecomm').filter(status_type = 1, current_sc_id = dest, status = 6).count()
        mismatch_count = Shipment.objects.using('local_ecomm').filter(status = 6, current_sc_id = dest, status_type = 4).count()
        return render_to_response(
            "delivery/inscan_shipment.html",
            {'shipment':shipment,
             'total_records':total_records,
             'success_count':success_count,
             'mismatch_count':mismatch_count},
            context_instance = RequestContext(request))

def outscan(request):
    before = now - datetime.timedelta(days=3)
    '''Outscan Delivery'''
    origin_sc = request.user.employeemaster.service_centre_id
    if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
        outscan = DeliveryOutscan.objects.filter(origin_id = origin_sc).\
                  filter(Q(added_on__range=(before, now)) | Q(status = 0)).\
                  order_by("-id").prefetch_related('shipments').\
                  select_related('employee_code__employee_code').\
                  only('employee_code__employee_code','id','route','status')
    else:
        outscan = DeliveryOutscan.objects.filter(Q(added_on__range=(before, now))|Q(status=0)).\
                  order_by("-id").prefetch_related('shipments').\
                  select_related('employee_code__employee_code').\
                  only('employee_code__employee_code','id','route','status')
    em = EmployeeMaster.objects.filter(service_centre=request.user.employeemaster.service_centre, user_type = "Staff").exclude(staff_status=2)
    return render_to_response("delivery/outscan.html",
                              {'outscan':outscan,
               #                'service_centre':service_centre,
                               'origin_sc':origin_sc,
                               'em':em },
                               context_instance = RequestContext(request))

@csrf_exempt
def outscan_batch(request):
    '''Creating Outscan Batch'''
    employee_code = request.POST['emp_code']
    employee_code = EmployeeMaster.objects.filter(employee_code=employee_code)
    if employee_code:
       employee_code = employee_code[0]
    else:
       return HttpResponse("Incorrect") 
    route = request.POST['route']
    mobile = request.POST['mobile']
    outscan = DeliveryOutscan.objects.create(
        employee_code=employee_code,mobile_no=mobile,
        route=route, origin_id=request.user.employeemaster.service_centre_id)

    return render_to_response(
        "service_centre/connection_data.html",
        {"a":outscan, 'status':'2'},
        context_instance=RequestContext(request))

@csrf_exempt
def include_shipment(request, oid):
    '''Including Shipment in Outscan Batch'''
    dest = request.user.employeemaster.service_centre_id
    outscan = DeliveryOutscan.objects.filter(id=oid).select_related(
                               'employee_code').only('id','employee_code')[0]
    if request.POST:
            awb_number = request.POST['awb']
            try:
                int(awb_number)
            except ValueError:
                return HttpResponse("Incorrect Shipment Number")
            sh = Shipment.objects.filter(airwaybill_number=awb_number)
            if sh:
               ship=sh[0]
            else:
                return HttpResponse("Incorrect Shipment Number. Please check")
            if ship.reverse_pickup and ship.status in [31,33]:
              if ship.reason_code is None  or  ship.reason_code.code not in [413,414,415,416,418,419,420,411,400,404,405,406]:
                  shipment = Shipment.objects.filter(
                      current_sc_id=dest, reverse_pickup=True, airwaybill_number=awb_number, 
                      status__in=[31,33]).exclude(rts_status=2).exclude(reason_code__code__in = [333, 888, 999]).\
                      select_related('service_centre__center_name','shipper__name').only(
                          'id', 'airwaybill_number','shipper__name','destination_city','service_centre__center_name',
                          'added_on','expected_dod','pickup')
                  if not shipment:
                    return HttpResponse("Incorrect Shipment Number ")
                  ship = shipment[0]
                  s = shipment.update(status=32 , current_sc = dest, updated_on=now)
                  if s :
                     outscan.shipments.add(ship)
                     if not DOShipment.objects.filter(shipment=ship, deliveryoutscan=outscan):
                        doshipment = DOShipment.objects.create(shipment=ship, deliveryoutscan=outscan)
                        history_update(
                            ship, 32, request, "(%s %s)(Outscan Number:%s)"%(outscan.employee_code.firstname,outscan.employee_code.lastname, outscan.id))
                  else:
                      return HttpResponse("Shipment not updated, please contact site admin")
                  return render_to_response(
                      "service_centre/shipment_bagging_data_os.html",
                      {'shipment':ship}, context_instance=RequestContext(request))
            else:
                shipment = Shipment.objects.filter(service_centre_id= dest, current_sc_id=dest,
                     airwaybill_number=awb_number, status__in=[6,8]).exclude(rts_status=2).exclude(
                     reason_code__code__in = [333, 888, 999]).select_related(
                     'service_centre__center_name','shipper__name').only('id',
                      'airwaybill_number','shipper__name','destination_city',
                      'service_centre__center_name', 'added_on','expected_dod','pickup')
                if not shipment:
                     return HttpResponse("Incorrect Shipment Number")
                ship = shipment[0]#obj getting lost after .update
                s = shipment.update(status=7, current_sc = dest, updated_on=now)
                if s:
                   outscan.shipments.add(ship)
                   if not DOShipment.objects.filter(shipment=ship, deliveryoutscan=outscan):
                      doshipment = DOShipment.objects.create(shipment=ship, deliveryoutscan=outscan)
                      history_update(ship, 7, request, "(%s %s)(Outscan Number:%s)"%(outscan.employee_code.firstname,
                      outscan.employee_code.lastname, outscan.id))

                else:
                    return HttpResponse("Shipment not updated, please contact site admin")
                return render_to_response(
                    "service_centre/shipment_bagging_data_os.html",
                    {'shipment':ship}, context_instance=RequestContext(request))
    else:
       shipment = outscan.shipments.using('local_ecomm').all().select_related('service_centre__center_name','shipper__name').\
               only('id','pickup','airwaybill_number','shipper__name','destination_city',
               'service_centre__center_name','added_on')
       shipment_count = shipment.count()

       return render_to_response("delivery/include_shipment.html",locals(),
                               context_instance=RequestContext(request))


@csrf_exempt
def delink_shipment(request, oid):
    '''Delinking Shipment in Outscan Batch'''
    outscan  =  DeliveryOutscan.objects.filter(id = oid).only('id')[0]
    dest = request.user.employeemaster.service_centre_id
    if request.POST:
        awb_number = request.POST['awb']
        shipment = Shipment.objects.filter(airwaybill_number = awb_number , status = 7, current_sc_id=dest).\
                   only('added_on','expected_dod','id')
        if not shipment:
            return HttpResponse("Incorrect Shipment Number")
        ship = shipment[0]
        s = shipment.update(status = 6)
        if s:
        #   history_update(ship, 6, request, "Delinked from Outscan")
           outscan.shipments.remove(ship)
           dos = ship.doshipment_set.filter(deliveryoutscan=outscan).only('id')
          # dos =  shipment.doshipment_set.get(deliveryoutscan=outscan)
           dos.delete()
           if outscan.shipments.filter(id=ship.id):
              ship.doshipment_set.filter(deliveryoutscan=outscan).update(status=2)
           history_update(ship, 6, request, "Delinked from Outscan")
        else:
             return HttpResponse("Shipment not updated, please contact site admin")
        return HttpResponse("Shipment removed Sucessfully")


    else:
        shipment = outscan.shipments.using('local_ecomm').all().select_related('service_centre__center_name','shipper__name').\
                   only('id','pickup','airwaybill_number','shipper__name','destination_city',
                   'service_centre__center_name','added_on')
        shipment_count = shipment.count()
        return render_to_response("delivery/delink_shipment.html",locals(),
                               context_instance=RequestContext(request))

def delivery_sheet(request, oid):
    '''Delivery Sheet for Outscan'''
    outscan = DeliveryOutscan.objects.get(id = oid)
    drs_shipment = get_model('service_centre', 'DeliveryOutscan_shipments')
    ship = drs_shipment.objects.filter(
        deliveryoutscan_id=oid
    ).order_by('-id')
    shipment = [a.shipment for a in ship]
    ship_sum = outscan.shipments.filter(
        product_type = "cod"
    ).exclude(rts_status=1)
    shipment_sum  =  ship_sum.aggregate(
        Sum('collectable_value')
    )['collectable_value__sum']
    print_no = request.GET.get('print', 0)

    if not int(print_no):
        return render_to_response(
            "delivery/delivery_sheet.html",
            {
                'outscan':outscan,
                'shipment':shipment,
                'oid':oid,
                'shipment_sum':shipment_sum,
            },
            context_instance=RequestContext(request)
        )
    elif int(print_no) == 1:
        # pisa
        return write_pdf("delivery/print_delivery_sheet.html",
                         {
                             'pagesize': 'A4',
                             'outscan':outscan,
                             'shipment':shipment,
                             'oid':oid,
                             'shipment_sum':shipment_sum,
                          })

    elif int(print_no) == 2:
        return render_to_response(
            "delivery/delivery_challan.html",
            {
                'outscan':outscan,
                'shipment':shipment,
                'oid':oid,
                'shipment_sum':shipment_sum,
            },
            context_instance=RequestContext(request)
        )
    elif int(print_no) == 3:
        text = render_to_string("delivery/delivery_challan_txt.html",
                {
                    'outscan':outscan, 
                    'shipment':shipment,
                    'oid':oid,
                    'shipment_sum':shipment_sum,
                },
                context_instance = RequestContext(request)
        )
        response =  HttpResponse("%s"%text, content_type="text/plain", 
                mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename=delivery_challan.txt'
        return response

@csrf_exempt
def close_outscan(request):
    '''Closing Outscan'''
    outscan_id = request.POST['outscan_id']
    DeliveryOutscan.objects.filter(id=outscan_id).update(status=1)
    outscan = DeliveryOutscan.objects.get(id=outscan_id)
    outscan_update_for_cash_tally(outscan.id)
    for s in outscan.shipments.all():
       if s.rts_status == 0 and s.rto_status == 0:
           add_awb(s.airwaybill_number)
    drs_shipment = get_model('service_centre', 'DeliveryOutscan_shipments')
    ships = drs_shipment.objects.filter(deliveryoutscan_id=outscan_id).order_by('-id')
    for order_number, sh in enumerate(ships, start=1):
        OutscanShipments.objects.get_or_create(outscan=outscan_id, awb=sh.shipment.airwaybill_number, serial=order_number)
    return HttpResponse("Success")

@csrf_exempt
def status_update(request):
    '''Status Update for Shipment'''
    before1 = now - datetime.timedelta(days=1)
    dest = request.user.employeemaster.service_centre_id
    if request.POST:
        data_entry_emp = request.POST['data_entry_emp']
        delivery_emp = request.POST['delivery_emp']
        awb = request.POST['awbu'] or request.POST['awbd']
        reason_code = request.POST['reason_code']
        recieved_by = request.POST['recieved_by']
        remarks = request.POST.get('remarks','')
        time = request.POST['time']
        date = request.POST['date']
        ajax_field = request.POST['ajax_num']
        pod_reversal = 0
        if not (data_entry_emp and delivery_emp):
             return HttpResponse("Incorrect Employee Code")
        data_entry_emp = EmployeeMaster.objects.filter(employee_code=int(data_entry_emp)).only('id')
        delivery_emp = EmployeeMaster.objects.filter(employee_code=delivery_emp).only('id')
        if delivery_emp and data_entry_emp:
           delivery_emp = delivery_emp[0]
           data_entry_emp = data_entry_emp[0]
        else:
           return HttpResponse("Incorrect Employee Code")
        try:
             reason_code = ShipmentStatusMaster.objects.get(id = int(reason_code))
        except:
             vals=reason_code.split('-')
             reason_code = ShipmentStatusMaster.objects.get(code = int(vals[0]))  
        dat = dateutil.parser.parse(date)
        date = dat.strftime("%Y-%m-%d")

      #  ship = Shipment.objects.filter(airwaybill_number = int(awb), status__in = [7,8,9], 
#        ship = Shipment.objects.filter(airwaybill_number = int(awb),
#                current_sc_id=dest).only('status','status_type','added_on','expected_dod')
        ship = Shipment.objects.filter(airwaybill_number = int(awb)
                ).only('status','status_type','added_on','expected_dod').exclude(status=9).exclude(reason_code__code__in = [333, 888, 999]).exclude(rts_status = 2)

        if not ship:
            return HttpResponse("Incorrect Shipment Number 1")
        shipment = ship[0]
        if reason_code.id not in [52]:
           if shipment.current_sc_id <> dest: 
                    return HttpResponse("Incorrect Shipment Number 2")
        else:
           bags = list(shipment.bags_set.all())
           if bags:
              bags = bags[-1] 
              bags.shipments.remove(shipment)
       # shipment = ship[0]
        if shipment.status in [7,8,9]:
          if not shipment.deliveryoutscan_set.latest("added_on").status:
            return HttpResponse("Please Close Outscan First")
        if reason_code.code == 666:
             ship.update(sdl=1)
             sdl_charge(shipment)

        if (request.POST['awbd'] <> ""):#Delivered
            if shipment.status == 32 and shipment.reverse_pickup == True :
               reason_code = ShipmentStatusMaster.objects.get(code=400)
               su_status =1
               shipment_status=2
               dos_status=1
               resp=False
               if request.POST['dim_breadth'] and request.POST['dim_height'] and request.POST['dim_length'] and request.POST['dim_wt']:
                   dim_breadth=float(request.POST['dim_breadth'])
                   dim_height=float(request.POST['dim_height'])
                   dim_length=float(request.POST['dim_length'])
                   dim_wt=float(request.POST['dim_wt'])
                   if isinstance(dim_breadth,float) or isinstance(dim_breadth,int) :
                       if isinstance(dim_height,float) or isinstance(dim_height,int ) :
                         if isinstance(dim_length,float)  or isinstance(dim_length,int ) :
                           if isinstance(dim_wt,float) or isinstance(dim_wt,int) :
                                  ish=Shipment.objects.filter(airwaybill_number=shipment.airwaybill_number).update(length=dim_length,breadth=dim_breadth,height=dim_height,actual_weight=dim_wt)

               reason=ShipmentStatusMaster.objects.get(code=400)
               ReverseShipment.objects.filter(shipment=shipment).update(status=1)
            else:
              
                if shipment.status <> 7:
                   return HttpResponse("Please Outscan the shipment")

                su_status = 2
                shipment_status = 9
                dos_status = 1
        else:
            if shipment.status == 9:#POD reversal
                if reason_code.id <> 44:
                    return HttpResponse("For updating this shipment enter the reason code as 202")
                shipment_status =7
                su_status = 1
                dos_status = 0
                pod_reversal = 1
            else:#Undelivered  
              if shipment.status == 32 and shipment.reverse_pickup == True :
                   su_status = 1
                   shipment_status = 33
                   dos_status = 2
                   if reason_code.code in [413,414,415,416,418,419,420,411,400,404,405,406]:
                       ReverseShipment.objects.filter(shipment=shipment).update(status=2)
                   #ReverseShipment.objects.filter(shipment=shipment).update(reason_code=reason_code)
              else:
                 if shipment.status not in [7,8,32]:
                    if reason_code.id not in [52]:
                      return HttpResponse("For updating this shipment enter the reason code as 311")
                 su_status = 1
                 shipment_status = 8
                 dos_status = 2
              #DOShipment.objects.filter(id=doss.id).update(status=dos_status, updated_on=now)
        ajax_check = StatusUpdate.objects.filter(ajax_field=ajax_field)
        if ajax_check:
              return HttpResponse("Incorrect Shipment Number 3")
        su = StatusUpdate.objects.get_or_create(shipment = shipment, data_entry_emp_code = data_entry_emp, delivery_emp_code = delivery_emp, reason_code = reason_code, date = date, time = time, recieved_by = recieved_by, status = su_status, origin = request.user.employeemaster.service_centre, remarks=remarks,ajax_field=ajax_field) #status update
        if shipment.status in [7,8,9,3,32,33]: 
           doss = shipment.doshipment_set.filter(deliveryoutscan__status=1).latest('added_on') #doshipment update
           if doss:
                if pod_reversal:
                   if doss.deliveryoutscan.cod_status == 1:
                        return HttpResponse("COD closed, Please contact Accounts")
                   DeliveryOutscan.objects.filter(id=doss.deliveryoutscan_id).update(collection_status=0)
                DOShipment.objects.filter(id=doss.id).update(status=dos_status, updated_on=now)

        altinstructiawb = InstructionAWB.objects.filter(batch_instruction__shipments__current_sc_id = dest, status = 0, batch_instruction__shipments=shipment).update(status=1)
        if pod_reversal:
           #su_undel = StatusUpdate.objects.filter(shipment=shipment, status=2).update(status=3) #no need to change hist to be maintained
           su_6 = deepcopy(su)
           su_6[0].status = 6
           su_6[0].added_on = now
           su_6[0].save()   
#      try: #samar: not sure what this is for, will need to check out
#                su_undel = StatusUpdate.objects.filter(shipment=shipment, status=2).update(status=3)
#        except:
#                pass

        s = ship.update(status=shipment_status, reason_code=reason_code, updated_on=now, current_sc=dest) #shipment update
        if shipment_status == 9:
            shipment.shipext.delivered_on = now
            shipment.shipext.save()
        if reason_code.code == 311:
           shipment_mail(shipment)

        if s:
           history_update(shipment, shipment_status, request, "", reason_code) #history update
        else:
           return HttpResponse("Shipment not updated, please contact site admin")
        status_update = StatusUpdate.objects.using('local_ecomm').filter(origin_id = dest,date__range=(before,now)).select_related('shipment__airwaybill_number','reason_code').only('id','status','remarks','shipment__airwaybill_number','reason_code')
    #    delivered_count = status_update.filter(date__range=(before1,now)).count()
    #    undelivered_count = status_update.filter().exclude(shipment__rts_status=2).exclude(shipment__rto_status=1).count()
        delivered_count = ""
        undelivered_count = ""
        outscan = shipment.deliveryoutscan_set.latest('id')
        #outscan.update_amount_tobe_collected()
        #outscan.update_unupdated_count()
        outscan_update_for_cash_tally(outscan.id)
        ShipmentExtension.objects.filter(
            shipment=shipment, cash_tally_status=None
        ).update(
            cash_tally_status=0, cash_deposit_status=0,collected_amount=0, 
            partial_payment=False)

        return render_to_response(
            "delivery/status_update_data.html",
            {'status_update':su[0], 'delivered_count':delivered_count,
             'undelivered_count':undelivered_count})

    else:
           status_update = [] #StatusUpdate.objects.using('local_ecomm').filter(origin_id = dest, date__range=(before,now)).select_related('shipment__airwaybill_number','reason_code').only('id','status','remarks','shipment__airwaybill_number','reason_code')
           delivered = [] #status_update.filter(date__range=(before1,now))
           undelivered = [] #status_update.filter(shipment__rts_status=0)
           delivered_count = 0 #delivered.only('id').count()
           undelivered_count = 0 #undelivered.only('id').count()
           reason_code  =  ShipmentStatusMaster.objects.filter().exclude(id=53).exclude(code__in=[200,777,213,207,230,666,202,229,216,226])
           return render_to_response(
               "delivery/status_update.html", locals(), 
               context_instance=RequestContext(request))

@csrf_exempt
def rts_pod_update(request):
     time = request.POST['pickup_time']
     date = request.POST['pickup_date']
     oid = request.POST['os_id']
     sr_f = request.POST['sr_no_f']
     sr_t = request.POST['sr_no_t']
     recv = request.POST['recv']
     employee_code = request.POST['emp_code']
     employee_code = EmployeeMaster.objects.get(employee_code=int(employee_code))
     reason_code = ShipmentStatusMaster.objects.get(id=1)
     shipments = OutscanShipments.objects.filter(outscan = oid, serial__range = (sr_f, sr_t))
     ship = [a.awb for a in shipments]
     shipments = Shipment.objects.filter(airwaybill_number__in = ship)
     for shipment in shipments:
          if shipment.rts_status:
             su = StatusUpdate.objects.get_or_create(shipment = shipment, data_entry_emp_code = employee_code, delivery_emp_code = employee_code, reason_code = reason_code, date = date, time = time, recieved_by = recv, status = 1, origin = request.user.employeemaster.service_centre)
             altinstructiawb = InstructionAWB.objects.filter(batch_instruction__shipments__current_sc = request.user.employeemaster.service_centre, status = 0, batch_instruction__shipments=shipment).update(status=1)
             doss = shipment.doshipment_set.filter(deliveryoutscan__status=1).update(status=1, updated_on=now)
             s = Shipment.objects.filter(id=shipment.id).update(status=9, reason_code=reason_code, updated_on=now, current_sc=request.user.employeemaster.service_centre) #shipment update
             if s:
                history_update(shipment, 9, request, "", reason_code) #history update
             else:
               return HttpResponse("Shipment not updated, please contact site admin")
          else:
            return HttpResponse("NON RTS airwaybills found")
     return HttpResponse("Shipments Updated Sucessfully")


@csrf_exempt
def sal_tally(request):
    '''SAL Tally'''
    origin = request.user.employeemaster.service_centre_id 
    if request.POST:
        employee_code = request.POST['emp_code']
        employee_code = EmployeeMaster.objects.get(employee_code=int(employee_code))
        date = request.POST['date']
        if ShipmentAtLocation.objects.filter(origin = origin, status=0):
            return HttpResponse("Please close existing SAL!")
        sal  =  ShipmentAtLocation.objects.create(
            data_entry_emp_code=employee_code, date=date, origin_id=int(origin)
        )
        # Please have this tested by sravan.
        sal_undelivered = Shipment.objects.filter(
            (Q(status__in= [6,7,8,0,1,2])) & Q(current_sc_id = origin)
        ).exclude(shipper_id=12).exclude(rts_status=2).exclude(
            reason_code_id__in=[46,4,6,5,52,53, 14,37,1,55]
        ).only('id')
        #sal.total_undelivered_shipment.add(*(list(sal_undelivered)))        
        for sal_ship in sal_undelivered:
            sal.total_undelivered_shipment.add(sal_ship)
        return render_to_response(
            "delivery/sal_data.html",
            {'a':sal}, context_instance=RequestContext(request))

    else:
        #sal  =  ShipmentAtLocation.objects.filter(origin_id = origin).filter(Q(status=0) | Q(date__range=(before, now))).order_by("-id")
        sal  =  ShipmentAtLocation.objects.filter(origin_id = origin).filter(Q(status=0)).order_by("-id")
        for a in sal:
           if a.status == 0:
             for ship in a.total_undelivered_shipment.all().iterator():
                 if ship.reason_code_id == 1 or ship.status in [3, 4,5]:
                     a.total_undelivered_shipment.remove(ship)

        return render_to_response("delivery/sal_tally.html",
                              {'sal':sal},
                               context_instance = RequestContext(request))

@csrf_exempt
def include_shipment_sal(request, sid):
    '''Include Shipment in SAL batch'''
    sal  =  ShipmentAtLocation.objects.get(id = sid)
    if request.POST:
        awb_number =  request.POST['awb']
        stype = request.POST['scan_type']  
        try:
           int(awb_number)
        except ValueError:
            return HttpResponse("Invalid Shipment")
        shipment = Shipment.objects.filter(airwaybill_number = awb_number, status__in=[6,8], current_sc=request.user.employeemaster.service_centre).select_related('service_centre__center_name','shipper__name').only('id','pickup','airwaybill_number','shipper__name','destination_city','service_centre__center_name','added_on','expected_dod','id','status','return_shipment').exclude(reason_code_id__in=[46,4,6,52,53,14,37,1,55]).exclude(rts_status=2)
        if shipment:
                shipment = shipment[0]
		if ((shipment.status in [6,7,8]) or (shipment.return_shipment and shipment.status in [0,1,2,3,4,5])):
	            if shipment.status == 8:
                             su = StatusUpdate.objects.filter(shipment=shipment)
                             if su:
                                su = su.latest('added_on')
                                su.id = None
                                su.added_on = now
                                su.status = 1
                                su.ajax_field = None
                                su.date = now.date()
                                su.time = now.time()
                                su.save()
                             history_update(shipment, 8, request, "Undelivered Shipment (SAL Tally)", su.reason_code)
                    try:
                        SALScanType.objects.create(sal=sal, shipment=shipment, sc = request.user.employeemaster.service_centre, scan_type=int(stype), emp=request.user.employeemaster)
               	        sal.scanned_shipments.add(shipment)# TODO: history to be added for this
                    except IntegrityError:
                        pass
                    return render_to_response("delivery/include_sal_data.html",
					  {'shipment':shipment,
					   },
					   context_instance=RequestContext(request))
        else:
            return HttpResponse("Invalid Shipment")
    else:
        shipment  =  sal.scanned_shipments.using('local_ecomm').all().select_related('service_centre__center_name','shipper__name').only('id','pickup','airwaybill_number','shipper__name','destination_city','service_centre__center_name','added_on')
        shipment_count  =  shipment.count()
        return render_to_response("delivery/include_shipment_sal.html",
                                  {'sal':sal,
                                   'shipment':shipment,
                                   'shipment_count':shipment_count,
                                   'sid':sid,},
                                   context_instance = RequestContext(request))

@csrf_exempt
def close_sal(request):
    '''Closing Outscan'''
    sal_id = request.POST['sal_id']
    sal = ShipmentAtLocation.objects.filter(id = sal_id)
    sal_scanned = sal[0].scanned_shipments.all().only('id')
    if len(sal_scanned) == len(sal[0].total_undelivered_shipment.all().only('id')):
        status = 1
    else:
        status = 2
    sal.update(status=status)
    return HttpResponse("Success")


def sal_excel_download(request, sid):
    file_name = "/SAL_%s.xlsx" % (now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()

    sal = ShipmentAtLocation.objects.get(pk=int(sid))

    # These are scanned shipments
    tss = sal.scanned_shipments.all().only('airwaybill_number','status','updated_on')
    all_scanned = [a.airwaybill_number for a in tss]

    # These are all undelivered shipments
    tus = sal.total_undelivered_shipment.all().only('airwaybill_number')
    all_undelivered = (a.airwaybill_number for a in tus)

    # the airwaybill_numbers in all_undelivered are unscanned
    # if it is not present in all_scanned
    all_unscanned = list(set(all_undelivered) - set(all_scanned))

    count = 1

    sheet.set_column(0,7, 20)
    sheet.write(0, 3, "Shipment at Location")
    sheet.write(2, 2, "SAL Tally id : %s " % sid)
    sheet.write(3, 2, "Date : %s " % sal.date.strftime('%d-%m-%Y'))

    sheet.write(4, 3, "Verified/Unverified")
    sheet.write(4, 4, 'Current Status')
    sheet.write(4, 5, 'Last Updated On')
    # write to excel
    for row, val in enumerate(tss, start=5):
        sheet.write(row, 2, val.airwaybill_number)
        sheet.write(row, 3, 'Verified')
        sheet.write(row, 4, get_internal_shipment_status(val.status))
        sheet.write(row, 5, str(val.updated_on))

    next_row = 5 + len(all_scanned)

    s = Shipment.objects.filter(airwaybill_number__in=all_unscanned).only('airwaybill_number','status','updated_on')
    for row, val in enumerate(s, start = next_row):
        sheet.write(row, 2, str(val.airwaybill_number))
        sheet.write(row, 3, 'Unverified')
        sheet.write(row, 4, get_internal_shipment_status(val.status))
        sheet.write(row, 5, str(val.updated_on))

    workbook.close()
    return HttpResponseRedirect("/static/uploads/%s"%(file_name))

def list_shipments(request):
    s3 = Shipment.objects.using('local_ecomm').filter((Q(status__in = [6,7,8]) | Q(return_shipment__in=[1,2,3]) &Q(status__in=[0,1,2])) &Q(current_sc = request.user.employeemaster.service_centre)).exclude(rts_status=2).exclude(reason_code_id__in=[46,4,6,5,52,53,14,3,1,7,55]).exclude(rts_status=2).select_related('reason_code__code_description').only('id','airwaybill_number','status','updated_on','reason_code__code_description')
    return render_to_response("delivery/list_undelivered_shipment.html",
                                {'total_undel_shipment':s3},
                               context_instance = RequestContext(request))

@csrf_exempt
def cash_tally(request):
    from .forms import CreditPaymentAwbDetailsForm, CreditDateForm, CreditPaymentDetailForm
    from .forms import CreditAwbDetailFormSet, CreditcardDeliveryForm
    origin = request.user.employeemaster.service_centre_id
    outscans = DeliveryOutscan.objects.get_incomplete_closures_for_sc(origin=origin)

    shipments = DeliveryOutscan.objects.get_cash_tally_shipments(origin=origin)

    success_amount_collected = 0
    #success_amount_collected = shipments.aggregate(Sum('collectable_value'))['collectable_value__sum']
    success_amount_collected = success_amount_collected if success_amount_collected else 0
    ppd_ship_ids = list(ShipmentExtension.objects.filter(upd_product_type='ppd', cash_deposit_status=0,
            shipment__current_sc=origin).values_list('shipment', flat=True))
    ppd_shipments = Shipment.objects.filter(id__in=ppd_ship_ids).values(
        'id', 'airwaybill_number', 'pieces', 'collectable_value', 'consignee', 'shipext__collected_amount')

    outscans_list = outscans.values_list('id', flat=True)
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    coddeposits = CODDeposits.objects.filter(Q(origin_id=origin), Q(deposited_on__gte=yesterday) | Q(status=0)).order_by('-id')
    empcode = request.user.employeemaster.employee_code
    service_centre = request.user.employeemaster.service_centre 

    # forms for credit card payment
    awb_details_form = CreditPaymentAwbDetailsForm()
    date_form = CreditDateForm(initial={'system_date': datetime.datetime.today().date()})
    payment_detail_form = CreditPaymentDetailForm()
    awb_formset = CreditAwbDetailFormSet()
    credit_form = CreditcardDeliveryForm()

    return render_to_response(
        "delivery/cash_tally.html",
        {'codd':coddeposits,
        'unclosed_ships': shipments,
        'ppd_shipments':ppd_shipments,
        'success_amount_collected':success_amount_collected,
        'outscans_list': outscans_list,
        'outscans':outscans,
        'credit_form': credit_form,
        'awb_details_form': awb_details_form,
        'date_form': date_form,
        'payment_detail_form': payment_detail_form,
        'awb_formset': awb_formset,
        'empcode': empcode, 'service_centre': service_centre},
        context_instance = RequestContext(request))

@csrf_exempt
def update_shipment_collected_value(request):
    if request.POST:
        ship_id = request.POST['id']
        amount_collected = request.POST['value']
        origin = request.user.employeemaster.service_centre
        collected_amount = update_shipment_collected_amount(ship_id, amount_collected, sc=origin)

        if collected_amount == None:
            s = Shipment.objects.get(id=ship_id)
            last_collection = CashTallyHistory.objects.get_last_collection(shipment=s)
            json = simplejson.dumps({'success':False,
                'message':'Amount greater than pending amount!',
                'last_collection': last_collection})
            return HttpResponse(json, mimetype='application/json')
        else:
            s = Shipment.objects.get(id=ship_id)
            collectable_value = s.collectable_value
            ship_collected_amount = s.shipext.collected_amount
            last_collection = CashTallyHistory.objects.get_last_collection(shipment=s)
            json = simplejson.dumps({'success':True,
                'message': "Amount updated successfully",
                'pend_amount': collectable_value - ship_collected_amount,
                'last_collection': last_collection})
            return HttpResponse(json, mimetype='application/json')
    else:
        return HttpResponse('Unauthorized')

@csrf_exempt
def delivered_cash_tally(request):
    """
    POST:called when user submits all checked airwaybill numbers from daily cash tally.
    update each shipment's collected amount
    GET:called to update outscan tally after collected amount of shipments has been updated from daily cash tally.
    """
    if request.method == 'POST' and request.is_ajax():
        awbs = request.POST.getlist('awbs[]')
        origin = request.user.employeemaster.service_centre
        update_shipments_collected_amount(awbs, origin=origin)
        outscans = DeliveryOutscan.objects.get_incomplete_closures_for_sc(origin=origin)
        html = render_to_string("delivery/outscan_collections.html",
                    {'outscans': outscans},
                    context_instance = RequestContext(request))
        data = {'html': html, 'success': True, 'awbs': awbs}
    elif request.method == 'GET' and request.is_ajax():
        origin = request.user.employeemaster.service_centre
        outscans = DeliveryOutscan.objects.get_incomplete_closures_for_sc(origin=origin)
        html = render_to_string("delivery/outscan_collections.html",
                    {'outscans': outscans}, context_instance = RequestContext(request))

        data = {'html': html, 'success': True}

    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')

@csrf_exempt
def add_shipment(request):
    """Take a ppd airwaybill number from Cash tally - daily cash tally section,
        and updated its collected amount. This is a special case. There are some
        conditions like shipment must be delivered(status=9) and it should not be
        a return shipment. We update the collected amount, and upd_product_type
        in shipment extension table.
    """
    success = False
    pieces = 0
    amount = 0
    customer = ''
    pending_amount = 0
    if request.method == 'POST' and request.is_ajax():
        awb = request.POST.get('awb')
        collectable_value = request.POST.get('collectable_value')
        error_list = []
        try:
            shipment = Shipment.objects.get(airwaybill_number=awb)
            if shipment.product_type != 'ppd':
                error_list.append('Shipment is not PPD.  \n')
            if shipment.rts_status or shipment.rto_status:
                error_list.append('Return Shipment can not be updated from here.  \n')
            if not shipment.status == 9:
                error_list.append('Only Delivered Shipment can be updated from here.  \n')
            if not collectable_value:
                error_list.append('Invalid collectable amount.  \n')
            if len(error_list) == 0:
                Shipment.objects.filter(id=shipment.id).update(collectable_value=float(collectable_value))
                updated = ShipmentExtension.objects.filter(shipment=shipment).\
                        update(upd_product_type='ppd', collected_amount=float(collectable_value), cash_tally_status=1)
                success = True
                pieces = shipment.pieces
                amount = collectable_value
                customer = shipment.shipper
                pending_amount = 0

                CashTallyHistory.objects.create(shipment=shipment, current_collection=collectable_value)
                cod_ships, created = CODDepositShipments.objects.get_or_create(origin=request.user.employeemaster.service_centre, status=0)
                cod_ships.add_shipment(shipment)
                cod_ships.save()
                update_changelog(shipment, 'collectable_value', customer, request.user, collectable_value)
        except Shipment.DoesNotExist:
            error_list.append('Shipment Does Not exist, please check airwaybill number.  \n')
    else:
        success = False

    data = {'success':success, 'error_list':error_list, 'pieces':pieces,
            'customer':customer, 'pending_amount':pending_amount,
            'collectable_value':amount, 'collected_amount':collectable_value,
            'airwaybill_number':awb}
    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')

@csrf_exempt
def add_coddeposit(request):
    if request.method == 'GET' and request.is_ajax():
        origin = request.user.employeemaster.service_centre_id
        date = request.GET['date']
        if CODDeposits.objects.filter(origin_id=origin, status=0).exists():
            json = simplejson.dumps({'success':False, 'msg':"Please close existing Cash Deposit!"})
            return HttpResponse(json, mimetype='application/json')

        codd_ships = CODDepositShipments.objects.filter(origin=origin, status=0)
        if not codd_ships.exists():
            json = simplejson.dumps({'success':False, 'msg':"No Shipments to create a cod deposit!"})
            return HttpResponse(json, mimetype='application/json')
        else:
            codd_ships = codd_ships[0]

        shipments = codd_ships.shipments.all()

        coll_amt = codd_ships.get_total()
        TW = Decimal(10) ** -2
        total = Decimal(coll_amt).quantize(TW)

        codd = CODDeposits.objects.create(origin_id=origin, date=date, time=now.time(),
                deposited_on=now, total_amount=total, collected_amount=0)
        codd.cod_shipments = shipments
        codd.save()
        # coddepositshipment is a temporary table to hold the shipments which is to be added to next
        # coddeposit. So once shipment added to coddeposit, we can update its status to 1 or delete it.
        CODDepositShipments.objects.filter(id=codd_ships.id).update(status=1)
        #codd_ships.delete()
        # Query Optimized for the folllowing commented code: JV 29 Sep
        #CashTallyHistory.objects.filter(shipment__in=shipments, coddeposit=None).update(coddeposit=codd)
        for s in shipments:
            for cash_tally_hist in  CashTallyHistory.objects.filter(shipment_id=s.id):
                if cash_tally_hist:
                    #cash_tally_hist = cash_tally_hist[0]
                    if not cash_tally_hist.coddeposit: 
                         CashTallyHistory.objects.filter(id=cash_tally_hist.id).update(coddeposit=codd)

        html = render_to_string("delivery/codd_data.html", {'codd':codd}, context_instance=RequestContext(request))
        data = {'html': html, 'success': True}
        json = simplejson.dumps(data)
        return HttpResponse(json, mimetype='application/json')

@csrf_exempt
def include_shipment_codd(request, cid):
    '''Inlcude Shipment in CODD'''
    codd = CODDeposits.objects.get(id=cid)
    shipments = codd.cod_shipments.all().values('id', 'airwaybill_number',
            'collectable_value', 'shipext__collected_amount')
    return render_to_response("delivery/list_undelivered_shipment.html",
            {'shipments':shipments, 'total_amount':codd.total_amount},
                               context_instance = RequestContext(request))

def cash_denomination(request, cid):
    codd = CODDeposits.objects.get(id=int(cid))
    denomination = codd.denomination.values_list('type', 'quantity')
    d = {}
    total=0
    for a in denomination:
        d[a[0]]=a[1]
        total=  a[0]*a[1] + total
    # generating unique id for cash deposit sheet
    codd_id = CODDeposits.objects.filter(date=datetime.date.today()).only('id').count()
    codd_id_str =  '0'+str(codd_id) if codd_id < 10 else str(codd_id)
    codid = codd.origin.center_shortcode + datetime.date.today().strftime('%Y%m%d') + codd_id_str
    return render_to_response("delivery/cash_denomination.html",
            {'codd':codd, 'denomination':d, 'total':total,'codid': codid},
            context_instance = RequestContext(request))

def cash_tally_deposits(request):
    if request.method == 'POST':
        codd = request.POST['codd_id']
        codd_code = request.POST['codd_code']
        slip_number = request.POST['slip_number']
        date = request.POST['date']
        time = request.POST['time']
        bank_code = request.POST['bank_code']
        CODDeposits.objects.filter(id=int(codd)).update(slip_number=slip_number,
                date=date, time=time, bank_code=bank_code, codd_code=codd_code)
        codd = CODDeposits.objects.get(id=int(codd))
        if request.POST['1000'] <> "0":
            denom = Denomination.objects.create(type = 1000, quantity=request.POST['d1000'])
            codd.denomination.add(denom)
        if request.POST['500'] <> "0":
            denom = Denomination.objects.create(type = 500, quantity=request.POST['d500'])
            codd.denomination.add(denom)
        if request.POST['100'] <> "0":
            denom = Denomination.objects.create(type = 100, quantity=request.POST['d100'])
            codd.denomination.add(denom)
        if request.POST['50'] <> "0":
            denom = Denomination.objects.create(type = 50, quantity=request.POST['d50'])
            codd.denomination.add(denom)
        if request.POST['20'] <> "0":
            denom = Denomination.objects.create(type = 20, quantity=request.POST['d20'])
            codd.denomination.add(denom)
        if request.POST['10'] <> "0":
            denom = Denomination.objects.create(type = 10, quantity=request.POST['d10'])
            codd.denomination.add(denom)
        if request.POST['5'] <> "0":
            denom = Denomination.objects.create(type = 5, quantity=request.POST['d5'])
            codd.denomination.add(denom)
        if request.POST['1'] <> "0":
            denom = Denomination.objects.create(type = 1, quantity=request.POST['d1'])
            codd.denomination.add(denom)
        if request.POST['total']:
            codd.collected_amount = int(request.POST['total'])
            codd.save()
    return HttpResponseRedirect('/delivery/cash_tally/')

def deposit_sheet(request, cid):
    '''Deposit Sheet for CODD'''
    coddeposit = CODDeposits.objects.filter(id=cid)
    codd = coddeposit[0]
    denos = codd.denomination.values_list('type', 'quantity').order_by('-type')  #filter().order_by("-type")
    denominations = OrderedDict(denos)
    for key, val in denominations.items():
        denominations[key] = [key, val,  int(key) * int(val)]

    deposited_by = request.user.employeemaster.firstname + request.user.employeemaster.lastname
    emp_code = request.user.employeemaster.employee_code
    return render_to_response("delivery/deposit_sheet.html",
            {'codd_id':codd, 'cid':cid, 'sheet':'deposit', 'denominations':denominations, 'deposited_by':deposited_by, 'emp_code':emp_code},
            context_instance=RequestContext(request))

@csrf_exempt
def close_codd(request):
    '''Close CODD'''
    codd_id = request.POST['codd_id']
    CODDeposits.objects.filter(id=codd_id).update(status=1, deposited_on=now)

    codd = CODDeposits.objects.get(id=int(codd_id))
    codd.update_shipments_status()
    # update the codcharge related to shipments in coddeposit
    closed_ships = list(codd.cod_shipments.filter(shipext__partial_payment=False).only('id'))
    CODCharge.objects.filter(shipment__in=closed_ships).update(status=1, updated_on=now)

    # update the unupdated count of delivery outscans related to coddeposit.
    codd.update_do_unupdated_count()

    #return HttpResponse("Success")

    # get daily cash tally section details to update it
    origin = request.user.employeemaster.service_centre_id
    outscans = DeliveryOutscan.objects.get_incomplete_closures_for_sc(origin=origin)
    shipments = DeliveryOutscan.objects.get_cash_tally_shipments(origin=origin)
    #success_amount_collected = shipments.aggregate(Sum('collectable_value'))['collectable_value__sum']
    success_amount_collected = 0
    success_amount_collected = success_amount_collected if success_amount_collected else 0
    ppd_ship_ids = list(ShipmentExtension.objects.using('local_ecomm').filter(upd_product_type='ppd', cash_deposit_status=0,
            shipment__current_sc=origin).values_list('shipment', flat=True))
    ppd_shipments = Shipment.objects.using("local_ecomm").filter(id__in=ppd_ship_ids).values('id', 'airwaybill_number', 'pieces', 'collectable_value', 'consignee', 'shipext__collected_amount')
    outscans_list = outscans.values_list('id', flat=True)

    html = render_to_string("delivery/daily_cash_tally.html",
                    {'unclosed_ships': shipments, 'ppd_shipments':ppd_shipments,
                        'success_amount_collected':success_amount_collected, 'outscans_list': outscans_list},
                    context_instance = RequestContext(request))

    json = simplejson.dumps({'codd_id':codd_id, 'daily_cash_tally_html':html})
    return HttpResponse(json, mimetype='application/json')

def cash_deposit(request):
    bank_code = request.POST['bank_code']
    bank_name = request.POST['bank_name']
    amount = request.POST['amount']
    date = request.POST['date']
    time = request.POST['time']
    emp_code = request.POST['emp_code']
    emp_name = request.POST['emp_name']
    DeliveryDeposits.objects.create(bank_code=bank_code, bank_name=bank_name, amount=amount, date=date, time=time, emp_code=emp_code, emp_name=emp_name, sc=request.user.employeemaster.service_centre)
    return HttpResponseRedirect("/delivery/cash_tally/")


@csrf_exempt
def denomination(request):
    type = request.POST["type"]
    quantity=request.POST['quantity']
    cid = request.POST['codd_id']
    amt = int(type)*int(quantity)
    return HttpResponse(amt)

@csrf_exempt
def redirection(request):
    if request.method == 'GET':
        reason_code = ShipmentStatusMaster.objects.filter(code__in=[207, 230])
        service_centre = ServiceCenter.objects.all()
        return render_to_response('delivery/redirection.html',
            {'reason_code':reason_code, 'service_centre':service_centre},
            context_instance = RequestContext(request))

    elif request.POST:
        dest = request.user.employeemaster.service_centre_id
        emp_code = request.POST['emp_code']
        awbs = request.POST['awb_list']
        awb_list = str(awbs).strip().split(',')
        reason_code = request.POST['reason_code']
        sc_id = request.POST['service_centre']
        reason_code = ShipmentStatusMaster.objects.get(id=int(reason_code))
        service_centre = ServiceCenter.objects.get(id=int(sc_id))
        destination_city = service_centre.city
        pincode = int(service_centre.pincode_set.all()[0].pincode)

        wrong_awbs = []
        for awb in awb_list:

            ship = Shipment.objects.filter(airwaybill_number=awb).exclude(rts_status=2).exclude(status=9)
            if ship.exists():
                shipment = ship[0]
            else:
                wrong_awbs.append(awb)
                continue
            #    return HttpResponse("Invalid Shipment")

            if shipment.status == 7:
               wrong_awbs.append(awb)
               continue
 #              return HttpResponse("Shipment in Outscan Stage, cannot be returned!!")
            if shipment.status == 9:
               wrong_awbs.append(awb)
               continue
#               return HttpResponse("Shipment already delivered, cannot be returned!!")

            #expected_dod = get_expected_dod(service_centre)
            #expected_dod = expected_dod if expected_dod else shipment.expected_dod

            ship.update(updated_on=now, pincode=pincode, status=1, status_type=0,
                reason_code=reason_code, current_sc=dest,
                rd_status=1,  return_shipment=1,
                service_centre=service_centre)

            altinstructiawb = InstructionAWB.objects.filter(batch_instruction__shipments__current_sc_id = dest,
                status=0, batch_instruction__shipments=shipment).update(status=1)

            history_update(shipment, 17, request, "Redirection under Same Airwaybill", reason_code)
        if len(wrong_awbs):
           wawbs = [str(x) for x in wrong_awbs]
           m = ','.join(wawbs)
           msg = "Following AWB's Failed. \n {0}".format(m)
        else:
           msg = "Success"
        return HttpResponse(msg)


@csrf_exempt
def return_redirection(request, rtype):
    rd_status=0
    rto_status=0
    rts_status=0
    if rtype == '1':
       rr = "/delivery/return_redirection/1/"
       rsp = "service_centre/rtoservicecenter.html"
    elif rtype == '2':
       rr = "/delivery/return_redirection/2/"
       rsp = "hub/return_redirection.html"
    elif rtype == '3':
       rr = "/delivery/return_redirection/3/"
       rsp = "delivery/return_redirection.html"
    dest = request.user.employeemaster.service_centre_id
    if request.POST:
       #var datastring = "emp_code="+emp_code+"&awb="+awb+"&reason_code="+rc+"&redir_code="+"74";
       redir_code = request.POST['redir_code']
       emp_code = request.POST['emp_code']
       awb = request.POST['awb']
       reason_code = request.POST['reason_code']
       reason_code = ShipmentStatusMaster.objects.get(id = int(reason_code))
       if redir_code == "76":
           rd_status = 1
           return_shipment = 1
           status=1
           remarks = "Redirection under Same Airwaybill"
       elif redir_code == "74":
            rto_status = 1
            status=1
            return_shipment=2
            remarks = "Return to Origin"
       elif redir_code == "75":
           return_shipment=3
           status = 8
           rts_status = 2

       if return_shipment == 3:
          new_airwaybill=request.POST['new_awb']
          remarks = "Redirection under on new Airwaybill " + str(new_airwaybill)
          ship = Shipment.objects.filter(airwaybill_number=new_airwaybill).exclude(status=9).exclude(reason_code__code__in = [333, 888, 999]).exclude(rts_status = 2)
          if ship:
              return HttpResponse("Used Airwaybill entered, kindly recheck")

          awb_num = AirwaybillNumbers.objects.filter(airwaybill_number=new_airwaybill, status=0)
          if not awb_num:
                 return HttpResponse("Wrong airwaybill Number")
          awb_num.update(status=1)
          ref_airwaybill_number = new_airwaybill
       if rtype == '3':
          ship = Shipment.objects.filter(airwaybill_number = awb, current_sc_id=dest).exclude(rts_status=2).exclude(status=9)
       else:
          ship = Shipment.objects.filter(airwaybill_number = awb).exclude(rts_status=2).exclude(status=9)

       if ship:
               shipment = ship[0] 
               awb = shipment.airwaybill_number  
       else:
               return HttpResponse("Invalid Shipment")
       if return_shipment <> 4:
          if shipment.status == 7:
                return HttpResponse("Shipment in Outscan Stage, cannot be returned!!")
          if rtype == '3' and shipment.status <> 8:
             if return_shipment == 2:
                return HttpResponse("Please update the shipment status before proceeding.")
          if shipment.status == 9:
                return HttpResponse("Shipment already delivered, cannot be returned!!")

       if return_shipment == 1:
          service_centre = ""
          if request.POST['service_centre']:
                 service_centre = request.POST['service_centre']
                 service_centre=ServiceCenter.objects.get(id=int(service_centre))
                 destination_city=service_centre.city
                 pincode=int(service_centre.pincode_set.all()[0].pincode)
       #   else:
        #         pincode = request.POST['pincode']
         #        pincode = Pincode.objects.get(pincode=pincode)

          #       shipment.service_centre=pincode.service_center
           #      destination_city=service_centre.city
            #     pincode = pincode.pincode

       elif return_shipment == 2:
          ship.update(remark = shipment.service_centre_id)
          pincode=shipment.pickup.pincode
          if ShipperMapping.objects.filter(shipper=shipment.pickup.subcustomer_code):
                          pinc = ShipperMapping.objects.get(shipper=shipment.pickup.subcustomer_code)
                          pincode = pinc.return_pincode   
          pincode_obj = Pincode.objects.get(pincode= pincode)
          service_centre=pincode_obj.service_center
       elif return_shipment == 3:
          if shipment.rts_status == 1:
                return HttpResponse("Invalid Shipment")
          ship.update(rts_date=now, ref_airwaybill_number=ref_airwaybill_number)

          if rts_status == 2:
               ref_airwaybill_number=shipment.airwaybill_number
               if request.POST['service_centre']:
                  ref_sc = request.POST['service_centre']
                  ref_service_centre=ServiceCenter.objects.get(id=int(ref_sc))
                  ref_destination_city=ref_service_centre.city
                  ref_pincode=int(ref_service_centre.pincode_set.all()[0].pincode)
               else:
                  ref_destination_city=shipment.pickup.subcustomer_code.address.city
                  ref_pincode=shipment.pickup.subcustomer_code.address.pincode
                  if ShipperMapping.objects.filter(shipper=shipment.pickup.subcustomer_code):
                          pinc = ShipperMapping.objects.get(shipper=shipment.pickup.subcustomer_code)
            #              ref_pincode = Pincode.objects.get(pincode= pinc.return_pincode)
                          ref_pincode = pinc.return_pincode  
                  pin = Pincode.objects.get(pincode=ref_pincode)
                  ref_service_centre=pin.service_center

       #expected_dod = get_expected_dod(dest)
       #expected_dod = expected_dod if expected_dod else shipment.expected_dod
       if rts_status ==2:
           pincode = shipment.pincode
           service_centre = shipment.service_centre
           #ref_service_centre = service_centre
           #expected_dod = shipment.expected_dod
           #ref_expected_dod = expected_dod
      
       rts_status = rts_status if rts_status  else shipment.rts_status
       rd_status = rd_status if rd_status else shipment.rd_status
       rto_status = rto_status if rto_status else shipment.rto_status
       if rd_status:
            ShipmentExtension.objects.filter(shipment=shipment).update(misroute_code=reason_code)
       ship.update(updated_on=now, pincode=pincode, status=status, status_type=0, reason_code=reason_code, current_sc=dest, rd_status=rd_status, rto_status=rto_status, rts_status=rts_status, return_shipment=return_shipment, service_centre=service_centre)
      
       altinstructiawb = InstructionAWB.objects.filter(batch_instruction__shipments__current_sc_id = dest, status = 0, batch_instruction__shipments=shipment).update(status=1)
     #  if altinstructiawb:

                #    for a in altinstructiawb:
                #         a.status = 1
                #         a.save()

       history_update(shipment, 17, request, remarks, reason_code)

       if reason_code.code == 666:
                utils.update_sdl_billing(shipment)
       if rts_status == 2:
           ref_shipment = shipment
           ref_shipment.id = None
           ref_shipment.airwaybill_number = new_airwaybill
           ref_shipment.ref_airwaybill_number=awb
           ref_shipment.shipment_date=None
           ref_shipment.inscan_date=now
           ref_shipment.billing=None
           ref_shipment.sbilling=None
           ref_shipment.save()

           Shipment.objects.filter(pk=ref_shipment.id).update(status=1, rd_status=0, rto_status=0, status_type=0, return_shipment=3, rts_date=now, rts_status=1, service_centre=ref_service_centre, pincode=ref_pincode, destination_city=ref_destination_city)
           rts_pricing(ref_shipment)
           ref_shipment.set_shipment_date
           #ShipmentExtension.objects.filter(shipment__airwaybill_number=awb).update(rev_shipment=ref_shipment)
           history_update(ref_shipment, 1, request, "Returning to Shipper: Org airwaybill number: " + str(awb), reason_code)
       if rtype == '3' or rtype =='1':
            return HttpResponse("Success")
       return HttpResponseRedirect(rr)
    else:
        reason_code = ShipmentStatusMaster.objects.filter(id__in=[38,40,39,5])
        service_centre = ServiceCenter.objects.filter().exclude(center_shortcode__in = ["DEP", "DEH", "BOM", "BOA", "DHQ", "GGP"])
        return render_to_response(rsp,
                                {'reason_code':reason_code,
                                 'service_centre':service_centre},
                               context_instance = RequestContext(request))

@csrf_exempt
def rto_reverse(request):
   awb = request.POST['awb']
   ship = Shipment.objects.get(airwaybill_number=awb, status=1)
   rto_reversal(ship, request)
   return HttpResponse("Success")

@csrf_exempt
def revert_inscan_shipment(request):
    if not request.is_ajax():
        raise Http404

    # change the shipment status_type to '0'
    awb_no = request.POST.get('awb_no',None)

    response = {'success': False}
    if awb_no:
        try:
            ship = Shipment.objects.filter(airwaybill_number=int(awb_no))
            shipment = ship[0]
            # update shipments status from shipment history table
            upd_time = shipment.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            ship_history = shipment_history.objects.filter(shipment=shipment).order_by('-updated_on')
            for history in ship_history:
                if history.status in [0, 7, 8, 9]:
                    break
                if history.status in [6, 11, 12, 16, 17]:
                    continue
                elif history.status == 14:
                    status = 3
                    current_sc = history.current_sc
                    break
                elif history.status == 15:
                    status = 5
                    current_sc = history.current_sc
                    break
                status = history.status
                current_sc = history.current_sc
                break

            ship.update(status=status, current_sc=current_sc, status_type=0)
            response['success'] = True
        except Shipment.DoesNotExist:
            pass

    json = simplejson.dumps(response)
    return HttpResponse(json,mimetype='application/json')


@csrf_exempt
def return_rto_shipment(awb, emp_code, reason_code, sc):
    rd_status = 0
    rts_status = 0
    rto_status = 1
    status = 1
    return_shipment = 2
    remarks = "Return to Origin"
    ship = Shipment.objects.filter(airwaybill_number=awb,
            current_sc=sc)
    if ship.exists():
        shipment = ship[0]
    else:
        return (None, awb)

    if shipment.status == 7:
        return (None, awb)
        #return HttpResponse("Shipment in Outscan Stage, cannot be returned!!")
    elif shipment.status == 9:
        return (None, awb)
        #return HttpResponse("Shipment already delivered, cannot be returned!!")
    elif shipment.status <> 8:
        return (None, awb)
        #return HttpResponse("Please update the shipment status before proceeding.")

    pincode = shipment.pickup.pincode
    if ShipperMapping.objects.filter(shipper=shipment.pickup.subcustomer_code):
                          pinc = ShipperMapping.objects.get(shipper=shipment.pickup.subcustomer_code)
                          pincode = pinc.return_pincode
    pincode_obj = Pincode.objects.get(pincode= pincode)
    service_centre = pincode_obj.service_center
#    service_centre = shipment.pickup.service_centre

    #expected_dod = get_expected_dod(sc)
    #expected_dod = expected_dod if expected_dod else shipment.expected_dod

    ship.update(updated_on=now,
            pincode=pincode,
            remark=shipment.service_centre_id,
            status=status,
            status_type=0,
            reason_code=reason_code,
            current_sc=sc,
            rto_status=rto_status,
            return_shipment=return_shipment,
            service_centre=service_centre)

    altinstructiawb = InstructionAWB.objects.filter(
            batch_instruction__shipments__current_sc=sc,
            status=0,
            batch_instruction__shipments=shipment).update(status=1)
    #history_update(shipment, 17, request, remarks, reason_code)

    if reason_code.code == 666:
        utils.update_sdl_billing(shipment)
    return (shipment,)


@csrf_exempt
def return_rto_shipments(request):
    if request.POST:
       #"emp_code="+emp_code+"&awb="+awb+"&reason_code="+rc+"&redir_code="+"74";
       emp_code = request.POST['emp_code']
       awbs = request.POST['awb_list']
       awb_list = str(awbs).strip().split(',')
       sc = request.user.employeemaster.service_centre
       reason_code_id = request.POST['reason_code']
       reason_code = ShipmentStatusMaster.objects.get(id=int(reason_code_id))
       remarks = "Return to Origin"
       wrong_awbs = []
       for awb in awb_list:
           res = return_rto_shipment(awb, emp_code, reason_code, sc)
           if res[0] == None:
               wrong_awbs.append(res[1])
           else:
               history_update(res[0], 17, request, remarks, reason_code)
       if len(wrong_awbs):
           wawbs = [str(x) for x in wrong_awbs]
           m = ','.join(wawbs)
           msg = "Following AWB's Failed. \n {0}".format(m)
       else:
           msg = "Success"
       return HttpResponse(msg)
    return render_to_response("delivery/include_rto_shipment.html",
                               context_instance = RequestContext(request))

@csrf_exempt
def awb_info(request):
     rs_code_op = ''
     resp=False
  #   drs_shipment = get_model('service_centre', 'DeliveryOutscan_shipments')
  #   ship = drs_shipment.objects.filter(deliveryoutscan_id=oid).order_by('-id')
     if 'awb' in request.POST:
        awb = request.POST['awb']
        try:
           shipment = Shipment.objects.filter(airwaybill_number=awb,status=32,reverse_pickup=True)
        except:
           return HttpResponse("Invalid")
     else:
        oid = request.POST['os']
        sr = request.POST['sr']
        try:
           ship = OutscanShipments.objects.get(outscan = oid, serial= sr)
        except (TypeError, ValueError, IndexError, OutscanShipments.DoesNotExist) as e:
           return HttpResponse("Invalid")
        shipment = Shipment.objects.filter(airwaybill_number=ship.awb,status=32,reverse_pickup=True)
        awb = str(ship.awb)

     if shipment:
          ship=shipment[0]
          if ship.length ==0 or ship.length ==0.0 or  ship.breadth == 0 or ship.breadth == 0.0 or ship.height == 0.0 or ship.height == 0 or ship.actual_weight == 0.0 or ship.actual_weight == 0:
             resp=True
          rs_code_op = '<option value=2 >400 Reverse shipment picked </option>'
          remark = 'Picked Up'
     else:
          rs_code_op ='<option value=1 >999 - Delivered</option>'
          #rs_code_op = '<option>---</option><option value=1 >999 - Delivered</option>'
          remark = 'Delivered'
     return HttpResponse(str(awb)+'$'+rs_code_op+'$'+remark+'$'+str(resp))

def redirection_bkup(request):
    if request.method == 'GET':
        reason_code = ShipmentStatusMaster.objects.filter(code__in=[207, 230])
        service_centre = ServiceCenter.objects.all()
        return render_to_response('delivery/redirection.html',
            {'reason_code':reason_code, 'service_centre':service_centre},
            context_instance = RequestContext(request))

    elif request.POST:
        dest = request.user.employeemaster.service_centre_id
        emp_code = request.POST['emp_code']
        awb = request.POST['awb']
        reason_code = request.POST['reason_code']
        sc_id = request.POST['service_centre']
        reason_code = ShipmentStatusMaster.objects.get(id=int(reason_code))
        ship = Shipment.objects.filter(airwaybill_number=awb).exclude(rts_status=2).exclude(status=9)
        if ship.exists():
             shipment = ship[0]
        else:
             return HttpResponse("Invalid Shipment")

        if shipment.status == 7:
             return HttpResponse("Shipment in Outscan Stage, cannot be returned!!")
        if shipment.status == 9:
             return HttpResponse("Shipment already delivered, cannot be returned!!")

        service_centre = ServiceCenter.objects.get(id=int(sc_id))
        destination_city = service_centre.city
        pincode = int(service_centre.pincode_set.all()[0].pincode)

        #expected_dod = get_expected_dod(service_centre)
        #expected_dod = expected_dod if expected_dod else shipment.expected_dod

        ship.update(updated_on=now, pincode=pincode, status=1, status_type=0,
                reason_code=reason_code, current_sc=dest,
                rd_status=1,  return_shipment=1,
                service_centre=service_centre)

        altinstructiawb = InstructionAWB.objects.filter(batch_instruction__shipments__current_sc_id = dest,
                status=0, batch_instruction__shipments=shipment).update(status=1)

        history_update(shipment, 17, request, "Redirection under Same Airwaybill", reason_code)
        return HttpResponseRedirect("/delivery/return_redirection/3/")


'''not used'''
@csrf_exempt
def awb_tally(request):
    upd_type=request.POST['upd_type']
    if upd_type=="rc":
        awb=request.POST['awb']
        reason_code_id=request.POST['reason_code']
        reason_code=ShipmentStatusMaster.objects.get(id=int(reason_code_id))
        AirwaybillTally.objects.filter(id=int(awb)).update(reason_code=reason_code)
        return HttpResponse(reason_code)
    cash_emp = request.POST['cash_emp']
    cash_emp = EmployeeMaster.objects.get(employee_code=int(cash_emp))
    delivery_emp = request.POST['delivery_emp']
    delivery_emp = EmployeeMaster.objects.get(employee_code=int(delivery_emp))
    awb = request.POST['awb']
    amount = request.POST['amt']
    shipment = Shipment.objects.get(airwaybill_number=awb, status=9)
    AirwaybillTally.objects.filter(shipment=shipment).update(cash_tally_emp_code = cash_emp, delivery_emp_code = delivery_emp, amount_collected=amount, status=1)
    awb = AirwaybillTally.objects.get(shipment=shipment)
    return render_to_response("delivery/cash_tally_data.html", {'a':awb})


'''not used '''
@csrf_exempt
def delink_shipment_codd(request, cid):
    '''Delink Shipment in CODD'''
    codd = CODDeposits.objects.get(id = cid)
    if request.POST:
        awb_number = request.POST['awb']
        try:
            shipment = Shipment.objects.get(airwaybill_number = awb_number)
            codd.cod_shipments.remove(shipment)
            return HttpResponse("Shipment removed Sucessfully")
        except:
            return HttpResponse("Incorrect Shipment Number")
    else:
        shipment  =  codd.cod_shipments.all()
        shipment_count  =  shipment.count()
        return render_to_response("delivery/delink_shipment_codd.html",
                                  {'codd':codd,
                                   'shipment':shipment,
                                   'shipment_count':shipment_count,
                                   'cid':cid,},
                                   context_instance  =  RequestContext(request))
'''not used'''
def delivery_sheet_sal(request, sid):
    '''Delivery Sheet for SAL'''
    sal  =  ShipmentAtLocation.objects.get(id = sid)
    shipment  =  sal.scanned_shipments.all()
    return render_to_response("delivery/delivery_sheet.html",
                                  {'outscan':sal,
                                   'shipment':shipment,
                                   'oid':sid,
                                   },
                                   context_instance = RequestContext(request))

'''not used'''
@csrf_exempt
def delink_shipment_sal(request, sid):
    '''Delink Shipment in SAL batch'''
    sal  =  ShipmentAtLocation.objects.get(id = sid)
    if request.POST:
        awb_number =  request.POST['awb']
        try:
            shipment  =  Shipment.objects.get(airwaybill_number = awb_number)
            sal.scanned_shipments.remove(shipment)
            return HttpResponse("Shipment removed Sucessfully")

        except:
            return HttpResponse("Incorrect Shipment Number")
    else:
        shipment  =  sal.scanned_shipments.all()
        shipment_count  =  shipment.count()
        return render_to_response("delivery/delink_shipment_sal.html",
                                  {'sal':sal,
                                   'shipment':shipment,
                                   'shipment_count':shipment_count,
                                   'sid':sid,},
                                   context_instance = RequestContext(request))
def cluster_based_sc(request):
    ncr = ["GGA","GGB","GGC","GGP","NDB","NDC","GNA","GZA","GZB","GZC","FAR"]
    if request.POST:
         state = request.POST['state']
         if state <> "NCR":
            sc = ServiceCenter.objects.filter(city__state__id = state)
         elif state == "NCR":
            sc = ServiceCenter.objects.filter(center_shortcode__in = ["GGA","GGB","GGC","GGP","NDB","NDC","GNA","GZA","GZB","GZC","FAR"])
         else:
            sc = ServiceCenter.objects.all()

    #if request.user.employeemaster.user_type in ["Sr Manager", "Director"]:
    #     sc = ServiceCenter.objects.all()
    elif DashboardVisiblity.objects.filter(employee = request.user.employeemaster):
          sc = ServiceCenter.objects.filter(city__state__in = DashboardVisiblity.objects.filter(employee = request.user.employeemaster).values_list('state'))
          if DashboardVisiblity.objects.filter(employee = request.user.employeemaster, ncr_state=1):
             sc = ServiceCenter.objects.filter(Q(city__state__in = DashboardVisiblity.objects.filter(employee = request.user.employeemaster).values_list('state')) | Q(center_shortcode__in = ncr))
    elif request.user.employeemaster.user_type == "Manager":
         sc = ServiceCenter.objects.filter(city__state = request.user.employeemaster.service_centre.city.state)
    else:
         sc = ServiceCenter.objects.filter(id = request.user.employeemaster.service_centre_id)
    return sc

@csrf_exempt
def monitoring_dashboard(request):
    #return HttpResponse("")
    counter_date = now.strftime('%Y-%m-%d 04:00:00')
    last_month = nextmonth = now - datetime.timedelta(days=10)
    sc = cluster_based_sc(request)

    monitor_counts = {}

    for cur_sc in sc:
        #manifested = Shipment.objects.using('local_ecomm').filter(current_sc = cur_sc,
        #           status__in = [0,1], rts_status = 0).exclude(status=9).exclude(reason_code__code__in = [310,333,111,311,888]).aggregate(Count('id'))
        #manifested = manifested['id__count']

        manifested = Shipment.objects.using('local_ecomm').filter(current_sc_id = cur_sc.id, status__in = [0,1]).only('id','rts_status','reason_code')
        manifest_count = 0
        for manifest in manifested:
            if manifest.rts_status == 0 and manifest.reason_code_id not in (55,53,52,6,4):
               manifest_count += 1
        manifested = manifest_count
        manifested_query = "Shipment.objects.using('local_ecomm').filter(current_sc_id = %s, status__in = [0,1], rts_status = 0).exclude(status=9).exclude(reason_code__code__in = [310,333,111,311,888]).values_list('airwaybill_number')"%(cur_sc.id)
  #  os_hub = Shipment.objects.filter(pickup__service_centre = request.user.employeemaster.service_centre,
  #                 shipext__status_bk = 15, rts_status = 0).exclude(status=9).aggregate(Count('id'))
  #  os_hub = os_hub['id__count']

   # run = 0

        #inscan_dc = Shipment.objects.using('local_ecomm').filter(service_centre = cur_sc, status = 6, rts_status = 0).exclude(status=9).exclude(reason_code__code__in = [310,333,111,311,888]).aggregate(Count('id'))
        #inscan_dc = inscan_dc['id__count']
        inscan_dc = Shipment.objects.using('local_ecomm').filter(service_centre_id = cur_sc.id, status = 6).only('id','rts_status','reason_code')
        inscan_dc_count = 0
        inscan_dc_list = inscan_dc
        for inscan_dc in inscan_dc_list:
            if inscan_dc.rts_status == 0 and inscan_dc.reason_code_id not in (55,53,52,6,4):
               inscan_dc_count += 1
        inscan_dc = inscan_dc_count
        inscan_dc_query = " Shipment.objects.using('local_ecomm').filter(service_centre_id = %s, status = 6, rts_status = 0).exclude(status=9).exclude(reason_code__code__in = [310,333,111,311,888]).values_list('airwaybill_number')"%(cur_sc.id)

       #ofd_fresh = Shipment.objects.using('local_ecomm').filter(service_centre = cur_sc,
       #           rts_status = 0, status = 7, updated_on__gte = counter_date).exclude(reason_code__code__in = [310,333,111,311,888]).exclude(status=9).\
       #           aggregate(Count('id'))

       #ofd_fresh = ofd_fresh['id__count']

        ofd_fresh = Shipment.objects.using('local_ecomm').filter(service_centre_id = cur_sc.id, status = 7).only('id','rts_status','reason_code','updated_on')
        ofd_fresh_count = 0
        ofd_bd_count = 0
        ofd_fresh_list = ofd_fresh
        for ofd_fresh in ofd_fresh_list:
            if ofd_fresh.rts_status == 0 and ofd_fresh.reason_code_id not in (55,53,52,6,4) and ofd_fresh.updated_on > datetime.datetime.strptime(counter_date,"%Y-%m-%d %H:%M:%S"):
               ofd_fresh_count += 1
            elif ofd_fresh.rts_status == 0 and ofd_fresh.reason_code_id not in (55,53,52,6,4) and ofd_fresh.updated_on < datetime.datetime.strptime(counter_date,"%Y-%m-%d %H:%M:%S"):
               ofd_bd_count += 1
        ofd_fresh = ofd_fresh_count
        ofd_bd = ofd_bd_count

        ofd_fresh_query = "Shipment.objects.using('local_ecomm').filter(service_centre_id = %s,rts_status = 0, status = 7, updated_on__gte = counter_date).exclude(status=9).exclude(reason_code__code__in = [310,333,111,311,888]).values_list('airwaybill_number')"%(cur_sc.id)

        #ofd_bd = Shipment.objects.using('local_ecomm').filter(service_centre = cur_sc,
        #           rts_status = 0, updated_on__lt = counter_date, status = 7).\
        #           exclude(reason_code__code__in = [310,333,111,311,888]).exclude(status=9).aggregate(Count('id'))
        #ofd_bd = ofd_bd['id__count']
        ofd_bd_query = "Shipment.objects.using('local_ecomm').filter(service_centre_id = %s,rts_status = 0, updated_on__lt = counter_date, status = 7).exclude(status=9).exclude(reason_code__code__in = [310,333,111,311,888]).values_list('airwaybill_number')"%(cur_sc.id)

      # ud_fresh = Shipment.objects.using('local_ecomm').filter(service_centre = cur_sc,
      #            rts_status = 0, updated_on__gte = counter_date, status = 8).exclude(status=9).exclude(reason_code__code__in = [310,333,111,311,888]).\
      #            aggregate(Count('id'))
      # ud_fresh = ud_fresh['id__count']

        ud_fresh = Shipment.objects.using('local_ecomm').filter(service_centre_id = cur_sc.id, status = 8, updated_on__gte = last_month).only('id','rts_status','reason_code','updated_on')
        ud_fresh_count = 0
        ud_bd_count = 0
        ud_fresh_list = ud_fresh
        for ud_fresh in ud_fresh_list:
            if ud_fresh.rts_status == 0 and ud_fresh.reason_code_id not in (55,53,52,6,4) and ud_fresh.updated_on > datetime.datetime.strptime(counter_date,"%Y-%m-%d %H:%M:%S"):
               ud_fresh_count += 1
            elif ud_fresh.rts_status == 0 and ud_fresh.reason_code_id not in (55,53,52,6,4) and ud_fresh.updated_on < datetime.datetime.strptime(counter_date,"%Y-%m-%d %H:%M:%S"):
               ud_bd_count += 1
        ud_fresh = ud_fresh_count
        ud_bd = ud_bd_count




      # ud_bd = Shipment.objects.using('local_ecomm').filter(service_centre = cur_sc,
      #            rts_status = 0, status = 8, added_on__year = now.year, updated_on__lt = counter_date).\
      #            exclude(status=9).exclude(reason_code__code__in = [310,333,111,311,888,777]).aggregate(Count('id'))
      # ud_bd = ud_bd['id__count']

        total_is_ofd = inscan_dc+ofd_fresh+ofd_bd+ud_fresh+ud_bd+manifested

       #del_fresh = Shipment.objects.using('local_ecomm').filter(service_centre = cur_sc,
       #           rts_status = 0, status=9, updated_on__gte = counter_date).\
       #           aggregate(Count('id'))
       #del_fresh = del_fresh['id__count']


        del_fresh = Shipment.objects.using('local_ecomm').filter(service_centre_id = cur_sc.id, status = 9,  updated_on__gte = counter_date).only('id','rts_status','reason_code','updated_on')
        del_fresh_count = 0
        del_bd_count = 0
        del_fresh_list = del_fresh
        for del_fresh in del_fresh_list:
            if del_fresh.rts_status == 0 :
               del_fresh_count += 1
        del_fresh = del_fresh_count



        
       # del_bd = Shipment.objects.using('local_ecomm').annotate(num_delos=Count('deliveryoutscan')).filter(service_centre = cur_sc,
       #            rts_status = 0, status = 9, updated_on__gte = last_month, num_delos__gt = 1).aggregate(Count('id')) 
    #    del_bd = Shipment.objects.using('local_ecomm').filter(service_centre = cur_sc,
     #              rts_status = 0, status = 9, updated_on__lt = counter_date, added_on__gte = last_month).\
     #              aggregate(Count('id'))
       # del_bd = del_bd['id__count']

        #del_bd = Shipment.objects.using('local_ecomm').filter(service_centre_id = cur_sc.id, status = 9,  updated_on__gte = last_month).only('id','rts_status','reason_code','updated_on')
        #del_bd = DeliveryOutscan.objects.using('local_ecomm').filter(service_centre_id = cur_sc.id, status = 9,  updated_on__gte = last_month).only('id','rts_status','reason_code','updated_on')
        del_bd = []
        del_bd_count = 0
        del_bd_list = del_bd
        for del_bd in del_bd_list:
            if del_bd.rts_status == 2:
               del_bd_count += 1
        del_bd = del_bd_count



        ret_ship = Shipment.objects.using('local_ecomm').filter(original_dest = cur_sc,
                   rts_status__gte = 1, added_on__gte = counter_date).exclude(rts_status=1).aggregate(Count('id'))
        ret_ship = ret_ship['id__count']

    #total_dv_rd = del_fresh+del_bd+ret_ship

       #bag_ib = Bags.objects.using('local_ecomm').annotate(num_shipments=Count('shipments')).filter(num_shipments__gt=0, added_on__gte = last_month, destination = cur_sc, bag_status__in = [2,7])
       #bag_ob = Bags.objects.using('local_ecomm').annotate(num_shipments=Count('shipments')).filter(num_shipments__gt=0, added_on__gte = last_month, origin = cur_sc, bag_status__in = [2,7])
        bag_ib_query = "Bags.objects.using('local_ecomm').annotate(num_shipments=Count('shipments')).filter(num_shipments__gt=0, added_on__gte = last_month, destination_id = %s, bag_status__in = [2,7]).values_list('bag_number','updated_on','origin__center_shortcode')"%(cur_sc.id)
        bag_ob_query = "Bags.objects.using('local_ecomm').annotate(num_shipments=Count('shipments')).filter(num_shipments__gt=0, added_on__gte = last_month, origin_id = %s, bag_status__in = [2,7]).values_list('bag_number','updated_on','destination__center_shortcode')"%(cur_sc.id)
        ship_ib_query = "Bags.objects.using('local_ecomm').filter(added_on__gte = last_month, destination_id = %s, bag_status__in = [2,7]).values_list('shipments__airwaybill_number', 'bag_number')"%(cur_sc.id)
        ship_ob_query = "Bags.objects.using('local_ecomm').filter(added_on__gte = last_month, origin_id = %s, bag_status__in = [2,7]).values_list('shipments__airwaybill_number', 'bag_number')"%(cur_sc.id)

      # ship_ib = Bags.objects.using('local_ecomm').filter(added_on__gte = last_month, destination = cur_sc, bag_status__in = [2,7]).aggregate(Count('shipments'))
      # ship_ob = Bags.objects.using('local_ecomm').filter(added_on__gte = last_month, origin = cur_sc, bag_status__in = [2,7]).aggregate(Count('shipments'))
       #bag_ib = bag_ib.aggregate(Count('id'))
       #bag_ob = bag_ob.aggregate(Count('id'))
       #bag_ib = bag_ib['id__count']
       #bag_ob = bag_ob['id__count']
       #ship_ib = ship_ib['shipments__count']
       #ship_ob = ship_ob['shipments__count']

        bag_ib = 0
        bag_ob = 0
        bag_ib = 0
        bag_ob = 0
        ship_ib = 0
        ship_ob = 0


        monitor_counts[cur_sc]=(manifested, manifested_query, inscan_dc, inscan_dc_query, ofd_fresh, ofd_fresh_query, ofd_bd, ofd_bd_query,
                                ud_fresh, ud_bd, total_is_ofd, del_fresh, del_bd, ret_ship, bag_ib_query, bag_ob_query, ship_ib_query,
                                ship_ob_query, ship_ib, ship_ob, bag_ib, bag_ob)

    state = State.objects.all()
    return render_to_response("delivery/monitoring_dashboard.html",
                                   {'monitor_counts':monitor_counts,
                                    'state':state },
                                   context_instance=RequestContext(request))


@csrf_exempt
def get_shipment_monitoring(request):
    counter_date = now.strftime('%Y-%m-%d 04:00:00')
    last_month = nextmonth = now - datetime.timedelta(days=60)

    query = request.GET['query']
    query_result = eval(query)
    if "Bags" in query:
        if "airwaybill_number" in query:
             shipment_info = dict((k[0],k[1] if len(k) >1 else 'None') for k in query_result)
        else:
              shipment_info = dict((k[0],(str(k[1]), str(k[2]))) for k in query_result)
    else:
        shipment_info = dict((int(k[0]),'None') for k in query_result)
    shipment_json = json.dumps(shipment_info)
    return HttpResponse(shipment_json)

@csrf_exempt
@json_view
def get_outscan_details(request):
    if request.method == 'GET':
        outscan_input = request.GET.get('outscan')
        data = cashtally_deliveryoutscan_details(outscan_input)
        return data

@csrf_exempt
@json_view
def update_outscan_details(request):
    if request.method == 'GET':
        outscan_input = request.GET.get('outscan')
        outscan_update_for_cash_tally(outscan_input)
        data = cashtally_deliveryoutscan_details(outscan_input)
        return data

@csrf_exempt
@json_view
def get_awbno_details(request):
    if request.method == 'GET':
        awbno_input = request.GET.get('awbno')
        data = cashtally_shipment_details(awbno_input)
        outscan_list = map(str, data.pop('delivery_outscan_list'))
        queues = map(str, data.pop('queues'))
        coddeposits_list = map(str, data.pop('coddeposits_list'))

        data['delivery_outscan_list'] = ', '.join(outscan_list)
        data['coddeposits_list'] = ', '.join(coddeposits_list)
        data['queues'] = ', '.join(queues)
        return data

# helper function for pisa
def write_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(
    html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse("Gremlin's ate your pdf! %s" % cgi.escape(html))

@json_view
@csrf_exempt
def credit_card_payment(request):
    from delivery.forms import CreditcardDeliveryForm
    if request.method == 'POST':
        form = CreditcardDeliveryForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return {'success': True, 'resp': str(instance)}
        return {'success': False, 'resp': form.errors}
    return HttpResponse("credit card")

@json_view
@csrf_exempt
def undel_awb_info(request):
   if request.method == 'POST':
     if 'awb' in request.POST:
        awb = request.POST['awb']
     else:
	oid = request.POST['os']
        sr = request.POST['sr']
        try:
           ship_awb = OutscanShipments.objects.get(outscan = oid, serial= sr)
        except (TypeError, ValueError, IndexError, OutscanShipments.DoesNotExist) as e:
            return HttpResponse("Invalid")
        awb = ship_awb.awb

     ship = Shipment.objects.get(airwaybill_number=awb)
     stm = []
     if ship:
         if ship.reverse_pickup == True and ship.status == 32:
	    #stm=ShipmentStatusMaster.objects.filter(code__range=[999,777])
           stm=ShipmentStatusMaster.objects.filter(code__gt=400,code__lt=500).exclude(code=444).values_list('id','code','code_description')
         elif ship.status == 7:
            stm=ShipmentStatusMaster.objects.filter(code__gt=111,code__lt=399).exclude(code__in=[205,206,207,333]).values_list('id','code','code_description')
	 if stm:
	    op_stmt = ''
	    for shipment in stm:
	       op_stmt += str(shipment[0])+'#'+str(shipment[1])+' - '+shipment[2]+'$'
	    if op_stmt != '':
	       op_stmt = op_stmt[:-1]
	    return {'msg':'success','op_stmt':op_stmt,'awb':awb}
      
     return {'msg':'fail'}

@json_view
@csrf_exempt
def update_card_payment(request):
    from .forms import CreditCardPaymentDepositForm, CreditPaymentAwbDetailsForm, CreditAwbDetailFormSet
    from .forms import CreditDateForm, CreditPaymentDetailForm, CreditcardDeliveryForm
    emp = request.user.employeemaster
    if request.method == 'POST':
        deposit_form = CreditCardPaymentDepositForm(request.POST)
        awb_form = CreditAwbDetailFormSet(request.POST)
        if deposit_form.is_valid() and awb_form.is_valid():
            credit = deposit_form.save(emp)
            #awb_form.save(credit)
            for form in awb_form.forms:
               form.save(credit)
            # create a template to replace update card payment section
            # forms for credit card payment
            awb_details_form = CreditPaymentAwbDetailsForm()
            date_form = CreditDateForm(initial={'system_date': datetime.datetime.today().date()})
            payment_detail_form = CreditPaymentDetailForm()
            awb_formset = CreditAwbDetailFormSet()
            credit_form = CreditcardDeliveryForm()

            html = render_to_string("delivery/update_card_payment.html",
                  {'awb_details_form': awb_details_form, 'date_form': date_form,
                   'payment_detail_form': payment_detail_form, 
                   'awb_formset': awb_formset, 'credit_form': credit_form})
            return {'success': True, 'message': str(credit) + ' succefully added', 'html': html}
        return {'success': False, 'deposit_error': deposit_form.errors, 'awb_error': awb_form.errors}
    return {'success': True}

#report
def generate_card_payment_report(
        report_date_from, report_date_to, cust_option, dc_option):
    card_payments = UpdateCardPaymentModified.objects.filter(
        date__range=(report_date_from, report_date_to),
        delivery_centre_name=dc_option)
    now = datetime.datetime.now() 
    report = ReportGenerator('card_payment_report_{0}.xlsx'.format(now))
    report.write_header((
        'SlNo', 'DC Name','Cust Code','Trans Date','Trans Slip No', 
        'Trans Slip Amount', 'Updated on', 'AWB No', 'Username', 'User ID', 
        'Remarks'))
    for card_payment in card_payments:
        slno = card_payment.id
        dc_name = card_payment.delivery_centre_name
        cust_code = card_payment.airwaybill_number
        trans_date = card_payment.transaction_date
        trans_slip_no = card_payment.transaction_slip_no
        trans_slip_amount = card_payment.airwaybill_amount
        updated_on = card_payment.date
        awbno = card_payment.airwaybill_number
        username = card_payment.delivery_centre_name 
        user_id = card_payment.id
        remarks = card_payment.remarks 
        report.write_row((
            slno, dc_name, cust_code, trans_date, trans_slip_no,
            trans_slip_amount, updated_on, awbno, username, user_id, remarks))
    file_name = report.manual_sheet_close()
    path = settings.ROOT_URL + '/static/uploads/reports/' + file_name
    return file_name
 
def card_payment_report(request):
     if request.method == 'GET':
         report_date_from = request.GET.get("report_date_from")
         report_date_to = request.GET.get("report_date_to")
         cust_option = request.GET.get("cust_option")
         dc_option = request.GET.get("dc_option")
         file_name = generate_card_payment_report(
             report_date_from, report_date_to, cust_option, dc_option)
         return HttpResponseRedirect('/static/uploads/reports/' + file_name)

@csrf_exempt
@json_view
def view_edit(request):
    if request.method == 'GET':
        trans_slip_no = request.GET.get('trans_slip_no')
        try:
            card_data = UpdateCardPaymentModified.objects.get(
                transaction_slip_no=trans_slip_no)
            date = card_data.date
            payment_type = card_data.payment_type
            airwaybill_number = card_data.airwaybill_number
            credit_payment_recvd_amount = card_data.credit_payment_recvd_amount
            delivery_centre_name = card_data.delivery_centre_name
            transaction_date = card_data.transaction_date
            now = datetime.datetime.now().strftime("%Y-%m-%d")
            return {
                'date': now, 'transaction_date': card_data.transaction_date,
                'airwaybill_number': airwaybill_number,
                'credit_payment_recvd_amount': credit_payment_recvd_amount,
                'delivery_centre_name': delivery_centre_name, 'success': True
            }
        except UpdateCardPaymentModified.DoesNotExist:
            return {'success': False}
    if request.method == 'POST':
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        return {'success': True, 'now': now}

@json_view
def awb_credit_details(request):
    awb = request.GET.get('awb')
    try:
        s = Shipment.objects.get(airwaybill_number=awb)
        awb_amount = s.collectable_value
        received_amount = CreditPaymentAwbDetails.objects.filter(shipment=s).aggregate(total=Sum('credit_card_payment_received'))['total']
        credit_received = received_amount if received_amount else 0
        balance =  awb_amount - credit_received
        return {
            'success': True, 'awb_amount': awb_amount, 'balance': balance, 
            'dc': s.original_dest.center_name, 'credit_received': credit_received
        }
    except Shipment.DoesNotExist:
        return {'success': False, 'awb': awb}


@json_view
@csrf_exempt
def rts_update(request):
    awb = request.POST.get('awb')
    ref_awb = request.POST.get('ref_awb')
    return update_rts_shipment(awb, ref_awb, request.user.employeemaster)


@login_required
def cod_panel(request):
    return render_to_response(
        'delivery/cod_panel.html', context_instance=RequestContext(request))


@json_view
def cod_panel_coddeposit_search(request):
    from delivery.forms import CODDepositSearchForm
    if request.GET: 
        form = CODDepositSearchForm(request.GET)
        if form.is_valid():
            cod_deposits = form.search()
        else:
            cod_deposits = []
    else:
        form = CODDepositSearchForm()
        cod_deposits = []
    html = render_to_string(
        "delivery/cod_panel_coddeposits.html",
        {'cod_deposits': cod_deposits, 'form': form},
        context_instance=RequestContext(request))
    return {'html': html}
