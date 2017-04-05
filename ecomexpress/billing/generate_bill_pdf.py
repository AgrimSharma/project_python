'''
Created on 29-May-2013

@author: prtouch
'''
import os
import pdb
import datetime
import subprocess
from decimal import *
from collections import defaultdict
import pyPdf
from xlsxwriter.workbook import Workbook
from collections import defaultdict
from django.conf import settings
#from django.db.models import Count, Sum
from django.core.mail import send_mail

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate,\
    Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT, TA_CENTER

from billing.models import BillingSubCustomer, Billing, ProductBilling
from billing.models import BillingSubCustomerPreview, BillingPreview, ProductBilling
from service_centre.models import MinActualWeight, get_internal_shipment_status, Shipment
from ecomm_admin.models import Brentrate

PROJECT_ROOT = settings.PROJECT_ROOT
PROJECT_ROOT = '/home/web/ecomm.prtouch.com/ecomexpress/'
img_location = PROJECT_ROOT + '/static/assets/img/EcomlogoPdf.png'

pdf_home = PROJECT_ROOT + settings.STATIC_URL + 'uploads/billing/'
pdf_folder = settings.STATIC_URL + 'uploads/billing/'
combined_pdf_name = 'combined_pdf_%s.pdf' % datetime.datetime.today().strftime('%Y_%m_%d')
pdf_chunk_size = 515

bill_reports_txt_file = PROJECT_ROOT + settings.STATIC_URL + \
    'uploads/billing/bill_reports.txt'
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
styles.add(ParagraphStyle(name='CidHead',
                          alignment=TA_LEFT,
                          spaceBefore=10,
                          spaceAfter=10,
                          leading=12,
                          leftIndent=18,
                          rightIndent=32,
                          textColor="red"))
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
    bill = Billing.objects.get(id=bill_id)
    bill_date = bill.billing_date + datetime.timedelta(days=1)
    #bill_date = bill.billing_date
    if slash:
        return bill_date.strftime('%d/%m/%Y')
    else:
        return bill_date.strftime('%Y_%m_%d')


def rectify_dict(d):
    """ this function takes a dict as input and check all values,
        if any of the value is None replace it with zero
    """
    for k in d.keys():
        d[k] = 0 if d[k] is None else d[k]
    return d

def get_bill_summary_filename(bill_id, name, ext):
    billing = Billing.objects.get(pk=bill_id)
    billing_date = billing.billing_date.strftime('%Y_%m_%d')
    bill_date_str = get_billing_date_str(bill_id)
    file_name = '%s_%s.%s' % ( str(name), str(bill_date_str), str(ext))
    full_file_name = os.path.join(pdf_home, file_name)
    return full_file_name

def get_filename(bill_id, name, ext, index=None, preview=False):
    if preview:
        billing = BillingPreview.objects.get(pk=bill_id)
    else:
        billing = Billing.objects.get(pk=bill_id)
    customer = billing.customer
    cust_name = customer.name.replace(' ', '_')
    billing_date = billing.billing_date.strftime('%Y_%m_%d')
    bill_date_str = get_billing_date_str(bill_id)
    month = billing.billing_date.strftime('%m')
    year = billing.billing_date.strftime('%Y')
    if preview:
        month_dir = str(month) + '_preview'
    else:
        month_dir = str(month)
    if index:
        file_name = '%s/%s/%s_%s_%s_%s_%s.%s' % (
            year, month_dir,
            str(name),
            str(cust_name),
            str(billing.pk),
            str(bill_date_str),
            str(index),
            str(ext))
    else:
        file_name = '%s/%s/%s_%s_%s_%s.%s' % (
            year, month_dir,
            str(name),
            str(cust_name),
            str(billing.pk),
            str(bill_date_str),
            str(ext))
    full_file_name = os.path.join(pdf_home, file_name)
    return full_file_name

def make_bold(val):
    return Paragraph('<b>%s</b>' % str(val), styles["Text6"])

def make_bold_right(val):
    return Paragraph('<b>%s</b>' % str(val), styles["BoldRight"])

def truncate(text):
    if text and len(text) > 13:
        return text[:13] + '..'
    else:
        return text

