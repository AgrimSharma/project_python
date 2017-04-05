# Create your views here.
import pdb
import datetime
import xlrd
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import RequestContext
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from jsonview.decorators import json_view

from service_centre.general_updates import mark_shipment_undelivered
from service_centre.models import *
from nimda.models import *
from location.models import ServiceCenter
from ecomm_admin.models import ChangeLogs, update_changelog, update_shipment_changelog
from utils import admin_and_others,update_weights,  admin_only, history_update,password_reset
from billing.charge_calculations import price_updated,rts_pricing

now = datetime.datetime.now()

def shipment_doshipment(shipment):
    '''updating outscan w.r.t shipment whose col value was changed'''
    if shipment.status in [7,8,9]:
        shipment.deliveryoutscan_set.filter().latest('added_on').update_collected_amount()
    return True

def pricing(shipment):
    '''pricing update for a shipment'''
    if shipment.rts_status == 1:
         rts_pricing(shipment)
    else:
         price_updated(shipment)
    return True

def weight_correction_v2(shipment, user=None, **kwargs):
    '''weight updation'''
    prev_act_wt = shipment.actual_weight
    prev_vol_wt = shipment.volumetric_weight
    prev_length = shipment.length
    prev_breadth = shipment.breadth
    prev_height = shipment.height
    shipment.__dict__.update(kwargs)
    price_updated(shipment)
    act_wt = kwargs.get('actual_weight')
    length = kwargs.get('length')
    #volumetric_weight = kwargs.get('volumetric_weight')
    breadth = kwargs.get('breadth')
    height = kwargs.get('height')
    if user:
        #update_shipment_changelog(shipment, 'status', user, 'RTS Reversed', 'RTS')
        update_shipment_changelog(shipment, 'actual_weight', user, act_wt, prev_act_wt)
        #update_shipment_changelog(shipment, 'volumetric_weight', user, volumetric_weight, prev_vol_wt)
        update_shipment_changelog(shipment, 'length', user, length, prev_length)
        update_shipment_changelog(shipment, 'breadth', user, breadth, prev_breadth)
        update_shipment_changelog(shipment, 'height', user, height, prev_height)
    return True



def weight_correction(shipment, user=None, **kwargs):
    '''weight updation'''
    prev_act_wt = shipment.actual_weight
    prev_vol_wt = shipment.volumetric_weight
    prev_length = shipment.length
    prev_breadth = shipment.breadth
    prev_height = shipment.height
    shipment.__dict__.update(kwargs)
    price_updated(shipment)
    act_wt = kwargs.get('actual_weight')
    length = kwargs.get('length')
    volumetric_weight = kwargs.get('volumetric_weight')
    breadth = kwargs.get('breadth')
    height = kwargs.get('height')
    if user:
        update_shipment_changelog(shipment, 'status', request.user, 'RTS Reversed', 'RTS')
        update_shipment_changelog(shipment, 'actual_weight', user, act_wt, prev_act_wt)
        update_shipment_changelog(shipment, 'volumetric_weight', user, volumetric_weight, prev_vol_wt)
        update_shipment_changelog(shipment, 'length', user, length, prev_length)
        update_shipment_changelog(shipment, 'breadth', user, breadth, prev_breadth)
        update_shipment_changelog(shipment, 'height', user, height, prev_height)
    return True

@admin_and_others
def cod_amount(request, shipment, amount):
    '''coll amt updation'''
    user = request.user if request else None
    prev_coll_val = shipment.collectable_value
    product = Product.objects.get(product_name='cod')
    Shipment.objects.filter(pk=shipment.id).update(collectable_value=amount, product_type='cod')
#    ShipmentExtension.objects.filter(shipment=shipment).update(product=product)
    update_shipment_changelog(shipment, 'collectable_value', user, amount, prev_coll_val)
    sh = Shipment.objects.get(pk=shipment.id)
    if sh.status >= 2:
        pricing(sh)
        shipment_doshipment(sh)
    return True

