import datetime
import calendar
from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Count, Sum, F
from django.db.models import Q
from django.core.mail import send_mail
from service_centre.models import Shipment,Zone
from reports.report_api import ReportGenerator

PROJECT_ROOT = '/home/web/ecomm.prtouch.com/ecomexpress'
root_url = 'http://ecomm.prtouch.com/'

"""
 This is the new daywise report including yield and having new 10 reports.
"""
"""
   Types of reports:
     0.Normal Daywise Report
     1.Destination=(West UP, South UP)
     2.Jasper separate
     3.Rest separate
     4.Original.Destination.city=pickup.service.city
     5.PPD
     6.COD
     7.Weight <=0.5
     8.Weight >0.5<=5
     9.Weight >5
     10.Zone
"""

"""
   Month wise:
    1.dec = 0
    2.nov = -1
    3.oct = -2
"""

col_heads = (
    'Date', 'Shipment Count',
    'Chargeable Weight', 'Collectable value',
    'Declared Value',
    'Freight', 'FuelSc',
    'SDL','SDD',
    'Reverse', 'COD',
    'VCHC Charge', 'To pay',
    'TAB', 'RTO Charge',
    'Total', 'Yield')



def get_daywise_charge_report(month_no, report_type=0):
    """
    for x in range(month_no, -3, -1):
        if x == 0:
            now=now - datetime.timedelta(days=1)
        else:
            if now.month == 1:
                year = now.year-1
                month = 12
                end_day = calendar.monthrange(year,month)[1]
                now = datetime.datetime(year,month,end_day)
            else:
                 month = now.month-1
                 end_day = calendar.monthrange(year,month)[1]
                 now = datetime.datetime(year,month,end_day)
    """

    now = datetime.datetime.now().date()
    if month_no == 0:
        # for current mnth
        year = now.year
        month = now.month
        now = now - datetime.timedelta(days=1)

    elif month_no == -1:
        # for previous month
        if now.month == 1:
            year = now.year - 1
            month = 12
            end_day = calendar.monthrange(year,month)[1]
            now = datetime.datetime(year,month,end_day)
        else:
            year = now.year
            month = now.month - 1
            end_day = calendar.monthrange(year, month)[1]
            now = datetime.datetime(year, month, end_day)

    elif month_no == -2:
        # for previous month's previous
        if now.month == 1:
            year = now.year - 1
            month = 11
            end_day = calendar.monthrange(year,month)[1]
            now = datetime.datetime(year,month,end_day)
        elif now.month == 2:
            year = now.year - 1
            month = 12
            end_day = calendar.monthrange(year,month)[1]
            now = datetime.datetime(year,month,end_day)
        else:
            year = now.year
            month = now.month - 1
            end_day = calendar.monthrange(year, month)[1]
            now = datetime.datetime(year, month, end_day)

    elif month_no == -9:
        # only for testing in prtouch
        year = now.year
        month = now.month - 9
        end_day = calendar.monthrange(year, month)[1]
        now = datetime.datetime(year, month, end_day)


    # Normal Daywise report
    if report_type == 0:
        q = Q()
        filename = 'daywise_charge_{0}_{1}.xlsx'.format(month, year)

    # Destination(West UP, South UP)
    if report_type == 1:
        q = Q()
        zone=Zone.objects.filter(zone_name__in=['West UP','South UP'])

        q = q & Q(original_dest__city__labeled_zones__in = zone)

        filename = 'daywise_charge_West_South_UP_{0}_{1}.xlsx'.format(month, year)

    # ONLY JASPER REPORT
    elif report_type == 2:
        q = Q()
        q = q & Q(shipper_id = 6)

        filename = 'daywise_charge_Jasper_{0}_{1}.xlsx'.format(month, year)

    # OTHER THAN JASPER REPORT
    elif report_type == 3:
        q = Q()
        q = q & Q(shipper_id = 6)

        filename = 'daywise_charge_other_than_jasper_{0}_{1}.xlsx'.format(month, year)

    # INTRACITY
    elif report_type == 4:
        q = Q()
        q = q & Q(original_dest__city=F('pickup__service_centre__city'))

        filename = 'daywise_charge_intracity_{0}_{1}.xlsx'.format(month, year)

    # ONLY PPD
    elif report_type == 5:
        q = Q()
        q = q & Q(shipext__product__product_name='ppd')

        filename = 'daywise_charge_PPD_{0}_{1}.xlsx'.format(month, year)

    # ONLY COD
    elif report_type == 6:
        q = Q()
        q = q & Q(shipext__product__product_name='cod')

        filename = 'daywise_charge_COD_{0}_{1}.xlsx'.format(month, year)

    # WEIGHT <= 0.5
    elif report_type == 7:
        q = Q()
        q = q & Q(chargeable_weight__lte=0.5)

        filename = 'daywise_charge_weight_lte_0.5_{0}_{1}.xlsx'.format(month, year)

    # WEIGHT > 0.5 <=5
    elif report_type == 8:
        q = Q()
        q = q & Q(chargeable_weight__gt=0.5, chargeable_weight__lte=5)

        filename = 'daywise_charge_weight_btwn_0.5_5_{0}_{1}.xlsx'.format(month, year)

    # WEIGHT > 5
    elif report_type == 9:
        q = Q()
        q = q & Q(chargeable_weight__gt=5)

        filename = 'daywise_charge_weight_gt_5_{0}_{1}.xlsx'.format(month, year)

    # INTRAZONE
    elif report_type == 10:
        q = Q()
        q = q & Q(original_dest__city__labeled_zones=F('pickup__service_centre__city__labeled_zones'))

        filename = 'daywise_charge_zone_{0}_{1}.xlsx'.format(month, year)

    report = ReportGenerator(filename)
    report.write_header(col_heads)

    if report_type == 3:
        freight_data = Shipment.objects.filter(
            shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(q
        ).exclude(shipment_date__gt = now
        ).values("shipment_date").annotate(
            Count('id'),
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
            op_to_pay=Sum('order_price__to_pay_charge')
        ).order_by('shipment_date')

        cod_charges = Shipment.objects.filter(
            shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year,
        ).exclude(rts_status = 1
        ).exclude(q
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(shipment_date__gt = now
        ).values("shipment_date").annotate(
            cod_charge = Sum('codcharge__cod_charge'),
            collectable_value = Sum('collectable_value')
        )

        cod_charges_negative = Shipment.objects.filter(
            shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year,
            rts_status = 1
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(q
        ).exclude(shipment_date__gt = now
        ).values("shipment_date").annotate(cod_charge = Sum('codcharge__cod_charge'),)

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
                        if not cod:
                            cod = 0
                        cod = cod - cod_charge['cod_charge']

            for k,v in fd.items():
                if fd[k] is None:
                    fd[k] = 0

            total = fd['op_freight']+\
                    fd['op_fuel']+\
                    fd['op_sdl']+\
                    fd['op_sdd_charge']+\
                    fd['op_reverse_charge']+\
                    cod+\
                    fd['op_valuable_cargo_handling_charge']+\
                    fd['op_to_pay']+\
                    fd['op_tab_charge']+fd['op_rto_price']

            yield_val = total/fd['id__count']

            row = (fd['shipment_date'], fd['id__count'], fd['total_chargeable_weight'],
                   round(collectable_value,0), round(fd['declared_value'],0),
                   round(fd['op_freight'],0), round(fd['op_fuel'],0),
                   round(fd['op_sdl'],0), round(fd['op_sdd_charge'],0),
                   round(fd['op_reverse_charge'],0), round(cod,0),
                   round(fd['op_valuable_cargo_handling_charge'],0),
                   round(fd['op_to_pay'],0), round(fd['op_tab_charge'],0),
                   round(fd['op_rto_price'],0), round(total,0), round(yield_val,0))

            report.write_row(row)

        fd = Shipment.objects.filter(
            shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(q
        ).exclude(shipment_date__gt = now
        ).aggregate(
            Count('id'),
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
        cod_charges = Shipment.objects.filter(shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(q
        ).exclude(shipment_date__gt = now
        ).exclude(rts_status = 1).aggregate(
            Sum('codcharge__cod_charge'), Sum('collectable_value')
        )
        cod_charges_negative = Shipment.objects.filter(
            shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year, rts_status = 1
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(q
        ).exclude(shipment_date__gt = now
        ).aggregate(Sum('codcharge__cod_charge'),)

        for key,value in fd.items():
            if fd[key] is None:
                fd[key] = 0

        if not cod_charges['codcharge__cod_charge__sum']:
            cod_charges['codcharge__cod_charge__sum'] = 0

        if not cod_charges_negative['codcharge__cod_charge__sum']:
            cod_charges_negative['codcharge__cod_charge__sum'] = 0

        collectable_value = cod_charges['collectable_value__sum']

        if not collectable_value:
            collectable_value = 0

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

        if not fd['id__count']:
            yield_val = 0
        else:
            yield_val = total/fd['id__count']

        row = ('Total', fd['id__count'], round(fd['chargeable_weight__sum'],0),
               round(collectable_value,0), round(fd['declared_value__sum'],0),
               round(fd['order_price__freight_charge__sum'],0),
               round(fd['order_price__fuel_surcharge__sum'],0),
               round(fd['order_price__sdl_charge__sum'],0),
               round(fd['order_price__sdd_charge__sum'],0),
               round(fd['order_price__reverse_charge__sum'],0), round(cod,0),
               round(fd['order_price__valuable_cargo_handling_charge__sum'],0),
               round(fd['order_price__to_pay_charge__sum'],0),
               round(fd['order_price__tab_charge__sum'],0),
               round(fd['order_price__rto_charge__sum'],0),
               round(total,0), round(yield_val,0))

        report.write_row(row)

        file_name = report.manual_sheet_close()
        return file_name

    else:
        freight_data = Shipment.objects.filter(
            q, shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(shipment_date__gt = now
        ).values("shipment_date").annotate(
            Count('id'),
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
            op_to_pay=Sum('order_price__to_pay_charge')
        ).order_by('shipment_date')

        cod_charges = Shipment.objects.filter(
            q, shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year,
        ).exclude(rts_status = 1
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(shipment_date__gt = now
        ).values("shipment_date").annotate(
            cod_charge = Sum('codcharge__cod_charge'),
            collectable_value = Sum('collectable_value')
        )

        cod_charges_negative = Shipment.objects.filter(
            q, shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year,
            rts_status = 1
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(shipment_date__gt = now
        ).values("shipment_date").annotate(cod_charge = Sum('codcharge__cod_charge'),)

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
                        if not cod:
                            cod = 0
                        cod = cod - cod_charge['cod_charge']

            for k,v in fd.items():
                if fd[k] is None:
                    fd[k] = 0

            total = fd['op_freight']+\
                    fd['op_fuel']+\
                    fd['op_sdl']+\
                    fd['op_sdd_charge']+\
                    fd['op_reverse_charge']+\
                    cod+\
                    fd['op_valuable_cargo_handling_charge']+\
                    fd['op_to_pay']+\
                    fd['op_tab_charge']+fd['op_rto_price']

            yield_val = total/fd['id__count']

            row = (fd['shipment_date'], fd['id__count'], fd['total_chargeable_weight'],
                   round(collectable_value,0), round(fd['declared_value'],0),
                   round(fd['op_freight'],0), round(fd['op_fuel'],0),
                   round(fd['op_sdl'],0), round(fd['op_sdd_charge'],0),
                   round(fd['op_reverse_charge'],0), round(cod,0),
                   round(fd['op_valuable_cargo_handling_charge'],0),
                   round(fd['op_to_pay'],0), round(fd['op_tab_charge'],0),
                   round(fd['op_rto_price'],0), round(total,0), round(yield_val,0))

            report.write_row(row)

        fd = Shipment.objects.filter(
            q, shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(shipment_date__gt = now
        ).aggregate(
            Count('id'),
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
        cod_charges = Shipment.objects.filter(q, shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(shipment_date__gt = now
        ).exclude(rts_status = 1).aggregate(
            Sum('codcharge__cod_charge'), Sum('collectable_value')
        )
        cod_charges_negative = Shipment.objects.filter(
            q, shipper__activation_status = True,
            shipment_date__month = month, shipment_date__year = year, rts_status = 1
        ).exclude(shipext__product__product_name__in = ['ebsppd', 'ebscod']
        ).exclude(shipment_date__gt = now
        ).aggregate(Sum('codcharge__cod_charge'),)

        for key,value in fd.items():
            if fd[key] is None:
                fd[key] = 0

        if not cod_charges['codcharge__cod_charge__sum']:
            cod_charges['codcharge__cod_charge__sum'] = 0

        if not cod_charges_negative['codcharge__cod_charge__sum']:
            cod_charges_negative['codcharge__cod_charge__sum'] = 0

        collectable_value = cod_charges['collectable_value__sum']

        if not collectable_value:
            collectable_value = 0

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

        if not fd['id__count']:
            yield_val = 0
        else:
            yield_val = total/fd['id__count']

        row = ('Total', fd['id__count'], round(fd['chargeable_weight__sum'],0),
               round(collectable_value,0), round(fd['declared_value__sum'],0),
               round(fd['order_price__freight_charge__sum'],0),
               round(fd['order_price__fuel_surcharge__sum'],0),
               round(fd['order_price__sdl_charge__sum'],0),
               round(fd['order_price__sdd_charge__sum'],0),
               round(fd['order_price__reverse_charge__sum'],0), round(cod,0),
               round(fd['order_price__valuable_cargo_handling_charge__sum'],0),
               round(fd['order_price__to_pay_charge__sum'],0),
               round(fd['order_price__tab_charge__sum'],0),
               round(fd['order_price__rto_charge__sum'],0),
               round(total,0), round(yield_val,0))

        report.write_row(row)

        file_name = report.manual_sheet_close()
        return file_name



    """
    mail_link = root_url + path_to_save
    send_mail('Daywise Charge Report',
              "Dear Team,\n Daywise charge report has been generated. Please find the link below.\n http://billing.ecomexpress.in/static/uploads{0}\n\n".format(file_name),
              'support@ecomexpress.in',['prashanta@ecomexpress.in','jignesh@prtouch.com', "satyak@ecomexpress.in", "jaideeps@ecomexpress.in", "nareshb@ecomexpress.in", "onkar@prtouch.com"])
              #'support@ecomexpress.in',['onkar@prtouch.com','onkartonge@gmail.com'])"""














