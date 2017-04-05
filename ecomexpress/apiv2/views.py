# Create your views here.
import json
import xmltodict
import utils
from datetime import timedelta, datetime
import dateutil.parser
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import *
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
from django.contrib.auth.models import User, Group
from customer.models import *
from ecomm_admin.models import *
from billing.models import Billing, BillingSubCustomer
from ecomexpress.utils import *
from api.utils import api_auth
from billing.models import ShipmentBillingQueue

from location.models import *
from collections import OrderedDict
from service_centre.transitmaster import get_expected_dod
from amazon_api.utils import validate_awb
from integration_services.utils import get_or_create_vendor

@login_not_required
@csrf_exempt
def pincode_pickup_create(record, capi, reverse_pickup):
    now = datetime.datetime.now()
    to_time_obj = now + datetime.timedelta(days=1)
    from_time=now.strftime("%Y-%m-%d")
    to_time=to_time_obj.strftime("%Y-%m-%d")
    pickup_dict = {}
    subcustomer_list = {}
    now = datetime.datetime.now()
    error = False

    try:
        pincode = Pincode.objects.get(pincode = int(record["PICKUP_PINCODE"]))
    except:
        error = True
    name = record["PICKUP_NAME"]
    address = ""
    address_1 = str(record["PICKUP_ADDRESS_LINE1"])
    address_2 = str(record["PICKUP_ADDRESS_LINE2"])
 
   
    if address_1 and address_2:
        address = address_1 +" "+ address_2
    elif not address_2:
        address = address_1
    elif not address_1:
        address = address_2
    else:
        #HttpResponse("Address not found in XML, please check address.")
        error = True

    return_pincode = False
    if record["RETURN_PINCODE"]:
        return_pincode = Pincode.objects.filter(pincode = int(record["RETURN_PINCODE"]))
    if return_pincode:
        return_pincode = str(record["RETURN_PINCODE"])
        return_name = record["RETURN_NAME"]
        return_phone = record["RETURN_PHONE"]
        return_address = ""
        return_address_1 = str(record["RETURN_ADDRESS_LINE1"])
        return_address_2 = str(record["RETURN_ADDRESS_LINE2"])
        if return_address_1 and return_address_2:
            return_address = return_address_1 +" "+ return_address_2
        elif not return_address_2:
            return_address = return_address_1
        elif not return_address_1:
            return_address = return_address_2
     


    phone = record["PICKUP_PHONE"]
    pincode = str(record["PICKUP_PINCODE"])
    customer_code = capi.customer.code
    
    #sub_customer_id = get_vendor(name,address,phone,pincode,customer_code,return_pincode=0)
    subcustomer = get_or_create_vendor( name=name, customer=capi.customer, pincode=pincode, address=address, phone=phone)
    subcustomer_id = subcustomer.id
    if return_pincode:
        return_subcustomer = get_or_create_vendor( name=return_name, customer=capi.customer, pincode=return_pincode, address=return_address, phone=return_phone)
    else:
        return_subcustomer = subcustomer
    return_subcustomer_id = return_subcustomer.id
    pickup = PickupRegistration.objects.filter(customer_code = capi.customer,
             subcustomer_code_id=subcustomer_id, return_subcustomer_code_id = return_subcustomer_id, pincode = pincode, status=0).filter(Q(pickup_time__gte="07:00:00", 
             pickup_date=from_time) & Q(pickup_time__lte="07:00:00", pickup_date=to_time)).filter(reverse_pickup=reverse_pickup).\
             order_by("-pickup_date", "-pickup_time")

    if pickup:
        pickup = pickup[0]
    else:
        #pincode_sc_map = PickupPincodeServiceCentreMAP.objects.filter(pincode = int(record["PICKUP_PINCODE"]))
         
        pincode = Pincode.objects.get(pincode = pincode)
        #return_pincode = Pincode.objects.get(pincode = return_pincode)
        
        #if pincode_sc_map :
        if  pincode.pickup_sc:
            sc = pincode.pickup_sc
        else:
            sc = pincode.service_center
            
        pickup_phone = "" 
        if record["PICKUP_PHONE"]:
            pickup_phone = record["PICKUP_PHONE"].replace("-","")
            pickup_phone = pickup_phone.replace(" ","")
        pickup = PickupRegistration.objects.create(customer_code=capi.customer,subcustomer_code=subcustomer,return_subcustomer_code=return_subcustomer,
                 pickup_time=now,pickup_date=now,mode_id=1,customer_name=record["PICKUP_NAME"],
                 address_line1=record["PICKUP_ADDRESS_LINE1"],address_line2=record["PICKUP_ADDRESS_LINE2"],
                 pincode=record["PICKUP_PINCODE"],
                 mobile=record["PICKUP_MOBILE"],telephone=pickup_phone,pieces=4,
                 actual_weight=1.2,volume_weight=2.1,service_centre=sc, reverse_pickup=reverse_pickup)
    pickup_dict[record["PICKUP_PINCODE"]] = pickup

    return (pickup_dict, error)




