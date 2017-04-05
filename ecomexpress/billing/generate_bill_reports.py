'''
Created on 29-May-2013

@author: prtouch
'''
import datetime
import os
import subprocess
import pyPdf
from decimal import *
from xlsxwriter.workbook import Workbook

from django.conf import settings
from django.db.models import Sum

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate,\
    Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT, TA_CENTER
from service_centre.models import *
from billing.models import Billing, ProductBilling, CustomerBillingReport, BillingQueue
from service_centre.models import get_internal_shipment_status, Shipment
from customer.models import Product,Customer
from reports.report_api import ReportGenerator
from customer.models import *
from reports.ecomm_mail import ecomm_send_mail
from billing.generate_bill_pdf import get_filename
TW = Decimal(10) ** -2


class GenerateReport(object):

    def __init__(self):
        self.PDF_HOME = settings.PROJECT_ROOT_DIR + settings.STATIC_URL + 'uploads/billing/'

    def get_filename(self, name, ext, index=None):
        customer = self.billing.customer
        cust_name = customer.name.replace(' ', '_')
        bill_date = self.billing.billing_date# + datetime.timedelta(days=1)
        billing_date = bill_date.strftime('%Y_%m_%d')
        month = self.billing.billing_date.strftime('%m')
        year = self.billing.billing_date.strftime('%Y')
        if index:
            file_name = '%s/%s/%s_%s_%s_%s_%s.%s' % (
                str(year),
                str(month),
                str(name),
                str(cust_name),
                str(self.billing.id),
                str(billing_date),
                str(index),
                str(ext))
        else:
            file_name = '%s/%s/%s_%s_%s_%s.%s' % (
                str(year),
                str(month),
                str(name),
                str(cust_name),
                str(self.billing.id),
                str(billing_date),
                str(ext))
        full_file_name = os.path.join(self.PDF_HOME, file_name)
        return full_file_name


class GeneratePdf(GenerateReport):

    def __init__(self):
        GenerateReport.__init__(self)
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='AWB_heading',
                                  alignment=TA_CENTER,
                                  fontSize=6))
        self.styles.add(ParagraphStyle(name='AWB_heading_right',
                                  alignment=TA_RIGHT,
                                  fontSize=6))
        self.styles.add(ParagraphStyle(name='Text6', fontSize=6))
        self.styles.add(ParagraphStyle(name='BoldRight',
                                  alignment=TA_RIGHT,
                                  fontSize=6))
        self.styles.add(ParagraphStyle(name='ImpPara',
                                  alignment=TA_LEFT,
                                  fontSize=7))
        self.styles.add(ParagraphStyle(name='InvoiceHead',
                                  alignment=TA_CENTER,
                                  textColor="black"))
        self.styles.add(ParagraphStyle(name='InvoicePara',
                                  alignment=TA_LEFT,
                                  spaceBefore=0,
                                  spaceAfter=0,
                                  leading=12,
                                  leftIndent=18,
                                  rightIndent=32,
                                  fontSize=10))
        self.styles.add(ParagraphStyle(name='AwbHead',
                                  alignment=TA_LEFT,
                                  spaceBefore=0,
                                  spaceAfter=0,
                                  leading=9,
                                  leftIndent=32,
                                  rightIndent=32,
                                  fontSize=6))
        self.styles.add(ParagraphStyle(name='CustCodeHead',
                                  alignment=TA_CENTER,
                                  #textColor="white",
                                  fontSize=6))
        self.styles.add(ParagraphStyle(name='BillHeadL',
                                  alignment=TA_LEFT,
                                  spaceBefore=0,
                                  spaceAfter=0,
                                  leading=9,
                                  fontSize=8))
        self.styles.add(ParagraphStyle(name='BillHeadR',
                                  alignment=TA_LEFT,
                                  spaceBefore=0,
                                  spaceAfter=0,
                                  leading=9,
                                  leftIndent=32,
                                  rightIndent=32,
                                  fontSize=8))