def update_customer(shipment, subshipper_id, user=None):
    subshipper = Shipper.objects.get(id=int(subshipper_id))
    shipper = subshipper.customer
    Shipment.objects.filter(pk=shipment.id).update(shipper=shipper)

    if subshipper_id == 2872:#to be updated to ecomm foc
        Shipment.objects.filter(pk=shipment.id).update(pickup=89887)
        return True

    address=Address.objects.get(id=subshipper.address_id)
    pincode=Pincode.objects.get(pincode=address.pincode)

    pr = PickupRegistration.objects.create(status=1,
                customer_code=shipper, subcustomer_code=subshipper,
                service_centre=pincode.service_center, mode_id=1,
                customer_name="Test", address_line1=address.address1,
                actual_weight=4.0, volume_weight=4.0, pickup_date = now,
                pieces=4)
    Shipment.objects.filter(pk=shipment.id).update(pickup=pr)#updating origin, and subshipper
    if shipment.status >= 2:
        pricing(shipment)
    #update_changelog(shipment, 'pickup', shipment.shipper, user, subshipper.name)
	return True

@csrf_exempt
@admin_and_others
def rts_reversal(request):
    awb = request.POST['awb']
    Shipment.objects.filter(airwaybill_number=awb).update(rts_status=0)
    ship = Shipment.objects.get(airwaybill_number=awb)
    update_shipment_changelog(ship, 'status', request.user, 'RTS Reversed', 'RTS')
    if ship.ref_airwaybill_number:
        ref_ship = Shipment.objects.get(airwaybill_number=ship.ref_airwaybill_number)
        if update_customer(ref_ship, 2872):
            RTSReversal.objects.create(airwaybill_number=awb)
            subject = "RTS REVERSAL"
            from_email = "support@ecomexpress.in"
            to_email = ("onkar@prtouch.com","sravank@ecomexpress.in","jignesh@prtouch.com",
                     "nareshb@ecomexpress.in","jaideeps@ecomexpress.in","karishmar@ecomexpress.in")
            email_msg = "Airwaybill: %s, RTS has been reveresed "%(awb)
            send_mail(subject,email_msg,from_email,to_email)
        return HttpResponse("Success")
    else:
        return HttpResponse("Failed")

def cod_reversal(shipment, request):#To be refined
    reason = ShipmentStatusMaster.objects.get(id=44)
    dos =  shipment.doshipment_set.filter(deliveryoutscan__status=1).order_by('-added_on')[:1][0]
    #dos.deliveryoutscan.cod_status == 1    #does shipment has to be delinked from the outscan
    shp = Shipment.objects.filter(id=shipment.id)
    shp.update(status = 7, reason_code = reason, updated_on = now)
    su = StatusUpdate.objects.filter(shipment=shipment, status=2)\
            .update(reason_code=shipment.reason_code, date=now.date(), time=now.time(), status=1)
    dos.status = 0
    dos.updated_on = now
    dos.save()
    dos.deliveryoutscan.collection_status = 0
    dos.deliveryoutscan.save()
    dos.deliveryoutscan.update_collected_amount()
    codd = shipment.coddeposits_set.get()
    codd.cod_shipments.remove(shipment)#To be confirmed
    #update_changelog(shipment, 'status', shipment.shipper, request.user, 7)
    update_shipment_changelog(shipment, 'status', request.user, 'COD Reversed', 'COD')
    history_update(shipment, 7, request, "Shipment Updated (POD reversal)", shipment.reason_code)#to be confirmed
  #  dos.delete   to be confirmed

def rd_reversal(shipment, user):
    shipment.return_shipment = 0
    shipment.rd_status=0
    shipment.status=8
    shipment.service_centre=original_dest
    shipment.destination_city=original_dest.city
    shipment.pincode = original_dest.pincode_set.all()[0].pincode
    shipment.save()
    update_shipment_changelog(shipment, 'status', user, 'RD Reversed', 'RD')
    history_update(shipment, 0, request, "Shipment Updated (RD reversal)", shipment.reason_code)#to be checked if reports get affected

