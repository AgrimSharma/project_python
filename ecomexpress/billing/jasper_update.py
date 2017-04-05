import os
import sys
import datetime

import math
import datetime

from django.db.models import Q
from reports.report_api import CSVReportGenerator
from service_centre.models import Shipment, Order_price, CODCharge, ShipmentExtension
from billing.special_billing import update_awbs_product_type
from billing.models import Billing
from location.models import City, Zone, ZoneLabel
from customer.models import Customer

from billing.charge_calculations import price_updated
import logging

#logging.basicConfig(format='%(asctime)s:  %(message)s',
    #filename='/home/web/ecomm.prtouch.com/ecomexpress/jasper_compare.log',
    #level=logging.DEBUG, filemode='w', datefmt='%Y:%m:%d %I:%M:%S %p')


# use if shipments per day is >= 11500
charge_dict = {
    'intra_city':{'name':'Intra-city', 1:25, 2:15},
    'zones':{'name':'Within Zones', 1:30, 2:20},
    'metro':{'name':'Metro Cities', 1:36, 2:25},
    'east':{'name':'East', 1:38, 2:32},
    'rest':{'name':'Rest of India', 1:36, 2:30},
    'jammu':{'name':'Jammu & Kashmir', 1:40, 2:40},
    'kerala':{'name':'Kerala', 1:40, 2:40},
    'rev_ncr':{'name': 'REV NCR', 1:40, 2:40},
    'rev_all':{'name': 'REV ALL', 1:50, 2:50},
    'delhi':{'name': 'Metro Cities'},
}

charge_dict_regular_pre_jan_2015 = {
    'intra_city':{'name':'Intra-city', 1:25, 2:15},
    'zones':{'name':'Within Zones', 1:30, 2:20},
    'metro':{'name':'Metro Cities', 1:36, 2:25},
    'east':{'name':'East', 1:38, 2:32},
    'rest':{'name':'Rest of India', 1:36, 2:30},
    'jammu':{'name':'Jammu & Kashmir', 1:40, 2:40},
    'kerala':{'name':'Kerala', 1:40, 2:40},
    'north_east':{'name':'North East', 1:43, 2:37},
    'rev_ncr':{'name': 'REV NCR', 1:40, 2:40},
    'rev_all':{'name': 'REV ALL', 1:50, 2:50},
    'delhi':{'name': 'Metro Cities'},
}

charge_dict_upcountry_pre_jan_2015 = {
    'intra_city':{'name':'Intra-city (UP)', 1:25, 2:15},
    'zones':{'name':'Within Zones (UP)', 1:35, 2:25},
    'metro':{'name':'Metro Cities (UP)', 1:41, 2:30},
    'east':{'name':'East (UP)', 1:43, 2:37},
    'rest':{'name':'Rest of India (UP)', 1:41, 2:35},
    'jammu':{'name':'Jammu & Kashmir (UP)', 1:45, 2:45},
    'kerala':{'name':'Kerala (UP)', 1:45, 2:45},
    'north_east':{'name':'North East (UP)', 1:48, 2:42},
    'rev_ncr':{'name': 'REV NCR (UP)', 1:40, 2:40},
    'rev_all':{'name': 'REV ALL (UP)', 1:50, 2:50},
    'delhi':{'name': 'Metro Cities (UP)'},
}

# use if shipments per day is >= 11500
charge_dict_regular_pre_march1 = {
    'intra_city':{'name':'Intra-city', 1:25, 2:15},
    'zones':{'name':'Within Zones', 1:33, 2:22},
    'metro':{'name':'Metro Cities', 1:39, 2:27},
    'east':{'name':'East', 1:41, 2:34},
    'rest':{'name':'Rest of India', 1:39, 2:32},
    'jammu':{'name':'Jammu & Kashmir', 1:40, 2:40},
    'kerala':{'name':'Kerala', 1:40, 2:40},
    'north_east':{'name':'North East', 1:46, 2:39},
    'rev_ncr':{'name': 'REV NCR', 1:40, 2:40},
    'rev_all':{'name': 'REV ALL', 1:50, 2:50},
    'delhi':{'name': 'Metro Cities'},
}

charge_dict_upcountry_pre_march1 = {
    'intra_city':{'name':'Intra-city (UP)', 1:25, 2:15},
    'zones':{'name':'Within Zones (UP)', 1:38, 2:27},
    'metro':{'name':'Metro Cities (UP)', 1:44, 2:32},
    'east':{'name':'East (UP)', 1:46, 2:39},
    'rest':{'name':'Rest of India (UP)', 1:44, 2:37},
    'jammu':{'name':'Jammu & Kashmir (UP)', 1:48, 2:47},
    'kerala':{'name':'Kerala (UP)', 1:48, 2:47},
    'north_east':{'name':'North East (UP)', 1:51, 2:44},
    'rev_ncr':{'name': 'REV NCR (UP)', 1:40, 2:40},
    'rev_all':{'name': 'REV ALL (UP)', 1:50, 2:50},
    'delhi':{'name': 'Metro Cities (UP)'},
}

charge_dict_regular = {
    'intra_city':{'name':'Intra-city', 1:25, 2:15},
    'zones':{'name':'Within Zones', 1:31.50, 2:21},
    'metro':{'name':'Metro Cities', 1:37.50, 2:26},
    'east':{'name':'East', 1:39.50, 2:33},
    'rest':{'name':'Rest of India', 1:37.50, 2:31},
    'jammu':{'name':'Jammu & Kashmir', 1:40, 2:40},
    'kerala':{'name':'Kerala', 1:40, 2:40},
    'north_east':{'name':'North East', 1:44.50, 2:38},
    'rev_ncr':{'name': 'REV NCR', 1:40, 2:40},
    'rev_all':{'name': 'REV ALL', 1:50, 2:50},
    'delhi':{'name': 'Metro Cities'},
}

charge_dict_upcountry = {
    'intra_city':{'name':'Intra-city (UP)', 1:25, 2:15},
    'zones':{'name':'Within Zones (UP)', 1:36.50, 2:26},
    'metro':{'name':'Metro Cities (UP)', 1:42.50, 2:31},
    'east':{'name':'East (UP)', 1:44.50, 2:38},
    'rest':{'name':'Rest of India (UP)', 1:42.50, 2:36},
    'jammu':{'name':'Jammu & Kashmir (UP)', 1:46.50, 2:46},
    'kerala':{'name':'Kerala (UP)', 1:46.50, 2:46},
    'north_east':{'name':'North East (UP)', 1:49.50, 2:43},
    'rev_ncr':{'name': 'REV NCR (UP)', 1:40, 2:40},
    'rev_all':{'name': 'REV ALL (UP)', 1:50, 2:50},
    'delhi':{'name': 'Metro Cities (UP)'},
}

