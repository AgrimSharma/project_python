import math
import xlrd
import datetime
import calendar
import pdb

from reports.ecomm_mail import ecomm_send_mail
from reports.report_api import CSVReportGenerator
from service_centre.models import Shipment, Order_price, CODCharge
from billing.models import Billing


"""
create one seperate file in billing and write your functions there
now the logic is simple.

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

charge_dict_11500 = {
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


def get_sum(*args, **kwargs):
    items = [val if val else 0 for val in args]
    return sum(items)

def get_freight_charge(chargeable_weight, first_slab, second_slab):
    second_wt = math.ceil(((chargeable_weight * 1000) - 500) / 500)
    if second_wt > 0:
        return ( second_wt * second_slab ) + first_slab
    else:
        return first_slab

metro_cities = ['MUMBAI', 'BENGALURU', 'DELHI', 'AHMEDABAD', 'KOLKATA', 'PUNE', 'HYDERABAD', 'CHENNAI']
ncr_cities = ['DELHI', 'FARIDABAD', 'GHAZIABAD', 'GREATER NOIDA', 'GURGAON', 'NOIDA']
KASHMIR_CITIES =  ['JAMMU', 'SRINAGAR', 'BARAMULLA', 'SOPORE', 'ANANTNAG', 'ACAHBAL',
    'BIJBIHARA', 'DAILGAM ', 'MATTAN ', 'GANDERBAL', 'BUDGAM', 'KULGAM']

def generate_report(from_date, to_date):
    year_month = datetime.datetime.today().strftime('%Y_%m')
    print year_month
    bill_shipments = Shipment.objects.filter(
            #airwaybill_number__in=[708383460, 105239931])
            shipper__id=6, shipment_date__gte=from_date,
            shipment_date__lte=to_date)

    charge_dict = charge_dict_11500
    report = CSVReportGenerator('Jasper_{0}_report.csv'.format(year_month))
    report.write_row(
       ('Forward Waybill number', 'RTO Waybill number', 'Sub-order / Refrence number',
        'Order date', 'Origin City', 'Destination City', 'Payment Mode', 'TYPE',
        'Origin Zone', 'Zone/Lanes (Destination)', '1 st slab rate/500gm',
        'Next slab rate/500gm', 'Product bill value', 'COD Amount', 'Amount collected',
        'Delivery status', 'Dead Weight (gms)', 'Length', 'Breadth', 'Height',
        'VOL WT IN GMS', 'Billed WT Type', 'Billed Wt (gms)', 'FORWARD FRT Charges',
        'FSC Charges', 'RTO Charges', 'COD Charges', 'Sdl Charge',
        'Sdd Charge', 'Valuable cargo handling Charge', 'To_pay Charge',
        'Reverse Charge', 'Net Amount', 'S tax', 'Education secondary tax',
        'Cess higher secondary tax', 'Grand Total')
    )
    shipments = bill_shipments.values('airwaybill_number',
            'ref_airwaybill_number', 'order_number', 'added_on', 'sdl',
            'pickup__service_centre__city__city_name', 'pickup__service_centre__city__zone__zone_name',
            'original_dest__city__city_name', 'original_dest__city__zone__zone_name',
            'shipext__product__product_name', 'rts_status', 'reverse_pickup', 'declared_value',
            'collectable_value', 'actual_weight', 'length', 'breadth', 'height', 'volumetric_weight',
            'chargeable_weight', 'reason_code__code_description', 'order_price__freight_charge',
            'order_price__fuel_surcharge', 'order_price__rto_charge', 'order_price__sdl_charge',
            'order_price__sdd_charge', 'order_price__valuable_cargo_handling_charge',
            'order_price__to_pay_charge', 'order_price__reverse_charge', 'codcharge__cod_charge')

    frt_sum = 0
    rto_sum = 0
    rev_sum = 0
    cod_sum = 0
    #pdb.set_trace()
    for shipment in shipments:
        airwaybill_number = shipment.get('airwaybill_number')
        ref_airwaybill_number = shipment.get('ref_airwaybill_number')
        order_number = shipment.get('order_number')
        order_date = shipment.get('added_on')
        origin_city = shipment.get('pickup__service_centre__city__city_name')
        destination_city = shipment.get('original_dest__city__city_name')
        payment_mode = shipment.get('shipext__product__product_name')
        ship_type = '' #Type
        origin_zone = shipment.get('pickup__service_centre__city__zone__zone_name') #Zone/Lanes
        destination_zone = shipment.get('original_dest__city__zone__zone_name') #Destination Zone
        first_slab = 0
        second_slab = 0
        declared_value = shipment.get('declared_value') #Product bill value
        collectable_value = shipment.get('collectable_value') #COD Amount, Amount collected
        code_desctription = shipment.get('reason_code__code_description') # Delivery status
        actual_weight = shipment.get('actual_weight') #Dead Weight (gms)
        length = shipment.get('length')
        breadth = shipment.get('breadth')
        height = shipment.get('height')
        vol_weight = shipment.get('volumetric_weight') #VOL WT IN GMS
        billed_weight_type = '' #Billed WT Type
        chargeable_weight = shipment.get('chargeable_weight') #Billed Wt (gms)
        if actual_weight <= 3:
            chargeable_weight = actual_weight
        freightcharge = shipment.get('order_price__freight_charge') #FORWARD FRT Charges
        freight_charge = 0
        #fuel_surcharge = shipment.get('order_price__fuel_surcharge') #FSC Charges
        fuel_surcharge = 0 # fuel surcharge will be 0 for all shipments of jasper
        rto_charge = 0
        rtocharge = shipment.get('order_price__rto_charge')
        codcharge = shipment.get('codcharge__cod_charge')
        cod_charge = shipment.get('codcharge__cod_charge')
        sdl_charge = shipment.get('order_price__sdl_charge')
        sdlcharge = shipment.get('order_price__sdl_charge')
        sdl_status = shipment.get('sdl')
        sdd_charge = shipment.get('order_price__sdd_charge')
        vchc = shipment.get('order_price__valuable_cargo_handling_charge')
        to_pay_charge = shipment.get('order_price__to_pay_charge')
        reversecharge = shipment.get('order_price__reverse_charge')
        reverse_charge = shipment.get('order_price__reverse_charge')
        rts_status = shipment.get('rts_status')
        reverse_pickup = shipment.get('reverse_pickup')
        net_amount = '' #Net Amount
        service_tax = '' #
        edu_tax = '' #
        cess = '' #
        grand_total = '' #
        cod_charge = cod_charge if cod_charge else 0
        codcharge = codcharge if codcharge else 0
        if payment_mode == 'cod':
            cod_charge = collectable_value * 0.02
        else:
            cod_charge = 0
        if rts_status == 1:
            ship_type = 'RTO'
            cod_charge = 0 - cod_charge
            #print 'cod charge reversed'
        elif reverse_pickup:
            ship_type = 'REVERSE'
        else:
            ship_type ='FRWRD'
        print airwaybill_number
        # charge calculation
        print 'orgin city : {0}  destination_city: {1}'.format(origin_city, destination_city)
        print 'orgin zone : {0}  destination_zone : {1}'.format(origin_zone, destination_zone)
        intracity = False
        intrazone = False
        restrts = False

        if reverse_pickup and not rts_status:
            if origin_zone == destination_zone == 'Delhi and Satellite cities':
                charges = charge_dict.get('rev_ncr')
            else:
                charges = charge_dict.get('rev_all')
        elif origin_city == destination_city:
            charges = charge_dict.get('intra_city')
            if rts_status == 1:
                intracity = True
        elif origin_zone == destination_zone == 'Delhi and Satellite cities':
            charges = charge_dict.get('intra_city')
            if rts_status == 1:
                intracity = True
        elif origin_zone == destination_zone:
            charges = charge_dict.get('zones')
            if rts_status == 1:
                intrazone = True
        elif (origin_city in KASHMIR_CITIES) and \
                    destination_city in KASHMIR_CITIES:
            charges = charge_dict.get('zones')
            if rts_status == 1:
                intrazone = True
        elif (origin_zone != destination_zone) and \
                    destination_city in metro_cities:
            charges = charge_dict.get('metro')
            if rts_status == 1:
                restrts = True
        elif (origin_zone != destination_zone) and \
                    destination_zone == 'Delhi and Satellite cities':
            charges = charge_dict.get('metro')
            if rts_status == 1:
                restrts = True
        elif (origin_zone != destination_zone) and \
                    destination_city in KASHMIR_CITIES:
            charges = charge_dict.get('jammu')
            if rts_status == 1:
                restrts = True
        elif (origin_zone != destination_zone) and \
                    destination_zone == 'East':
            charges = charge_dict.get('east')
            if rts_status == 1:
                restrts = True
        else:
            charges = charge_dict.get('rest')
            if rts_status == 1:
                restrts = True
        #print charges
        #print '*'*100
        first_slab = charges.get(1)
        second_slab = charges.get(2)

        if intracity:
            first_slab = 0
            second_slab = 0
        elif intrazone:
            first_slab =  first_slab * 0.5
            second_slab = second_slab * 0.5
        elif restrts:
            first_slab =  22.5
            second_slab = 22.5

        # find origin and destination zone
        if origin_city == destination_city:
            origin_zone = 'intra_city'
            destination_zone = 'intra_city'
        elif origin_zone == destination_zone == 'Delhi and Satellite cities':
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
            elif origin_zone == 'East':
                origin_zone = 'east'
            else:
                origin_zone = 'rest'

            if destination_city in metro_cities:
                destination_zone = 'metro'
            elif destination_city in ncr_cities:
                destination_zone = 'delhi'
            elif destination_city in KASHMIR_CITIES:
                destination_zone = 'jammu'
            elif destination_zone == 'East':
                destination_zone = 'east'
            else:
                destination_zone = 'rest'

        #if airwaybill_number in [500087566, 500043766, 500082713]:
             #first_slab = 50
             #second_slab = 50

        if rts_status == 1:
            if destination_zone not in ['intra_city','zones']:
                origin_zone = 'rest'
                destination_zone = 'rest'

        # update origin and destination zones
        origin_zone = charge_dict.get(origin_zone).get('name')
        destination_zone = charge_dict.get(destination_zone).get('name')
        #print first_slab, second_slab
        # calculate freight, fuel surcharge, and other taxes, charges
        if rts_status == 1:
           rto_charge = get_freight_charge(chargeable_weight, first_slab, second_slab)
           #if (not freightcharge) or (freightcharge % 22.5 == 0):
           #    rto_charge = freightcharge
           #else:
           #    rto_charge = freightcharge / 2
        else:
            if reverse_pickup:
                reverse_charge = get_freight_charge(chargeable_weight, first_slab, second_slab)
            else:
                freight_charge = get_freight_charge(chargeable_weight, first_slab, second_slab)
        #if freightcharge != freight_charge:
            #print 'frt : ', airwaybill_number, freightcharge, freight_charge
        if sdl_status == 1 and destination_city in KASHMIR_CITIES:
            sdl_charge = get_freight_charge(chargeable_weight, 50, 50)
        else:
            sdl_charge = 0

        """ for comparison
        if cod_charge or codcharge:
            c1 = round(codcharge * codcharge, 2)
            c2 = round(cod_charge * cod_charge, 2)
            d = c1 - c2
            if d != 0:
                print 'cod :', airwaybill_number, codcharge, cod_charge

        if reversecharge != reverse_charge:
            print 'rev :', airwaybill_number, reversecharge, reverse_charge

        if rtocharge != rto_charge:
            print 'rto :', airwaybill_number, rtocharge, rto_charge
        """
        net_amount = get_sum(
            freight_charge ,sdl_charge ,fuel_surcharge ,vchc ,
            to_pay_charge, rto_charge , sdd_charge, reverse_charge, cod_charge)

        service_tax = net_amount * 0.12
        edu_tax =  service_tax * 0.02
        cess =  service_tax * 0.01
        grand_total = get_sum(net_amount , service_tax , edu_tax , cess)
        frt_sum = get_sum(frt_sum, freight_charge)
        rto_sum = get_sum(rto_charge , rto_sum )
        cod_sum = get_sum(cod_charge , cod_sum )
        rev_sum = get_sum(reverse_charge , rev_sum )
        if rts_status == 1:
            disp_airwaybill_number = ref_airwaybill_number
            disp_ref_airwaybill_number =  airwaybill_number
        else:
            disp_airwaybill_number = airwaybill_number
            disp_ref_airwaybill_number =  ref_airwaybill_number

        row_data = ( disp_airwaybill_number, disp_ref_airwaybill_number, order_number, order_date,
            origin_city, destination_city, payment_mode, ship_type, origin_zone,
            destination_zone, first_slab, second_slab, declared_value, collectable_value,
            collectable_value, code_desctription, actual_weight, length, breadth, height, vol_weight,
            billed_weight_type, chargeable_weight, freight_charge, fuel_surcharge,
            rto_charge, cod_charge, sdl_charge, sdd_charge, vchc, to_pay_charge,
            reverse_charge, net_amount, service_tax, edu_tax, cess, grand_total)
        report.write_row(row_data)
    print 'Frt sum: {0} RTO Sum: {1} COD Sum: {2}  Rev Chg: {3}'.format(frt_sum, rto_sum, cod_sum, rev_sum)
    ecomm_send_mail('Jasper Invoice Report',
                    'http://billing.ecomexpress.in/static/uploads/reports/{0}'.format(report.file_name),
                    ['jinesh@prtouch.com'])

def jasper_price_update(from_date=None, to_date=None, bill_id=None):
    bill_shipments = Shipment.objects.filter(
            shipper__id=6,
            shipment_date__gte=from_date,
            shipment_date__lte=to_date
    ).exclude(billing__isnull = False)
    ship_count = bill_shipments.only('airwaybill_number').count()
    now = datetime.datetime.now()
    first, last = calendar.monthrange(now.year, now.month)
    ship_per_day = ship_count / last

    if ship_per_day >= 11500:
        charge_dict = charge_dict_11500
    else:
        charge_dict = charge_dict_normal

    shipments = bill_shipments.values('airwaybill_number',
            'ref_airwaybill_number', 'order_number', 'added_on', 'sdl',
            'pickup__service_centre__city__city_name', 'pickup__service_centre__city__zone__zone_name',
            'original_dest__city__city_name', 'original_dest__city__zone__zone_name',
            'shipext__product__product_name', 'rts_status', 'reverse_pickup', 'declared_value',
            'collectable_value', 'actual_weight', 'length', 'breadth', 'height', 'volumetric_weight',
            'chargeable_weight', 'reason_code__code_description', 'order_price__freight_charge',
            'order_price__fuel_surcharge', 'order_price__rto_charge', 'order_price__sdl_charge',
            'order_price__sdd_charge', 'order_price__valuable_cargo_handling_charge',
            'order_price__to_pay_charge', 'order_price__reverse_charge', 'codcharge__cod_charge')
    metro_cities = ['MUMBAI', 'BENGALURU', 'DELHI', 'AHMEDABAD', 'KOLKATA', 'PUNE', 'HYDERABAD', 'CHENNAI']
    ncr_cities = ['DELHI', 'FARIDABAD', 'GHAZIABAD', 'GREATER NOIDA', 'GURGAON', 'NOIDA']
    KASHMIR_CITIES =  ['JAMMU', 'SRINAGAR', 'BARAMULLA', 'SOPORE', 'ANANTNAG', 'ACAHBAL', 'BIJBIHARA', 'DAILGAM ', 'MATTAN ', 'GANDERBAL', 'BUDGAM', 'KULGAM']

    frt_sum = 0
    rto_sum = 0
    rev_sum = 0
    cod_sum = 0
    #pdb.set_trace()
    for shipment in shipments:
        airwaybill_number = shipment.get('airwaybill_number')
        ref_airwaybill_number = shipment.get('ref_airwaybill_number')
        order_number = shipment.get('order_number')
        order_date = shipment.get('added_on')
        origin_city = shipment.get('pickup__service_centre__city__city_name')
        destination_city = shipment.get('original_dest__city__city_name')
        payment_mode = shipment.get('shipext__product__product_name')
        ship_type = '' #Type
        origin_zone = shipment.get('pickup__service_centre__city__zone__zone_name') #Zone/Lanes
        destination_zone = shipment.get('original_dest__city__zone__zone_name') #Destination Zone
        first_slab = 0
        second_slab = 0
        declared_value = shipment.get('declared_value') #Product bill value
        collectable_value = shipment.get('collectable_value') #COD Amount, Amount collected
        code_desctription = shipment.get('reason_code__code_description') # Delivery status
        actual_weight = shipment.get('actual_weight') #Dead Weight (gms)
        length = shipment.get('length')
        breadth = shipment.get('breadth')
        height = shipment.get('height')
        vol_weight = shipment.get('volumetric_weight') #VOL WT IN GMS
        billed_weight_type = '' #Billed WT Type
        chargeable_weight = shipment.get('chargeable_weight') #Billed Wt (gms)
        if actual_weight <= 3:
            chargeable_weight = actual_weight
        freightcharge = shipment.get('order_price__freight_charge') #FORWARD FRT Charges
        freight_charge = 0
        fuel_surcharge = shipment.get('order_price__fuel_surcharge') #FSC Charges
        rto_charge = shipment.get('order_price__rto_charge')
        codcharge = shipment.get('codcharge__cod_charge')
        cod_charge = shipment.get('codcharge__cod_charge')
        sdl_charge = shipment.get('order_price__sdl_charge')
        sdl_status = shipment.get('sdl')
        sdd_charge = shipment.get('order_price__sdd_charge')
        vchc = shipment.get('order_price__valuable_cargo_handling_charge')
        to_pay_charge = shipment.get('order_price__to_pay_charge')
        reversecharge = shipment.get('order_price__reverse_charge')
        reverse_charge = shipment.get('order_price__reverse_charge')
        rts_status = shipment.get('rts_status')
        reverse_pickup = shipment.get('reverse_pickup')
        net_amount = '' #Net Amount
        service_tax = '' #
        edu_tax = '' #
        cess = '' #
        grand_total = '' #
        cod_charge = cod_charge if cod_charge else 0
        codcharge = codcharge if codcharge else 0
        #if payment_mode == 'cod':
        #    cod_charge = collectable_value * 0.018
        #else:
        #    cod_charge = 0

        if rts_status == 1:
            ship_type = 'RTO'
            cod_charge = 0 - cod_charge
        elif reverse_pickup:
            ship_type = 'REVERSE'
        else:
            ship_type ='FRWRD'

        # charge calculation
        #print 'orgin city : {0}  destination_city: {1}'.format(origin_city, destination_city)
        #print 'orgin zone : {0}  destination_zone : {1}'.format(origin_zone, destination_zone)
        intracity = False
        intrazone = False
        restrts = False

        if reverse_pickup and not rts_status:
            if origin_zone == destination_zone == 'Delhi and Satellite cities':
                charges = charge_dict.get('rev_ncr')
            else:
                charges = charge_dict.get('rev_all')
        elif origin_city == destination_city:
            charges = charge_dict.get('intra_city')
            if rts_status == 1:
                intracity = True
        elif origin_zone == destination_zone == 'Delhi and Satellite cities':
            charges = charge_dict.get('intra_city')
            if rts_status == 1:
                intracity = True
        elif origin_zone == destination_zone:
            charges = charge_dict.get('zones')
            if rts_status == 1:
                intrazone = True
        elif (origin_city in KASHMIR_CITIES) and \
                    destination_city in KASHMIR_CITIES:
            charges = charge_dict.get('zones')
            if rts_status == 1:
                intrazone = True
        elif (origin_zone != destination_zone) and \
                    destination_city in metro_cities:
            charges = charge_dict.get('metro')
            if rts_status == 1:
                restrts = True
        elif (origin_zone != destination_zone) and \
                    destination_zone == 'Delhi and Satellite cities':
            charges = charge_dict.get('metro')
            if rts_status == 1:
                restrts = True
        elif (origin_zone != destination_zone) and \
                    destination_city in KASHMIR_CITIES:
            charges = charge_dict.get('jammu')
            if rts_status == 1:
                restrts = True
        elif (origin_zone != destination_zone) and \
                    destination_zone == 'East':
            charges = charge_dict.get('east')
            if rts_status == 1:
                restrts = True
        else:
            charges = charge_dict.get('rest')
            if rts_status == 1:
                restrts = True
        #print charges
        #print '*'*100
        first_slab = charges.get(1)
        second_slab = charges.get(2)

        if intracity:
            first_slab = 0
            second_slab = 0
        elif intrazone:
            first_slab =  first_slab * 0.5
            second_slab = second_slab * 0.5
        elif restrts:
            first_slab =  22.5
            second_slab = 22.5

        # find origin and destination zone
        if origin_city == destination_city:
            origin_zone = 'intra_city'
            destination_zone = 'intra_city'
        elif origin_zone == destination_zone == 'Delhi and Satellite cities':
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
            elif origin_zone == 'East':
                origin_zone = 'east'
            else:
                origin_zone = 'rest'

            if destination_city in metro_cities:
                destination_zone = 'metro'
            elif destination_city in ncr_cities:
                destination_zone = 'delhi'
            elif destination_city in KASHMIR_CITIES:
                destination_zone = 'jammu'
            elif destination_zone == 'East':
                destination_zone = 'east'
            else:
                destination_zone = 'rest'

        #if airwaybill_number in [500087566, 500043766, 500082713]:
             #first_slab = 50
             #second_slab = 50

        if rts_status == 1:
            if destination_zone not in ['intra_city','zones']:
                origin_zone = 'rest'
                destination_zone = 'rest'

        # update origin and destination zones
        origin_zone = charge_dict.get(origin_zone).get('name')
        destination_zone = charge_dict.get(destination_zone).get('name')
        #print first_slab, second_slab
        # calculate freight, fuel surcharge, and other taxes, charges
        if rts_status == 1:
            rto_charge = get_freight_charge(chargeable_weight, first_slab, second_slab)
           #if (not freightcharge) or (freightcharge % 22.5 == 0):
           #    rto_charge = freightcharge
           #else:
           #    rto_charge = freightcharge / 2
        else:
            if reverse_pickup:
                reverse_charge = get_freight_charge(chargeable_weight, first_slab, second_slab)
            else:
                freight_charge = get_freight_charge(chargeable_weight, first_slab, second_slab)
        #if freightcharge != freight_charge:
            #li = (airwaybill_number, ref_airwaybill_number , freightcharge, freight_charge)
            #print li
        if sdl_status == 1 and destination_city in KASHMIR_CITIES:
            sdl_charge = get_freight_charge(chargeable_weight, 50, 50)
        else:
            sdl_charge = 0

        #if (cod_charge or codcharge) and (abs(codcharge) != abs(cod_charge)):
            #li = (airwaybill_number, ref_airwaybill_number , codcharge, cod_charge)

        net_amount = get_sum(
            freight_charge ,sdl_charge ,fuel_surcharge ,vchc ,
            to_pay_charge, rto_charge , sdd_charge, reverse_charge, cod_charge
        )

        service_tax = net_amount * 0.12
        edu_tax =  service_tax * 0.02
        cess =  service_tax * 0.01
        grand_total = get_sum(net_amount , service_tax , edu_tax , cess)
        frt_sum = get_sum(frt_sum, freight_charge)
        rto_sum = get_sum(rto_charge , rto_sum )
        cod_sum = get_sum(cod_charge , cod_sum )
        rev_sum = get_sum(reverse_charge , rev_sum )

        oup = Order_price.objects.filter(shipment__airwaybill_number=airwaybill_number).update(
            rto_charge=rto_charge, reverse_charge=reverse_charge,
            freight_charge=freight_charge, sdl_charge=sdl_charge
        )
        #cop = CODCharge.objects.filter(shipment__airwaybill_number=airwaybill_number).update(cod_charge=abs(cod_charge))
        print 'awb, frt, cod, rto, sdl ',airwaybill_number, freight_charge, cod_charge, rto_charge, sdl_charge

    print 'Frt sum: {0} RTO Sum: {1} COD Sum: {2}  Rev Chg: {3}'.format(frt_sum, rto_sum, cod_sum, rev_sum)