def rto_reversal(shipment, request):
    sc = ServiceCenter.objects.get(id=int(shipment.remark))
    pincode = sc.pincode_set.all()[0].pincode
    Shipment.objects.filter(id=shipment.id).update(reason_code=None,
                return_shipment=0, rto_status=0, status=8,
                service_centre=sc, destination_city=sc.city, pincode=pincode)
    history_update(shipment, 17, request, "Shipment Updated (RTO reversal)")#to be checked if reports get affected
    #update_changelog(shipment, 'rto_status', shipment.shipper, request.user, 0)
    update_shipment_changelog(shipment, 'rto_status', request.user, 'RTO Reversed', 'RTO')

def shipment_closure(shipment, request):
    reason = ShipmentStatusMaster.objects.get(id=50)
    shipment.status = 0
    shipment.status_type= 3
    shipment.reason_code = reason
    shipment.save()
    if shipment.codcharge_set.all():
        codcharge = shipment.codcharge_set.get()
        codcharge.delete()#To be confirmed
    if shipment.order_price_set.all():
        orderprice = shipment.order_price_set.get()
        orderprice.delete()#to be confirmed
    update_shipment_changelog(shipment, 'status', user, 'Closed', 'Unclosed')
    history_update(shipment, 0, request, "Shipment Closed", shipment.reason_code)

@update_weights
def shipment_update_weight(request):
     '''excel file updation'''
     upload_file = request.FILES['upload_file']
     file_contents = upload_file.read()
     import_wb = xlrd.open_workbook(file_contents=file_contents)
     import_sheet = import_wb.sheet_by_index(0)
     user = request.user
     for rx in range(1, import_sheet.nrows):
            airwaybill_num = import_sheet.cell_value(rowx=rx, colx=0)
            shipment = Shipment.objects.get(airwaybill_number=int(airwaybill_num))
            #collectable_value=import_sheet.cell_value(rowx=rx, colx=3)
           #if str(collectable_value):
           #     try:
           #         int(collectable_value)
           #     except ValueError:
           #         collectable_value = collectable_value.replace(",", "")
           #     cod_amount(shipment, collectable_value, user=user)
            weight_dict = {}
            actual_weight = import_sheet.cell_value(rowx=rx, colx=1)
            length = import_sheet.cell_value(rowx=rx, colx=2)
            if str(actual_weight) or str(length):
                 #volumetric_weight = import_sheet.cell_value(rowx=rx, colx=6)
                 breadth = import_sheet.cell_value(rowx=rx, colx=3)
                 height = import_sheet.cell_value(rowx=rx, colx=4)

                 weight_dict['actual_weight'] = float(actual_weight) if str(actual_weight)  else shipment.actual_weight
                 #weight_dict['volumetric_weight'] = float(volumetric_weight) if str(volumetric_weight)  else shipment.volumetric_weight
                 weight_dict['length'] = float(length) if str(length)  else shipment.length
                 weight_dict['breadth'] = float(breadth) if str(breadth)  else shipment.breadth
                 weight_dict['height'] = float(height) if str(height)  else shipment.height

                 #return HttpResponse("%s"%weight_dict)
                 weight_correction_v2(shipment, user=user, **weight_dict)

     return render_to_response("nimda/shipment_mass_updation.html",
                              {'msg':'Shipments Updated Sucessfully'},
                               context_instance=RequestContext(request))



