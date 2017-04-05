import datetime

from django.db.models import get_model, Q

from service_centre.models import (Shipment,
        get_internal_shipment_status, StatusUpdate, ServiceCenter)
from reports.models import *
from customer.models import Customer, Shipper, Product


def get_previous_year_month(n):
    today = datetime.datetime.today()
    year, month = today.year, today.month
    if n == 0:
        return (year, month)

def update_shipment(awb):
    year_month = Shipment.objects.get(airwaybill_number=awb).added_on.strftime('%Y_%m')
    genericquery = get_model('reports', 'GenericQuery_%s'%(year_month))
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(year_month))
    shipments = list(Shipment.objects.using('local_ecomm')\
            .filter(airwaybill_number=awb)\
            .values(
                'airwaybill_number', 'order_number', 'product_type', 
                'actual_weight', 'volumetric_weight', 'collectable_value', 
                'declared_value', 'pickup__service_centre', 'original_dest',
                'shipper__name', 'pickup__customer_code__name', 'consignee', 
                'mobile', 'added_on', 'status', 'expected_dod',
                'ref_airwaybill_number', 'rts_status', 'rto_status', 
                'return_shipment', 'reason_code__code', 'reason_code_id'
            )
    )
    shipment = shipments[0]
    airwaybill_number = shipment.get('airwaybill_number')
    order_number = shipment.get('order_number')
    product_type = shipment.get('product_type')
    weight = shipment.get('actual_weight')
    vol_weight = shipment.get('volumetric_weight')
    cod_amount = shipment.get('collectable_value')
    declared_value = shipment.get('declared_value')
    origin_sc = shipment.get('pickup__service_centre')
    destination_sc = shipment.get('original_dest')
    origin = ServiceCenter.objects.get(id=origin_sc) if origin_sc else None
    destination = ServiceCenter.objects.get(id=destination_sc) if destination_sc else None
    vendor_id = shipment.get('shipper__name')
    shipper_id = shipment.get('pickup__customer_code__name')
    vendor = Customer.objects.get(name=vendor_id) if vendor_id else None
    shipper = Customer.objects.get(name=shipper_id) if shipper_id else None
    consignee = shipment.get('consignee')
    contact_number = shipment.get('mobile')
    pu_date = shipment.get('added_on')
    status = shipment.get('status')
    expected_date = shipment.get('expected_dod')
    rts_status = shipment.get('rts_status')
    rto_status = shipment.get('rto_status')
    ref_airwaybill_number = shipment.get('ref_airwaybill_number')
    reason_code_id = shipment.get('reason_code_id')
    reason_code = shipment.get('reason_code__code')
    return_shipment = shipment.get('return_shipment')

    ship_status = None
    updated_date = None
    remarks = None
    reason = None
    recieved_by = None
    del_date = None
    del_time = None
    return_status = None
    ref_updated_on = None
    prud_date = None
    first_attempt_date = None
    first_attempt_status = None

    history = shipment_history.objects.using('local_ecomm')\
            .filter(shipment__airwaybill_number=airwaybill_number).order_by('-updated_on')\
            .values('status', 'updated_on', 'reason_code__code', 'remarks',
                'reason_code__code_description', 'current_sc__center_name')

    status_updates = StatusUpdate.objects.using('local_ecomm')\
            .filter(shipment__airwaybill_number=airwaybill_number).order_by('-added_on')\
            .values('status', 'added_on', 'reason_code__code', 'remarks',
                'reason_code__code_description', 'date', 'time', 'recieved_by')

    history_exists = history.exists()
    su_exists = status_updates.exists()

    # product_type
    if str(airwaybill_number)[0] in ['1', '7']:
        pass
    elif str(airwaybill_number)[0] == '3':
        product_type = 'ebsppd'
    elif str(airwaybill_number)[0] == '4':
        product_type = 'ebscod'
    elif str(airwaybill_number)[0] == '5':
        product_type = 'rev'
    product_type = Product.objects.get(product_name=product_type)
    # get updated_date
    if history_exists:
        updated_date = history[0].get('updated_on')

    # status
    if rts_status or rto_status or return_shipment == 3 or reason_code_id == 5:
        ship_status = "Returned"
    else:
        ship_status = get_internal_shipment_status(status)

    # reason_code and reason, received_by
    if su_exists:
        reason_code = status_updates[0].get('reason_code__code')
        reason = status_updates[0].get('reason_code__code_description')
        recieved_by = status_updates[0].get('recieved_by')
    elif history_exists:
        reason_code = history[0].get('reason_code__code')
        reason = history[0].get('reason_code__code_description')

    # get del_date, del_time, prud_date, first_attempt_date, first_attempt_status and update remarks
    if su_exists:
        if status_updates.count() > 1:
            prud_date = status_updates[1].get('added_on')
        else:
            prud_date = status_updates[0].get('added_on')

        del_date = status_updates[0].get('date')
        del_time = status_updates[0].get('time')
        first_attempt_date = status_updates[0].get('date')
        first_attempt_status = status_updates[0].get('reason_code__code_description')

    # if reason code among following then swap remarks with status
    if reason_code in [207, 230, 303, 304, 309]:
        ship_status = 'Intransit'
        h = history.filter(status__in=[3,5])
        if h.exists():
            hremarks = h[0].get('remarks')
            current_sc = h[0].get('current_sc__center_name')
            bag = hremarks.split('. ')[1][:3]
            remarks = "Shipment Connected to {0} from {1}".format(bag, current_sc)
    elif reason_code in [200, 206, 208, 302, 311, 888]:
        reason, ship_status = ship_status, reason
    elif reason_code == 333:
        ship_status = 'Shipment Lost'

    # get remarks
    if remarks:
        pass
    elif su_exists:
        rem_status = status_updates[0].get('status')
        if rem_status == 2:
            remarks = 'Delivered'
        else:
            remarks = status_updates[0].get('remarks')
    elif history_exists:
        remarks = history[0].get('remarks')

    # return_status and ref_updated_on
    if ref_airwaybill_number:
        try:
            ref_ship = Shipment.objects.using('local_ecomm').get(airwaybill_number=ref_airwaybill_number)
            ref_rts_status = ref_ship.rts_status
            if ref_rts_status == 2:
                return_status = 'Returned'
            else:
                ref_status = ref_ship.status
                return_status = get_internal_shipment_status(ref_status)

            # get ref_updated_on
            ref_ship_added_on = ref_ship.added_on.strftime('%Y_%m')
            ref_shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(ref_ship_added_on))
            ref_history = ref_shipment_history.objects.using('local_ecomm')\
                    .filter(shipment=ref_ship).order_by('-updated_on').values('updated_on')
            if ref_history.exists():
                ref_updated_on = ref_history[0].get('updated_on')
        except Shipment.DoesNotExist:
            pass
    else:
        ref_airwaybill_number = 0

    # convert dates to string
    if pu_date:
        pu_date = pu_date
    if expected_date:
        expected_date = expected_date

    gq, created = genericquery.objects.get_or_create(airwaybill_number=awb)

    genericquery.objects.filter(airwaybill_number=gq.airwaybill_number).\
        update(order_number=order_number, product_type=product_type, weight=weight, vol_weight=vol_weight,
        cod_amount=cod_amount, declared_value=declared_value, origin=origin, destination=destination,
        customer=vendor, sub_customer=shipper, consignee=consignee, contact=contact_number,
        pickup_date=pu_date, status=ship_status, expected_date=expected_date, updated_date=updated_date,
        remarks=remarks, reason_code=reason_code, reason=reason, received_by=recieved_by,
        delivery_date=del_date, delivery_time=del_time, ref_airwaybill_number=ref_airwaybill_number,
        return_status=return_status, return_updated_on=ref_updated_on, rts_status=rts_status,
        rto_status=rto_status, prud_date=prud_date, first_attempt_status=first_attempt_status,
        first_attempt_date=first_attempt_date, update_on=datetime.datetime.now())

    if int(rts_status) == 1:
        return (True, ref_airwaybill_number)
    else:
        return (False, ref_airwaybill_number)

