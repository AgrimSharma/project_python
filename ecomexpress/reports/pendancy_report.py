from django.db.models import Q

from service_centre.models import Shipment, Bags
from reports.report_api import ReportGenerator
from reports.ecomm_mail import ecomm_send_mail


def unclosed_ships(year, month, rts=False):
    col_heads = ("Air Waybill No","Order No", "Item Desctiption", "Added On", "Origin", 
        "Destination", "Current SC", "Shipper", "Consignee", "Collectable Value", "Declared Value", 
        "Reason code", "Reason", "RTS Status", "Ref Airwaybill Number", "Bag No", "Last Bag No")

    q = Q()
    if rts:
        q = Q(rts_status=1)
        file_name = 'open_rts_ships_{0}_{1}.xlsx'.format(year, month)
    else:
        q = ~Q(rts_status=1)
        file_name = 'open_non_rts_ships_{0}_{1}.xlsx'.format(year, month)

    data = list(Shipment.objects.using('local_ecomm')\
        .filter(q, status__lte=8, added_on__year=year, added_on__month=month)\
        .exclude(rts_status=2)\
        .exclude(shipper__code=32012)\
        .exclude(reason_code__code__in=[111, 777, 999, 888, 333, 310, 200,208,302,311])\
        .values_list('airwaybill_number', 'order_number', 'item_description', 'added_on', 
         'pickup__service_centre__center_name', 'original_dest__center_name', 
         'current_sc__center_name', 'shipper__name', 'consignee', 'collectable_value', 
         'declared_value', 'reason_code__code', 'reason_code__code_description', 'rts_status', 
         'ref_airwaybill_number'))

    report = ReportGenerator(file_name)
    report.write_header(col_heads)
    for row in data:
        try:
            bag = Bags.objects.filter(shipments__airwaybill_number=row[0])
            if bag: 
                bag = bag[0].bag_number
            else:
                bag = ''
            latest_bag = Bags.objects.filter(ship_data__airwaybill_number=row[0])
            if latest_bag:
                latest_bag = latest_bag[0].bag_number
            else:
                latest_bag = ""
        except Bags.DoesNotExist:
            latest_bag = ''
            bag = ''
        dt = list(row) + [bag, latest_bag]
        report.write_row(dt)
    report.manual_sheet_close()
    path = 'http://billing.ecomexpress.in/static/uploads/reports/' + report.file_name
    ecomm_send_mail('Pendancy Report {0} {1}'.format(year, month), path, 
        ['jinesh@prtouch.com', 'jaideeps@ecomexpress.in', 'manjud@ecomexpress.in', 'sunainas@ecomexpress.in'])