@admin_and_others
def shipment_update(request):
     '''excel file updation'''
     upload_file = request.FILES['upload_file']
     file_contents = upload_file.read()
     import_wb = xlrd.open_workbook(file_contents=file_contents)
     import_sheet = import_wb.sheet_by_index(0)
     user = request.user
     for rx in range(1, import_sheet.nrows):
            airwaybill_num = import_sheet.cell_value(rowx=rx, colx=0)
            shipment = Shipment.objects.get(airwaybill_number=int(airwaybill_num))
            collectable_value=import_sheet.cell_value(rowx=rx, colx=3)
            if str(collectable_value):
                 try:
                     int(collectable_value)
                 except ValueError:
                     collectable_value = collectable_value.replace(",", "")
                 cod_amount(shipment, collectable_value, user=user)
            weight_dict = {}
            actual_weight = import_sheet.cell_value(rowx=rx, colx=5)
            length = import_sheet.cell_value(rowx=rx, colx=7)
            if str(actual_weight) or str(length):
                 volumetric_weight = import_sheet.cell_value(rowx=rx, colx=6)
                 breadth = import_sheet.cell_value(rowx=rx, colx=8)
                 height = import_sheet.cell_value(rowx=rx, colx=9)

                 weight_dict['actual_weight'] = float(actual_weight) if str(actual_weight)  else shipment.actual_weight
                 weight_dict['volumetric_weight'] = float(volumetric_weight) if str(volumetric_weight)  else shipment.volumetric_weight
                 weight_dict['length'] = float(length) if str(length)  else shipment.length
                 weight_dict['breadth'] = float(breadth) if str(breadth)  else shipment.breadth
                 weight_dict['height'] = float(height) if str(height)  else shipment.height

                 weight_correction(shipment, user=user, **weight_dict)
            subshipper = import_sheet.cell_value(rowx=rx, colx=10)
            if (str(subshipper)):
                    update_customer(shipment, subshipper, user=user)

     return render_to_response("nimda/shipment_mass_updation.html",
                              {'msg':'Shipments Updated Sucessfully'},
                               context_instance=RequestContext(request))

@admin_and_others
def individual_shipment_update(request):
    awb = request.POST['awb']
    update_type = request.POST['upd']
    shipment = Shipment.objects.get(airwaybill_number=awb)
    if update_type == "1":
        cod_reversal(shipment, request)
    if update_type == "2":
        rd_reversal(shipment, request.user)
    if update_type == "3":
        rto_reversal(shipment, request)
    if update_type == "4":
        shipment_closure(shipment, request)
    return render_to_response("nimda/shipment_mass_updation.html",
                              {'msg':'Shipment Updated Sucessfully'},
                               context_instance=RequestContext(request))

@csrf_exempt
@admin_and_others
def coll_val_update(request):
    awb = request.POST['awb']
    coll_val = request.POST['coll_val']
    shipment = Shipment.objects.get(airwaybill_number=awb)
    a = cod_amount(request, shipment, coll_val)
    if a:
        subject = "COD Amount Correction"
        from_email = "support@ecomexpress.in"
        to_email = ("onkar@prtouch.com","sravank@ecomexpress.in","jignesh@prtouch.com",
                     "nareshb@ecomexpress.in","jaideeps@ecomexpress.in","karishmar@ecomexpress.in")
        email_msg = "Airwaybill: %s, Amount changed to: %s"%(awb, coll_val)
        send_mail(subject,email_msg,from_email,to_email)
        return HttpResponse("Success")
    else:
        return HttpResponse("Failed")

@csrf_exempt
@admin_and_others
def sh_code(request):
    awb = request.POST['awb']
    sh_code = request.POST['sh_code']
    shipment = Shipment.objects.get(airwaybill_number=awb)
    a = update_customer(shipment, sh_code)
    if a :
        subject = "Customer Code Updation"
        from_email = "support@ecomexpress.in"
        to_email = ("onkar@prtouch.com","sravank@ecomexpress.in","jignesh@prtouch.com",
                   "nareshb@ecomexpress.in","jaideeps@ecomexpress.in","murarikp@ecomexpress.in","karishmar@ecomexpress.in")
        email_msg = "Airwaybill: %s, Shipper changed to: %s"%(awb, sh_code)
        send_mail(subject,email_msg,from_email,to_email)
        return HttpResponse("Success")
    else:
        return HttpResponse("Failed")


@csrf_exempt
@admin_and_others
def mark_ship_undelivered(request):
    awb=request.POST['awb']
    status = mark_shipment_undelivered(awb, request.user)
    if status:
        shipment = Shipment.objects.get(airwaybill_number=awb)
        ShipmentUndelivered.objects.create(airwaybill_number=awb)
        subject = "Mark shipment as undelivred"
        from_email = "support@ecomexpress.in"
        #to_email = ('arun@prtouch.com',"onkar@prtouch.com")
        to_email = ("onkar@prtouch.com","sravank@ecomexpress.in","jignesh@prtouch.com")
        email_msg = "Airwaybill: %s, has been updated as undelivered"%(awb)
        send_mail(subject,email_msg,from_email,to_email)
        return HttpResponse("Success")
    else:
        return HttpResponse("Updation Failed. Please check Airwaybill number")

