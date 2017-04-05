# Create your functions here.

import os
import sys

STATUS_ROOT_DIR = '/home/s3/as2/status_files/'
SENDSTATUS_ROOT_DIR = '/home/s3/as2/send/'
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
from service_centre.models import *
import datetime
import shutil


from daemon import runner
import logging

def reset_database_connection():
    from django import db
    db.close_connection()



#today = datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d")
template_path = os.path.dirname(os.path.abspath(__file__)) 

get_month = lambda month: str(month) if len(str(month)) == 2 else '0' + str(month)

def generate_ship_status(seconds = 3600, year_month=datetime.datetime.now().strftime("%Y_%m")):
    """
    Generates shipment status from amazon models.
    """
    from amazon_api.models import ShipmentStatus, ShipmentIdentification, EstimatedDeliveryDateTime

    now = datetime.datetime.now()
    #start_time = now - datetime.timedelta(days=start_days)
    start_time = now - datetime.timedelta(seconds=seconds)
    end_time = now 
    #month = get_month(now)
    #year_month = year_month
    #print year_month, hours
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(year_month))
    awbs = shipment_history.objects.filter(updated_on__range=(start_time, end_time), shipment__shipper_id = 375).exclude(status = 0)
    #print awbs
    entry_string = '''<?xml version="1.0" encoding="us-ascii"?>
<ShipmentInformation>
<TransactionInformation>
 <SenderIdentifier>ECXIN</SenderIdentifier>
 <RecipientIdentifier>AMAZON</RecipientIdentifier>
 <DateOfPreparation>%s</DateOfPreparation>
 <TimeOfPreparation>%s</TimeOfPreparation>
</TransactionInformation>
<EdiDocumentInformation>
<EdiDocumentStandard>X12</EdiDocumentStandard>
<EdiDocumentName>XML</EdiDocumentName>
<EdiDocumentVersion>1.1</EdiDocumentVersion>
</EdiDocumentInformation>
<ShipmentStatusSeq>''' % (now.strftime("%Y%m%d"), now.strftime("%H%M%S"))
    if not awbs:
        return False

    for hist in awbs:
	#ship_stat = "<ShipmentStatus><ShipmentIdentification> <MessageReferenceNum>DXj5pJnDR</MessageReferenceNum> <CarrierTrackingNum>9102901000076005492218</CarrierTrackingNum> </ShipmentIdentification> <ShipToInformation> <PartyName>"+partyname+"</PartyName> <Address> <Line1>"+addressline1+"</Line1> <Line2>"+addressline2+"</Line2> <Line3>"+addressline3+"</Line3> <City>"+addresscity+"</City> <StateProvinceCode>"+addressstateprovincecode+"</StateProvinceCode> <PostalCode>"+addresspostalcode+"</PostalCode> <CountryCode>IN</CountryCode> </Address> </ShipToInformation> <LocationOfFreight> <Address> <City>"+locaddresscity+",</City> <StateProvinceCode>"+locaddressstate+"</StateProvinceCode> <CountryCode>IN</CountryCode> </Address> </LocationOfFreight> <ShipmentStatusInformation> <Status>"+status+"</Status> <StatusReason>"+statusreason+"</StatusReason> </ShipmentStatusInformation> <TransportInformation> <TransportMode>"+transport+"</TransportMode> <CarrierSCAC>EXCIN</CarrierSCAC> </TransportInformation> <DateTimePeriodInformation> <DateTimePeriodCode>"+datetimeperiodcode+"</DateTimePeriodCode> <DateTimePeriodFormat>"+datetimeperiodformat+"</DateTimePeriodFormat> <DateTimePeriodValue>"+s.+"</DateTimePeriodValue> </DateTimePeriodInformation> <ShipmentReferenceSequence> <ShipmentReference> <ReferenceId>DXj5pJnDR</ReferenceId> <ReferenceIdType /> </ShipmentReference> </ShipmentReferenceSequence> </ShipmentStatus>\n "
        s = hist.shipment
        if not s.amzshipment_set.filter():
            continue 
        amzsh = s.amzshipment_set.get() 
        if hist.reason_code:
            amz_status = AMZShipmentSatus.objects.filter(status_code = hist.reason_code.code)
        else:
            amz_status = AMZShipmentSatus.objects.filter(status_code = hist.status)
        print amz_status
        if amz_status:
            status = amz_status[0].amz_status_code
            statusreason = amz_status[0].amz_reason_code
        else:
            status = "AF" 
            statusreason = "NS" 
	ship_stat = "<ShipmentStatus><ShipmentIdentification> <MessageReferenceNum>"+amzsh.message_reference_num+"</MessageReferenceNum> <CarrierTrackingNum>"+str(s.airwaybill_number)+"</CarrierTrackingNum> </ShipmentIdentification> <ShipToInformation> <PartyName>"+s.consignee+"</PartyName> <Address> <Line1>"+s.consignee_address1+"</Line1> <Line2>"+s.consignee_address2+"</Line2> <Line3>"+s.consignee_address3+"</Line3> <City>"+s.destination_city+"</City> <StateProvinceCode>"+s.state+"</StateProvinceCode> <PostalCode>"+str(s.pincode)+"</PostalCode> <CountryCode>IN</CountryCode> </Address> </ShipToInformation> <LocationOfFreight> <Address> <City>"+s.current_sc.city.city_name+",</City> <StateProvinceCode>"+s.current_sc.city.state.state_name+"</StateProvinceCode> <CountryCode>IN</CountryCode> </Address> </LocationOfFreight> <ShipmentStatusInformation> <Status>"+status+"</Status> <StatusReason>"+statusreason+"</StatusReason> </ShipmentStatusInformation> <TransportInformation> <TransportMode>"+amzsh.transport_mode+"</TransportMode> <CarrierSCAC>ECXIN</CarrierSCAC> </TransportInformation> <DateTimePeriodInformation> <DateTimePeriodCode>203</DateTimePeriodCode><DateTimePeriodDescription>IST</DateTimePeriodDescription><DateTimePeriodFormat>YYYYMMDDHHMMSS</DateTimePeriodFormat> <DateTimePeriodValue>"+hist.updated_on.strftime("%Y%m%d%H%M%S")+"</DateTimePeriodValue> </DateTimePeriodInformation> <EstimatedDeliveryDateTime> <DateTimePeriodCode>203</DateTimePeriodCode><EstimatedDeliveryDateTimeTz>IST</EstimatedDeliveryDateTimeTz> <EstimatedDeliveryDateTimeFormat>YYYYMMDDHHMMSS</EstimatedDeliveryDateTimeFormat> <EstimatedDeliveryDateTimeValue>"+s.expected_dod.strftime("%Y%m%d%H%M%S")+"</EstimatedDeliveryDateTimeValue> </EstimatedDeliveryDateTime> <ShipmentReferenceSequence> <ShipmentReference> <ReferenceId>"+amzsh.reference_id+"</ReferenceId> <ReferenceIdType /> </ShipmentReference> </ShipmentReferenceSequence> </ShipmentStatus>\n "
        if not ship_stat:
            return "No Shipment Found"
	#if amz_ships.index(amz_ship) == len(amz_ships) - 1:
	# ship_stat.append('\n')

        entry_string+=ship_stat
	#print entry_string
	# return
    entry_string+='</ShipmentStatusSeq>\n</ShipmentInformation>'
    file_name = 'status_outfile%s.xml' % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = STATUS_ROOT_DIR + file_name
    send_file_path = SENDSTATUS_ROOT_DIR + file_name
    #template_path = os.path.dirname(os.path.abspath(__file__)) 
     

    #print template_path
    #print entry_string
    #exit()
    #return None

    with open(file_path, 'w') as outfile:
    # "Ensure file RF.txt is in the same folder as utils.py".
        outfile.write( entry_string)
#   	try:
#           for line in fileinput.input(template_path+'/SF.txt'):
#               # outfile.write(line.replace('TiMe HeRe', time_string))
#      	        outfile.write( entry_string)
#       	print 'done\n'
#       except:
#   	    return None # HttpResponse("Template not found.")
 
    filed = FileWrapper(file(file_path))
    print send_file_path
    shutil.copy(file_path, send_file_path)
    return True

    
def process_status():
    #create_dummy_manifest()
    generate_ship_status()
    #generate_ship_status(year_month="2015_04")
    #generate_ship_status(year_month="2015_03")
    #generate_ship_status(year_month="2015_02")
    #map_shipment()   
    # print my_xml_reader()
    #read_shipment_status()
    #pass


class App():

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/api_daeomn/amazone_status_process.pid'
        self.pidfile_timeout = 5

    def run(self):
        while True:
            #Main code goes here ...
            reset_database_connection()
            process_status()
            time.sleep(3600)
app = App()
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/api_daeomn/amazone_status_process.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()



