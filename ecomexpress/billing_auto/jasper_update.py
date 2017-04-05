import math
import xlrd
import datetime
import calendar
import pdb

from django.db.models import Q
from reports.ecomm_mail import ecomm_send_mail
from reports.report_api import CSVReportGenerator
from service_centre.models import Shipment, Order_price, CODCharge
from billing.models import Billing
from billing.special_billing import update_awbs_product_type


"""
if the shipment.pickup.service_centre.city and original_dest_city is same
apply the rates as per naresh's file. i.e. first 500 gms and second 500 gms

if shipment is from zone ncr to ncr apply city rates as above
if shipment is from different city but zone same then apply within zone rates
if zones are different all India rate.

Now some more exception, if zones are different and  shipment's city and
original dest is within metro city (mumbai, delhi, hyd, ahmedabad, kolkatta, chennai, bangalore), apply metro rates

if any of the region (city is jammu or srinagar) apply j&K rates in the above there is a change. If dest is j&K,
Also, if dest is east, apply east rates

No only if Original Dest is jammu or srinagar. Also zones must be different

city to city :
NCR to NCR : City Rate
Zone to Zone: Within Zone
Zone is different and original_dest.city in (jammu and srinagar): jammu
Zone is different and original_dest.zone in (East): east
Zone is different and original_dest.city in (Metro): metro Rates
Zone is different and original_dest not in (Metro cities): Rest of India

Zone/City           0-500 gms         addl 500gms
-------------------------------------------------------------------
Intra-city          Rs. 25-00         Rs. 20-00
Within Zones        Rs. 30-00         Rs. 25-00
Metro Cities*       Rs. 36-00         Rs. 25-00
East                Rs. 38-00         Rs. 32-00
Rest of India       Rs. 36-00         Rs. 30-00
Jammu & Kashmir     Rs. 40-00         Rs. 40-00
Kerala              Rs. 40-00         Rs. 40-00

Metro cities: *Mumbai, Chennai, Bangalore, Hyderabad, Delhi, Ahmadabad and Pune
East: Patna, Ranchi, Kolkatta, Bhuvneshwar.
Kashmir:  [u'JAMMU', u'SRINAGAR', u'BARAMULLA', u'SOPORE', u'ANANTNAG', u'ACAHBAL', u'BIJBIHARA', u'DAILGAM ', u'MATTAN ', u'GANDERBAL', u'BUDGAM', u'KULGAM']

"""
charge_dict_normal = {
    'intra_city':{'name':'Intra-city', 1:25, 2:20},
    'zones':{'name':'Within Zones', 1:30, 2:25},
    'metro':{'name':'Metro Cities', 1:36, 2:25},
    'east':{'name':'East', 1:38, 2:32},
    'rest':{'name':'Rest of India', 1:36, 2:30},
    'jammu':{'name':'Jammu & Kashmir', 1:40, 2:40},
    'kerala':{'name':'Kerala', 1:40, 2:40},
    'rev_ncr':{'name': 'REV NCR', 1:40, 2:40},
    'rev_all':{'name': 'REV ALL', 1:50, 2:50},
    'delhi':{'name': 'Metro Cities'},
}

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

header_row = ('Forward Waybill number', 'RTO Waybill number', 'Sub-order / Refrence number',
        'Order date', 'Origin City', 'Destination City', 'Payment Mode', 'TYPE',
        'Origin Zone', 'Zone/Lanes (Destination)', '1 st slab rate/500gm',
        'Next slab rate/500gm', 'Product bill value', 'COD Amount', 'Amount collected',
        'Delivery status', 'Dead Weight (gms)', 'Length', 'Breadth', 'Height',
        'VOL WT IN GMS', 'Billed WT Type', 'Billed Wt (gms)', 'FORWARD FRT Charges',
        'FSC Charges', 'RTO Charges', 'COD Charges', 'Sdl Charge',
        'Sdd Charge', 'Valuable cargo handling Charge', 'To_pay Charge',
        'Reverse Charge', 'Net Amount', 'S tax', 'Education secondary tax',
        'Cess higher secondary tax', 'Grand Total')

