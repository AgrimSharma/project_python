import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from datetime import timedelta, datetime
from xlsxwriter.workbook import Workbook

from django.db.models import Q, Sum, Count
from django.conf import settings

from service_centre.models import Shipment, RemittanceCODCharge,\
    get_internal_shipment_status
from ecomm_admin.models import ShipmentStatusMaster
from customer.models import Customer, Remittance


def get_status_code(code, data_list):
    for d in data_list:
        if d.get('reason_code__code') == code:
            return d
    return {}

def convert_to_unicode(in_str):
    try:
        value = unicode(in_str, "ascii")
    except UnicodeError:
        value = unicode(in_str)
    else:
        value = str(in_str)
    return value
    #if isinstance(in_str, unicode):
        #return in_str.encode('utf-8')
    #else:
        #return str(in_str)

def get_reconciliation_query(date_from, date_to, cust_id):
    q = Q()

    if not cust_id == "0":
        q = q & Q(shipper__id=int(cust_id))
    if date_from and date_to:
        q = q & Q(shipment_date__gte=date_from, shipment_date__lte=date_to)
    elif date_from:
        q = q & Q(shipment_date__gte=date_from)
    elif date_to:
        q = q & Q(shipment_date__lte=date_to)

    # gather data to display
    # get all shipments ans ppd,cod shipments seperately
    return q

def get_remittance_query(date_from, date_to, cust_id):
    q = Q()

    if not cust_id == "0":
        q = q & Q(customer__id=cust_id)

    if date_from and date_to:
        q = q & Q(remittancecodcharge__codcharge__shipment__shipment_date__gte=date_from)
        q = q & Q(remittancecodcharge__codcharge__shipment__shipment_date__lte=date_to)
    elif date_from:
        q = q & Q(remittancecodcharge__codcharge__shipment__shipment_date__gte=date_from)
    elif date_to:
        q = q & Q(remittancecodcharge__codcharge__shipment__shipment_date__lte=date_to)

    q = q & Q(remittancecodcharge__codcharge__remittance_status=1)
    return q

def get_main_sheet_data(date_from, date_to, cust_id):
    q = get_reconciliation_query(date_from, date_to, cust_id)
    shipments = Shipment.objects.filter(q).exclude(rts_status=1)
    ppd_shipments = shipments.filter(product_type='ppd')
    cod_shipments = shipments.filter(product_type='cod')

    # get data for 'shipments booked' header
    shipments_booked_dict = {
        'ppd_shipments': ppd_shipments.count(), # total ppd shipments
        'cod_shipments': cod_shipments.count(), # total cod shipments
        'collectable_value': shipments.aggregate(Sum('collectable_value'))['collectable_value__sum'] # total collectable value
    }

    # get data to display in status code section
    # group ppd,cod shipments based on reason_code and annotate count of
    # reason_code and sum of collectable value
    # output format: [{'reason_code__code': 999L,
    #                  'collectable_sum': 538185.0,
    #                  'status_count': 158}, ..]
    cod_ships_list = cod_shipments.values('reason_code__code').\
            annotate(collectable_sum = Sum('collectable_value'), status_count=Count('reason_code'))

    ppd_ships_list = ppd_shipments.values('reason_code__code').\
            annotate(collectable_sum = Sum('collectable_value'), status_count=Count('reason_code'))

    # get all unique status codes
    ppd_status = [d['reason_code__code'] for d in ppd_ships_list]
    cod_status = [d['reason_code__code'] for d in cod_ships_list]
    all_status = set(ppd_status + cod_status)

    # status code section data list
    # format: [{'status_code':999,
    #           'Description':'blah blah',
    #           'ppd shipmnts':122,
    #           'cod shipmnts: 778,
    #           'collectable value':7979799.00},...]

    status_code_data_list = []
    sub_total_dict = {
        'ppd':0,
        'cod':0,
        'cv':0
    }

    net_payable_dict = {
        'ppd':0,
        'cod':0,
        'cv':0
    }


    for status in all_status:
        if status is None:
            continue
        ppd_dict = get_status_code(status, ppd_ships_list)
        ppd_shipments = ppd_dict.get('status_count', 0)
        ppd_collectable_sum = ppd_dict.get('collectable_sum', 0)

        cod_dict = get_status_code(status, cod_ships_list)
        cod_shipments = cod_dict.get('status_count', 0)
        cod_collectable_sum = cod_dict.get('collectable_sum', 0)

        cv = cod_collectable_sum + ppd_collectable_sum

        status_code_data_list.append({
            'code':status,
            'desc':ShipmentStatusMaster.objects.get(code=status).code_description,
            'ppd':ppd_shipments,
            'cod':cod_shipments,
            'cv': cv
        })

        sub_total_dict['ppd'] += ppd_shipments
        sub_total_dict['cod'] += cod_shipments
        sub_total_dict['cv'] += cv

        if status in [333,999]:
            net_payable_dict['ppd'] += ppd_shipments
            net_payable_dict['cod'] += cod_shipments
            net_payable_dict['cv'] += cv

    # Remittance table data
    qr = get_remittance_query(date_from, date_to, cust_id)
    remittance_list = Remittance.objects.filter(qr).\
        values("remitted_on", "id", "bank_ref_number").\
            annotate(total_amount=Sum('remittancecodcharge__codcharge__remitted_amount'),
                     shipts_count=Count('remittancecodcharge__codcharge__shipment')).\
            order_by('remittancecodcharge__added_on')

    return (shipments_booked_dict,
            status_code_data_list,
            sub_total_dict,
            net_payable_dict,
            remittance_list)