header_row = (
    'Forward Waybill number', 'RTO Waybill number', 'Sub-order / Refrence number',
    'Order date', 'Origin City', 'Destination City', 'Payment Mode', 'TYPE',
    'Origin Zone', 'Zone/Lanes (Destination)', '1 st slab rate/500gm',
    'Next slab rate/500gm', 'Product bill value', 'COD Amount', 'Amount collected',
    'Delivery status', 'Dead Weight (gms)', 'Length', 'Breadth', 'Height',
    'VOL WT IN GMS', 'Billed WT Type', 'Billed Wt (gms)', 'FORWARD FRT Charges',
    'FSC Charges', 'RTO Charges', 'COD Charges', 'Sdl Charge',
    'Sdd Charge', 'Valuable cargo handling Charge', 'To_pay Charge',
    'Reverse Charge', 'Net Amount', 'S tax', 'Education secondary tax',
    'Cess higher secondary tax', 'Grand Total')

METRO_CITIES = ['MUMBAI', 'BENGALURU', 'DELHI', 'AHMEDABAD', 'KOLKATA', 'PUNE', 'HYDERABAD', 'CHENNAI']
NCR_CITIES = ['DELHI', 'FARIDABAD', 'GHAZIABAD', 'GREATER NOIDA', 'GURGAON', 'NOIDA']
KASHMIR_CITIES =  ['JAMMU', 'SRINAGAR', 'BARAMULLA', 'SOPORE',
    'ANANTNAG', 'ACAHBAL', 'BIJBIHARA', 'DAILGAM ', 'MATTAN ', 'GANDERBAL', 'BUDGAM', 'KULGAM']

upcountry_cities = list(
    City.objects.filter(
        labeled_zones__label_id=1, labeled_zones__location_type=1
    ).values_list('city_name', flat=True))
UPCOUNTRY_CITIES  = [s.upper() for s in upcountry_cities]

# set city location type dict
cities = City.objects.all()
city_location = {}
#city_upcountry = {}

for city in cities:
    city_name = city.city_name.upper()
    if city.labeled_zones.filter(location_type=1).exists():
        city_location[city_name] = 1
    else:
        city_location[city_name] = 0

frt_sum = 0
rto_sum = 0
rev_sum = 0
cod_sum = 0
chg_sum = 0

# Zone Dictionary:
# city_zone_dict = { 'PAT': 'EST', 'SIV': 'STU', 'CCU': 'CCU'}
zl = ZoneLabel.objects.get(id=1)
zones = Zone.objects.filter(label=zl)
city_zone_dict = {}
for zone in zones:
    cities = zone.label_city.all()
    for city in cities:
        city_zone_dict[city.city_shortcode.upper()] = zone.zone_shortcode.upper()


customer = Customer.objects.get(id=6)
vchc_min = customer.vchc_min
vchc_rate = customer.vchc_rate
vchc_min_amnt_applied = customer.vchc_min_amnt_applied

def get_vchc_charge(declared_value, collectable_value, actual_weight):
    if not declared_value:
        declared_value = collectable_value

    if actual_weight:
        val_weight_ratio = declared_value/actual_weight
    else:
        val_weight_ratio = 0

    if val_weight_ratio >= vchc_min_amnt_applied:
        vchc_charges = float(val_weight_ratio - vchc_min_amnt_applied) * float(actual_weight) * float(vchc_rate/100)
        if vchc_charges < vchc_min:
            vchc_charges = vchc_min
    else:
        vchc_charges = 0
    return vchc_charges

def get_sum(*args, **kwargs):
    items = [val if val else 0 for val in args]
    return sum(items)

def get_freight_charge(chargeable_weight, first_slab, second_slab):
    second_wt = math.ceil(((chargeable_weight * 1000) - 500) / 500)
    if second_wt > 0:
        return ( second_wt * second_slab ) + first_slab
    else:
        return first_slab

def get_shipment_type(rts_status, reverse_pickup):
    if rts_status == 1:
        ship_type = 'RTO'
    elif reverse_pickup:
        ship_type = 'REVERSE'
    else:
        ship_type ='FRWRD'
    return ship_type

def get_cod_charge(*args, **kwargs):
    airwaybill_number = kwargs.get('airwaybill_number')
    collectable_value = kwargs.get('collectable_value')
    payment_mode = kwargs.get('payment_mode').lower()
    rts_status = kwargs.get('rts_status')
    rate = kwargs.get('rate')

    if rts_status == 1:
        if payment_mode == 'cod':
            ref_awb = Shipment.objects.get(airwaybill_number=airwaybill_number).ref_airwaybill_number
            try:
                cod_charge = CODCharge.objects.get(shipment__airwaybill_number=ref_awb).cod_charge
            except CODCharge.DoesNotExist:
                cod_charge = collectable_value * (rate/100)
        else:
            cod_charge = 0
    elif payment_mode == 'cod':
        cod_charge = collectable_value * (rate/100)
    else:
        cod_charge = 0

    if rts_status == 1:
        cod_charge = 0 - cod_charge
    return round(cod_charge, 2)

def get_charge_for_city(origin_city, destination_city):
    if origin_city in UPCOUNTRY_CITIES and destination_city in UPCOUNTRY_CITIES:
        return charge_dict_upcountry
    else:
        return charge_dict_regular

def get_charge_for_zone(origin_zone_location_type, destination_zone_location_type):
    if origin_zone_location_type == destination_zone_location_type == 1:
        return charge_dict_upcountry
    else:
        return charge_dict_regular