def history_hour_update(year, month):
    """update all shipments which are updated in between previous 6
    hours, for the given month and year
    """
    now = datetime.datetime.now()
    today = now.strftime('%Y-%m-%d')
    start_hour = (now - datetime.timedelta(hours=4)).hour
    start_time = '{today} {hour}:00:00'.format(today=today, hour=start_hour)
    end_hour = now.hour
    end_time = '{today} {hour}:00:00'.format(today=today, hour=end_hour)

    year_month = "{0}_{1}".format(year, month) #now.strftime('%Y_%m')
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(year_month))
    awbs = shipment_history.objects.filter(updated_on__range=(start_time, end_time))\
            .values_list('shipment__airwaybill_number', flat=True)
    unique_awbs = list(set(awbs))

    for awb in unique_awbs:
        update_rts, ref_awb = update_shipment(awb)
        if update_rts:
            update_shipment(ref_awb)

def history_day_update(gq_date):
    year_month = datetime.datetime.strptime(gq_date, '%Y-%m-%d').date().strftime('%Y_%m')
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(year_month))
    awbs = shipment_history.objects.filter(updated_on__range=(gq_date + ' 00:00:00', gq_date + ' 23:59:59'))\
            .values_list('shipment__airwaybill_number', flat=True)
    unique_awbs = list(set(awbs))

    for awb in unique_awbs:
        update_rts, ref_awb = update_shipment(awb)
        if update_rts:
            update_shipment(ref_awb)

    return True