def generate_reconciliation_excel(date_from, date_to, cust_id):
    print 'start reconciliation stmt..'
    main_sheet_data = get_main_sheet_data(date_from, date_to, cust_id)
    cust_name = Customer.objects.get(pk=int(cust_id)).name if int(cust_id) != 0 else 'All Customers'
    header_dict = {
       'date_from': date_from,
       'date_to': date_to,
       'customer_name': cust_name}

    # add filename and set save file path
    file_name = "/reconciliation_stmt_%s.xlsx"%(datetime.now().strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#cccccc'})
    #header_format.set_bg_color('#cccccc')
    #header_format.set_bold()

    # Create a format to use in the merged range.
    merge_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'yellow'})

    plain_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter'})

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    shipments_booked_dict = main_sheet_data[0]
    status_code_data_list = main_sheet_data[1]
    sub_total_dict = main_sheet_data[2]
    net_payable_dict = main_sheet_data[3]
    remittance_list = main_sheet_data[4]

    sheet.set_column(0, 5, 12) # set column width
    # write statement headers: statement name, customer name, and date
    print ' write statement headers: statement name, customer name, and date'
    sheet.merge_range('A1:E1', 'Reconciliation Statement')
    sheet.merge_range('A2:E2',
        header_dict.get('customer_name'),
        merge_format) # write to first 5 columns
    sheet.write(2, 0, "From")
    sheet.write(2, 1, header_dict.get('date_from'))
    sheet.write(2, 2, "To")
    sheet.write(2, 3, header_dict.get('date_to'))

    # write main column headers
    print ' write main column headers'
    sheet.write(4, 0, "Particulars", plain_format)
    sheet.write(4, 1, "", plain_format)
    sheet.write(4, 2, "PPD Shpmts", plain_format)
    sheet.write(4, 3, "COD Shpmts", plain_format)
    sheet.write(4, 4, "Collectable Value", plain_format)

    # write shipments booked header
    sheet.write(5,0, "Shipments Booked", header_format)
    sheet.write(5,1, "", header_format)
    sheet.write(5,2, shipments_booked_dict['ppd_shipments'], header_format)
    sheet.write(5,3, shipments_booked_dict['cod_shipments'], header_format)
    sheet.write(5,4, shipments_booked_dict['collectable_value'], header_format)
    sheet.write(5,5, "Ref: Sheet2", header_format)

    # write status code section data
    sheet.write(6,0, "Status Code")
    sheet.write(6,1, "Description")
    row_count = 7

    code_sheet_ref = {'200':'Ref:Sheet3',
                      '0':'Ref:Sheet4',
                      '333':'Ref:Sheet5',
                      '999':'Ref:Sheet7',
                      '777':'Ref:Sheet6'}
    for d in status_code_data_list:
        c = d.get('code')
        print 'status code ..',c
        ref = code_sheet_ref.get(str(c), '')
        sheet.write(row_count, 0, c)
        sheet.write(row_count, 1, d.get('desc'))
        sheet.write(row_count, 2, d.get('ppd'))
        sheet.write(row_count, 3, d.get('cod'))
        sheet.write(row_count, 4, d.get('cv'))
        sheet.write(row_count, 5, ref)
        row_count += 1

    row_count += 2
    # write sub total row
    print ' write sub total row..'
    sheet.write(row_count, 0, "", header_format)
    sheet.write(row_count, 1, "Sub Total", header_format)
    sheet.write(row_count, 2, sub_total_dict.get('ppd'), header_format)
    sheet.write(row_count, 3, sub_total_dict.get('cod'), header_format)
    sheet.write(row_count, 4, sub_total_dict.get('cv'), header_format)

    row_count += 2
    # write net payable section (status code 999 and 333)
    for d in status_code_data_list:
        print 'd is ',d
        if d.get('code') not in [333,999]:
            continue
        c = d.get('code')
        ref = code_sheet_ref.get(str(c), '')
        sheet.write(row_count,0,c)
        sheet.write(row_count,1,d.get('desc'))
        sheet.write(row_count,2,d.get('ppd'))
        sheet.write(row_count,3,d.get('cod'))
        sheet.write(row_count,4,d.get('cv'))
        sheet.write(row_count,5,ref)
        row_count += 1

    row_count += 2
    # write sub total row
    sheet.write(row_count, 0, "", header_format)
    sheet.write(row_count, 1, "Total", header_format)
    sheet.write(row_count, 2, net_payable_dict.get('ppd'), header_format)
    sheet.write(row_count, 3, net_payable_dict.get('cod'), header_format)
    sheet.write(row_count, 4, net_payable_dict.get('cv'), header_format)

    # remittance_list : [{
    # 'remittancecodcharge__bank_ref_number': u'13042068097 Dtd. 09.02.2013',
    # 'remittancecodcharge__added_on': datetime.datetime(2013, 5, 12, 13, 17, 20),
    # 'total_amount': 1298.0,
    # 'shipts_count': 1}]
    row_count += 4
    mc = 'A'+str(row_count)+':E'+str(row_count)
    sheet.merge_range(mc, "Amount Remitted", header_format) # write to first 5 columns

    row_count += 1
    sheet.write(row_count, 0, "Sl No", header_format)
    sheet.write(row_count, 1, "Bank Reference Number", header_format)
    sheet.write(row_count, 2, "Date", header_format)
    sheet.write(row_count, 3, "No of Shipts", header_format)
    sheet.write(row_count, 4, "Amount", header_format)
    row_count += 1
    rem_total_ships = 0
    rem_total_amt = 0
    index = 0
    for ind, remit_dict in enumerate(remittance_list, start=1):
        print 'ind ',ind
        sheet.write(row_count, 0, ind, plain_format)
        sheet.write(row_count, 1, remit_dict.get('bank_ref_number'), plain_format)
        sheet.write(row_count, 2, str(remit_dict.get('remitted_on')), plain_format)
        ship_count = remit_dict.get('shipts_count')
        tot_amt = remit_dict.get('total_amount')
        sheet.write(row_count, 3, ship_count, plain_format)
        sheet.write(row_count, 4, tot_amt, plain_format)
        sheet.write(row_count, 5, str('Ref:Sheet7'), plain_format)
        rem_total_ships += ship_count
        rem_total_amt += tot_amt
        row_count += 1
        index = ind

    next_cycle_ships = sub_total_dict.get('cod') - rem_total_ships
    next_cycle_amt = sub_total_dict.get('cv') - rem_total_amt
    sheet.write(row_count, 0, index+1, plain_format)
    sheet.write(row_count, 1, "Remittance to be done in next cycle", plain_format)
    sheet.write(row_count, 3, str(next_cycle_ships), plain_format)
    sheet.write(row_count, 4, str(next_cycle_amt), plain_format)
    sheet.write(row_count, 5, str('Ref:Sheet8'), plain_format)
    row_count += 1
    sheet.write(row_count, 2, 'Total', header_format)
    sheet.write(row_count, 3, sub_total_dict.get('cod'), plain_format)
    sheet.write(row_count, 4, sub_total_dict.get('cv'), plain_format)
    print 'wrote main sheet...'

    # adding sheet 1 data to excel file ----------------------------------
    del main_sheet_data
    q = get_reconciliation_query(date_from, date_to, cust_id)
    q = q & (Q(product_type='cod') | Q(product_type='ppd'))
    sheet1_data = Shipment.objects.filter(q)
    sheet1 = workbook.add_worksheet()
    sheet1_col_heads = (
        'Air Waybill No',
        'PAYMENT REF NO',
        'TEST',
        'NATURE',
        'Order No',
        'Weight',
        'Vol Weight',
        'COD Amount - collectable value',
        'Declared Value',
        'Origin',
        'Destination',
        'Vendor',
        'Shipper',
        'Consignee',
        'Consignee Address',
        'Contact Number',
        'P/U Date',
        'Status',
        'Expected Date',
        'Updated Date',
        'Reason Code',
        'Reason',
        'Received by',
        'Delivery Date',
        'Delivery Time',
        'New Air Waybill (RTS)',
        'Return Status',
        'Updated on',
        'New status',
        'RTS NO')

    sheet1.set_column(0, 29, 15)

    for col, head in enumerate(sheet1_col_heads):
        sheet1.write(1, col, head, header_format)

    for row, ship in enumerate(sheet1_data, start=2):
        print '1 ', row
        sheet1.write(row, 0, str(ship.airwaybill_number), plain_format)
        rem = RemittanceCODCharge.objects.filter(codcharge__shipment__id=ship.id)
        if rem.exists():
            sheet1.write(row, 1, rem[0].bank_ref_number, plain_format)
        else:
            sheet1.write(row, 1, 0, plain_format)
        sheet1.write(row, 2, 0, plain_format)
        sheet1.write(row, 3, str(ship.product_type), plain_format)
        sheet1.write(row, 4, str(ship.order_number), plain_format)
        sheet1.write(row, 5, str(ship.actual_weight), plain_format)
        sheet1.write(row, 6, str(ship.volumetric_weight), plain_format)
        sheet1.write(row, 7, str(ship.collectable_value), plain_format)
        sheet1.write(row, 8, str(ship.declared_value), plain_format)
        sheet1.write(row, 9, str(ship.pickup.service_centre.center_name), plain_format)
        sheet1.write(row, 10, str(ship.original_dest.center_name), plain_format)
        sheet1.write(row, 11, str(ship.pickup.subcustomer_code.name), plain_format)
        sheet1.write(row, 12, str(ship.shipper.name), plain_format)
        try:
            sheet1.write(row, 13, str(ship.consignee), plain_format)
        except:
            sheet1.write(row, 13, '', plain_format)
        #try:
        ad1 = ship.consignee_address1 if ship.consignee_address1 else u''
        ad2 = ship.consignee_address2 if ship.consignee_address2 else u''
        ad3 = ship.consignee_address3 if ship.consignee_address3 else u''
        ad4 = ship.consignee_address4 if ship.consignee_address4 else u''
        address = ad1 + ad2 + ad3 + ad4
        sheet1.write(row, 14, address, plain_format)
        #except:
            #sheet1.write(row, 14, '', plain_format)
        sheet1.write(row, 15, str(ship.mobile), plain_format)
        sheet1.write(row, 16, str(ship.added_on), plain_format)
        sheet1.write(row, 17, get_internal_shipment_status(ship.status), plain_format)
        sheet1.write(row, 18, str(ship.expected_dod), plain_format)
        sheet1.write(row, 19, str(ship.updated_on), plain_format)
        if ship.reason_code:
            sheet1.write(row, 20, str(ship.reason_code.code), plain_format)
            sheet1.write(row, 21, str(ship.reason_code.code_description), plain_format)
        else:
            sheet1.write(row, 20, str(''), plain_format)
            sheet1.write(row, 21, str(''), plain_format)
        try:
            rec_by = ship.statusupdate_set.all()[0].recieved_by
            sheet1.write(row, 22, str(rec_by), plain_format)
        except:
            sheet1.write(row, 22, '', plain_format)

        del_added = ship.deliveryoutscan_set.all().order_by('-added_on')
        del_date = ''
        del_time = ''
        if del_added.exists():
            del_added = del_added[0]
            del_date = del_added.added_on.date()
            del_time = del_added.added_on.time()

        sheet1.write(row, 23, str(del_date), plain_format)
        sheet1.write(row, 24, str(del_time), plain_format)
        ref_awb = ship.ref_airwaybill_number
        sheet1.write(row, 25, str(ref_awb), plain_format)
        ret_status = ''
        ret_upd = ''
        ret_refawb = ''
        if ref_awb:
            rstatus = Shipment.objects.filter(airwaybill_number=ref_awb).\
                    values_list('status', 'updated_on', 'ref_airwaybill_number')
            if rstatus.exists():
                ret_status = rstatus[0][0]
                ret_upd = rstatus[0][1]
                ret_refawb = rstatus[0][2]
        sheet1.write(row, 26, str(ret_status), plain_format)
        sheet1.write(row, 27, str(ret_upd), plain_format)
        sheet1.write(row, 28, '', plain_format)
        sheet1.write(row, 29, str(ret_refawb), plain_format)

    print 'sheet1 finished..'
    #sheet2 data ---------------------------------------------------------
    del sheet1_data
    q = get_reconciliation_query(date_from, date_to, cust_id)
    q = q & Q(reason_code__code=200)
    sheet2_data = Shipment.objects.filter(q)
    sheet2 = workbook.add_worksheet()
    sheet2_col_heads = (
        'Air Waybill No',
        'nature',
        'Order No',
        'Weight',
        'Vol Weight',
        'COD Amount',
        'Declared Value',
        'Origin',
        'Destination',
        'Vendor',
        'Shipper',
        'Consignee',
        'Consignee Address',
        'Contact Number',
        'P/U Date',
        'Status',
        'Expected Date',
        'Updated Date',
        'Remarks',
        'Reason Code',
        'Reason',
        'Received by',
        'Delivery Date',
        'Delivery Time',
        'new status',
        'RTS NO')

    sheet2.set_column(0, 25, 15)

    for col, head in enumerate(sheet2_col_heads):
        sheet2.write(1, col, head, header_format)

    for row, ship in enumerate(sheet2_data, start=2):
        print '2 ', row
        sheet2.write(row, 0, str(ship.airwaybill_number), plain_format)
        sheet2.write(row, 1, str(ship.product_type), plain_format)
        sheet2.write(row, 2, str(ship.order_number), plain_format)
        sheet2.write(row, 3, str(ship.actual_weight), plain_format)
        sheet2.write(row, 4, str(ship.volumetric_weight), plain_format)
        sheet2.write(row, 5, str(ship.collectable_value), plain_format)
        sheet2.write(row, 6, str(ship.declared_value), plain_format)
        sheet2.write(row, 7, str(ship.pickup.service_centre.center_name), plain_format)
        sheet2.write(row, 8, str(ship.original_dest.center_name), plain_format)
        sheet2.write(row, 9, str(ship.pickup.subcustomer_code.name), plain_format)
        sheet2.write(row, 10, str(ship.shipper.name), plain_format)
        try:
            sheet2.write(row, 11, str(ship.consignee), plain_format)
        except:
            sheet2.write(row, 11, '', plain_format)
        ad1 = ship.consignee_address1 if ship.consignee_address1 else u''
        ad2 = ship.consignee_address2 if ship.consignee_address2 else u''
        ad3 = ship.consignee_address3 if ship.consignee_address3 else u''
        ad4 = ship.consignee_address4 if ship.consignee_address4 else u''
        address = ad1 + ad2 + ad3 + ad4
        sheet2.write(row, 12, address, plain_format)
        sheet2.write(row, 13, str(ship.mobile), plain_format)
        sheet2.write(row, 14, str(ship.added_on), plain_format)
        sheet2.write(row, 15, get_internal_shipment_status(ship.status), plain_format)
        sheet2.write(row, 16, str(ship.expected_dod), plain_format)
        sheet2.write(row, 17, str(ship.updated_on), plain_format)
        try:
            sheet2.write(row, 18, str(ship.remark), plain_format)
        except:
            sheet2.write(row, 18, '', plain_format)
        if ship.reason_code:
            sheet2.write(row, 19, str(ship.reason_code.code), plain_format)
            sheet2.write(row, 20, str(ship.reason_code.code_description), plain_format)
        else:
            sheet2.write(row, 19, str(''), plain_format)
            sheet2.write(row, 20, str(''), plain_format)
        try:
            rec_by = ship.statusupdate_set.all()[0].recieved_by
            sheet2.write(row, 21, str(rec_by), plain_format)
        except:
            sheet2.write(row, 21, '', plain_format)
        del_added = ship.deliveryoutscan_set.all().order_by('-added_on')
        del_date = ''
        del_time = ''
        if del_added.exists():
            del_added = del_added[0]
            del_date = del_added.added_on.date()
            del_time = del_added.added_on.time()

        sheet2.write(row, 22, str(del_date), plain_format)
        sheet2.write(row, 23, str(del_time), plain_format)
        ref_awb = ship.ref_airwaybill_number
        ret_status = ''
        if ref_awb:
            rstatus = Shipment.objects.filter(airwaybill_number=ref_awb).\
                    values_list('status')
            if rstatus.exists():
                ret_status = rstatus[0][0]
        sheet2.write(row, 24, str(ret_status), plain_format)
        sheet2.write(row, 25, str(''), plain_format)

    #---------------------------- sheet3
    print 'sheet2 finished..'
    del sheet2_data
    q = get_reconciliation_query(date_from, date_to, cust_id)
    q = q & Q(reason_code__code=0)
    sheet3_data = Shipment.objects.filter(q)
    sheet3 = workbook.add_worksheet()
    sheet3_col_heads = (
        'Air Waybill No',
        'nature',
        'Order No',
        'Weight',
        'Vol Weight',
        'COD Amount',
        'Declared Value',
        'Origin',
        'Destination',
        'Vendor',
        'Shipper',
        'Consignee',
        'Consignee Address',
        'Contact Number',
        'P/U Date',
        'Status',
        'Expected Date',
        'Updated Date',
        'Remarks',
        'Reason Code',
        'Reason',
        'Received by',
        'Del Date',
        'Del Time',
        'New Air Waybill (RTS)',
        'Return Status',
        'Updated on',
        'new status',
        'RTS NO')

    sheet3.set_column(0, 28, 15)

    for col, head in enumerate(sheet3_col_heads):
        sheet3.write(1, col, head, header_format)

    for row, ship in enumerate(sheet3_data, start=2):
        print '3 ', row
        sheet3.write(row, 0, str(ship.airwaybill_number), plain_format)
        sheet3.write(row, 1, str(ship.product_type), plain_format)
        sheet3.write(row, 2, str(ship.order_number), plain_format)
        sheet3.write(row, 3, str(ship.actual_weight), plain_format)
        sheet3.write(row, 4, str(ship.volumetric_weight), plain_format)
        sheet3.write(row, 5, str(ship.collectable_value), plain_format)
        sheet3.write(row, 6, str(ship.declared_value), plain_format)
        sheet3.write(row, 7, str(ship.pickup.service_centre.center_name), plain_format)
        sheet3.write(row, 8, str(ship.original_dest.center_name), plain_format)
        sheet3.write(row, 9, str(ship.pickup.subcustomer_code.name), plain_format)
        sheet3.write(row, 10, str(ship.shipper.name), plain_format)
        try:
            sheet3.write(row, 11, str(ship.consignee), plain_format)
        except:
            sheet3.write(row, 11, '', plain_format)
        ad1 = ship.consignee_address1 if ship.consignee_address1 else u''
        ad2 = ship.consignee_address2 if ship.consignee_address2 else u''
        ad3 = ship.consignee_address3 if ship.consignee_address3 else u''
        ad4 = ship.consignee_address4 if ship.consignee_address4 else u''
        address = ad1 + ad2 + ad3 + ad4
        sheet3.write(row, 12, address, plain_format)
        #except:
            #sheet3.write(row, 12, '', plain_format)
        sheet3.write(row, 13, str(ship.mobile), plain_format)
        sheet3.write(row, 14, str(ship.added_on), plain_format)
        sheet3.write(row, 15, get_internal_shipment_status(ship.status), plain_format)
        sheet3.write(row, 16, str(ship.expected_dod), plain_format)
        sheet3.write(row, 17, str(ship.updated_on), plain_format)
        try:
            sheet3.write(row, 18, str(ship.remark), plain_format)
        except:
            sheet3.write(row, 18, '', plain_format)
        if ship.reason_code:
            sheet3.write(row, 19, str(ship.reason_code.code), plain_format)
            sheet3.write(row, 20, str(ship.reason_code.code_description), plain_format)
        else:
            sheet3.write(row, 19, str(''), plain_format)
            sheet3.write(row, 20, str(''), plain_format)
        try:
            rec_by = ship.statusupdate_set.all()[0].recieved_by
            sheet3.write(row, 21, str(rec_by), plain_format)
        except:
            sheet3.write(row, 21, '', plain_format)
        del_added = ship.deliveryoutscan_set.all().order_by('-added_on')
        del_date = ''
        del_time = ''
        if del_added.exists():
            del_added = del_added[0]
            del_date = del_added.added_on.date()
            del_time = del_added.added_on.time()

        sheet3.write(row, 22, str(del_date), plain_format)
        sheet3.write(row, 23, str(del_time), plain_format)
        ref_awb = ship.ref_airwaybill_number
        sheet3.write(row, 24, str(ref_awb), plain_format)
        ret_status = ''
        ret_upd = ''
        ret_rawb = ''
        if ref_awb:
            rstatus = Shipment.objects.filter(airwaybill_number=ref_awb).\
                    values_list('status', 'updated_on', 'ref_airwaybill_number')
            if rstatus.exists():
                ret_status = rstatus[0][0]
                ret_upd = rstatus[0][1]
                ret_rawb = rstatus[0][2]
        sheet3.write(row, 25, str(ret_status), plain_format)
        sheet3.write(row, 26, str(ret_upd), plain_format)
        sheet3.write(row, 27, str(''), plain_format)
        sheet3.write(row, 28, str(ret_rawb), plain_format)

    #--------------------------- sheet4
    print 'sheet3 finished..'
    del sheet3_data
    q = get_reconciliation_query(date_from, date_to, cust_id)
    q = q & Q(reason_code__code=333)
    sheet4_data = Shipment.objects.filter(q)
    sheet4 = workbook.add_worksheet()
    sheet4_col_heads = (
        'Air Waybill No',
        'nature',
        'Order No',
        'Weight',
        'Vol Weight',
        'COD Amount',
        'Declared Value',
        'Origin',
        'Destination',
        'Vendor',
        'Shipper',
        'Consignee',
        'Consignee Address',
        'Contact Number',
        'P/U Date',
        'Status',
        'Expected Date',
        'Updated Date',
        'Remarks',
        'Reason Code',
        'Reason',
        'Received by',
        'Del Date',
        'Del Time',
        'new status')

    sheet4.set_column(0, 25, 15)

    for col, head in enumerate(sheet4_col_heads):
        sheet4.write(1, col, head, header_format)

    for row, ship in enumerate(sheet4_data, start=2):
        sheet4.write(row, 0, str(ship.airwaybill_number), plain_format)
        sheet4.write(row, 1, str(ship.product_type), plain_format)
        sheet4.write(row, 2, str(ship.order_number), plain_format)
        sheet4.write(row, 3, str(ship.actual_weight), plain_format)
        sheet4.write(row, 4, str(ship.volumetric_weight), plain_format)
        sheet4.write(row, 5, str(ship.collectable_value), plain_format)
        sheet4.write(row, 6, str(ship.declared_value), plain_format)
        sheet4.write(row, 7, str(ship.pickup.service_centre.center_name), plain_format)
        sheet4.write(row, 8, str(ship.original_dest.center_name), plain_format)
        sheet4.write(row, 9, str(ship.pickup.subcustomer_code.name), plain_format)
        sheet4.write(row, 10, str(ship.shipper.name), plain_format)
        try:
            sheet4.write(row, 11, str(ship.consignee), plain_format)
        except:
            sheet4.write(row, 11, '', plain_format)
        ad1 = ship.consignee_address1 if ship.consignee_address1 else u''
        ad2 = ship.consignee_address2 if ship.consignee_address2 else u''
        ad3 = ship.consignee_address3 if ship.consignee_address3 else u''
        ad4 = ship.consignee_address4 if ship.consignee_address4 else u''

        address = ad1 + ad2 + ad3 + ad4
        sheet4.write(row, 12, address, plain_format)
        sheet4.write(row, 13, str(ship.mobile), plain_format)
        sheet4.write(row, 14, str(ship.added_on), plain_format)
        sheet4.write(row, 15, get_internal_shipment_status(ship.status), plain_format)
        sheet4.write(row, 16, str(ship.expected_dod), plain_format)
        sheet4.write(row, 17, str(ship.updated_on), plain_format)
        try:
            sheet4.write(row, 18, str(ship.remark), plain_format)
        except:
            sheet4.write(row, 18, '', plain_format)
        if ship.reason_code:
            sheet4.write(row, 19, str(ship.reason_code.code), plain_format)
            sheet4.write(row, 20, str(ship.reason_code.code_description), plain_format)
        else:
            sheet4.write(row, 19, str(''), plain_format)
            sheet4.write(row, 20, str(''), plain_format)
        try:
            rec_by = ship.statusupdate_set.all()[0].recieved_by
            sheet4.write(row, 21, str(rec_by), plain_format)
        except:
            sheet4.write(row, 21, '', plain_format)

        del_added = ship.deliveryoutscan_set.all().order_by('-added_on')
        del_date = ''
        del_time = ''
        if del_added.exists():
            del_added = del_added[0]
            del_date = del_added.added_on.date()
            del_time = del_added.added_on.time()

        sheet4.write(row, 22, str(del_date), plain_format)
        sheet4.write(row, 23, str(del_time), plain_format)
        ref_awb = ship.ref_airwaybill_number
        ret_status = ''
        if ref_awb:
            rstatus = Shipment.objects.filter(airwaybill_number=ref_awb).\
                    values_list('status')
            if rstatus.exists():
                ret_status = rstatus[0][0]
        sheet4.write(row, 24, str(ret_status), plain_format)

    # --------------------------------- sheet5
    print 'sheet4 finished..'
    del sheet4_data
    q = get_reconciliation_query(date_from, date_to, cust_id)
    q = q & Q(reason_code__code=777)
    sheet5_data = Shipment.objects.filter(q)
    sheet5 = workbook.add_worksheet()
    sheet5_col_heads = (
        'Air Waybill No',
        'nature',
        'Order No',
        'Weight',
        'Vol Weight',
        'COD Amount',
        'Declared Value',
        'Origin',
        'Destination',
        'Vendor',
        'Shipper',
        'Consignee',
        'Consignee Address',
        'Contact Number',
        'P/U Date',
        'Status',
        'Expected Date',
        'Updated Date',
        'Remarks',
        'Reason Code',
        'Reason',
        'Received by',
        'Del Date',
        'Del Time',
        'New Air Waybill (RTS)',
        'Return Status',
        'Updated on',
        'new status',
        'RTS NO')

    sheet5.set_column(0, 28, 15)

    for col, head in enumerate(sheet5_col_heads):
        sheet5.write(1, col, head, header_format)

    for row, data_dict in enumerate(sheet5_data, start=2):
        sheet5.write(row, 0, str(ship.airwaybill_number), plain_format)
        sheet5.write(row, 1, str(ship.product_type), plain_format)
        sheet5.write(row, 2, str(ship.order_number), plain_format)
        sheet5.write(row, 3, str(ship.actual_weight), plain_format)
        sheet5.write(row, 4, str(ship.volumetric_weight), plain_format)
        sheet5.write(row, 5, str(ship.collectable_value), plain_format)
        sheet5.write(row, 6, str(ship.declared_value), plain_format)
        sheet5.write(row, 7, str(ship.pickup.service_centre.center_name), plain_format)
        sheet5.write(row, 8, str(ship.original_dest.center_name), plain_format)
        sheet5.write(row, 9, str(ship.pickup.subcustomer_code.name), plain_format)
        sheet5.write(row, 10, str(ship.shipper.name), plain_format)
        try:
            sheet5.write(row, 11, str(ship.consignee), plain_format)
        except:
            sheet5.write(row, 11, '', plain_format)
        ad1 = ship.consignee_address1 if ship.consignee_address1 else u''
        ad2 = ship.consignee_address2 if ship.consignee_address2 else u''
        ad3 = ship.consignee_address3 if ship.consignee_address3 else u''
        ad4 = ship.consignee_address4 if ship.consignee_address4 else u''

        address = ad1 + ad2 + ad3 + ad4
        sheet5.write(row, 12, address, plain_format)
        sheet5.write(row, 13, str(ship.mobile), plain_format)
        sheet5.write(row, 14, str(ship.added_on), plain_format)
        sheet5.write(row, 15, get_internal_shipment_status(ship.status), plain_format)
        sheet5.write(row, 16, str(ship.expected_dod), plain_format)
        sheet5.write(row, 17, str(ship.updated_on), plain_format)
        try:
            sheet5.write(row, 18, str(ship.remark), plain_format)
        except:
            sheet5.write(row, 18, '', plain_format)
        if ship.reason_code:
            sheet5.write(row, 19, str(ship.reason_code.code), plain_format)
            sheet5.write(row, 20, str(ship.reason_code.code_description), plain_format)
        else:
            sheet5.write(row, 19, str(''), plain_format)
            sheet5.write(row, 20, str(''), plain_format)
        try:
            rec_by = ship.statusupdate_set.all()[0].recieved_by
            sheet5.write(row, 21, str(rec_by), plain_format)
        except:
            sheet5.write(row, 21, '', plain_format)
        del_added = ship.deliveryoutscan_set.all().order_by('-added_on')
        del_date = ''
        del_time = ''
        if del_added.exists():
            del_added = del_added[0]
            del_date = del_added.added_on.date()
            del_time = del_added.added_on.time()

        sheet5.write(row, 22, str(del_date), plain_format)
        sheet5.write(row, 23, str(del_time), plain_format)
        ref_awb = ship.ref_airwaybill_number
        sheet5.write(row, 24, str(ref_awb), plain_format)
        ret_status = ''
        ret_upd = ''
        ret_nst = ''
        if ref_awb:
            rstatus = Shipment.objects.filter(airwaybill_number=ref_awb).\
                    values_list('status', 'updated_on')
            if rstatus.exists():
                ret_status = rstatus[0][0]
                ret_upd = rstatus[0][1]
        sheet5.write(row, 25, str(ret_status), plain_format)
        sheet5.write(row, 26, str(ret_upd), plain_format)
        sheet5.write(row, 27, str(ret_nst), plain_format)
        sheet5.write(row, 28, str(''), plain_format)
    #------------------------- sheet6
    print 'sheet5 finished..'
    del sheet5_data
    q = get_reconciliation_query(date_from, date_to, cust_id)
    q = q & Q(reason_code__code=999)
    sheet6_data = Shipment.objects.filter(q)
    sheet6 = workbook.add_worksheet()
    sheet6_col_heads = (
        'Air Waybill No',
        'payment ref no',
        'nature',
        'Order No',
        'Weight',
        'Vol Weight',
        'COD Amount',
        'Declared Value',
        'Origin',
        'Destination',
        'Vendor',
        'Shipper',
        'Consignee',
        'Consignee Address',
        'Contact Number',
        'P/U Date',
        'Status',
        'Expected Date',
        'Updated Date',
        'Reason Code',
        'Reason',
        'Received by',
        'Del Date',
        'Del Time',
        'New Air Waybill (RTS)',
        'Return Status',
        'Updated on',
        'new status')

    sheet6.set_column(0, 27, 15)

    for col, head in enumerate(sheet6_col_heads):
        sheet6.write(1, col, head, header_format)

    for row, ship in enumerate(sheet6_data, start=2):
        sheet6.write(row, 0, str(ship.airwaybill_number), plain_format)
        sheet6.write(row, 1, str(ship.product_type), plain_format)
        sheet6.write(row, 2, str(ship.order_number), plain_format)
        sheet6.write(row, 3, str(ship.actual_weight), plain_format)
        sheet6.write(row, 4, str(ship.volumetric_weight), plain_format)
        sheet6.write(row, 5, str(ship.collectable_value), plain_format)
        sheet6.write(row, 6, str(ship.declared_value), plain_format)
        sheet6.write(row, 7, str(ship.pickup.service_centre.center_name), plain_format)
        sheet6.write(row, 8, str(ship.original_dest.center_name), plain_format)
        sheet6.write(row, 9, str(ship.pickup.subcustomer_code.name), plain_format)
        sheet6.write(row, 10, str(ship.shipper.name), plain_format)
        try:
            sheet6.write(row, 11, str(ship.consignee), plain_format)
        except:
            sheet6.write(row, 11, '', plain_format)

        ad1 = ship.consignee_address1 if ship.consignee_address1 else u''
        ad2 = ship.consignee_address2 if ship.consignee_address2 else u''
        ad3 = ship.consignee_address3 if ship.consignee_address3 else u''
        ad4 = ship.consignee_address4 if ship.consignee_address4 else u''

        address = ad1 + ad2 + ad3 + ad4
        sheet6.write(row, 12, address, plain_format)
        sheet6.write(row, 13, str(ship.mobile), plain_format)
        sheet6.write(row, 14, str(ship.added_on), plain_format)
        sheet6.write(row, 15, get_internal_shipment_status(ship.status), plain_format)
        sheet6.write(row, 16, str(ship.expected_dod), plain_format)
        sheet6.write(row, 17, str(ship.updated_on), plain_format)
        try:
            sheet6.write(row, 18, str(ship.remark), plain_format)
        except:
            sheet6.write(row, 18, '', plain_format)
        if ship.reason_code:
            sheet6.write(row, 19, str(ship.reason_code.code), plain_format)
            sheet6.write(row, 20, str(ship.reason_code.code_description), plain_format)
        else:
            sheet6.write(row, 19, str(''), plain_format)
            sheet6.write(row, 20, str(''), plain_format)
        try:
            rec_by = ship.statusupdate_set.all()[0].recieved_by
            sheet6.write(row, 21, str(rec_by), plain_format)
        except:
            sheet6.write(row, 21, '', plain_format)
        del_added = ship.deliveryoutscan_set.all().order_by('-added_on')
        del_date = ''
        del_time = ''
        if del_added.exists():
            del_added = del_added[0]
            del_date = del_added.added_on.date()
            del_time = del_added.added_on.time()

        sheet6.write(row, 22, str(del_date), plain_format)
        sheet6.write(row, 23, str(del_time), plain_format)
        ref_awb = ship.ref_airwaybill_number
        sheet6.write(row, 24, str(ref_awb), plain_format)
        ret_status = ''
        ret_upd = ''
        ret_nst = ''
        if ref_awb:
            rstatus = Shipment.objects.filter(airwaybill_number=ref_awb).\
                    values_list('status', 'updated_on')
            if rstatus.exists():
                ret_status = rstatus[0][0]
                ret_upd = rstatus[0][1]
        sheet6.write(row, 25, str(ret_status), plain_format)
        sheet6.write(row, 26, str(ret_upd), plain_format)
        sheet6.write(row, 27, str(ret_nst), plain_format)
    print 'sheet6 finished..'
    del sheet6_data

    # -------------------------- sheet7
    q = get_reconciliation_query(date_from, date_to, cust_id)
    q = q & Q(product_type='cod')
    all_ships = Shipment.objects.filter(q).values_list('airwaybill_number')

    qr = get_remittance_query(date_from, date_to, cust_id)
    remittance_list = Remittance.objects.filter(qr).values_list('remittancecodcharge__codcharge__shipment__airwaybill_number')
    all_awb = [x[0] for x in all_ships]
    all_remt = [x[0] for x in remittance_list]
    rem_awbs = set(all_awb) - set(all_remt)
    sheet7_data = Shipment.objects.filter(airwaybill_number__in=rem_awbs)
    sheet7 = workbook.add_worksheet()
    sheet7_col_heads = (
        'Air Waybill No',
        'payment ref no',
        'nature',
        'Order No',
        'Weight',
        'Vol Weight',
        'COD Amount',
        'Declared Value',
        'Origin',
        'Destination',
        'Vendor',
        'Shipper',
        'Consignee',
        'Consignee Address',
        'Contact Number',
        'P/U Date',
        'Status',
        'Expected Date',
        'Updated Date',
        'Reason Code',
        'Reason',
        'Received by',
        'Del Date',
        'Del Time',
        'New Air Waybill (RTS)',
        'Return Status',
        'Updated on',
        'new status',
        'RTS NO')

    sheet7.set_column(0, 28, 15)

    for col, head in enumerate(sheet7_col_heads):
        sheet7.write(1, col, head, header_format)

    for row, ship in enumerate(sheet7_data, start=2):
        sheet7.write(row, 0, str(ship.airwaybill_number), plain_format)
        sheet7.write(row, 1, 0, plain_format)
        sheet7.write(row, 2, str(ship.product_type), plain_format)
        sheet7.write(row, 3, str(ship.order_number), plain_format)
        sheet7.write(row, 4, str(ship.actual_weight), plain_format)
        sheet7.write(row, 5, str(ship.volumetric_weight), plain_format)
        sheet7.write(row, 6, str(ship.collectable_value), plain_format)
        sheet7.write(row, 7, str(ship.declared_value), plain_format)
        sheet7.write(row, 8, str(ship.pickup.service_centre.center_name), plain_format)
        sheet7.write(row, 9, str(ship.original_dest.center_name), plain_format)
        sheet7.write(row, 10, str(ship.pickup.subcustomer_code.name), plain_format)
        sheet7.write(row, 11, str(ship.shipper.name), plain_format)
        try:
            sheet7.write(row, 12, str(ship.consignee), plain_format)
        except:
            sheet7.write(row, 12, '', plain_format)

        ad1 = ship.consignee_address1 if ship.consignee_address1 else u''
        ad2 = ship.consignee_address2 if ship.consignee_address2 else u''
        ad3 = ship.consignee_address3 if ship.consignee_address3 else u''
        ad4 = ship.consignee_address4 if ship.consignee_address4 else u''

        address = ad1 + ad2 + ad3 + ad4
        sheet7.write(row, 13, address, plain_format)
        sheet7.write(row, 14, str(ship.mobile), plain_format)
        sheet7.write(row, 15, str(ship.added_on), plain_format)
        sheet7.write(row, 16, get_internal_shipment_status(ship.status), plain_format)
        sheet7.write(row, 17, str(ship.expected_dod), plain_format)
        sheet7.write(row, 18, str(ship.updated_on), plain_format)
        if ship.reason_code:
            sheet7.write(row, 19, str(ship.reason_code.code), plain_format)
            sheet7.write(row, 20, str(ship.reason_code.code_description), plain_format)
        else:
            sheet7.write(row, 19, str(''), plain_format)
            sheet7.write(row, 20, str(''), plain_format)
        try:
            rec_by = ship.statusupdate_set.all()[0].recieved_by
            sheet7.write(row, 21, str(rec_by), plain_format)
        except:
            sheet7.write(row, 21, '', plain_format)
        del_added = ship.deliveryoutscan_set.all().order_by('-added_on')
        del_date = ''
        del_time = ''
        if del_added.exists():
            del_added = del_added[0]
            del_date = del_added.added_on.date()
            del_time = del_added.added_on.time()

        sheet7.write(row, 22, str(del_date), plain_format)
        sheet7.write(row, 23, str(del_time), plain_format)
        ref_awb = ship.ref_airwaybill_number
        sheet7.write(row, 24, str(ref_awb), plain_format)
        ret_status = ''
        ret_upd = ''
        ret_nst = ''

        if ref_awb:
            rstatus = Shipment.objects.filter(airwaybill_number=ref_awb).\
                    values_list('status', 'updated_on')
            if rstatus.exists():
                ret_status = rstatus[0][0]
                ret_upd = rstatus[0][1]
        sheet7.write(row, 25, str(ret_status), plain_format)
        sheet7.write(row, 26, str(ret_upd), plain_format)
        sheet7.write(row, 27, str(ret_nst), plain_format)
        sheet7.write(row, 28, str(''), plain_format)
    print 'sheet7 finished..'
    del sheet7_data

    workbook.close()
    return file_name


if __name__ == "__main__":
    date_from1 = '2013-8-01'
    date_to1 = '2013-8-31'
    date_from2 = '2013-9-01'
    date_to2 = '2013-9-31'
    date_from3 = '2013-10-01'
    date_to3 = '2013-10-31'
    cust_id = 7 
    file_name = generate_reconciliation_excel(date_from1, date_to1, cust_id)
    file_name = generate_reconciliation_excel(date_from2, date_to2, cust_id)
    file_name = generate_reconciliation_excel(date_from3, date_to3, cust_id)
    print file_name
