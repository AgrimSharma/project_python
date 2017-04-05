import os
from collections import defaultdict
from service_centre.models import Shipment, AirportConfirmation
from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Sum, Count


def get_shipments():
    return Shipment.objects.filter(shipper__id__in=[6,7, 38], shipment_date__month=8, sdl=1, original_dest__city__zone__id=9)

def generate_xls():
    col_heads=('Date',  'Customer Name', 'Customer Code', 'Inscan Date ', 'Origin', 'Destination', 'Chargeable Weight')
    col_count = len(col_heads)
    # add filename and set save file path
    pdf_home = settings.PROJECT_ROOT + settings.STATIC_URL + 'uploads/billing/'
    file_name = 'shipment_report_aug.xlsx'
    path_to_save = os.path.join(pdf_home, file_name)
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format()
    header_format.set_bg_color('yellow')
    header_format.set_bold()
    plain_format = workbook.add_format()

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, col_count, 12) # set column width
    sheet.write(0, 2, "Bill Summary")
    for col, name in enumerate(col_heads):
        sheet.write(2, col, name, header_format)

    ships = get_shipments()
    for ind, ship in enumerate(ships, start=3):
        print 'shipment id ', ship.id
        sheet.write(ind, 0, str(ship.airwaybill_number), plain_format)
        sheet.write(ind, 1, str(ship.shipper.name), plain_format)
        sheet.write(ind, 2, str(ship.shipper.code), plain_format)
        sheet.write(ind, 3, str(ship.inscan_date), plain_format)
        sheet.write(ind, 4, str(ship.pickup.service_centre.center_shortcode), plain_format)
        sheet.write(ind, 5, str(ship.original_dest.center_shortcode), plain_format)
        sheet.write(ind, 6, str(ship.chargeable_weight), plain_format)
        # shipper name, shipper code, inscan_date
    workbook.close()
    return path_to_save

def airport_confirmation(date_str):
    airport_confirm = AirportConfirmation.objects.filter(date=date_str)
    aw = AirportConfirmation.objects.filter(date='2013-10-08').values_list('id').annotate(Sum('run_code__connection__bags__ship_data__actual_weight'))
    bags_count = AirportConfirmation.objects.filter(date='2013-10-08').values_list('id').annotate(Count('run_code__connection__bags'))
    actual_weight = list(aw)

    aw_id_dict = defaultdict(float)
    bags_count_dict = defaultdict(int)

    for k in actual_weight:
        aw_id_dict[k[0]] = k[1] if k[1] else 0

    for k in bags_count:
        bags_count_dict[k[0]] = k[1] if k[1] else 0

    #.values_list('id', 'cnote', 'run_code__coloader__name', 'run_code__destination', 'num_of_bags')
    col_heads=('Airport Confirmation id',  'Cnote Number', 'Coloader Name', 'Origin', 'Destination', 'Number of Bags',  'Chargeable Weight')
    col_count = len(col_heads)
    # add filename and set save file path
    pdf_home = settings.PROJECT_ROOT + settings.STATIC_URL + 'uploads/billing/'
    file_name = 'airportconfirmation_2013_08_10.xlsx'
    path_to_save = os.path.join(pdf_home, file_name)
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format()
    header_format.set_bg_color('yellow')
    header_format.set_bold()
    plain_format = workbook.add_format()

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, col_count, 12) # set column width
    sheet.write(0, 1, 'DATE: '+date_str) # set column width
    for col, name in enumerate(col_heads):
        sheet.write(2, col, name, header_format)

    for ind, ac in enumerate(airport_confirm, start=3):
        print 'shipment id ', ac.id
        sheet.write(ind, 0, str(ac.id), plain_format)
        sheet.write(ind, 1, str(ac.cnote), plain_format)
        sheet.write(ind, 2, str(ac.run_code.coloader.name), plain_format)
        sheet.write(ind, 3, str(ac.origin), plain_format)
        dest = ac.run_code.destination.values_list('center_name', flat=True)
        destn = ' ,'.join(dest)
        sheet.write(ind, 4, str(destn), plain_format)
        bags = bags_count_dict[ac.id]
        sheet.write(ind, 5, str(bags), plain_format)
        aw = aw_id_dict[ac.id]
        sheet.write(ind, 6, str(aw), plain_format)
        # shipper name, shipper code, inscan_date
    workbook.close()
    return path_to_save




