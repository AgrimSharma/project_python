# Create your views here.
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

from django.shortcuts import render_to_response, redirect, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from jsonview.decorators import json_view

from customer.models import Shipper
from location.models import Pincode, ServiceCenter
from integration_services.models import FetchAirwayBillBatch, PickupEnroll
from integration_services.forms import PickupEnrollForm
from .process_pickup import ProcessPickup


def home(request):
    """
    Show unclosed AirwaybillFetch batches
    """
    fawb_batch = FetchAirwayBillBatch.objects.filter(
        employee_code=request.user.employeemaster.employee_code, status=0
    ).order_by("-added_on")
    return render_to_response(
        "integration_services/home.html",
        {'fawb_batch':fawb_batch},
        context_instance=RequestContext(request))


@csrf_exempt
@json_view
def create_batch(request):
    """
    create a fetch airwaybillbatch for pickup. This airwaybill bathes will be
    used to identify whether airwaybills has been picked up or not.
    """
    emp_code = request.user.employeemaster.employee_code

    # read the attributes
    location = request.POST.get("location")
    pincode = request.POST.get("pincode")

    # get the airwaybills and clean the values
    awb_list = request.POST.get("awbs")

    awbs = awb_list.split("\n")
    cleaned_awbs = [str(a).strip() for a in awbs if a]

    if cleaned_awbs:
        awb_batch = FetchAirwayBillBatch.objects.create(
            employee_code=emp_code, location=location, pincode=pincode)
    else:
        {'success': False, 'message': 'No valid airwaybills found'}

    # bulk create fetched airwaybills
    fetch_awbs_objs = [
        FetchAirwayBill(airwaybill_number=awb,
                        fetch_airwaybill_batch=awb_batch)
        for awb in cleaned_awbs]
    airwaybills = FetchAirwayBill.objects.bulk_create(fetch_awbs_objs)

    # updated the total count in batch object
    total_count = len(airwaybills)
    FetchAirwayBillBatch.objects.filter(id=awb_batch.id).update(
        total_count=total_count)

    html = render_to_string(
        "integration_services/fetch_awb_row.html", {'batch': awb_batch})
    return {'success': True, 'html': html}


@json_view
def refresh_awb_fetch(request):
    batch_id = request.POST.get('batch_id')
    awb_batch = FetchAirwayBillBatch.objects.get(id=batch_id)
    updated_count = awb_batch.refresh()
    updated_count = updated_count  or 0
    return {'processed_count': updated_count}


def pickup_dashboard(request):
     """
     List all pickups.
     """
     if request.method == 'GET':
         enrol_form = PickupEnrollForm()
     else:
         enrol_form = PickupEnrollForm(request.POST)
         if enrol_form.is_valid():
             pickup = enrol_form.save(request.user)   # check validity of this
             pickup.save()

     pickup_list = PickupEnroll.objects.all().order_by('-id')
     return render_to_response(
         "integration_services/enroll_form.html",
         {'enrol_form':enrol_form, 'pickup_list':pickup_list},
         context_instance = RequestContext(request))


@csrf_exempt
def pickup_enrolment(request):
     """
     View for PickupEnroll.
     """
     enrol_form = PickupEnrollForm(request.POST or None)
     if enrol_form.is_valid():
         pickup = enrol_form.save(request.user)   # check validity of this
         pickup_dashboard = pickup.save()

     pickup_list = PickupEnroll.objects.all().order_by('-id')
     return render_to_response(
         "integration_services/enroll_form.html",
         {'enrol_form':enrol_form, 'pickup_list':pickup_list},
         context_instance = RequestContext(request))


def pickup_add(request):
     enrol_form = PickupEnrollForm(request.POST)



# def pickup_dashboardrequest):
#    """
#    View for PickupEnroll.
#    """
#    enrol_form = PickupEnrollForm()
#    return render_to_response(
#        "integration_services/enroll_form.html",
#        {'enrol_form':enrol_form},
#        context_instance = RequestContext(request))

# from django.forms import ModelForm
# from .models import PickupEnroll
#
# class PickupEnrollForm(ModelForm):
# 	"""
# 	Frontend for the PickupEnroll model
# 	"""
# 	class Meta:
# 		model = PickupEnroll
# 		fields = ['customer', 'pickup_date', 'pincode']
#
# form = PickupEnrollForm()

