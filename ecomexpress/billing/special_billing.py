import xlrd
import math
from django.db.models import Q, Sum, Count
from service_centre.models import Shipment, Order_price, CODCharge, ShipmentExtension
from location.models import Zone
#from service_centre.general_updates import update_shipment_pricing
from customer.models import Customer, Product
from ecomm_admin.models import Brentrate
from billing.charge_calculations import rts_pricing, price_updated


NCR_CITIES = ['DELHI', 'FARIDABAD', 'GHAZIABAD', 'GREATER NOIDA', 'GURGAON', 'NOIDA']
tv_18_bill_dict = {
    'Delhi and Satellite cities':{'South':32.00,'Delhi and Satellite cities':18.00, 'North':22.00, 'Mumbai':27.00, 'Bengaluru':30.00, 'West':27.00, 'Srinagar':33.00},
    'North':{'South':30.00,'Delhi and Satellite cities':22.00, 'North':23.00, 'Mumbai':29.00, 'Bengaluru':30.00, 'West':29.00, 'Srinagar':35.00},
    'Mumbai':{'Delhi and Satellite cities':27.00, 'North':29.00, 'Mumbai':18.00, 'Bengaluru':25.00, 'West':25.00, 'Srinagar':40.00, 'South': 25.00},
    'Bengaluru':{'Delhi and Satellite cities':30.00, 'North':30.00, 'Mumbai':25.00, 'Bengaluru':18.00, 'West':27.00, 'Srinagar':40.00, 'South':23.00},
    'West':{'South':27.00,'Delhi and Satellite cities':27.00, 'North':29.00, 'Mumbai':25.00, 'Bengaluru':27.00, 'West':25.00, 'Srinagar':40.00},
    'Srinagar':{'Delhi and Satellite cities':33.00, 'North':35.00, 'Mumbai':40.00, 'Bengaluru':40.00, 'West':40.00, 'Srinagar':18.00}
}

def get_fuel_surcharge_rate(cid):
    #fuel_surcharge_rate = c.fuelsurcharge_set.get().fuelsurcharge_min_fuel_rate
    customer = Customer.objects.get(id=cid)

    fs = customer.fuelsurcharge_set.all()
    if not fs.exists():
        return 0

    fs = fs[0]
    br = Brentrate.objects.latest('id')
    if not fs.flat_fuel_surcharge and not fs.fuelsurcharge_min_rate:
        return 0
    elif fs.flat_fuel_surcharge:
        return fs.flat_fuel_surcharge
    elif fs.fuelsurcharge_min_fuel_rate >= br.todays_rate:
        return fs.fuelsurcharge_min_rate
    else:
        diff = br.todays_rate - fs.fuelsurcharge_min_fuel_rate
        updated_rate = math.ceil(diff / br.fuel_cost_increase) * br.percentage_increase + fs.fuelsurcharge_min_rate

        if not fs.max_fuel_surcharge:
            return updated_rate
        elif fs.max_fuel_surcharge > updated_rate:
            return updated_rate
        else:
            return fs.max_fuel_surcharge

def get_shipment_zones(shipment):
    org_zone = shipment.pickup.service_centre.city.zone
    if shipment.original_dest:
        dest_zone = shipment.original_dest.city.zone
    else:
        dest_zone = shipment.service_centre.city.zone
    return (org_zone, dest_zone)

def get_zone_rate(shipment):
    org_zone = shipment.pickup.service_centre.city.zone.zone_name
    if shipment.original_dest:
        dest_zone = shipment.original_dest.city.zone.zone_name
    else:
        dest_zone = shipment.service_centre.city.zone.zone_name

    zone_list = ['North', 'West', 'Delhi and Satellite cities', 'Bengaluru', 'Mumbai', 'Srinagar']
    if dest_zone == 'Other North':
        dest_zone = 'North'
    if org_zone == 'Other North':
        org_zone = 'North'
    if org_zone in zone_list and dest_zone in zone_list:
        return tv_18_bill_dict[org_zone][dest_zone]
    return None

