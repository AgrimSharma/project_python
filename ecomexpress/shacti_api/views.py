import json
import xlrd
import xmltodict
import xlwt
import utils
from datetime import timedelta, datetime
from xlsxwriter.workbook import Workbook
import dateutil.parser
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import get_model
from django.core.mail import send_mail
from models import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from django.core.mail import EmailMultiAlternatives

from jsonview.decorators import json_view

from privateviews.decorators import login_not_required
from track_me.models import *
from service_centre.models import *
from location.models import *
from pickup.models import PickupRegistration
from airwaybill.models import *

now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")
from reports.ecomm_mail import ecomm_send_mail
from django.utils import simplejson
from django.db.models import *
from django.contrib.auth.models import User, Group
from privateviews.decorators import login_not_required
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
import json
import csv
from delivery.models import *


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
from location.models import *
from collections import OrderedDict

def history_update_api(shipment, __status, employee_code = 124, remarks="", reason_code=None):
    now = datetime.datetime.now()
    employee_code = EmployeeMaster.objects.get(employee_code = employee_code)
    current_sc = employee_code.service_centre
    remarks = remarks
    if not shipment.added_on:
       shipment.added_on = now
    upd_time = shipment.added_on
    monthdir = upd_time.strftime("%Y_%m")
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
    shipment_history.objects.create(
        shipment=shipment, status=__status, employee_code=employee_code,
        current_sc=current_sc, expected_dod=shipment.expected_dod, 
        reason_code=reason_code, remarks=remarks
    )    
    Shipment.objects.filter(airwaybill_number=shipment.airwaybill_number).update(updated_on=now)
    ShipmentExtension.objects.filter(shipment_id=shipment.id).update(
        status_bk=__status, current_sc_bk=current_sc, 
        remarks=remarks, updated_on=now)

    reason = reason_code.code if reason_code else ''

    ShipmentBagHistory.objects.update_ship_history(
        shipment.airwaybill_number, __status, employee_code, reason, remarks,
        updated_on=now)
 

@csrf_exempt
def order_pricing_api(sh=None, type=0, employee_code = 124):
     if sh:
        awb= sh.airwaybill_number 
     else:
        return False

     employee = EmployeeMaster.objects.get(employee_code = employee_code)   
     sc = employee.service_centre
     ship = Shipment.objects.filter(airwaybill_number=awb, status__in=[0,1,2]).select_related('pickup__service_centre__center_shortcode','shipper__name', 'shipper__code').only('shipper__code','shipper__name','airwaybill_number','consignee','pieces','pickup__service_centre__center_shortcode','added_on','id','expected_dod','status_type','status','return_shipment','rts_status','reason_code','inscan_date','product_type','collectable_value','order_number','service_centre','actual_weight','pincode').exclude(status=9).exclude(reason_code__code__in = [333, 888, 999]).exclude(rts_status = 2)
     if not ship:
         return "Incorrect Airway Bill Number"
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
         ship.update(status=2, manifest_location = sc, current_sc=sc)
         if type == 1:
            history_update_api(shipment, 2, employe_code, "Shipment Auto in-scan", shipment.reason_code)
         else:
            history_update_api(shipment, 2, employe_code, "", shipment.reason_code)
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
        ship.update(status=2, manifest_location = sc, current_sc=sc)
     if type == 1:
            history_update_api(shipment, 2, employee_code, "Shipment Auto in-scan", shipment.reason_code)
     else:
          history_update_api(shipment, 2, employee_code, "", shipment.reason_code)
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




@login_not_required
@csrf_exempt
def get_pincodes(request):
    mylist=[]
    #srecords = OrderedDict()
    #return "hi"
    loca = Pincode.objects.all()
    for l in loca:
         srecords = {'pincode':l.pincode,"city":l.service_center.city.city_name,"dccode":l.service_center.center_name,"state":l.service_center.address.state.state_name,"routecode":l.pin_route}
         #srecords['pincode'] = l.pincode
         #srecords['city'] = l.service_center.city.city_name
         #srecords['dccode'] = l.service_center.center_name
         #srecords['state'] = l.service_center.address.state.state_name
         #srecords['routecode'] = l.pin_route
         mylist.append(srecords)
    import json
    #data = simplejson.dumps(mylist)
    #return data  
    return HttpResponse(simplejson.dumps(mylist),content_type="application/json")   
 
