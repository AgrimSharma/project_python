# Create your views here.
import os
import sys 

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from django.db import models
import pdb 
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from smsapp.models import * 
from service_centre.models import *
from urllib import quote, unquote
import requests

def add_awb(awb):
    ship=Shipment.objects.get(airwaybill_number=awb)
    SMSQueue.objects.create(awb=awb,types=ship.product_type,short_name=ship.shipper.code,order_no=ship.order_number,cod_amount=ship.collectable_value,item_description=ship.item_description)

def process_queue():
    queue=SMSQueue.objects.filter(status=0)
    for q in queue:
       ship = Shipment.objects.get(airwaybill_number=q.awb)
       if ship.reverse_pickup:
          temp=SMSTemplate.objects.filter(prod_type="rev")
       else:
          temp=SMSTemplate.objects.filter(prod_type=q.types)
       if temp:
         msg_body=temp[0].template
         msg_body = msg_body.replace("AWB",str(q.awb))
         msg_body= msg_body.replace("ORDERNUM",str(ship.order_number))
         msg_body = msg_body.replace("COLL_AMT",str(ship.collectable_value))
         sh=Shipment.objects.get(airwaybill_number=q.awb)
         mobile = sh.mobile
         if sh.shipper.website:
            site=sh.shipper.website        
         else:        
            site = sh.shipper.name[:14]   
            site = site+"."       
         msg_body =  msg_body.replace("DOMAIN.COM",site)
         msg_body = quote(msg_body.encode('utf8'))
         req_url="http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="+str(mobile)+"&msg="+str(msg_body)+"&msg_type=TEXT&userid=2000135917&auth_scheme=plain&password=UMCBY1pJ0&v=1.1&format=text&password=Y4ZFLe"
         r=requests.get(req_url)
         if r.status_code == 200:
             SMSQueue.objects.filter(id=q.id).update(status=1)
    return HttpResponse("Success")