# Jasper - RTS - Where Original Dest is jammu city
def jasper_jammu(from_date, to_date):
    shipments = Shipment.objects.filter(shipment_date__range=(from_date, to_date), original_dest__id__in=[112, 170, 171], shipper__id=6, rts_status=1, billing=None)
    print 'start updating'
    count = 0
    for ship in shipments:
        count += 1
        print count
        awt = ship.actual_weight / 0.5
        Order_price.objects.filter(shipment=ship).update(freight_charge = 22.5 * awt)
    print 'updation completed'


def jasper_rts(from_date, to_date):
    shipments = Shipment.objects.filter(shipper__id=6, rts_status=1, shipment_date__range=(from_date, to_date), billing=None)
    print shipments.only('id').count()
    count = 0
    for s in shipments:
        count += 1
        print count
        wt = s.chargeable_weight / 0.5
        frt = math.ceil(wt) * 22.5
        Order_price.objects.filter(shipment=s).update(freight_charge=frt)
    print 'finished'

#Jasper
#-----------
#ncr - ncr - 0 frt
#other north- other north 50 % 0f frt
#fsc =0 jasper alwys
def jasper_rts_frt_update(from_date, to_date):
    shipments = Shipment.objects.filter(shipper__id=6, rts_status=1, shipment_date__range=(from_date, to_date), billing=None)
    ncr = Zone.objects.get(zone_name='Delhi and Satellite cities')
    north = Zone.objects.get(zone_name='North')
    other_north = Zone.objects.get(zone_name='Other North')
    for shipment in shipments:
        org_zone, dest_zone = get_shipment_zones(shipment)
        #print org_zone, dest_zone
        if (org_zone.id == dest_zone.id == ncr.id): #or (org_zone == dest_zone == other_north):
            print 'NCR Zone Update'
            Order_price.objects.filter(shipment=shipment).update(freight_charge=0, fuel_surcharge=0)
        elif org_zone in [ncr, north, other_north] and dest_zone in [ncr, north, other_north]:
            print 'Org and Dest in List'
            frt = shipment.order_price_set.get().freight_charge * 0.5
            Order_price.objects.filter(shipment=shipment).update(freight_charge=frt, fuel_surcharge=0)
        else:
            print 'No updation', org_zone, dest_zone

    print 'finished'

#rts cases - vector ecomm 
#-------------------------------------
#frt
#fsc = 70%
def vector_ecomm_rts(from_date, to_date):
    shipments = Shipment.objects.filter(shipper__id=126, rts_status=1, shipment_date__range=(from_date, to_date), billing=None)
    count = 0
    for shipment in shipments:
        count += 1
        print count
        frt = shipment.order_price_set.get().freight_charge * 0.7
        fsc = shipment.order_price_set.get().fuel_surcharge * 0.7
        Order_price.objects.filter(shipment=shipment).update(freight_charge=frt, fuel_surcharge=fsc)

# ACTOLINGERIE RETAIL PRIVATE LIMITED  (cid-47, code-96047)
# reverse charges will be same as freight for this customer
# i.e. whatever is the freight charged on the particular reverse pickup
# shipment will also be considered as reverse.
def actolingerie_update(from_date, to_date):
    # ships = Ships where reverse_status = 1
    shipments = Shipment.objects.filter(
                       reverse_pickup=1,
                       shipment_date__range=(from_date, to_date),
                       shipper__id=47, billing=None)

    #c = Customer.objects.get(id=47)
    count = 0
    print shipments.only('id').count()
    fuel_surcharge_rate = get_fuel_surcharge_rate(47)
    for ship in shipments:
        count += 1
        print count
        op = ship.order_price_set.get()
        op.reverse_charge = op.freight_charge
        op.fuel_surcharge =  (op.reverse_charge + op.freight_charge ) * fuel_surcharge_rate / 100
        op.save()
    print 'actrolingerie updated'


