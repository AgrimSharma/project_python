import sys
import datetime
import xlrd

from django.conf import settings
from django.db.models import Sum, Count

from service_centre.models import Shipment
#from service_centre.general_updates import update_shipment_pricing
from reports.report_api import ReportGenerator
from billing.models import Billing, ProductBilling
import logging


def issue_finder(file_name, awb_column_no, comparing_column_number, field_name='freight_charge', sheet_index=0):
    """
    file_name: uploaded file name
    awb_column_no: airwaybill number column number
    comparing_column_number: anshul's values column number
    field_name: field to compare
    sheet_index: sheet number
    """
    fn = '/tmp/' + file_name
    wb = xlrd.open_workbook(fn)
    sh = wb.sheet_by_index(sheet_index)
    awbs = sh.col_values(awb_column_no)[1:]
    f2v = sh.col_values(comparing_column_number)[1:]

    val_tup = zip(awbs, f2v)
    error_list= []
    now = datetime.datetime.now().strftime('%Y-%m-%d-:%H:%m:%S')
    report = ReportGenerator('issue_list_{0}.xlsx'.format(now))
    report.write_header(('AWB', field_name + ' Ours', field_name + ' Ecomm', 'Chargeable Wt', 'Origin Zone', 'Dest Zone', 'Customer'))
    for awb, v2 in val_tup:
        s = Shipment.objects.get(airwaybill_number=awb)
        if field_name == 'cod_charge':
            try:
                obj = s.codcharge_set.get()
            except CODCharge.DoesNotExist:
                t = (int(awb), frt, v2, s.chargeable_weight, s.pickup.service_centre.city.zone, s.original_dest.city.zone, s.shipper.name)
                error_list.append(t)
                report.write_row(t)
                print t
                continue
        else:
            obj = s.order_price_set.get()

        frt = obj.__dict__.get(field_name)

        if round(float(frt), 2) != round(float(v2), 2):
            t=(int(awb), frt, v2, s.chargeable_weight, s.pickup.service_centre.city.zone, s.original_dest.city.zone, s.shipper.name)
            error_list.append(t)
            report.write_row(t)
            print t

    error_awbs = [int(x[0]) for x in error_list]
    print len(error_awbs)
    path = report.manual_sheet_close()
    print path

def pre_billing_checks(date_from, date_to):
    shipments = Shipment.objects.filter(shipment_date__range=(date_from, date_to)).exclude(shipper_id=12)
    logging.info('CHECK FOR PRODUCT UPDATE')
    # check for un updated product field for shipment extension
    none_product_count = shipments.filter(shipext__product=None).only('id').count()
    if none_product_count > 0:
        logging.info(
            'ERROR: {0} unupdated product fields found'.format(
            none_product_count))
    else:
        logging.info('SUCCESS: There are no Shipments with unupdated product')

    logging.info('CHECK FOR FREIGHT CHARGES FOR EBS SHIPMENTS')
    ebs_ships = shipments.filter(shipext__product__product_name__in=['ebsppd', 'ebscod'],
            order_price__freight_charge__gt=1).only('id').count()
    if ebs_ships > 0:
        logging.info('ERROR: Ebs shipments exists with freight charge greater than one :{0}'.format(ebs_ships))
    else:
        logging.info('SUCCESS: No ebs shipments with freight charge greater than 1')

    # check for ref_airwaybill number issues
    logging.info('CHECK FOR REF_AIRWAYBILL NUMBER ISSUES')
    """ 
    if rts status is 0 and ref_awb exists then ref awb should belongs to ecomm
    """
    non_rts_ships = shipments.filter(rts_status=0).exclude(ref_airwaybill_number=None).only('id').count()
    if non_rts_ships > 0:
        logging.info('SUCCESS: Non rts shipments has ref airwaybill numbers. Please check: {0}'.format(non_rts_ships))
    else:
        logging.info('ERROR: no Non rts shipment found with ref airwaybill numbers')

    # CODCHARGE
    logging.info('CODCHARGE OBJECT CHECKS')
    cods = Shipment.objects.filter(
        shipment_date__range=(date_from, date_to), 
        product_type='cod', codcharge=None, rts_status=0
    ).exclude(shipper_id=12).aggregate(Count('airwaybill_number'))
    logging.info('ERROR:{0}'.format(cods))

    # JASPER
    logging.info('START JASPER TESTS')
    ships = Shipment.objects.filter(shipment_date__range=(date_from, date_to), shipper__id=6)
    logging.info('CHECK FOR RTO CHARGES')
    frt = ships.filter(rts_status=1, order_price__freight_charge__gt=0).aggregate(Count('id'))
    logging.info('Freight charge applied for RTS shipments :{0}'.format(frt))
    rto = ships.filter(rts_status=1, order_price__rto_charge=0).aggregate(Count('id'))
    logging.info('RTO charge not applied for RTS shipments :{0}'.format(rto))
    logging.info('CHECK FOR SDL CHARGES')
    sdl = ships.filter(order_price__sdl_charge__gt=0).aggregate(Count('id'))
    logging.info('SDL applied :{0}'.format(sdl))
    vchc = ships.filter(order_price__valuable_cargo_handling_charge__gt=0).aggregate(Count('id'))
    logging.info('VCHC applied :{0}'.format(vchc))

    shipments = Shipment.objects.filter(shipper_id=6, shipment_date__range=(date_from, date_to))

    cod_shipments = shipments.filter(shipext__product_id=2)
    logging.info('CHECK FOR COD CHARGE')
    for s in cod_shipments:
        cc = round(s.collectable_value * 0.018, 2)
        cd = round(s.codcharge_set.get().cod_charge, 2)
        if  cc != cd:
            logging.info([s.airwaybill_number, cc, cd])

    logging.info('CHECK FOR RTO SHIPMENTS(rts_status=0)')
    logging.info('RTO Charge applied count :{0}'.format(
        shipments.filter(rts_status=0, order_price__rto_charge__gt=0).aggregate(Count('id'))))
    fc_not_applied = shipments.filter(rts_status=0, order_price__freight_charge__lte=0).exclude(reverse_pickup=True).aggregate(Count('id'))
    logging.info('FRIEGHT Charge not applied count :{0}'.format(fc_not_applied))
    logging.info('CHECK FOR RTO SHIPMENTS(rts_status=2)')
    logging.info('RTO Charge applied count :{0}'.format(
        shipments.filter(rts_status=2, order_price__rto_charge__gt=0).aggregate(Count('id'))))
    fc_not_applied = shipments.filter(rts_status=2, order_price__freight_charge__lte=0).exclude(reverse_pickup=True).aggregate(Count('id'))
    logging.info('FRIEGHT Charge not applied count :{0}'.format(fc_not_applied))
    logging.info('CHECK FOR RTO SHIPMENTS(rts_status=1)')
    logging.info('RTO Charge not applied count :{0}'.format(
        shipments.filter(rts_status=1, order_price__rto_charge__lte=0).aggregate(Count('id'))))
    fc_not_applied = shipments.filter(rts_status=1, order_price__freight_charge__gt=0).exclude(reverse_pickup=True).aggregate(Count('id'))
    logging.info('FRIEGHT Charge applied count :'.format(fc_not_applied))

