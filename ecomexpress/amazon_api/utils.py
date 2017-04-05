# Create your functions here.

import os
import sys

PROJECT_ROOT_DIR = '/home/web/ecomm.prtouch.com/ecomexpress/'
os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
import fileinput
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from service_centre.models import *
from privateviews.decorators import login_not_required
# from api.utils import api_auth

today = datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d")

@login_not_required
@csrf_exempt
def read_shipment_status():

    import xml.etree.ElementTree as et
    '''
    if request.POST or request.GET:
        username = request.POST.get('username', None)
        if not username:
            username = request.GET.get('username', None)

        if username.strip().lower() == 'ecomexpress':
            capi = CustomerAPI.objects.get(username='ecomexpress')    
        else:
            capi =  api_auth(request)
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")
    
    #return HttpResponse("Incomplete or no input provided. %s" % request.GET)
    if not capi or  not request.POST.get('xml_input'):
        return HttpResponse("Incomplete or no input provided.")
    xmlshipments = request.POST['xml_input']
    # xmlshipments = xmlshipments.replace("\\t","")

    if request.POST:
    '''
	# xml_tree = et.parse(request.GET.get("strXML"))
    xml_tree = et.fromstring(xmlshipments)
	# for i in gotxmltree.getiterator():
	#    print i.tag, i.text

    xml_tree = '<ECOMEXPRESS-OBJECTS><SHIPMENT><AWB_NUMBER>103086396</AWB_NUMBER><ORDER_NUMBER>15573113</ORDER_NUMBER><PRODUCT>Adiction Deodorant Spray 150ml</PRODUCT><CONSIGNEE>prateek</CONSIGNEE><CONSIGNEE_ADDRESS1>154-D, NOFRA-1</CONSIGNEE_ADDRESS1><CONSIGNEE_ADDRESS2>DABOLIM AIRPORT  ROAD</CONSIGNEE_ADDRESS2><CONSIGNEE_ADDRESS3>DABOLIM AIRPORT ROAD</CONSIGNEE_ADDRESS3><DESTINATION_CITY>VASCO</DESTINATION_CITY><PINCODE>110008</PINCODE><STATE>GA</STATE><MOBILE>9764565877</MOBILE><TELEPHONE>9764565877</TELEPHONE><ITEM_DESCRIPTION>Adiction Deodorant Spray 150ml</ITEM_DESCRIPTION><PIECES>3</PIECES><COLLECTABLE_VALUE>41.00 </COLLECTABLE_VALUE><DECLARED_VALUE>1</DECLARED_VALUE><ACTUAL_WEIGHT>1</ACTUAL_WEIGHT><VOLUMETRIC_WEIGHT>1</VOLUMETRIC_WEIGHT><LENGTH> 20.00</LENGTH><BREADTH>12.00</BREADTH><HEIGHT>4.00</HEIGHT><VENDOR_ID></VENDOR_ID><PICKUP_NAME>Aleva International</PICKUP_NAME><PICKUP_ADDRESS_LINE1>20/3 Old Market, West Patel Nagar</PICKUP_ADDRESS_LINE1><PICKUP_ADDRESS_LINE2>20/3 Old Market, West Patel Nagar</PICKUP_ADDRESS_LINE2><PICKUP_PINCODE>110008</PICKUP_PINCODE><PICKUP_PHONE>9764565877</PICKUP_PHONE><PICKUP_MOBILE>9764565877</PICKUP_MOBILE></SHIPMENT></ECOMEXPRESS-OBJECTS>'
    root = xml_tree.getroot()
    for child in root:
        print child.tag, child.attrib
	stats=child.findall('ShipmentStatus')
	for stat in stats:
	    for elem in list(stat):
		for x in elem.iter():
		    print x.tag, x.text
    # pass 
    

ERR = {'VALIDITY':'INVALID',
	'VALUE': 'CHECK_VALUE_OF',
	'SERVICE': 'NOT_SERVICED',
	'FORMAT': 'NOT_IN_SPECIFIED_FORMAT',
	'MATCH': 'MATCH_NOT_FOUND',
	'CLASH': 'ALREADY_EXISTS',
	'2': 'CONSIGNEE',
	'3': 'DESTINATION',
	'4': 'RETURN'}


