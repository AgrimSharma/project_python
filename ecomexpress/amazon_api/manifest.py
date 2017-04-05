# Create your functions here.

import os
import sys

from os import walk

PROJECT_ROOT_DIR = '/home/web/ecomm.prtouch.com/ecomexpress/'
os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
import fileinput
import json
import xmltodict
#from django.views.decorators.csrf import csrf_exempt
#from django.http import HttpResponse

from django.core.servers.basehttp import FileWrapper

from service_centre.models import *
#from privateviews.decorators import login_not_required
from amazon_api.models import *


from daemon import runner
import logging

def reset_database_connection():  
    from django import db  
    db.close_connection()  
    
#@login_not_required
#@csrf_exempt
def my_xml_reader(file_tobe_processed):
    """
	Reads xml and creates a dict of objects of the form key=node.element:value=value.
	Dicts are created for each node specified in 'stats' declaration.
	After all nodes are processed, returns a list of dicts that can then be called using
	keys of the form "node.element" to get values.
    @params xml file of name cscac.xml
    @returns list of dicts
    """
    '''
	known limitations: 
	Currently does not equally treat all child nodes that have identical names. 
	This means identically named siblings in immediate parents 
	are not all expressed and contained in the dicts. 
	This is possibly a limitation of the way input xml is encoded since there is no implicit
	pattern in which nodes are absent. Therefore, of identically named
	subelements, only one subelement seems to be parsed presently.
	However, identically named subelements in different parent nodes are expressed
	separately without any trouble.
    '''
    import xmltodict
    f = open(file_tobe_processed,"r")
    xdata = f.read()
    xdictionary = xmltodict.parse(xdata)
    #print len(xdictionary['transmission']['message']['amazonManifest']['manifestDetail']['shipmentDetail'])
    return xdictionary
    #exit()
    import xml.etree.ElementTree as et
    
    #x_tf = et.parse('/mnt/s3mnt/cscac.xml')
    x_tf = et.parse(file)
    ## Test string.
    # x_t = et.fromstring('<ECOMEXPRESS-OBJECTS><SHIPMENT><AWB_NUMBER>103086396</AWB_NUMBER><ORDER_NUMBER>15573113</ORDER_NUMBER><PRODUCT>Adiction Deodorant Spray 150ml</PRODUCT><CONSIGNEE>prateek</CONSIGNEE><CONSIGNEE_ADDRESS1>154-D, NOFRA-1</CONSIGNEE_ADDRESS1><CONSIGNEE_ADDRESS2>DABOLIM AIRPORT ROAD</CONSIGNEE_ADDRESS2><CONSIGNEE_ADDRESS3>DABOLIM AIRPORT ROAD</CONSIGNEE_ADDRESS3><DESTINATION_CITY>VASCO</DESTINATION_CITY><PINCODE>110008</PINCODE><STATE>GA</STATE><MOBILE>9764565877</MOBILE><TELEPHONE>9764565877</TELEPHONE><ITEM_DESCRIPTION>Adiction Deodorant Spray 150ml</ITEM_DESCRIPTION><PIECES>3</PIECES><COLLECTABLE_VALUE>41.00</COLLECTABLE_VALUE><DECLARED_VALUE>1</DECLARED_VALUE><ACTUAL_WEIGHT>1</ACTUAL_WEIGHT><VOLUMETRIC_WEIGHT>1</VOLUMETRIC_WEIGHT><LENGTH>20.00</LENGTH><BREADTH>12.00</BREADTH><HEIGHT>4.00</HEIGHT><VENDOR_ID></VENDOR_ID><PICKUP_NAME>Aleva International</PICKUP_NAME><PICKUP_ADDRESS_LINE1>20/3 Old Market, West Patel Nagar</PICKUP_ADDRESS_LINE1><PICKUP_ADDRESS_LINE2>20/3 Old Market, West Patel Nagar</PICKUP_ADDRESS_LINE2><PICKUP_PINCODE>110008</PICKUP_PINCODE><PICKUP_PHONE>9764565877</PICKUP_PHONE><PICKUP_MOBILE>9764565877</PICKUP_MOBILE></SHIPMENT></ECOMEXPRESS-OBJECTS>')
    root = x_tf.getroot()
    # print root.findall('ShipmentStatus')
    k = 0 
    """For each node called amazonManifest:
       iterate over subnodes and find elements
       for each such node; expand and find text.
    """
    for child in root: #.iter(): # x_tf.getiterator():
        k+=1
        # stats= child.findall('ShipmentStatus')
        #stats= child.findall('amazonManifest')
        stats= child.findall('amazonManifest')
        # stats= child.iter('manifestDetail')
        #print "length of stats", len(stats)
        #exit()
        if len(stats):
            b = []
            for stat in stats:
                # print "="*15
                # print "node", stat.getchildren()
                # print list(stat)
                # found= stat.find('City')
                # print found.text
                a = []
                m={}
                for elem in list(stat):
		    m[str(stat.tag)+'.'+str(elem.tag)]=str(elem.text)
                    for x in elem.iter():
                        # print "this is", elem, "'s ",x.tag,": ", x.text
                        m[str(elem.tag)+"."+str(x.tag)]=str(x.text)
                        # a.append(m)
                # print m
                b.append(m)
            # print b
    # print k
    return b