def get_awb_table_data(bill_id, ptype, index=None):
    #print 'getting table data for ',bill_id
    #print '5.3.1 inside awb table data generation function...bill_id is :', bill_id
    billing = Billing.objects.get(pk=bill_id)
    if index:
        shipments = billing.shipments.filter(product_type=ptype)[index-1:index-1+pdf_chunk_size]
    else:
        shipments = billing.shipments.filter(product_type=ptype)
        index = 1
    minactualweight = MinActualWeight.objects.all()

    def get_sub_cust_code(shipment):
        #print '5.3.x.1 get sub_cust_code...',bill_id
        #print shipment.id
        try:
            return str(shipment.shipper.code) + \
                  truncate(str(shipment.pickup.subcustomer_code.id)) # + '-' +\
                  #str(shipment.pickup.subcustomer_code.name))
        except:
            return str(shipment.shipper.code)

    def get_destination(shipment):
        ##print '5.3.x.2 get destination...',index
        if shipment.original_dest :
            result = shipment.original_dest.center_name
        else:
            result = shipment.service_centre.center_name
        return result.split('-')[0]

    def get_freight(shipment):
        ##print '5.3.x.4 get freight...', index
        #minwt = minactualweight.filter(customer=shipment.shipper)
        ps = shipment.order_price_set.all()
        if ps.count() > 0:
            fc = ps[0].freight_charge
        else:
            fc = 0
        ##print '5.3.x.4 get freight...',Decimal(fc).quantize(TW)
        del shipment
        return Decimal(fc).quantize(TW)

    def get_cod(shipment):
        ##print '5.3.x.5.1 get cod...',index
        cod = shipment.codcharge_set.all()
        if cod.count() > 0:
            cod = shipment.codcharge_set.all()[0].cod_charge
        else:
            cod = 0
        if shipment.rts_status == 1:
            ##print '5.3.x.5.2 get cod...',Decimal(cod).quantize(TW)
            return Decimal(0-cod).quantize(TW)
        ##print '5.3.x.5.2 get cod...',Decimal(cod).quantize(TW)
        return Decimal(cod).quantize(TW)

    def get_reverse(shipment):
        ##print '5.3.x.5.3 get reverse...', index
        return shipment.order_price_set.all()[0].reverse_charge

    def get_sdd(shipment):
        ##print '5.3.x.5.3 get sdd...', index
        return shipment.order_price_set.all()[0].sdd_charge

    def get_others(op):
        ##print '5.3.x.6 get others...',index
        if not op:
            return 0
        if not op.sdl_charge:
            op.sdl_charge = 0
        other_price = op.sdl_charge + \
                op.rto_charge + \
                op.to_pay_charge + \
                op.valuable_cargo_handling_charge
        ##print '5.3.x.6 get others...',Decimal(other_price).quantize(TW)
        return Decimal(other_price).quantize(TW)

    def get_total(shipment):
        ##print '5.3.x.7 get total...', index
        op = shipment.order_price_set.all()[0]
        if not op.sdl_charge:
            op.sdl_charge = 0
        total_op = op.sdl_charge + \
                op.rto_charge + \
                op.to_pay_charge + \
                op.freight_charge + \
                op.reverse_charge + \
                op.sdd_charge + \
                op.valuable_cargo_handling_charge
        if shipment.codcharge_set.all():
            codcharge = shipment.codcharge_set.all()[0].cod_charge
        else:
            codcharge = 0
        ##print '5.3.x.7 get total...',Decimal(total_op + codcharge).quantize(TW)
        if shipment.rts_status != 1:
            return Decimal(total_op + codcharge).quantize(TW)
        else:
            return Decimal(total_op - codcharge).quantize(TW)

    ##print '5.3.2 getting awb table data...'

    if not billing.shipments.all().count():
        ##print '5.3.3 no shipments in billing..',[[0]*12]
        return [[0]*12]

    awb_table_data = (
        [index,
         get_sub_cust_code(shipment),
         shipment.airwaybill_number,
         shipment.order_number,
         shipment.added_on.strftime('%d/%m/%y'),
         #shipment.product_type,
         get_destination(shipment).split("-")[0],
         #get_accurate_weight(shipment),
         shipment.chargeable_weight,
         get_freight(shipment),
         get_cod(shipment),
         get_reverse(shipment),
         get_sdd(shipment),
         get_others(shipment.order_price_set.all()[0]),
         get_total(shipment)]
        for index, shipment in enumerate(shipments, start=index))

    #print '5.3.4 awb table data generated returing to callee...', bill_id
    del shipments, billing
    return awb_table_data

def get_awb_total_table_data_copy(bill_id):
    billing = Billing.objects.get(pk=bill_id)
    awb_total_table = [
        ['Gross Total', Decimal(billing.total_charge_pretax - billing.fuel_surcharge).quantize(TW)],
        ['Fuel Surcharge', Decimal(billing.fuel_surcharge).quantize(TW)],
        ['Total Before Tax', Decimal(billing.total_charge_pretax).quantize(TW)],
        ['Service Tax',	Decimal(billing.service_tax).quantize(TW)],
        ['Education Cess', Decimal(billing.education_secondary_tax).quantize(TW)],
        ['HSE Cess', Decimal(billing.cess_higher_secondary_tax).quantize(TW)],
        ['Grand Total',	Decimal(round(billing.total_payable_charge,0)).quantize(TW)]
    ]
    del billing
    return awb_total_table

def get_awb_total_table_data(bill_id, ptype=None):
    billing = Billing.objects.get(pk=bill_id)
    if ptype:
        billing = ProductBilling.objects.filter(billing__id=bill_id, product__product_name=ptype)[0]
    awb_total_table = [
        ['Gross Total', Decimal(billing.total_charge_pretax - billing.fuel_surcharge).quantize(TW)],
        ['Fuel Surcharge', Decimal(billing.fuel_surcharge).quantize(TW)],
        ['Total Before Tax', Decimal(billing.total_charge_pretax).quantize(TW)],
        ['Service Tax',	Decimal(billing.service_tax).quantize(TW)],
        ['Education Cess', Decimal(billing.education_secondary_tax).quantize(TW)],
        ['HSE Cess', Decimal(billing.cess_higher_secondary_tax).quantize(TW)],
        ['Grand Total',	Decimal(round(billing.total_payable_charge,0)).quantize(TW)]
    ]
    del billing
    return awb_total_table

def get_awb_total_table(bill_id, ptype=None):
    total_table_data = get_awb_total_table_data(bill_id, ptype)
    total_table = Table(total_table_data,
            splitByRow=True,
            repeatRows=1,
            repeatCols=2)
    total_table.setStyle(TableStyle([
        ('ALIGN',(0,0),(0,-1),'RIGHT'),
        ('ALIGN',(1,0),(1,-1),'LEFT'),
        ]))
    total_table.hAlign = 'RIGHT'
    del total_table_data
    return total_table


