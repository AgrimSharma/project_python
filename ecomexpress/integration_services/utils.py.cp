import os
import sys
import json
import math
import urllib
import urllib2

PROJECT_ROOT_DIR = '/home/web/ecomm.prtouch.com/ecomexpress/'
os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from customer.models import Shipper, ShipperMapping, Customer
from location.models import Pincode, Address, ServiceCenter
from integration_services.models import Add_Coords
from service_centre.models import Shipment

def get_shipment_address(awb):
    ship = Shipment.objects.get(airwaybill_number=awb)
    address1, address2, address3, address4, state, city = '', '', '', '', '', ''
    if ship.consignee_address1:
        address1 = ship.consignee_address1 
    if ship.consignee_address2:
        address2 = ship.consignee_address2 
    if ship.consignee_address3:
        address3 = ship.consignee_address3 
    if ship.consignee_address4:
        address4 = ship.consignee_address4 
    if ship.destination_city: 
        city = ship.destination_city 
    if ship.state: 
        state = ship.state

    #ship_addr = [address1, address2, address3, address4, city, state]
    ship_addr = address2+address3+','+address4+','+city
    print "Ship addr: ", ship_addr

    return ship_addr


def get_or_create_vendor(*args, **kwargs):
    pincode = kwargs.get('pincode')
    address = kwargs.get('address')
    name = kwargs.get('name')
    customer = kwargs.get('customer')
    phone = ""
    if kwargs.get('phone'):
        phone = kwargs.get('phone')

    try:
        shipper = Shipper.objects.get(
            name=name, customer=customer, address__pincode=pincode)
        return shipper
    except Shipper.DoesNotExist:
        pass

    pin = Pincode.objects.get(pincode=pincode)
    address1 = address[:100]
    address2 = address[100:200]
    address3 = address[200:300]
    address4 = address[300:400]

    address  =  Address.objects.create(
        city=pin.service_center.city, state=pin.service_center.city.state,
        address1=address1, address2=address2, address3=address3, 
        address4=address4, pincode=pincode, phone = phone)

    shipper = Shipper.objects.create(
        name=name, customer=customer, address=address)
    ShipperMapping.objects.create(
       shipper=shipper, forward_pincode=pincode, return_pincode=0)
    return shipper