def create_dummy_manifest():
    '''
    Creates a dummy manifest from a file that has each awb in a separate line
    and an xml file with an _equal_number_of_amazonManifest_tags_ .May fail
    otherwise. Input awbs path might need to be provided.
    @return output.xml
    '''
    f_p = template_path+'/awbs_test'
    # with open('awbs_test', 'r') as a:
    with open(f_p, 'r') as a:
	l = []
	for line in a:
	    l.append(line.strip('\n'))
	print l

    import xml.etree.ElementTree as ET
    tree = ET.parse('cscac.xml')
    root = tree.getroot()
    awbn = root.iter('manifestNumber')
    count = 0
    for awb in awbn:
        awb.text=l[count]
	count+=1
    tree.write('output.xml')


def create_amazon_entry(q):
    """
    Creates an Amazon entry given a successfully validated shipment.
    """
    ## import Shipment 
    ## import datetime
    ## from amazon_api.models import ShipmentStatus ShipmentInformation ShipmentIdentification EstimatedDeliveryDateTime, ItemInformation, TransactionInformation 

    t = datetime.datetime.now()
    tt = datetime.datetime.strftime(t, "%Y-%m-%d %H:%M:%S")
    # Create other Amazon objects. Check for dummy values here.
    eddt = EstimatedDeliveryDateTime.objects.create(estimateddeliverydatetimevalue=tt)
    si = TransactionInformation.objects.create(SenderIdentifier = "amz") 
    ee = EdiDocumentInformation.objects.create()
    shipinf = ShipmentInformation.objects.create(TransactionInformation=si, EdiDocumentInformation=ee)
    ii = ItemInformation.objects.create(itemid = 1, cartonquantity=q["manifestDetail.quantity"], palletquantity=2)
    amship = Shipment.objects.filter(airwaybill_number = long(str(q["awb"])))
    if amship:
	s_id = amship[0]
    else:
        return None
    # ShipmentIdentification maps each shipment with each Amazon ShipmentStatus object.
    # For xml mapping, see: ShipmentIdentification.objects.create(messagereferencenum=stat.get('ShipmentIdentification.MessageReferenceNum'), amazonreferencenumber=stat.get('ShipmentIdentification.AmazonReferenceNumber'), shipment_status=shipment_status)
    AMZShipment.objects.create(shipment= s_id, 
                               message_reference_num = q['message_reference_num'],
                               carrier_tracking_num = q['carrier_tracking_num'],
                               amazon_reference_number = q['amazon_reference_number'],
                               transport_mode = q['transport_mode'],
                               reference_id = q['reference_id'])
    return AMZShipment


    ssi = ShipmentIdentification.objects.create(messagereferencenum=9788787, shipmentidentifier=s_id, amazonreferencenumber="23345", shipmentinformation=shipinf)
    sstat= ShipmentStatus.objects.create(shipment_info = ssi, appointmentstatus="ofd", appointmentstatusreason="x", carrierscac="ECXIN",
    transportmode="AMtoEE", iteminformation = ii, datetimeperiodcode=eddt)
    # Shipment.objects.get(id=c.shipmentidentifier_id)
    print "sttat", sstat
 
    if sstat:
	return True
    else:
	# print "ERROR"
        return False