# WS Retail JMU origin shipment rates should be 40+40.
#DealsKart - Reverse no Fuel surcharge (94020 - 20)
# Fuelsurcharge min rate: 0
# Fuelsurcharge min fuel rate: 0
# Flat fuel surcharge: 25
# Max fuel surcharge: 0
def dealskart_update(from_date, to_date):

    #if cid == 20:
    #    tot_charge = freight_charge
    #else:
    #    tot_charge = freight_charge+sdd_charge+to_pay_charge+reverse_charge
    shipments = Shipment.objects.filter(
                       reverse_pickup=1,
                       shipment_date__range=(from_date, to_date),
                       shipper__id=20, billing=None)

    print 'updation started..'
    fuel_surcharge_rate = get_fuel_surcharge_rate(20)
    for s in shipments:
        op = s.order_price_set.get()
        op.fuel_surcharge = op.freight_charge *  fuel_surcharge_rate / 100
        op.save()
    print 'deals kart updated..'


def tv18_updates_stage1(from_date, to_date):
    """
    #get all (dec, jan) Shipments where orginal_actual_weight <= 0.250 and rto_status = 1
    #for each of this ship, get ref shipment and update extension.orginal_actual_weight = parent shipment orginal_actual_weight.
    """
    shipments = Shipment.objects.filter(shipment_date__range=(from_date, to_date),
                       shipper__id=7, rto_status=1, shipext__original_act_weight__lte=0.25, billing=None)

    print shipments.only('id').count()
    count = 0
    for s in shipments:
        count += 1
        print count
        ref_ship = Shipment.objects.filter(airwaybill_number=s.ref_airwaybill_number)
        if ref_ship.exists() and ref_ship[0].shipext.original_act_weight != s.shipext.original_act_weight:
            ref_ship[0].shipext.original_act_weight = s.shipext.original_act_weight
            ref_ship[0].save()
        else:
            print s.airwaybill_number
    print 'tv18 stage 1 completed..'

def tv18_updates_stage2(from_date, to_date):
    """
    Rts_status = 1
    RTSShips (Jan) where ship.extension.orginal_actual_weight <= 0.250 (kg)
    Get rates, and update freight, fuel surcharge
    """
    shipments = Shipment.objects.filter(shipment_date__range=(from_date, to_date),
                       shipper__id=7, shipext__original_act_weight__lte=0.25, billing=None)

    print shipments.only('id').count()
    count = 0
    fuel_surcharge_rate = get_fuel_surcharge_rate(7)
    for s in shipments:
        count += 1
        print count
        # freight to be updated here
        rate = get_zone_rate(s)
        if not rate:
            print 'zone out :',s.airwaybill_number
            continue
        op = s.order_price_set.get()
        op.freight_charge = rate
        op.fuel_surcharge = rate * fuel_surcharge_rate / 100
        op.save()
    print 'tv18 stage 2 completed..'

def ecomm_charge_update(start_date, end_date):
    shipments = Shipment.objects.filter(
        shipper__id=12,
        shipment_date__range=(start_date, end_date),
        billing=None
    )

    for s in shipments:
        Order_price.objects.filter(
            shipment=s
        ).update(
            freight_charge=0, fuel_surcharge=0, 
            valuable_cargo_handling_charge=0,
            to_pay_charge=0, rto_charge=0, 
            sdd_charge=0, sdl_charge=0, 
            reverse_charge=0, tab_charge=0
        )
        CODCharge.objects.filter(
            shipment=s
        ).update(cod_charge=0)

