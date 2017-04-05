import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
import urllib2
import urllib
from service_centre.models import Customer
from urllib2 import urlopen, HTTPError
import httplib2
import httplib, urllib
from xml.etree import ElementTree
from xml.dom.minidom import parseString    
import xmltodict
from xml.dom.minidom import Node
import xml.dom.minidom
from xml.dom.minidom import parse
import StringIO
from mobi_api.models import	*

def main():
     params = urllib.urlencode({'customerCode':'c00000002','Password':'traconmobi@123','datetime':'2014-09-01 10:00'})
     headers = {"Content-Length":len(params),"Host":"navatech.cloudapp.net","Content-type": "application/x-www-form-urlencoded"}
     conn = httplib.HTTPConnection("navatech.cloudapp.net")
     conn.request("POST","/TOMWS/Pickup.asmx/TOM_PCK_EXPORT",params,headers)
     response = conn.getresponse()
     print response.status
     if response.status == '200' or response.status == 200:
        print "####################################"
        r=response.read()
        stri=response.read()
        #return str(r)
        dom = parse(StringIO.StringIO(r))
        newdata=[]
        data=["AssignmentRefPickUpID","AssignmentNo","ClientPickUpID","ClientShipperAccNo","ClientShipperName","UserName","Scan_Item","PickupStatus","isFreight","FreightAmount","FreightCollected","AttemptDate","AttemptTime","ServerUpdateDateTime"]
        newdata.append("anyType")
     #pickup_list=[] 
     #awb_list=[]
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
                            
               #else:
                   #pickups needs to be created  
                         #if n == b.nodeName:
                    #    print "values are","Node is",n,"\t",b.childNodes[0].data
               print "############## NEW RECORD #############",shipper
               
      # store awbs here
      # cehck pickup status
      # if picked up 
      # check awb and check pickups 

main()
