import datetime
from django.db.models import get_model, Q, get_model

from service_centre.models import Bags, Connection
from reports.report_api import ReportGenerator
from delivery.models import get_bag_history
from location.models import ServiceCenter


bag_status_dict = {
    0: 'Bag creation at SC',
    1: 'Bag closed at SC',
    2: 'Bag connected at SC',
    3: 'Bag inscanned at HUB',
    5: 'Bag creation at HUB',
    6: 'Bag closed at HUB',
    7: 'Bag connected at HUB',
    8: 'Bag inscanned at Delivery',
    9: 'Debagged at HUB, all shipments delinked',
    10: 'Debagged at Delivery, all shipments delinked',
    11: 'Deleted'
}

"""
    status 0 - not updated
           1 - bag created (SC)
           2 - shipment added (SC)
           3 - bag closed (SC)
           4 - added to connection (SC)
           5 - bag delinked from  connection (SC)
           6 - connection closed (SC)

           7 - bag created (HUB)
           8 - shipment added (HUB)
           9 - bag closed (HUB)
           10 - added to connection (HUB)
           11 - bag delinked from  connection (HUB)
           12 - connection closed (HUB)

           14 - bag scanned (DC)
           15 - bag scanned (HUB)

           16 - Mass updation

           17 - shipment debagged (DC)
           18 - shipment debagged (HUB)
"""


def bag_exception_inbound_origin(origin_obj, date_from_obj, date_to_obj):
    connections = Connection.objects.filter(
        destination=origin_obj, added_on__range=(date_from_obj, date_to_obj))
    data = []
    for conn in connections:
        bags = conn.bags.filter(
            Q(hub=origin_obj) | Q(destination=origin_obj),
            ~Q(current_sc=origin_obj), Q(bag_status=2)|Q(bag_status=7))
        for bag in bags:
            if bag.connection_set.latest('id').id != conn.id:
                continue

            bag_history = get_bag_history(bag).filter(Q(status=15) & Q(bag_sc=origin_obj))
            if not bag_history:
                ship_count = bag.shipments.filter(
                    status__in=[3,5]
                ).exclude(rts_status=2).exclude(status=9).exclude(
                     reason_code__code__in=[111, 777, 999, 888, 333, 310, 200,208, 302,311]
                ).count()
                destination = bag.destination.center_name if bag.destination else ''
                row = (conn.id, bag.bag_number, bag.origin.center_name,
                    destination, conn.added_on, conn.coloader,
                    conn.origin, conn.destination, ship_count)
                data.append(row)
    return data

def bag_exception_inbound_report(origin, date_from, date_to):
    """
    Reports for: Incoming bags to a particular hub / dc which is connected.
    """
    date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').strftime("%Y-%m-%d 00:00:00")
    date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').strftime("%Y-%m-%d 23:59:59")
    if int(origin) == 0:
        scs = ServiceCenter.objects.all()
    else:
        scs = ServiceCenter.objects.filter(id=origin)

    report = ReportGenerator('bag_exception_inbound_{0}.xlsx'.format(date_to))
    col_heads = (
        'Conn Number', 'Bag number', 'Bag origin', 'Bag destination',
        'Conn Date', 'Coloader Name', 'Conn. Origin', 'Conn. Dest',
        'No.of shipments')

    report.write_header(col_heads)

    for sc in scs:
        data = bag_exception_inbound_origin(sc.id, date_from_obj, date_to_obj)
        report.write_matrix(data)

    file_name = report.manual_sheet_close()
    return file_name

def bag_exception_outbound_origin(origin_obj, date_from_obj, date_to_obj):
    connections = Connection.objects.filter(
        origin=origin_obj, added_on__range=(date_from_obj, date_to_obj))
    data = []
    for conn in connections:
        bags = conn.bags.filter(
            Q(hub=conn.destination) | Q(destination=conn.destination),
            ~Q(current_sc=conn.destination), Q(bag_status=2)|Q(bag_status=7))
        for bag in bags:
            if bag.connection_set.latest('id').id != conn.id:
                continue

            bag_history = get_bag_history(bag).filter(Q(status=15) &
                    Q(bag_sc=conn.destination))
            if not bag_history:
                ship_count = bag.shipments.filter(
                    status__in=[3,5]
                ).exclude(rts_status=2).exclude(status=9).exclude(
                     reason_code__code__in=[111, 777, 999, 888, 333, 310, 200,208, 302,311]
                ).count()
                destination = bag.destination.center_name if bag.destination else ''
                row = (conn.id, bag.bag_number, bag.origin.center_name,
                    destination, conn.added_on, conn.coloader,
                    conn.origin, conn.destination, ship_count)
                data.append(row)
    return data

def bag_exception_outbound_report(origin, date_from, date_to):
    date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').strftime("%Y-%m-%d 00:00:00")
    date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').strftime("%Y-%m-%d 23:59:59")
    if int(origin) == 0:
        scs = ServiceCenter.objects.all()
    else:
        scs = ServiceCenter.objects.filter(id=origin)

    report = ReportGenerator('bag_exception_outbound_{0}.xlsx'.format(date_to))
    col_heads = (
        'Conn Number', 'Bag number', 'Bag origin', 'Bag destination',
        'Conn Date', 'Coloader Name', 'Conn. Origin', 'Conn. Dest',
        'No.of shipments')

    report.write_header(col_heads)
    for sc in scs:
        data = bag_exception_outbound_origin(sc.id, date_from_obj, date_to_obj)
        report.write_matrix(data)

    file_name = report.manual_sheet_close()
    return file_name