def get_awb_chunk_table(bill_id, ptype, index=None, add_total=False):
    #print '5.2.2.2.3.1  inside chunk table data ..index  :',bill_id
    billing = Billing.objects.get(pk=bill_id)
    awb_table_headers = [
         Paragraph('<b>Sl No</b>', styles["AWB_heading"]),
         Paragraph('<b>Cust Code</b>', styles["AWB_heading"]),
         Paragraph('<b>Air Waybill No</b>', styles["AWB_heading"]),
         Paragraph('<b>Order No</b>', styles["AWB_heading"]),
         Paragraph('<b>Date</b>', styles["AWB_heading"]),
         #Paragraph('<b>Service</b>', styles["AWB_heading"]),
         Paragraph('<b>Destination</b>', styles["AWB_heading"]),
         Paragraph('<b>Weight</b>', styles["AWB_heading"]),
         Paragraph('<b>Freight</b>', styles["AWB_heading"]),
         Paragraph('<b>COD</b>', styles["AWB_heading"]),
         Paragraph('<b>Reverse</b>', styles["AWB_heading"]),
         Paragraph('<b>SDD</b>', styles["AWB_heading"]),
         Paragraph('<b>Others</b>', styles["AWB_heading"]),
         Paragraph('<b>Total</b>', styles["AWB_heading"])
    ]

    #print '5.2.2.2.3.2 get chunk table data ..', index
    awb_table_data = list(get_awb_table_data(bill_id, ptype, index))

    def get_awb_table_totals_row(bill_id, ptype):
        print 'get total...%s ships...',ptype
        if ptype:
            pbilling = ProductBilling.objects.filter(billing__id=bill_id, product__product_name=ptype)[0]
        else:
            pbilling = Billing.objects.filter(id=bill_id)

        row = ['', '', '', '', '', 'TOTAL',
          Decimal(pbilling.total_chargeable_weight).quantize(TW),
          Decimal(pbilling.freight_charge).quantize(TW),
          Decimal(pbilling.total_cod_charge).quantize(TW),
          Decimal(pbilling.reverse_charge).quantize(TW),
          Decimal(pbilling.sdd_charge).quantize(TW),
          Decimal(pbilling.valuable_cargo_handling_charge + pbilling.rto_charge + pbilling.to_pay_charge).quantize(TW),
          Decimal(pbilling.total_charge_pretax - pbilling.fuel_surcharge).quantize(TW)]
        return row

    awb_table_data.insert(0, awb_table_headers)
    if add_total:
        print 'getting awb totals...'
        awb_table_totals_row = get_awb_table_totals_row(bill_id, ptype)
        awb_table_data.append(awb_table_totals_row)

    #print '5.2.2.2.3.3 got chunk table data ..', index
    awb_table = Table(awb_table_data,
            splitByRow=True,
            repeatRows=1,
            colWidths=(30, 60, 50, 55, 40, 60, 35, 45, 45, 30, 30, 30, 50))
    awb_table.setStyle(TableStyle([
        ('ALIGN',(0, 0), (-1, 0), 'CENTER'),
        ('ALIGN',(0, 1), (4, -1), 'CENTER'),
        ('ALIGN',(5, 1), (5, -1), 'LEFT'),
        ('ALIGN',(6, 1), (-1, -1), 'RIGHT'),
        ('LEFTPADDING',(2, 0), (2, -1), 1),
        ('FONTSIZE',(0, 0),(-1, 0), 6),
        ('FONTSIZE',(0, 1),(-1, -1), 6),
        ('INNERGRID', (0,0), (-1, -1), 0.25, colors.black),
        ('BOX', (0,0), (-1, -1), 0.25, colors.black),
        ]))

    #print '5.2.2.2.3.4 return from chunk table data ..', index
    del awb_table_data, awb_table_headers, index, get_awb_table_totals_row#, billing
    return awb_table

def generate_awb_pdf_chunk(bill_id, index, add_total, ptype):
    """ This function will take a chunk(500 for eg) of shipments
    and generate awb_wise pdf file
    generate_awb_pdf_chunk(shipments, billing, index) --> return file_name
    """
    print '%s ships...',ptype
    #print '5.2.2.2.1 chunk..generating..pdf.. bid, index',bill_id, index
    # generate pdf file name
    billing = Billing.objects.get(pk=bill_id)
    file_name = get_filename(bill_id, 'awb_wise'+ptype, 'pdf', index)
    full_file_name = os.path.join(pdf_home, file_name)
    #print '5.2.2.2.2 chunk...full file name  ',full_file_name
    doc = SimpleDocTemplate(full_file_name, pagesize=A4, topMargin=50,
              bottomMargin=30, leftMargin=60, rightMargin=60)
    # container for the 'Flowable' objects we add the para, tables to this
    # flowable and generate pdf at the end
    elements = []
    # page header
    if index == 1:
        page_header1 = Paragraph('<b>AirwayBill wise charges</b><br/>', styles["AWB_heading"])
        elements.append(page_header1)

        para = '''
            <para spaceb=3>
            <b>Customer Name:</b> {0}<br/>
            <b>Bill No:</b> {1}<br/>
            <b>Bill Period:</b> {2} to {3}<br/>
            <b>Product Type:</b> {4}<br/>
            </para>'''.format(billing.customer.name, billing.id,
                              billing.billing_date_from.strftime("%d/%m/%Y"),
                              billing.billing_date.strftime("%d/%m/%Y"),
                              ptype)
        page_header2 = Paragraph(para, styles["AwbHead"])

        main_header_data = [['', page_header2]]
        main_header_table = Table(main_header_data,
            colWidths=(300, 260))
        main_header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ]))
        elements.append(main_header_table)
        elements.append(Spacer(1, 12))

    # invoice head - customer and billing details
    #print '5.2.2.2.3 getting chunk display table data..',index
    awb_table = get_awb_chunk_table(bill_id, ptype, index, add_total)
    if add_total:
        elements.append(awb_table)
        awb_total = get_awb_total_table(bill_id, ptype)
        elements.append(Spacer(1, 12))
        elements.append(awb_total)
    else:
        elements.append(awb_table)

    doc.build(elements)

    #print '5.2.2.2.4 chunk pdf created ',index
    del awb_table, elements, file_name, doc, billing, add_total
    return full_file_name

