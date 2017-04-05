import os
import datetime
from service_centre.models import Shipment
from customer.models import Customer

from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Sum, Q


def update_shipmentinfo_n_downloadlist(shipment):
    # get Shipmenthistory object for given shipment
    upd_time = shipment.added_on
    monthdir = upd_time.strftime("%Y_%m")
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
    history = shipment_history.objects.filter(shipment=shipment, status=6)
    updated_on = history.order_by('updated_on')[0].updated_on if history else None
    status = get_internal_shipment_status(shipment.status)
    inscan_date = shipment.inscan_date

    # get DeliveryOutscan object for given shipment
    deliveryscan = DeliveryOutscan.objects.filter(shipments=shipment)
    first_scan, second_scan, last_scan = None, None, None
    if deliveryscan:
        first_scan = deliveryscan.order_by('id')[0].added_on
        last_scan = deliveryscan.order_by('-id')[0].added_on
        try:
            second_scan = deliveryscan.order_by('id')[1].added_on
        except IndexError:
            pass

    # following are the list of values we required to generate this report
    # airway_bill_no, pickup date, shipment at delivery centre, origin,
    # destination, shipper, type, inscan_time, 1st outscan date, no of outscans,
    # last outscan date, last updation date, status
    u = (shipment.airwaybill_number, shipment.added_on, updated_on,
         shipment.pickup.service_centre, shipment.original_dest, shipment.shipper.name,
         shipment.product_type,inscan_date, first_scan,second_scan, len(deliveryscan),
         last_scan,shipment.updated_on, status)

    return u

def outscan_for_shipment():
        print 'started...'
        date_from = '2013-10-21'
        date_to =  '2013-10-25'
        q = Q()

        if date_from and date_to:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to))

        shipments = Shipment.objects.filter(q, status__gte=6)
        print 'get display date..'
        display_data_list = (update_shipmentinfo_n_downloadlist(shipment) for shipment in shipments)
        print 'got display date..'

        cols_head = ( 'AWB No',
                     'Pickup Date',  #1
                     'Shipment DC',  #2
                     'Origin',       #3
                     'Destination',       #4
                     'Shipper',       #5
                     'Type',       #6
                     'Inscan Date',       #7
                     '1st outscan date',       #8
                     '2nd otscan date',       #9
                     'No of outscans',       #10
                     'Last outscan date',       #11
                     'Last updation date',       #12
                     'Status')       #13

        pdf_home = settings.PROJECT_ROOT + settings.STATIC_URL + 'uploads/reports/'
        file_name = 'outscan_report.xlsx'
        path_to_save = os.path.join(pdf_home, file_name)
        workbook = Workbook(path_to_save)
        sheet = workbook.add_worksheet()
        # print 'downloading data as excel..'

        # define style formats for header and data
        header_format = workbook.add_format()
        header_format.set_bg_color('yellow')
        header_format.set_bold()
        plain_format = workbook.add_format()

        sheet.write(0, 2, "Outscan for Shipment Report", header_format)

        for ind,val in enumerate(cols_head):
            sheet.write(3, ind, val, header_format)

        for row, rowdata in enumerate(display_data_list, start=4):
            print row
            for col, val in enumerate(rowdata):
                if not val:
                    continue
                if col in [1,2,7,8,9,11,12]:
                    sheet.write(row, col, val.strftime('%d-%m-%Y'), plain_format)
                else:
                    sheet.write(row, col, str(val), plain_format)

        workbook.close()
        print path_to_save