#@profile
def get_charge(*args, **kwargs):
    """
    Return proper charge_dict for the given 
    origin city / zone, destination city / zone 
    """
    reverse_pickup = kwargs.get('reverse_pickup')
    rts_status = kwargs.get('rts_status')
    origin_zone = kwargs.get('origin_zone')
    destination_zone = kwargs.get('destination_zone')
    origin_city = kwargs.get('origin_city').upper()
    destination_city = kwargs.get('destination_city').upper()

    origin_zone_location_type = city_location.get(origin_city)
    destination_zone_location_type = city_location.get(destination_city)

    # reverse pickups
    if reverse_pickup and rts_status != 1:
        #logging.info('reverse pickups')
        if origin_zone == destination_zone == 'DEL':
            if origin_zone_location_type == destination_zone_location_type == 1:
                charges = charge_dict_upcountry.get('rev_ncr')
            else:
                charges = charge_dict_regular.get('rev_ncr')
        else:
            charges = charge_dict_regular.get('rev_all')
    # intra city
    elif origin_city == destination_city:
        #logging.info('intra city')
        if origin_city in UPCOUNTRY_CITIES:
            charges = charge_dict_upcountry.get('intra_city')
        else:
            charges = charge_dict_regular.get('intra_city')
    # Intra zone - Delhi
    elif origin_zone == destination_zone == 'DEL':
        #logging.info('intra zone delhi')
        if origin_zone_location_type == destination_zone_location_type == 1:
            charges = charge_dict_upcountry.get('intra_city')
        else:
            charges = charge_dict_regular.get('intra_city')
    # other intra zone
    elif origin_zone == destination_zone:
        #logging.info('intra zone other')
        if origin_zone_location_type == destination_zone_location_type == 1:
            charges = charge_dict_upcountry.get('zones')
        else:
            charges = charge_dict_regular.get('zones')
    # kashmir origin and destination
    elif origin_city in KASHMIR_CITIES and destination_city in KASHMIR_CITIES:
        #logging.info('origin and dest city kashmir')
        if origin_city in UPCOUNTRY_CITIES and destination_city in UPCOUNTRY_CITIES:
            charges = charge_dict_upcountry.get('zones')
        else:
            charges = charge_dict_regular.get('zones')
    # origin and destination zones diffrent but destination city in Kashmir
    elif (origin_zone != destination_zone) and  \
            (destination_city in KASHMIR_CITIES) or (origin_city in KASHMIR_CITIES):
        #logging.info('origin and destination zones diffrent but one city in Kashmir')
        if origin_city in UPCOUNTRY_CITIES or destination_city in UPCOUNTRY_CITIES:
            charges = charge_dict_upcountry.get('jammu')
        else:
            charges = charge_dict_regular.get('jammu')
    # origin and destination zones diffrent but destination in metro city
    elif (origin_zone != destination_zone) and  destination_city in METRO_CITIES:
        #logging.info('origin and destination zones diffrent but destination in metro city')
        if origin_city in UPCOUNTRY_CITIES :
            charges = charge_dict_upcountry.get('metro')
        else:
            charges = charge_dict_regular.get('metro')
    # origin and destination zones diffrent but destination zone is delhi
    elif (origin_zone != destination_zone) and destination_zone == 'DEL':
        #logging.info('origin and destination zones diffrent but destination zone is delhi')
        if origin_city in UPCOUNTRY_CITIES :
            charges = charge_dict_upcountry.get('metro')
        else:
            charges = charge_dict_regular.get('metro')
    # origin and destination zones diffrent but destination zone is east
    elif (origin_zone != destination_zone) and  destination_zone == 'EST':
        #logging.info('origin and destination zones diffrent but destination zone is east')
        if  destination_zone_location_type == 1:
            charges = charge_dict_upcountry.get('east')
        else:
            charges = charge_dict_regular.get('east')
    # rest of india
    else:
        #logging.info('rest of india')
        if origin_city in UPCOUNTRY_CITIES or destination_city in UPCOUNTRY_CITIES:
            charges = charge_dict_upcountry.get('rest')
        else:
            charges = charge_dict_regular.get('rest')
    return charges

def get_slab_rates(*args, **kwargs):
    reverse_pickup = kwargs.get('reverse_pickup')
    rts_status = kwargs.get('rts_status')
    origin_zone = kwargs.get('origin_zone') 
    destination_zone = kwargs.get('destination_zone') 
    origin_city = kwargs.get('origin_city').upper()
    destination_city = kwargs.get('destination_city').upper()
    first_slab = kwargs.get('first_slab')
    second_slab = kwargs.get('second_slab')

    intracity = False
    intrazone = False
    restrts = False
    if reverse_pickup and rts_status != 1:
        pass
    elif origin_city == destination_city:
        if rts_status == 1: intracity = True
    elif origin_zone == destination_zone == 'DEL':
        if rts_status == 1: intracity = True
    elif origin_zone == destination_zone:
        if rts_status == 1: intrazone = True
    elif (origin_city in KASHMIR_CITIES) and destination_city in KASHMIR_CITIES:
        if rts_status == 1: intrazone = True
    elif (origin_zone != destination_zone) and destination_city in METRO_CITIES:
        if rts_status == 1: restrts = True
    elif (origin_zone != destination_zone) and destination_zone == 'DEL':
        if rts_status == 1: restrts = True
    elif (origin_zone != destination_zone) and destination_city in KASHMIR_CITIES:
        if rts_status == 1: restrts = True
    elif (origin_zone != destination_zone) and destination_zone == 'EST':
        if rts_status == 1: restrts = True
    else:
        if rts_status == 1: restrts = True

    if intracity:
        first_slab = 0
        second_slab = 0
        #logging.info('intracity - slabs made 0')
    elif intrazone:
        first_slab =  first_slab * 0.5
        second_slab = second_slab * 0.5
        #logging.info('intracity - slabs made 1/2')
    elif restrts:
        first_slab =  22.5
        second_slab = 22.5
        #logging.info('rest rts - slabs made 22.5')

    #logging.info([first_slab, second_slab])
    return (first_slab, second_slab)

#@profile
def get_upcountry_status(*args, **kwargs):
    reverse_pickup = kwargs.get('reverse_pickup')
    rts_status = kwargs.get('rts_status')
    origin_city = kwargs.get('origin_city').upper()
    destination_city = kwargs.get('destination_city').upper()
    origin_zone = kwargs.get('origin_zone').upper()
    destination_zone = kwargs.get('destination_zone').upper()

    origin_zone_location_type = city_location.get(origin_city)
    destination_zone_location_type = city_location.get(destination_city)
    upcountry_status = False
    # ##############################
    if reverse_pickup and rts_status != 1:
        if origin_zone == destination_zone == 'DEL':
            if origin_zone_location_type == destination_zone_location_type == 1:
                upcountry_status = True
            else:
                upcountry_status = False
        else:
            upcountry_status = False
    elif origin_city == destination_city:
        if origin_city in UPCOUNTRY_CITIES and destination_city in UPCOUNTRY_CITIES:
            upcountry_status = True
        else:
            upcountry_status = False
    elif origin_zone == destination_zone == 'DEL':
        if origin_zone_location_type == destination_zone_location_type == 1:
            upcountry_status = True
        else:
            upcountry_status = False
    elif origin_zone == destination_zone:
        if origin_zone_location_type == destination_zone_location_type == 1:
            upcountry_status = True
        else:
            upcountry_status = False
    elif (origin_city in KASHMIR_CITIES) and destination_city in KASHMIR_CITIES:
        if origin_city in UPCOUNTRY_CITIES :
            upcountry_status = True
        else:
            upcountry_status = False
    elif (origin_zone != destination_zone) and  destination_city in METRO_CITIES:
        if origin_city in UPCOUNTRY_CITIES and destination_city in UPCOUNTRY_CITIES:
            upcountry_status = True
        else:
            upcountry_status = False
    elif (origin_zone != destination_zone) and destination_zone == 'DEL':
        if origin_city in UPCOUNTRY_CITIES:
            upcountry_status = True
        else:
            upcountry_status = False
    elif (origin_zone != destination_zone) and  destination_city in KASHMIR_CITIES:
        if origin_city in UPCOUNTRY_CITIES and destination_city in UPCOUNTRY_CITIES:
            upcountry_status = True
        else:
            upcountry_status = False
    elif (origin_zone != destination_zone) and  destination_zone == 'EST':
        if destination_zone_location_type == 1:
            upcountry_status = True
        else:
            upcountry_status = False
    else:
        if origin_city in UPCOUNTRY_CITIES or destination_city in UPCOUNTRY_CITIES:
            upcountry_status = True
        else:
            upcountry_status = False
    return upcountry_status

