import datetime
from django.db.models import get_model, Q, Count, Sum

from service_centre.models import Bags, Connection
from reports.report_api import ReportGenerator, CSVReportGenerator


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

def generate_bagging_report(date_from, date_to):
    date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').strftime("%Y-%m-%d 00:00:00")
    date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').strftime("%Y-%m-%d 23:59:59")
    year_month = datetime.datetime.strptime(date_to, '%Y-%m-%d').strftime('%Y_%m')
    bag_history = get_model('delivery', 'BaggingHistory_%s'%(year_month))

    #report = ReportGenerator('bagging_report_{0}.xlsx'.format(date_to))
    report = CSVReportGenerator('bagging_report_{0}.csv'.format(date_to))

    col_heads = (
            'Bag Number', 'Bag Created Service Center',
            'Hub selected', 'Destination Selected', 'Status', 
            'Bag Inscanned Location', 'Bag Creation Date', 
            'Bag Inscan Date', 'Connection Date', 
            'Connected From', 'Massupdate Reason',
            'Total Shipments', 'Total Scanned')

    #report.write_header(col_heads)
    report.write_row(col_heads)
    bags = Bags.objects.using('local_ecomm').filter(added_on__range=(date_from_obj, date_to_obj))\
            .values('bag_number', 'bag_status', 'origin__center_name', 'hub__center_name', 
                    'current_sc__center_name', 'updated_on', 'destination__center_name', 'added_on')

    for bag in bags:
        # get connection details
        try:
            connection = Connection.objects.using('local_ecomm').filter(bags__bag_number=bag.get('bag_number')).latest('id')
            conn_origin = connection.origin
            conn_date = connection.added_on
        except Connection.DoesNotExist:
            conn_origin = ''
            conn_date = ''

        # get inscan date and inscanned sc
        try:
            bh = bag_history.objects.using('local_ecomm').filter(
                Q(status=14) | Q(status=15) | Q(status=17) | Q(status=18), 
                bag__bag_number=bag.get('bag_number')).latest('id')
            inscan_date = bh.updated_on
            inscan_sc = bh.bag_sc
        except bag_history.DoesNotExist:
            inscan_date = '' # bag.get('updated_on')
            inscan_sc = '' # bag.get('current_sc__center_name')

        # mass updated column
        try:
            bh = bag_history.objects.using('local_ecomm').filter(status=16, bag__bag_number=bag.get('bag_number')).latest('id')
            mass_updation = bh.reason_code
        except bag_history.DoesNotExist:
            mass_updation = ''

        # get total count and scanned count
        total = 0
        scanned = 0
        if  bag.get('bag_number'):
            try:
                original_bag = Bags.objects.get(bag_number=bag.get('bag_number'))
                total = original_bag.ship_data.aggregate(s=Count('id'))['s']
                scanned = original_bag.ship_data.filter(status__in=[4,6,7,8,9]).aggregate(s=Count('id'))['s']
                total = total if total else 0
                scanned = scanned if scanned else 0
            except: #  (Bags.DoesNotExist, MultipleObjectsReturned) as e:
                pass

        row = (bag.get('bag_number'), bag.get('origin__center_name'), 
               bag.get('hub__center_name'), bag.get('destination__center_name'), 
               bag_status_dict.get(bag.get('bag_status'), ''), inscan_sc, 
               bag.get('added_on'), inscan_date, conn_date, 
               conn_origin, mass_updation, total, scanned)
        report.write_row(row)

    file_name = report.file_name
    return file_name
