import pyPdf
import os
import pdb
import datetime
from decimal import *
from collections import defaultdict
from xlsxwriter.workbook import Workbook

from django.conf import settings
from django.core.mail import send_mail

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate,\
    Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT, TA_CENTER

from octroi.models import OctroiBilling
from service_centre.models import OctroiShipments

PROJECT_ROOT = '/home/web/ecomm.prtouch.com/ecomexpress'
img_location = PROJECT_ROOT + '/static/assets/img/EcomlogoPdf.png'
pdf_home = PROJECT_ROOT + settings.STATIC_URL + 'uploads/billing/'
pdf_folder = settings.STATIC_URL + 'uploads/billing/'

TW = Decimal(10) ** -2

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='LJustify', alignment=TA_LEFT))
styles.add(ParagraphStyle(name='RJustify', alignment=TA_RIGHT))
styles.add(ParagraphStyle(name='CJustify', alignment=TA_CENTER))
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='AWB_heading',
                          alignment=TA_CENTER,
                          fontSize=6))
styles.add(ParagraphStyle(name='AWB_heading_right',
                          alignment=TA_RIGHT,
                          fontSize=6))
styles.add(ParagraphStyle(name='Text6', fontSize=6))
styles.add(ParagraphStyle(name='BoldRight',
                          alignment=TA_RIGHT,
                          fontSize=6))
styles.add(ParagraphStyle(name='ImpPara',
                          alignment=TA_LEFT,
                          fontSize=7))
styles.add(ParagraphStyle(name='InvoiceHead',
                          alignment=TA_CENTER,
                          textColor="black"))
styles.add(ParagraphStyle(name='InvoicePara',
                          alignment=TA_LEFT,
                          spaceBefore=0,
                          spaceAfter=0,
                          leading=12,
                          leftIndent=18,
                          rightIndent=32,
                          fontSize=10))
styles.add(ParagraphStyle(name='AwbHead',
                          alignment=TA_LEFT,
                          spaceBefore=0,
                          spaceAfter=0,
                          leading=9,
                          leftIndent=32,
                          rightIndent=32,
                          fontSize=6))
styles.add(ParagraphStyle(name='CustCodeHead',
                          alignment=TA_CENTER,
                          #textColor="white",
                          fontSize=6))
styles.add(ParagraphStyle(name='BillHeadL',
                          alignment=TA_LEFT,
                          spaceBefore=0,
                          spaceAfter=0,
                          leading=9,
                          fontSize=8))
styles.add(ParagraphStyle(name='BillHeadR',
                          alignment=TA_LEFT,
                          spaceBefore=0,
                          spaceAfter=0,
                          leading=9,
                          leftIndent=32,
                          rightIndent=32,
                          fontSize=8))

def get_billing_date_str(bill_id, slash=False):
    bill = OctroiBilling.objects.get(id=bill_id)
    bill_date = bill.bill_generation_date + datetime.timedelta(days=1)
    if slash:
        return bill_date.strftime('%d/%m/%Y')
    else:
        return bill_date.strftime('%Y_%m_%d')

def make_bold_right(val):
    return Paragraph('<b>%s</b>' % str(val), styles["BoldRight"])

def truncate(text):
    if text and len(text) > 13:
        return text[:13] + '..'
    else:
        return text

def get_bill_header():
    left_head = Paragraph('''
                          <para>
                          <img src="%s" width="84" height="35" valign="0"/><br/>
                          PAN No : AADCE1344F<br/>
                          Service Tax Regn No. : AADCE1344FSD001<br/>
                          Category : Courier Sevices<br/>
                          </para>''' % img_location,
                          styles["BillHeadL"])

    right_head = Paragraph('''
                           <para>
                           Ecom Express Private Limited<br/>
                           No. 14/12/2, Samalka,<br/>
                           Old Delhi-Gurgaon Road,<br/>
                           New Delhi 110 037 (India)<br/>
                           Tel : 011-30212000<br/>
                           www.ecomexpress.in<br/>
                           </para>''',
                           styles["BillHeadR"])

    header_data = [[left_head, '', right_head]]
    header_table = Table(header_data, colWidths=(200, 160, 200))
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (1, 0), 'MIDDLE')]))

    return header_table