class GenerateAwbPdf(GeneratePdf):

    def __init__(self, bill_id):
        GeneratePdf.__init__(self)
        self.bill_id = bill_id
        self.billing = Billing.objects.get(id=bill_id)
        self.shipments = self.billing.shipments
        self.awb_files = []
        self.PDF_CHUNK_SIZE = 594

    def awbpara(self, arg, style):
        return Paragraph('<b>'+ arg +'</b>', self.styles[style])

    def delete_awb_chunks(self):
        try:
            for filename in self.awb_files:
                os.remove(filename)
        except OSError:
            pass

    def pdf_to_ps(self, file_name):
        """ Convert pdf files to ps files."""
        ps_filename = file_name[:-2] + 's'
        subprocess.Popen(['pdftops', file_name, ps_filename])
        return ps_filename

    def generate_pdf_by_ptype(self, ptype):
        #print '2.',ptype
        #ships_count = self.billing.shipments.filter(shipext__product__product_name=ptype).only('id').count()
        product = Product.objects.get(product_name=ptype)
        pbill = ProductBilling.objects.filter(billing=self.billing, product=product)
        if pbill.only('id').exists():
            ships_count = int(pbill[0].shipment_count)
        else:
            ships_count = 0
            return None

        for index in xrange(1, ships_count+1, self.PDF_CHUNK_SIZE):
            if index + self.PDF_CHUNK_SIZE > ships_count:
                add_total = True
            else:
                add_total = False

            file_name = self.generate_awb_pdf_chunk(index, ptype, add_total)
            self.awb_files.append(file_name)

        return

    def generate_combined_pdf(self):
        #print '5.generating combined pdf'
        #combine all filenames and create combined pdf file
        full_file_name = self.get_filename('awb_wise', 'pdf')
        output = pyPdf.PdfFileWriter()
        for dfile in self.awb_files:
            fileName, fileExt = os.path.splitext(dfile)
            if fileExt != '.pdf':
                continue
            f = open(dfile, 'rb')
            inputf = pyPdf.PdfFileReader(f)
            for page in range(inputf.getNumPages()):
                output.addPage(inputf.getPage(page))

        filename = self.get_filename('awb_wise', 'pdf')
        outs = open(filename, 'wb')
        output.write(outs)
        outs.close()
        return filename

    def get_awb_table_data(self, ptype, index):
        product = Product.objects.get(product_name=ptype)
        awb_shipments = self.shipments.filter(shipext__product=product)[index-1:index-1+self.PDF_CHUNK_SIZE]
        current_index = index - 1
        if not awb_shipments.only('id').count():
            yield [[0]*21]

        for shipment in awb_shipments:
            current_index += 1
            cod_charge = shipment.codcharge_set.all()
            codcharge = cod_charge[0].cod_charge if cod_charge.count() else 0
            op = shipment.order_price_set.all()

            sub_cust_code = str(shipment.shipper.code) + str(shipment.pickup.subcustomer_code.id)

            if shipment.original_dest :
                destn = shipment.original_dest.center_name
            elif shipment.service_centre:
                destn = shipment.service_centre.center_name
            else:
                destn =  ''

            if op.exists():
                op = op[0]
                frt_chg = Decimal(op.freight_charge).quantize(TW)
                # get others charge
                other_price = op.sdl_charge + \
                        op.rto_charge + \
                        op.to_pay_charge + \
                        op.valuable_cargo_handling_charge
                others = Decimal(other_price).quantize(TW)
                fuel_sc = op.fuel_surcharge

                # get total
                total_op = op.sdl_charge + \
                        op.rto_charge + \
                        op.to_pay_charge + \
                        op.freight_charge + \
                        op.reverse_charge + \
                        op.sdd_charge + \
                        op.valuable_cargo_handling_charge

                revchg = op.reverse_charge
                sddchg = op.sdd_charge
            else:
                frt_chg = 0
                other_price = 0
                others = 0
                fuel_sc = 0
                total_op = 0
                revchg = 0
                sddchg = 0

            if shipment.rts_status != 1:
                ship_total = Decimal(total_op + codcharge).quantize(TW)
                ship_cod = Decimal(codcharge).quantize(TW)
            else:
                ship_total = Decimal(total_op - codcharge).quantize(TW)
                ship_cod = Decimal(0-codcharge).quantize(TW)

            origin = shipment.pickup.service_centre.center_name
            status = get_internal_shipment_status(shipment.status)
            parent_awb = shipment.ref_airwaybill_number
            parent_awb_date = shipment.rts_date
            ord_num = shipment.order_number
            ord_num = ord_num.encode('ascii', 'ignore') if isinstance(ord_num, unicode) else str(ord_num)

            ls = [str(current_index),
                 sub_cust_code,
                 str(shipment.airwaybill_number),
                 ord_num,
                 shipment.added_on.strftime('%d/%m/%y'),
                 destn,
                 str(shipment.chargeable_weight),
                 str(frt_chg),
                 str(ship_cod),
                 str(revchg),
                 str(sddchg),
                 str(others),
                 str(ship_total)]
            yield ls

    def get_awb_table_totals_row(self, ptype=None):
        if ptype:
            pbilling = ProductBilling.objects.filter(billing__id=self.bill_id, product__product_name=ptype)
            if not pbilling.exists():
                return [0]*13
            else:
                pbilling = pbilling[0]

        else:
            pbilling = self.billing

        row = ['', '', '', '', '', 'TOTAL',
            Decimal(pbilling.total_chargeable_weight).quantize(TW),
            Decimal(pbilling.freight_charge).quantize(TW),
            Decimal(pbilling.total_cod_charge).quantize(TW),
            Decimal(pbilling.reverse_charge).quantize(TW),
            Decimal(pbilling.sdd_charge).quantize(TW),
            Decimal(pbilling.valuable_cargo_handling_charge + pbilling.rto_charge + pbilling.to_pay_charge).quantize(TW),
            Decimal(pbilling.total_charge_pretax - pbilling.fuel_surcharge).quantize(TW)]
        return row

    def get_awb_total_table(self, ptype=None):
        if ptype:
            billing = ProductBilling.objects.filter(billing__id=self.bill_id, product__product_name=ptype)[0]
        else:
            billing = Billing.objects.get(pk=self.bill_id)

        awb_total_table = [
            ['Gross Total', Decimal(billing.total_charge_pretax - billing.fuel_surcharge).quantize(TW)],
            ['Fuel Surcharge', Decimal(billing.fuel_surcharge).quantize(TW)],
            ['Total Before Tax', Decimal(billing.total_charge_pretax).quantize(TW)],
            ['Service Tax',	Decimal(billing.service_tax).quantize(TW)],
            ['Education Cess', Decimal(billing.education_secondary_tax).quantize(TW)],
            ['HSE Cess', Decimal(billing.cess_higher_secondary_tax).quantize(TW)],
            ['Grand Total',	Decimal(round(billing.total_payable_charge,0)).quantize(TW)]
        ]

        total_table = Table(awb_total_table,
                splitByRow=True,
                repeatRows=1,
                repeatCols=2)

        total_table.setStyle(TableStyle([
            ('ALIGN',(0,0),(0,-1),'RIGHT'),
            ('ALIGN',(1,0),(1,-1),'LEFT'),
            ]))

        total_table.hAlign = 'RIGHT'
        return total_table

    def generate_awb_pdf_chunk(self, index, ptype, add_total):
        """ This function will take a chunk(self.chunk_size) of shipments
        and generate awb_wise pdf file.
        generate_awb_pdf_chunk(int, 'cod'/'ppd', bool) --> return file_name
        """
        #print '3.',index
        file_name = self.get_filename('awb_wise_'+ptype, 'pdf', index)
        full_file_name = os.path.join(self.PDF_HOME, file_name)
        doc = SimpleDocTemplate(full_file_name, pagesize=A4, topMargin=30,
                  bottomMargin=30, leftMargin=30, rightMargin=30)

        # container for the 'Flowable' objects we add the para, tables to this
        # flowable and generate pdf at the end
        elements = []
        # page header
        if index == 1:
            page_header1 = self.awbpara('AirwayBill wise charges', "AWB_heading")
            elements.append(page_header1)

            para = '''
                <para spaceb=3>
                <b>Customer Name:</b> {0}<br/>
                <b>Bill No:</b> {1}<br/>
                <b>Bill Period:</b> {2} to {3}<br/>
                <b>Product Type:</b> {4}<br/>
                </para>'''.format(self.billing.customer.name, self.billing.id,
                                  self.billing.billing_date_from.strftime("%d/%m/%Y"),
                                  self.billing.billing_date.strftime("%d/%m/%Y"),
                                  ptype)

            page_header2 = Paragraph(para, self.styles["AwbHead"])

            main_header_data = [['', page_header2]]
            main_header_table = Table(main_header_data, colWidths=(300, 260))
            main_header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ]))
            elements.append(main_header_table)
            elements.append(Spacer(1, 2))

        awb_table_headers = [
            self.awbpara('Sl No', "AWB_heading"),
            self.awbpara('Cust Code', "AWB_heading"),
            self.awbpara('Air Waybill No', "AWB_heading"),
            self.awbpara('Order No', "AWB_heading"),
            self.awbpara('Date', "AWB_heading"),
            self.awbpara('Destination', "AWB_heading"),
            self.awbpara('Weight', "AWB_heading"),
            self.awbpara('Freight', "AWB_heading"),
            self.awbpara('COD', "AWB_heading"),
            self.awbpara('Reverse', "AWB_heading"),
            self.awbpara('SDD', "AWB_heading"),
            self.awbpara('Others', "AWB_heading"),
            self.awbpara('Total', "AWB_heading")
        ]

        awb_table_data = list(self.get_awb_table_data(ptype, index))
        awb_table_data.insert(0, awb_table_headers)
        rowheights = [10]*len(awb_table_data)

        if add_total:
            awb_table_totals_row = self.get_awb_table_totals_row(ptype)
            awb_table_data.append(awb_table_totals_row)
            rowheights.append(12)

        awb_table = Table(awb_table_data,
                splitByRow=True,
                repeatRows=1,
                rowHeights=rowheights,
                colWidths=(30, 50, 50, 65, 40, 80, 35, 35, 35, 30, 30, 30, 50))
        awb_table.setStyle(TableStyle([
            ('ALIGN',(0, 0), (-1, 0), 'CENTER'),
            ('ALIGN',(0, 1), (4, -1), 'CENTER'),
            ('ALIGN',(5, 1), (5, -1), 'LEFT'),
            ('ALIGN',(6, 1), (-1, -1), 'RIGHT'),
            ('VALIGN',(0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',(0, 0), (-1, -1), 5),
            #('BOTTOMPADDING',(0, 0), (-1, -1), 5),
            ('LEFTPADDING',(2, 0), (2, -1), 1),
            ('FONTSIZE',(0, 0),(-1, 0), 6),
            ('FONTSIZE',(0, 1),(-1, -1), 6),
            ('INNERGRID', (0,0), (-1, -1), 0.25, colors.black),
            ('BOX', (0,0), (-1, -1), 0.25, colors.black),
            ]))

        if add_total:
            elements.append(awb_table)
            awb_total = self.get_awb_total_table(ptype)
            elements.append(Spacer(1, 12))
            elements.append(awb_total)
        else:
            elements.append(awb_table)

        doc.build(elements)
        #print full_file_name
        return full_file_name

    def generate_awb_pdf(self):
        """ create multiple pdf files for each product types and combines them in the end."""
        #print '1. generate awb pdf'
        if not self.billing.shipment_count:
            return None

        # first generate separate pdf files for each product type.
        # each product type pdf will be split into chunk files of shipment
        # count as specified by chunks size
        self.generate_pdf_by_ptype('cod')
        self.generate_pdf_by_ptype('ppd')
        self.generate_pdf_by_ptype('ebscod')
        self.generate_pdf_by_ptype('ebsppd')
        self.generate_pdf_by_ptype('rev')

        file_name = self.generate_combined_pdf()
        self.delete_awb_chunks()
        #self.pdf_to_ps(file_name)
        return file_name

# generate billwise excel
class GenerateAwbExcel(GenerateReport):

    def __init__(self, bill_id):
        GenerateReport.__init__(self)
        self.bill_id = bill_id
        self.billing = Billing.objects.get(id=bill_id)
        self.row_num = 0
        self.col_heads = (
            'Sl No',
            'Cust/Sub Cust Code',
            'Air Waybill No',
            'Order No',
            'Date',
            'Service',
            'Destination',
            'Origin',
            'Weight',
            'Collectable Charge',
            'Freight',
            'COD',
            'Reverse',
            'SDD',
            'Others',
            'Fuel SC',
            'Total',
            'Pincode',
            'Status',
            'Parent/RTS AWB',
            'Parent/RTS AWB Date',
            'RTS')
        self.file_name = self.get_filename('awb_excel', 'xlsx')
        self.path_to_save = os.path.join(self.PDF_HOME, self.file_name)
        self.workbook = Workbook(self.path_to_save)
        self.sheet = self.workbook.add_worksheet()

        # define style formats for header and data
        self.header_format = self.workbook.add_format()
        self.header_format.set_bg_color('yellow')
        self.header_format.set_bold()

    def write_header(self, ptype):
        self.row_num += 1
        self.sheet.write(self.row_num+1, 5, 'Customer Name: ' + self.billing.customer.name)
        self.sheet.write(self.row_num+2, 5, 'Bill No: '+str(self.billing.id))

        bill_period = 'Bill Period: ' + self.billing.billing_date_from.strftime('%Y-%m-%d') +\
                ' To ' + self.billing.billing_date.strftime('%Y-%m-%d')

        self.sheet.write(self.row_num+3, 5, bill_period)
        self.sheet.write(self.row_num+4, 5, 'Products Type: '+ptype)
        for col, name in enumerate(self.col_heads):
            self.sheet.write(self.row_num+6, col, name, self.header_format)
        self.row_num += 6

    def get_awb_total_table_data(self, ptype=None):
        if ptype:
            billing = ProductBilling.objects.filter(billing__id=self.bill_id, product__product_name=ptype)
            if not billing.exists():
                return [['Total'],[],[],[],[],[],[]]
            else:
                billing = billing[0]
            total_collectable_value = self.billing.shipments.filter(shipext__product__product_name=ptype)\
                .aggregate(tot=Sum('collectable_value'))['tot']
            total_str = 'Total'
        else:
            billing = self.billing
            total_str = 'Grand Total'
            total_collectable_value = self.billing.shipments.all().aggregate(tot=Sum('collectable_value'))['tot']
        total_other_charge = Decimal(billing.sdl_charge + billing.rto_charge + billing.to_pay_charge + billing.valuable_cargo_handling_charge).quantize(TW)
        gross_total = Decimal(billing.total_charge_pretax - billing.fuel_surcharge).quantize(TW)
        total_row = ['','','','',total_str, billing.total_chargeable_weight, total_collectable_value,
                billing.freight_charge, billing.total_cod_charge, billing.reverse_charge, billing.sdd_charge,
                total_other_charge, billing.fuel_surcharge, gross_total]
        awb_total_table = [total_row,
            ['Gross Total', gross_total],
            ['Fuel Surcharge', Decimal(billing.fuel_surcharge).quantize(TW)],
            ['Total Before Tax', Decimal(billing.total_charge_pretax).quantize(TW)],
            ['Service Tax',	Decimal(billing.service_tax).quantize(TW)],
            ['Education Cess', Decimal(billing.education_secondary_tax).quantize(TW)],
            ['HSE Cess', Decimal(billing.cess_higher_secondary_tax).quantize(TW)],
            ['Grand Total',	Decimal(round(billing.total_payable_charge,0)).quantize(TW)]
        ]
        return awb_total_table

    def get_awb_table_data_direct(self, ptype):
        product = Product.objects.get(product_name=ptype)
        shipments = self.billing.shipments.filter(shipext__product=product)
        if not shipments.only('id').count():
            yield [[0]*21]

        for index, shipment in enumerate(shipments, start=1):
            cod_charge = shipment.codcharge_set.all()
            codcharge = cod_charge[0].cod_charge if cod_charge.count() else 0
            op = shipment.order_price_set.all()

            try:
                sub_cust_code = str(shipment.shipper.code) + \
                      str(shipment.pickup.subcustomer_code.id) + '-' +\
                      str(shipment.pickup.subcustomer_code.name)
            except:
                sub_cust_code = str(shipment.shipper.code)

            if shipment.original_dest :
                destn = shipment.original_dest.center_name
            elif shipment.service_centre:
                destn = shipment.service_centre.center_name
            else:
                destn =  ''

            if op.exists():
                op = op[0]
                frt_chg = Decimal(op.freight_charge).quantize(TW)
                # get others charge
                other_price = op.sdl_charge + \
                        op.rto_charge + \
                        op.to_pay_charge + \
                        op.valuable_cargo_handling_charge
                others = Decimal(other_price).quantize(TW)
                fuel_sc = op.fuel_surcharge

                # get total
                total_op = op.sdl_charge + \
                        op.rto_charge + \
                        op.to_pay_charge + \
                        op.freight_charge + \
                        op.reverse_charge + \
                        op.sdd_charge + \
                        op.valuable_cargo_handling_charge

                revchg = op.reverse_charge
                sddchg = op.sdd_charge
            else:
                frt_chg = 0
                other_price = 0
                others = 0
                fuel_sc = 0
                total_op = 0
                revchg = 0
                sddchg = 0

            if shipment.rts_status != 1:
                ship_total = Decimal(total_op + codcharge).quantize(TW)
                ship_cod = Decimal(codcharge).quantize(TW)
            else:
                ship_total = Decimal(total_op - codcharge).quantize(TW)
                ship_cod = Decimal(0-codcharge).quantize(TW)

            origin = shipment.pickup.service_centre.center_name
            status = get_internal_shipment_status(shipment.status)
            parent_awb = shipment.ref_airwaybill_number
            parent_awb_date = shipment.rts_date
            if shipment.ref_airwaybill_number:
                ref_shipment = Shipment.objects.filter(airwaybill_number=shipment.ref_airwaybill_number)
                if ref_shipment.exists():
                    parent_awb_date = ref_shipment[0].shipment_date
                else:
                    #print 'reference awb does not exits ', shipment.ref_airwaybill_number
                    parent_awb_date =  ''
            rts_status = shipment.rts_status
            try:
                pincode = shipment.shipext.original_pincode
            except:
                pincode = shipment.pincode

            yield [index,
                 sub_cust_code,
                 shipment.airwaybill_number,
                 shipment.order_number,
                 shipment.added_on.strftime('%d/%m/%y'),
                 shipment.product_type,
                 destn,
                 origin, # to add
                 shipment.chargeable_weight,
                 shipment.collectable_value,
                 frt_chg,
                 ship_cod,
                 revchg,
                 sddchg,
                 others,
                 fuel_sc, #to add
                 ship_total,
                 pincode,
                 status, #to add,
                 parent_awb, #to add
                 parent_awb_date,
                 rts_status]

    def write_gen_data(self, data_list_gen):
        for data_list in data_list_gen:
            self.row_num += 1
            for col, val in enumerate(data_list):
                val = val.encode('ascii', 'ignore') if isinstance(val, unicode) else str(val)
                self.sheet.write_string(self.row_num, col, val)

    def write_awb_total(self, awb_total_table):
        for row, data_list in enumerate(awb_total_table, start=self.row_num+1):
            self.row_num+=1
            for col, val in enumerate(data_list, start=3):
                self.sheet.write_string(row, col, str(val))

    def generate_awb_excel(self):
        col_count = len(self.col_heads)
        self.sheet.set_column(0, col_count, 12) # set column width
        self.sheet.write(0, 2, "AirwayBill Wise Charges")

        # COD SECTION ####################
        codproduct = Product.objects.get(product_name='cod')
        cod_shipments = self.billing.shipments.filter(shipext__product=codproduct).only('id').exists()
        if cod_shipments:
            self.write_header('COD')

            cod_data_gen = self.get_awb_table_data_direct('cod')
            self.write_gen_data(cod_data_gen)

            cod_total_table = self.get_awb_total_table_data('cod')
            self.write_awb_total(cod_total_table)

        # PPD SECTION ####################
        ppdproduct = Product.objects.get(product_name='ppd')
        ppd_shipments = self.billing.shipments.filter(shipext__product=ppdproduct).only('id').exists()
        if ppd_shipments:
            self.write_header('PPD')

            ppd_data_gen = self.get_awb_table_data_direct('ppd')
            self.write_gen_data(ppd_data_gen)

            ppd_total_table = self.get_awb_total_table_data('ppd')
            self.write_awb_total(ppd_total_table)

        # EBSCOD SECTION ####################
        ebscodproduct = Product.objects.get(product_name='ebscod')
        ebscod_shipments = self.billing.shipments.filter(shipext__product=ebscodproduct).only('id').exists()
        if ebscod_shipments:
            self.write_header('EBSCOD')

            ebscod_data_gen = self.get_awb_table_data_direct('ebscod')
            self.write_gen_data(ebscod_data_gen)

            ebscod_total_table = self.get_awb_total_table_data('ebscod')
            self.write_awb_total(ebscod_total_table)

        # PPD SECTION ####################
        ebsppdproduct = Product.objects.get(product_name='ebsppd')
        ebsppd_shipments = self.billing.shipments.filter(shipext__product=ebsppdproduct).only('id').exists()
        if ebsppd_shipments:
            self.write_header('EBSPPD')

            ebsppd_data_gen = self.get_awb_table_data_direct('ebsppd')
            self.write_gen_data(ebsppd_data_gen)

            ebsppd_total_table = self.get_awb_total_table_data('ebsppd')
            self.write_awb_total(ebsppd_total_table)

        # REV SECTION ####################
        revproduct = Product.objects.get(product_name='rev')
        ebscod_shipments = self.billing.shipments.filter(shipext__product=revproduct).only('id').exists()
        if ebscod_shipments:
            self.write_header('REV SHIPS')

            rev_data_gen = self.get_awb_table_data_direct('rev')
            self.write_gen_data(rev_data_gen)

            rev_total_table = self.get_awb_total_table_data('rev')
            self.write_awb_total(rev_total_table)

        # GRAND TOTAL
        awb_total_table = self.get_awb_total_table_data()
        self.sheet.write_string(self.row_num+2, 0, 'GRAND TOTAL FOR ALL PRODUCTS')
        self.row_num += 1
        self.write_awb_total(awb_total_table)

        self.workbook.close()
        return self.file_name

def generate_awbpdf_report(bill_id):
    gen_awb = GenerateAwbPdf(bill_id)
    awb_pdf = gen_awb.generate_awb_pdf()
    return awb_pdf

def generate_awbexcel_report(bill_id):
    gen_excel = GenerateAwbExcel(bill_id)
    awb_exl = gen_excel.generate_awb_excel()
    return awb_exl

def generate_all_awb_reports(bills_list):
    download_files = []
    for bill_id in bills_list:
        gen_awb = GenerateAwbPdf(bill_id)
        awb_pdf = gen_awb.generate_awb_pdf()
        #print 'awb pdf file is :', awb_pdf
        gen_excel = GenerateAwbExcel(bill_id)
        awb_exl = gen_excel.generate_awb_excel()
        download_files.append(awb_pdf)
        download_files.append(awb_exl)
    print 'pdf generation completed...', download_files

def bill_report(year,month):
    report = ReportGenerator('consolidated_billing_reports_{0}_{1}.xlsx'.format(year, month))
    report.write_header(('Bill_id', 'Customer Name','Invoice Summary','Invoice Summary(headless)',
        'Awb Excel','Awb Pdf'))
    bills = Billing.objects.filter(billing_date__year=year,billing_date__month =month )
    month_str = str(month)
    if len(month_str) == 1:
        month_str = '0' + month_str
    for bill in bills:
        bill_id = bill.id
        in_summary_url = get_filename(bill_id, 'bill_wise', 'pdf')
        in_summary ='http://billing.ecomexpress.in/static/uploads/billing/'+month_str+'/'+os.path.split(in_summary_url)[1]

        in_summary_with_header_url = get_filename(bill_id, 'bill_wise_without_header', 'pdf')
        in_summary_with_header ='http://billing.ecomexpress.in/static/uploads/billing/'+str(month)+'/'+os.path.split(in_summary_with_header_url)[1]
        customer_name = bill.customer.name
        print bill_id
        gen_awb = GenerateAwbPdf(bill_id)
        awb_pdf_url = gen_awb.get_filename('awb_wise', 'pdf')
        awb_pdf ='http://billing.ecomexpress.in/static/uploads/billing/'+str(month)+'/'+os.path.split(awb_pdf_url)[1]
        awb_excel_url = gen_awb.get_filename('awb_excel', 'xlsx')
        awb_excel ='http://billing.ecomexpress.in/static/uploads/billing/'+str(month)+'/'+os.path.split(awb_excel_url)[1]
        report.write_row((bill_id,customer_name,in_summary,in_summary_with_header,awb_excel,awb_pdf))
    file_name = report.manual_sheet_close()
    path = 'http://billing.ecomexpress.in/static/uploads/reports/'+file_name
    print path

def ebs_shipments_report(bill_id):
    report = ReportGenerator('ebs_shipments_{0}.xlsx'.format(bill_id))
    report.write_header((
       'AWB', 'Order No','Pickup Date', 'Actual Weight', 
       'Chargeable Weight', 'Cod Amount', 'Origin',
       'Destination','Shipper', 'Sub customer',
       'Consignee','Expected DOD')
    )
    billing = Billing.objects.get(id=bill_id)
    ebsppd = Product.objects.get(product_name='ebsppd')
    ebscod = Product.objects.get(product_name='ebscod')
    data = billing.shipments.filter(
        shipext__product__in=[ebsppd,ebscod]
    ).exclude(
        billing=None
    ).values_list(
        'airwaybill_number', 'order_number', 'added_on', 
        'shipext__original_act_weight', 'chargeable_weight', 
        'collectable_value', 'pickup__service_centre__center_name', 
        'original_dest__center_name', 'shipper__name', 
        'pickup__subcustomer_code__name', 'consignee', 'expected_dod'
    )
    file_name = report.write_body(data)
    path = 'http://billing.ecomexpress.in/static/uploads/reports/'+file_name
    ecomm_send_mail(
        'Ebs shipments report', 
        path, 
        [   'birjus@ecomexpress.in',
            'jinesh@prtouch.com', 
            'jaideeps@ecomexpress.in', 
            'nareshb@ecomexpress.in'
        ]
    )
    return path


def update_customer_bill_reports_links(qid):
    from billing.generate_bill import update_customer_reports
    queue = BillingQueue.objects.get(id=qid)
    if not CustomerBillingReport.objects.filter(billqueue=queue).exists():
        update_customer_reports(queue)
    bills = queue.bills.all()
    month_str = queue.billing_from.strftime('%m')
    bill_url = 'http://billing.ecomexpress.in/static/uploads/billing/' + month_str + '/'

    for bill in bills:
        bill_id = bill.id
        customer_name = bill.customer.name
        print bill_id

        in_summary_url = get_filename(bill_id, 'bill_wise', 'pdf')
        invoice_report = bill_url + os.path.split(in_summary_url)[1]

        in_summary_with_header_url = get_filename(bill_id, 'bill_wise_without_header', 'pdf')
        headless_invoice_report = bill_url + os.path.split(in_summary_with_header_url)[1]

        gen_awb = GenerateAwbPdf(bill_id)

        awb_pdf_url = gen_awb.get_filename('awb_wise', 'pdf')
        awb_pdf_report = bill_url + os.path.split(awb_pdf_url)[1]

        awb_excel_url = gen_awb.get_filename('awb_excel', 'xlsx')
        awb_excel_report = bill_url + os.path.split(awb_excel_url)[1]

        CustomerBillingReport.objects.filter(billing=bill).update(
            invoice_report = invoice_report,
            headless_invoice_report = headless_invoice_report ,
            awb_pdf_report = awb_pdf_report,
            awb_excel_report = awb_excel_report,
            ebs_invoice_report = '',
            headless_ebs_invoice_report = '')
    print 'finished'
    return True
