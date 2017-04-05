from django import template
from service_centre.models import ReverseShipment, CashTallyHistory, Shipment
register = template.Library()


@register.filter
def get_shipment_count_bk(pickups):

    pickups = pickups.all()
    count = 0

    if pickups:
        for p in pickups:
            count += int(p.pieces)
    return count

@register.filter
def get_shipment_count(pickups):
    rs = ReverseShipment.objects.filter(reverse_pickup_id = pickups)
    count = 0
    if rs:
       count = rs.count()
    return count

@register.filter
def subtract(value, arg):
    value = value if value else 0
    arg = arg if arg else 0
    return value - arg


@register.filter
def get_collected_amount(ship_id):
    shipment = Shipment.objects.get(id=ship_id)
    if shipment.shipext.partial_payment:
        return CashTallyHistory.objects.filter(shipment=shipment).latest('id').current_collection
    else:
        return shipment.collectable_value

@register.filter
def show_checked_collected_amount(shipment):
    if shipment.shipext.partial_payment:
        return CashTallyHistory.objects.get_last_collection(shipment=shipment)

    collected_amount = shipment.shipext.collected_amount
    if collected_amount:
        return collected_amount
    else:
        return shipment.collectable_value


@register.filter
def show_unchecked_collected_amount(shipment):
    if shipment.shipext.partial_payment:
        return CashTallyHistory.objects.get_last_collection(shipment=shipment)

    collected_amount = shipment.shipext.collected_amount
    if collected_amount:
        return collected_amount
    else:
        return 0

@register.filter
def show_pending_amount(shipment, checked):
    collectable_value = shipment.collectable_value
    if shipment.shipext.partial_payment:
        return collectable_value - CashTallyHistory.objects.get_collection_sum(shipment=shipment)

    if int(checked):
        return 0
    else:
        return collectable_value - shipment.shipext.collected_amount

@register.filter
def show_ref_awb_status(awb):
    try:
        sh = Shipment.objects.get(airwaybill_number =awb)
    except Shipment.DoesNotExist:
        return ''
    if sh.reason_code:
        return sh.reason_code.code_description
    else:
        return ''

@register.filter
def show_ref_rts_status(awb):
    try:
        sh = Shipment.objects.get(airwaybill_number =awb)
    except Shipment.DoesNotExist:
        return ''
    return sh.rts_status

@register.filter
def show_ref_awb(awb):
    try:
        sh = Shipment.objects.get(airwaybill_number =awb)
    except Shipment.DoesNotExist:
        return ''
    return sh.ref_airwaybill_number