def generate_awb_pdf_chunks(bill_id):
    """ This function will generate a number of pdfs for shipments
    group of 500. generate_awb_pdf_chunks(<billing obj>) -->
    list of awb pdf files
    """
    #print '5.2.2.1 generating awb details pdf chunks...', bill_id
    billing = Billing.objects.get(pk=bill_id)
    if not billing.shipment_count:
        return []

    files = []

    cod_ships_count = billing.shipments.filter(product_type='cod').count()
    for index in xrange(1, cod_ships_count+1, pdf_chunk_size):
        print 'COD SHIPS........'
        #print '5.2.2.2 chunk.group..generating.. bid, index', bill_id, index
        if index + pdf_chunk_size > cod_ships_count:
            add_total = True
        else:
            add_total = False
        file_name = generate_awb_pdf_chunk(bill_id, index, add_total, 'cod')
        print file_name
        files.append(file_name)
        #print '5.2.2.3 chunk...generated.. filename',file_name

    ppd_ships_count = billing.shipments.filter(product_type='ppd').count()
    for index in xrange(1, ppd_ships_count+1, pdf_chunk_size):
        print 'PPD SHIPS........'
        #print '5.2.2.2 chunk.group..generating.. bid, index', bill_id, index
        if index + pdf_chunk_size > ppd_ships_count:
            add_total = True
        else:
            add_total = False
        file_name = generate_awb_pdf_chunk(bill_id, index, add_total, 'ppd')
        print file_name
        files.append(file_name)
    #print '5.2.2.4 all chunks...generated.. files ',files
    del billing
    return files