def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        #raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return False

@login_not_required
@csrf_exempt
def get_pincodes_all(request):
    q = Q()
    if not request.POST:
        return HttpResponse("%s"%"Page not found!")
    if request.POST:
        capi =  api_auth(request)
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")
        if request.POST.get("date"): 
            if not validate_date(request.POST.get("date")): 
                return HttpResponse("%s"%"invalid date field")
            q = q & Q(added_on__gte = request.POST.get("date"))
        if request.POST.get("state"): 
            q = q & Q(service_center__city__state__state_shortcode = request.POST.get("state"))

    mylist=[]
    location = Pincode.objects.filter(status=1).filter(q).values("pincode", "service_center__city__city_name", "service_center__city__city_shortcode", "service_center__center_shortcode",  "service_center__city__state__state_name", "service_center__city__state__state_shortcode", "date_of_discontinuance", "pin_route__pinroute_name")
    for l in location:
         srecords = {'pincode':l['pincode'],"city":l['service_center__city__city_name'],"state":l['service_center__city__state__state_name'],"city_code":l['service_center__city__city_shortcode'],"dccode":l['service_center__center_shortcode'],"state_code":l['service_center__city__state__state_shortcode'],"date_of_discontinuance":l['date_of_discontinuance'],"route":l['service_center__city__state__state_shortcode']+"/"+l['service_center__city__city_shortcode']}
         mylist.append(srecords)
    return HttpResponse(simplejson.dumps(mylist),content_type="application/json")   
 

@login_not_required
@csrf_exempt
def get_pincodes_state(request):
    if not request.POST:
        return HttpResponse("%s"%"Page not found!")
    if request.POST:
        capi =  api_auth(request)
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")
        if not request.POST.get("state_code"):
            return HttpResponse("%s"%"empty state_code field")

    mylist=[]
    location = Pincode.objects.filter(status=1, service_center__city__state__state_shortcode = request.POST.get("state_code")).values("pincode", "service_center__city__city_name", "service_center__city__city_shortcode", "service_center__center_shortcode",  "service_center__city__state__state_name", "service_center__city__state__state_shortcode", "date_of_discontinuance", "pin_route__pinroute_name")
    for l in location:
         srecords = {'pincode':l['pincode'],"city":l['service_center__city__city_name'],"state":l['service_center__city__state__state_name'],"city_code":l['service_center__city__city_shortcode'],"dccode":l['service_center__center_shortcode'],"state_code":l['service_center__city__state__state_shortcode'],"date_of_discontinuance":l['date_of_discontinuance'],"route":l['pin_route__pinroute_name']}
         mylist.append(srecords)
    return HttpResponse(simplejson.dumps(mylist),content_type="application/json")   
 

@login_not_required
@csrf_exempt
def get_pincodes_date(request):
    if not request.POST:
        return HttpResponse("%s"%"Page not found!")
    if request.POST:
        capi =  api_auth(request)
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")
        if not request.POST.get("date"):
            return HttpResponse("%s"%"empty date field")
        if not validate_date(request.POST.get("date")): 
            return HttpResponse("%s"%"invalid date field")

    mylist=[]
    location = Pincode.objects.filter(status=1, added_on__gte = request.POST.get("date")).values("pincode", "service_center__city__city_name", "service_center__city__city_shortcode", "service_center__center_shortcode",  "service_center__city__state__state_name", "service_center__city__state__state_shortcode", "date_of_discontinuance", "pin_route__pinroute_name")
    for l in location:
         srecords = {'pincode':l['pincode'],"city":l['service_center__city__city_name'],"state":l['service_center__city__state__state_name'],"city_code":l['service_center__city__city_shortcode'],"dccode":l['service_center__center_shortcode'],"state_code":l['service_center__city__state__state_shortcode'],"date_of_discontinuance":l['date_of_discontinuance'],"route":l['pin_route__pinroute_name']}
         mylist.append(srecords)
    return HttpResponse(simplejson.dumps(mylist),content_type="application/json")   
 
