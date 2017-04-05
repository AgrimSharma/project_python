import datetime
from collections import defaultdict

from service_centre.models import Shipment, get_internal_shipment_status, StatusUpdate
from ecomm_admin.models import ChangeLogs
from reports.report_api import ReportGenerator


def generate_correction_report(date_from, date_to):
    if date_to:
        report = ReportGenerator('correction_report{0}.xlsx'.format(date_to))
    else:
        report = ReportGenerator('correction_report.xlsx')

    # report column headings
    col_heads = ('Sr No',
        'AWB No', #1
        'Original Deliveries Date', #2
        'Shipper Code', #3
        'Dest Centre', #4
        'COD dues', #5
        'Change Status', #6
        'Remittance Status', #7
        'Correction Date', #8
        'Previous  Status', #9
        'Current Status', #10 shipment current status
        'Correction By', #11
        'Employee ID') #12

    # get data with in the date range
    if not (date_from and date_to):
        date_from, date_to = report.current_month_range()

    date_from_time = datetime.datetime.strptime(date_from, "%Y-%m-%d")
    date_from_time_str = datetime.datetime.strftime(date_from_time, '%Y-%m-%d 00:00:00')
    date_to_time = datetime.datetime.strptime(date_to, "%Y-%m-%d")
    date_to_time_str = datetime.datetime.strftime(date_to_time, '%Y-%m-%d 23:59:59')

    cls = ChangeLogs.objects.get_shipment_changes().\
            filter(updated_on__range=(date_from_time_str, date_to_time_str)).values_list('id',
                'field_name', 'remittance_status', 'updated_on', 'status_intime',
                'user__employeemaster__firstname', 'user__employeemaster__employee_code',
                'object_id', 'change_message')

    # preparing data to print in excel in the order of column headings
    data = []
    ind = 0
    for cl in cls:
        ship = Shipment.objects.get(id=cl[7])
        if ship.status != 9:
            continue
        remt_status = ship.codcharge_set.all().get().remittance_status if ship.codcharge_set.exists() else None

        if ship.product_type == 'ppd':
            rem_status = 'ppd'
        elif ship.rts_status == 1:
            rem_status = 'rts'
        elif remt_status == 1:
            rem_status = 'yes'
        else:
            rem_status = 'no'

        su = ship.statusupdate_set.all().order_by('-added_on')
        prev_status = ChangeLogs.objects.get_previous_value(ship, cl[1])
        if prev_status == cl[8]:
             continue
        try:
            curr_status = ship.__dict__[cl[1]]
        except KeyError:
            curr_status = ship.__dict__[cl[1]+'_id']
        #if su.exists():
            #curr_status = su[0].reason_code
        #if su.count() > 1:
            #prev_status = su[1].reason_code

        dsc = ship.original_dest.center_shortcode if ship.original_dest else ''
        del_date = su.filter(reason_code__code=999)[0].added_on.strftime('%Y-%m-%d') if su.filter(reason_code__code=999).exists() else ''

        ind += 1
        data.append([ind, ship.airwaybill_number, del_date, ship.shipper.code, dsc,
                    ship.collectable_value, cl[1], rem_status, cl[3].date(), prev_status, curr_status, cl[5], cl[6]])

    status_updates = StatusUpdate.objects.filter(date__range=(date_from, date_to)).filter(reason_code__code='202')
    for su in status_updates:
        ship = su.shipment
        sus = ship.statusupdate_set.all().order_by('-added_on')
        pos = 0
        for st in sus:
            if st.reason_code.code == 202:
                break
            else:
                pos += 1

        prev_status = ''

        if pos+1 < sus.count():
            prev_status = sus[pos+1]
            if prev_status.reason_code.code != 999:
                continue
        else:
            continue

        curr_status = ''
        curr_status = su.reason_code
        remt_status = ship.codcharge_set.all().get().remittance_status if ship.codcharge_set.exists() else None

        if ship.product_type == 'ppd':
            rem_status = 'ppd'
        elif ship.rts_status == 1:
            rem_status = 'rts'
        elif remt_status == 1:
            rem_status = 'yes'
        else:
            rem_status = 'no'

        emp = su.data_entry_emp_code
        emp_name = emp.firstname
        emp_id = emp.pk

        dsc = ship.original_dest.center_shortcode if ship.original_dest else ''
        del_date = prev_status.added_on.strftime('%Y-%m-%d') if prev_status else ''
        upd_on = su.added_on.strftime('%Y-%m-%d')
        if del_date == upd_on:
            continue

        ind += 1
        data.append([ind, ship.airwaybill_number, del_date, ship.shipper.code, dsc,
                    ship.collectable_value, 'status', rem_status, upd_on, prev_status.reason_code, curr_status, emp_name, emp_id])
    # create a report object and write headers
    report.write_header(col_heads)

    #write data to report
    path = report.write_body(data)
    return path