@login_not_required
@csrf_exempt
def add_to_history( awb, length, width, height, weight, employee_code ): 
   #if request.POST:
   #    capi =  api_auth(request)
   #    if not capi:
   #        return HttpResponse('{"success":"no","remarks":"Unauthorised Request"}', mimetype='application/json')
 
    if awb:
        update_date = datetime.datetime.now().strftime("%Y-%m-%d")
        update_time = datetime.datetime.now().strftime("%H:%M:%S")
        breadth = width
        actual_weight = weight
        volumetric_weight = 0
        volume = None

        if not awb or not update_date or not update_time or not length or not breadth or not height or not actual_weight  or not employee_code:
            #return HttpResponse("not enough data")
            return '{"success":"no","remarks":"not enough data"}'

        if not Shipment.objects.filter(airwaybill_number = awb):
            return '{"success":"no","remarks":"No Shipment Manifest in the System"}'

        if 1 == 1:
            #return HttpResponse("'%s  '"%(update_date+" "+update_time));
            ShactiWeigthUpdateHistory.objects.create(
                        airwaybill_number = awb,
                        update_date = datetime.datetime.strptime(update_date,'%Y-%m-%d').date(),
                        update_time = datetime.datetime.strptime((update_date+" "+update_time),'%Y-%m-%d %H:%M:%S'),
                        length = float(length)/10,
                        breadth = float(breadth)/10,
                        height = float(height)/10,
                        actual_weight = actual_weight,
                        volumetric_weight = volumetric_weight,
                        volume = 0,
                        employee_code = employee_code,
            )
            return '{"success":"yes","remarks":"record inserted"}'
        else:  
            return '{"success":"no","remarks":"formating error"}'
    #return HttpResponse("no post input")
    return '{"success":"no","remarks":"no input data"}'



def process_weight_update_queue(start_count=0,total=5000):
    error_list=[]
    pending_ships = ShactiWeigthUpdateHistory.objects.filter(status=0)[start_count:total]
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
@csrf_exempt
@login_not_required
def failed_csv(request):
    resp='no request'
    if request.FILES:
      upload_file_1 = request.FILES['upload_file']
      file_contents_1 = upload_file_1.read()
      if file_contents_1 :
         #resp= file_contents_1
            resp='Upload succeeded'
         #ecomm_send_mail('Failed CSV', '', ['theonkar10@gmail.com','onkar@prtouch.com'],
         #str(file_contents_1))
                     #ecomm_send_mail('Successfull CSV', '', ['theonkar10@gmail.com','onkar@prtouch.com'],
            #str(file_contents_1))
            #resp=file_contents_1
            #resp='Upload succeeded'  
            html = file_contents_1
            mail_ids = ['theonkar10@gmail.com','onkar@prtouch.com']
            #mail_ids = ['sunainas@ecomexpress.in', 'manjud@ecomexpress.in', 'veenav@ecomexpress.in', 'jignesh@prtouch.com', 'suprotip@prtouch.com', 'onkar@prtouch.com']
            #dbg_ml=['suprotip@gmail.com', 'theonkar10@gmail.com']
            msg =MIMEMultipart()
            html =MIMEText(html, 'html')
            #msg['Subject'] = 'Performance customer report'
    
            msg['From']='support@prtouch.com'
            msg = EmailMultiAlternatives('failed  uploaded report', html, msg['From'], mail_ids)

            msg.attach_alternative(file_contents_1, "text/html")
            msg.send()
            #print "done"
            return HttpResponse(resp)

      else:
         resp = 'Upload failed'
    else:
        resp = "Unable to process the request"
        #return HttpResponse(resp)
    return HttpResponse(resp)

@csrf_exempt
@json_view
def add_bagging_api(bag_type="destination", bag_size="medium", bag_number = "", hub = 0, destination = "", employee_code = 124):
    
    employee = EmployeeMaster.objects.get(employee_code = employee_code)   
    if Bags.objects.filter(bag_number=bag_number).exists():
        return {'success': False, 'message': 'Bag number already exists'}

    #return {'success': False, 'message': 'Bag number already exists'}

    if not bag_number:
        return {'success': False, 'message': 'Bag_number Empty'}
        
    origin = employee.service_centre 
    if int(hub):
        hub = ServiceCenter.objects.get(id=int(hub))
    else:
        hub = None 

    if (destination):
        destination = ServiceCenter.objects.get(center_shortcode=(destination))
    else:
        return {'success': False, 'message': 'no destination provided'}

    #print employee
    #return True

    bag = Bags.objects.create(
        bag_number=bag_number, bag_type=bag_type, bag_size=bag_size,
        origin=origin, hub=hub, destination=destination, current_sc=origin, employee_code=employee)

    update_bag_history(
        bag, employee=employee, action="created",
        content_object=bag, sc=employee,
        status=1)

    html = render_to_string(
        "service_centre/bag_data.html", {'a':bag},
        context_instance=RequestContext(request))

    return {'success': True, 'html': html}


