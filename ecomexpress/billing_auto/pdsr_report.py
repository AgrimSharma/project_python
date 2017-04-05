import datetime
import calendar
import pdb
from xlsxwriter.workbook import Workbook
from decimal import Decimal
from collections import defaultdict

from django.conf import settings
from django.db.models import Count, Sum
from django.core.mail import send_mail

from service_centre.models import Shipment
from location.models import Pincode
from customer.models import Customer
TW = Decimal(10)** -2


def clean_dict(d):
    for k,v in d.items():
        if not v:
            d[k] = 0
    return d

def fix_decimal(val):
    return Decimal(val).quantize(TW)

def add_months(sourcedate, months):
     month = sourcedate.month - 1 + months
     year = sourcedate.year + month / 12
     month = month % 12 + 1
     day = min(sourcedate.day,calendar.monthrange(year,month)[1])
     return datetime.date(year,month,day)

def get_dates(date_str):
    report_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    from_date = report_date.strftime('%Y-%m-01 07:01:00')
    to_date = report_date.strftime('%Y-%m-%d 07:00:00')
    last_date = add_months(report_date, 1)
    last_date = last_date.strftime('%Y-%m-01 07:00:00')

    todate = datetime.datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")
    fromdate = datetime.datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")
    lastdate = datetime.datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")

    return (todate, fromdate, lastdate)