"""
7 Payment Mode                  - calculate
8 TYPE                          - calculate
9 Origin Zone                   - calculate
10 Zone/Lanes (Destination)     - calculate
11 1 st slab rate/500gm         - calculate
12 Next slab rate/500gm         - calculate
24 FORWARD FRT Charges          - calculate
26 RTO Charges                  - calculate
27 COD Charges                  - calculate
28 Sdl Charge                   - calculate
29 Sdd Charge                   - calculate
30 VCHC                         - calculate
31 To_pay Charge                - calculate
32 Reverse Charge               - calculate
33 Net Amount                   - calculate
34 S tax                        - calculate
35 Education secondary tax      - calculate
36 Cess higher secondary tax    - calculate
37 Grand Total                  - calculate
"""
metro_cities = ['MUMBAI', 'BENGALURU', 'DELHI', 'AHMEDABAD', 'KOLKATA', 'PUNE', 'HYDERABAD', 'CHENNAI']
ncr_cities = ['DELHI', 'FARIDABAD', 'GHAZIABAD', 'GREATER NOIDA', 'GURGAON', 'NOIDA']
KASHMIR_CITIES =  ['JAMMU', 'SRINAGAR', 'BARAMULLA', 'SOPORE',
    'ANANTNAG', 'ACAHBAL', 'BIJBIHARA', 'DAILGAM ', 'MATTAN ', 'GANDERBAL', 'BUDGAM', 'KULGAM']

frt_sum = 0
rto_sum = 0
rev_sum = 0
cod_sum = 0


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
    collectable_value = kwargs.get('collectable_value')
    payment_mode = kwargs.get('payment_mode').lower()
    rts_status = kwargs.get('rts_status')
    rate = kwargs.get('rate')

    if payment_mode == 'cod':
        cod_charge = collectable_value * (rate/100)
    else:
        cod_charge = 0

    if rts_status == 1:
        cod_charge = 0 - cod_charge
    return round(cod_charge, 2)

def get_charge(*args, **kwargs):
    reverse_pickup = kwargs.get('reverse_pickup')
    rts_status = kwargs.get('rts_status')
    origin_zone = kwargs.get('origin_zone').upper()
    destination_zone = kwargs.get('destination_zone').upper()
    origin_city = kwargs.get('origin_city').upper()
    destination_city = kwargs.get('destination_city').upper()

    if reverse_pickup and rts_status != 1:
        if origin_zone == destination_zone == 'DELHI AND SATELLITE CITIES':
            charges = charge_dict.get('rev_ncr')
        else:
            charges = charge_dict.get('rev_all')
    elif origin_city == destination_city:
        charges = charge_dict.get('intra_city')
    elif origin_zone == destination_zone == 'DELHI AND SATELLITE CITIES':
        charges = charge_dict.get('intra_city')
    elif origin_zone == destination_zone:
        charges = charge_dict.get('zones')
    elif (origin_city in KASHMIR_CITIES) and destination_city in KASHMIR_CITIES:
        charges = charge_dict.get('zones')
    elif (origin_zone != destination_zone) and  destination_city in metro_cities:
        charges = charge_dict.get('metro')
    elif (origin_zone != destination_zone) and destination_zone == 'DELHI AND SATELLITE CITIES':
        charges = charge_dict.get('metro')
    elif (origin_zone != destination_zone) and  destination_city in KASHMIR_CITIES:
        charges = charge_dict.get('jammu')
    elif (origin_zone != destination_zone) and  destination_zone == 'EAST':
        charges = charge_dict.get('east')
    else:
        charges = charge_dict.get('rest')
    return charges

