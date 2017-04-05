import calendar
import datetime

from django.db.models import Count
from service_centre.models import ServiceCenter, Shipment, ShipmentStatusMaster, StatusUpdate
from reports.report_api import ReportGenerator

def generate_sunday_report():
    now = datetime.datetime.now()
    report = ReportGenerator('sunday_delivery_report_{0}.xlsx'.format(now.strftime('%Y-%m-%d')))
    col_list =['Service Center']
    year = now.year
    month = now.month
    day = now.day
    sunday_date_list = []
    
    # update sunday list if day 1 on month is monday
    if day == 1:
        month = month - 1
        if month == 0:
            year = year - 1
            month = 12
        sunday_date_list = [i[6] for i in calendar.monthcalendar(year, month) if i[6] != 0]
    else:
        sunday_date_list = [i[6] for i in calendar.monthcalendar(year, month) if i[6] != 0]
    
    body = []
    sunday_date_list_copy = sunday_date_list
    active_sundays = [x for x in sunday_date_list if x <= day]
    for date in active_sundays:
        d = str(year)+'-'+str(month)+'-'+str(date)
        col_list.append(d)
    col_heads = tuple(col_list)
    st_up = StatusUpdate.objects.filter(date__in = col_list[1:], status=2)
    data = st_up.values('origin__center_name', 'date').annotate(ct=Count('id'))
    service_list = ServiceCenter.objects.all()
    count_li =[0 for i in active_sundays]
    sc_dict ={}
    for se in service_list:
        lis = [se.center_name] + count_li
        sc_dict[se.center_name] = lis
    for d in data:
        da = d['date']
        index = sunday_date_list.index(da.day) + 1
        sc_dict[d['origin__center_name']][index] = d['ct']
    for se in service_list:
        body.append(sc_dict[se.center_name])
    report.write_header(col_heads)
    path = report.write_body(body)
    return path
	