def get_pdsr_dispaly_data(date_str):
    #pdb.set_trace()
    ##print 'getting display_data..'
    # making out put data, data structure
    day_data = Shipment.objects.using('local_ecomm').filter(shipment_date=date_str).values("shipper__code").\
            annotate(
                ship_count=Count('id'),
                total_cw=Sum('chargeable_weight'),
                freight_sum=Sum('order_price__freight_charge'),
                sdl_sum=Sum('order_price__sdl_charge'),
                fuel_sum=Sum('order_price__fuel_surcharge'),
                rto_sum=Sum('order_price__rto_charge'),
                sdd_sum=Sum('order_price__sdd_charge'),
                reverse_sum=Sum('order_price__reverse_charge'),
                vchc_sum=Sum('order_price__valuable_cargo_handling_charge'),
                to_pay_sum=Sum('order_price__to_pay_charge'))

    # shipper product wise details
    ddata = Shipment.objects.using('local_ecomm').filter(shipment_date=date_str).values("shipper__code", "shipper__name", "product_type").\
            annotate(
                ship_count=Count('id'),
                total_cw=Sum('chargeable_weight'),
                freight_sum=Sum('order_price__freight_charge'),
                sdl_sum=Sum('order_price__sdl_charge'),
                fuel_sum=Sum('order_price__fuel_surcharge'),
                rto_sum=Sum('order_price__rto_charge'),
                sdd_sum=Sum('order_price__sdd_charge'),
                reverse_sum=Sum('order_price__reverse_charge'),
                vchc_sum=Sum('order_price__valuable_cargo_handling_charge'),
                to_pay_sum=Sum('order_price__to_pay_charge'))

    day_cod = Shipment.objects.using('local_ecomm').filter(shipment_date=date_str).exclude(rts_status = 1).values("shipper__code").\
        annotate(cod_sum=Sum('codcharge__cod_charge'),)

    day_cod_negative = Shipment.objects.using('local_ecomm').filter(shipment_date=date_str, rts_status=1).\
            values("shipper__code").\
            annotate(cod_sum=Sum('codcharge__cod_charge'),)

    # Monthly Report
    year, month, day = date_str.strip().split('-')
    month_data = Shipment.objects.using('local_ecomm').filter(shipment_date__year=year, shipment_date__month=month, shipment_date__lte=date_str)\
            .values("shipper__code", "shipper__id").\
            annotate(
                mship_count=Count('id'),
                mtotal_cw=Sum('chargeable_weight'),
                mfreight_sum=Sum('order_price__freight_charge'),
                msdl_sum=Sum('order_price__sdl_charge'),
                mfuel_sum=Sum('order_price__fuel_surcharge'),
                mrto_sum=Sum('order_price__rto_charge'),
                msdd_sum=Sum('order_price__sdd_charge'),
                mreverse_sum=Sum('order_price__reverse_charge'),
                mvchc_sum=Sum('order_price__valuable_cargo_handling_charge'),
                mto_pay_sum=Sum('order_price__to_pay_charge'))

    mdata = Shipment.objects.using('local_ecomm').filter(shipment_date__year=year, shipment_date__month=month, shipment_date__lte=date_str)\
            .values("shipper__code", "shipper__name", "product_type").\
            annotate(
                mship_count=Count('id'),
                mtotal_cw=Sum('chargeable_weight'),
                mfreight_sum=Sum('order_price__freight_charge'),
                msdl_sum=Sum('order_price__sdl_charge'),
                mfuel_sum=Sum('order_price__fuel_surcharge'),
                mrto_sum=Sum('order_price__rto_charge'),
                msdd_sum=Sum('order_price__sdd_charge'),
                mreverse_sum=Sum('order_price__reverse_charge'),
                mvchc_sum=Sum('order_price__valuable_cargo_handling_charge'),
                mto_pay_sum=Sum('order_price__to_pay_charge'))

    month_cod_cod = Shipment.objects.using('local_ecomm').filter(shipment_date__year=year, shipment_date__month=month, shipment_date__lte=date_str)\
            .exclude(rts_status = 1).values("shipper__code").\
        annotate(mcod_sum=Sum('codcharge__cod_charge'),)

    month_cod_cod_negative = Shipment.objects.using('local_ecomm').filter(shipment_date__year=year,
                                 shipment_date__month=month,
                                 shipment_date__lte=date_str,
                                 rts_status=1).\
            values("shipper__code").\
            annotate(mcod_sum=Sum('codcharge__cod_charge'),)

    ccodes = month_data.values_list('shipper__id', 'shipper__code').distinct()
    customer_id_code = {}
    for i in ccodes:
        customer_id_code[i[0]] = i[1]

    # day customer wise data
    day_customer_wise = list(day_data)
    # day customer wise total codcharge : for rts_status = 1
    day_cod_customer_wise = list(day_cod)
    # day customer wise total codcharge : for rts_status = 2
    day_cod_customer_wise_negative = list(day_cod_negative)

    # create dict of customers for daily data - from customer wise list
    day_customer_wise_dict = defaultdict(dict)
    for d in day_customer_wise:
        day_customer_wise_dict[d['shipper__code']]['total'] = d
    for d in day_cod_customer_wise:
        day_customer_wise_dict[d['shipper__code']]['codcharge'] = d
    for d in day_cod_customer_wise_negative:
        day_customer_wise_dict[d['shipper__code']]['codcharge_negative'] = d
    ##print 'day dict - customer wise :'

    day_product_wise = list(ddata)

    # create dict of customers - from customer wise list
    day_product_wise_dict = defaultdict(dict)
    for d in day_product_wise:
        ptype = d.get('product_type')
        if ptype == 'cod':
            day_product_wise_dict[d['shipper__code']]['cod'] = d
        else:
            day_product_wise_dict[d['shipper__code']]['ppd'] = d

    ##print 'day dict - product type wise :'

    # month customer wise data
    month_customer_wise = list(month_data)
    # month customer wise data total codcharge : rts_status = 1
    month_cod_customer_wise = list(month_cod_cod)
    # month customer wise data total codcharge : rts_status = 2
    month_cod_customer_wise_negative = list(month_cod_cod_negative)

    # create a dict of customer for monthly data
    month_customer_wise_dict = defaultdict(dict)
    for d in month_customer_wise:
        month_customer_wise_dict[d['shipper__code']]['total'] = d
    for d in month_cod_customer_wise:
        month_customer_wise_dict[d['shipper__code']]['codcharge'] = d
    for d in month_cod_customer_wise_negative:
        month_customer_wise_dict[d['shipper__code']]['codcharge_negative'] = d
    ##print 'month dict - customer wise :'

    month_product_wise = list(mdata)

    # create dict of customers - from product wise list
    month_product_wise_dict = defaultdict(dict)
    for d in month_product_wise:
        ptype = d.get('product_type')
        if ptype == 'cod':
            month_product_wise_dict[d['shipper__code']]['cod'] = d
        else:
            month_product_wise_dict[d['shipper__code']]['ppd'] = d
    ##print 'month dict - product wise :'

    todate, fromdate, lastdate = get_dates(date_str)

    daygenerator = (fromdate + datetime.timedelta(x) for x in xrange((todate - fromdate).days + 2))
    projected_days_now = sum(1 for day in daygenerator if day.weekday() < 6)    #getting days excluding sundays
    #projected_days_now = projected_days_now -1
    if projected_days_now < 1:
        projected_days_now = 1
    daygeneratormonth = (fromdate + datetime.timedelta(x) for x in xrange((lastdate - fromdate).days + 1))
    total_projected_days = sum(1 for day in daygeneratormonth if day.weekday() < 6)    #getting days excluding sundays
    #total_projected_days = total_projected_days - 1
    #print projected_days_now ,"and",total_projected_days   
     
    def get_prodwise_row(day_data, month_data, day_cod_sum=0, month_cod_sum=0, ptype=None):
        ##print 'product wise row...',ptype
        customer = Customer.objects.using('local_ecomm').get(code=code)
        cname = customer.name
        website = customer.website
        pincode = customer.address.pincode
        if month_data:
            month_data = clean_dict(month_data)
        if day_data:
            day_data = clean_dict(day_data)
        try:
            zone = Pincode.objects.using('local_ecomm').get(pincode=pincode).service_center.city.zone
        except Pincode.DoesNotExist:
            zone = ''
        cod_row = [code, ptype, cname, website, zone]

        if day_data:
            if day_data.get('reverse_sum'):
                dreverse_sum = day_data.get('reverse_sum')
            else:
                dreverse_sum = 0

            if day_data.get('sdl_sum'):
                dsdl_sum = day_data.get('sdl_sum')
            else:
                dsdl_sum = 0

            if day_data.get('sdd_sum'):
                dsdd_sum = day_data.get('sdd_sum')
            else:
                dsdd_sum = 0

            if day_data.get('vchc_sum'):
                dvchc_sum = day_data.get('vchc_sum')
            else:
                dvchc_sum = 0

            if day_data.get('to_pay_sum'):
                dto_pay_sum = day_data.get('to_pay_sum')
            else:
                dto_pay_sum = 0

            if day_data.get('rto_sum'):
                drto_sum = day_data.get('rto_sum')
            else:
                drto_sum = 0

            if day_data.get('freight_sum'):
                dfreight_sum = day_data.get('freight_sum')
            else:
                dfreight_sum = 0

            if day_data.get('fuel_sum'):
                dfuel_sum = day_data.get('fuel_sum')
            else:
                dfuel_sum = 0
        else:
            dreverse_sum = 0
            dsdl_sum = 0
            dsdd_sum = 0
            dvchc_sum = 0
            dto_pay_sum = 0
            drto_sum = 0
            dfreight_sum = 0
            dfuel_sum = 0

        revers_sdl_sdd_vchc_topay_rto_sum =  dreverse_sum + dsdl_sum+ dsdd_sum + dvchc_sum + dto_pay_sum + drto_sum

        ##print day_data
        if day_data:
            ##print 'daily data exists...',ptype
            others = revers_sdl_sdd_vchc_topay_rto_sum
            total = others + dfreight_sum + dfuel_sum + day_cod_sum
            wt_ship = day_data.get('total_cw') / day_data.get('ship_count')
            yl_ship = total / day_data.get('ship_count')
            cw = day_data.get('total_cw')
            yl_kl = total/cw if cw else total
            cod_rowd = [day_data.get('ship_count'), day_data.get('total_cw'), dfreight_sum,
                    dfuel_sum, day_cod_sum, others, total, wt_ship, yl_ship, yl_kl]
        else:
            ##print 'daily cod not exists...'
            cod_rowd = [0]*10
        cod_row.extend(cod_rowd)

        # month data calculation
        ##print 'month data exists..'
        if month_data:
            #print month_data
            others = month_data.get('mvchc_sum') + month_data.get('mto_pay_sum') + month_data.get('mrto_sum') + \
                    month_data.get('msdl_sum') + month_data.get('mreverse_sum') + month_data.get('msdd_sum')

            total = others + month_data.get('mfreight_sum') + month_data.get('mfuel_sum') + month_cod_sum
            mtotal_cw = month_data.get('mtotal_cw')
            wt_ship = mtotal_cw/month_data.get('mship_count')
            yl_ship = total/month_data.get('mship_count')
            mtotal_cw = mtotal_cw if mtotal_cw else 1
            yl_kl = total/mtotal_cw
            proj_ships = (month_data.get('mship_count') / projected_days_now) * total_projected_days
            proj_revenue = (total / projected_days_now) * total_projected_days
            cod_rowm = [month_data.get('mship_count'),  month_data.get('mtotal_cw'),
                    month_data.get('mfreight_sum'), month_data.get('mfuel_sum'),
                    month_cod_sum, others, total, wt_ship, yl_ship, yl_kl, proj_ships, proj_revenue]
        else:
            cod_rowm = [0]*12
        cod_row.extend(cod_rowm)

        return cod_row

    def get_total_row(day_data, month_data, day_cod_sum=0, month_cod_sum=0):

        ##print 'totals row..'
        # making total row
        if month_data:
            month_data = clean_dict(month_data)
        if day_data:
            day_data = clean_dict(day_data)
        customer = Customer.objects.using('local_ecomm').get(code=code)
        cname = customer.name
        website = customer.website
        pincode = customer.address.pincode
        try:
            zone = Pincode.objects.using('local_ecomm').get(pincode=pincode).service_center.city.zone
        except Pincode.DoesNotExist:
            zone = ''

        total_row = [code, 'Total', cname, website, zone]
        if day_data:
            ##print 'daily total exists..'
            daily_total_cw = day_data.get('total_cw')
            if day_data.get('vchc_sum'): day_data_vchc_sum = day_data.get('vchc_sum')
            else: day_data_vchc_sum = 0
            if day_data.get('to_pay_sum'): day_data_to_pay_sum = day_data.get('to_pay_sum')
            else: day_data_to_pay_sum = 0
            if day_data.get('rto_sum'): day_data_rto_sum = day_data.get('rto_sum')
            else: day_data_rto_sum = 0
            if day_data.get('sdl_sum'): day_data_sdl_sum = day_data.get('sdl_sum')
            else: day_data_sdl_sum = 0
            if day_data.get('reverse_sum'): day_data_reverse_sum = day_data.get('reverse_sum')
            else: day_data_reverse_sum = 0
            if day_data.get('sdd_sum'): day_data_sdd_sum = day_data.get('sdd_sum')
            else: day_data_sdd_sum = 0
            if day_data.get('freight_sum'): day_data_freight_sum = day_data.get('freight_sum')
            else: day_data_freight_sum = 0
            if day_data.get('fuel_sum'): day_data_fuel_sum = day_data.get('fuel_sum')
            else: day_data_fuel_sum = 0
            if day_data.get('total_cw'): day_data_total_cw = day_data.get('total_cw')
            else: day_data_total_cw = 0

            ##print day_data.get('total_cw') , day_data.get('freight_sum') , day_cod_sum

            others = day_data_vchc_sum + day_data_to_pay_sum + day_data_rto_sum +\
                    day_data_sdl_sum + day_data_reverse_sum + day_data_sdd_sum
            total = others + day_data_freight_sum + day_data_fuel_sum + day_cod_sum
            wt_ship = day_data.get('total_cw') / day_data.get('ship_count')
            yl_ship = total/day_data.get('ship_count')
            daily_total_cw = daily_total_cw if daily_total_cw else 1
            yl_kl = total/daily_total_cw
            total_rowd = [day_data.get('ship_count'),  day_data.get('total_cw'),
                    day_data.get('freight_sum'), day_data.get('fuel_sum'), day_cod_sum,
                    others, total, wt_ship, yl_ship, yl_kl]
            ##print 'total row got'
        else:
            ##print 'daily total not exists..'
            total_rowd = [0]*10
        total_row.extend(total_rowd)

        # monthly data calculation
        #print 'month total exists..'
        others = month_data.get('mvchc_sum') + month_data.get('mto_pay_sum') + month_data.get('mrto_sum') + \
                    month_data.get('msdl_sum') + month_data.get('mreverse_sum') + month_data.get('msdd_sum')

        total = others + month_data.get('mfreight_sum') + month_data.get('mfuel_sum') + month_cod_sum
        wt_ship = month_data.get('mtotal_cw') / month_data.get('mship_count')
        yl_ship = total/month_data.get('mship_count')
        month_total_cw = month_data.get('mtotal_cw')
        month_total_cw = month_total_cw if month_total_cw else 1
        yl_kl = total/month_total_cw
        proj_ships = (month_data.get('mship_count') / projected_days_now) * total_projected_days
        proj_revenue = (total / projected_days_now) * total_projected_days
        total_rowm = [month_data.get('mship_count'),  month_data.get('mtotal_cw'), month_data.get('mfreight_sum'),
                month_data.get('mfuel_sum'), month_cod_sum, others, total, wt_ship, yl_ship, yl_kl, proj_ships, proj_revenue]
        total_row.extend(total_rowm)
        return total_row

    customers = list(Customer.objects.using('local_ecomm').exclude(activation_status=False).values_list('id', 'code', 'name'))
    cust_dict = defaultdict(dict)
    for c in customers:
        cust_dict[c[0]] = {'code':c[1], 'name':c[2]}

    cids = cust_dict.keys()
    for cid in cids:
        ##print '*'*100
        code = customer_id_code.get(cid, None)
        #print 'reading for ', code
        if code:
            day_ppd_data = day_product_wise_dict[code].get('cod')
            month_ppd_data = month_product_wise_dict[code].get('cod')

            day_cod_data = day_product_wise_dict[code].get('ppd')
            month_cod_data = month_product_wise_dict[code].get('ppd')

            day_total_data = day_customer_wise_dict[code].get('total')
            month_total_data = month_customer_wise_dict[code].get('total')

            day_codcharge_data = day_customer_wise_dict[code].get('codcharge', {})
            day_codcharge_negative_data = day_customer_wise_dict[code].get('codcharge_negative', {})

            month_codcharge_data = month_customer_wise_dict[code].get('codcharge', {})
            month_codcharge_negative_data = month_customer_wise_dict[code].get('codcharge_negative', {})

            day_cod_pos = day_codcharge_data.get('cod_sum', 0)
            day_cod_neg = day_codcharge_negative_data.get('cod_sum', 0)
            day_cod_pos = 0 if day_cod_pos is None else day_cod_pos
            day_cod_neg = 0 if day_cod_neg is None else day_cod_neg
            day_cod_sum = day_cod_pos - day_cod_neg

            month_cod_pos = month_codcharge_data.get('mcod_sum', 0)
            month_cod_neg = month_codcharge_negative_data.get('mcod_sum', 0)
            month_cod_pos = 0 if month_cod_pos is None else month_cod_pos
            month_cod_neg = 0 if month_cod_neg is None else month_cod_neg
            month_cod_sum = month_cod_pos - month_cod_neg
            ##print 'got all data....'

            #if month_total_data:
            # get cod row
            #print 'prepare cod row.............'
            cod_row = get_prodwise_row(day_ppd_data, month_ppd_data, day_cod_sum=day_cod_sum, month_cod_sum=month_cod_sum, ptype='COD')

            # get ppd row
            #print 'prepare ppd row.............'
            ppd_row = get_prodwise_row(day_cod_data, month_cod_data, ptype='PPD')

            # get total row
            #print 'prepare total row.............'
            total_row = get_total_row(day_total_data, month_total_data, day_cod_sum=day_cod_sum, month_cod_sum=month_cod_sum)
            #else:
                ##print '#'*100
                #cod_row, ppd_row, total_row = [], [], []
        else:
            code = cust_dict.get(cid).get('code')
            name = cust_dict.get(cid).get('name')
            cod_row, ppd_row, total_row = [0]*27, [0]*27, [0]*27
            cod_row[0] = code
            ppd_row[0] = code
            total_row[0] = code
            cod_row[1] = 'COD'
            ppd_row[1] = 'PPD'
            total_row[1] = 'TOTAL'
            cod_row[2] = name
            ppd_row[2] = name
            total_row[2] = name

        yield (ppd_row, cod_row, total_row)