def get_tan_pan_header():
    left_head = Paragraph('''
                          <para>
                          PAN No : AADCE1344F<br/>
                          Service Tax Regn No. : AADCE1344FSD001<br/>
                          Category : Courier Sevices<br/>
                          </para>''',
                          styles["BillHeadL"])

    right_head = Paragraph('''
                           <para>
                           Ecom Express Private Limited<br/>
                           No. 14/12/2, Samalka,<br/>
                           Old Delhi-Gurgaon Road,<br/>
                           New Delhi 110 037 (India)<br/>
                           Tel : 011-30212000<br/>
                           www.ecomexpress.in<br/>
                           </para>''',
                           styles["BillHeadR"])

    header_data = [[left_head, '', right_head]]
    header_table = Table(header_data, colWidths=(200, 160, 200))
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (1, 0), 'BOTTOM')]))

    return header_table

def get_bill_invoice_table(bill_id, total_amount, due_date):
    billing = OctroiBilling.objects.get(pk=bill_id)
    bill_date_str = get_billing_date_str(bill_id, slash=True)
    billto_date = billing.bill_generation_date.strftime('%d/%m/%Y')
    customer = billing.customer
    invoice_bill_data = '''
        <para spaceb=3>
        <b>Bill No.</b>: {0}<br/>
        <b>Bill Date:</b> {1}<br/>
        <b>Total amount Due:</b> {2}<br/>
        </para>'''.format(billing.bill_id,
                          billto_date,
                          Decimal(round(total_amount,0)).quantize(TW))
    invoice_bill_para = Paragraph(invoice_bill_data, styles["InvoicePara"])

    invoice_cust_data = '<para spaceb=3>{0}<br/>{1}<br/>'.\
        format(customer.code, customer.name.replace('&', '&amp;'))
    if customer.address.address1:
        invoice_cust_data = invoice_cust_data + customer.address.address1\
            + '<br/>'
    if customer.address.address2:
        invoice_cust_data = invoice_cust_data + customer.address.address2\
            + '<br/>'
    if customer.address.address3:
        invoice_cust_data = invoice_cust_data + customer.address.address3\
            + '<br/>'
    if customer.address.address4:
        invoice_cust_data = invoice_cust_data + customer.address.address4\
            + '<br/>'
    if customer.address.city:
        invoice_cust_data = invoice_cust_data + customer.address.city\
            + ','
    if customer.address.state:
        invoice_cust_data = invoice_cust_data + customer.address.state\
            + '<br/>'
    if customer.address.pincode:
        invoice_cust_data = invoice_cust_data + customer.address.pincode\
            + '<br/>'
    if customer.address.phone:
        invoice_cust_data = invoice_cust_data + 'Phone No: ' +customer.address.phone\
            + '<br/>'
    invoice_cust_data = invoice_cust_data + '</para>'
    invoice_cust_para = Paragraph(invoice_cust_data,
                                  styles["InvoicePara"])
    invoice_header_data = [[invoice_cust_para, '', invoice_bill_para]]
    invoice_header_table = Table(invoice_header_data, colWidths=(300, 60, 200))
    invoice_header_table.setStyle(TableStyle(
        [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
         ('LEFTPADDING', (0, 0), (-1, -1), 3),
         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
         ]))

    return invoice_header_table

def get_bill_soc_table_left(bill_id):
    billing = OctroiBilling.objects.get(pk=bill_id)
    soc_table_data = [
        ['Octroi Charge', Decimal(billing.octroi_charge).quantize(TW)],
        ['Octroi Ecom Charge', Decimal(billing.octroi_ecom_charge).quantize(TW)]]
    soc_table_left = Table(soc_table_data, colWidths=(140, 60))
    soc_table_left.setStyle(TableStyle([
        ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ]))
    del billing
    return soc_table_left

def get_bill_soc_table_right(bill_id):
    billing = OctroiBilling.objects.get(pk=bill_id)
    soc_table_data = [
        ['Amount Before Tax', Decimal(billing.total_charge_pretax).quantize(TW)],
        ['Service Tax', Decimal(billing.service_tax).quantize(TW)],
        ['Education Cess', Decimal(billing.education_secondary_tax).quantize(TW)],
        ['HSE Cess', Decimal(billing.cess_higher_secondary_tax).quantize(TW)],
        ['Total', Decimal(round(billing.total_payable_charge,0)).quantize(TW)]]
    soc_table_right = Table(soc_table_data, colWidths=(140, 60))
    soc_table_right.setStyle(TableStyle([
        ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ]))
    return soc_table_right

