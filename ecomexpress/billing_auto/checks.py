import sys
import datetime
import xlrd

from django.conf import settings
from django.db.models import Sum

from service_centre.models import Shipment
#from service_centre.general_updates import update_shipment_pricing
from reports.report_api import ReportGenerator
from billing.models import Billing, ProductBilling


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
    shipments = Shipment.objects.filter(shipment_date__range=(date_from, date_to))

    print 'CHECK FOR PRODUCT UPDATE'
    # check for un updated product field for shipment extension
    none_product_count = shipments.filter(shipext__product=None).only('id').count()
    if none_product_count > 0:
        print 'There are shipments whose product field is not updated. Please check, then contine'
        #sys.exit(0)
    else:
        print 'Congrats! There are no Shipments with unupdated product'

    print 'CHECK FOR FREIGHT CHARGES FOR EBS SHIPMENTS'
    ebs_ships = shipments.filter(shipext__product__product_name__in=['ebsppd', 'ebscod'],
            order_price__freight_charge__gt=1).only('id').count()
    if ebs_ships > 0:
        print 'Ebs shipments exists with freight charge greater than one'
        #sys.exit(0)
    else:
        print 'Congrats! No ebs shipments with freight charge greater than 1'

    # check for ref_airwaybill number issues
    print 'CHECK FOR REF_AIRWAYBILL NUMBER ISSUES'
    non_rts_ships = shipments.filter(rts_status=0).exclude(ref_airwaybill_number=None).only('id').count()
    if non_rts_ships > 0:
        print 'Non rts shipments has ref airwaybill numbers. Please check .', non_rts_ships
        #sys.exit(0)
    else:
        print 'Congrats! no Non rts shipment found with ref airwaybill numbers'

    rts_ships = shipments.exclude(rts_status=0)
    rts_awbs = []
    for ship in rts_ships:
        try:
            if Shipment.objects.get(airwaybill_number=ship.ref_airwaybill_number).ref_airwaybill_number != ship.airwaybill_number:
                print 'Ref Issue :', ship.airwaybill_number
                rts_awbs.append(ship.airwaybill_number)
        except Shipment.DoesNotExist:
            print 'shipment does not exist ', ship.airwaybill_number
    if rts_awbs:
        print rts_awbs
        #sys.exit(0)
    else:
        print 'Congrats! No RTS shipments issue found'

    print 'START JASPER TESTS'
    ships = Shipment.objects.filter(shipment_date__range=(date_from, date_to), shipper__id=6)
    print 'check for rto charges'
    frt = ships.filter(rts_status=1, freight_charge__gt=0)
    print 'Freight charge applied for RTS shipments :', frt
    rto = ships.filter(rts_status=1, rto_charge=0)
    print 'RTO charge not applied for RTS shipments :', rto

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