def update_product_type(year, month):
    cod = Product.objects.get(product_name='cod')
    ppd = Product.objects.get(product_name='ppd')
    ebscod = Product.objects.get(product_name='ebscod')
    ebsppd = Product.objects.get(product_name='ebsppd')
    rev = Product.objects.get(product_name='rev')

    print 'COD'
    codships = Shipment.objects.filter(shipment_date__year=year, shipment_date__month=month, product_type='cod', billing=None)
    cod_count = ShipmentExtension.objects.filter(shipment__in=codships).update(product=cod)
    print cod_count

    print 'PPD'
    ppdships = Shipment.objects.filter(shipment_date__year=year, shipment_date__month=month, product_type='ppd', billing=None)
    ppd_count = ShipmentExtension.objects.filter(shipment__in=ppdships).update(product=ppd)
    print ppd_count

    print 'EBS PPD'
    ebsppdships = Shipment.objects.filter(shipment_date__year=year, shipment_date__month=month, airwaybill_number__startswith=3, billing=None)
    ebsppd_count = ShipmentExtension.objects.filter(shipment__in=ebsppdships).update(product=ebsppd)
    print ebsppd_count

    print 'EBS COD'
    ebscodships = Shipment.objects.filter(shipment_date__year=year, shipment_date__month=month, airwaybill_number__startswith=4, billing=None)
    ebscod_count = ShipmentExtension.objects.filter(shipment__in=ebscodships).update(product=ebscod)
    print ebscod_count

    print 'REV SHIPS'
    revships = Shipment.objects.filter(shipment_date__year=year, shipment_date__month=month, airwaybill_number__startswith=5, billing=None)
    rev_count = ShipmentExtension.objects.filter(shipment__in=revships).update(product=rev)
    print rev_count

def update_awbs_product_type(awbs):
    cod = Product.objects.get(product_name='cod')
    ppd = Product.objects.get(product_name='ppd')
    ebscod = Product.objects.get(product_name='ebscod')
    ebsppd = Product.objects.get(product_name='ebsppd')
    rev = Product.objects.get(product_name='rev')

    for awb in awbs:
        first_digit = str(awb)[0]
        try:
            ship = Shipment.objects.get(airwaybill_number=awb, billing=None)
            if first_digit == '3':
                ShipmentExtension.objects.filter(shipment=ship).update(product=ebsppd)
            elif first_digit == '4':
                ShipmentExtension.objects.filter(shipment=ship).update(product=ebscod)
            elif first_digit == '5':
                ShipmentExtension.objects.filter(shipment=ship).update(product=rev)
            elif ship.product_type == 'cod':
                ShipmentExtension.objects.filter(shipment=ship).update(product=cod)
            elif ship.product_type == 'ppd':
                ShipmentExtension.objects.filter(shipment=ship).update(product=ppd)
        except Shipment.DoesNotExist:
            pass 

def update_awbs_product_type_backup(awbs):
    cod = Product.objects.get(product_name='cod')
    ppd = Product.objects.get(product_name='ppd')
    ebscod = Product.objects.get(product_name='ebscod')
    ebsppd = Product.objects.get(product_name='ebsppd')
    rev = Product.objects.get(product_name='rev')

    print 'COD'
    codships = Shipment.objects.filter(airwaybill_number__in=awbs, product_type='cod', billing=None)
    cod_count = ShipmentExtension.objects.filter(shipment__in=codships).update(product=cod)
    print cod_count

    print 'PPD'
    ppdships = Shipment.objects.filter(airwaybill_number__in=awbs, product_type='ppd', billing=None)
    ppd_count = ShipmentExtension.objects.filter(shipment__in=ppdships).update(product=ppd)
    print ppd_count

    print 'EBS PPD'
    ebsppdships = Shipment.objects.filter(airwaybill_number__in=awbs, airwaybill_number__startswith=3, billing=None)
    ebsppd_count = ShipmentExtension.objects.filter(shipment__in=ebsppdships).update(product=ebsppd)
    print ebsppd_count

    print 'EBS COD'
    ebscodships = Shipment.objects.filter(airwaybill_number__in=awbs, airwaybill_number__startswith=4, billing=None)
    ebscod_count = ShipmentExtension.objects.filter(shipment__in=ebscodships).update(product=ebscod)
    print ebscod_count

    print 'REV SHIPS'
    revships = Shipment.objects.filter(airwaybill_number__in=awbs, airwaybill_number__startswith=5, billing=None)
    rev_count = ShipmentExtension.objects.filter(shipment__in=revships).update(product=rev)
    print rev_count


