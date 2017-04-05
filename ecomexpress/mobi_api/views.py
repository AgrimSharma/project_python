import os
import sys, traceback
import string, random
import xlrd
import xlwt
import utils
import gzip
from subprocess import call
from datetime import timedelta, datetime
import dateutil.parser
from django.core.management import call_command
import xml.dom.minidom
from xml.dom.minidom import parse
import StringIO
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import get_model
from django.core.management import call_command
from django.core.mail import send_mail
from django.core.files.move import file_move_safe
from django.core import serializers
from django.utils.encoding import smart_str
from models import *
from privateviews.decorators import login_not_required
from reports.views import excel_download
from xlsxwriter.workbook import Workbook
from track_me.models import *
from service_centre.models import *
from location.models import ServiceCenter
from pickup.models import PickupRegistration
import xmldict, xmltodict
from utils import history_update
now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from models import *
import base64
import sys, traceback
from pickup.models import PickupRegistration
from location.models import *
from service_centre.models import *
from django.template import RequestContext
from service_centre.models import ServiceCenter
from django.contrib import auth
import json 
from django.utils import simplejson
from django.contrib.auth import login, logout
import string, random
from django.core.mail import send_mail 
from privateviews.decorators import login_not_required
import xlwt
from service_centre.models import Shipment
from django.core.serializers import serialize
from django.utils.simplejson import dumps, loads, JSONEncoder
from django.db.models.query import QuerySet
from django.utils.functional import curry
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
import re
import time
from airwaybill.models import *
#from mobi_api import send_request

@csrf_exempt
def get_awb_details(request):
   if request.POST:
     count = 0
     upload_file = request.FILES['upload_file']
     file_contents = upload_file.read()
     if file_contents:
        pickup_dict={} 
        import_wb = xlrd.open_workbook(file_contents=file_contents)
        import_sheet = import_wb.sheet_by_index(0)
        file_contents = ''
        for rx in range(1, import_sheet.nrows):
            awb = import_sheet.cell_value(rowx=rx, colx=0)
            address = import_sheet.cell_value(rowx=rx, colx=1)
            pincode = import_sheet.cell_value(rowx=rx, colx=2)
            mobile = import_sheet.cell_value(rowx=rx, colx=3)
            ref_pickup = import_sheet.cell_value(rowx=rx, colx=4)
            cust_id = import_sheet.cell_value(rowx=rx, colx=5)     
            #file_contents = file_contents + awb
            a = awb
            abn = AirwaybillNumbers.objects.get(airwaybill_number=a)
     #count =0
     #tmp1=""
            chck=False
     #for a in awb:
            abc = AirwaybillCustomer.objects.filter(customer_id=cust_id)	
            for ab in abc:
               if abn in ab.airwaybill_number.all():
                  chck=True
                  break
               else:
                  chck=False
      
       #return HttpResponse(a)
            ship=Shipment.objects.filter(airwaybill_number=a)
            if ship and chck:
               count = count + 1
               if ship[0].pickup:
                  pickup=ship[0].pickup
               else:
                  pincode=Pincode.objects.filter(pincode=pincode)
                  if pincode:
                     pincode=pincode[0]
                     sub_cust=Shipper.objects.filter(address__pincode=pincode.pincode,customer_id=cust_id)
                     if sub_cust:
                        sub_cust=sub_cust[0]
                        pkp=PickupRegistration.objects.filter(subcustomer_code_id=sub_cust.id,status=0)
                        if pkp:
                           pkp.shipment_pickup.add(ship[0])
                           pickup=pkp[0]
                        else:
                           pickup=PickupRegistration.objects.create(subcustomer_code=sub_cust,status=0,service_centre=pincode.service_center,customer_id=cust_id)  
               pickup.shipment_pickup.add(ship[0]) 
               pickup = pickup.id
               #else:
                 #return HttpResponse("Please enter correct pincode !!")   
               shipper=ship[0].shipper.code[:5]
               shipper_name=ship[0].shipper.name[:5]
               pickup_status="picked"
               frt_status="Y"
               frt_coll=ship[0].collectable_value
               frt_amt=ship[0].declared_value
               pkpawb=PickupAPIAWB.objects.filter(airwaybill_number=a)
               if pkpawb:
                  pkpawb.update(pickup_id=pickup)
               else:
                  PickupAPIAWB.objects.create(airwaybill_number=a,pickup_id=pickup)
            else:
               pickup=None
               shipper="NA"
               shipper_name="NA"
               pickup_status="NA"
               frt_status="NA"
               frt_amt="NA"
               frt_coll="NA"
               ref_pickup=None
               #PickupAPIAWB.objects.create(airwaybill_number=a,pickup_id=pickup)
     #return HttpResponse(tmp)
            awb=a
            att_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            pickup=pickup
            username=request.user.employeemaster.employee_code
       #username="prtouch"
            updated_on=datetime.datetime.now()
            #a=str(a)
            PickupAPIHistory.objects.create(airwaybill_number=a,ref_pickup=ref_pickup,pickup=pickup,updated_on=updated_on,shipper_code=shipper,shipper_name=shipper_name,username=username,pickupstatus=pickup_status,attempt_date=att_date,freight_status=frt_status,freight_amount=frt_amt,freight_collected=frt_coll)
     #msg="Request captured successfully!!"
     #return HttpResponse(msg)
            ships=PickupAPIAWB.objects.filter(pickup_id=None)
            return render_to_response("mobile/no_manifest_ships.html",{"ships":ships},context_instance=RequestContext(request))
   else:
     ships=PickupAPIAWB.objects.filter(pickup_id=None)
     return render_to_response("mobile/no_manifest_ships.html",{"ships":ships},context_instance=RequestContext(request))
     #customer=Customer.objects.using('local_ecomm').filter(activation_status=True)
     #return render_to_response("mobile/get_awb_details.html",{'customer':customer},context_instance=RequestContext(request))