@login_not_required
@csrf_exempt
def get_awb(request):
    if not request.POST:
        return HttpResponse("%s"%"Page not found!")
    if request.POST:
        capi =  api_auth(request)
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")
        error = []
        if not request.POST.get("count"):
            error.append("empty count field")
        elif not request.POST.get("count").isdigit():
            error.append("invalid count")
        elif int(request.POST.get("count")) > 100000:
            error.append("request count %s exceeds 100000" % (int(request.POST.get("count")) > 100000))
        if not request.POST.get("type"): 
            error.append("empty type field")
        elif request.POST.get("type").lower() not in ["cod","ppd","rev"]: 
            error.append("invalid type field")
    else:
        return render_to_response('invalid request')

    if error:
        error_response = {}
        error_response["success"] = "no"
        error_response["error"] = error
        return HttpResponse(simplejson.dumps(error_response), mimetype='application/json')

    #awb_numbers = AirwaybillNumbers.objects.filter(awbc_info__customer=Customer.objects.get(id=capi.customer.id), status = 0).values("awbc_info__customer").annotate(count=Count("airwaybill_number"))
    awb_numbers = AirwaybillNumbers.objects.filter(awbc_info__customer_id=capi.customer.id, status = 0).values("awbc_info__customer").annotate(count=Count("airwaybill_number"))
    unused_limit =  capi.customer.customerawbusedlimit_set.all()
    
    if unused_limit :
        unused_limit = unused_limit[0].awb_limit
    else:
        if capi.customer_id == 6:
            unused_limit = 100000
        else:
            unused_limit = 5000
    #return HttpResponse("%s---" %  unused_limit)
    if awb_numbers[0]['count'] > unused_limit and capi.customer_id != 12:
        return HttpResponse('{"success":"no","error":["Limit Exceeded"]}', mimetype='application/json')

    product_type = {}
    product_type['ppd'] = 1
    product_type['cod'] = 2
    product_type['rev'] = 3

    count = request.POST['count']
    ship_type = request.POST['type'].lower()

        
    awbc = AirwaybillCustomer.objects.create(customer=capi.customer, type=product_type[ship_type], quantity=count)
    if product_type[ship_type] == 1:
        awb_start = PPD.objects.latest('id').id + 1
        awb_total_ids = [PPD(id=i) for i in range(awb_start, int(awb_start) + int(count))]
        awb_objs = PPD.objects.bulk_create(awb_total_ids)
    if product_type[ship_type] == 2:
        awb_start = COD.objects.latest('id').id + 1
        awb_total_ids = [COD(id=i) for i in range(awb_start, int(awb_start) + int(count))]
        awb_objs = COD.objects.bulk_create(awb_total_ids)
    if product_type[ship_type] == 3:
        awb_start = ReversePickup.objects.latest('id').id + 1
        awb_total_ids = [ReversePickup(id=i) for i in range(awb_start, int(awb_start) + int(count))]
        awb_objs = ReversePickup.objects.bulk_create(awb_total_ids)


    awb_ids = [a.id for a in awb_objs]
    airs = [AirwaybillNumbers(airwaybill_number=a) for a in awb_ids]
    awbs = AirwaybillNumbers.objects.bulk_create(airs)
    awb_nums = [a.airwaybill_number for a in awbs]
    awb_objs = AirwaybillNumbers.objects.filter(airwaybill_number__in=awb_nums)
    awbc.airwaybill_number = awb_objs
    awbc.save()

    success_response = {};
    success_response["success"] = "yes"
    success_response["reference_id"] = awbc.id
    success_response["awb"] = awb_nums
    
    return HttpResponse(simplejson.dumps(success_response),content_type="application/json")