@csrf_exempt
def mass_update_undelivered(request):
    message = ''
    if request.method == 'POST': 
        upload_file = request.FILES.get('undel_awb_file')
        wb = xlrd.open_workbook(upload_file.name, file_contents=upload_file.read())
        sh  = wb.sheet_by_index(0)
        awbs = sh.col_values(0)[1:]
        user = request.user
        error_list = []
        for awb in awbs:
            status = mark_shipment_undelivered(awb, request.user)
            if status:
                ShipmentUndelivered.objects.create(airwaybill_number=awb)
            else:
                error_list.append(str(awb))
        if error_list:
            message = "Undelivered Shipment update failed for the\
                following airwaybill numbers:\n" + ', '.join(error_list)
        else:
            message = '{0} airwaybills updated '.format(len(awbs))
    return render_to_response("nimda/shipment_mass_updation.html",
                              {'msg':message},
                               context_instance=RequestContext(request))


@csrf_exempt
@password_reset
def password_reset(request):
    emp_code=request.POST['emp_code']
    emp=EmployeeMaster.objects.filter(employee_code=emp_code)
    if emp:
        emp=emp[0]
        usr=emp.user
        usr.set_password(emp_code)
        usr.save()
        subject = "Password Reset"
        from_email="support@ecomexpress.in"
        #to_email = ("onkar@prtouch.com","nikunj.gadhiya01@gmail.com","theonkar10@gmail.com")
        to_email = ("lalitm@ecomexpress.in","sandeepn@ecomexpress.in","divakard@ecomexpress.in","murali@ecomexpress.in","onkar@prtouch.com","nikunj@prtouch.com")
        email_msg="Password for emp code %s, has been updated "%(emp_code)
        send_mail(subject,email_msg,from_email,to_email)
        msg=" Password has been reset !Employee email is "+emp.email
        return HttpResponse(msg)
    else:
       return HttpResponse("Updation Failed. Please check employee code")

def shipment_rts_creation(a):
    now = datetime.datetime.now()
    rc = ShipmentStatusMaster.objects.get(code=777)
    ref_destination_city=a.pickup.subcustomer_code.address.city
    ref_pincode=a.pickup.subcustomer_code.address.pincode
    pin = Pincode.objects.get(pincode=ref_pincode)
    ref_service_centre=pin.service_center
    ol_aw = a.airwaybill_number
    ref_shipment = a
    ref_shipment.id = None
    ref_shipment.airwaybill_number = a.ref_airwaybill_number
    ref_shipment.ref_airwaybill_number=ol_aw
    ref_shipment.shipment_date=None
    ref_shipment.inscan_date=now
    ref_shipment.billing=None
    ref_shipment.sbilling=None
    ref_shipment.save()
    Shipment.objects.filter(pk=ref_shipment.id).update(status=1, rd_status=0, rto_status=0, status_type=0, return_shipment=3, rts_date=now, rts_status=1, service_centre=ref_service_centre, pincode=ref_pincode, expected_dod=a.expected_dod, destination_city=ref_destination_city)
    rts_pricing(ref_shipment)
    ref_shipment.set_shipment_date
    monthdir = now.strftime("%Y_%m")
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
    shipment_history.objects.create(shipment=ref_shipment, status=1, remarks = "Returning to Shipper: Org airwaybill number: " + str(ol_aw), reason_code = rc, current_sc = a.current_sc)
    return True


def update_as_lost(request):
    awb=request.POST["awb"]
    reason_code=ShipmentStatusMaster.objects.get(code=333)
    shipment=Shipment.objects.get(airwaybill_number=awb)
    Shipment.objects.filter(airwaybill_number=awb).update(reason_code=reason_code)
    history_update(shipment, 0, request, "Shipment updated as lost", reason_code)
    return True