#@profile
def get_zone_display_names(*args, **kwargs):
    reverse_pickup = kwargs.get('reverse_pickup')
    rts_status = kwargs.get('rts_status')
    origin_city = kwargs.get('origin_city').upper()
    destination_city = kwargs.get('destination_city').upper()
    origin_zone = kwargs.get('origin_zone').upper()
    destination_zone = kwargs.get('destination_zone').upper()

    origin_zone_location_type = city_location.get(origin_city)
    destination_zone_location_type = city_location.get(destination_city)

    if origin_city == destination_city:
        origin_zone = 'intra_city'
        destination_zone = 'intra_city'
    elif origin_zone == destination_zone == 'DEL':
        origin_zone = 'intra_city'
        destination_zone = 'intra_city'
    elif origin_zone == destination_zone:
        origin_zone = 'zones'
        destination_zone = 'zones'
    elif (origin_city in KASHMIR_CITIES) and \
                destination_city in KASHMIR_CITIES:
        origin_zone = 'zones'
        destination_zone = 'zones'
    else:
        if origin_city in METRO_CITIES:
            origin_zone = 'metro'
        elif origin_city in NCR_CITIES:
            origin_zone = 'delhi'
        elif origin_city in KASHMIR_CITIES:
            origin_zone = 'jammu'
        elif origin_zone == 'EST':
            origin_zone = 'east'
        else:
            origin_zone = 'rest'

        if destination_city in METRO_CITIES:
            destination_zone = 'metro'
        elif destination_city in NCR_CITIES:
            destination_zone = 'delhi'
        elif destination_city in KASHMIR_CITIES:
            destination_zone = 'jammu'
        elif destination_zone == 'EST':
            destination_zone = 'east'
        else:
            destination_zone = 'rest'

    if rts_status == 1:
        if destination_zone not in ['intra_city','zones']:
            origin_zone = 'rest'
            destination_zone = 'rest'

    upcountry_status = get_upcountry_status(*args, **kwargs)

    ####################################
    if upcountry_status:
        charge_dict = charge_dict_upcountry
    else:
        charge_dict = charge_dict_regular

    # update origin and destination zones
    origin_zone = charge_dict.get(origin_zone).get('name')
    destination_zone = charge_dict.get(destination_zone).get('name')
    return (origin_zone, destination_zone)

def get_shipment_charges(*args, **kwargs):
    rts_status = kwargs.get('rts_status')
    chargeable_weight = kwargs.get('chargeable_weight')
    first_slab = kwargs.get('first_slab')
    second_slab = kwargs.get('second_slab')
    reverse_pickup = kwargs.get('reverse_pickup')
    sdl_status = kwargs.get('sdl_status')
    destination_city = kwargs.get('destination_city')

    sdl_charge = 0
    freight_charge = 0
    rto_charge = 0
    reverse_charge = 0.0
    if rts_status == 1:
       rto_charge = get_freight_charge(chargeable_weight, first_slab, second_slab)
    else:
        if reverse_pickup:
            reverse_charge = get_freight_charge(chargeable_weight, first_slab, second_slab)
        else:
            freight_charge = get_freight_charge(chargeable_weight, first_slab, second_slab)

    if sdl_status == 1 and destination_city in KASHMIR_CITIES:
        sdl_charge = get_freight_charge(chargeable_weight, 50, 50)
    else:
        sdl_charge = 0
    return {'sdl_charge': 0, 'freight_charge': freight_charge,
            'rto_charge': rto_charge, 'reverse_charge': reverse_charge}


