import math
from collections import defaultdict

from django.db.models import Q

from customer.models import Customer, ForwardFreightRate
from location.models import City
from service_centre.models import Shipment


def get_customer_city_zone_mapping(customer):
    # customer_city_zone_mapping: For each customer city is mapped to different
    # zones. So we keep a city-zone mapping for each customer.
    # customer_city_zone_mapping: {'city code': 'zone code', ...   }
    # customer_city_zone_mapping: {'DEH': 'NTU', 'MUM': 'WTU', ...   }
    zone_label = customer.zone_label_id
    if not zone_label:
        return {}
    return dict(City.objects.filter(
        labeled_zones__label_id=zone_label
    ).values_list('city_shortcode', 'labeled_zones__zone_shortcode'))


def get_customer_zone_rate_mapping(customer):
    # customer zone to zone rate map
    # customer_zone_rate_mapping :{
    #     'NTU': {'STU': {1:120, 2:100}, 'WTU': {1: 100: 2: 80}, ..}
    #     'STU': {'NTU': {1:120, 2:100}, 'WTU': {1: 100: 2: 80}, ..}
    #     ...
    #     'origin zone code': {
    #         'dest zone code 1': {1:120, 2:100},
    #         'dest zone code 2': {1: 100: 2: 80}, ..
    #     }
    # }

    customer_zone_rate_mapping = defaultdict(dict)
    forward_rates = ForwardFreightRate.objects.filter(
        version__customer_id=customer, version__active=True
    ).values('org_zone__zone_shortcode', 'dest_zone__zone_shortcode',
             'range_from', 'rate_per_slab')
    for rate in forward_rates:
        org_zone = rate['org_zone__zone_shortcode']
        dest_zone = rate['dest_zone__zone_shortcode']
        slab_rate = rate['rate_per_slab']
        try:
            customer_zone_rate_mapping[org_zone][dest_zone]
        except KeyError:
            customer_zone_rate_mapping[org_zone][dest_zone] = {1: 0, 2: 0}

        if int(rate['range_from']) == 0:
            customer_zone_rate_mapping[org_zone][dest_zone][1] = slab_rate
        else:
            customer_zone_rate_mapping[org_zone][dest_zone][2] = slab_rate
    return customer_zone_rate_mapping


def verify_freight(customer, year, month):
    """verify whether the freight charge is applied properly for the given
    customer for the given year and month."""
    customer_city_zone_mapping = get_customer_city_zone_mapping(customer)

    customer_zone_rate_mapping = get_customer_zone_rate_mapping(customer.id)

    def calc_rates(args):
        origin_city = args[2]
        dest_city = args[3]
        chargeable_weight = args[4]
        freight = args[5]

        try:
            origin_zone = customer_city_zone_mapping[origin_city]
            dest_zone = customer_city_zone_mapping[dest_city]

            rates = customer_zone_rate_mapping[origin_zone][dest_zone]
            first_slab, second_slab = rates[1], rates[2]

            second_wt = math.ceil(((chargeable_weight * 1000) - 500) / 500)
            if second_wt > 0:
                calculated_freight = (second_wt * second_slab) + first_slab
            else:
                calculated_freight = first_slab

            freight = freight if freight else 0
            calculated_freight = calculated_freight if calculated_freight else 0
        except KeyError:
            calculated_freight = -1
        return (args[0], args[1], origin_zone, dest_zone, chargeable_weight, 
                freight, calculated_freight)

    q = Q()
    # for naaptol, awari and vector ecommerce freight charge calculation 
    # logic is different for RTS shipments. so we exclude them
    if customer.id in [4, 13, 126]:
        q = q & Q(rts_status=0)

    # get the shipments for customer, year, month
    shipments = Shipment.objects.filter(
        q, shipper_id=customer, shipment_date__year=year,
        shipment_date__month=month
    ).values_list(
        'airwaybill_number', 'shipper__name',
        'pickup__service_centre__city__city_shortcode',
        'original_dest__city__city_shortcode',
        'chargeable_weight',
        'order_price__freight_charge')
    # for each shipment get the origin and destination zone.
    # then calculate the freight for those zones combination based on the rates
    # given for the customer. (calculated rate)
    # then match the curent rate with the calculated rate.
    # if it is wrong add it to the error list.
    ship_with_rates = map(calc_rates, shipments)
    # if rate not found or freights not matching filter it
    match_rates = lambda x: int(x[6]) == 0 or round(float(x[5]), 2) != round(float(x[6]), 2)
    return filter(match_rates, ship_with_rates)
