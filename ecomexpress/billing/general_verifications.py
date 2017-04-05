import logging

from service_centre.models import Shipment


def rts_parent_customer_check(start_date, end_date):
    ships = Shipment.objects.filter(
        shipment_date__range=(start_date, end_date), billing=None
    ).exclude(rts_status=0).exclude(shipper_id=12).values_list(
        'airwaybill_number', 'shipper_id', 'ref_airwaybill_number')

    for awb, shipper_id, ref_awb in ships:
        try:
            rs = Shipment.objects.get(airwaybill_number=ref_awb)
            if rs.shipper_id != shipper_id:
                logging.info('{0} - {1} - mismatch'.format(ref_awb, rs.shipper_id))
        except Shipment.DoesNotExist:
            logging.info('{0} - not exist'.format(ref_awb))

def cod_shipments_with_zero_collectable_value(start_date, end_date):
    """ Cod Shipment's can't have zero collectable value """
    ships = Shipment.objects.filter(
        shipment_date__range=(start_date, end_date), billing=None, 
        product_type='cod', collectable_value=0
    ).exclude(shipper_id=12).values_list(
        'airwaybill_number', 'shipper_id', 'shipment_date')
    for a, s, sd in ships:
        logging.info('{0} - {1} - {2}'.format(a, s, sd))


def blank_subcustomer_check(start_date, end_date):
    """Subcustomer / Vendor cannot be none for shipment. Otherwise price calculation wont happen """
    ships = Shipment.objects.filter(
        shipment_date__range=(start_date, end_date), billing=None,
        pickup__subcustomer_code=None).values_list('airwaybill_number', 'shipper__name')

    for a, s in ships:
        logging.info('{0} - {1}'.format(a, s))