@login_not_required
@csrf_exempt
def get_pending_pickups(request):
   pickup_dict={}
   #if request.POST:
   if 1 == 1:
      #username=request.POST['username']
      #password=request.POST['password']
      #datetime=request.POST['datetime']
      username="onkar"
      password="prtouch"
      datetime="2014-06-01 11:11:11"
      user=username + "@prtouch.com"
      try:
        newuser = auth.authenticate(username=user, password=password)
        login(request,newuser)
      except:
        pickup_dict["status"]="0"
        pickup_dict["message"]="Invalid username & password combination. Please try again"
        return HttpResponse(simplejson.dumps(pickup_dict),content_type="application/json")
      pickups=PickupRegistration.objects.filter(added_on__gt=datetime).exclude(status=1)
      pickup_records=[]
      ships_records=[]
      service_center=""
      contact=0000000
      con_email="NA"
      for tmpPickUp in pickups:
          pkp=PickupRegistrationEmployee.objects.filter(pickup_id=tmpPickUp.id)
          if pkp:
            emps=EmployeeMaster.objects.get(employee_code=pkp[0].employee_code)
            email=emps.email
            emp=email.split('@')
            ships=Shipment.objects.filter(pickup=tmpPickUp)
            for s in ships:
               if s.product_type<>"cod":
                  prod_type="N"
               else:
                  prod_type="Y"
               cust=s.shipper
               email=cust.email
               city=s.pickup.service_centre.city.city_name
               try:
                  op=s.order_price_set.get()
                  frt=op.freight_charge
               except:
                  frt=0
               record={"AssignmentNo":s.airwaybill_number,"AssignmentType":"E","NoOfPcs":s.pieces,"PickupTime":s.pickup.added_on.strftime("%d-%m-%Y %H:%M"),"Weight":s.chargeable_weight,"ShipperAccNo":cust.code,"PickUpID":s.pickup.id,"ShipperName":s.pickup.customer_name,"ShipperAddress1":s.pickup.address_line1,"ShipperAddress2":s.pickup.address_line2,"ShipperCity":city,"ShipperPincode":s.pickup.customer_code.address.pincode,"ShipperEmail":con_email,"ShipperContactNo":s.pickup.mobile,"isFreight":"Y","Freight AMT":frt,"UserName":emp[0]}
               ships_records.append(record)
      return HttpResponse(simplejson.dumps(ships_records),content_type="application/json")