def unconnected_bag_report_exception(origin_obj, date_from_obj, date_to_obj):
    bags = Bags.objects.filter(
        Q(bag_status=1) | Q(bag_status=6), connection=None,
        added_on__range=(date_from_obj, date_to_obj)
    ).exclude(bag_number=None)
    data = []
    for bag in bags:
        bag_history = get_bag_history(bag)
        # dont show bag if it is either included in any connection or inscanned at hub / dc
        if not bag_history.filter(Q(status=15) | Q(status=14) | Q(status=4) | Q(status=10)).exists():
            row = (bag.bag_number, bag.added_on, bag.bag_type, bag.origin, bag.destination, bag.hub)
            data.append(row)
    return data

def unconnected_bag_report(origin, date_from, date_to):
    date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').strftime("%Y-%m-%d 00:00:00")
    date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').strftime("%Y-%m-%d 23:59:59") 
    if int(origin) == 0:
        scs = ServiceCenter.objects.all()
    else:
        scs = ServiceCenter.objects.filter(id=origin)

    report = ReportGenerator('unconnected_bag_report_{0}.xlsx'.format(date_to))
    col_heads = ('Bag no', 'Created on', 'Bag Type', 'Bag origin', 'Bag destination', 'Hub')

    report.write_header(col_heads)
    for sc in scs:
        data = unconnected_bag_report_exception(sc.id, date_from_obj, date_to_obj)
        report.write_matrix(data)

    file_name = report.manual_sheet_close()
    return file_name

def bag_inscan_unconnected(sc_id, date_from_obj, date_to_obj):
    year_month = datetime.datetime.strptime(date_to_obj, '%Y-%m-%d').date().strftime('%Y_%m')
    bag_history = get_model('delivery', 'BaggingHistory_%s'%(year_month))
    date_from = datetime.datetime.strptime(date_from_obj, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
    date_to = datetime.datetime.strptime(date_to_obj, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')

    # dont show bag if it is either included in any connection or inscanned at hub / dc
    history = bag_history.objects.filter(
        updated_on__range=(date_from, date_to), bag_sc_id=sc_id,
        status=15, bag__bag_status=3, bag__connection=None
    ).exclude(status=14).exclude(bag__bag_number=None)

    #bags = Bags.objects.filter(
        #bag_status=3, connection=None,
        #added_on__range=(date_from_obj, date_to_obj)
    #).exclude(bag_number=None)
    data = []
    for bh in history:
        if bh.bag.shipments.count() == 0:
            continue

        scanned_sc = bh.bag_sc
        scanned_date = bh.updated_on
        row = (bh.bag.added_on, bh.bag.bag_number, scanned_sc, scanned_date, 
               bh.bag.origin, bh.bag.destination, bh.bag.shipments.count())
        data.append(row)
    return data

def bag_inscan_unconnected_report(origin, date_from, date_to):
    if int(origin) == 0:
        scs = ServiceCenter.objects.all()
    else:
        scs = ServiceCenter.objects.filter(id=origin)

    report = ReportGenerator('bag_inscan_unconnected_report_{0}.xlsx'.format(date_to))
    col_heads = ('Created on', 'Bag No', 'Inscanned locn', 'Inscanned Date', 'Origin',
                 'Destination', 'Shipment count')

    report.write_header(col_heads) 
    for sc in scs:
        data = bag_inscan_unconnected(sc.id, date_from, date_to)
        report.write_matrix(data)

    file_name = report.manual_sheet_close()
    return file_name


def bag_hub_inscan_report(hub, from_date, to_date):
    year_month = datetime.datetime.strptime(to_date, '%Y-%m-%d').date().strftime('%Y_%m')
    bag_history = get_model('delivery', 'BaggingHistory_%s'%(year_month))
    date_from_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
    date_to_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')
    report = ReportGenerator('bag_hub_inscan_report_{0}.xlsx'.format(to_date))
    report.write_header(('Bag Number', 'Inscanned Date', 'Origin', 'Hub', 'Destination', 'Connection Time'))

    # dont show bag if it is either included in any connection or inscanned at hub / dc
    history = bag_history.objects.filter(
        updated_on__range=(date_from_obj, date_to_obj), bag_sc_id=hub, status__in=[15, 14]
    ).exclude(bag__bag_number=None)

    data = []
    for bh in history:
        scanned_sc = bh.bag_sc
        scanned_date = bh.updated_on
        bag = bh.bag
        #conn_time = bag.connection_set.filter(origin=hub).latest('id').added_on
        conn_hist = bag_history.objects.filter(bag=bag, bag_sc_id=hub, status=6)
        if conn_hist:
            conn_time = conn_hist.latest('updated_on').updated_on
            if conn_time < scanned_date:
                conn_time = ''
        else:
            conn_time = ''
        row = (bag.bag_number, scanned_date, bag.origin, bag.hub, bag.destination, conn_time)
        report.write_row(row)

    file_name = report.manual_sheet_close()
    return file_name
