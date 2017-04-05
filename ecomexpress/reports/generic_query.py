import pdb
import os
import datetime

from django.db.models import get_model

from service_centre.models import Shipment, get_internal_shipment_status, StatusUpdate
from reports.report_api import CSVReportGenerator
from reports.ecomm_mail import ecomm_send_mail


def generic_query(date_str, multiple=True):
    end_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    startdate = end_date.strftime('%Y-%m-01')
    start_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
    year_month = end_date.strftime('%Y_%m')


    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(year_month))
    col_heads = ("Air Waybill No","Order No", "Product Type", "Weight", "Vol Weight", "COD Amount", "Declared Value", # 1-6
         "Origin", "Destination", "Vendor", "Shipper", "Consignee", "Contact Number", "P/U Date", "Status", "Expected Date", #7-15
         "Updated Date", "Remarks", "Reason Code", "Reason", "Received by", "Del Date", "Del Time", "New Air Waybill (RTS)", #16-23
         "Return Status", "Updated on", "RTS Status", "RTO Status","PRUD_DATE", "FRST_ATMPTD_UDSTATUS", "FRST_ATMPT_DATE") #24-30

    #common report
    #report = CSVReportGenerator('generic_query_{0}.csv'.format(year_month))
    #report.write_row(col_heads)
    if multiple:
        # Actolingerie: 47
        act_report = CSVReportGenerator('actolingeie_generic_query_{0}.csv'.format(year_month))
        act_report.write_row(col_heads)
        # WS Retails: 92
        ws_report = CSVReportGenerator('ws_retail_generic_query_{0}.csv'.format(year_month))
        ws_report.write_row(col_heads)
        # TV18 : 7
        tv_report = CSVReportGenerator('tv18_generic_query_{0}.csv'.format(year_month))
        tv_report.write_row(col_heads)
        # Jasper: 6
        jas_report = CSVReportGenerator('jasper_generic_query_{0}.csv'.format(year_month))
        jas_report.write_row(col_heads)

    while start_date <= end_date:
        date_str = start_date.strftime('%Y-%m-%d')
        start_date += datetime.timedelta(days=1)

        shipments = list(Shipment.objects.using('local_ecomm')\
            .filter(added_on__range=(date_str+' 00:00:00', date_str+' 23:59:59'), shipper__id__in=[6,7,47,92])\
            .values('airwaybill_number', 'order_number', 'product_type', 'actual_weight', 'volumetric_weight',
                'collectable_value', 'declared_value', 'pickup__service_centre__center_name',
                'original_dest__center_name', 'shipper__id', 'shipper__name', 'pickup__subcustomer_code__name',
                'consignee', 'mobile', 'added_on', 'status', 'expected_dod', 'ref_airwaybill_number', 
                'rts_status', 'rto_status', 'return_shipment', 'reason_code_id', 'reason_code__code'))

        for shipment in shipments:
            airwaybill_number = shipment.get('airwaybill_number')
            order_no = shipment.get('order_number')
            product_type = shipment.get('product_type')
            weight = shipment.get('actual_weight')
            vol_weight = shipment.get('volumetric_weight')
            cod_amount = shipment.get('collectable_value')
            declared_value = shipment.get('declared_value')
            origin = shipment.get('pickup__service_centre__center_name')
            destination = shipment.get('original_dest__center_name')
            vendor = shipment.get('shipper__name')
            shipper = shipment.get('pickup__subcustomer_code__name')
            consignee = shipment.get('consignee')
            contact_number = shipment.get('mobile')
            pu_date = shipment.get('added_on')
            status = shipment.get('status')
            expected_date = shipment.get('expected_dod')
            rts_status = shipment.get('rts_status')
            rto_status = shipment.get('rto_status')
            ref_airwaybill_number = shipment.get('ref_airwaybill_number')
            reason_code_id = shipment.get('reason_code_id')
            reason_code = shipment.get('reason_code__code')
            return_shipment = shipment.get('return_shipment')
            customer = shipment.get('shipper__id')

            ship_status = ''
            updated_date = ''
            remarks = ''
            reason = ''
            recieved_by = ''
            del_date = ''
            del_time = ''
            return_status = ''
            ref_updated_on = ''
            prud_date = ''
            first_attempt_date = ''
            first_attempt_status = ''

            history = shipment_history.objects.using('local_ecomm')\
                    .filter(shipment__airwaybill_number=airwaybill_number).order_by('-updated_on')\
                    .values('status', 'updated_on', 'reason_code__code', 'remarks',
                        'reason_code__code_description', 'current_sc__center_name')

            status_updates = StatusUpdate.objects.using('local_ecomm')\
                    .filter(shipment__airwaybill_number=airwaybill_number).order_by('-added_on')\
                    .values('status', 'added_on', 'reason_code__code', 'remarks',
                        'reason_code__code_description', 'date', 'time', 'recieved_by')

            history_exists = history.exists()
            su_exists = status_updates.exists()

            # product_type
            if str(airwaybill_number)[0] in ['1', '7']:
                pass
            elif str(airwaybill_number)[0] == '3':
                product_type = 'ebsppd'
            elif str(airwaybill_number)[0] == '4':
                product_type = 'ebscod'
            elif str(airwaybill_number)[0] == '5':
                product_type = 'ebsrev'

            # get updated_date
            if history_exists:
                updated_date = history[0].get('updated_on').strftime('%Y-%m-%d')

            # status
            if rts_status or rto_status or return_shipment == 3 or reason_code_id == 5:
                ship_status = "Returned"
            else:
                ship_status = get_internal_shipment_status(status)

            # reason_code and reason, received_by
            if su_exists:
                reason_code = status_updates[0].get('reason_code__code')
                reason = status_updates[0].get('reason_code__code_description')
                recieved_by = status_updates[0].get('recieved_by')
            elif history_exists:
                reason_code = history[0].get('reason_code__code')
                reason = history[0].get('reason_code__code_description')

            # get del_date, del_time, prud_date, first_attempt_date, first_attempt_status and update remarks
            if su_exists:
                if status_updates.count() > 1:
                    prud_date = status_updates[1].get('added_on')
                else:
                    prud_date = status_updates[0].get('added_on')

                del_date = status_updates[0].get('date')
                del_time = status_updates[0].get('time')
                first_attempt_date = status_updates.order_by('added_on')[0].get('date')
                first_attempt_status = status_updates.order_by('added_on')[0].get('reason_code__code_description')

            # if reason code among following then swap remarks with status
            if reason_code in [207, 230, 303, 304, 309]:
                ship_status = 'Intransit'
                h = history.filter(status__in=[3,5])
                if h.exists():
                    hremarks = h[0].get('remarks')
                    current_sc = h[0].get('current_sc__center_name')
                    bag = hremarks.split('. ')[1][:3]
                    remarks = "Shipment Connected to {0} from {1}".format(bag, current_sc)
            elif reason_code in [200, 206, 208, 302, 311, 888]:
                reason, ship_status = ship_status, reason
            elif reason_code == 333:
                ship_status = 'Shipment Lost'

            # get remarks
            if remarks:
                pass
            elif su_exists:
                rem_status = status_updates[0].get('status')
                if rem_status == 2:
                    remarks = 'Delivered'
                else:
                    remarks = status_updates[0].get('remarks')
            elif history_exists:
                remarks = history[0].get('remarks')

            # return_status and ref_updated_on
            if ref_airwaybill_number:
                try:
                    ref_ship = Shipment.objects.using('local_ecomm').get(airwaybill_number=ref_airwaybill_number)
                    ref_rts_status = ref_ship.rts_status
                    if ref_rts_status == 2:
                        return_status = 'Returned'
                    else:
                        ref_status = ref_ship.status
                        return_status = get_internal_shipment_status(ref_status)

                    # get ref_updated_on
                    ref_ship_added_on = ref_ship.added_on.strftime('%Y_%m')
                    ref_shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(ref_ship_added_on))
                    ref_history = ref_shipment_history.objects.using('local_ecomm')\
                            .filter(shipment=ref_ship).order_by('-updated_on').values('updated_on')
                    if ref_history.exists():
                        ref_updated_on = ref_history[0].get('updated_on').strftime('%Y-%m-%d')
                except Shipment.DoesNotExist:
                    pass
            else:
                ref_airwaybill_number = ''

            # convert dates to string
            if pu_date:
                pu_date = pu_date.strftime('%Y-%m-%d')
            if expected_date:
                expected_date = expected_date.strftime('%Y-%m-%d')

            row_data = (airwaybill_number, order_no, product_type, weight, vol_weight, cod_amount,
                declared_value, origin, destination, vendor, shipper, consignee, contact_number,
                pu_date, ship_status, expected_date, updated_date, remarks, reason_code, reason, recieved_by,
                del_date, del_time, ref_airwaybill_number, return_status, ref_updated_on, rts_status,
                rto_status, prud_date, first_attempt_status, first_attempt_date)
            #report.write_row(row_data)

            if multiple:
                if customer == 6:
                    # Jasper: 6
                    jas_report.write_row(row_data)
                elif customer == 7:
                    # TV18 : 7
                    tv_report.write_row(row_data)
                elif customer == 92:
                    # WS Retails: 92
                    ws_report.write_row(row_data)
                elif customer == 47:
                    # Actolingerie: 47
                    act_report.write_row(row_data)

    files_list = []
    #report.write_row(['','','','','','','','','','',''])
    #file_name = report.get_file_path()
    #compressed_file = report.compress_file()
    #files_list.append(compressed_file)
    if multiple:
        jas_report.write_row(['','','','','','','','','','',''])
        tv_report.write_row(['','','','','','','','','','',''])
        ws_report.write_row(['','','','','','','','','','',''])
        act_report.write_row(['','','','','','','','','','',''])
        jas = jas_report.compress_file()
        tv = tv_report.compress_file()
        ws = ws_report.compress_file()
        act = act_report.compress_file()
        files_list.extend([act, ws, tv, jas])
    return files_list