def get_slab_rates(*args, **kwargs):
    reverse_pickup = kwargs.get('reverse_pickup')
    rts_status = kwargs.get('rts_status')
    origin_zone = kwargs.get('origin_zone').upper()
    destination_zone = kwargs.get('destination_zone').upper()
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
    elif origin_zone == destination_zone == 'DELHI AND SATELLITE CITIES':
        if rts_status == 1: intracity = True
    elif origin_zone == destination_zone:
        if rts_status == 1: intrazone = True
    elif (origin_city in KASHMIR_CITIES) and destination_city in KASHMIR_CITIES:
        if rts_status == 1: intrazone = True
    elif (origin_zone != destination_zone) and  destination_city in metro_cities:
        if rts_status == 1: restrts = True
    elif (origin_zone != destination_zone) and destination_zone == 'DELHI AND SATELLITE CITIES':
        if rts_status == 1: restrts = True
    elif (origin_zone != destination_zone) and destination_city in KASHMIR_CITIES:
        if rts_status == 1: restrts = True
    elif (origin_zone != destination_zone) and destination_zone == 'EAST':
        if rts_status == 1: restrts = True
    else:
        if rts_status == 1: restrts = True

    if intracity:
        first_slab = 0
        second_slab = 0
    elif intrazone:
        first_slab =  first_slab * 0.5
        second_slab = second_slab * 0.5
    elif restrts:
        first_slab =  22.5
        second_slab = 22.5
    return (first_slab, second_slab)

def get_zone_display_names(*args, **kwargs):
    origin_city = kwargs.get('origin_city').upper()
    destination_city = kwargs.get('destination_city').upper()
    origin_zone = kwargs.get('origin_zone').upper()
    destination_zone = kwargs.get('destination_zone').upper()
    rts_status = kwargs.get('rts_status')
    #print origin_city , destination_city, origin_zone, destination_zone, rts_status

    if origin_city == destination_city:
        origin_zone = 'intra_city'
        destination_zone = 'intra_city'
    elif origin_zone == destination_zone == 'DELHI AND SATELLITE CITIES':
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
        if origin_city in metro_cities:
            origin_zone = 'metro'
        elif origin_city in ncr_cities:
            origin_zone = 'delhi'
        elif origin_city in KASHMIR_CITIES:
            origin_zone = 'jammu'
        elif origin_zone == 'EAST':
            origin_zone = 'east'
        else:
            origin_zone = 'rest'

        if destination_city in metro_cities:
            destination_zone = 'metro'
        elif destination_city in ncr_cities:
            destination_zone = 'delhi'
        elif destination_city in KASHMIR_CITIES:
            destination_zone = 'jammu'
        elif destination_zone == 'EAST':
            destination_zone = 'east'
        else:
            destination_zone = 'rest'

    if rts_status == 1:
        if destination_zone not in ['intra_city','zones']:
            origin_zone = 'rest'
            destination_zone = 'rest'

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
    return {'sdl_charge': sdl_charge, 'freight_charge': freight_charge,
            'rto_charge': rto_charge, 'reverse_charge': reverse_charge}