@login_not_required
#Login Authentication 
@csrf_exempt       
def login_authenticate(request):
    #return HttpResponse("Coming here")
    pickup_dict = {}
    #if 1==1:
    if request.POST:
        username=request.POST['username']
        password=request.POST['password']
        shipper=request.POST['shipper']
        datetime=request.POST['datetime']
	#username="onkar@prtouch.com"
	#password="prtouch"
        #shipper="92006"
        #datetime="2014-03-20 11:11"
        try:
            newuser = auth.authenticate(username=username, password=password)
            login(request, newuser)
        except:
            pickup_dict["status"]="0"
            pickup_dict["message"]="Invalid username & password combination. Please try again"
            return HttpResponse(simplejson.dumps(pickup_dict),content_type="application/json")   
        #return  newuser
        emp=EmployeeMaster.objects.filter(user=newuser)
        pickup=[]
        pke=PickupRegistrationEmployee.objects.filter(employee_code=emp[0].employee_code)
        for p in pke:
            pkp=PickupRegistration.objects.filter(id=p.pickup_id,customer_code__code=int(shipper),added_on__gt=datetime)
            if pkp:
               pickup.append(pkp)
        #pickup=PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre,customer_code__code=int(shipper),added_on__gt=datetime)    
        #pickup = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre,status=0)
        #pincodes=Pincode.objects.filter()
        #pincodes_records = []
        pickup_records=[]
        service_center=""
        name=""
        cust=Customer.objects.get(code=shipper)
        email=cust.email
        contact=0000000
        con_email="NA"  
        name=cust.name
        #name = "Onkar T"     
        #for pin in pincodes:
            #pincodes_records.append(pin.pincode)
        ships_records=[]
        for tmpPickUp in pickup:
             ships=Shipment.objects.filter(pickup=tmpPickUp)
             for s in ships:
                  if s.product_type<>"cod":
                       prod_type="N"
                  else:
                      prod_type="Y" 
                  #pi=s.pickup.pincode
                  #pin=Pincode.objects.get(pincode=pi)
                  city=s.pickup.service_centre.city.city_name
                  #city=pin.service_center.city.city_name
               
                  try:
                     op=s.order_price_set.get()    
                     frt=op.freight_charge             
                  except:
                     frt=0
                  record={"AssignmentNo":s.airwaybill_number,"AssignmentType":"E","NoOfPcs":s.pieces,"PickupTime":s.pickup.added_on.strftime("%d-%m-%Y %H:%M"),"Weight":s.chargeable_weight,"ShipperAccNo":s.pickup.id,"ShipperName":s.pickup.customer_name,"ShipperAddress1":s.pickup.address_line1,"ShipperAddress2":s.pickup.address_line2,"ShipperCity":city,"ShipperPincode":s.pickup.customer_code.address.pincode,"ShipperEmail":con_email,"ShipperContactNo":s.pickup.mobile,"isFreight":"Y","Freight AMT":frt,"UserName":username}
                  #record={"AssignmentNo":/iss.airwaybill_number,"AssignmentType":"D","ShipperAccNo":shipper,"ShipperName":name,"ShipperEmail":email,"ShipperContactNo":contact,"ConsigneeName":s.consignee,"ConsigneeAddress1":s.consignee_address1,"ConsigneeAddress2":s.consignee_address2,"ConsigneeCity":s.original_dest.city.city_name,"ConsigneePincode":s.pincode,"ConsigneeEmail":con_email,"ConsigneeContactNo":s.mobile,"isCOD":prod_type,"CODAmount":s.collectable_value,"UserName":username} 
                  ships_records.append(record)
        #for tmpPickUp in pickup:
         #if count < 3:
         #   count = count+1
            #pickup_date=tmpPickUp.pickup_date.strftime("%d-%m-%Y")
            #pickup_time=tmpPickUp.pickup_time.strftime("%H:%m")
            #time=pickup_time + " "+ pickup_date
            #name=request.user.employeemaster.firstname+" "+request.user.employeemaster.lastname
            #service_center=tmpPickUp.service_centre.center_name
            #pickup_id = tmpPickUp.id
            #pickup_name=tmpPickUp.customer_name
            #pickup_number=tmpPickUp.pieces
	    #noofshipments=Shipment.objects.filter(pickup_id=pickup_id)
            #record = {"name":pickup_name, "id":pickup_id,"number":pickup_number,"shipment_status":"1","time":time,"awbs":len(noofshipments)}
            #pickup_records.append(record)
        
        #pickup_dict["pickups"]=pickup.count()
        #pickup_dict["service_code"]=service_center
        #pickup_dict["name"]=name
        #pickup_dict["status"]="1"
        #pickup_dict["details"]=ships_records
        #pickup_dict["pin_codes"]=pincodes_records
        
        return HttpResponse(simplejson.dumps(ships_records),content_type="application/json")    
         
               
    else:
        pickup_dict["status"]="0"
        pickup_dict["message"]="Unable to process the request"
        return HttpResponse(simplejson.dumps(pickup_dict),content_type="application/json")    
        
 
     
@login_not_required
@csrf_exempt       
def details(request):
    awb_dict={}
    shipment_records=[]
    #if 1==1:
    if request.method == "POST":
        #id=request.POST['id']
        #username=request.POST['username']
        #password=request.POST['password']
        id=595
	username="onkar@prtouch.com"
	password="prtouch"
	try:
            newuser = auth.authenticate(username=username, password=password)
            login(request, newuser)
        except:
            awb_dict["status"]="0"
            awb_dict["message"]="Invalid username & password combination. Please try again"
            return HttpResponse(simplejson.dumps(awb_dict),content_type="application/json") 
        
        
        shippments=Shipment.objects.filter(pickup_id=id)
        
        for obj in shippments:
            awb=obj.airwaybill_number
            order_number=obj.order_number
            pincode=obj.pincode
            dest_sc=obj.service_centre
            type=obj.product_type
            if(type == "ccd"):
                col_val=obj.collectable_value
            else:
                col_val=""    
            status=obj.status
            city=obj.destination_city
            act_wt=obj.actual_weight
            dest_SC="hi"
            dest_SC=obj.service_centre
            #dest_SC=String(dest_SC).replace('-',' ')   
            record={"awb":awb,"ordernumber":order_number,"pincode":pincode,"weight":act_wt,"status":status,"city":city,"type":type,"col_value":col_val,"dest_SC":city}
            shipment_records.append(record)
        
        awb_dict["count"]=len(shipment_records)
        awb_dict["shipments"]=shipment_records
        awb_dict["status"]="1"
        awb_dict["message"]="Request processed successfully"
        return HttpResponse(simplejson.dumps(awb_dict),content_type="application/json")
    
    else:
        awb_dict["status"]="0"
        awb_dict["message"]="Unable to process the request"
        return HttpResponse(simplejson.dumps(awb_dict),content_type="application/json")  
         
    