#@profile
def get_row_data(shipment):
    global frt_sum 
    global rto_sum 
    global rev_sum
    global cod_sum
    global chg_sum

    airwaybill_number = shipment.get('airwaybill_number')
    ref_airwaybill_number = shipment.get('ref_airwaybill_number')
    origin_city = shipment.get('pickup__service_centre__city__city_name')
    destination_city = shipment.get('original_dest__city__city_name')
    origin_city_shortcode = shipment.get('pickup__service_centre__city__city_shortcode')
    destination_city_shortcode = shipment.get('original_dest__city__city_shortcode')

    # origin_zone = shipment.get('pickup__service_centre__city__zone__zone_name') #Zone/Lanes
    # destination_zone = shipment.get('original_dest__city__zone__zone_name') #Destination Zone
    origin_zone = city_zone_dict.get(str(origin_city_shortcode))
    destination_zone = city_zone_dict.get(str(destination_city_shortcode))

    origin_zone_location_type = shipment.get('pickup__service_centre__city__zone__location_type') #Zone/Lanes
    destination_zone_location_type = shipment.get('original_dest__city__zone__location_type') #Destination Zone

    collectable_value = shipment.get('collectable_value') #COD Amount, Amount collected
    declared_value = shipment.get('declared_value') #COD Amount, Amount collected

    actual_weight = shipment.get('actual_weight') #Dead Weight (gms)
    chargeable_weight = shipment.get('chargeable_weight') #Billed Wt (gms)

    #if actual_weight <= 3:
        #chargeable_weight = actual_weight

    vol_weight = shipment.get('volumetric_weight') #VOL WT IN GMS
    fuel_surcharge = 0 # fuel surcharge will be 0 for all shipments of jasper
    sdl_status = shipment.get('sdl')
    sdd_charge = shipment.get('order_price__sdd_charge')
    vchc = shipment.get('order_price__valuable_cargo_handling_charge') # get_vchc_charge(declared_value, collectable_value, actual_weight)
    to_pay_charge = shipment.get('order_price__to_pay_charge')
    reverse_pickup = shipment.get('reverse_pickup')

    rts_status = shipment.get('rts_status')
    payment_mode = shipment.get('shipext__product__product_name')

    cod_charge = get_cod_charge(
        airwaybill_number=airwaybill_number,
        collectable_value=collectable_value, payment_mode=payment_mode,
        rts_status=rts_status, rate=1.8)
    #cod_charge = shipment.get('codcharge__cod_charge')

    #if not cod_charge:
         #cod_charge = 0

    #if rts_status == 1:
        #cod_charge = 0 - cod_charge

    ship_type = get_shipment_type(rts_status, reverse_pickup)
    # UPCOUNTRY_CITIES
    # charge calculation
    charges = get_charge(reverse_pickup=reverse_pickup,
            rts_status=rts_status, origin_zone=origin_zone,
            destination_zone=destination_zone, origin_city=origin_city,
            destination_city=destination_city,
            origin_zone_location_type=origin_zone_location_type,
            destination_zone_location_type=destination_zone_location_type)

    # get the slab rates
    first_slab, second_slab = get_slab_rates(
        reverse_pickup=reverse_pickup, rts_status=rts_status,
        origin_zone=origin_zone, destination_zone=destination_zone,
        origin_city=origin_city, destination_city=destination_city,
        first_slab=charges.get(1), second_slab=charges.get(2))

    # get the shipment charges
    ship_charges = get_shipment_charges(
        destination_city=destination_city,
        rts_status=rts_status, chargeable_weight=chargeable_weight,
        first_slab=first_slab, second_slab=second_slab,
        reverse_pickup=reverse_pickup, sdl_status=sdl_status)

    freight_charge = ship_charges.get('freight_charge')
    sdl_charge = ship_charges.get('sdl_charge')
    rto_charge = ship_charges.get('rto_charge')
    reverse_charge = ship_charges.get('reverse_charge')

    # find origin and destination zone
    disp_origin_zone, disp_destination_zone = get_zone_display_names(
        origin_city=origin_city, destination_city=destination_city,
        origin_zone=origin_zone, destination_zone=destination_zone,
        origin_zone_location_type=origin_zone_location_type,
        destination_zone_location_type=destination_zone_location_type,
        rts_status=rts_status, reverse_pickup=reverse_pickup)

    net_amount = get_sum(
        freight_charge, sdl_charge, fuel_surcharge, vchc ,to_pay_charge,
        rto_charge, sdd_charge, reverse_charge, cod_charge)

    service_tax = net_amount * 0.12
    edu_tax =  service_tax * 0.02
    cess =  service_tax * 0.01

    grand_total = get_sum(net_amount, service_tax, edu_tax, cess)

    if rts_status == 1:
        disp_airwaybill_number = ref_airwaybill_number
        disp_ref_airwaybill_number =  airwaybill_number
    else:
        disp_airwaybill_number = airwaybill_number
        disp_ref_airwaybill_number =  ref_airwaybill_number

    frt_sum += freight_charge
    rto_sum += rto_charge
    rev_sum += reverse_charge
    cod_sum += cod_charge
    chg_sum += chargeable_weight
    row_data = (
        disp_airwaybill_number, disp_ref_airwaybill_number,
        shipment.get('order_number'), shipment.get('added_on'),
        origin_city, destination_city,
        payment_mode, ship_type,
        disp_origin_zone, disp_destination_zone,
        first_slab, second_slab,
        shipment.get('declared_value'), collectable_value,
        collectable_value, shipment.get('reason_code__code_description'),
        actual_weight, shipment.get('length'),
        shipment.get('breadth'), shipment.get('height'),
        vol_weight, '',
        chargeable_weight, freight_charge,
        fuel_surcharge, rto_charge,
        cod_charge, sdl_charge,
        sdd_charge, vchc,
        to_pay_charge, reverse_charge,
        net_amount, service_tax,
        edu_tax, cess, grand_total)

    return row_data

#@profile
def generate_report(from_date, to_date, update=False):
    q = Q()
    if to_date:
        q = q & Q(shipment_date__range=(from_date, to_date))
    else:
        q = q & Q(shipment_date=from_date)

    if update:
        awbs = list(Shipment.objects.filter(q, shipper__id=6, shipext__product=None).values_list('airwaybill_number', flat=True))
        if awbs:
            update_awbs_product_type(awbs)

    year_month = datetime.datetime.today().strftime('%Y_%m')

    bill_shipments = Shipment.objects.using('local_ecomm').filter(
        shipper__id=6, shipment_date__range=(from_date, to_date))

    report = CSVReportGenerator('Jasper_{0}.csv'.format(to_date))
    report.write_row(header_row)
    shipments = bill_shipments.values(
        'airwaybill_number', 'ref_airwaybill_number', 'order_number', 'added_on', 'sdl',
        'pickup__service_centre__city__city_name', 'pickup__service_centre__city__zone__zone_name',
        'pickup__service_centre__city__zone__location_type','original_dest__city__zone__location_type',
        'pickup__service_centre__city__city_shortcode', 'original_dest__city__city_shortcode',
        'original_dest__city__city_name', 'original_dest__city__zone__zone_name',
        'shipext__product__product_name', 'rts_status', 'reverse_pickup', 'declared_value',
        'collectable_value', 'actual_weight', 'length', 'breadth', 'height', 'volumetric_weight',
        'chargeable_weight', 'reason_code__code_description', 'order_price__sdd_charge',
        'order_price__valuable_cargo_handling_charge', 'order_price__to_pay_charge', 'codcharge__cod_charge' )

    for shipment in shipments:
        row_data = get_row_data(shipment)
        report.write_row(row_data)

    print 'frt sum:', frt_sum
    print 'rto sum:', rto_sum
    print 'rev sum:', rev_sum
    print 'cod sum:', cod_sum
    print 'chg sum:', chg_sum
    return report.file_name

