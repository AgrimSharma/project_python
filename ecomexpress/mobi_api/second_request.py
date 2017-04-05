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
     code="C00000002"
     password="traconmobi@123"
     ships_records=[]
     resp_dict={}
     resp_dict["shipments"]=ships_records
     data="""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TOM_PCK_IMPORT xmlns="http://navatech.cloudapp.net/TOMWS/">
      <objValue>
        <customerCode>"""+code+"""</customerCode>
        <Password>"""+password+"""</Password>
        <JsonPickupData>"""+str(resp_dict)+"""</JsonPickupData>
      </objValue>
    </TOM_PCK_IMPORT>
  </soap:Body>
</soap:Envelope>"""
     print data
     headers = {
    'Host': 'navatech.cloudapp.net',
    'Content-Type': 'text/xml; charset=utf-8',
    'Content-Length': len(data),
    'SOAPAction': "http://navatech.cloudapp.net/TOMWS/TOM_PCK_IMPORT"
    }
     site="http://navatech.cloudapp.net/TOMWS/Pickup.asmx?op=TOM_PCK_IMPORT"
     auth_handler = urllib2.HTTPBasicAuthHandler()
     opener = urllib2.build_opener(auth_handler)
     urllib2.install_opener(opener)
     page = urllib2.urlopen(site)
     req = urllib2.Request(site, data, headers)
     response = urllib2.urlopen(req)
     the_page = response.read()
     print "response is "
     print (the_page)

main()