@login_not_required      
@csrf_exempt        
def pickup_report(request):
        #my_var="demo"
    pickup_dict={}
   
    if request.POST:
        scanned = request.POST['scanned']
        unscanned = request.POST['unscanned']
        pickupid=request.POST['pickupid']
        username=request.POST['username']
        password=request.POST['password']
      
        newuser = auth.authenticate(username=username, password=password)
   
        unscanned_records=[]
        unscanned_records=re.split("#", unscanned)
             
        for tmp in unscanned_records:
            tmp_list=[]
            if tmp<>"":
                tmp_list=re.split("@", tmp)
                tmp_variable=tmp_list[0]
                shipment=Shipment.objects.get(airwaybill_number=int(tmp_variable))
                shipment.status_type=tmp_list[1]
                shipment.save()
                
        scanned_records=[]
        scanned_records=re.split('#',scanned)
        
        shipment=Shipment.objects.filter(pickup_id=pickupid)
        for tmp in scanned_records:
            #return HttpResponse(tmp)
            if tmp<>"":
                
                try:
                    shipment=Shipment.objects.get(airwaybill_number=int(tmp))
                    shipment.status_type = 1#verified
                    shipment.save()
                    #return HttpResponse(tmp)
                except:
                    traceback.print_exc()
                    pickup_dict["status"]="0"
                    pickup_dict["message"]="Wrong Shipment Number has been submitted"
                    return HttpResponse(simplejson.dumps(pickup_dict),content_type="application/json")
                 
        #tmp_total=Shipment.objects.filter(pickup_id=pickupid).count()
        #tmp_success_count = Shipment.objects.filter(pickup_id=pickupid, status_type=1).count()
      
        
        #total_records = Shipment.objects.filter(pickup_id=pickupid, status=0).count()
        #success_count = Shipment.objects.filter(pickup_id=pickupid, status_type=1, status=0).count()
        #mismatch_count = Shipment.objects.filter(pickup_id=pickupid, status=0, status_type= 2 or 3 or 4).count()
        #return HttpResponse("onkar :)")    
        pickup_dict["status"]="1"
        #pickup_dict["success"]=success_count
        #pickup_dict["total"]=total_records
        pickup_dict["message"]="All the shippments have been submitted successfully"
        return HttpResponse(simplejson.dumps(pickup_dict),content_type="application/json") 
        
    else:
       
        pickup_dict["status"]="0"
        #pickup_dict["total"]=total_records
        #pickup_dict["success"]=tmp_success_count
        pickup_dict["message"]="Unable to process the request"
        return HttpResponse(simplejson.dumps(pickup_dict),content_type="application/json")    




@login_not_required
@csrf_exempt
def delivery_login(request):
    deli_dict={}
    if 1==1:
        username=request.POST['username']
        password=request.POST['password']
        #username="onkar@prtouch.com"
        #password='prtouch'
        try:
            newuser = auth.authenticate(username=username, password=password)
            login(request, newuser)
        except:
            deli_dict["status"]="0"
            deli_dict["message"]="Invalid username & password combination. Please try again"
            return HttpResponse(simplejson.dumps(deli_dict),content_type="application/json")    
        emp=EmployeeMaster.objects.get(employee_code=10345)
        #otscans=DeliveryOutscan.objects.filter(origin=emp.service_centre,status=0)
        otscans=DeliveryOutscan.objects.filter(employee_code=request.user.employeemaster).exclude(status=1)
        deliot_records=[]
        for ot in otscans:
                  record={"amount":ot.amount_to_be_collected,"id":ot.id,"origin":ot.origin.center_name,"update":ot.dos_updated_count().count(),"unupdate_count":ot.dos_unupdated_count().count()}
                  deliot_records.append(record)
        deli_dict["status"]="1"
        deli_dict["message"]="Authneticated"
        deli_dict["outscans"]=deliot_records
        return HttpResponse(simplejson.dumps(deli_dict),content_type="application/json")     

@login_not_required
@csrf_exempt
def save_images(request):
    sign_dict={}
    #if request.POST:
    if 1==1:
        awb=request.POST['awb']
        photo=request.POST['photo']
        photo_timestamp=request.POST['photo_timestamp']
        sign_enc=request.POST['sign_enc']
        sign_timestamp=request.POST['sign_timestamp']
        imgdata = base64.b64decode(photo)
        filename="/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/app_data/photo/"+awb+"_"+photo_timestamp+".png"
        with open(filename, 'wb') as f:
           f.write(imgdata)
        imgdata = base64.b64decode(sign_enc)
        filename="/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/app_data/sign/"+awb+"_"+sign_timestamp+".png"
        with open(filename, 'wb') as f:           f.write(imgdata)
           #f.write(imgdata)
        return HttpResponse("updated")

 