def get_row_data(shipment):
    airwaybill_number = shipment.get('airwaybill_number')
    ref_airwaybill_number = shipment.get('ref_airwaybill_number')

    origin_city = shipment.get('pickup__service_centre__city__city_name')
    destination_city = shipment.get('original_dest__city__city_name')
    origin_zone = shipment.get('pickup__service_centre__city__zone__zone_name') #Zone/Lanes
    destination_zone = shipment.get('original_dest__city__zone__zone_name') #Destination Zone

    collectable_value = shipment.get('collectable_value') #COD Amount, Amount collected

    actual_weight = shipment.get('actual_weight') #Dead Weight (gms)
    chargeable_weight = shipment.get('chargeable_weight') #Billed Wt (gms)
    if actual_weight <= 3:
        chargeable_weight = actual_weight

    vol_weight = shipment.get('volumetric_weight') #VOL WT IN GMS
    fuel_surcharge = 0 # fuel surcharge will be 0 for all shipments of jasper
    sdl_status = shipment.get('sdl')
    sdd_charge = shipment.get('order_price__sdd_charge')
    vchc = shipment.get('order_price__valuable_cargo_handling_charge')
    to_pay_charge = shipment.get('order_price__to_pay_charge')
    reverse_pickup = shipment.get('reverse_pickup')

    rts_status = shipment.get('rts_status')
    payment_mode = shipment.get('shipext__product__product_name')

    cod_charge = get_cod_charge(
        collectable_value=collectable_value, payment_mode=payment_mode,
        rts_status=rts_status, rate=1.8)
    ship_type = get_shipment_type(rts_status, reverse_pickup)

    # charge calculation
    #print 'orgin city : {0}  destination_city: {1}'.format(origin_city, destination_city)
    #print 'orgin zone : {0}  destination_zone : {1}'.format(origin_zone, destination_zone)

    charges = get_charge(reverse_pickup=reverse_pickup,
            rts_status=rts_status, origin_zone=origin_zone,
            destination_zone=destination_zone, origin_city=origin_city,
            destination_city=destination_city)

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
        rts_status=rts_status)


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

    row_data = (disp_airwaybill_number, disp_ref_airwaybill_number,
            shipment.get('order_number'), shipment.get('added_on'),
            origin_city, destination_city, payment_mode, ship_type,
            disp_origin_zone, disp_destination_zone, first_slab, second_slab,
            shipment.get('declared_value'), collectable_value,
            collectable_value, shipment.get('reason_code__code_description'),
            actual_weight, shipment.get('length'), shipment.get('breadth'),
            shipment.get('height'), vol_weight, '',
            chargeable_weight, freight_charge, fuel_surcharge,
            rto_charge, cod_charge, sdl_charge, sdd_charge, vchc, to_pay_charge,
            reverse_charge, net_amount, service_tax, edu_tax, cess, grand_total)

    return row_data

def generate_report(from_date, to_date):
    year_month = datetime.datetime.today().strftime('%Y_%m')
    bill_shipments = Shipment.objects.filter(
        shipper__id=6, shipment_date__range=(from_date, to_date))

    report = CSVReportGenerator('Jasper_{0}.csv'.format(year_month))
    report.write_row(header_row)
    shipments = bill_shipments.values(
        'airwaybill_number', 'ref_airwaybill_number', 'order_number', 'added_on', 'sdl',
        'pickup__service_centre__city__city_name', 'pickup__service_centre__city__zone__zone_name',
        'original_dest__city__city_name', 'original_dest__city__zone__zone_name',
        'shipext__product__product_name', 'rts_status', 'reverse_pickup', 'declared_value',
        'collectable_value', 'actual_weight', 'length', 'breadth', 'height', 'volumetric_weight',
        'chargeable_weight', 'reason_code__code_description', 'order_price__sdd_charge',
        'order_price__valuable_cargo_handling_charge', 'order_price__to_pay_charge', 'codcharge__cod_charge' )

    for shipment in shipments:
        row_data = get_row_data(shipment)
        report.write_row(row_data)

    return report.file_name