@csrf_exempt
def include_shipment_in_bag_api(awb=0,bid=0, employee_code = 124):
    bags = Bags.objects.filter(bag_number=bid)
    if bags:
        bags = bags[0]
        if bags.bag_status in [1, 6]:
            return "Bag is already closed"
        if not awb:
            return "AWB not provided"
        awb_number= awb
        if bags.bag_type == "mixed":
            try:
                shipment = Shipment.objects.filter(airwaybill_number=awb_number)\
                    .exclude(status=9)\
                    .exclude(reason_code__code__in = [333, 888, 999])\
                    .exclude(rts_status = 2)
                if not shipment:
                    return "Soft Data not Uploaded"
                if not Pincode.objects.filter(pincode=shipment[0].pincode):
                    return "Non Serviceable pincode"

                if shipment[0].status in [3, 5]:
                    bag = shipment[0].bags_set.all()
                    if bag.exists():
                        return "Shipment already bagged in bag number %s"%(bag[0].bag_number)
                shipment = shipment.get(status__in=[0,1,2,4])
            except:
                return "Incorrect Shipment Number"
        else:
            try:
                shipment = Shipment.objects.filter(
                    airwaybill_number=awb_number
                ).exclude(status=9).exclude(
                    reason_code__code__in = [333, 888, 999]
                ).exclude(rts_status = 2)
                if not shipment:
                    return "Soft Data not Uploaded"
                if not Pincode.objects.filter(pincode=shipment[0].pincode):
                    return "Non Serviceable pincode"
                shipment = shipment.get(service_centre=bags.destination, status__in=[0,1,2,4])
            except:
               return "Incorrect Shipment Number"

        if shipment.status in [0,1]:
            order_pricing_api(shipment, 1, employee_code)
        if shipment.status_type in [0,1]:
            bag_no = bags.bag_number if bags.bag_number else bags.id
            if shipment.status in [0,1,2]:
                Shipment.objects.filter(id=shipment.id).update(status_type=0, status=3)
                if bags.hub:
                     dst = bags.hub
                else:
                     dst = bags.destination
                history_update_api(shipment, 3, employee_code, "Shipment connected to %s (Bag No. %s)"%(dst, bag_no))
            elif shipment.status == 4:
                Shipment.objects.filter(id=shipment.id).update(status_type=0, status=5)
                history_update_api(shipment, 5, employee_code, "Shipment connected from HUB (Bag No. %s)"%(bag_no))

            bags.shipments.add(shipment)
            bags.ship_data.add(shipment)
            return True
           #return render_to_response(
           #    "service_centre/shipment_bagging_data.html",
           #    {'shipment':shipment},
           #    context_instance=RequestContext(request)
           #)
        else:
            return 'Invalid Airwaybill number'
    else:
        shipment = bags.shipments.filter()
        shipment_count = shipment.count()
        return True
       #return render_to_response(
       #    "service_centre/include_shipment.html",
       #    {'bags':bags, 'shipment':shipment, 
       #        'shipment_count':shipment_count, 'bid':bid},
       #    context_instance=RequestContext(request)
       #)



@csrf_exempt
@json_view
def close_bagging_api(bag_number, employee_code):
    #if not request.method == 'POST':
    #    return {'success': False, 'message':'Not an authorized request'}
 
    if not bag_number:
        return {'success': False, 'message':'Not an authorized request'}

    bag_id = bag_number
    employee = EmployeeMaster.objects.filter(employee_code = employee_code)
    if employee:
        employee = employee[0]
    else:
        employee = None
    #bag_number = request.POST['bag_number']
    #match = re.match(r'\w+$', bag_number)
    #if not match:
        #return {'success': False, 'message':'Invalid Bag number. Only Alapha numerals allowed.'}
    #bag_number = match.group()

    bag = Bags.objects.get(bag_number=bag_id)
    if bag.bag_status in [1, 6]:
        return {'success': False, 'message': 'Bag already closed.'}

    #if Bags.objects.filter(bag_number=bag_number).exists():
    #    return {'success': False, 'message': 'Bag number already exists'}

    weight_sum =  bag.shipments.aggregate(Sum('actual_weight'))['actual_weight__sum']
    if bag.bag_status == 5:
        bag_status = 6
    else:
        bag_status = 1

    Bags.objects.filter(id=bag.id).update(
        bag_status=bag_status,  actual_weight=weight_sum,
        employee_code=employee
    )
    bag = Bags.objects.get(id=bag.id)
    update_bag_history(
        bag, employee=employee,
        action="closed (No. of Shipments - %s)"%(bag.shipments.count()),
        content_object=bag, sc=employee.service_centre,
        status=2
    )
    update_bag_remarks(bag.bag_number, 1)
    update_trackme_bagging_remarks(bag.bag_number)
    return {'success': True, 'bag_number': bag.bag_number, 'message': 'Bag closed'}

