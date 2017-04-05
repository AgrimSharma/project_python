from math import ceil
import datetime
from datetime import timedelta

from django.db.models import *
from django.core.mail import send_mail
from django.db.models.loading import get_model
from django.core.exceptions import PermissionDenied
from delivery.models import *
from reports.models import *
from airwaybill.models import AirwaybillNumbers
from customer.models import *
from service_centre.models import *
from billing.models import *
from billing.charge_calculations import add_to_shipment_queue
from reports.models import ShipmentBagHistory

now=datetime.datetime.now()
t8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
t3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)

def get_subcustomer(shid):
    shipper=Shipper.objects.get(id=shid)
    address=""
    add=shipper.address 
    if add.address1 is not None:
       address = address + add.address1    
    if add.address2 is not None:
       address = address + add.address2
    if add.address3 is not None:
       address = address + add.address3
    if add.address4 is not None:
       address = address + add.address4  
    return address,add.pincode

def create_vendor(name,address,phone,pincode,customer_code,return_pincode=0):
    #customer_code = int(customer_code)
    customer=Customer.objects.filter(code=customer_code)
    #return_pincode = int(return_pincode)
    return_pincode = str(return_pincode)
    #return HttpResponse(customer_code)
    if customer:
       customer = customer[0]
       pin = Pincode.objects.get(pincode=pincode)
       city=pin.service_center.city
       state = city.state
       address  =  Address.objects.create(city=city,state=state,address1=address,phone=phone,pincode=pincode)
       shipper = Shipper.objects.create(address=address,customer=customer,name=name)
       ShipperMapping.objects.create(shipper=shipper,forward_pincode=pincode,return_pincode=return_pincode)
       return shipper       

def get_vendor(name,address,phone,pincode,customer_code,return_pincode=0):
    #from django.http import HttpResponse
    #tmp = ""
    #return HttpResponse(name,address,phone,pincode,customer_code,return_pincode)
    #subcustomer=None
    #customer_code = int(customer_code)
    customer_code = str(customer_code)
    #pincode=int(pincode)
    pincode = str(pincode)
    shipper= Shipper.objects.filter(name=name,address__pincode=pincode,customer__code=customer_code)
    if shipper:
        subcustomer = shipper[0].id
       # for ship in shipper:
          # u=get_subcustomer(ship)
           #if u[0] == address and u[1] == pincode:
             #id=shipper[0].id
             #break;
    else:
        subcust =  create_vendor(name,address,phone,pincode,customer_code,return_pincode)
        if subcust :
           subcustomer = subcust.id
    return subcustomer