def post_billing_checks(bill_id):
    bill = Billing.objects.get(id=bill_id)
    keys = ['cod_applied_charge',
            'to_pay_charge',
            'total_chargeable_weight',
            'education_secondary_tax',
            'service_tax',
            'total_cod_charge',
            #'demarrage_charge',
            'cess_higher_secondary_tax',
            'freight_charge',
            'fuel_surcharge',
            'shipment_count',
            'sdl_charge',
            'valuable_cargo_handling_charge',
            'rto_charge',
            'reverse_charge',
            'total_charge_pretax',
            'sdd_charge',
            'cod_subtract_charge',
            'total_payable_charge']
    for key in keys:
        key_val = ProductBilling.objects.filter(billing=bill).aggregate(val=Sum(key))['val']
        bill_val = bill.__dict__[key]
        if int(key_val) != int(bill_val):
            print 'Mismatch found - {0} : {1} - {2}'.format(key, bill_val, key_val)
    print 'Check finished for {0}'.format(bill_id)

def check_jasper(from_date, to_date):
    shipments = Shipment.objects.filter(shipper_id=6, shipment_date__range=(from_date, to_date))

    cod_shipments = shipments.filter(shipext__product_id=2)
    print 'CHECK FOR COD CHARGE'
    for s in cod_shipments:
        cc = round(s.collectable_value * 0.018, 2)
        cd = round(s.codcharge_set.get().cod_charge, 2)
        if  cc != cd:
            print s.airwaybill_number, cc, cd

    sys.exit(0)
    print 'CHECK FOR RTO SHIPMENTS(rts_status=0)'
    print 'RTO Charge applied count :', shipments.filter(rts_status=0, order_price__rto_charge__gt=0).aggregate(Count('id'))
    fc_not_applied = shipments.filter(rts_status=0, order_price__freight_charge__lte=0).exclude(reverse_pickup=True).aggregate(Count('id'))
    print 'FRIEGHT Charge not applied count :', fc_not_applied 
    print 'CHECK FOR RTO SHIPMENTS(rts_status=2)'
    print 'RTO Charge applied count :', shipments.filter(rts_status=2, order_price__rto_charge__gt=0).aggregate(Count('id'))
    fc_not_applied = shipments.filter(rts_status=2, order_price__freight_charge__lte=0).exclude(reverse_pickup=True).aggregate(Count('id'))
    print 'FRIEGHT Charge not applied count :', fc_not_applied 
    print 'CHECK FOR RTO SHIPMENTS(rts_status=1)'
    print 'RTO Charge not applied count :', shipments.filter(rts_status=1, order_price__rto_charge__lte=0).aggregate(Count('id'))
    fc_not_applied = shipments.filter(rts_status=1, order_price__freight_charge__gt=0).exclude(reverse_pickup=True).aggregate(Count('id'))
    print 'FRIEGHT Charge applied count :', fc_not_applied
