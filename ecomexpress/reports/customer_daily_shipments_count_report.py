import calendar
import datetime
from collections import defaultdict
from django.db.models import Sum
from customer.models import Customer
from reports.models import DaywiseCustomerReport
from reports.report_api import ReportGenerator


def generate_report():
    today = datetime.datetime.today()
    start_day = datetime.date(today.year, today.month, 01)
    today_str = today.strftime('%Y-%m-%d')
    file_name = 'customer_daily_shipment_count_{0}.xlsx'.format(today_str)

    month_range = calendar.monthrange(today.year, today.month)
    col_heads = ('Code' ,'Customer Name') + tuple(reversed(range(1, today.day)))
    report = ReportGenerator(file_name)
    report.write_header(col_heads)

    # for each day fill customer day shipment count list
    # structure : {'customer_code':[day1_count, day2_count]}
    end_day = today - datetime.timedelta(1)
    data_rows = list(DaywiseCustomerReport.objects.filter(shipment_date__range=(start_day, end_day))\
                       .values('code', 'name', 'shipment_date').annotate(ship_count=Sum('shipment_count')))

    customer_wise_shipment_count = defaultdict(list)
    customer_codes = list(Customer.objects.using('local_ecomm').values_list('code', 'name'))

    for code, name in customer_codes:
        customer_wise_shipment_count[code] = [name] + [0] * (today.day - 1)

    lastindex = end_day.day+1
    for row in data_rows:
        ind = row['shipment_date'].day
        ind = lastindex - ind
        code = row['code']
        ship_count = row['ship_count'] if row['ship_count'] else 0
        customer_wise_shipment_count[code][ind] = ship_count

    data_matrix = []
    for k, v in customer_wise_shipment_count.items():
        row = [k]
        row.extend(v)
        data_matrix.append(row)

    total_ships_list = list(DaywiseCustomerReport.objects.filter(shipment_date__range=(start_day, end_day))\
                       .values('shipment_date').annotate(ship_count=Sum('shipment_count')))

    total_row = [0] * (today.day + 1)
    lastindex = end_day.day+1
    for data in total_ships_list:
        ind = lastindex - data['shipment_date'].day + 1
        total_row[ind] = data['ship_count']
    total_row[1] = 'Grand Total'
    data_matrix.append(total_row)
    path = report.write_body(data_matrix)
    return path