def update_charges(from_date, to_date=None, compare=True, update=False):
    #logging.info('start charge update')
    q = Q()
    if to_date:
        q = q & Q(shipment_date__range=(from_date, to_date))
    else:
        q = q & Q(shipment_date=from_date)

    awbs = list(Shipment.objects.filter(q, shipper__id=6, shipext__product=None).values_list('airwaybill_number', flat=True))
    if awbs:
        update_awbs_product_type(awbs)

    bill_shipments = Shipment.objects.filter(q, shipper__id=6, billing=None)
    shipments = bill_shipments.values(
        'airwaybill_number', 'sdl',
        'pickup__service_centre__city__city_name',
        'pickup__service_centre__city__city_shortcode',
        'pickup__service_centre__city__zone__zone_name',
        'pickup__service_centre__city__zone__location_type',
        'original_dest__city__city_name',
        'original_dest__city__city_shortcode',
        'original_dest__city__zone__location_type',
        'original_dest__city__zone__zone_name',
        'shipext__product__product_name',
        'rts_status',
        'declared_value',
        'reverse_pickup',
        'collectable_value',
        'chargeable_weight',
        'actual_weight',
        'shipext__product__product_name',
        'order_price__sdd_charge',
        'order_price__valuable_cargo_handling_charge',
        'order_price__to_pay_charge',
        'order_price__freight_charge',
        'order_price__sdl_charge',
        'order_price__rto_charge',
        'order_price__reverse_charge',
        'codcharge__cod_charge')
    counter = 0

    for shipment in shipments:
        airwaybill_number = shipment.get('airwaybill_number')
        reverse_pickup = shipment.get('reverse_pickup')
        rts_status = shipment.get('rts_status')
        sdl_status = shipment.get('sdl')

        chargeable_weight = shipment.get('chargeable_weight')
        actual_weight = shipment.get('actual_weight')
        collectable_value = shipment.get('collectable_value')
        declared_value = shipment.get('declared_value')
        payment_mode = shipment.get('shipext__product__product_name')
        #origin_zone = shipment.get('pickup__service_centre__city__zone__zone_name')
        #destination_zone = shipment.get('original_dest__city__zone__zone_name')

        origin_zone_location_type = shipment.get('pickup__service_centre__city__zone__location_type') #Zone/Lanes
        destination_zone_location_type = shipment.get('original_dest__city__zone__location_type') #Destination Zone

        origin_city = shipment.get('pickup__service_centre__city__city_name')
        destination_city = shipment.get('original_dest__city__city_name')

        origin_city_shortcode = shipment.get('pickup__service_centre__city__city_shortcode')
        destination_city_shortcode = shipment.get('original_dest__city__city_shortcode')

        origin_zone = city_zone_dict.get(str(origin_city_shortcode))
        destination_zone = city_zone_dict.get(str(destination_city_shortcode))

        #if actual_weight <= 3:
            #chargeable_weight = actual_weight

        # DB charges
        db_freight_charge = shipment.get('order_price__freight_charge')
        db_sdl_charge = shipment.get('order_price__sdl_charge')
        db_rto_charge = shipment.get('order_price__rto_charge')
        db_reverse_charge = shipment.get('order_price__reverse_charge')
        db_vchc = shipment.get('order_price__valuable_cargo_handling_charge')
        db_cod_charge = shipment.get('codcharge__cod_charge')

        db_freight_charge = db_freight_charge if db_freight_charge else 0
        db_sdl_charge = db_sdl_charge if db_sdl_charge else 0
        db_rto_charge = db_rto_charge if db_rto_charge else 0
        db_reverse_charge = db_reverse_charge if db_reverse_charge else 0
        db_vchc = db_vchc if db_vchc else 0
        db_cod_charge = db_cod_charge if db_cod_charge else 0

        # get the charge dict based on the inputs
        charges = get_charge(
            reverse_pickup=reverse_pickup,
            rts_status=rts_status, origin_zone=origin_zone,
            destination_zone=destination_zone, origin_city=origin_city,
            destination_city=destination_city,
            origin_zone_location_type=origin_zone_location_type,
            destination_zone_location_type=destination_zone_location_type)

        # get the slab rates
        first_slab, second_slab = get_slab_rates(
            reverse_pickup=reverse_pickup, rts_status=rts_status,
            origin_zone=origin_zone, destination_zone=destination_zone,
            origin_city=origin_city, destination_city=destination_city,
            first_slab=charges.get(1), second_slab=charges.get(2))

        # get the shipment charges
        ship_charges = get_shipment_charges(
            destination_city=destination_city,
            rts_status=rts_status, chargeable_weight=chargeable_weight,
            first_slab=first_slab, second_slab=second_slab,
            reverse_pickup=reverse_pickup, sdl_status=sdl_status)

        freight_charge = ship_charges.get('freight_charge')
        sdl_charge = ship_charges.get('sdl_charge')
        rto_charge = ship_charges.get('rto_charge')
        reverse_charge = ship_charges.get('reverse_charge')
        cod_charge = get_cod_charge(
            airwaybill_number=airwaybill_number,
            collectable_value=collectable_value, payment_mode=payment_mode,
            rts_status=rts_status, rate=1.8)

        vchc = db_vchc
        if not cod_charge:
            cod_charge = 0

        if compare:
            if round(freight_charge, 2) != round(db_freight_charge, 2):
                logging.info('FRT: {0} - {1} - {2}'.format(airwaybill_number, freight_charge, db_freight_charge))
            if round(sdl_charge, 2) != round(db_sdl_charge, 2):
                logging.info('SDL: {0} - {1} - {2}'.format(airwaybill_number, sdl_charge, db_sdl_charge))
            if round(rto_charge, 2) != round(db_rto_charge, 2):
                logging.info('RTO: {0} - {1} - {2}'.format(airwaybill_number, rto_charge, db_rto_charge))
            if round(reverse_charge, 2) != round(db_reverse_charge, 2):
                logging.info('REV: {0} - {1} - {2}'.format(airwaybill_number, reverse_charge, db_reverse_charge))
            if round(vchc, 2) != round(db_vchc, 2):
                logging.info('VCH: {0} - {1} - {2}'.format(airwaybill_number, vchc, db_vchc)) 
            if abs(round(cod_charge, 2)) != abs(round(db_cod_charge, 2)):
                logging.info('COD: {0} - {1} - {2}'.format(airwaybill_number, cod_charge, db_cod_charge))

        if update:
            logging.info(airwaybill_number)
            ship_obj = Shipment.objects.get(airwaybill_number=airwaybill_number)
            try:
                Order_price.objects.get(shipment=ship_obj)
                oup = Order_price.objects.filter(shipment=ship_obj).update(
                    rto_charge=rto_charge, reverse_charge=reverse_charge, fuel_surcharge=0,
                    freight_charge=freight_charge, sdl_charge=0,
                    valuable_cargo_handling_charge=vchc)
            except Order_price.DoesNotExist:
                oup = Order_price.objects.create(
                    shipment=ship_obj, rto_charge=rto_charge,
                    reverse_charge=reverse_charge, fuel_surcharge=0,
                    freight_charge=freight_charge, sdl_charge=0, 
                    valuable_cargo_handling_charge=vchc)

            if payment_mode.lower() == 'cod':
                try:
                    CODCharge.objects.get(shipment=ship_obj)
                    CODCharge.objects.filter(shipment=ship_obj).update(cod_charge=abs(cod_charge))
                except CODCharge.DoesNotExist:
                    CODCharge.objects.create(shipment=ship_obj, cod_charge=abs(cod_charge))

    logging.info('start charge finish')

