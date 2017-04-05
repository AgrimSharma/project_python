import os
from collections import defaultdict
from decimal import Decimal

from xlsxwriter.workbook import Workbook
from billing.models import BillingPreview, BillingSubCustomerPreview, ProvisionalProductBilling
from billing.generate_bill_pdf import get_bill_summary_filename

TW = Decimal(10) ** -2



def get_bill_summary_data(bill_id):
    """ generate pdf containing bill information"""
    bill = BillingPreview.objects.get(pk=bill_id)

    ppdbill = ProvisionalProductBilling.objects.filter(billing__id=bill_id, product__product_name='ppd')
    codbill = ProvisionalProductBilling.objects.filter(billing__id=bill_id, product__product_name='cod')
    ebsppdbill = ProvisionalProductBilling.objects.filter(billing__id=bill_id, product__product_name='ebsppd')
    ebscodbill = ProvisionalProductBilling.objects.filter(billing__id=bill_id, product__product_name='ebscod')
    revbill = ProvisionalProductBilling.objects.filter(billing__id=bill_id, product__product_name='rev')
    if ppdbill.exists():
        ppdbill = ppdbill[0]
        ship_count = int(ppdbill.shipment_count) if ppdbill.shipment_count else 0
        ppdlist = [ 'PPD', ppdbill.billing.customer.code, ppdbill.billing.customer.name,
            ppdbill.billing.billing_date, ppdbill.billing.id, ship_count, ppdbill.total_chargeable_weight,
            ppdbill.freight_charge, ppdbill.fuel_surcharge, ppdbill.sdl_charge,
            ppdbill.sdd_charge, ppdbill.reverse_charge, '', 
            ppdbill.valuable_cargo_handling_charge, ppdbill.cod_applied_charge,
            ppdbill.cod_subtract_charge, ppdbill.cod_applied_charge + ppdbill.cod_subtract_charge, '', 
            ppdbill.total_charge_pretax, ppdbill.service_tax, ppdbill.education_secondary_tax, 
            ppdbill.cess_higher_secondary_tax, ppdbill.total_payable_charge]
    else:
        ppdlist = [0]*22
        ppdlist[0] = 'PPD'

    if codbill.exists():
        codbill = codbill[0]
        ship_count = int(codbill.shipment_count) if codbill.shipment_count else 0
        codlist = [ 'COD', codbill.billing.customer.code, codbill.billing.customer.name,
            codbill.billing.billing_date, codbill.billing.id, ship_count, codbill.total_chargeable_weight,
            codbill.freight_charge, codbill.fuel_surcharge, codbill.sdl_charge,
            codbill.sdd_charge, codbill.reverse_charge, '', codbill.valuable_cargo_handling_charge,
            codbill.cod_applied_charge, codbill.cod_subtract_charge, codbill.total_cod_charge, '', 
            codbill.total_charge_pretax, codbill.service_tax, codbill.education_secondary_tax, 
            codbill.cess_higher_secondary_tax, codbill.total_payable_charge]
    else:
        codlist = [0]*22
        codlist[0] = 'COD'

    if ebsppdbill.exists():
        ebsppdbill = ebsppdbill[0]
        ship_count = int(ebsppdbill.shipment_count) if ebsppdbill.shipment_count else 0
        ebsppdlist = [ 'EBSPPD', ebsppdbill.billing.customer.code, ebsppdbill.billing.customer.name,
            ebsppdbill.billing.billing_date, ebsppdbill.billing.id, ship_count, ebsppdbill.total_chargeable_weight,
            ebsppdbill.freight_charge, ebsppdbill.fuel_surcharge, ebsppdbill.sdl_charge,
            ebsppdbill.sdd_charge, ebsppdbill.reverse_charge, '', ebsppdbill.valuable_cargo_handling_charge,
            ebsppdbill.cod_applied_charge, ebsppdbill.cod_subtract_charge, ebsppdbill.total_cod_charge, '', 
            ebsppdbill.total_charge_pretax, ebsppdbill.service_tax, ebsppdbill.education_secondary_tax, 
            ebsppdbill.cess_higher_secondary_tax, ebsppdbill.total_payable_charge]
    else:
        ebsppdlist = [0]*22
        ebsppdlist[0] = 'EBSPPD'

    if ebscodbill.exists():
        ebscodbill = ebscodbill[0]
        ship_count = int(ebscodbill.shipment_count) if ebscodbill.shipment_count else 0
        ebscodlist = [ 'EBSCOD', ebscodbill.billing.customer.code, ebscodbill.billing.customer.name,
            ebscodbill.billing.billing_date, ebscodbill.billing.id, ship_count, ebscodbill.total_chargeable_weight,
            ebscodbill.freight_charge, ebscodbill.fuel_surcharge, ebscodbill.sdl_charge,
            ebscodbill.sdd_charge, ebscodbill.reverse_charge, '', ebscodbill.valuable_cargo_handling_charge,
            ebscodbill.cod_applied_charge, ebscodbill.cod_subtract_charge, ebscodbill.total_cod_charge, '', 
            ebscodbill.total_charge_pretax, ebscodbill.service_tax, ebscodbill.education_secondary_tax, 
            ebscodbill.cess_higher_secondary_tax, ebscodbill.total_payable_charge]
    else:
        ebscodlist = [0]*22
        ebscodlist[0] = 'EBSCOD'

    if revbill.exists():
        revbill = revbill[0]
        ship_count = int(revbill.shipment_count) if revbill.shipment_count else 0
        revlist = [ 'REVERSE', revbill.billing.customer.code, revbill.billing.customer.name,
            revbill.billing.billing_date, revbill.billing.id, ship_count, revbill.total_chargeable_weight,
            revbill.freight_charge, revbill.fuel_surcharge, revbill.sdl_charge,
            revbill.sdd_charge, revbill.reverse_charge, '', revbill.valuable_cargo_handling_charge,
            revbill.cod_applied_charge, revbill.cod_subtract_charge, revbill.total_cod_charge, '', 
            revbill.total_charge_pretax, revbill.service_tax, revbill.education_secondary_tax, 
            revbill.cess_higher_secondary_tax, revbill.total_payable_charge]
    else:
        revlist = [0]*22
        revlist[0] = 'REVERSE'

    data = [ppdlist, codlist, ebsppdlist, ebscodlist, revlist,
        ['Total', bill.customer.code, bill.customer.name, '', bill.id, bill.shipment_count, bill.total_chargeable_weight, bill.freight_charge,
        bill.fuel_surcharge, bill.sdl_charge, bill.sdd_charge, bill.reverse_charge, '', bill.valuable_cargo_handling_charge,
        bill.cod_applied_charge, bill.cod_subtract_charge, bill.total_cod_charge, '', bill.total_charge_pretax, bill.service_tax,
        bill.education_secondary_tax, bill.cess_higher_secondary_tax, bill.total_payable_charge]]
    return data