def zero_freight_shipments(from_date, to_date):
    nn_labels = Customer.objects.get(code=25053)
    jasper = Customer.objects.get(code=92006)

    inv_ships = Shipment.objects.filter(shipment_date__range=('2014-09-01', '2014-09-30'),order_price__freight_charge=0).exclude(Q(shipper__id=6) | Q(shipper__id=53), rts_status=1, 
        pickup__service_centre__city__city_name__in=NCR_CITIES, original_dest__city__city_name__in=NCR_CITIES)

    origin_city = shipment.get('pickup__service_centre__city__city_name')
    destination_city = shipment.get('original_dest__city__city_name')
    jas_ships = Shipment.objects.filter(shipment_date__range=('2014-09-01', '2014-09-30'), rts_status=1, shipper__id=6,
        order_price__freght_charge__gt=0, pickup__service_centre__city__city_name__in=NCR_CITIES, original_dest__city__city_name__in=NCR_CITIES)
    if jas_ships:
        print jas_ships.count()
    nn_ships = Shipment.objects.filter(shipment_date__range=('2014-09-01', '2014-09-30'), rts_status=1, shipper__id=53,
        order_price__freght_charge__gt=0, pickup__service_centre__city__city_name__in=NCR_CITIES, original_dest__city__city_name__in=NCR_CITIES)
    if nn_ships:
        print nn_ships.count()

def update_rate_freight(file_path):
    wb = xlrd.open_workbook(file_path)
    sh = wb.sheet_by_index(0)
    awbs = sh.col_values(0)[1:]
    frts = sh.col_values(1)[1:]
    fuels = sh.col_values(2)[1:]

    awb_frt_fuel = zip(awbs, frts, fuels)
 
    for a, frt, fuel in awb_frt_fuel:
        try:
            u = Order_price.objects.filter(shipment__airwaybill_number=int(a)).update(
                freight_charge=frt, fuel_surcharge=fuel)
            if not u:
                print a
        except:
            print a


def update_rates(file_path):
    wb = xlrd.open_workbook(file_path)
    sh = wb.sheet_by_index(0)
    awbs = sh.col_values(0)[1:]
    for a in awbs:
        try:
            s = Shipment.objects.get(airwaybill_number=a)
            price_updated(s, True)
        except:
            print a


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

def update_vchc(from_date, to_date):
    ships = Shipment.objects.filter(shipment_date__range=(from_date, to_date), shipper_id=6)

    for s in ships:
        vchc = get_vchc_charge(s.declared_value, s.collectable_value, s.actual_weight)
        Order_price.objects.filter(shipment=s).update(valuable_cargo_handling_charge=vchc)

def update_vchc_from_file(file_path):
    f = open(file_path, 'r')
    awbs = f.readlines()

    for awb in awbs:
        s = Shipment.objects.get(airwaybill_number=awb, shipper_id=6)
        vchc = get_vchc_charge(s.declared_value, s.collectable_value, s.actual_weight)
        Order_price.objects.filter(shipment=s).update(valuable_cargo_handling_charge=vchc)