def update_charges(from_date, to_date=None, compare=True, update=False):
    q = Q()
    if to_date:
        q = q & Q(shipment_date__range=(from_date, to_date))
    else:
        q = q & Q(shipment_date=from_date)

    if update:
        awbs = list(Shipment.objects.filter(q, shipper__id=6, shipext__product=None).values_list('airwaybill_number', flat=True))
        awb_count = len(awbs)
        print 'updating {0} product types'.format(awb_count)
        if awb_count:
            update_awbs_product_type(awbs)

    bill_shipments = Shipment.objects.filter(q, shipper__id=6)
    shipments = bill_shipments.values(
        'airwaybill_number', 'sdl',
        'pickup__service_centre__city__city_name',
        'pickup__service_centre__city__zone__zone_name',
        'original_dest__city__city_name',
        'original_dest__city__zone__zone_name',
        'shipext__product__product_name',
        'rts_status',
        'collectable_value',
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
        payment_mode = shipment.get('shipext__product__product_name')
        origin_zone = shipment.get('pickup__service_centre__city__zone__zone_name')
        destination_zone = shipment.get('original_dest__city__zone__zone_name')
        origin_city = shipment.get('pickup__service_centre__city__city_name')
        destination_city = shipment.get('original_dest__city__city_name')
        if actual_weight <= 3:
            chargeable_weight = actual_weight

        # DB charges
        db_freight_charge = shipment.get('order_price__freight_charge')
        db_sdl_charge = shipment.get('order_price__sdl_charge')
        db_rto_charge = shipment.get('order_price__rto_charge')
        db_reverse_charge = shipment.get('order_price__reverse_charge')
        db_cod_charge = shipment.get('codcharge__cod_charge')

        db_freight_charge = db_freight_charge if db_freight_charge else 0
        db_sdl_charge = db_sdl_charge if db_sdl_charge else 0
        db_rto_charge = db_rto_charge if db_rto_charge else 0
        db_reverse_charge = db_reverse_charge if db_reverse_charge else 0
        db_cod_charge = db_cod_charge if db_cod_charge else 0

        charges = get_charge(reverse_pickup=reverse_pickup,
            rts_status=rts_status, origin_zone=origin_zone,
            destination_zone=destination_zone, origin_city=origin_city,
            destination_city=destination_city)

        # get the slab rates
        first_slab, second_slab = get_slab_rates(
            reverse_pickup=reverse_pickup, rts_status=rts_status,
            origin_zone=origin_zone, destination_zone=destination_zone,
            origin_city=origin_city, destination_city=destination_city,
            first_slab=charges.get(1), second_slab=charges.get(2))

        #print first_slab, second_slab
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
            collectable_value=collectable_value, payment_mode=payment_mode,
            rts_status=rts_status, rate=1.8)

        #print 'Frt: ',airwaybill_number, ship_charges, destination_city, sdl_status
        if compare:
            if round(freight_charge, 2) != round(db_freight_charge, 2):
                print 'Frt: ',airwaybill_number, freight_charge, db_freight_charge
            if round(sdl_charge, 2) != round(db_sdl_charge, 2):
                print 'Sdl: ',airwaybill_number, sdl_charge, db_sdl_charge
            if round(rto_charge, 2) != round(db_rto_charge, 2):
                print 'Rto: ',airwaybill_number, rto_charge, db_rto_charge
            if round(reverse_charge, 2) != round(db_reverse_charge, 2):
                print 'Rev: ',airwaybill_number, reverse_charge, db_reverse_charge
            if abs(round(cod_charge, 2)) != abs(round(db_cod_charge, 2)):
                print 'Cod: ',airwaybill_number, cod_charge, db_cod_charge
        #print freight_charge, sdl_charge, reverse_charge, rto_charge
        if update:
            oup = Order_price.objects.filter(shipment__airwaybill_number=airwaybill_number).update(
                rto_charge=rto_charge, reverse_charge=reverse_charge, fuel_surcharge=0,
                freight_charge=freight_charge, sdl_charge=sdl_charge)
            counter += 1
            print counter

def airwaybill_details(awbs):
    year_month = datetime.datetime.today().strftime('%Y_%m')
    today = datetime.datetime.today()
    from_date = datetime.date(today.year, today.month, 01).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    bill_shipments = Shipment.objects.filter(airwaybill_number__in=awbs, shipper__id=6, shipment_date__range=(from_date, to_date))

    shipments = bill_shipments.values(
        'airwaybill_number', 'ref_airwaybill_number', 'order_number', 'added_on', 'sdl',
        'pickup__service_centre__city__city_name', 'pickup__service_centre__city__zone__zone_name',
        'original_dest__city__city_name', 'original_dest__city__zone__zone_name',
        'shipext__product__product_name', 'rts_status', 'reverse_pickup', 'declared_value',
        'collectable_value', 'actual_weight', 'length', 'breadth', 'height', 'volumetric_weight',
        'chargeable_weight', 'reason_code__code_description', 'order_price__sdd_charge',
        'order_price__valuable_cargo_handling_charge', 'order_price__to_pay_charge', 'codcharge__cod_charge' )

    print header_row    
    for shipment in shipments:
        row_data = get_row_data(shipment)
        print row_data