def get_bill_important_info_para():
    imp_info_data = '''
        <para>
        Important Information:<br/>
    	1. This is a computerised generated Invoice and does not require
        any official signature.  Kindly notify us immediately in case of
        any discrepancy in the Invoice.<br/>
    	2. Delay in payments shall attract Interest @ 2% per month.<br/>
        </para>'''

    return Paragraph(imp_info_data, styles["ImpPara"])

def get_invoice_summary(bill_id, file_name, with_header=True):
    """
    """
    # preapre the data to be written to pdf
    billing = OctroiBilling.objects.get(id=bill_id)

    if billing.bill_generation_date:
        due_date = billing.bill_generation_date + datetime.timedelta(10)
    else:
        due_date = ""
    total_amount = billing.balance +\
        billing.total_payable_charge +\
        billing.adjustment -\
        billing.received -\
        billing.adjustment_cr

    full_file_name = os.path.join(pdf_home, file_name)
    doc = SimpleDocTemplate(full_file_name, pagesize=A4, topMargin=50,
              bottomMargin=30, leftMargin=60, rightMargin=60)
    elements = []
    if with_header:
        header_table = get_bill_header()
        elements.append(header_table)

        # invoice heading
        invoice = Paragraph('<b>INVOICE</b>', styles["InvoiceHead"])
        elements.append(invoice)
        #elements.append(Spacer(1, 2))
    else:
        pan_header = get_tan_pan_header()
        elements.append(pan_header)
        elements.append(Spacer(1, 12))

    # invoice head - customer and billing details
    invoice_header_table = get_bill_invoice_table(
        bill_id, total_amount, due_date)
    elements.append(invoice_header_table)
    elements.append(Spacer(1, 20))

    # summary of charges section
    soc_heading = Paragraph('<font size=9><b>Summary Of Charges<b></font>', styles["LJustify"])
    elements.append(soc_heading)
    elements.append(Spacer(1, 12))

    soc_table_left = get_bill_soc_table_left(bill_id)
    soc_table_right = get_bill_soc_table_right(bill_id)

    soc_table = Table([[soc_table_left, '', soc_table_right]], colWidths=(250, 50, 250))
    soc_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
    elements.append(soc_table)
    elements.append(Spacer(1, 10))

    # important information section
    imp_info_para = get_bill_important_info_para()
    imp_table = Table([[imp_info_para]], colWidths=(560))
    elements.append(imp_table)
    elements.append(Spacer(1, 20))

    doc.build(elements)
    return pdf_folder + file_name

