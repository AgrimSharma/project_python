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
from security.models import *

@csrf_exempt
def read_remarks(request):
    shipment_id = request.POST.get('id')
    shipment = Shipment.objects.get(id=shipment_id)
    security = SecurityModule.objects.filter(shipment_id=shipment.id)    
    return render_to_response(
        "security/read_remarks.html",
        {'security':security,'shipment': shipment,},
        context_instance = RequestContext(request))
 

@csrf_exempt
def security(request):
    '''DeBagging Shipments'''
    dest = request.user.employeemaster.service_centre_id
    if request.POST:
       awb_num = request.POST['awb_num']
       try:
          int(awb_num)
       except ValueError:
          return HttpResponse("1")
  
       #q = Q(shipmentsecuritystatus_set.all()[0].status == 0)
       ship = Shipment.objects.filter(airwaybill_number=int(awb_num),reason_code__code__in=[332,333]).select_related(
                'service_centre__center_name','shipper__name').only('id','added_on',
                'expected_dod','status','airwaybill_number','order_number','inscan_date',
                'shipper__name','shipper__code','consignee','actual_weight',
                'service_centre__center_name','pincode','pieces','collectable_value','status_type'
         ).exclude(rts_status=2)
       shipment = ship[0]
       total_records = ""
       return render_to_response("security/security_new.html",
                                   {'a':shipment,
                                    'total_records':total_records,
               })
    else:
        #q = Q(shipmentsecuritystatus__status = 0) | Q(shipmentdamagestatus__status__isnull = True)
       #q = Q(shipmentsecuritystatus_set.all()[0].status == 0)
        shipment = Shipment.objects.filter(reason_code__code__in=[332,333]).select_related('service_centre__center_name',
                      'shipper__name').only('airwaybill_number','order_number','shipper__name',
                      'shipper__code','consignee','actual_weight','service_centre__center_name',
                      'pincode','pieces','collectable_value','status_type')
        total_records  =  Shipment.objects.using('local_ecomm').filter(reason_code__code__in=[332,333]).count()
        return render_to_response("security/security_new.html",
                               {'shipment':shipment,
                                'total_records':total_records,},
                                context_instance = RequestContext(request))

def download_xcl(request):
    file_name = 'security_list.xlsx'
    report = ReportGenerator(file_name)
    col_heads = ('airwaybill_number','shippername','consignee','actual_weight','center_name','pincode','pieces','collectable_value','order_number','description','shippercode')
    shipments = Shipment.objects.filter(reason_code__code__in=[332,333]).values_list('airwaybill_number','shipper__name','consignee','actual_weight','service_centre__center_name','pincode','pieces','collectable_value','order_number','item_description','shipper__code')
    report.write_header(col_heads)
    report.write_matrix(shipments)
    file_name = report.manual_sheet_close()
    excel_file = open(settings.FILE_UPLOAD_TEMP_DIR + '/reports/' + file_name, "rb").read()
    response = HttpResponse(excel_file, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' %  file_name
    #report.workbook.save(response)
    return response
 
def add_remarks(request):
    shipment_id = request.POST.get('id')
    shipment = Shipment.objects.get(id=shipment_id)
    return render_to_response('security/add_remarks.html',
                              {'shipment': shipment}, context_instance=RequestContext(request))

@json_view
@csrf_exempt
def add_remarks_details(request):
    awb = request.POST.get('awb')
    remarks_add = request.POST.get('remarks_add')
    ship = Shipment.objects.get(airwaybill_number = awb)
    security = SecurityModule.objects.create(shipment = ship,remarks_add = remarks_add)
    return {'success': True, 'id': ship.id}
 