@login_not_required
@csrf_exempt
def outscan_details(request):   
    outscan_dict={}
    if 1==1:
        oid=request.POST['outscan_id']
        #oid=38777
        records=[]
        ot=DeliveryOutscan.objects.get(id=oid)
        for a in ot.dos_unupdated_count():
        #for a in ot.dos_updated_count():
            record={"name":a.shipment.consignee,"mobile":a.shipment.mobile,"awb":a.shipment.airwaybill_number,"shipper":a.shipment.shipper.name,"collectable_value":a.shipment.collectable_value,"item_description":a.shipment.item_description,"order_number":a.shipment.order_number}
            records.append(record)
        outscan_dict["outscans"]=records      
        return HttpResponse(simplejson.dumps(outscan_dict),content_type="application/json")   

@login_not_required
@csrf_exempt
def sample_response(request):
   response_dict={}
   response_dict["pickupId"]=34234
   response_dict["RefPickupId"]=1000
   response_dict["EmployeeCode"]=10032
   response_dict["username"]=12345
   response_dict["password"]="abcd@123"
   awb_list=[]
   awbs=[100351208,100570936,101633239]
   for a in awbs:
       ship=Shipment.objects.get(airwaybill_number=a)
       record={"awb":ship.airwaybill_number,"order_number":ship.order_number,"product_type":ship.product_type,"consignee":ship.consignee,"consignee_address1":ship.consignee_address1,"consignee_address2":ship.consignee_address2,"consignee_address3":ship.consignee_address3,"consignee_address4":ship.consignee_address4,"destination_city":ship.destination_city,"pincode":ship.pincode,"state":ship.state,"mobile":ship.mobile,"telephone":ship.telephone,"item_description":ship.item_description,"pieces":ship.pieces,"collectable_value":ship.collectable_value,"declared_value":ship.declared_value,"actual_weight":ship.actual_weight,"volumetric_weight":ship.volumetric_weight,"length":ship.length,"breadth":ship.breadth,"height":ship.height}
       awb_list.append(record)
   response_dict["shipments"]=awb_list
   return HttpResponse(simplejson.dumps(response_dict),content_type="application/json")




@login_not_required
@csrf_exempt
def delivery_update(request):
  if 1==1:
     f=open('/home/web/ecomm.prtouch.com/ecomexpress/mobi_api/demo','r')
     imgstring=f.read()
     imgstring=request.POST['username']
     #return HttpResponse(imgstring)
     fh=open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/app_data/some_image.jpg","wb")
     result=""
     lens=len(imgstring)
     lenx = lens - (lens % 4 if lens % 4 else 4)
     try:
         result = base64.decodestring(strg[:lenx])
     except:           
                pass
     fh.write(result)
     fh.close()
     imgdata = base64.b64decode(imgstring)
     #imgdata=base64.decodestring(imgstring)
     filename="/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/app_data/some_image.jpg"
     filename="/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/app_data/some_image.png"
     with open(filename, 'wb') as f:
           f.write(imgdata)
     return HttpResponse(imgstring)



@login_not_required
@csrf_exempt
def delivery_update1(request):
        deivery_dict={}
        #if request.POST:
        if 1==1:
                import time
                awb=701658975
                shipment=Shipment.objects.get(airwaybill_number=awb) 
                data_entry_emp=EmployeeMaster.objects.get(employee_code=124)
                delivery_emp=data_entry_emp
                su_status=9
                reason_code=ShipmentStatusMaster.objects.get(id=1) 
                date=time.strftime("%Y-%m-%d")
                time=time.strftime("%H:%M:%S")
                recieved_by='me' 
                ajax_field=time
                imgstring=''
                remarks=''
                su = StatusUpdate.objects.get_or_create(shipment = shipment, data_entry_emp_code = data_entry_emp, delivery_emp_code = delivery_emp, reason_code = reason_code, date = date, time = time, recieved_by = recieved_by, status = su_status, origin = request.user.employeemaster.service_centre, remarks=remarks,ajax_field=ajax_field) #status update
                #imgstring=request.POST['image']
                print "image obtained"
                #imgdata = base64.b64decode(imgstring)
                print "image deocded"
                #filename = 'some_image.jpg'  # I assume you have a way of picking unique filenames
                print "got filename"
                #with open(filename, 'wb') as f:
                #       f.write(imgdata)
                fh=open("/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/app_data/some_image.jpg","wb")
                #fh.write(imgstring.decode('base64'))
                #fh.write(decode_base64(imgstring))
                result=""
                lens=len(imgstring)
                lenx = lens - (lens % 4 if lens % 4 else 4)
                try:
                        result = base64.decodestring(strg[:lenx])
                except:
                        pass
                fh.write(result)
                fh.close()
                print "saved"
                deivery_dict["status"]="1"
                if su:
                    message="fine"
                else:
                    message='some problem'
                deivery_dict["message"]=message
                return HttpResponse(simplejson.dumps(deivery_dict),content_type="application/json")
        else:
                deivery_dict["status"]="0"
                deivery_dict["message"]="Unable to process the request of saving image"
                return HttpResponse(simplejson.dumps(deivery_dict),content_type="application/json")