@json_view
def get_pincode_pickup_sc(request):
    pin_number = request.GET.get('pincode')
    try:
        pickup_sc = Pincode.objects.get(pincode=pin_number).pickup_sc.id
        success = True
    except Pincode.DoesNotExist:
        pickup_sc = None
        success = False

    return {'pincode': pin_number, 'pickup_sc': pickup_sc, 'success': success}



@json_view
def get_vendors(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        vendors = Shipper.objects.filter(
            name__icontains=q
        )[:20].values_list('name', flat=True)
        return [{'value': name} for name in vendors]


@json_view
def get_vendor_address(request):
    if request.is_ajax():
        name = request.GET.get('name', '')
        vendors = Shipper.objects.filter(name=name).values_list(
            'address__address1', 'address__address2',
            'address__address3', 'address__address4')
        get_address = lambda x: [str(s) if s else '' for s in x]
        address = ', '.join(get_address(vendors[0])) if vendors.exists() else ''
        return {'name': name, 'address': address}


def dc_dashboard(request):
    """
    Show employee DC-specific dashboard.
    """
    emp_code = request.user.employeemaster.employee_code
    # return HttpResponse(emp_code)

    from authentication.models import EmployeeMaster

    emp = EmployeeMaster.objects.get(employee_code=emp_code)
    emp_dc_id = emp.service_centre_id
    pickup_list = PickupEnroll.objects.filter(
        delivery_service_centre_id=emp_dc_id).order_by('-id')

    return render_to_response(
         "integration_services/dc_dashboard.html",
         {'pickup_list':pickup_list, 'delivery_dc':emp.service_centre},
         context_instance = RequestContext(request))


@json_view
def update_pickup_enroll_status(request):
    if request.is_ajax() and request.method == 'POST':
        status_dict = {"yes": 3, "retry": 2, "cancel": 0}

        pickup_id = request.POST.get('pickup_id')
        pickup_status = request.POST.get('pickup_status')
        status = status_dict.get(pickup_status)

        PickupEnroll.objects.filter(id=pickup_id).update(status=status)
        pickup_status = PickupEnroll.objects.get(id=pickup_id).get_status

        return {
            'success': True, 'pickup_id': pickup_id, 'status': pickup_status}
    else:
        return {'success': False, 'pickup_id': pickup_id}


@csrf_exempt
def multiple_pickup_enroll(request):
    pickup_file = request.FILES['input_file']
    file_contents = pickup_file.read()
    pickup = ProcessPickup(file_contents, request.user)
    pickups, errors = pickup.read_excel()
    # return HttpResponseRedirect(reverse('pickup-dashboard'))
    row_errors = dict([(k, ', '.join(v)) for k, v in errors.items()])
    return render_to_response(
         "integration_services/pickup_update_messages.html",
         {'pickups': pickups, 'errors': row_errors},
         context_instance = RequestContext(request))

@json_view
def get_awb_dc(request):
    from integration_services.utils import nearest_dc, get_display_address
    awb = request.GET.get('awb')
    ship_address = get_display_address(awb)
    dc = nearest_dc(ship_address)
    if dc:
        dc_name = ServiceCenter.objects.get(id=dc).center_name
    return {'awb': awb, 'address': ship_address, 'dc_list': dc, 'dc_name': dc_name}

def pickup_dashbaord(request):
     file_name = 'pickup_format.xlsx'
     col_heads = ('Air Waybill number','Order Number','Product','Shipper','Consignee','Consignee Address1','Consignee Address2','Consignee Address3','Destination City','Pincode','State','Mobile','Telephone','Item Description','Pieces','Collectable Value','Declared value','Actual Weight','Volumetric Weight','Length(cms)','Breadth(cms)','Height(cms)','sub customer id','Pickup name','Pickup Address','Pickup Phone','Pickup Pincode','Return name','Return Address','Return Phone','Return Pincode')
     report.write_row(col_heads)
     report.manual_sheet_close()
     return render_to_response("integration_services/pickup_dashboard.html",
                               context_instance=RequestContext(request))

def download_xcl(request):
    file_name = 'pickup_file.xlsx'
    report = ReportGenerator(file_name)
    col_heads = ('Customer Code','pincode','vendor name','vendor address', 'vendor contact', 'shipment count','pickup date (dd/mm/yyyy)')
    report.write_header(col_heads)
    file_name = report.manual_sheet_close()
    excel_file = open(settings.FILE_UPLOAD_TEMP_DIR + '/reports/' + file_name, "rb").read()
    response = HttpResponse(excel_file, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' %  file_name
    return response
                         