def map_shipment(file_tobe_processed):
    """
    This method maps amazon shipments to manifest. .xml file needs to be explicitly specified 
    in my_xml_reader at this point.
    Check error.log for errors in creating Amazon ShipmentStatus objects.
    """
    '''
    Shipment template:
	    { "AWB_NUMBER": "103086828", "ORDER_NUMBER": "7677", "PRODUCT":
	"PPD", "CONSIGNEE": "TEST", "CONSIGNEE_ADDRESS1":
	"ADDR1",
	"CONSIGNEE_ADDRESS2": "ADDR2", "CONSIGNEE_ADDRESS3": "ADDR3",
	"DESTINATION_CITY": "MUMBAI", "PINCODE": "400067", "STATE": "MH",
	"MOBILE": "156729", "TELEPHONE": "1234", "ITEM_DESCRIPTION": "MOBILE",
	"PIECES": "1", "COLLECTABLE_VALUE": " 3000 ", "DECLARED_VALUE": " 3000 ",
	"ACTUAL_WEIGHT": "5", "VOLUMETRIC_WEIGHT": "0" , "LENGTH": " 10",
	"BREADTH": "10", "HEIGHT": "10", "PICKUP_NAME": "abcde",
	"PICKUP_ADDRESS_LINE1": "Samalkha", "PICKUP_ADDRESS_LINE2":
	"kapashera", "PICKUP_PINCODE" : "110013", "PICKUP_PHONE": "98204",
	"PICKUP_MOBILE": "59536","RETURN_PINCODE": "110013", "RETURN_NAME":
	"abcde", "RETURN_ADDRESS_LINE1": "Samalkha", "RETURN_ADDRESS_LINE2":
	"kapashera", "RETURN_PINCODE": "110013", "RETURN_PHONE": "98204",
	"RETURN_MOBILE": "59536" }
    '''
    json_input = []
    from reports.report_api import ReportGenerator
    #report = ReportGenerator('/home/s3/as2/reports/reports.xlsx' )
    #report = ReportGenerator('/home/s3/as2/reports/%s.xlsx' % datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d%H%M%S"))
    
    #print report
    #exit()
    if 1==1:
	manifest_xml = my_xml_reader(file_tobe_processed)
	#print "correct xml!"
        px = manifest_xml['transmission']['message']['amazonManifest']['manifestDetail']['shipmentDetail']
        if not type(manifest_xml['transmission']['message']['amazonManifest']['manifestDetail']['shipmentDetail']) is list:
            px = [manifest_xml['transmission']['message']['amazonManifest']['manifestDetail']['shipmentDetail']]
	#print manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["name"]

        PICKUP_NAME = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["name"]
        PICKUP_ADDRESS_LINE1 = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["addressLine1"]
        PICKUP_ADDRESS_LINE2 = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["addressLine2"] + ", " + manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["addressLine3"]
        PICKUP_PINCODE = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["zip"]
        print  manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']
        #exit()
        if manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"].get("contactPhone"):
            PICKUP_PHONE = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["contactPhone"]
        else: 
            PICKUP_PHONE = ""
        RETURN_NAME = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["name"]
        RETURN_ADDRESS_LINE1 = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["addressLine1"]
        RETURN_ADDRESS_LINE2 = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["addressLine2"] + ", " + manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["addressLine3"]
        RETURN_PINCODE = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["zip"]
        if manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"].get("contactPhone"):
            RETURN_PHONE = manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["shipFromAddress"]["contactPhone"]
        else: 
            RETURN_PHONE = ""
        #exit();
        for p in px:
            i = {}
            #print json.dumps(p)


            #exit()
	    if not p["shipmentPackageInfo"]["ShipmentMethodOfPayment"] == "COD":
	        p["shipmentPackageInfo"]["ShipmentMethodOfPayment"] = "PPD"
	    if not p["consigneeAddress"].get("addressLine2"):
	        p["consigneeAddress"]["addressLine2"] = ""

	        # print p["manifestDetail.paymentMethod"] is "COD"
            i = {"AWB_NUMBER": p["shipmentPackageInfo"]["cartonID"]["trackingID"], "ORDER_NUMBER": p["customerOrderNumber"], "PRODUCT":p["shipmentPackageInfo"]["ShipmentMethodOfPayment"], "CONSIGNEE": p["consigneeAddress"]["name"], "CONSIGNEE_ADDRESS1":p["consigneeAddress"]["addressLine1"], "CONSIGNEE_ADDRESS2":p["consigneeAddress"]["addressLine2"], "CONSIGNEE_ADDRESS3":"", "DESTINATION_CITY":p["consigneeAddress"]["city"], "PINCODE":p["consigneeAddress"]["zip"], "STATE": p["consigneeAddress"]['stateChoice']["stateProvince"], "MOBILE": p["consigneeAddress"]["contactPhone"], "TELEPHONE": "", "ITEM_DESCRIPTION": p["shipmentPackageInfo"]["pkgHarmonizedTariffDescription"], "PIECES": p['shipmentPackageInfo']['shipmentPackageItemQuantity']["quantity"]['#text'], "COLLECTABLE_VALUE": p["shipmentCostInfo"]["CashOnDeliveryCharge"]["monetaryAmount"]["#text"], "DECLARED_VALUE": p["shipmentCostInfo"]["valueOfGoods"]["monetaryAmount"]["#text"], "ACTUAL_WEIGHT": p["shipmentPackageInfo"]["shipmentPackageActualGrossWeight"]["weightValue"]["#text"], "VOLUMETRIC_WEIGHT": "", "LENGTH": p["shipmentPackageInfo"]["shipmentPackageDimensions"]["lengthValue"]["#text"], "BREADTH": p["shipmentPackageInfo"]["shipmentPackageDimensions"]["widthValue"]["#text"], "HEIGHT": p["shipmentPackageInfo"]["shipmentPackageDimensions"]["heightValue"]["#text"], "PICKUP_NAME": PICKUP_NAME, "PICKUP_ADDRESS_LINE1": PICKUP_ADDRESS_LINE1, "PICKUP_ADDRESS_LINE2": PICKUP_ADDRESS_LINE2, "PICKUP_PINCODE" : PICKUP_PINCODE, "PICKUP_PHONE": PICKUP_PHONE, "PICKUP_MOBILE": "0", "RETURN_PINCODE": RETURN_PINCODE, "RETURN_NAME": RETURN_NAME, "RETURN_ADDRESS_LINE1": RETURN_ADDRESS_LINE1, "RETURN_ADDRESS_LINE2": RETURN_ADDRESS_LINE2, "RETURN_PINCODE": RETURN_PINCODE, "RETURN_PHONE": RETURN_PHONE, "RETURN_MOBILE":"0"}
	    #i = {"AWB_NUMBER": p["manifestDetail.trackingID"], "ORDER_NUMBER": p["customerOrderNumber"], "PRODUCT":p["ShipmentMethodOfPayment"], "CONSIGNEE": p["manifestDetail.name"], "CONSIGNEE_ADDRESS1":p["manifestDetail.addressLine1"], "CONSIGNEE_ADDRESS2":p["manifestDetail.addressLine2"], "CONSIGNEE_ADDRESS3":p["manifestDetail.addressLine2"], "DESTINATION_CITY":p["manifestDetail.city"], "PINCODE":p["manifestDetail.zip"], "STATE": p["manifestDetail.stateProvince"], "MOBILE": p["manifestDetail.contactPhone"], "TELEPHONE": p["manifestDetail.contactPhone"], "ITEM_DESCRIPTION": p["manifestDetail.itemTitle"], "PIECES": p["manifestDetail.quantity"], "COLLECTABLE_VALUE": p["manifestDetail.monetaryAmount"], "DECLARED_VALUE": p["manifestDetail.totalDeclaredValue"], "ACTUAL_WEIGHT": p["manifestSummary.weightValue"], "VOLUMETRIC_WEIGHT": p["manifestDetail.weightValue"], "LENGTH": p["manifestDetail.lengthValue"], "BREADTH": p["manifestDetail.widthValue"], "HEIGHT": p["manifestDetail.heightValue"], "PICKUP_NAME": p["manifestHeader.name"], "PICKUP_ADDRESS_LINE1": p["manifestHeader.addressLine1"], "PICKUP_ADDRESS_LINE2": p["manifestHeader.addressLine2"], "PICKUP_PINCODE" : p["manifestHeader.zip"], "PICKUP_PHONE": "0", "PICKUP_MOBILE": "59536", "RETURN_PINCODE": p["manifestHeader.zip"], "RETURN_NAME": p["manifestHeader.name"], "RETURN_ADDRESS_LINE1": p["manifestHeader.addressLine1"], "RETURN_ADDRESS_LINE2": p["manifestHeader.addressLine2"], "RETURN_PINCODE": p["manifestHeader.zip"], "RETURN_PHONE": p["manifestDetail.contactPhone"], "RETURN_MOBILE":p["manifestDetail.contactPhone"]}
	    json_input.append(i)
            # print json_input

        import requests

        #payload = {'username':'amazon','password':'a1m2a3a4z9o8n8e','json_input':json.dumps(json_input)}
        payload = {'username':'ecomexpress','password':'Ke$3c@4oT5m6h#$','json_input':json.dumps(json_input)}
        ## use a HTTP request to get json response from apiv2. Can directly use apiv2 python import?
        r = requests.post("http://ecomm.prtouch.com/apiv2/manifest_awb/", data=payload)
        print r
        print payload
        s = r.json()
        # print type(s)

        ##If all ok, generate header. Start processing to create Amazon Statuses.
        headers = ['reason', 'order_number', 'awb', 'success']
        print "report.write_header"
        #report.write_header(headers)
        for x in s['shipments']:
            # print x
	    if x['success'] == True:
	        for p in px:
		    if p["shipmentPackageInfo"]["cartonID"]["trackingID"] == x['awb']:
		        q = {}
		        q["manifestDetail.quantity"] = p['shipmentPackageInfo']['shipmentPackageItemQuantity']["quantity"]['#text']
		        q["awb"] = x["awb"]
		        q["message_reference_num"] =  manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["manifestNumber"]
		        q["carrier_tracking_num"] =  x["awb"]
		        q["amazon_reference_number"] =  manifest_xml['transmission']['message']['amazonManifest']['manifestHeader']["manifestNumber"]
		        q["transport_mode"] =   p['shipmentPackageInfo']['ShipmentMethodOfPayment']
		        q["reference_id"] =   p['shipmentPackageInfo']['cartonID']['encryptedShipmentID']
		        amz_status_created = create_amazon_entry(q)
		        print "amz_status_created", amz_status_created
		        if not amz_status_created:
			    print "Amazonstatus for ",x['awb']," not created."
			    #with open("/home/s3/as2/reports/error.log", "rw+") as err:
			    #    err_string="\nAmazonstatus for ",x['awb']," not created "+today
			    #    err.write(err_string)
            #report.write_row(list(x.values()))
    else :
        print "bad xml!"
        #report.write("Please check xml format")
    return True