@login_not_required
@csrf_exempt
def cancel_rto_awb(request):
    q = Q()
    #return HttpResponse("%s"%"Page not found!")
    if not request.POST:
        return HttpResponse("%s"%"Page not found!")
    if request.POST:
        capi =  api_auth(request)
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")
        if not request.POST.get("awbs"): 
            return HttpResponse("%s"%"No data")
        awbs = request.POST.get("awbs").split(",")

        #return HttpResponse("---%s----" % request)
        #response = {}
        response_list = []

        for awb in awbs:
            response = {}
            s = Shipment.objects.filter(airwaybill_number = awb)
            #return HttpResponse("---%s----%s" % (s.count(), awb))
            #return HttpResponse("%s----" % awbs)
            if s:
                #return HttpResponse("%s----" % awb)
                s = s[0]
                if s.rts_status == 2:
                    response["awb"] = awb
                    response["success"] = False
                    response["reason"] = "AIRWAYBILL_NUMBER_RETURNED"
                    continue
                if s.status == 9:
                    response["awb"] = awb
                    response["success"] = False
                    response["reason"] = "AIRWAYBILL_NUMBER_ALREADY_DELIVERED"
                    continue
                if s.status == 7:
                    response["awb"] = awb
                    response["success"] = False
                    response["reason"] = "AIRWAYBILL_NUMBER_OUT_FOR_DELIVERY"
                    continue
                shipment_cancel_queue = ShipmentCancelQueue.objects.filter(airwaybill_number = awb)
                if not shipment_cancel_queue:
                    ShipmentCancelQueue.objects.create(airwaybill_number = awb, status=0)
                
                response["awb"] = awb
                response["success"] = True
                response["reason"] = ""
            else:
                response["awb"] = awb
                response["success"] = False
                response["reason"] = "INVALID_AWB_NUMBER"
            response_list.append(response)
                
    return HttpResponse(simplejson.dumps(response_list),content_type="application/json")   
 



@login_not_required
@csrf_exempt
def api_manifest_awb_shipment(request):
    """
    This is the manifest API.
    """
    if not request.POST:
        return HttpResponse("%s"%"Page not found!")
    pid=1
    awb_overweight=[]
    subCustomers_list=[]
    capi = False
    f = open("/tmp/apitest","w")
    f.write("%s" % request)
    f.close()

    response_awb = {}
    response_awb["shipments"] = []
    #return HttpResponse("%s"%request.POST)
    if request.POST :
