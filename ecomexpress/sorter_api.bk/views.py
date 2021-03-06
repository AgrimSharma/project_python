import json
import xlrd
import xmltodict
import xlwt
import utils
from datetime import timedelta, datetime
from xlsxwriter.workbook import Workbook
import dateutil.parser

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import get_model
from django.core.mail import send_mail
from models import *

from privateviews.decorators import login_not_required
from track_me.models import *
from service_centre.models import *
from location.models import *
from pickup.models import PickupRegistration
from airwaybill.models import *

now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")

from django.utils import simplejson
from django.db.models import *
from django.contrib.auth.models import User, Group

from customer.models import *
from ecomm_admin.models import *
from service_centre.models import *
from billing.models import Billing, BillingSubCustomer
from airwaybill.models import AirwaybillNumbers
from api.utils import create_vendor
from utils import *
from api.utils import api_auth
from billing.models import ShipmentBillingQueue
from billing.charge_calculations import add_to_shipment_queue

now = datetime.datetime.now()
to_time_obj = now + datetime.timedelta(days=1)
from_time=now.strftime("%Y-%m-%d")
to_time=to_time_obj.strftime("%Y-%m-%d")
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

before = now - datetime.timedelta(days=7)
beforem = now - datetime.timedelta(days=30)



@login_not_required
@csrf_exempt
def add_to_history(request):
    if request.POST:
        capi =  api_auth(request)
        if not capi:
            return HttpResponse('{"success":"no","remarks":"Unauthorised Request"}', mimetype='application/json')
 
    if request.POST:
        awb = request.POST.get('code', None)
        update_date = request.POST.get('date', None)
        update_time = request.POST.get('time', None)
        length = request.POST.get('length', None)
        breadth = request.POST.get('width', None)
        height = request.POST.get('height', None)
        actual_weight = request.POST.get('weight', None)
        volumetric_weight = 0
        #volumetric_weight = request.POST.get('volume_weight', None)
        volume = request.POST.get('volume', None)
        employee_code = request.POST.get('emp_username', None)

        if not awb or not update_date or not update_time or not length or not breadth or not height or not actual_weight or not volumetric_weight or not volume or not employee_code:
            #return HttpResponse("not enough data")
            return HttpResponse('{"success":"no","remarks":"not enough data"}', mimetype='application/json')

        if not Shipment.objects.filter(airwaybill_number = awb):
            return HttpResponse('{"success":"no","remarks":"No Shipment Manifest in the System"}', mimetype='application/json')

        if 1 == 1:
            #return HttpResponse("'%s  '"%(update_date+" "+update_time));
            WeigthUpdateHistory.objects.create(
                        airwaybill_number = awb,
                        update_date = datetime.datetime.strptime(update_date,'%d/%m/%Y').date(),
                        update_time = datetime.datetime.strptime((update_date+" "+update_time),'%d/%m/%Y %H:%M:%S'),
                        length = float(length)/10,
                        breadth = float(breadth)/10,
                        height = float(height)/10,
                        actual_weight = actual_weight,
                        volumetric_weight = volumetric_weight,
                        volume = float(volume)/1000,
                        employee_code = employee_code,
            )
            return HttpResponse('{"success":"yes","remarks":"record inserted"}', mimetype='application/json')
        else:  
            return HttpResponse('{"success":"no","remarks":"formating error"}', mimetype='application/json')
    #return HttpResponse("no post input")
    return HttpResponse('{"success":"no","remarks":"no input data"}', mimetype='application/json')



def process_weight_update_queue(start_count=0,total=5000):
    error_list=[]
    pending_ships = WeigthUpdateHistory.objects.filter(status=0)[start_count:total]
    #return (pending_ships.count())
    for sh in  pending_ships:
        ship = Shipment.objects.filter(airwaybill_number=sh.airwaybill_number)
        if not ship:
            error_list.append(sh.airwaybill_number)
        else:
            if not ship[0].billing:
                ship.update(length = sh.length, breadth=sh.breadth, height=sh.height, actual_weight = sh.actual_weight, volumetric_weight = sh.volumetric_weight)
                ship = ship[0]
                if ShipmentBillingQueue.objects.filter(airwaybill_number=sh.airwaybill_number):
                    ShipmentBillingQueue.objects.filter(airwaybill_number=sh.airwaybill_number).update(status=0)
                else:
                    add_to_shipment_queue(sh.airwaybill_number)
            else:
                error_list.append(ship[0].airwaybill_number)
    if error_list:
          ecomm_send_mail(
            'Weight Update Queue error', '',
            ['jinesh@prtouch.com', 'birjus@ecomexpress.in','onkar@prtouch.com','jignesh@prtouch.com'],
            str(error_list)
        )
    return (error_list)           