def get_jasper_figures(from_date, to_date):
    shipments = Shipment.objects.filter(shipment_date__range=(from_date, to_date), shipper_id=6)

    total_ship_count = shipments.aggregate(ct=Count('id'))['ct']
    rts_ship_count = shipments.filter(rts_status=1).aggregate(ct=Count('id'))['ct']

    freight_sum = shipments.exclude(rts_status=1).aggregate(sm=Sum('order_price__freight_charge'))['sm']
    rts_sum = shipments.filter(rts_status=1).aggregate(sm=Sum('order_price__rto_charge'))['sm']
    cod_rts = shipments.filter(rts_status=1).aggregate(sm=Sum('codcharge__cod_charge'))['sm']
    cod_non_rts = shipments.exclude(rts_status=1).aggregate(sm=Sum('codcharge__cod_charge'))['sm']
    reverse_sum = shipments.aggregate(sm=Sum('order_price__reverse_charge'))['sm']
    vchc_sum = shipments.aggregate(sm=Sum('order_price__valuable_cargo_handling_charge'))['sm']

    return { 
        'total_ship_count':total_ship_count,
        'rts_ship_count':rts_ship_count,
        'freight_sum':freight_sum,
        'rts_sum':rts_sum,
        'cod_rts':cod_rts,
        'cod_non_rts':cod_non_rts,
        'reverse_sum':reverse_sum,
        'vchc_sum':vchc_sum}

def jasper_type_wise_figures(from_date, to_date):
    # forward
    shipments = Shipment.objects.filter(shipment_date__range=(from_date, to_date), shipper_id=6).exclude(reverse_pickup=True).exclude(rts_status=1)
    total_ship_count = shipments.aggregate(ct=Count('id'))['ct']
    freight_sum = shipments.exclude(rts_status=1).aggregate(sm=Sum('order_price__freight_charge'))['sm']
    cod_rts = shipments.filter(rts_status=1).aggregate(sm=Sum('codcharge__cod_charge'))['sm']
    cod_non_rts = shipments.exclude(rts_status=1).aggregate(sm=Sum('codcharge__cod_charge'))['sm']
    cod_rts =  cod_rts if cod_rts else 0
    cod_non_rts = cod_non_rts if cod_non_rts else 0
    print 'FWD', total_ship_count, freight_sum, cod_non_rts - cod_rts 

    # RTS
    shipments = Shipment.objects.filter(shipment_date__range=(from_date, to_date), shipper_id=6, rts_status=1).exclude(reverse_pickup=True)
    total_ship_count = shipments.aggregate(ct=Count('id'))['ct']
    rts_sum = shipments.filter(rts_status=1).aggregate(sm=Sum('order_price__rto_charge'))['sm']
    cod_rts = shipments.filter(rts_status=1).aggregate(sm=Sum('codcharge__cod_charge'))['sm']
    cod_non_rts = shipments.exclude(rts_status=1).aggregate(sm=Sum('codcharge__cod_charge'))['sm']
    cod_rts =  cod_rts if cod_rts else 0
    cod_non_rts = cod_non_rts if cod_non_rts else 0
    print 'RTO', total_ship_count, rts_sum, cod_non_rts - cod_rts 

    # Reverse
    shipments = Shipment.objects.filter(shipment_date__range=(from_date, to_date), shipper_id=6, reverse_pickup=True).exclude(rts_status=1)
    total_ship_count = shipments.aggregate(ct=Count('id'))['ct']
    cod_rts = shipments.filter(rts_status=1).aggregate(sm=Sum('codcharge__cod_charge'))['sm']
    cod_non_rts = shipments.exclude(rts_status=1).aggregate(sm=Sum('codcharge__cod_charge'))['sm']
    reverse_sum = shipments.aggregate(sm=Sum('order_price__reverse_charge'))['sm']
    cod_rts =  cod_rts if cod_rts else 0
    cod_non_rts = cod_non_rts if cod_non_rts else 0
    print 'REV', total_ship_count, reverse_sum, cod_non_rts - cod_rts 

from service_centre.models import *
from billing.models import BillingSubCustomer, Billing
from billing.product_billing_update import update_productbilling
from customer.models import Customer

def get_sum(*args):
    return sum([x for x in args if x])