@login_not_required
@csrf_exempt
def lastmile_pod_update(request):
    reason = ""
    #strXML =  request.POST.get("strXML")
    #userID =  request.POST.get("userID")
    api_post = {}

    #if not strXML or not userID: 
    #    reason = "either of the parameter not found"
    #strxml_parse = request.GET.get("strXML")   
    #return HttpResponse('hi')
    strxml_parse = xmltodict.parse(request.POST.get("strXML"))
    #strxml_parse = xmltodict.parse(request.GET.get("strXML"))

    #return HttpResponse(strxml_parse["DETAILS"]['DOCKET']["BIKER_ID"])
    #strxml_parse = xmldict.xml_to_dict(strXML) 
    user_emp = EmployeeMaster.objects.get(employee_code=strxml_parse["DETAILS"]['DOCKET']["BIKER_ID"])
    user = user_emp.user

    api_post['delivery_emp'] = strxml_parse["DETAILS"]['DOCKET']["BIKER_ID"]
    #api_post['delivery_emp'] = 10026
    api_post['reason_code'] = strxml_parse["DETAILS"]['DOCKET']["COMMENTS"]
    if api_post['reason_code'] == "999":
        api_post['awbd'] = strxml_parse["DETAILS"]['DOCKET']["DOCKET_NUMBER"]
    else:
        api_post['awbu'] = strxml_parse["DETAILS"]['DOCKET']["DOCKET_NUMBER"]
        api_post['awbd'] = ""
   # api_post['reason_code'] = 10
    api_post['recieved_by'] = strxml_parse["DETAILS"]['DOCKET']["Delivery_Person"]
    api_post['remarks'] = ""
    date_time1 = strxml_parse["DETAILS"]['DOCKET']["DELIVERY_TIME"]
    date_time1="2013-10-09 10:30:59.0"
    date_time = date_time1.split(".")
    date_time = date_time[0].split(" ")
    api_post['time'] = date_time[1]
    api_post['date'] = date_time[0]

    customer_photo = strxml_parse["DETAILS"]['DOCKET']["CUSTOMER_PHOTO"]
    customer_photo1 = strxml_parse["DETAILS"]['DOCKET']["CUSTOMER_PHOTO1"]
    customer_photo2 = strxml_parse["DETAILS"]['DOCKET']["CUSTOMER_PHOTO2"]
    lat = strxml_parse["DETAILS"]['DOCKET']["LATITUDE"]
    lon = strxml_parse["DETAILS"]['DOCKET']["LONGITUDE"]
    signature_link = strxml_parse["DETAILS"]['DOCKET']["SIGNATURE_LINK"]
    statusapi = strxml_parse["DETAILS"]['DOCKET']["STATUS"]
    location = strxml_parse["DETAILS"]['DOCKET']["LOCATION"]
    actual_cod_sod = strxml_parse["DETAILS"]['DOCKET']["ACTUAL_COD_SOD"]
    cls_klm = strxml_parse["DETAILS"]['DOCKET']["ClS_KLM"]
    drs_number = strxml_parse["DETAILS"]['DOCKET']["DRS_NUMBER"]
    imei = strxml_parse["DETAILS"]['DOCKET']["IMEI"]
    '''Status Update for Shipment'''
    before1 = now - datetime.timedelta(days=1)
    #dest = user.employeemaster.service_centre_id
    dest = user_emp.service_centre_id
    if api_post:
        data_entry_emp = api_post['delivery_emp']
        delivery_emp = api_post['delivery_emp']
        awb = api_post.get('awbu') or api_post.get('awbd')
        reason_code = api_post['reason_code']
        recieved_by = api_post['recieved_by']
        remarks = api_post.get('remarks','')
        #time=""
        #date+""
        time = api_post['time']
        date = api_post['date']
        #ajax_field = api_post['ajax_num']
        pod_reversal = 0
        if not (data_entry_emp and delivery_emp):
             return HttpResponse("<string><root><message>Incorrect Employee Code</message></root></string>", content_type="application/xhtml+xml")

          #   return HttpResponse("Incorrect Employee Code")
        data_entry_emp = EmployeeMaster.objects.filter(employee_code=int(data_entry_emp)).only('id')
        delivery_emp = EmployeeMaster.objects.filter(employee_code=int(delivery_emp)).only('id')
        if delivery_emp and data_entry_emp:
           delivery_emp = delivery_emp[0]
           data_entry_emp = data_entry_emp[0]
        else:
             return HttpResponse("<string><root><message>Incorrect Employee Code</message></root></string>", content_type="application/xhtml+xml")
          # return HttpResponse("Incorrect Employee Code")
        reason_code=ShipmentStatusMaster.objects.get(id=1)
        #reason_code = ShipmentStatusMaster.objects.get(code = int(reason_code))
        dat = dateutil.parser.parse(date)
        date = dat.strftime("%Y-%m-%d")

        ship = Shipment.objects.filter(airwaybill_number = int(awb), status__in = [7,8,9],
                current_sc_id=dest).only('status','status_type','added_on','expected_dod')
        if not ship:
             return HttpResponse("<string><root><message>Incorrect Shipment Number</message></root></string>", content_type="application/xhtml+xml")
            #return HttpResponse("Incorrect Shipment Number")

        shipment = ship[0]
        if not shipment.deliveryoutscan_set.latest("added_on").status:
             return HttpResponse("<string><root><message>Please Close Outscan First</message></root></string>", content_type="application/xhtml+xml")
          #  return HttpResponse("Please Close Outscan First")
        if reason_code.code == 666:
             ship.update(sdl=1)
             sdl_charge(shipment)

        if (api_post['awbd'] <> ""):#Delivered
            if shipment.status <> 7:
                return HttpResponse("<string><root><message>Please Outscan the shipment</message></root></string>", content_type="application/xhtml+xml")
                #return HttpResponse("Please Outscan the shipment")

            su_status = 2
            shipment_status = 9
            dos_status = 1
        else:
            if shipment.status == 9:#POD reversal
                if reason_code.id <> 44:
                   return HttpResponse("<string><root><message>For updating this shipment enter the reason code as 202</message></root></string>", content_type="application/xhtml+xml")
                  #  return HttpResponse("For updating this shipment enter the reason code as 202")
                shipment_status =7
                su_status = 1
                dos_status = 0
                pod_reversal = 1
            else:#Undelivered
              su_status = 1
              shipment_status = 8
              dos_status = 2
        #ajax_check = StatusUpdate.objects.filter(ajax_field=ajax_field)
        #if ajax_check:
        #      return HttpResponse("Incorrect Shipment Number")
        su = StatusUpdate.objects.get_or_create(shipment = shipment, data_entry_emp_code = data_entry_emp, delivery_emp_code = delivery_emp, reason_code = reason_code, date = date, time = time, recieved_by = recieved_by, status = su_status, origin = user_emp.service_centre, remarks=remarks)#,ajax_field=ajax_field) #status update

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
        if s:
           upd_time = shipment.added_on
           monthdir = upd_time.strftime("%Y_%m")
           shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
           shipment_history.objects.create(shipment=shipment, status=shipment_status, employee_code = delivery_emp, current_sc = user_emp.service_centre, expected_dod=shipment.expected_dod, reason_code=reason_code, remarks=remarks)
           ShipmentLastMileUpdate.objects.create(shipment=shipment, delivered_on=date_time1,status=shipment_status, current_sc=user_emp.service_centre, reason_code=reason_code,
                                                 employee_code=delivery_emp, delivered_to = recieved_by, lat =lat , lon=lon, statusapi=statusapi, imei=imei,
                                                 signature_link=signature_link, customer_photo=customer_photo, customer_photo1=customer_photo1,customer_photo2=customer_photo2,
                                                 location=location, drs_number=drs_number, cls_klm=cls_klm, actual_cod_sod=actual_cod_sod) #cod_method=cod_method,status_text=status_text

       #    history_update(shipment, shipment_status, request, "", reason_code) #history update
           return HttpResponse("<string><root><message>Updated Successfully</message></root></string>", content_type="application/xhtml+xml")
        else:
           return HttpResponse("<string><root><message>Not Updated (%s)</message></root></string>" % reason, content_type="application/xhtml+xml")
           return HttpResponse("Shipment not updated, please contact site admin")
   #     status_update = StatusUpdate.objects.filter(origin_id = dest,date__range=(before,now)).select_related('shipment__airwaybill_number','reason_code').only('id','status','remarks','shipment__airwaybill_number','reason_code')


       #    delivered_count = status_update.filter(date__range=(before1,now)).count()
    #    undelivered_count = status_update.filter().exclude(shipment__rts_status=2).exclude(shipment__rto_status=1).count()
    #    delivered_count = ""
    #    undelivered_count = ""
    #    return HttpResponse("Success")
        #return render_to_response("delivery/status_update_data.html",
        #                              {'status_update':su[0],
        #                               'delivered_count':delivered_count,
        #                               'undelivered_count':undelivered_count,
        #                               },
        #                              )

    else:
           status_update = StatusUpdate.objects.filter(origin_id = dest, date__range=(before,now)).select_related('shipment__airwaybill_number','reason_code').only('id','status','remarks','shipment__airwaybill_number','reason_code').order_by("-id")
           delivered = status_update.filter(date__range=(before1,now)).order_by("-id")
           undelivered = status_update.filter().exclude(shipment__rts_status=2).exclude(shipment__rto_status=1)
           delivered_count = delivered.count()
           undelivered_count = undelivered.count()
           reason_code  =  ShipmentStatusMaster.objects.all()
           return render_to_response("delivery/status_update.html",locals(),
                               context_instance = RequestContext(request))     