class GenerateReport(object):

    def __init__(self):
        self.PDF_HOME = settings.PROJECT_ROOT_DIR + settings.STATIC_URL + 'uploads/billing/'

    def get_filename(self, name, ext, index=None):
        if index:
            file_name = '%s_%s_%s.%s' % (
                str(name),
                str(self.billing.bill_id),
                str(index),
                str(ext))
        else:
            file_name = '%s_%s.%s' % (
                str(name),
                str(self.billing.bill_id),
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

class GenerateOctroiPdf(GeneratePdf):

    def __init__(self, bill_id):
        GeneratePdf.__init__(self)
        self.bill_id = bill_id
        self.billing = OctroiBilling.objects.get(id=bill_id)
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

    def generate_pdf_by_ptype(self, ptype):
        ships_count = self.billing.shipments.all().count()
        for index in xrange(1, ships_count+1, self.PDF_CHUNK_SIZE):
            if index + self.PDF_CHUNK_SIZE > ships_count:
                add_total = True
            else:
                add_total = False

            file_name = self.generate_awb_pdf_chunk(index, ptype, add_total)
            self.awb_files.append(file_name)

    def generate_combined_pdf(self):
        print '5.generating combined pdf'
        #combine all filenames and create combined pdf file
        output = pyPdf.PdfFileWriter()
        for dfile in self.awb_files:
            fileName, fileExt = os.path.splitext(dfile)
            if fileExt != '.pdf':
                continue
            f = open(dfile, 'rb')
            inputf = pyPdf.PdfFileReader(f)
            for page in range(inputf.getNumPages()):
                output.addPage(inputf.getPage(page))

        filename = self.get_filename('octroi_awb_pdf', 'pdf')
        outs = open(filename, 'wb')
        output.write(outs)
        outs.close()
        return filename

    def get_awb_table_data(self, ptype, index):
        awb_shipments = self.shipments.all()[index-1:index-1+self.PDF_CHUNK_SIZE]
        current_index = index - 1
        if not awb_shipments.count():
            yield [[0]*21]

        for shipment in awb_shipments:
            current_index += 1
            sub_cust_code = str(shipment.shipper.code)

            if shipment.origin:
                origin = shipment.origin.center_name
            else:
                origin =  ''
            oct_chg = shipment.octroi_charge if shipment.octroi_charge else 0
            oct_ecom_chg = shipment.octroi_ecom_charge if shipment.octroi_ecom_charge else 0
            total = Decimal(oct_chg + oct_ecom_chg).quantize(TW)
            yield [current_index,
                 shipment.shipment.airwaybill_number,
                 shipment.shipment.order_number,
                 shipment.receipt_number,
                 shipment.added_on.strftime('%d/%m/%y'),
                 origin, # to add
                 shipment.shipment.original_dest.center_name,
                 shipment.shipment.declared_value,
                 Decimal(shipment.octroi_charge).quantize(TW),
                 Decimal(shipment.octroi_ecom_charge).quantize(TW),
                 Decimal(total).quantize(TW)]

    def get_awb_table_totals_row(self, ptype=None):
        pbilling = self.billing
        row = ['', '', 'TOTAL', '', '', '', '', '', '', '', Decimal(pbilling.total_charge_pretax).quantize(TW)]
        return row

    def get_awb_total_table(self, ptype=None):
        billing = OctroiBilling.objects.get(pk=self.bill_id)

        awb_total_table = [
            ['Total Octroi Charge',	Decimal(billing.octroi_charge).quantize(TW)],
            ['Total Ecomm Charge', Decimal(billing.octroi_ecom_charge).quantize(TW)],
            ['Service Tax',	Decimal(billing.service_tax).quantize(TW)],
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
        print '3.',index
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
                </para>'''.format(self.billing.customer.name, self.billing.bill_id,
                                  self.billing.bill_id)

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
            self.awbpara('Air Waybill No', "AWB_heading"),
            self.awbpara('Order No', "AWB_heading"),
            self.awbpara('Octroi Receipt No', "AWB_heading"),
            self.awbpara('Date', "AWB_heading"),
            self.awbpara('Origin', "AWB_heading"),
            self.awbpara('Destination', "AWB_heading"),
            self.awbpara('Value', "AWB_heading"),
            self.awbpara('Octroi', "AWB_heading"),
            self.awbpara('S.Charge', "AWB_heading"),
            self.awbpara('Total', "AWB_heading"),
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
                colWidths=(30, 60, 60, 65, 65, 60, 60, 40, 40, 40, 40))
        awb_table.setStyle(TableStyle([
            #('SPAN', (0, 0), (-1, 1)),
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

        return full_file_name

    def generate_awb_pdf(self):
        """ create multiple pdf files for each product types and combines them in the end."""
        print '1. generate awb pdf'
        if not self.billing.shipments.count():
            return None

        # first generate separate pdf files for each product type.
        # each product type pdf will be split into chunk files of shipment
        # count as specified by chunks size
        self.generate_pdf_by_ptype('cod')
        #self.generate_pdf_by_ptype('ppd')

        file_name = self.generate_combined_pdf()
        self.delete_awb_chunks()
        fp, fn = os.path.split(file_name)
        return '/static/uploads/billing/{0}'.format(fn)

# generate billwise excel
class GenerateOctroiExcel(GenerateReport):

    def __init__(self, bill_id):
        GenerateReport.__init__(self)
        self.bill_id = bill_id
        self.billing = OctroiBilling.objects.get(id=bill_id)
        self.row_num = 0
        self.col_heads = (
            'Sl No', #0
            'Cust Code',
            'Air Waybill No',
            'Order No', #3
            'Receipt No',
            'Date',
            'Origin',
            'Destination',
            'Declared Charge', #6
            'Octroi',
            'Ecom Charges', #8
            'Total') #9
        self.file_name = self.get_filename('octroi_awb_excel', 'xlsx')
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
        self.sheet.write(self.row_num+2, 5, 'Bill No: '+str(self.billing.bill_id))
        for col, name in enumerate(self.col_heads):
            self.sheet.write(self.row_num+4, col, name, self.header_format)
        self.row_num += 4

    def get_awb_total_table_data(self):
        billing = self.billing
        awb_total_table = [
            ['Total Before Tax', Decimal(billing.total_charge_pretax).quantize(TW)],
            ['Service Tax',	Decimal(billing.service_tax).quantize(TW)],
            ['Education Cess', Decimal(billing.education_secondary_tax).quantize(TW)],
            ['HSE Cess', Decimal(billing.cess_higher_secondary_tax).quantize(TW)],
            ['Grand Total',	Decimal(round(billing.total_payable_charge,0)).quantize(TW)]
        ]
        return awb_total_table

    def get_awb_table_data_direct(self, ptype):
        shipments = self.billing.shipments.all()
        if not shipments.count():
            yield [[0]*21]
            #'Sl No', #0 'Cust Code', 'Air Waybill No', 'Order No', #3 'Date', 'Origin',
            #'Declared Charge', #6 'Octroi', 'Ecom Charges', #8 'Total') #9

        for index, shipment in enumerate(shipments, start=1):
            sub_cust_code = str(shipment.shipper.code)

            if shipment.origin:
                origin = shipment.origin.center_name
            else:
                origin =  ''
            oct_chg = shipment.octroi_charge if shipment.octroi_charge else 0
            oct_ecom_chg = shipment.octroi_ecom_charge if shipment.octroi_ecom_charge else 0
            total = oct_chg + oct_ecom_chg
            yield [index,
                 sub_cust_code,
                 shipment.shipment.airwaybill_number,
                 shipment.shipment.order_number,
                 shipment.receipt_number,
                 shipment.added_on.strftime('%d/%m/%y'),
                 origin, # to add
                 shipment.shipment.original_dest.center_name,
                 Decimal(shipment.shipment.declared_value).quantize(TW),
                 Decimal(shipment.octroi_charge).quantize(TW),
                 Decimal(shipment.octroi_ecom_charge).quantize(TW),
                 Decimal(total).quantize(TW)]

    def write_gen_data(self, data_list_gen):
        for data_list in data_list_gen:
            self.row_num += 1
            for col, val in enumerate(data_list):
                val = val.encode('ascii', 'ignore') if isinstance(val, unicode) else str(val)
                self.sheet.write_string(self.row_num, col, val)

    def write_awb_total(self, awb_total_table):
        for row, data_list in enumerate(awb_total_table, start=self.row_num+2):
            self.row_num+=1
            for col, val in enumerate(data_list, start=3):
                self.sheet.write_string(row, col, str(val))

    def generate_awb_excel(self):
        col_count = len(self.col_heads)
        self.sheet.set_column(0, col_count, 12) # set column width
        self.sheet.write(0, 2, "AirwayBill Wise Charges")

        # COD SECTION ####################
        cod_shipments = self.billing.shipments.all().exists()
        if cod_shipments:
            self.write_header('COD')

            cod_data_gen = self.get_awb_table_data_direct('cod')
            self.write_gen_data(cod_data_gen)

            #cod_total_table = self.get_awb_total_table_data()
            #self.write_awb_total(cod_total_table)

        # PPD SECTION ####################
        #ppd_shipments = self.billing.shipments.filter(shipment__product_type='ppd').exists()
        #if ppd_shipments:
            #self.write_header('PPD')
#
            #ppd_data_gen = self.get_awb_table_data_direct('ppd')
            #self.write_gen_data(ppd_data_gen)
#
            #ppd_total_table = self.get_awb_total_table_data('ppd')
            #self.write_awb_total(ppd_total_table)

        # GRAND TOTAL
        awb_total_table = self.get_awb_total_table_data()
        self.sheet.write_string(self.row_num+2, 0, 'GRAND TOTAL FOR ALL PRODUCTS')
        self.row_num += 1
        self.write_awb_total(awb_total_table)

        self.workbook.close()
        fp, fn = os.path.split(self.file_name)
        return '/static/uploads/billing/{0}'.format(fn)

def get_octroi_pdf_report(bill_id):
    gen_awb = GenerateOctroiPdf(bill_id)
    awb_pdf = gen_awb.generate_awb_pdf()
    return awb_pdf

def get_octroi_excel_report(bill_id):
    gen_excel = GenerateOctroiExcel(bill_id)
    awb_exl = gen_excel.generate_awb_excel()
    return awb_exl