def generate_ship_status():
    """
    Generates shipment status from amazon models.
    """
    from amazon_api.models import ShipmentStatus, ShipmentIdentification, EstimatedDeliveryDateTime
    amz_ships = ShipmentStatus.objects.all()
    entry_string = ""
    for amz_ship in amz_ships:
	c = ShipmentIdentification.objects.get(id=amz_ship.shipment_info.id)
	shipment = Shipment.objects.get(id=c.shipmentidentifier_id)
	# ShipToInformation :: consignee
        partyname = shipment.consignee
        addressline1 = shipment.consignee_address1
        addressline2 = shipment.consignee_address2
        addressline3 = shipment.consignee_address3
        addresscity = shipment.destination_city
	addressstateprovincecode = shipment.state
	addresspostalcode = str(shipment.pincode)	 
	# LocationOfFreight
	import datetime
	#now = datetime.datetime.now()
	ship_date = datetime.datetime.now() #-datetime.timedelta(days=7)
	if amz_ship.get_loccode(ship_date):
	    loc = amz_ship.get_loccode(ship_date)
	    locaddresscity = loc.city.city_name
	    locaddressstate = loc.city.state.state_name
	else:
	    loc, locaddresscity, locaddressstate = "","",""
	# ShipmentStatus
	status = str(shipment.status)
	statusreason = str(0)# shipment.reason_code
	# TransportMode
	transport = amz_ship.transportmode
	# DateTimePeriodInformation
	dtpi = amz_ship.datetimeperiodcode.get_DTPI()
	datetimeperiodcode = dtpi[0]
	datetimeperiodformat = dtpi[1]
	datetimeperiodvalue = dtpi[2]

	datetimeperiodcode = str(amz_ship.datetimeperiodcode.datetimeperiodcode)
	datetimeperiodformat = amz_ship.datetimeperiodcode.estimateddeliverydatetimeformat 
	datetimeperiodvalue = str(amz_ship.datetimeperiodcode.estimateddeliverydatetimevalue )

	ship_stat = "<ShipmentStatus><ShipmentIdentification> <MessageReferenceNum>DXj5pJnDR</MessageReferenceNum> <CarrierTrackingNum>9102901000076005492218</CarrierTrackingNum> </ShipmentIdentification> <ShipToInformation> <PartyName>"+partyname+"</PartyName> <Address> <Line1>"+addressline1+"</Line1> <Line2>"+addressline2+"</Line2> <Line3>"+addressline3+"</Line3> <City>"+addresscity+"</City> <StateProvinceCode>"+addressstateprovincecode+"</StateProvinceCode> <PostalCode>"+addresspostalcode+"</PostalCode> <CountryCode>IN</CountryCode> </Address> </ShipToInformation> <LocationOfFreight> <Address> <City>"+locaddresscity+",</City> <StateProvinceCode>"+locaddressstate+"</StateProvinceCode> <CountryCode>IN</CountryCode> </Address> </LocationOfFreight> <ShipmentStatusInformation> <Status>"+status+"</Status> <StatusReason>"+statusreason+"</StatusReason> </ShipmentStatusInformation> <TransportInformation> <TransportMode>"+transport+"</TransportMode> <CarrierSCAC>SCAC</CarrierSCAC> </TransportInformation> <DateTimePeriodInformation> <DateTimePeriodCode>"+datetimeperiodcode+"</DateTimePeriodCode> <DateTimePeriodFormat>"+datetimeperiodformat+"</DateTimePeriodFormat> <DateTimePeriodValue>"+datetimeperiodvalue+"</DateTimePeriodValue> </DateTimePeriodInformation> <ShipmentReferenceSequence> <ShipmentReference> <ReferenceId>DXj5pJnDR</ReferenceId> <ReferenceIdType /> </ShipmentReference> </ShipmentReferenceSequence> </ShipmentStatus>\n "
	#if amz_ships.index(amz_ship) == len(amz_ships) - 1:
	# ship_stat.append('\n')

        entry_string+=ship_stat
	# print entry_string
	# return
    file_path = PROJECT_ROOT_DIR + 'static/uploads/reports/status_outfile.xml'
    template_path = os.path.dirname(os.path.abspath(__file__)) 
     
    with open(file_path, 'w') as outfile:
    # "Ensure file RF.txt is in the same folder as utils.py".
    	try:
            for line in fileinput.input(template_path+'/SF.txt'):
                # outfile.write(line.replace('TiMe HeRe', time_string))
       	        outfile.write(line.replace('StAtUsEs HeRe', entry_string))
		# print 'done\n'
        except:
    	    return None # HttpResponse("Template not found.")
 
    filed = FileWrapper(file(file_path))
    # print filed

def process_file():
    #create_dummy_manifest()
    #generate_ship_status()
    map_shipment("%s" % ("/home/jignesh/2015-06-11-1415.488077627.DEL2.MANIFEST"))
    return False
    manifest_file_path = '/home/s3/as2/receive/users/52.74.152.61/amazonlive/home/as2'
    manifest_processed_path = '/home/s3/as2/processed'
    for (dirpath, dirnames, filenames) in walk(manifest_file_path):
     for filename in filenames:
         if 'MANIFEST' in filename:
              print "%s" % (manifest_file_path+"/"+filename)   
              map_shipment("%s" % (manifest_file_path+"/"+filename))
              os.rename("%s" % (manifest_file_path+"/"+filename), "%s" % (manifest_processed_path+"/"+filename))
    # print my_xml_reader()
    #read_shipment_status()
    #pass



class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/api_daeomn/amazone_manifest_process.pid'
        self.pidfile_timeout = 5 
    
    def run(self):
        while True:
            #Main code goes here ...
            reset_database_connection()
            process_file()
            time.sleep(30)
app = App()
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/api_daeomn/amazone_manifest_process.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()

#today = datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d")
#template_path = os.path.dirname(os.path.abspath(__file__)) 