def generate_provisional_bill_summary_xls(bill_list):
    col_heads=(
        'Product', 'code', 'Customer', 'Billing Date', 'Bill No', 'Shipment Count',
        'Weight ', 'Freight', 'Fuel', 'SDL', 'SDD', 'Reverse', 'TNB', 'VCHC Charge',
        'COD Applied', 'COD reversed', 'COD Final', 'Discount', 'Total Pre Tax',
        'Service Tax', 'Edu Cess', 'Hsc ', 'Total With Tax')

    col_count = len(col_heads)
    # add filename and set save file path
    if bill_list:
        file_name = get_bill_summary_filename(bill_list[0], 'provisional_bill_summary', 'xlsx')
    else:
        file_name = get_bill_summary_filename(None, 'provisional_bill_summary', 'xlsx', none_bill=True)
    #path_to_save =   os.path.join(pdf_home, file_name)
    workbook = Workbook(file_name)

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

    # write data to excel sheet
    #print '5.3.3 writing data to excel file..'
    data_matrix = []
    for bill_id in bill_list:
        l = get_bill_summary_data(bill_id)
        data_matrix.extend(l)

    total_row = defaultdict(float)
    row_count = 3
    for row, data_list in enumerate(data_matrix, start=3):
        #print '5.3.4.1 writing row to excel file..', row
        row_count += 1
        for col, val in enumerate(data_list):
            if not val:
                continue
            if col > 5 and val:
                val = Decimal(float(val)).quantize(TW)

            #if data_list[0] != 'Total':
            if col > 4:
               sheet.write_number(row, col, val)
            else:
               sheet.write_string(row, col, str(val))

            if data_list[0] == 'Total':
                if int(col) == 5 and val:
                    total_row['ship_count'] += int(val)
                elif int(col) == 6 and val:
                    total_row['tot_wt'] += float(val)
                elif int(col) == 7 and val:
                    total_row['tot_ft'] += float(val)
                elif int(col) == 8 and val:
                    total_row['tot_fl'] += float(val)
                elif int(col) == 9 and val:
                    total_row['tot_sdl'] += float(val)
                elif int(col) == 10 and val:
                    total_row['tot_sdd'] += float(val)
                elif int(col) == 11 and val:
                    total_row['tot_reverse'] += float(val)
                elif int(col) == 12 and val:
                    total_row['tot_tnb'] += float(val)
                elif int(col) == 13 and val:
                    total_row['tot_cod'] += float(val)
                elif int(col) == 14 and val:
                    total_row['tot_rev'] += float(val)
                elif int(col) == 15 and val:
                    total_row['tot_cod_final'] += float(val)
                elif int(col) == 16 and val:
                    total_row['tot_disc'] += float(val)
                elif int(col) == 17 and val:
                    total_row['tot_tpt'] += float(val)
                elif int(col) == 18 and val:
                    total_row['tot_st'] += float(val)
                elif int(col) == 19 and val:
                    total_row['tot_ec'] += float(val)
                elif int(col) == 20 and val:
                    total_row['tot_hsc'] += float(val)
                elif int(col) == 21 and val:
                    total_row['tot_tot'] += float(val)

    # writing totals row
    sheet.write_number(row_count, 5, int(total_row['ship_count']))
    sheet.write_number(row_count, 6, Decimal(total_row['tot_wt']).quantize(TW))
    sheet.write_number(row_count, 7, Decimal(total_row['tot_ft']).quantize(TW))
    sheet.write_number(row_count, 8, Decimal(total_row['tot_fl']).quantize(TW))
    sheet.write_number(row_count, 9, Decimal(total_row['tot_sdl']).quantize(TW))
    sheet.write_number(row_count, 10, Decimal(total_row['tot_sdd']).quantize(TW))
    sheet.write_number(row_count, 11, Decimal(total_row['tot_reverse']).quantize(TW))
    sheet.write_number(row_count, 12, Decimal(total_row['tot_tnb']).quantize(TW))
    sheet.write_number(row_count, 13, Decimal(total_row['tot_cod']).quantize(TW))
    sheet.write_number(row_count, 14, Decimal(total_row['tot_rev']).quantize(TW))
    sheet.write_number(row_count, 15, Decimal(total_row['tot_cod_final']).quantize(TW))
    sheet.write_number(row_count, 16, Decimal(total_row['tot_disc']).quantize(TW))
    sheet.write_number(row_count, 17, Decimal(total_row['tot_tpt']).quantize(TW))
    sheet.write_number(row_count, 18, Decimal(total_row['tot_st']).quantize(TW))
    sheet.write_number(row_count, 19, Decimal(total_row['tot_ec']).quantize(TW))
    sheet.write_number(row_count, 20, Decimal(total_row['tot_hsc']).quantize(TW))
    sheet.write_number(row_count, 21, Decimal(total_row['tot_tot']).quantize(TW))

    workbook.close()
    return file_name