#        uname = (file_contents['SOAP-ENV:Envelope']['username'])
#        password = (file_contents['SOAP-ENV:Envelope']['password'])
        username = request.POST.get('username', None)
        if not username:
            username = request.GET.get('username', None)

        if username.strip().lower() == 'ecomexpress':
            capi = CustomerAPI.objects.get(username='ecomexpress')    
        else:
            capi =  api_auth(request)
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")

    '''
{

    "SHIPMENT": [{
      "AWB_NUMBER": "923712739",
      "ORDER_NUMBER": "7677",
      "PRODUCT": "PPD",
      "CONSIGNEE": "TEST",
      "CONSIGNEE_ADDRESS1": "ADDR1",
      "CONSIGNEE_ADDRESS2": "ADDR2",
      "CONSIGNEE_ADDRESS3": "ADDR3",
      "DESTINATION_CITY": "MUMBAI",
      "PINCODE": "400067",
      "STATE": "MH",
      "MOBILE": "156729",
      "TELEPHONE": "1234",
      "ITEM_DESCRIPTION": "MOBILE ",
      "PIECES": "1",
      "COLLECTABLE_VALUE": " 3000 ",
      "DECLARED_VALUE": " 3000 ",
      "ACTUAL_WEIGHT": "5",
      "VOLUMETRIC_WEIGHT": "0",
      "LENGTH": " 10",
      "BREADTH": "10",
      "HEIGHT": "10",
      "PICKUP_NAME": "abcde",
      "PICKUP_ADDRESS_LINE1": "Samalkha",
      "PICKUP_ADDRESS_LINE2": "kapashera",
      "PICKUP_PINCODE": "110013",
      "PICKUP_PHONE": "98204",
      "PICKUP_MOBILE": "59536",
      "RETURN_NAME": "abcde",
      "RETURN_ADDRESS_LINE1": "Samalkha",
      "RETURN_ADDRESS_LINE2": "kapashera",
      "RETURN_PINCODE": "110013",
      "RETURN_PHONE": "98204",
      "RETURN_MOBILE": "59536"
    },{
      "AWB_NUMBER": "923712739",
      "ORDER_NUMBER": "7677",
      "PRODUCT": "PPD",
      "CONSIGNEE": "TEST",
      "CONSIGNEE_ADDRESS1": "ADDR1",
      "CONSIGNEE_ADDRESS2": "ADDR2",
      "CONSIGNEE_ADDRESS3": "ADDR3",
      "DESTINATION_CITY": "MUMBAI",
      "PINCODE": "400067",
      "STATE": "MH",
      "MOBILE": "156729",
      "TELEPHONE": "1234",
      "ITEM_DESCRIPTION": "MOBILE ",
      "PIECES": "1",
      "COLLECTABLE_VALUE": " 3000 ",
      "DECLARED_VALUE": " 3000 ",
      "ACTUAL_WEIGHT": "5",
      "VOLUMETRIC_WEIGHT": "0",
      "LENGTH": " 10",
      "BREADTH": "10",
      "HEIGHT": "10",
      "PICKUP_NAME": "abcde",
      "PICKUP_ADDRESS_LINE1": "Samalkha",
      "PICKUP_ADDRESS_LINE2": "kapashera",
      "PICKUP_PINCODE": "110013",
      "PICKUP_PHONE": "98204",
      "PICKUP_MOBILE": "59536",
      "RETURN_NAME": "abcde",
      "RETURN_ADDRESS_LINE1": "Samalkha",
      "RETURN_ADDRESS_LINE2": "kapashera",
      "RETURN_PINCODE": "110013",
      "RETURN_PHONE": "98204",
      "RETURN_MOBILE": "59536"
    }]
}
    '''

    #return HttpResponse("Incomplete or no input provided. %s" % request.GET)
    if not capi or  not request.POST.get('json_input'):
        return HttpResponse("Incomplete or no input provided.")
    json_shipments = request.POST['json_input']
    dict_shipments = simplejson.loads(json_shipments)
    #xmlshipments = simplejson.loads('{ "SHIPMENT": [{ "AWB_NUMBER": "923712739", "ORDER_NUMBER": "7677", "PRODUCT": "PPD", "CONSIGNEE": "TEST", "CONSIGNEE_ADDRESS1": "ADDR1", "CONSIGNEE_ADDRESS2": "ADDR2", "CONSIGNEE_ADDRESS3": "ADDR3", "DESTINATION_CITY": "MUMBAI", "PINCODE": "400067", "STATE": "MH", "MOBILE": "156729", "TELEPHONE": "1234", "ITEM_DESCRIPTION": "MOBILE ", "PIECES": "1", "COLLECTABLE_VALUE": " 3000 ", "DECLARED_VALUE": " 3000 ", "ACTUAL_WEIGHT": "5", "VOLUMETRIC_WEIGHT": "0", "LENGTH": " 10", "BREADTH": "10", "HEIGHT": "10", "PICKUP_NAME": "abcde", "PICKUP_ADDRESS_LINE1": "Samalkha", "PICKUP_ADDRESS_LINE2": "kapashera", "PICKUP_PINCODE": "110013", "PICKUP_PHONE": "98204", "PICKUP_MOBILE": "59536", "RETURN_NAME": "abcde", "RETURN_ADDRESS_LINE1": "Samalkha", "RETURN_ADDRESS_LINE2": "kapashera", "RETURN_PINCODE": "110013", "RETURN_PHONE": "98204", "RETURN_MOBILE": "59536" },{ "AWB_NUMBER": "923712739", "ORDER_NUMBER": "7677", "PRODUCT": "PPD", "CONSIGNEE": "TEST", "CONSIGNEE_ADDRESS1": "ADDR1", "CONSIGNEE_ADDRESS2": "ADDR2", "CONSIGNEE_ADDRESS3": "ADDR3", "DESTINATION_CITY": "MUMBAI", "PINCODE": "400067", "STATE": "MH", "MOBILE": "156729", "TELEPHONE": "1234", "ITEM_DESCRIPTION": "MOBILE ", "PIECES": "1", "COLLECTABLE_VALUE": " 3000 ", "DECLARED_VALUE": " 3000 ", "ACTUAL_WEIGHT": "5", "VOLUMETRIC_WEIGHT": "0", "LENGTH": " 10", "BREADTH": "10", "HEIGHT": "10", "PICKUP_NAME": "abcde", "PICKUP_ADDRESS_LINE1": "Samalkha", "PICKUP_ADDRESS_LINE2": "kapashera", "PICKUP_PINCODE": "110013", "PICKUP_PHONE": "98204", "PICKUP_MOBILE": "59536", "RETURN_NAME": "abcde", "RETURN_ADDRESS_LINE1": "Samalkha", "RETURN_ADDRESS_LINE2": "kapashera", "RETURN_PINCODE": "110013", "RETURN_PHONE": "98204", "RETURN_MOBILE": "59536" }] }')

    #awb_validation = {}
    for awb_details in dict_shipments:
        awb_validation = {}
        #return HttpResponse("%s" % simplejson.dumps([str(capi.customer_id),awb_details["AWB_NUMBER"], awb_details["PINCODE"], awb_details["PICKUP_PINCODE"], awb_details["RETURN_PINCODE"], awb_details["ACTUAL_WEIGHT"], awb_details["PRODUCT"], awb_details["COLLECTABLE_VALUE"]]))
        awb_validation_response = validate_awb([str(capi.customer_id),awb_details["AWB_NUMBER"], awb_details["PINCODE"], awb_details["PICKUP_PINCODE"], awb_details["RETURN_PINCODE"], awb_details["ACTUAL_WEIGHT"], awb_details["PRODUCT"], awb_details["COLLECTABLE_VALUE"]])
        #awb_validation_response = '{ "success": true, "reason": "Invalid_PINCODE INVALID_COLLECTED_AMOUNT INVALID_VENDOR" }'
        #return HttpResponse("%s" % awb_validation_response)
        awb_validation_response = simplejson.loads(awb_validation_response)
        awb_num = AirwaybillNumbers.objects.filter(airwaybill_number=awb_details["AWB_NUMBER"], awbc_info__customer_id = capi.customer_id)
        if not awb_num: 
            awb_validation["awb"] = awb_details["AWB_NUMBER"] 
            awb_validation["order_number"] = awb_details["ORDER_NUMBER"] 
            awb_validation["success"] = False
            awb_validation["reason"] = "INCORRECT_AWB_NUMBER"
            
            response_awb["shipments"].append(awb_validation)
            continue

 
        if awb_validation_response["SUCCESS"]:
           #awb_validation[awb_details["AWB_NUMBER"]] = {}
           #awb_validation[awb_details["AWB_NUMBER"]]["success"] = True
           #awb_validation[awb_details["AWB_NUMBER"]]["reason"] = "Updated Successfully" 
            
            awb_validation["awb"] = awb_details["AWB_NUMBER"]
            awb_validation["order_number"] = awb_details["ORDER_NUMBER"] 
            awb_validation["success"] = True
            awb_validation["reason"] = "Updated Successfully" 

            airwaybill_num =  int(awb_details["AWB_NUMBER"])

                #pickup_data, error = pickup_create(subcustomer_check)
            #return HttpResponse("%s" %awb_details)
            
            pickup_data, error = pincode_pickup_create(awb_details, capi, 0)
            #return HttpResponse(file_contents['ECOMEXPRESS-OBJECTS']['SHIPMENT'])
            if error:
                return HttpResponse(str(error))            
            pickup = pickup_data.get(awb_details["PICKUP_PINCODE"])

            order_num = repr(awb_details["ORDER_NUMBER"])
            product_type = awb_details["PRODUCT"]
            product_type = product_type.lower()
            #if str(airwaybill_num)[0] in ["1","2","3"]:
            #       product_type="ppd"
            #elif str(airwaybill_num)[0] in ["7","8","9"]:
            #       product_type="cod"

            shipper = pickup.customer_code

            consignee = awb_details["CONSIGNEE"]
            consignee_address1 = awb_details["CONSIGNEE_ADDRESS1"]
            consignee_address2 = awb_details["CONSIGNEE_ADDRESS2"]
            consignee_address3 = awb_details["CONSIGNEE_ADDRESS3"]
                    
            destination_city = awb_details["DESTINATION_CITY"]
            pincode = awb_details["PINCODE"]
            state = awb_details["STATE"]
            mobile = awb_details["MOBILE"] if awb_details["MOBILE"] else 0
            telephone = awb_details["TELEPHONE"]
            item_description = awb_details["ITEM_DESCRIPTION"]
            pieces = awb_details["PIECES"]
            collectable_value = awb_details["COLLECTABLE_VALUE"] if awb_details["COLLECTABLE_VALUE"] else 0
            try:
                    int(collectable_value)
            except ValueError:
                    collectable_value = collectable_value.replace(",", "")

            declared_value = awb_details["DECLARED_VALUE"] if awb_details["DECLARED_VALUE"] else 0
            try:
                    int(declared_value)
            except ValueError:
                  declared_value = declared_value.replace(",", "")
 
            actual_weight = awb_details["ACTUAL_WEIGHT"]
            volumetric_weight = awb_details["VOLUMETRIC_WEIGHT"] if awb_details["VOLUMETRIC_WEIGHT"] else 0
            length = awb_details["LENGTH"]
            breadth = awb_details["BREADTH"]
            height = awb_details["HEIGHT"]

            if order_num.replace(".", "", 1).isdigit():
               order_num = int(float(order_num))
            elif 'e+' in str(order_num):
               order_num = int(float(order_num))
            else:
               order_num = awb_details["ORDER_NUMBER"]

            if ((actual_weight > 10.0) or (volumetric_weight > 10.0)):
                    a = str(airwaybill_num)+"("+str(max(actual_weight,volumetric_weight))+"Kgs)"
                    awb_overweight.append(a)
    
            org_pincode = pickup.pincode
            dest_pincode = pincode                
            servicecentre = Pincode.objects.get(pincode=dest_pincode).service_center                            
            exp_date = get_expected_dod(pickup.service_centre,servicecentre, datetime.datetime.now())

            shipment = Shipment.objects.filter(airwaybill_number=airwaybill_num)
            if shipment:
                #shipment = shipment[0]
                awb_validation["success"] = False
                awb_validation["reason"] = "AIRWAYBILL_IN_USE" 
                awb_validation["order_number"] = awb_details["ORDER_NUMBER"] 
                continue
            else: 
                shipment = Shipment.objects.create(airwaybill_number=int(airwaybill_num), 
                         current_sc=pickup.service_centre, order_number=str(order_num), product_type=product_type, 
                         shipper=shipper, pickup=pickup, reverse_pickup=0, consignee=consignee, 
                         consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , 
                         consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, 
                         state=state, mobile=mobile, telephone=telephone, item_description=item_description, 
                         pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, 
                         actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, 
                         expected_dod = exp_date, breadth=breadth, height=height, service_centre = servicecentre, 
                         original_dest = servicecentre)
                awb_num = AirwaybillNumbers.objects.get(airwaybill_number=airwaybill_num)
                awb_num.status=1
                awb_num.save()
                     
            status = shipment.status
            ShipmentExtension.objects.filter(shipment_id=shipment.id).update(status_bk = status, updated_on = now)
            remarks = ""
            if not shipment.added_on:
               shipment.added_on = now
            upd_time = shipment.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            shipment_history.objects.create(shipment=shipment, status=status, current_sc = shipment.current_sc)

            tmp_count=Shipment.objects.filter(pickup=pickup.id).count()
            pickup.pieces=tmp_count;
            pickup.status=0 
            pickup.save() 
        else:
            awb_validation["awb"] = awb_details["AWB_NUMBER"] 
            awb_validation["order_number"] = awb_details["ORDER_NUMBER"] 
            awb_validation["success"] = False
            awb_validation["reason"] = awb_validation_response["RESPONSE_MESSAGE"]

        response_awb["shipments"].append(awb_validation)

    return HttpResponse(simplejson.dumps(response_awb),content_type="application/json")   


