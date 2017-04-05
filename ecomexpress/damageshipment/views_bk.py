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
from service_centre.models import *
from utils import history_update, price_updated, shipment_transit_time, developers_only
import re
from damageshipment.models import *


@csrf_exempt
def damageshipment(request):
    '''DeBagging Shipments'''
    dest = request.user.employeemaster.service_centre_id
    if request.POST:
        awb_num = request.POST['awb_num']
        try:
            int(awb_num)
        except ValueError:
           return HttpResponse("1")
 
        q = Q(shipmentdamagestatus_set.all()[0].status == 0)
        ship = Shipment.objects.filter(airwaybill_number=int(awb_num),reason_code__code=888).select_related(
               'service_centre__center_name','shipper__name').only('id','added_on',
               'expected_dod','status','airwaybill_number','order_number','inscan_date',
               'shipper__name','shipper__code','consignee','actual_weight',
               'service_centre__center_name','pincode','pieces','collectable_value','status_type'
        ).exclude(rts_status=2)
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
        total_records = ""
        return render_to_response("damageshipment/damage.html",
                                  {'a':shipment,
                                   'status':"2",
                                   'total_records':total_records,
              })
    else:
            q = Q(shipmentdamagestatus__status = 0) | Q(shipmentdamagestatus__status__isnull = True)
            shipment = Shipment.objects.filter(reason_code__code=888).filter(q).select_related('service_centre__center_name',
                     'shipper__name').only('airwaybill_number','order_number','shipper__name',
                     'shipper__code','consignee','actual_weight','service_centre__center_name',
                     'pincode','pieces','collectable_value','status_type')
            total_records  =  Shipment.objects.using('local_ecomm').filter(reason_code__code=888).count()
            return render_to_response("damageshipment/damage.html",
                                {'shipment':shipment,
                                 'total_records':total_records,},
                               context_instance = RequestContext(request))

def airwaybill_search(request):

    if request.POST:
      awb_number = request.POST['awb_number']
      try:
       #awb = AirwaybillNumbers.objects.filter(airwaybill_number=awb_number,reason_code__code=888)
       shipment = Shipment.objects.filter(airwaybill_number=awb_number,reason_code__code=888).select_related('service_centre__center_name',
                     'shipper__name').only('airwaybill_number','order_number','shipper__name',
                     'shipper__code','consignee','actual_weight','service_centre__center_name',
                     'pincode','pieces','collectable_value','status_type')

      except:
       awb = ""
      return render_to_response('damageshipment/airwaybill_search.html',
                                {"shipment":shipment
                                 },context_instance=RequestContext(request))
    else:
      awbc = AirwaybillCustomer.objects.filter().order_by("-created_on")
      return render_to_response('damageshipment/airwaybill_search.html',
                                {"shipment":shipment},context_instance=RequestContext(request))


def download_xcl(request):
    file_name = 'damageshipment_list.xlsx'
    report = ReportGenerator(file_name)
    col_heads = ('airwaybill_number','shippername','consignee','actual_weight','center_name','pincode','pieces','collectable_value','order_number','description','shippercode')
    shipments = Shipment.objects.filter(reason_code__code=888)
    report.write_header(col_heads)
    for s in shipments:
        row = [s.airwaybill_number,s.shipper.name,s.consignee,s.actual_weight,s.service_centre.center_name,s.pincode,s.pieces,s.collectable_value,s.order_number,s.item_description,s.shipper.code]
        report.write_row(row)
    file_name = report.manual_sheet_close()        
    excel_file = open(settings.FILE_UPLOAD_TEMP_DIR + '/reports/' + file_name, "rb").read()
    response = HttpResponse(excel_file, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' %  file_name
    #report.workbook.save(response)
    return response

@csrf_exempt
def shipment_sold(request):
    shipment_id = request.POST.get('id')
    shipment = Shipment.objects.get(id=shipment_id)
    return render_to_response('damageshipment/shipment_sold.html',
                              {'shipment': shipment}, context_instance=RequestContext(request))

@json_view
@csrf_exempt
def shipment_sold_details(request):
    awb = request.POST.get('awb')
    recovered_amount = request.POST.get('recovered_amount')
    recovery_name = request.POST.get('recovery_name')
    sold_date = request.POST.get('sold_date')
    if not sold_date:
        sold_date = datetime.datetime.today()
    recovery_recipt_number = request.POST.get('recovery_recipt_number')
    emp_id = request.POST.get('employee_code')
    ship = Shipment.objects.get(airwaybill_number = awb)
    damageshipment = ShipmentDamageStatus.objects.create(shipment = ship,recovered_amount=recovered_amount,recovery_name=recovery_name,recovery_recipt_number=recovery_recipt_number,employee_code_id=int(emp_id),status=1,sold_date=sold_date, actual_amount=ship.collectable_value)
    return {'success': True, 'id': ship.id}

@csrf_exempt
def recovery_view(request):
    shipment_id = request.POST.get('id')
    shipment = Shipment.objects.get(id=shipment_id)
    return render_to_response('damageshipment/recovery_view.html',
                              {'shipment': shipment}, context_instance=RequestContext(request))
