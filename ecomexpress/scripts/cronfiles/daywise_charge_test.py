import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Count, Sum
from django.core.mail import send_mail
from service_centre.models import Shipment

PROJECT_ROOT = '/home/web/ecomm.prtouch.com/ecomexpress'
root_url = 'http://ecomm.prtouch.com/'

def get_daywise_charge_report():
    # add filename and set save file path
    file_name = "/daywise_charge_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
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

    date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()

    sheet.set_column(0, 14, 12) # set column width
    # write statement headers: statement name, customer name, and date
    sheet.write(2, 0, "Date", header_format)
    sheet.write(2, 1, "Shipment Count", header_format)
    sheet.write(2, 2, "Chargeable Weight", header_format)
    sheet.write(2, 3, "Collectable Value", header_format)
    sheet.write(2, 4, "Declared value", header_format)
    sheet.write(2, 5, "Freight", header_format)
    sheet.write(2, 6, "FuelSc", header_format)
    sheet.write(2, 7, "SDL", header_format)
    sheet.write(2, 8, "SDD", header_format)
    sheet.write(2, 9, "Reverse", header_format)
    sheet.write(2, 10, "COD", header_format)
    sheet.write(2, 11, "VCHC Charge", header_format)
    sheet.write(2, 12, "To Pay", header_format)
    sheet.write(2, 13, "TAB", header_format)
    sheet.write(2, 14, "RTO Charge", header_format)
    sheet.write(2, 15, "Total", header_format)

    now = datetime.date(2013, 12, 01)
    #now = now - datetime.timedelta(days=1)
    print now
    year = now.strftime("%Y")
    month = now.strftime("%m")
    freight_data = Shipment.objects.filter(
        shipment_date__gte='2013-11-01',
        shipment_date__lt=now).values("shipment_date").\
        annotate(Count('id'),
            total_chargeable_weight=Sum('chargeable_weight'),
            collectable_value=Sum('collectable_value'),
            declared_value=Sum('declared_value'),
            op_freight=Sum('order_price__freight_charge'),
            op_sdl=Sum('order_price__sdl_charge'),
            op_fuel=Sum('order_price__fuel_surcharge'),
            op_rto_price=Sum('order_price__rto_charge'),
            op_sdd_charge=Sum('order_price__sdd_charge'),
            op_reverse_charge=Sum('order_price__reverse_charge'),
            op_valuable_cargo_handling_charge=Sum('order_price__valuable_cargo_handling_charge'),
            op_tab_charge=Sum('order_price__tab_charge'),
            op_to_pay=Sum('order_price__to_pay_charge')).exclude(shipment_date__gt=now).order_by('shipment_date')

    cod_charges = Shipment.objects.filter(
        shipment_date__gte='2013-11-01',
        shipment_date__lt=now).exclude(rts_status = 1).exclude(shipment_date__gt=now).values("shipment_date").\
        annotate(cod_charge=Sum('codcharge__cod_charge'), collectable_value=Sum('collectable_value'))

    cod_charges_negative = Shipment.objects.filter(
        shipment_date__gte='2013-11-01',
        shipment_date__lt=now,
        rts_status=1).exclude(shipment_date__gt=now).values("shipment_date").\
        annotate(cod_charge=Sum('codcharge__cod_charge'),)

    row_count = 3
    for fd in  freight_data:
        cod = 0
        collectable_value = 0
        for cod_charge in cod_charges:
            if cod_charge['shipment_date'] == fd['shipment_date']:
                cod = cod_charge['cod_charge']
                collectable_value = cod_charge['collectable_value']
        for cod_charge in cod_charges_negative:
            if cod_charge['shipment_date'] == fd['shipment_date']:
                if not cod_charge['cod_charge']:
                     cod_charge['cod_charge'] = 0
                cod = cod - cod_charge['cod_charge']

        total = fd['op_freight']+\
                fd['op_fuel']+\
                fd['op_sdl']+\
                fd['op_sdd_charge']+\
                fd['op_reverse_charge']+\
                cod+\
                fd['op_valuable_cargo_handling_charge']+\
                fd['op_to_pay']+\
                fd['op_tab_charge']+fd['op_rto_price']

        sheet.write_datetime(row_count, 0, fd['shipment_date'], date_format)
        sheet.write(row_count, 1,(fd['id__count']))
        sheet.write(row_count, 2, round(fd['total_chargeable_weight'],2)) 
        sheet.write(row_count, 3, round(collectable_value,2))
        sheet.write(row_count, 4, round(fd['declared_value'],2))
        sheet.write(row_count, 5, round(fd['op_freight'],2))
        sheet.write(row_count, 6, round(fd['op_fuel'],2))
        sheet.write(row_count, 7, round(fd['op_sdl'],2))
        sheet.write(row_count, 8, round(fd['op_sdd_charge'],2))
        sheet.write(row_count, 9, round(fd['op_reverse_charge'],2))
        sheet.write(row_count, 10, round(cod,2))
        sheet.write(row_count, 11, round(fd['op_valuable_cargo_handling_charge'],2))
        sheet.write(row_count, 12, round(fd['op_to_pay'],2))
        sheet.write(row_count, 13, round(fd['op_tab_charge'],2))
        sheet.write(row_count, 14, round(fd['op_rto_price'],2))
        sheet.write(row_count, 15, round(total,2))
        row_count += 1
    
    fd = Shipment.objects.filter(
        shipment_date__gte='2013-11-01',
        shipment_date__lt=now).exclude(shipment_date__gt=now).\
        aggregate(Count('id'),
            Sum('chargeable_weight'),
            Sum('collectable_value'),
            Sum('declared_value'),
            Sum('order_price__freight_charge'),
            Sum('order_price__sdl_charge'),
            Sum('order_price__fuel_surcharge'),
            Sum('order_price__rto_charge'),
            Sum('order_price__sdd_charge'),
            Sum('order_price__reverse_charge'),
            Sum('order_price__valuable_cargo_handling_charge'),
            Sum('order_price__reverse_charge'),
            Sum('order_price__to_pay_charge'),
            Sum('order_price__tab_charge'),Sum('order_price__rto_charge'),
)
    cod_charges = Shipment.objects.filter(
        shipment_date__gte='2013-11-01',
        shipment_date__lt=now).exclude(shipment_date__gt=now).exclude(rts_status = 1).\
        aggregate(Sum('codcharge__cod_charge'), Sum('collectable_value'))
    cod_charges_negative = Shipment.objects.filter(
        shipment_date__gte='2013-11-01',
        shipment_date__lt=now,
        rts_status=1).exclude(shipment_date__gt=now).\
        aggregate(Sum('codcharge__cod_charge'),)
    print cod_charges_negative['codcharge__cod_charge__sum'] 
    if not cod_charges_negative['codcharge__cod_charge__sum']:
           cod_charges_negative['codcharge__cod_charge__sum'] = 0
    collectable_value = cod_charges['collectable_value__sum'] 
    cod = cod_charges['codcharge__cod_charge__sum'] - cod_charges_negative['codcharge__cod_charge__sum']

    total = fd['order_price__freight_charge__sum']+\
                fd['order_price__fuel_surcharge__sum']+\
                fd['order_price__sdl_charge__sum']+\
                fd['order_price__sdd_charge__sum']+\
                fd['order_price__reverse_charge__sum']+\
                cod+\
                fd['order_price__valuable_cargo_handling_charge__sum']+\
                fd['order_price__to_pay_charge__sum']+\
                fd['order_price__tab_charge__sum']+fd['order_price__rto_charge__sum']


    sheet.write(row_count, 0, 'Total')
    sheet.write(row_count, 1, fd['id__count'])
    sheet.write(row_count, 2, round(fd['chargeable_weight__sum'],0))
    sheet.write(row_count, 3, round(collectable_value,0))
    sheet.write(row_count, 4, round(fd['declared_value__sum'],0))
    sheet.write(row_count, 5, round(fd['order_price__freight_charge__sum'],0))
    sheet.write(row_count, 6, round(fd['order_price__fuel_surcharge__sum'],0))
    sheet.write(row_count, 7, round(fd['order_price__sdl_charge__sum'],0))
    sheet.write(row_count, 8, round(fd['order_price__sdd_charge__sum'],0))
    sheet.write(row_count, 9, round(fd['order_price__reverse_charge__sum'],0))
    sheet.write(row_count, 10, round(cod,0))
    sheet.write(row_count, 11, round(fd['order_price__valuable_cargo_handling_charge__sum'],0))
    sheet.write(row_count, 12, round(fd['order_price__to_pay_charge__sum'],0))
    sheet.write(row_count, 13, round(fd['order_price__tab_charge__sum'],0))
    sheet.write(row_count, 14, round(fd['order_price__rto_charge__sum'],0))
    sheet.write(row_count, 15, round(total,0))
 #   sheet.write(row_count, 13, fd['op_rto_price__sum'])
 #   sheet.write(row_count, 14, total)'''
  

    mail_link = root_url + path_to_save
    send_mail('Daywise Charge Report',
              "Dear Team,\n Daywise charge report has been generated. Please find the link below.\n http://billing.ecomexpress.in/static/uploads{0}\n\n".format(file_name),
           'support@ecomexpress.in',['samar@prtouch.com', 'jinesh@prtouch.com'])
if __name__ == '__main__':
    get_daywise_charge_report()