def history_month_update(year, month):
    year_month = '{0}_{1}'.format(year, month)
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(year_month))
    awbs = shipment_history.objects.values_list('shipment__airwaybill_number', flat=True)
    unique_awbs = list(set(awbs))

    for awb in unique_awbs:
        update_rts, ref_awb = update_shipment(awb)
        if update_rts:
            update_shipment(ref_awb)

    return True

def history_delivered_update(gq_date):

    now = datetime.datetime.now()
    today = now.strftime('%Y-%m-%d')
    start_hour = (now - datetime.timedelta(hours=4)).hour
    start_time = '{today} {hour}:00:00'.format(today=today, hour=start_hour)
    end_hour = now.hour
    end_time = '{today} {hour}:00:00'.format(today=today, hour=end_hour)

    year_month = datetime.datetime.strptime(gq_date, '%Y-%m-%d').date().strftime('%Y_%m')
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(year_month))
    awbs = shipment_history.objects.filter(
        updated_on__range=(start_time, end_time),
        shipment__status=9
    ).values_list('shipment__airwaybill_number', flat=True)
    unique_awbs = list(set(awbs))

    for awb in unique_awbs:
        update_rts, ref_awb = update_shipment(awb)
        if update_rts:
            update_shipment(ref_awb)

    return True

def month_update(year, month, rts=False):
    q = Q()
    q = q & Q(added_on__year=year, added_on__month=month)
    if rts:
        q = q & Q(rts_status=1)
    
    awbs = Shipment.objects.filter(q).values_list('airwaybill_number', flat=True)
    for awb in awbs:
        update_rts, ref_awb = update_shipment(awb)
        if update_rts:
            update_shipment(ref_awb)

def date_range_update(frm, to):
    awbs = Shipment.objects.filter(
        added_on__range=(frm, to)
    ).values_list('airwaybill_number', flat=True)
    for awb in awbs:
        update_rts, ref_awb = update_shipment(awb)
        if update_rts:
            update_shipment(ref_awb)

def hourly_update():
    # update all the airwaybill numbers which are updated in the previous six hours
    today = datetime.datetime.today()
    year, month = today.strftime('%Y'), today.strftime('%m')

    # current month date
    history_hour_update(year, month)

    # previous month update
    if month == 1:
    # if present month=Jan, then previus month=dec
        year = year - 1
        month = 12
        history_hour_update(year, month)
    else:
        history_hour_update(year, month-1)

    # second previous month update
    if month == 1:
    # if present month=Jan, second previous month=nov
       year = year - 1
       month = 11
       history_hour_update(year, month)
    elif month == 2:
    # if present month=Feb, second previous month=dec
       year = year - 1
       month = 12
       history_hour_update(year, month)
    else:
       history_hour_update(year, month-2)