def validate_awb(single_awb_details):
    '''Feed each awb details as a list like:
       [customer_id, AWB_Number, Pincode, Pickup Pincode, Return Pincode, actual_weight, Product type, Collectible value]
    '''
    reasons, destination_pin = '',''
    # cleaned_awb_details = single_awb_details

    if len(single_awb_details) == 8:
	# capi_id = single_awb_details[0]
        product_type = None 
        # pin_serviced = 0
    # cleaned_awb_details = single_awb_details
        for i in single_awb_details:
	    # cleaned_awb_details[awb_details.index(i)] = validate_data(awb_details.index(i), i)
	    field, val_reasons, product_type =  validate_data(single_awb_details.index(i), i, product_type)
	    # cleaned_awb_details[i] = v
	    if val_reasons:
	        reasons+=val_reasons+',' 
	    else:
	        pass
    else:
	reasons = 'INCORRECT_NUMBER_OF_PARAMETERS_PASSED_TO_VALIDATE'
    # return reasons # cleaned_awb_details
    import json
    if not reasons:
	return json.dumps({'SUCCESS':True}, indent=4, separators=(',', ': '))
    else:
	return json.dumps({'SUCCESS':False, 'RESPONSE_MESSAGE':reasons}, indent=4, sort_keys=False, separators=(',', ': '))

	
def validate_data(field, value, product_t):
    ''' each value passed as a number and a value
    '''
    field = int(field)
    try:
        value = value.strip()
    except:
        value = value
    reasons = ''      
    # capi = api_auth
    product_type=product_t

    if field == 1:	# 6 AWB_NUMBER
	if not int(value) or len(value)<9:
	    reasons+=('AIRWAYBILL_NUMBER_' + ERR['FORMAT'])
	else:
	    try:
		awb_exists = Shipment.objects.get(airwaybill_number=int(value))
		# print 'awb_exists: ', awb_exists
	    	if awb_exists:
		    reasons+=('AIRWAYBILL_NUMBER_' + ERR['CLASH'])
	    	else:
	            try:
	                from airwaybill.models import AirwaybillCustomer
	                awbc = AirwaybillCustomer.objects.get(id = int(capi_id))
		        awb_matched = awbc.airwaybill_number.filter(airwaybill_number=int(value))[0]
		        # return field, value
	            except:
		        reasons+=(ERR['VALUE'] + '_AIRWAYBILL_NUMBER')
		        # return field, (ERR['VALUE'] + ' airwaybill number')
	    except:
	        # reasons+=('AIRWAYBILL_NUMBER_' + ERR['MATCH'])
		pass
		
    if field in (2, 3, 4):	# 25, 27, PINCODE
        # print len(value)
	if value:
	    field = str(field)
	    try:
	        int(value)
	        from service_centre.models import Pincode
	        # swp = Shipment.objects.filter(airwaybill_number=int(value))
	        # inward_pin = swp[0]
	        try:
		    pin_serviced = Pincode.objects.get(pincode=value, status=1)
		    destination_pin = value
		    # return field, value
	        except:
		    reasons+=(ERR[field]+'_PINCODE_'+ERR['SERVICE'])
	    except:
	        reasons+=(ERR[field]+ERR['_VALIDITY']+'_PINCODE_FORMAT')
	else:
	    reasons+=(ERR[field]+ERR['_VALIDITY']+ '_PINCODE_FORMAT')
	    # return field, ERR['VALIDITY']

    if field == 8:	# MOBILE
	if len(value) is not 10:
	    reasons+=('MOBILE_NUMBER_'+ERR['VALIDITY'])

    if field == 6:	#PRODUCT
	# print value.lower()
	if not value.lower() in ('ppd', 'cod', 'rts', 'rto', 'ebsppd', 'ebscod', 'ebs ppd', 'ebs cod', 'ebs-ppd', 'ebs-cod'):
	    reasons+=(ERR['VALIDITY']+'_PRODUCT_TYPE')
	elif value.lower() == 'cod':
	    # global product_typ
	    product_type = 6

    if field == 7:	# COLLECTABLE VALUE, ONLY FOR COD SHIPMENTS
	if product_type == 6:
	    try:
		1/float(value)
	    except:
		reasons+=(ERR['VALIDITY'] + '_COLLECTABLE_VALUE')

    if field == 5:	# ACTUAL_WEIGHT
	try:
	    1/float(value)
	    # return field, format(float(value), '.2f')
	except:
	    reasons+=(ERR['VALIDITY'] + '_VALUE_FOR_WEIGHT')

    # print field, reasons
    return field, reasons, product_type


if __name__=='__main__':
    # read_shipment_status()
    # inputs = sys.argv[1], sys.argv[2]
    inputs = [['xx0011','103086871','110003','400071','400002','1.6','ppd','i2.9'],['xx0011',' 705166472','110011','743302','110023','1','cOD','a2.9'],['xx0011',' 705166472','110011','400071','743302','0','cOD','2.9']]

    print inputs
    for i in inputs:
	# print len(i)
	print validate_awb(i)
    # print validate_data(inputs[0], inputs[1])