def airwaybill_details(awbs):
    year_month = datetime.datetime.today().strftime('%Y_%m')
    today = datetime.datetime.today()
    from_date = datetime.date(today.year, today.month, 01).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    bill_shipments = Shipment.objects.filter(airwaybill_number__in=awbs, shipper__id=6)

    shipments = bill_shipments.values(
        'airwaybill_number', 'sdl',
        'added_on',
        'ref_airwaybill_number',
        'order_number',
        'declared_value',
        'length',
        'breadth',
        'height',
        'volumetric_weight',
        'reason_code__code_description',
        'pickup__service_centre__city__city_name',
        'pickup__service_centre__city__city_shortcode',
        'pickup__service_centre__city__zone__zone_name',
        'pickup__service_centre__city__zone__location_type',
        'original_dest__city__city_name',
        'original_dest__city__city_shortcode',
        'original_dest__city__zone__location_type',
        'original_dest__city__zone__zone_name',
        'shipext__product__product_name',
        'rts_status',
        'reverse_pickup',
        'collectable_value',
        'chargeable_weight',
        'actual_weight',
        'shipext__product__product_name',
        'order_price__sdd_charge',
        'order_price__valuable_cargo_handling_charge',
        'order_price__to_pay_charge',
        'order_price__freight_charge',
        'order_price__sdl_charge',
        'order_price__rto_charge',
        'order_price__reverse_charge',
        'codcharge__cod_charge')
    for shipment in shipments:
        row_data = get_row_data(shipment)

def update_reverse_shipments(from_date, to_date, update=False):
    q = Q(shipment_date__range=(from_date, to_date), shipper__id=6, billing=None)
    shipments = Shipment.objects.filter(q, Q(reverse_pickup=True) | Q(rts_status=1)).values(
        'airwaybill_number', 'pickup__service_centre__city__city_name',
        'original_dest__city__city_name', 'rts_status', 'reverse_pickup', 'chargeable_weight',
        'order_price__freight_charge', 'order_price__fuel_surcharge')
    for s in shipments:
        airwaybill_number = shipment.get('airwaybill_number')
        reverse_pickup = shipment.get('reverse_pickup')
        rts_status = shipment.get('rts_status')

        origin_city = shipment.get('pickup__service_centre__city__city_name')
        destination_city = shipment.get('original_dest__city__city_name')

        origin_city_shortcode = shipment.get('pickup__service_centre__city__city_shortcode')
        destination_city_shortcode = shipment.get('original_dest__city__city_shortcode')

        origin_zone = city_zone_dict.get(str(origin_city_shortcode))
        destination_zone = city_zone_dict.get(str(destination_city_shortcode))
        chargeable_weight = shipment.get('chargeable_weight')

        fuel_surcharge = shipment.get('order_price__fuel_surcharge')
        # process if shipment is RTS
        if rts_status == 1:
            # RTS - Intercity = 0
            if (origin_city_shortcode == destination_city_shortcode) or (origin_city in NCR_CITIES and destination_city in NCR_CITIES):
                freight = 0
            # witin zone
            # RTS - Within Zone  = 50% Run -  Price Update and divide both freight and FS/ 2
            elif origin_zone == destination_zone:
                ship = Shipment.objects.get(airwaybill_number=s.get('airwaybill_number'))
                price_updated(ship)
                ship = Shipment.objects.get(airwaybill_number=s.get('airwaybill_number'))
                freight = ship.order_price_set.get().freight_charge / 2
                fuel_surcharge = ship.order_price_set.get().fuel_surcharge / 2
            # RTS - Rest of india = 22.5
            else:
                freight = get_freight_charge(chargeable_weight, 22.5, 22.5)

        # process if shipment is reverse pickup
        elif reverse_pickup == 1:
            # REV - Intercity = 40
            if (origin_city_shortcode == destination_city_shortcode) or (origin_city in NCR_CITIES and destination_city in NCR_CITIES):
                freight = get_freight_charge(chargeable_weight, 40, 40)
            # REV - Rest of india = 50
            else:
                freight = get_freight_charge(chargeable_weight, 50, 50)

        if update:
            ship_obj = Shipment.objects.get(airwaybill_number=airwaybill_number)
            try:
                Order_price.objects.get(shipment=ship_obj)
                Order_price.objects.filter(shipment=ship_obj).update(
                    rto_charge=rto_charge, reverse_charge=reverse_charge, fuel_surcharge=0,
                    freight_charge=freight_charge, sdl_charge=0)
            except Order_price.DoesNotExist:
                Order_price.objects.create(
                    shipment=ship_obj, rto_charge=rto_charge,
                    reverse_charge=reverse_charge, fuel_surcharge=0,
                    freight_charge=freight_charge, sdl_charge=0)

            if payment_mode.lower() == 'cod':
                try:
                    CODCharge.objects.get(shipment=ship_obj)
                    CODCharge.objects.filter(shipment=ship_obj).update(cod_charge=abs(cod_charge))
                except CODCharge.DoesNotExist:
                    CODCharge.objects.create(shipment=ship_obj, cod_charge=abs(cod_charge))

