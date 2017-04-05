import math
from django.db.models import Q
from service_centre.models import Shipment, Order_price, CODCharge, ShipmentExtension
from location.models import Zone
#from service_centre.general_updates import update_shipment_pricing
from customer.models import Customer, Product
from ecomm_admin.models import Brentrate


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