@csrf_exempt
@login_not_required
def success_csv(request):
    
    if not request.FILES:
        return render_to_response("shacti/file_upload.html",
                                  )
        
    if request.FILES:
        upload_file = request.FILES['upload_file']
    else: 
        return HttpResponse("File not found")

    file_contents = csv.reader(upload_file)
    if not file_contents :
        return HttpResponse("File not found")


    #return HttpResponse("======%s" % csv.reader(file_contents)) 
    bag_list = {}
    header = ["awb","length","width","height","weight","inscanned_timestamp","primary_sort_timestamp","in_bag_timestamp","manifested_timestamp","bag_closed_timestamp","bag_number","bag_dest","putbaguser","closebaguser"]
    resp='no request'
    count = 0 
    for row in file_contents:
        if row[0] == "AWB": 
            continue
        awb_detail = dict(zip(header,row)) 

        if not EmployeeMaster.objects.filter(employee_code = awb_detail["putbaguser"]):
            awb_detail["putbaguser"] = 124
        if not EmployeeMaster.objects.filter(employee_code = awb_detail["closebaguser"]):
            awb_detail["closebaguser"] = 124
        #return HttpResponse("======%s" % awb_detail)
        #exit()
        if ShactiSortedAwb.objects.filter(airwaybill_number = awb_detail["awb"], bag_id = awb_detail["bag_number"]):
            print "Already processed"
            continue
            

        #return HttpResponse("%s" % "----")
        shipment = Shipment.objects.filter(airwaybill_number = awb_detail["awb"])
        if not shipment:
            continue
        shipment =shipment[0]
        
        bags = Bags.objects.filter(bag_number = awb_detail["bag_number"])
        ip = request.META['REMOTE_ADDR']
        ftp_details = SchactiFTPDetails.objects.filter(ftp_ip_address = ip)
        hub = 0
        if ftp_details :
            hub = ServiceCenter.objects.filter(center_shortcode= ftp_details.hub)
            if hub :
                hub = hub.id
        if not bags:
            add_bagging_api_response = add_bagging_api("destination", "medium", awb_detail["bag_number"], 0, awb_detail["bag_dest"], awb_detail["putbaguser"])
            #return HttpResponse("%s" % add_bagging_api_response)
        bags = Bags.objects.get(bag_number = awb_detail["bag_number"])
        bag_list[awb_detail["bag_number"]] = awb_detail["putbaguser"]

        include_shipment_in_bag_api(awb_detail["awb"],bags.bag_number, awb_detail["putbaguser"])

        add_to_history( awb_detail["awb"], awb_detail["length"], awb_detail["width"], awb_detail["height"], awb_detail["weight"], awb_detail["putbaguser"] ) 
        length = 0
        breadth = 0
        height = 0
        actual_weight = 0
        if awb_detail["length"]: 
            length = awb_detail["length"]
        if awb_detail["width"]: 
            breadth = awb_detail["width"]
        if awb_detail["height"]: 
            height = awb_detail["height"]
        if awb_detail["weight"]: 
            actual_weight = awb_detail["weight"]

        ShactiSortedAwb.objects.create(
                 airwaybill_number = awb_detail["awb"], 
                 length = length, 
                 breadth = breadth, 
                 height = height, 
                 actual_weight = actual_weight, 
                 volumetric_weight = 0,
                 volume  = 0,
                 employee_code  = awb_detail["putbaguser"],
                 inscanned_timestamp  = datetime.datetime.strptime(awb_detail["inscanned_timestamp"], "%Y-%m-%d %H:%M:%S"), 
                 #primary_sort_timestamp  = datetime.datetime.strptime(awb_detail["primary_sort_timestamp"], "%Y-%m-%d %H:%M:%S"), 
                 in_bag_timestamp   = datetime.datetime.strptime(awb_detail["in_bag_timestamp"], "%Y-%m-%d %H:%M:%S"), 
                 manifested_timestamp   = datetime.datetime.strptime(awb_detail["manifested_timestamp"], "%Y-%m-%d %H:%M:%S"), 
                 bag_closed_timestamp   = datetime.datetime.strptime(awb_detail["bag_closed_timestamp"], "%Y-%m-%d %H:%M:%S"), 
                 bag_id = awb_detail["bag_number"])
    for bag_number, employee_code in bag_list.iteritems():
        close_bagging_api_response = close_bagging_api(bag_number, employee_code)
        #return HttpResponse("{'success': True, 'message': 'Bag number.%s - %s'}" % (bag_list,close_bagging_api_response))
 
    return HttpResponse("{'success': True, 'message': 'Shipments processed successfully.%s'}" % bag_list)
        #break