def email_generic_query(prev_month=False):

    curr_date = datetime.datetime.today() - datetime.timedelta(days=1)
    if prev_month:
        prev_month_last_date = curr_date - datetime.timedelta(days=curr_date.day)
        report_date = prev_month_last_date.strftime('%Y-%m-%d')
        month = prev_month_last_date.strftime('%B')
    else:
        report_date = curr_date.strftime('%Y-%m-%d')
        month = curr_date.strftime('%B')
    month="April"
    base_url = 'http://cs.ecomexpress.in/'
    files_list=generic_query("2014-04-30")
    #files_list = generic_query(report_date)
    files = [ base_url + 'static/uploads/reports/' + os.path.split(f)[1] for f in files_list]

    content = """Dear Team,

    Please find the link below of Generic Query for shipments for {4}.The shipments marked as 1 in rts status are secondary airwaybills (the one that are marked as red in original sheet) whereas those marked as 2 are primary airwaybills and 0 are normal airwaybills, similarly shipments marked as 1 in rto status are rto airwaybills(marked as blue), and 0 are normal.

     Actolingerie: {0}
     WS Retail: {1}
     TV18: {2}
     Jasper: {3}""".format(files[0], files[1], files[2], files[3], month)

    to_email = ("sunainas@ecomexpress.in","shilpaa@ecomexpress.in","veenav@ecomexpress.in", "jaideeps@ecomexpress.in", "jignesh@prtouch.com", "sravank@ecomexpress.in", "rajeshwars@ecomexpress.in", "vaibhavk@ecomexpress.in", "rsinha@ecomexpress.in", "balwinders@ecomexpress.in", "kavitac@ecomexpress.in", "mukundh@ecomexpress.in", "shalinia@ecomexpress.in", "shwethaj@ecomexpress.in", "onkar@prtouch.com", "samar@prtouch.com", "jinesh@prtouch.com", "sandeepc@ecomexpress.in", "rameshw@ecomexpress.in", "nitashaa@ecomexpress.in")
    #to_email = ("samar@prtouch.com","jinesh@prtouch.com", "sravank@ecomexpress.in")

    ecomm_send_mail('Generic Query {0}'.format(month), '', to_email, content)