def update_jasper_awb(awb, compare=False, update=True):
    bill_shipment = Shipment.objects.filter(airwaybill_number=awb, shipper__id=6, billing=None)
    if not bill_shipment:
        return False

    q = Q()

    if not bill_shipment[0].shipext.product:
        update_awbs_product_type([awb])
        bill_shipment = Shipment.objects.filter(airwaybill_number=awb, shipper__id=6, billing=None)

    #logging.info(awb)
    shipments = bill_shipment.values(
        'airwaybill_number', 'sdl',
        'pickup__service_centre__city__city_name',
        'pickup__service_centre__city__city_shortcode',
        'pickup__service_centre__city__zone__zone_name',
        'pickup__service_centre__city__zone__location_type',
        'original_dest__city__city_name',
        'original_dest__city__city_shortcode',
        'original_dest__city__zone__location_type',
        'original_dest__city__zone__zone_name',
        'shipext__product__product_name',
        'rts_status',
        'declared_value',
        'reverse_pickup',
        'collectable_value',
        'chargeable_weight',
        'actual_weight',
        'order_price__sdd_charge',
        'order_price__valuable_cargo_handling_charge',
        'order_price__to_pay_charge',
        'order_price__freight_charge',
        'order_price__sdl_charge',
        'order_price__rto_charge',
        'order_price__reverse_charge',
        'codcharge__cod_charge')

    counter = 0

    for shipment in shipments:
        airwaybill_number = shipment.get('airwaybill_number')
        reverse_pickup = shipment.get('reverse_pickup')
        rts_status = shipment.get('rts_status')
        sdl_status = shipment.get('sdl')

        chargeable_weight = shipment.get('chargeable_weight')
        actual_weight = shipment.get('actual_weight')
        collectable_value = shipment.get('collectable_value')
        declared_value = shipment.get('declared_value')
        payment_mode = shipment.get('shipext__product__product_name')
        #origin_zone = shipment.get('pickup__service_centre__city__zone__zone_name')
        #destination_zone = shipment.get('original_dest__city__zone__zone_name')

        origin_zone_location_type = shipment.get('pickup__service_centre__city__zone__location_type') #Zone/Lanes
        destination_zone_location_type = shipment.get('original_dest__city__zone__location_type') #Destination Zone

        origin_city = shipment.get('pickup__service_centre__city__city_name')
        destination_city = shipment.get('original_dest__city__city_name')

        origin_city_shortcode = shipment.get('pickup__service_centre__city__city_shortcode')
        destination_city_shortcode = shipment.get('original_dest__city__city_shortcode')

        origin_zone = city_zone_dict.get(str(origin_city_shortcode))
        destination_zone = city_zone_dict.get(str(destination_city_shortcode))

        #if actual_weight <= 3:
            #chargeable_weight = actual_weight

        # DB charges
        db_freight_charge = shipment.get('order_price__freight_charge')
        db_sdl_charge = shipment.get('order_price__sdl_charge')
        db_rto_charge = shipment.get('order_price__rto_charge')
        db_reverse_charge = shipment.get('order_price__reverse_charge')
        db_cod_charge = shipment.get('codcharge__cod_charge')
        db_vchc = shipment.get('order_price__valuable_cargo_handling_charge')

        db_freight_charge = db_freight_charge if db_freight_charge else 0
        db_sdl_charge = db_sdl_charge if db_sdl_charge else 0
        db_rto_charge = db_rto_charge if db_rto_charge else 0
        db_reverse_charge = db_reverse_charge if db_reverse_charge else 0
        db_cod_charge = db_cod_charge if db_cod_charge else 0
        db_vchc = db_vchc if db_vchc else 0

        #logging.info([
            #origin_zone, destination_zone, origin_city, destination_city,
            #origin_zone_location_type, destination_zone_location_type, 
            #reverse_pickup, rts_status])
        charges = get_charge(reverse_pickup=reverse_pickup,
            rts_status=rts_status, origin_zone=origin_zone,
            destination_zone=destination_zone, origin_city=origin_city,
            destination_city=destination_city,
            origin_zone_location_type=origin_zone_location_type,
            destination_zone_location_type=destination_zone_location_type)

        #logging.info(charges)
        # get the slab rates
        first_slab, second_slab = get_slab_rates(
            reverse_pickup=reverse_pickup, rts_status=rts_status,
            origin_zone=origin_zone, destination_zone=destination_zone,
            origin_city=origin_city, destination_city=destination_city,
            first_slab=charges.get(1), second_slab=charges.get(2))

        # get the shipment charges
        ship_charges = get_shipment_charges(
            destination_city=destination_city,
            rts_status=rts_status, chargeable_weight=chargeable_weight,
            first_slab=first_slab, second_slab=second_slab,
            reverse_pickup=reverse_pickup, sdl_status=sdl_status)

        freight_charge = ship_charges.get('freight_charge')
        sdl_charge = ship_charges.get('sdl_charge')
        rto_charge = ship_charges.get('rto_charge')
        reverse_charge = ship_charges.get('reverse_charge')
        cod_charge = get_cod_charge(
            airwaybill_number=airwaybill_number,
            collectable_value=collectable_value, payment_mode=payment_mode,
            rts_status=rts_status, rate=1.8)
        # cod_charge = shipment.get('codcharge__cod_charge')

        vchc = shipment.get('order_price__valuable_cargo_handling_charge') #get_vchc_charge(declared_value, collectable_value, actual_weight)

        if not cod_charge:
            cod_charge = 0

        #if rts_status == 1:
            #cod_charge = 0 - cod_charge

        if compare:
            if round(freight_charge, 2) != round(db_freight_charge, 2):
                logging.info('FRT: {0} - {1} - {2}'.format(airwaybill_number, freight_charge, db_freight_charge))
            if round(sdl_charge, 2) != round(db_sdl_charge, 2):
                logging.info('SDL: {0} - {1} - {2}'.format(airwaybill_number, sdl_charge, db_sdl_charge))
            if round(rto_charge, 2) != round(db_rto_charge, 2):
                logging.info('RTO: {0} - {1} - {2}'.format(airwaybill_number, rto_charge, db_rto_charge))
            if round(reverse_charge, 2) != round(db_reverse_charge, 2):
                logging.info('REV: {0} - {1} - {2}'.format(airwaybill_number, reverse_charge, db_reverse_charge))
            if round(vchc, 2) != round(db_vchc, 2):
                logging.info('VCH: {0} - {1} - {2}'.format(airwaybill_number, vchc, db_vchc)) 
            if abs(round(cod_charge, 2)) != abs(round(db_cod_charge, 2)):
                logging.info('COD: {0} - {1} - {2}'.format(airwaybill_number, cod_charge, db_cod_charge))

        if update:
            logging.info(awb)
            ship_obj = Shipment.objects.get(airwaybill_number=awb)
            try:
                Order_price.objects.get(shipment=ship_obj)
                Order_price.objects.filter(shipment=ship_obj).update(
                    rto_charge=rto_charge, reverse_charge=reverse_charge, fuel_surcharge=0,
                    freight_charge=freight_charge, sdl_charge=0,
                    valuable_cargo_handling_charge=vchc)
            except Order_price.DoesNotExist:
                Order_price.objects.create(
                    shipment=ship_obj, rto_charge=rto_charge,
                    reverse_charge=reverse_charge, fuel_surcharge=0,
                    freight_charge=freight_charge, sdl_charge=0,
                    valuable_cargo_handling_charge=vchc)

            if payment_mode.lower() == 'cod':
                try:
                    CODCharge.objects.get(shipment=ship_obj)
                    CODCharge.objects.filter(shipment=ship_obj).update(cod_charge=abs(cod_charge))
                except CODCharge.DoesNotExist:
                    CODCharge.objects.create(shipment=ship_obj, cod_charge=abs(cod_charge))

    return True