def get_bill_header():
    left_head = Paragraph('''
                          <para>
                          <img src="%s" width="84" height="35" valign="0"/><br/>
                          PAN No : AADCE1344F<br/>
                          Service Tax Regn No. : AADCE1344FSD001<br/>
                          Category : Courier Sevices<br/>
                          CIN:U63000DL2012PTC241107<br/>
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
                          CIN:U63000DL2012PTC241107<br/>
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

def get_bill_invoice_table(bill_id, total_amount, due_date, preview=False):
    if preview:
        billing = BillingPreview.objects.get(pk=bill_id)
    else:
        billing = Billing.objects.get(pk=bill_id)
    bill_date_str = get_billing_date_str(bill_id, slash=True)
    billto_date = billing.billing_date.strftime('%d/%m/%Y')
    customer = billing.customer
    invoice_bill_data = '''
        <para spaceb=3>
        <b>Bill No.</b>: {0}<br/>
        <b>Bill Period</b>: {1} to {2}<br/>
        <b>Bill Date:</b> {3}<br/>
        <b>Total amount Due:</b> {4}<br/>
        <b>Pay by:</b> {5}<br/>
        </para>'''.format(billing.id,
                          billing.billing_date_from.strftime("%d/%m/%Y"),
                          billto_date,
                          bill_date_str,
                          Decimal(round(total_amount,0)).quantize(TW),
                          due_date.strftime("%d/%m/%Y"))
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

def get_bill_account_summary_table(bill_id, total_amount, preview=False):
    if preview:
        billing = BillingPreview.objects.get(pk=bill_id)
    else:
        billing = Billing.objects.get(pk=bill_id)
    account_summary_data = [
        ['Previous Balance',
         'Payments Received',
         'Adjustments (Dr)',
         'Adjustments (Cr)',
         'Current Billing',
         'Total amount Due by Date'],
        [Decimal(billing.balance).quantize(TW),
         Decimal(billing.received).quantize(TW),
         Decimal(billing.adjustment).quantize(TW),
         Decimal(billing.adjustment_cr).quantize(TW),
         Decimal(round(billing.total_payable_charge,0)).quantize(TW),
         Decimal(round(total_amount,0)).quantize(TW)]]

    account_summary_table = Table(account_summary_data,
            colWidths=(70, 80, 70, 70, 60, 100))
    account_summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))

    return account_summary_table

def get_bill_soc_table_left(bill_id, preview=False):
    if preview:
        billing = BillingPreview.objects.get(pk=bill_id)
    else:
        billing = Billing.objects.get(pk=bill_id)

    soc_table_data = [
        ['Freight', Decimal(billing.freight_charge).quantize(TW)],
        ['Fuel Surcharge', Decimal(billing.fuel_surcharge).quantize(TW)],
        ['Special Delivery Location', Decimal(billing.sdl_charge).quantize(TW)],
        ['Same Day Delivery', Decimal(billing.sdd_charge).quantize(TW)],
        ['Return To Origin', Decimal(billing.rto_charge).quantize(TW)],
        ['Reverse Pickup', Decimal(billing.reverse_charge).quantize(TW)],
        ['COD applied', Decimal(billing.cod_applied_charge).quantize(TW)],
        ['COD reversed', Decimal(billing.cod_subtract_charge).quantize(TW)],
        ['Valuable Cargo Handling Charge',
         Decimal(billing.valuable_cargo_handling_charge).quantize(TW)]]
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

def get_bill_soc_table_right(bill_id, preview=False):
    if preview:
        billing = BillingPreview.objects.get(pk=bill_id)
    else:
        billing = Billing.objects.get(pk=bill_id)
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
    brate = Brentrate.objects.latest('id').min_brent_rate
    imp_info_data = '''
        <para>
        Important Information:<br/>
    	1. This is a computerised generated Invoice and does not require
        any official signature.  Kindly notify us immediately in case of
        any discrepancy in the Invoice.<br/>
    	2. Delay in payments shall attract Interest @ 2% per month.<br/>
        </para>'''

    return Paragraph(imp_info_data, styles["ImpPara"])

def get_cust_code_summary_table(bill_id, preview=False):
    if preview:
        billing = BillingPreview.objects.get(pk=bill_id)
        billing_subcustomer = BillingSubCustomerPreview.objects.filter(billing=billing).distinct()
    else:
        billing = Billing.objects.get(pk=bill_id)
        billing_subcustomer = BillingSubCustomer.objects.filter(billing=billing).distinct()

    bill_customer = billing.customer
    #shipper = bill_customer.shipper_set.all()

    cust_code_table_headers = [
            'Sr.', 'Sub Cust. Code', 'Customer Name',
            'No of Ships', 'Freight', 'FuelSC', 'SDL',
            'SDD', 'Reverse', 'COD Applied',
            'COD Subtract', 'VCHC', 'Total']

    def get_subcustomer_code(customer):
        return str(customer.subcustomer.customer.code) + \
            str(customer.subcustomer.id)

    def get_total(sbilling):
        total_sbilling = sbilling.rto_charge + \
            sbilling.to_pay_charge + \
            sbilling.freight_charge + \
            sbilling.valuable_cargo_handling_charge + \
            sbilling.demarrage_charge + \
            sbilling.fuel_surcharge + \
            sbilling.cod_applied_charge - \
            sbilling.cod_subtract_charge + \
            sbilling.sdd_charge+ \
            sbilling.reverse_charge+ \
            sbilling.sdl_charge
        return Decimal(total_sbilling).quantize(TW)

    cust_code_table_data = [
        [index,
         get_subcustomer_code(customer),
         truncate(customer.subcustomer.name),
         customer.shipments.count(),
         Decimal(customer.freight_charge).quantize(TW),
         Decimal(customer.fuel_surcharge).quantize(TW),
         Decimal(customer.sdl_charge).quantize(TW),
         Decimal(customer.sdd_charge).quantize(TW),
         Decimal(customer.reverse_charge).quantize(TW),
         Decimal(customer.cod_applied_charge).quantize(TW),
         Decimal(customer.cod_subtract_charge).quantize(TW),
         Decimal(customer.valuable_cargo_handling_charge).quantize(TW),
         make_bold_right(get_total(customer))]
        for index, customer in enumerate(billing_subcustomer, start=1)]

    cust_code_table_total = ['',
            '',
            'Total',
            billing.shipments.count(),
            Decimal(billing.freight_charge).quantize(TW),
            Decimal(billing.fuel_surcharge).quantize(TW),
            Decimal(billing.sdl_charge).quantize(TW),
            Decimal(billing.sdd_charge).quantize(TW),
            Decimal(billing.reverse_charge).quantize(TW),
            Decimal(billing.cod_applied_charge).quantize(TW),
            Decimal(billing.cod_subtract_charge).quantize(TW),
            Decimal(billing.valuable_cargo_handling_charge).quantize(TW),
            Decimal(billing.total_charge_pretax).quantize(TW)]

    cust_code_table_total = [make_bold_right(val) for val in cust_code_table_total]

    cust_code_table_data.insert(0, cust_code_table_headers)
    cust_code_table_data.append(cust_code_table_total)
    cust_code_table = Table(cust_code_table_data,
            splitByRow=True,
            repeatRows=1,
            colWidths=(20, 50, 65, 40, 50, 50, 35, 30, 40, 50, 40, 30, 50))

    cust_code_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (1, -2), 'CENTER'),
        ('ALIGN', (2, 1), (2, -2), 'LEFT'),
        ('ALIGN', (3, 1), (-1, -2), 'RIGHT'),
        ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
        ('FONTSIZE',(0, 0), (-1, -1), 6),
        #('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.6, 0.6, 0.6)),
        #('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.8, 0.8, 0.8)),
        ('INNERGRID', (0,0), (-1, -1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))

    return cust_code_table

def generate_awb_excel(bill_id):
    billing = Billing.objects.get(pk=bill_id)
    print '5.3.1 generating excel file...',bill_id
    col_heads = (
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
        'Parent/RTS Date',
        'RTS',
    )
    col_count = len(col_heads)
    # add filename and set save file path
    file_name = get_filename(bill_id, 'awb_excel', 'xlsx')
    path_to_save = os.path.join(pdf_home, file_name)
    #print '5.3.2 awb data list received...bid, file name',bill_id, file_name
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format()
    header_format.set_bg_color('yellow')
    header_format.set_bold()
    plain_format = workbook.add_format()

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, col_count, 12) # set column width
    sheet.write(0, 2, "AirwayBill Wise Charges")
    sheet.write(0, 5, 'Customer Name: '+billing.customer.name)
    sheet.write(1, 5, 'Bill No: '+str(billing.id))
    bill_period = 'Bill Period: ' + billing.billing_date_from.strftime('%Y-%m-%d') +\
            ' To ' + billing.billing_date.strftime('%Y-%m-%d')
    sheet.write(2, 5, bill_period)
    sheet.write(3, 5, 'Products Type: COD')
    for col, name in enumerate(col_heads):
        sheet.write(5, col, name, header_format)

    # write data to excel sheet
    #print '5.3.3 writing data to excel file..'
    data_list_gen = get_awb_table_data_direct(bill_id, 'cod')
    #print '5.3.4 awb data list received...'
    row_num = 6
    for data_list in data_list_gen:
        print '5.3.4.1 writing row to excel file..', data_list
        for col, val in enumerate(data_list):
            sheet.write_string(row_num, col, str(val))
        row_num+=1

    #print '5.3.5 writing total values data to excel file..'
    awb_total_table = get_awb_total_table_data(bill_id, 'cod')
    for row, data_list in enumerate(awb_total_table, start=row_num+2):
        row_num += 1
        print '5.3.4.1 writing row to excel file..', data_list
        for col, val in enumerate(data_list, start=3):
            #print '5.3.5.1 writing data to excel file..',str(val)
            sheet.write_string(row, col, str(val))

    # PPD SECTION ####################
    row_num += 2
    sheet.write(row_num + 2, 5, 'Customer Name: '+billing.customer.name)
    sheet.write(row_num + 3, 5, 'Bill No: '+str(billing.id))
    bill_period = 'Bill Period: ' + billing.billing_date_from.strftime('%Y-%m-%d') + \
            ' To ' + billing.billing_date.strftime('%Y-%m-%d')
    sheet.write(row_num + 4, 5, bill_period)
    sheet.write(row_num + 5, 5, 'Products Type: PPD')
    for col, name in enumerate(col_heads):
        sheet.write(row_num + 7, col, name, header_format)

    # write data to excel sheet
    #print '5.3.3 writing data to excel file..'
    data_list_gen = get_awb_table_data_direct(bill_id, 'ppd')
    #print '5.3.4 awb data list received...'
    row_num += 8
    for data_list in data_list_gen:
        print '5.3.4.1 writing row to excel file..',data_list
        for col, val in enumerate(data_list):
            sheet.write_string(row_num, col, str(val))
        row_num+=1

    #print '5.3.5 writing total values data to excel file..'
    awb_total_table = get_awb_total_table_data(bill_id, 'ppd')
    for row, data_list in enumerate(awb_total_table, start=row_num+2):
        row_num+=1
        print '5.3.4.1 writing row to excel file..',data_list
        for col, val in enumerate(data_list, start=3):
            #print '5.3.5.1 writing data to excel file..',str(val)
            sheet.write_string(row, col, str(val))

    # GRAND TOTAL
    awb_total_table = get_awb_total_table_data(bill_id)
    row_num+=3
    sheet.write_string(row_num, 0, 'GRAND TOTAL FOR ALL PRODUCTS')
    for row, data_list in enumerate(awb_total_table, start=row_num+2):
        for col, val in enumerate(data_list, start=3):
            #print '5.3.5.1 writing data to excel file..',str(val)
            sheet.write_string(row, col, str(val))

    workbook.close()
    #print '5.3.6 excel file generated..',file_name
    del data_list, data_list_gen, workbook, sheet, header_format, \
        plain_format, col_heads, billing, bill_id, awb_total_table

    return file_name

def generate_bill_pdf(bill_id, with_header=True, preview=False):
    """This function will generate pdf report for the given bill_id
        generate_bill_pdf(bill_id) --> pdf_file_name
    """
    # preapre the data to be written to pdf
    if preview:
        billing = BillingPreview.objects.get(id=bill_id)
    else:
        billing = Billing.objects.get(id=bill_id)

    if billing.billing_date:
        due_date = billing.billing_date + datetime.timedelta(10)
    else:
        due_date = ""
    total_amount = billing.balance +\
        billing.total_payable_charge +\
        billing.adjustment -\
        billing.received -\
        billing.adjustment_cr

    if with_header:
        file_name = get_filename(bill_id, 'bill_wise', 'pdf', preview=preview)
    else:
        file_name = get_filename(bill_id, 'bill_wise_without_header', 'pdf', preview=preview)

    full_file_name = os.path.join(pdf_home, file_name)
    doc = SimpleDocTemplate(full_file_name, pagesize=A4, topMargin=50,
              bottomMargin=30, leftMargin=60, rightMargin=60)
    # container for the 'Flowable' objects
    elements = []

    # header
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
        bill_id, total_amount, due_date, preview=preview)
    elements.append(invoice_header_table)
    elements.append(Spacer(1, 20))

    # account summary section
    account_summary_header = Table([['Account Summary']], colWidths=(450))
    account_summary_header.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0 ,0), (-1, -1), 0.25, colors.black),
        ]))
    elements.append(account_summary_header)

    account_summary_table = get_bill_account_summary_table(
        bill_id, total_amount, preview=preview)

    elements.append(account_summary_table)
    elements.append(Spacer(1, 20))

    # summary of charges section
    soc_heading = Paragraph('<font size=9><b>Summary Of Charges<b></font>', styles["LJustify"])
    elements.append(soc_heading)
    elements.append(Spacer(1, 12))

    soc_table_left = get_bill_soc_table_left(bill_id, preview=preview)
    soc_table_right = get_bill_soc_table_right(bill_id, preview=preview)

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

    # customer code airwaybill section
    cust_code_header = Table([[Paragraph(
        '<b>Customer Code/Sub-Code wise Summary</b>',
        styles["CustCodeHead"])]],
        colWidths=(550))
    cust_code_header.setStyle(TableStyle([
        #('BACKGROUND', (0, 0), (0, 0), colors.Color(0.4, 0.4, 0.4)),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
    elements.append(cust_code_header)

    cust_code_wise_summary_table = get_cust_code_summary_table(bill_id, preview=preview)
    elements.append(cust_code_wise_summary_table)
    elements.append(Spacer(1, 20))

    doc.build(elements)
    print 'pdf generated...',file_name
    return file_name

def delete_awb_chunks(files):
    try:
        for filename in files:
            os.remove(filename)
    except OSError:
        pass

def get_awb_table_data_direct(bill_id, ptype=None):
    print 'getting table data for total pdf ',bill_id
    billing = Billing.objects.get(pk=bill_id)
    if ptype:
        shipments = billing.shipments.filter(product_type=ptype)
    else:
        shipments = billing.shipments.all()
    if not shipments.count():
        yield [[0]*21]

    awb_table_data = []
    count = 1
    next_count = 1
    for index, shipment in enumerate(shipments, start=1):
        #print 'get data from table..'
        if count >= next_count:
            next_count = count + 100
        count = count + 1
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

            revchg = op.reverse_charge,
            sddchg = op.sdd_charge,
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
        parent_awb_date = ""
        if shipment.ref_airwaybill_number:
             ref_shipment = Shipment.objects.get(airwaybill_number = shipment.ref_airwaybill_number)
             parent_awb_date = ref_shipment.shipment_date
        rts_status = shipment.rts_status

        ls = [index,
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
             shipment.pincode,
             status, #to add,
             parent_awb, #to add
             parent_awb_date,
             rts_status
             ]
        yield ls

    #del shipments, billing
    #return awb_table_data

def generate_awb_pdf(bill_id):
    #print '5.2.1 generate awb details pdf for ', bill_id
    # create multiple pdf files for 500 shipments each and get all file names.
    #print '5.2.2 generating awb details pdf chunks...'
    files = generate_awb_pdf_chunks(bill_id)
    #combine all filenames and create combined pdf file
    #print '5.2.3 combining all awb details pdf chunks ...'
    full_file_name = get_filename(bill_id, 'awb_wise', 'pdf')
    file_name = generate_combined_pdf(files, full_file_name)
    delete_awb_chunks(files)
    #print '5.2.4 combined pdf generated ...', file_name
    #print 'awb pdf file generated...'
    ps_filename = file_name[:-2] + 's'
    subprocess.Popen(['pdftops', file_name, ps_filename])
    return ps_filename

def generate_combined_pdf(download_files, filename):
    output = pyPdf.PdfFileWriter()
    for dfile in download_files:
        fileName, fileExt = os.path.splitext(dfile)
        if fileExt == '.xlsx':
            continue
        f = open(dfile, 'rb')
        inputf = pyPdf.PdfFileReader(f)
        for page in range(inputf.getNumPages()):
            output.addPage(inputf.getPage(page))

    outs = open(filename, 'wb')
    output.write(outs)
    outs.close()
    return filename

def email_bill_report(files):
    email_msg = '  '.join(files)
    email_msg = 'Please download the bill generation pdfs from the following links\n' + email_msg
    #to_email = ("samar@prtouch.com", "jignesh@prtouch.com", "jaideeps@ecomexpress.in", "jinesh@prtouch.com")
    to_email = ("samar@prtouch.com", "jignesh@prtouch.com", "jinesh@prtouch.com")
    from_email = "support@ecomexpress.in"
    send_mail("Bills Generated", email_msg, from_email, to_email)

def generate_all_reports_for_bill_ids(bills_list):
    print 'BILLS LIST IS ',bills_list
    download_files = []
    #bills_list = sorted(bills_list, reverse=True)
    for bill_id in bills_list:
        print '5.1 start generating pdfs for bill ...',bill_id
        bill_pdf = generate_bill_pdf(bill_id)
        print 'bill pdf generated...'
        hbill_pdf = generate_bill_pdf(bill_id, with_header=False)
        print 'no head bill pdf generated...'
        download_files.append(bill_pdf)
        download_files.append(hbill_pdf)
    #for bill_id in bills_list:
        #print '5.3 start generating excel for awb...',bill_id
        #awb_excel = generate_awb_excel(bill_id)
        #download_files.append(awb_excel)
    #for bill_id in bills_list:
        #print '5.2 start generating pdfs for awb...',bill_id
       #billing_count_check = Billing.objects.get(pk=bill_id)
        #awb_pdf = generate_awb_pdf(bill_id)
        #download_files.append(awb_pdf)
    print '6. pdfs generation finished.. now generate combined pdfs'
    #download_files = [pdf_home + item for item in download_files]

    # generate an aggregate pdf book containing all billwise
    # and awb wise bills
    #filename = pdf_home + combined_pdf_name
    #file_name = generate_combined_pdf(download_files, filename)
    #download_files.append(file_name)

    print '7. combined pdfs generated.. now send emails..'
    # email the result
    #email_bill_report(download_files)
    ##print '8. Email send...'
    #print 'END: all bills generated...', len(bills_list), bills_list
    return True

def get_bill_summary_data(bill_id):
    """ generate pdf containing bill information"""
    bill = Billing.objects.get(pk=bill_id)

    ppdbill = ProductBilling.objects.filter(billing__id=bill_id, product__product_name='ppd')
    codbill = ProductBilling.objects.filter(billing__id=bill_id, product__product_name='cod')
    ebsppdbill = ProductBilling.objects.filter(billing__id=bill_id, product__product_name='ebsppd')
    ebscodbill = ProductBilling.objects.filter(billing__id=bill_id, product__product_name='ebscod')
    revbill = ProductBilling.objects.filter(billing__id=bill_id, product__product_name='rev')
    if ppdbill.exists():
        ppdbill = ppdbill[0]
        ship_count = int(ppdbill.shipment_count) if ppdbill.shipment_count else 0
        ppdlist = [
            'PPD', ppdbill.billing.customer.code, 
            ppdbill.billing.customer.name,
            ppdbill.billing.billing_date, ppdbill.billing.id, 
            ship_count, ppdbill.total_chargeable_weight,
            ppdbill.freight_charge, ppdbill.fuel_surcharge, ppdbill.sdl_charge,
            ppdbill.sdd_charge, ppdbill.reverse_charge, ppdbill.rto_charge, 
            ppdbill.valuable_cargo_handling_charge, ppdbill.cod_applied_charge,
            ppdbill.cod_subtract_charge, 
            ppdbill.cod_applied_charge + ppdbill.cod_subtract_charge, '', 
            ppdbill.total_charge_pretax, ppdbill.service_tax, 
            ppdbill.education_secondary_tax, ppdbill.cess_higher_secondary_tax, 
            ppdbill.total_payable_charge]
    else:
        ppdlist = [0]*22
        ppdlist[0] = 'PPD'

    if codbill.exists():
        codbill = codbill[0]
        ship_count = int(codbill.shipment_count) if codbill.shipment_count else 0
        codlist = [ 'COD', codbill.billing.customer.code, codbill.billing.customer.name,
            codbill.billing.billing_date, codbill.billing.id, ship_count, codbill.total_chargeable_weight,
            codbill.freight_charge, codbill.fuel_surcharge, codbill.sdl_charge,
            codbill.sdd_charge, codbill.reverse_charge, codbill.rto_charge, codbill.valuable_cargo_handling_charge,
            codbill.cod_applied_charge, codbill.cod_subtract_charge, codbill.total_cod_charge, '', codbill.total_charge_pretax, codbill.service_tax, codbill.education_secondary_tax, codbill.cess_higher_secondary_tax, codbill.total_payable_charge]
    else:
        codlist = [0]*22
        codlist[0] = 'COD'

    if ebsppdbill.exists():
        ebsppdbill = ebsppdbill[0]
        ship_count = int(ebsppdbill.shipment_count) if ebsppdbill.shipment_count else 0
        ebsppdlist = [ 'EBSPPD', ebsppdbill.billing.customer.code, ebsppdbill.billing.customer.name,
            ebsppdbill.billing.billing_date, ebsppdbill.billing.id, ship_count, ebsppdbill.total_chargeable_weight,
            ebsppdbill.freight_charge, ebsppdbill.fuel_surcharge, ebsppdbill.sdl_charge,
            ebsppdbill.sdd_charge, ebsppdbill.reverse_charge, ebsppdbill.rto_charge, ebsppdbill.valuable_cargo_handling_charge,
            ebsppdbill.cod_applied_charge, ebsppdbill.cod_subtract_charge, ebsppdbill.total_cod_charge, '', ebsppdbill.total_charge_pretax, ebsppdbill.service_tax, ebsppdbill.education_secondary_tax, ebsppdbill.cess_higher_secondary_tax, ebsppdbill.total_payable_charge]
    else:
        ebsppdlist = [0]*22
        ebsppdlist[0] = 'EBSPPD'

    if ebscodbill.exists():
        ebscodbill = ebscodbill[0]
        ship_count = int(ebscodbill.shipment_count) if ebscodbill.shipment_count else 0
        ebscodlist = [ 'EBSCOD', ebscodbill.billing.customer.code, ebscodbill.billing.customer.name,
            ebscodbill.billing.billing_date, ebscodbill.billing.id, ship_count, ebscodbill.total_chargeable_weight,
            ebscodbill.freight_charge, ebscodbill.fuel_surcharge, ebscodbill.sdl_charge,
            ebscodbill.sdd_charge, ebscodbill.reverse_charge, ebscodbill.rto_charge, ebscodbill.valuable_cargo_handling_charge,
            ebscodbill.cod_applied_charge, ebscodbill.cod_subtract_charge, ebscodbill.total_cod_charge, '', ebscodbill.total_charge_pretax, ebscodbill.service_tax, ebscodbill.education_secondary_tax, ebscodbill.cess_higher_secondary_tax, ebscodbill.total_payable_charge]
    else:
        ebscodlist = [0]*22
        ebscodlist[0] = 'EBSCOD'

    if revbill.exists():
        revbill = revbill[0]
        ship_count = int(revbill.shipment_count) if revbill.shipment_count else 0
        revlist = [ 'REVERSE', revbill.billing.customer.code, revbill.billing.customer.name,
            revbill.billing.billing_date, revbill.billing.id, ship_count, revbill.total_chargeable_weight,
            revbill.freight_charge, revbill.fuel_surcharge, revbill.sdl_charge,
            revbill.sdd_charge, revbill.reverse_charge, revbill.rto_charge, revbill.valuable_cargo_handling_charge,
            revbill.cod_applied_charge, revbill.cod_subtract_charge, revbill.total_cod_charge, '', revbill.total_charge_pretax, revbill.service_tax, revbill.education_secondary_tax, revbill.cess_higher_secondary_tax, revbill.total_payable_charge]
    else:
        revlist = [0]*22
        revlist[0] = 'REVERSE'

    data = [ppdlist, codlist, ebsppdlist, ebscodlist, revlist,
        [ 'Total', bill.customer.code, bill.customer.name, '', bill.id, bill.shipment_count, bill.total_chargeable_weight, bill.freight_charge,
        bill.fuel_surcharge, bill.sdl_charge, bill.sdd_charge, bill.reverse_charge, bill.rto_charge, bill.valuable_cargo_handling_charge,
        bill.cod_applied_charge, bill.cod_subtract_charge, bill.total_cod_charge, '', bill.total_charge_pretax, bill.service_tax,
        bill.education_secondary_tax, bill.cess_higher_secondary_tax, bill.total_payable_charge]]
    return data

def generate_bill_summary_xls(bill_list):
    col_heads=(
        'Product',
        'code',
        'Customer',
        'Billing Date',
        'Bill No',
        'Shipment Count',
        'Weight ',
        'Freight',
        'Fuel',
        'SDL',
        'SDD',
        'Reverse',
        'RTO',
        'VCHC Charge',
        'COD Applied',
        'COD reversed',
        'COD Final',
        'Discount',
        'Total Pre Tax',
        'Service Tax',
        'Edu Cess',
        'Hsc ',
        'Total With Tax')

    col_count = len(col_heads)
    # add filename and set save file path
    file_name = get_bill_summary_filename(bill_list[0], 'bill_summary', 'xlsx')
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

    # write data to excel sheet
    #print '5.3.3 writing data to excel file..'
    data_matrix = []
    for bill_id in bill_list:
        l = get_bill_summary_data(bill_id)
        data_matrix.extend(l)

    total_row = defaultdict(float)
    row_count = 3
    #pdb.set_trace()
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


    del data_list, data_matrix
    workbook.close()
    return file_name