def find_coords(address):
    """
    This function extracts coordinates from the json response
    given the address.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json?" 
    data = {'address':address,
	    'components':'country:IN'}
    encode_args = urllib.urlencode(data)
    url = url+encode_args
    # print 'url', url
    coords = None
    req = urllib2.Request(url)
    response = None
    jsonenco = None
    try:
        response = urllib2.urlopen(req)
        if response:
	    jsonenco = response.read()
        else:
	    return -1
    except urllib2.HTTPError as e:
	from time import sleep
	sleep(1.3)
	response = urllib2.urlopen(req)
    
    loc_json = json.loads(jsonenco)
    # print "loc_json: %s" %(loc_json)
    if loc_json['results']:
        coords = loc_json['results'][0]['geometry']['location']
    # print "coords: %s" %type(coords)
        if coords == None:
            #print "no single coords found"
            coords={}
            coordsa = loc_json['results'][0]['geometry']['bounds']['northeast']
            coordsb = loc_json['results'][0]['geometry']['bounds']['southwest']
            if coordsa['lat']>coordsb['lat']:
                coordslat = ((coordsa['lat']-coordsb['lat'])/2)+coordsb['lat']
                coordslng = ((coordsb['lng']-coordsb['lng'])/2)+coordsb['lng']
                coords = {'lat':coordslat, 'lng':coordslng}
            else:
                coords = loc_json['results'][0]['geometry']['bounds']['northeast']
    else:
	coords = {'lat':0.00, 'lng':0.00}
    # print "coords: %s" %(coords)
    return (coords['lat'], coords['lng'])


def distance_on_unit_sphere(lat1, long1, lat2, long2):
 
    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
 
    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
     
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
 
    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc

def find_distance(coords1, coords2):
    """
    Find the rough distance in kilometres between
    coords1 and coords2 using the formula:
    """
    try:
        lat1, long1 = coords1
        lat2, long2 = coords2

        # Calculate difference between two sets of lats and longs. Multiply 
        # by 6373 for distance in kilometres.
        distance = 6373*distance_on_unit_sphere(lat1, long1, lat2, long2)
    except TypeError, e:
        distance = -1

    return distance

def format_address(address_string):
    """
    Format the address to create an allowable string
    to feed to Google url.
    """
    stop_list = '!@#$%*&><?/'  #string within single
                                #quotes.
    #address = '+'.join(address_string.split(" "))
    address = address_string
    # print '---------', address
    address = address.encode('ascii', 'ignore')
    address = address.decode('utf-8')
    for stop_char in address:
        if stop_char in stop_list:
            address = ''.join(address.split(stop_char))

    # print "Formatted address: %s" %address

    return address

def feed_addresses(address1, address2):
    """
    Entry point for testing purposes.
    """
    address1 = format_address(address1)
    address2 = format_address(address2)
    coords1 = find_coords(address1)
    coords2 = find_coords(address2)
    distance = find_distance(coords1, coords2)

    print "="*50
    print
    print "Linear distance between %s and %s is %f kilometres" %(address1,
            address2, distance)
    print
    print "="*50
    return distance

def nearest_dc(cons_add):
    dc_addresses = Add_Coords.objects.all()
      # find the lat, lng for cons_add
    f_cons_add = format_address(cons_add)
    coords1 = find_coords(f_cons_add)
    # print coords1
    # print
    result_dict = {}
    for dc_address in dc_addresses:
        if not dc_address.lat or not dc_address.lng:
            continue
	# print dc_address, '   ', dc_address.lng
 	coords2 = (dc_address.lat, dc_address.lng)
          # find dist from cons_add lat, lng to dc_address lat, lng
        # print coords2
 	dist = find_distance(coords1, coords2)
         
        if dist > 0:
            result_dict[dist] = dc_address.dc_id
    if result_dict:
        return result_dict.get(min(result_dict.keys()))
    return None


def update_dc_lat_lng():
    '''
    with open xlsx file:
        read every row,
        state, location, code, address, type, city, region
        model is:
        state, location, code, address, type, lat, lng
        for address in xlsx, find coords
        add lat, lng to model.
        for each cons_add, iterate through dc model using lat lng, not address.
    '''
    import openpyxl as px

    W = px.load_workbook('Ecom_Premises Address.xlsx', use_iterators = True)
    p = W.get_sheet_by_name(name = 'new')
    f = open('/tmp/coords.txt', 'w')	#log file.
    a=[]

    for row in p.iter_rows():
	b=[]
	# a.append(cell.row)
        for cell in row:
            b.append(cell.value)
	a.append(b)

    # print "a", a
    # return None
    add_coords = []
    error_list = []
    for x in a[6:]:
	addr = ' '.join(x[4].split('\n'))
	addr=format_address(addr)
	# addr = addr[0].encode('utf-8')
	# print addr
	if x[3]:
	    dc=x[3].encode('utf-8')
	    print "This is ", dc
	else:
	    dc=None
        dc = process_slashes(dc)
	# print "Processed DC ", dc
	# if dc:
	    # pass
	# print str(addr), type(addr), dc
 	from time import sleep
 	sleep(1.3)
     	try:
 	    lat, lng = find_coords(addr)
            # print lat, lng
 	    add_coords.append([x[2].encode('utf-8'), dc, lat, lng, addr])
# 	    print add_coords
 	except:
 	    error_list.append([x[2], x[3]])
    f.write(', '.join(str(add_coords)))
    f.write('\n')
    f.write('='*10)
    f.write('Error list follows\n')
    f.write('='*10)
    f.write(', '.join(str(error_list)))
    f.close()

    created_coords = None
    for coord in add_coords:
	lat=coord[2]
	lng=coord[3]
	dc=coord[1]  # ServiceCenter.objects.get(coord[1])
	address=coord[4]
	try:
	    created_coords = Add_Coords.objects.get(dc=dc)    
	    created_coords = Add_Coords.objects.filter(dc=dc).update(lat=lat, lng=lng, address=address)
	    print 'Record found, updated.'
	except Add_Coords.DoesNotExist:
            if dc:
	        created_coords = Add_Coords.objects.create(lat=lat, lng=lng, dc=dc, address=address)
	        print 'Record created with: ', lat, lng, dc
            else:
                print lng, lat, address
   
    return created_coords

def process_slashes(entry):
    if entry:
	x=entry.split('/')
        for i in x:
	    dc = ServiceCenter.objects.filter(center_shortcode=i, type=0)
	    if dc:
	        return dc[0]
	    else:
		return None
    else:
	return ServiceCenter.objects.filter(center_shortcode='his', type=0)[0]


if __name__ == "__main__":
    #print update_dc_lat_lng()
    #print process_slashes(None)
    print nearest_dc('Udyog Vihar,Phase-1,16, BLE, Gurgaon')