# bill_type : 0 - reverse pickups, 1 - forward shipments
def subcustomer_billing(bill_id):
    billing = Billing.objects.get(id=bill_id)
    #print 'start generation ', billing_from, billing_to
    customer = billing.customer
    billing_from = billing.billing_date_from
    billing_to = billing.billing_date
    print 1
    shipments = billing.shipments.all()

    f = open('/tmp/subs.txt', 'r')
    sub_ids = f.readlines()
    f.close()
    sub_ids = [int(a) for a in sub_ids]

    if not shipments:
        return None

    today = datetime.datetime.now()
    print 2
    freight_data = list(shipments.values("pickup__subcustomer_code__id").\
            annotate(
                Count('id'),
                total_cw = Sum('chargeable_weight'),
                op_freight = Sum('order_price__freight_charge'),
                op_sdl = Sum('order_price__sdl_charge'),
                op_fuel = Sum('order_price__fuel_surcharge'),
                op_rto_price = Sum('order_price__rto_charge'),
                op_sdd_charge = Sum('order_price__sdd_charge'),
                op_reverse_charge = Sum('order_price__reverse_charge'),
                op_valuable_cargo_handling_charge = Sum('order_price__valuable_cargo_handling_charge'),
                #op_tab_charge = Sum('order_price__tab_charge'),
                op_to_pay = Sum('order_price__to_pay_charge')))

    print 3
    cod_charges = dict(shipments.exclude(rts_status = 1).values("pickup__subcustomer_code__id").\
        annotate(cod_charge=Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code__id', 'cod_charge'))

    print 4
    cod_charges_negative = dict(shipments.filter(rts_status = 1).\
            values("pickup__subcustomer_code__id").\
            annotate(cod_charge = Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code__id', 'cod_charge'))
    print 5
    cod_charge = 0
    cod_charge_negative = 0
    for fd in freight_data:
        subsc_id = fd["pickup__subcustomer_code__id"]
        if int(subsc_id) not in sub_ids:
            continue
        print subsc_id
        # get the cod charge for the subcustomer
        #print 'subcustomer :',subsc_id
        cod_charge = cod_charges.get(subsc_id)
        cod_charge = cod_charge if cod_charge else 0

        # get the negative cod charge for the subcustomer
        cod_charge_negative = cod_charges_negative.get(subsc_id)
        cod_charge_negative = cod_charge_negative if cod_charge_negative else 0
        try:
            sbilling = BillingSubCustomer(
                subcustomer_id=subsc_id,
                freight_charge=fd["op_freight"],
                sdl_charge=fd["op_sdl"],
                fuel_surcharge=fd["op_fuel"],
                valuable_cargo_handling_charge=fd["op_valuable_cargo_handling_charge"],
                to_pay_charge=fd["op_to_pay"],
                rto_charge=fd["op_rto_price"],
                sdd_charge=fd["op_sdd_charge"],
                reverse_charge=fd["op_reverse_charge"],
                total_chargeable_weight=fd["total_cw"],
                #tab_charge = fd["op_tab_charge"],
                cod_applied_charge=cod_charge,
                cod_subtract_charge=cod_charge_negative,
                total_cod_charge=cod_charge - cod_charge_negative,
                billing_date=billing.billing_date,
                billing_date_from=billing.billing_date_from,
                shipment_count=fd["id__count"],
                billing_id=billing.id)
            total_charge = get_sum(
                sbilling.freight_charge, sbilling.sdl_charge,
                sbilling.fuel_surcharge, sbilling.valuable_cargo_handling_charge,
                sbilling.to_pay_charge, sbilling.rto_charge,
                sbilling.sdd_charge, sbilling.reverse_charge)
            
            sbilling.total_charge = total_charge + cod_charge - cod_charge_negative
            sbilling.generation_status = 1
            sbilling.save()
    
            sub_shipments = shipments.filter(pickup__subcustomer_code__id=subsc_id)
            sbilling.shipments.add(*(list(sub_shipments)))
            sub_shipments.update(sbilling=sbilling)
        except IOError:
            print 'failed for ', subsc_id

    return billing

def subcustomer_id_billing(bill_id, sub_id):
    billing = Billing.objects.get(id=bill_id)
    #print 'start generation ', billing_from, billing_to
    customer = billing.customer
    billing_from = billing.billing_date_from
    billing_to = billing.billing_date
     
    shipments = billing.shipments.all()

    if not shipments:
        return None

    today = datetime.datetime.now()
    fd = dict(shipments.filter(pickup__subcustomer_code_id=sub_id).\
            aggregate(
                Count('id'),
                total_cw = Sum('chargeable_weight'),
                op_freight = Sum('order_price__freight_charge'),
                op_sdl = Sum('order_price__sdl_charge'),
                op_fuel = Sum('order_price__fuel_surcharge'),
                op_rto_price = Sum('order_price__rto_charge'),
                op_sdd_charge = Sum('order_price__sdd_charge'),
                op_reverse_charge = Sum('order_price__reverse_charge'),
                op_valuable_cargo_handling_charge = Sum('order_price__valuable_cargo_handling_charge'),
                #op_tab_charge = Sum('order_price__tab_charge'),
                op_to_pay = Sum('order_price__to_pay_charge')))

    cod_charges = dict(shipments.filter(pickup__subcustomer_code_id=sub_id).exclude(rts_status = 1).\
        aggregate(cod_charge=Sum('codcharge__cod_charge')))

    cod_charges_negative = dict(shipments.filter(pickup__subcustomer_code_id=sub_id).filter(rts_status = 1).\
        aggregate(cod_charge = Sum('codcharge__cod_charge')))

    cod_charge = cod_charges['cod_charge']
    cod_charge = cod_charge if cod_charge else 0

    # get the negative cod charge for the subcustomer
    cod_charge_negative = cod_charges_negative['cod_charge']
    cod_charge_negative = cod_charge_negative if cod_charge_negative else 0

    sbilling = BillingSubCustomer(
        subcustomer_id=sub_id,
        freight_charge=fd["op_freight"],
        sdl_charge=fd["op_sdl"],
        fuel_surcharge=fd["op_fuel"],
        valuable_cargo_handling_charge=fd["op_valuable_cargo_handling_charge"],
        to_pay_charge=fd["op_to_pay"],
        rto_charge=fd["op_rto_price"],
        sdd_charge=fd["op_sdd_charge"],
        reverse_charge=fd["op_reverse_charge"],
        total_chargeable_weight=fd["total_cw"],
        #tab_charge = fd["op_tab_charge"],
        cod_applied_charge=cod_charge,
        cod_subtract_charge=cod_charge_negative,
        total_cod_charge=cod_charge - cod_charge_negative,
        billing_date=billing.billing_date,
        billing_date_from=billing.billing_date_from,
        shipment_count=fd["id__count"],
        billing_id=billing.id)
    
    cod_applied_charge = cod_charge if cod_charge else 0
    cod_subtract_charge = cod_charge_negative if cod_charge_negative else 0
    total_charge = get_sum(
        sbilling.freight_charge,
        sbilling.sdl_charge,
        sbilling.fuel_surcharge,
        sbilling.valuable_cargo_handling_charge,
        sbilling.to_pay_charge,
        sbilling.rto_charge,
        sbilling.sdd_charge,
        sbilling.reverse_charge)
        
    sbilling.total_charge = total_charge + cod_applied_charge - cod_subtract_charge
    sbilling.generation_status = 1
    sbilling.save()
    
    sub_shipments = shipments.filter(pickup__subcustomer_code_id=sub_id)
    sbilling.shipments.add(*(list(sub_shipments)))
    sub_shipments.update(sbilling=sbilling)

    return billing