def write_pdsr_to_excel(date_str):
    file_name = "/complete_pdsr_report_%s.xlsx"%(date_str)
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()

    header_format = workbook.add_format()
    header_format.set_bg_color('yellow')
    header_format.set_bold()
    header1_format = workbook.add_format()
    header1_format.set_bg_color('blue')
    header1_format.set_bold()
    header2_format = workbook.add_format()
    header2_format.set_bg_color('red')
    header2_format.set_bold()
    plain_format = workbook.add_format()

    sheet.write(0, 3, "Previous Day Sales Report ", header_format)
    sheet.write(0, 15, "Month to date Sales Report", header1_format)
    sheet.set_column(2, 2, 25) # set column width

    sheet.write(1, 0, "Date ", header_format)
    sheet.write(1, 1, date_str)
    col_heads = ("Customer Code", "Service", "Customer Name", "Website", "Zone","No Of Ships",
                "Chargeable Weight", "Freight", "fuel Surcharge", "COD",
                "Others", "total", "Wt/Shipt", "Yld/Shipt", "Yld/Kilo",
                "No Of Ships", "Chargeable Weight", "Freight", "fuel Surcharge",
                "COD", "Others", "Total", "Wt/Shipt", "Yld/Shipt", "Yld/Kilo",
                "Total Projected Shipments", "Total Projected Revenue")

    for ind, col in enumerate(col_heads):
        if ind <= 14:
            sheet.write(3, ind, col, header_format)
        elif ind <= 24:
            sheet.write(3, ind, col, header1_format)
        else:
            sheet.write(3, ind, col, header2_format)

    # write data to excel sheet
    # data_dict = {'ccode': [ (daily_cod,   daily_ppd), (monthly_cod,monthly_ppd)], ....}
    ##print 'got pdsr data...'
    data_gen = get_pdsr_dispaly_data(date_str)
    ##print 'got pdsr gen...'

    row_num = 4
    totals_row = [[0]*22, [0]*22, [0]*22]
    for data in data_gen:
        # PPD row
        for ind, val in enumerate(data[0]):
            val = fix_decimal(val) if ind > 5 else str(val)
            # in the totals row last two values are day_yield and month_yield
            # respectively which we dont need to write to excel.
            if ind <= 24:
                sheet.write(row_num, ind, val)
        totals_row[0] = map(sum, zip(totals_row[0], data[0][5:]))

        # COD row
        for ind, val in enumerate(data[1]):
            if not val:
                val = 0
            val = fix_decimal(val) if ind > 5 else str(val)
            # in the totals row last two values are day_yield and month_yield
            # respectively which we dont need to write to excel.
            if ind <= 24:
                sheet.write(row_num+1, ind, val)
        totals_row[1] = map(sum, zip(totals_row[1], data[1][5:]))

        # Total row
        for ind, val in enumerate(data[2]):
            if not val: 
                val = 0
            val = fix_decimal(val) if ind > 5 else str(val)
            # in the totals row last two values are day_yield and month_yield
            # respectively which we dont need to write to excel.
            if ind <= 24:
                sheet.write(row_num+2, ind, val)
        if not data[2][7]: data[2][7] = 0
        if not data[2][8]: data[2][8] = 0
        ##print  data[2]
        totals_row[2] = map(sum, zip(totals_row[2], data[2][5:]))

        row_num += 4

    #pdb.set_trace()
    # recalculating yield/ship ... values
    #ppd - day
    totals_row[0][7] = totals_row[0][1]/totals_row[0][0]
    totals_row[0][8] = totals_row[0][6]/totals_row[0][0]
    totals_row[0][9] = totals_row[0][6]/totals_row[0][1]

    #ppd - month
    totals_row[0][17] = totals_row[0][11]/totals_row[0][10]
    totals_row[0][18] = totals_row[0][16]/totals_row[0][10]
    totals_row[0][19] = totals_row[0][16]/totals_row[0][11]

    #cod - day
    totals_row[1][7] = totals_row[1][1]/totals_row[1][0]
    totals_row[1][8] = totals_row[1][6]/totals_row[1][0]
    totals_row[1][9] = totals_row[1][6]/totals_row[1][1]

    #cod - month
    totals_row[1][17] = totals_row[1][11]/totals_row[1][10]
    totals_row[1][18] = totals_row[1][16]/totals_row[1][10]
    totals_row[1][19] = totals_row[1][16]/totals_row[1][11]

    # total - day
    totals_row[2][7] = totals_row[2][1]/totals_row[2][0]
    totals_row[2][8] = totals_row[2][6]/totals_row[2][0]
    totals_row[2][9] = totals_row[2][6]/totals_row[2][1]

    # total - month
    totals_row[2][17] = totals_row[2][11]/totals_row[2][10]
    totals_row[2][18] = totals_row[2][16]/totals_row[2][10]
    totals_row[2][19] = totals_row[2][16]/totals_row[2][11]

    # COD row
    sheet.write(row_num, 2, 'PPD TOTAL')
    for ind, val in enumerate(totals_row[0], start=5):
        val = fix_decimal(val) if ind > 5 else str(val)
        if ind <= 26:
            sheet.write(row_num, ind, val)

    # PPD row
    sheet.write(row_num+1, 2, 'COD TOTAL')
    for ind, val in enumerate(totals_row[1], start=5):
        val = fix_decimal(val) if ind > 5 else str(val)
        if ind <= 26:
            sheet.write(row_num+1, ind, val)

    # Total row
    sheet.write(row_num+2, 2, 'GRAND TOTAL')
    for ind, val in enumerate(totals_row[2], start=5):
        val = fix_decimal(val) if ind > 5 else str(val)
        if ind <= 26:
            sheet.write(row_num+2, ind, val)

    workbook.close()

    totals_row.insert(0, col_heads)
    return (path_to_save, totals_row)