#def update_pincode(request):
#    #return HttpResponse("called")
#    cities = City.objects.all()
#    codes = ServiceCenter.objects.all()
#    #for city in cities:
#    #codes[city.id] = ServiceCenter.objects.filter(city=city.id)
#    if request.method == 'POST':
#		if not request.FILES:
#			pincode = request.POST['id_Pincode']
#			TAT = request.POST['TAT']
#			Area = 	request.POST['Area']
#			DC_Code = request.POST['DC Code']
#			cities = request.POST['cities']
#			sub = request.POST['sub']
#			#return HttpResponse((pincode, TAT, Area, DC_Code, cities, sub))
#			#p, created = Pincode.objects.update_or_create(pincode=pincode, defaults={})
#			#return HttpResponse('done')
#			format = "Created/updated 1 record."
#			#return render_to_response("/nimda/", {'form': format}, context_instance=RequestContext(request))
#			return HttpResponseRedirect("/nimda/")
#		else:
#		    pincode_file = request.FILES['update_pincode']
#		    return HttpResponseRedirect('/nimda/')
#    return render_to_response("nimda/update_pincode.html", {'cities':cities, 'codes': codes}, context_instance=RequestContext(request))

#@json_view
def update_pincode(request):
    
    cities = City.objects.all()
    codes = ServiceCenter.objects.all()
    if request.method == 'POST' and request.is_ajax():
        #file = request.FILES.get('update_pincode')
        #return HttpResponse(request)
        pincode = request.POST['id_Pincode']
        if not pincode:
            message = "got no files"
            return HttpResponse(message)
            
            pincode = request.POST['id_Pincode']
            Area = 	request.POST['Area']
            city = request.POST['cities']
            DC_Code = request.POST['DC Code']
            #sub = request.POST['sub']
            #TAT = request.POST['TAT']
            data = {}
            flag = ""
            
            #return HttpResponse('message')
            # Handle the update or create properly.
            try:
                pin_found = Pincode.objects.filter(pincode=pincode)
                if pin_found[0]:
                    pin_found.update(area=Area, service_center=DC_Code)
                    flag = " Pincode %s updated" %pincode
                else:
                    Pincode.objects.create(pincode=pincode,area=Area,service_center=DC_Code)
                    flag = " Pincode %s created" %pincode
                #result = pin_found[0].pincode
                data['success'] = True
                data['response'] = flag
            except Exception, e:
                err = str(e)
                data['success'] = False
                data['response'] = err
            
            # Return a JSON object for AJAX to process.  
            return HttpResponse(json.dumps(data), content_type="application/json")
            
            # insert logic for putting pincode change from above.
        else:
            #process file
            pincode_file = request.FILES.get('update_pincode')
            return HttpResponse(pincode_file)
            
            wb = xlrd.open_workbook(file_contents=content)
            sheetnames = wb.sheet_names()
            sh = wb.sheet_by_name(sheetnames[0])
    
            pincodes = sh.col_values(0)[4:]
            DC_Codes = sh.col_values(1)[4:]
            cities = sh.col_value(2)[4:]
    
            #errata = [{"row":row, "value":{"pincode":pincode, "DC_Code": DC_Code, "city": city}, "error_in": }]
    
            import re
            patt = re.compile(r"[1-9]\d{4}[1-9]$")
            for pin in pincodes:
                if not patt.match(pin):
                    error = (pincodes.index(pin), pin)
                    errata.append(error) 
            #[pin for pin in pincodes if not patt.match(pin)]
            # Look for DC Codes in models. Create list of cities found
            dc_found = ServiceCenter.objects.filter(Q(id__in=DC_Codes))
            # Check and collect if city is not in found list.
            #[dc for dc in dc_found not in DC_Codes]
            error_list = filter(lambda p:p not in dc_found, DC_Codes)

            error = (DC_Codes.index(dc), dc)
    
            city_found = City.objects.filter(Q(id__in=cities))

            error = (cities.index(city_found), city_found)
            #return HttpResponseRedirect('/nimda/')
    
    
            for row, each in enumerate(error, start=4):
                #print type(each)
                for column, value in enumerate(each):
                    #print row, column, type(value)
                    sheet.write(row, column, value)

            workbook.close()
            return HttpResponse(workbook)
    
    return render_to_response("nimda/update_pincode.html", {'cities':cities, 'codes': codes}, context_instance=RequestContext(request))