@login_not_required
@csrf_exempt
def complete_pickup(request):    
    resp_dict={}
    if request.POST:
    #if 1==1:
        #r=send_request.main()
      
        #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        #print "this is the input"
        #print r
        #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        #return HttpResponse("----")
        r=request.POST['pickup_details'] 
        dom = parse(StringIO.StringIO(r))
        newdata=[]
        data=["AssignmentRefPickUpID","AssignmentNo","ClientPickUpID","ClientShipperAccNo","ClientShipperName","UserName","Scan_Item","PickupStatus","isFreight","FreightAmount","FreightCollected","AttemptDate","AttemptTime","ServerUpdateDateTime"]
        newdata.append("anyType")
     #pickup_list=[] 
     #awb_list=[]
        processed_awbs=[]
        pickup_dict={}
        for d in newdata:
           alist=dom.getElementsByTagName(d)
           print len(alist)
           for a in alist:
               for n in data:
                 for b in  a.getElementsByTagName(n):
                    if n == "ClientShipperAccNo":
                          shipper=b.childNodes[0].data
                          #print "shipper is",shipper
                    if n == "ClientPickUpID" :
                          pickup=b.childNodes[0].data
                          if pickup == None or pickup=="None":
                            for n in data:
                               for b in  a.getElementsByTagName(n):
                                  if n == "ClientShipperAccNo":
                                     shipper=b.childNodes[0].data
                                     customer=Customer.objects.filter(code=int(shipper))
                                     #return shipper
                                     if customer:
                                        customer=customer[0]
                                     else:
                                        customer=Customer.objects.get(code=32012)
                                     sc=ServiceCenter.objects.get(center_shortcode='dsw')
                                     now=datetime.datetime.now()
               
                                     p=PickupRegistration.objects.create(customer_code=customer,service_centre=sc,pickup_date=now)
                                     pickup=p.id
                          #print customer,"is customer"
                    if n=="AssignmentRefPickUpID":
                          ref_pickup=b.childNodes[0].data
                    if n == "ClientShipperName":
                          shipper_name=b.childNodes[0].data
                    if n == "UserName":
                          username=b.childNodes[0].data
                    if n == "Scan_Item":
                          awb=b.childNodes[0].data
                    if n == "PickupStatus":
                          pickup_status=b.childNodes[0].data
                    if n == "ServerUpdateDateTime":
                          updated_on=b.childNodes[0].data
                          updated_on = updated_on.replace("12:00:00 AM","")
                    if n == "AttemptDate":
                          att_date=b.childNodes[0].data
                    if n == "AttemptTime":
                          att_date= att_date + b.childNodes[0].data
                    if n == "isFreight":
                           frt_status = b.childNodes[0].data
                    if n == "FreightAmount":
                           frt_amt=b.childNodes[0].data
                    if n == "FreightCollected":
                           frt_coll=b.childNodes[0].data
                    if n == "AssignmentNo":
                           ass_no=b.childNodes[0].data
               # add in history
               # create pickup awbs and pickups
               #update_on = updated_on.strftime("%Y-%m-%d %H:%M")
               print updated_on
               print att_date
               print shipper,shipper_name
               shipper_name = shipper_name[:5]
               updated_on=datetime.datetime.now()
               update_on = updated_on.strftime("%Y-%m-%d %H:%M")
               att_date = updated_on.strftime("%Y-%m-%d %H:%M")
               PickupAPIHistory.objects.create(airwaybill_number=awb,ref_pickup=ref_pickup,pickup=pickup,updated_on=updated_on,shipper_code=shipper,shipper_name=shipper_name,username=username,pickupstatus=pickup_status,attempt_date=att_date,freight_status=frt_status,freight_amount=frt_amt,freight_collected=frt_coll)
               PickupAPIAWB.objects.create(airwaybill_number=awb,pickup_id=pickup)
               pkpShipment=PickupAPIShipment.objects.filter(airwaybill_number=awb)
               if pickup_status == "PICKED":
                  pkp_status=0
               else:
                  pkp_status = 1
              
               #if pkpShipment:
               #    pkpShipment.update(pickup_status=pkp_status)
               #else:
               #   PickupAPIShipment.objects.create(pickup_status=pkp_status)
               print shipper,pickup,ref_pickup,shipper_name,username,awb,pickup_status,updated_on,att_date,frt_status,frt_amt,frt_coll,ass_no
               if pickup_status == "PICKED":
                  pkp = PickupRegistration.objects.filter(customer_code__code=shipper,id=pickup).exclude(status=1)
                  print pkp
                  if pkp:
                       ships=Shipment.objects.filter(airwaybill_number=awb,pickup_id=pkp[0].id)
                       if ships:
                            ships.update(status=1)
                            record={"awb":awb,"status":1}
                            processed_awbs.append(record)
                       else:
                            record={"awb":awb,"status":0}
                            processed_awbs.append(record)

               #else:
                   #pickups needs to be created  
                         #if n == b.nodeName:
                    #    print "values are","Node is",n,"\t",b.childNodes[0].data
               print "############## NEW RECORDs from views  #############",shipper
               #return HttpResponse ("request processed")
        resp_dict["status"]="1"
        resp_dict["awbs"]=processed_awbs
        return HttpResponse(simplejson.dumps(resp_dict),content_type="application/json")
    else:
        resp_dict["status"]="0"   
        resp_dict["message"]="Invalid request"
        return HttpResponse(simplejson.dumps(resp_dict),content_type="application/json")     

   
      
