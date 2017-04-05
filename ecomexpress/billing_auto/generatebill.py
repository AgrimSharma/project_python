'''
Created on 29-May-2013

@author: prtouch
'''
import os
import datetime
import xlrd
import pyPdf
from multiprocessing import Pool
from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Count, Sum
from django.core.mail import send_mail

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate,\
    Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT, TA_CENTER

from billing.models import BillingSubCustomer, Billing
from service_centre.models import Shipper, Customer, MinActualWeight,\
    StatusUpdate, Shipment

#img_location = settings.PROJECT_ROOT + '/ecomexpress' + \
    #settings.STATIC_URL + 'assets/img/EcomlogoPdf.png'

#pdf_home = settings.PROJECT_ROOT + '/ecomexpress' + \
    #settings.STATIC_URL + 'uploads/billing/'
PROJECT_ROOT = '/home/web/ecomm.prtouch.com/ecomexpress'
#PROJECT_ROOT = '/home/prtouch/workspace/ecomexpress'
img_location = PROJECT_ROOT + '/static/assets/img/EcomlogoPdf.png'

pdf_home = PROJECT_ROOT + settings.STATIC_URL + 'uploads/billing/'
pdf_folder = settings.STATIC_URL + 'uploads/billing/'
combined_pdf_name = 'combined_pdf_%s.pdf' % datetime.datetime.today().strftime('%Y_%m_%d')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='LJustify', alignment=TA_LEFT))
styles.add(ParagraphStyle(name='RJustify', alignment=TA_RIGHT))
styles.add(ParagraphStyle(name='CJustify', alignment=TA_CENTER))
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='AWB_heading',
                          alignment=TA_CENTER,
                          fontSize=6))
styles.add(ParagraphStyle(name='Text6', fontSize=6))
styles.add(ParagraphStyle(name='BoldRight',
                          alignment=TA_RIGHT,
                          fontSize=6))
styles.add(ParagraphStyle(name='ImpPara',
                          alignment=TA_LEFT,
                          fontSize=6))
styles.add(ParagraphStyle(name='InvoiceHead',
                          alignment=TA_CENTER,
                          textColor="grey"))
styles.add(ParagraphStyle(name='InvoicePara',
                          alignment=TA_LEFT,
                          leftIndent=10,
                          fontSize=8))
styles.add(ParagraphStyle(name='CustCodeHead',
                          alignment=TA_CENTER,
                          textColor="white",
                          fontSize=6))
styles.add(ParagraphStyle(name='BillHeadL',
                          alignment=TA_LEFT,
                          spaceBefore=0,
                          leading=12,
                          spaceAfter=0,
                          fontSize=5))
styles.add(ParagraphStyle(name='BillHeadR',
                          alignment=TA_LEFT,
                          spaceBefore=1,
                          spaceAfter=1,
                          leftIndent=6,
                          fontSize=6))


def rectify_dict(d):
    """ this function takes a dict as input and check all values,
        if any of the value is None replace it with zero
    """
    for k in d.keys():
        d[k] = 0 if d[k] is None else d[k]
    return d


def init_billing_fields(billing):
    billing.freight_charge = 0
    billing.sdl_charge = 0
    billing.fuel_surcharge = 0
    billing.valuable_cargo_handling_charge = 0
    billing.to_pay_charge = 0
    billing.rto_charge = 0
    billing.total_charge = 0
    billing.cod_applied_charge = 0
    billing.cod_subtract_charge = 0
    billing.total_cod_charge = 0
    billing.save()
    return billing


def update_subcustomer_billing_fields(shipper):
    sbilling = BillingSubCustomer.objects.filter(
        subcustomer=shipper,
        generation_status=0)

    if sbilling:
        sbilling = sbilling[0]
        sbilling.freight_charge = 0
        sbilling.sdl_charge = 0
        sbilling.fuel_surcharge = 0
        sbilling.valuable_cargo_handling_charge = 0
        sbilling.to_pay_charge = 0
        sbilling.rto_charge = 0
        sbilling.total_charge = 0
        sbilling.cod_applied_charge = 0
        sbilling.cod_subtract_charge = 0
        sbilling.total_cod_charge = 0
        sbilling.save()
        sbilling.shipments.remove(*sbilling.shipments.all())

    print '2.3.5.1.1 subcustomer.... billing updated..'
    return sbilling


def update_billing(code, date_from, date_to):
    ''' update billing from utils.py'''
    customer = Customer.objects.get(code=code)
    print '2.3.1 inside update billing...cid ', customer.id
    bill_from = date_from.strftime('%Y-%m-%d 07:00:00')
    bill_to = date_to.strftime('%Y-%m-%d 07:00:00')
    shipments = Shipment.objects.filter(
        shipper=customer,
        inscan_date__range=(bill_from, bill_to)).\
            annotate(Count('order_price'),
                     op_freight=Sum('order_price__freight_charge'),
                     op_sdl=Sum('order_price__sdl_charge'),
                     op_fuel=Sum('order_price__fuel_surcharge'),
                     op_rto_price=Sum('order_price__rto_charge'),
                     op_to_pay=Sum('order_price__to_pay_charge'))

    print '2.3.2 shipments collected for customer'

    if not shipments.count():
        print '2.3.2x no shipments found...'
        return None

    print '2.3.3 update billing for customer ',customer.id
    billing, created = Billing.objects.get_or_create(customer=customer,
                                                     generation_status=0)
    billing = init_billing_fields(billing)
    billing.shipments.remove(*billing.shipments.all())
    if not billing.bill_generation_date:
        billing.bill_generation_date = datetime.datetime.now()
    billing.save()
    print '2.3.4 billing saved..', billing.pk

    # get all the sub customers for the customer
    shippers = Shipper.objects.filter(customer=billing.customer)

    print '\n2.3.5 update billin for subcustomers....',customer.id
    for shipper in shippers:
        print '2.3.5.1 subcustomer....',customer.id,shipper.id
        update_subcustomer_billing_fields(shipper)

    billing.billing_date_from = date_from
    billing.billing_date = date_to
    bill_date = date_from
    billing.save()

    sum_dict = shipments.aggregate(
        freight_sum=Sum('op_freight'),
        sdl_sum=Sum('op_sdl'),
        fuel_sum=Sum('op_fuel'),
        rto_sum=Sum('op_rto_price'),
        to_pay_sum=Sum('op_to_pay'))

    sum_dict = rectify_dict(sum_dict)

    print '2.3.6 sum dict produced for customer ..'
    # update billing charges from shipment order price values
    billing.freight_charge += sum_dict.get('freight_sum', 0)
    billing.sdl_charge += sum_dict.get('sdl_sum', 0)
    billing.fuel_surcharge += sum_dict.get('fuel_sum', 0)
    billing.rto_charge += sum_dict.get('rto_sum', 0)
    billing.to_pay_charge += sum_dict.get('to_pay_sum', 0)

    # get all shipments with product_type cod and rts_status 1,
    # all shipments with product_type cod and rts_status other than 1
    # and update cod_subtract_charge, total_cod_charge, and cod_applied_charge
    # of billing
    cod_shipments = shipments.filter(product_type='cod').\
            annotate(cc_cod_charge=Sum('codcharge__cod_charge'))
    cod_shipments_rts_1 = cod_shipments.filter(rts_status=1).\
            aggregate(Sum('cc_cod_charge'))
    cod_shipments_rts_not_1 = cod_shipments.exclude(rts_status=1).\
            aggregate(Sum('cc_cod_charge'))

    cod_shipments_rts_1 = rectify_dict(cod_shipments_rts_1)
    cod_shipments_rts_not_1 = rectify_dict(cod_shipments_rts_not_1)
    cod_rts_1_charge = cod_shipments_rts_1.get('cc_cod_charge__sum', 0)
    cod_rts_not_1_charge = cod_shipments_rts_not_1.get('cc_cod_charge__sum', 0)

    billing.cod_subtract_charge += cod_rts_1_charge
    billing.total_cod_charge =  billing.total_cod_charge + \
            cod_rts_not_1_charge - \
            cod_rts_1_charge
    billing.cod_applied_charge = cod_rts_not_1_charge

    bill_ships = shipments.filter(order_price__count__gte=0)
    billing.shipments = bill_ships
    # update the billing for all bill_ships
    bill_ships.update(billing=billing)
    billing.save()
    print '2.3.7 billing again updated ..bid ',billing.pk
    #print 'billing updated..'
    print '2.3.8.now update bililng for subcustomers..'
    # update subcustomer billing
    sub_customers = shipments.values('pickup__subcustomer_code').distinct()
    sub_customers_code = [s.get('pickup__subcustomer_code')
                          for s in sub_customers if s.get('pickup__subcustomer_code')]

    # for each unique subcustomers from shipments, update billing for sub
    # customers
    for sub_customer in sub_customers_code:
        print '2.3.8.1 sub customer code ----> ',sub_customer
        subcustomer = Shipper.objects.get(pk=sub_customer)
        sub_ships = shipments.filter(pickup__subcustomer_code=sub_customer).\
            annotate(Count('order_price'),
                op_freight=Sum('order_price__freight_charge'),
                op_sdl=Sum('order_price__sdl_charge'),
                op_fuel=Sum('order_price__fuel_surcharge'),
                op_rto_price=Sum('order_price__rto_charge'),
                op_to_pay=Sum('order_price__to_pay_charge'))

        print '2.3.8.2 updating sub customer...', subcustomer.id,'  -- ', sub_ships.count()
        sub_sum_dict = sub_ships.aggregate(
            freight_sum=Sum('op_freight'),
            sdl_sum=Sum('op_sdl'),
            fuel_sum=Sum('op_fuel'),
            rto_sum=Sum('op_rto_price'),
            to_pay_sum=Sum('op_to_pay'))

        sub_sum_dict = rectify_dict(sub_sum_dict)
        print '2.3.8.3 sub_sum_dict '
        sbilling, created = BillingSubCustomer.objects.get_or_create(
            subcustomer=subcustomer, generation_status=0)

        # update billing charges from shipment order price values
        sbilling.freight_charge += sub_sum_dict.get('freight_sum', 0)
        sbilling.sdl_charge += sub_sum_dict.get('sdl_sum', 0)
        sbilling.fuel_surcharge += sub_sum_dict.get('fuel_sum', 0)
        sbilling.rto_charge += sub_sum_dict.get('rto_sum', 0)
        sbilling.to_pay_charge += sub_sum_dict.get('to_pay_sum', 0)

        # get all shipments with product_type cod and rts_status 1,
        # all shipments with product_type cod and rts_status other than 1
        # and update cod_subtract_charge, total_cod_charge, and cod_applied_charge
        # of billing
        cod_shipments = sub_ships.filter(product_type='cod').\
            annotate(cc_cod_charge=Sum('codcharge__cod_charge'))
        cod_shipments_rts_1 = cod_shipments.filter(rts_status=1).\
            aggregate(Sum('cc_cod_charge'))
        cod_shipments_rts_not_1 = cod_shipments.exclude(rts_status=1).\
            aggregate(Sum('cc_cod_charge'))

        cod_shipments_rts_1 = rectify_dict(cod_shipments_rts_1)
        cod_shipments_rts_not_1 = rectify_dict(cod_shipments_rts_not_1)
        cod_rts_1_charge = cod_shipments_rts_1.get('cc_cod_charge__sum', 0)
        cod_rts_not_1_charge = cod_shipments_rts_not_1.get('cc_cod_charge__sum', 0)

        sbilling.cod_subtract_charge += cod_rts_1_charge
        sbilling.total_cod_charge = sbilling.total_cod_charge + \
            cod_rts_not_1_charge - \
            cod_rts_1_charge
        sbilling.cod_applied_charge += cod_rts_not_1_charge

        sbill_ships = sub_ships.filter(order_price__count__gte=0)
        sbilling.shipments = sbill_ships
        sbill_ships.update(sbilling=sbilling)
        sbilling.billing = billing
        sbilling.save()
        print '2.3.8.4 subcustomer billing updated..'

    print '2.3.9 billing updated.. returing back to callee'
    return billing


def make_bold(val):
    return Paragraph('<b>%s</b>' % str(val), styles["Text6"])


def make_bold_right(val):
    return Paragraph('<b>%s</b>' % str(val), styles["BoldRight"])


def truncate(text):
    if text and len(text) > 25:
        return text[:25] + '..'
    else:
        return text


def generate_bill(*args, **kwargs):
    print '2.1 inside generate_bill'
    from_excel = kwargs.get('from_excel')
    code = kwargs.get('code')
    balance = kwargs.get('balance')
    payment = kwargs.get('payment')
    adjustments = kwargs.get('adjustments')
    adjust_cr = kwargs.get('adjust_cr')
    date_from_str = kwargs.get('date_from')
    date_to_str = kwargs.get('date_to')
    date_from = datetime.datetime.strptime(date_from_str, "%Y%m%d").date()
    date_to = datetime.datetime.strptime(date_to_str, "%Y%m%d").date() + datetime.timedelta(days=1)

    print '2.2 Args ',args,kwargs

    billing = update_billing(code, date_from, date_to)

    if not billing:
        print '2.3x Error: Billing not updated for customer code %s ' % code
        return None

    print '2.3 bill received.. '
    # if generate bill is not called from excel following variables will not be
    # available.
    if from_excel:
        billing.billing_date = date_to
        billing.balance = balance
        billing.received = payment
        billing.adjustment = adjustments
        billing.adjustment_cr = adjust_cr
    billing.bill_generation_date = datetime.datetime.today()

    billing.total_charge = billing.freight_charge +\
        billing.sdl_charge +\
        billing.fuel_surcharge +\
        billing.valuable_cargo_handling_charge +\
        billing.to_pay_charge +\
        billing.rto_charge
    billing.total_cod_charge = billing.cod_applied_charge -\
        billing.cod_subtract_charge
    billing.total_charge_pretax = billing.freight_charge +\
        billing.sdl_charge +\
        billing.fuel_surcharge +\
        billing.valuable_cargo_handling_charge +\
        billing.to_pay_charge +\
        billing.rto_charge +\
        billing.demarrage_charge +\
        billing.total_cod_charge
    billing.service_tax = round(billing.total_charge_pretax * 0.12, 2)
    billing.education_secondary_tax = round(billing.service_tax * 0.02, 2)
    billing.cess_higher_secondary_tax = round(billing.service_tax *
                                              0.01, 2)
    billing.total_payable_charge = billing.total_charge_pretax +\
        billing.service_tax +\
        billing.education_secondary_tax +\
        billing.cess_higher_secondary_tax
    billing.generation_status = 1
    billing.save()
    print '2.4 Billing value updation completed ..'

    shippers = Shipper.objects.filter(customer=billing.customer)
    print '2.5 update billing subcustomer objects..'

    for shipper in shippers:
        print '2.5.1 updating subcustomer :',billing.customer.id, shipper.id
        BillingSubCustomer.objects.filter(
            subcustomer=shipper,
            generation_status=0).update(
                billing=billing,
                billing_date=date_to.strftime("%Y-%m-%d"),
                generation_status = 1)
    print '2.6 Shippers billing updated .. returning from generate billing'
    return billing


def get_awb_table_data(bill_id):
    print '4.6.4.1.1 inside awb table data generation function...bill_id is :',bill_id
    billing = Billing.objects.get(pk=bill_id)
    minactualweight = MinActualWeight.objects.all()
    def get_sub_cust_code(shipment):
        print '\n4.6.4.1.x.1 get sub_cust_coe...',shipment.airwaybill_number
        try:
            return str(shipment.shipper.code) + \
                  str(shipment.pickup.subcustomer_code.id) + '-' +\
                  str(shipment.pickup.subcustomer_code.name)
        except:
            return str(shipment.shipper.code)

    def get_destination(shipment):
        print '\n4.6.4.1.x.2 get destination...',shipment.airwaybill_number
        if shipment.original_dest and shipment.return_shipment > 0:
            return shipment.original_dest
        else:
            return shipment.service_centre

    def get_accurate_weight(shipment):
        print '\n4.6.4.1.x.3 get accurate weight...',shipment.airwaybill_number
        minwt = minactualweight.filter(customer=shipment.shipper)
        min_actual_weight = minwt[0].weight if minwt else 0
        max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        if min_actual_weight:
            if max_weight_dimension < min_actual_weight:
                max_weight_dimension =  shipment.actual_weight
            else:
                max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        else:
            max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        print '\n4.6.4.1.x.3 get accurate weight...',max_weight_dimension
        return max_weight_dimension

    def get_freight(shipment):
        print '\n4.6.4.1.x.4 get freight...',shipment.airwaybill_number
        minwt = minactualweight.filter(customer=shipment.shipper)
        ps = shipment.order_price_set.all()
        if ps.count() > 0:
            fc = ps[0].freight_charge
        else:
            fc = 0
        print '\n4.6.4.1.x.4 get freight...',round(fc, 2)
        return round(fc, 2)

    def get_cod(shipment):
        print '\n4.6.4.1.x.5.1 get cod...',shipment.airwaybill_number
        cod = shipment.codcharge_set.all()
        if cod.count() > 0:
            cod = shipment.codcharge_set.all()[0].cod_charge
        else:
            cod = 0
        if shipment.return_shipment == 3:
            print '\n4.6.4.1.x.5.2 get cod...',round(cod, 2)
            return round(0-cod, 2)
        print '\n4.6.4.1.x.5.2 get cod...',round(cod, 2)
        return round(cod, 2)

    def get_others(op):
        print '\n4.6.4.1.x.6 get others...'
        if not op:
            return 0
        if not op.sdl_charge:
            op.sdl_charge = 0
        other_price = op.sdl_charge + \
                op.rto_charge + \
                op.to_pay_charge + \
                op.valuable_cargo_handling_charge
        print '\n4.6.4.1.x.6 get others...',round(other_price, 2)
        return round(other_price, 2)

    def get_total(shipment):
        print '\n4.6.4.1.x.7 get total...',shipment.airwaybill_number
        op = shipment.order_price_set.all()[0]
        if not op.sdl_charge:
            op.sdl_charge = 0
        total_op = op.sdl_charge + \
                op.rto_charge + \
                op.to_pay_charge + \
                op.freight_charge + \
                op.valuable_cargo_handling_charge
        if shipment.codcharge_set.all():
            codcharge = shipment.codcharge_set.all()[0].cod_charge
        else:
            codcharge = 0
        print '\n4.6.4.1.x.7 get total...',round(total_op + codcharge, 2)
        return round(total_op + codcharge, 2)

    print '4.6.4.1.2 getting awb table data...'

    if not billing.shipments.all().count():
        print '4.6.4.1.3 no shipments in billing..',[[0]*12]
        return [[0]*12]

    awb_table_data = (
        [index,
         get_sub_cust_code(shipment),
         shipment.airwaybill_number,
         shipment.order_number,
         shipment.added_on.strftime('%d %b, %Y'),
         shipment.product_type,
         get_destination(shipment),
         get_accurate_weight(shipment),
         get_freight(shipment),
         get_cod(shipment),
         get_others(shipment.order_price_set.all()[0]),
         get_total(shipment)]
        for index, shipment in enumerate(billing.shipments.all(), start=1))

    print '4.6.4.1.4 awb table data generated returing to callee...'
    return awb_table_data


def get_awb_table(billing):
    print '4.5.4.1 get awb table...',billing.__dict__
    awb_table_headers = [
         Paragraph('<b>Sl No</b>', styles["AWB_heading"]),
         Paragraph('<b>Cust/Sub Cust Code</b>', styles["AWB_heading"]),
         Paragraph('<b>Air Waybill No</b>', styles["AWB_heading"]),
         Paragraph('<b>Order No</b>', styles["AWB_heading"]),
         Paragraph('<b>Date</b>', styles["AWB_heading"]),
         Paragraph('<b>Service</b>', styles["AWB_heading"]),
         Paragraph('<b>Destination</b>', styles["AWB_heading"]),
         Paragraph('<b>Weight</b>', styles["AWB_heading"]),
         Paragraph('<b>Freight</b>', styles["AWB_heading"]),
         Paragraph('<b>COD</b>', styles["AWB_heading"]),
         Paragraph('<b>Others</b>', styles["AWB_heading"]),
         Paragraph('<b>Total</b>', styles["AWB_heading"])
    ]

    awb_table_data = list(get_awb_table_data(billing.pk))
    print '4.5.4.2 got awb table data...'
    awb_table_data.insert(0, awb_table_headers)
    awb_table = Table(awb_table_data,
            splitByRow=True,
            repeatRows=1,
            colWidths=(40, 100, 60, 40, 40, 40, 50, 40, 40, 40, 40, 30))
    awb_table.setStyle(TableStyle([
        ('ALIGN',(0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING',(2, 0), (2, -1), 1),
        ('FONTSIZE',(0, 0),(-1, 0), 6),
        ('FONTSIZE',(0, 1),(-1, -1), 6),
        ]))

    print '4.5.4.3 awb table generated returning to callee..'
    return awb_table


def get_awb_total_table(billing):
    total_table_data = [
        ['Total', round(billing.total_charge_pretax - billing.fuel_surcharge, 2)],
        ['Fuel Surcharge', round(billing.fuel_surcharge, 2)],
        ['Total Before Tax', round(billing.total_charge_pretax)],
        ['Service Tax',	round(billing.service_tax, 2)],
        ['Education Cess', round(billing.education_secondary_tax,2)],
        ['HSE Cess', round(billing.cess_higher_secondary_tax)],
        ['Grand Total',	round(billing.total_payable_charge, 2)]
    ]

    total_table = Table(total_table_data,
            splitByRow=True,
            repeatRows=1,
            repeatCols=2)
    total_table.setStyle(TableStyle([
        ('ALIGN',(0,0),(0,-1),'RIGHT'),
        ('ALIGN',(1,0),(1,-1),'LEFT'),
        ]))
    return total_table


def get_awb_chunk_table_data(shipments, index):
    print '4.5.2.2.3.2.1 inside get chunk table data ..index :', index
    minactualweight = MinActualWeight.objects.all()
    def get_sub_cust_code(shipment):
        print '\n4.5.2.2.3.2.2  get sub_cust_coe...',shipment.airwaybill_number
        try:
            return str(shipment.shipper.code) + \
                  str(shipment.pickup.subcustomer_code.id) + '-' +\
                  str(shipment.pickup.subcustomer_code.name)
        except:
            return str(shipment.shipper.code)

    def get_destination(shipment):
        print '\n4.5.2.2.3.2.3 get destination...',shipment.airwaybill_number
        if shipment.original_dest and shipment.return_shipment > 0:
            return shipment.original_dest
        else:
            return shipment.service_centre

    def get_accurate_weight(shipment):
        print '\n4.5.2.2.3.2.4 get accurate weight...',shipment.airwaybill_number
        minwt = minactualweight.filter(customer=shipment.shipper)
        min_actual_weight = minwt[0].weight if minwt else 0
        max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        if min_actual_weight:
            if max_weight_dimension < min_actual_weight:
                max_weight_dimension =  shipment.actual_weight
            else:
                max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        else:
            max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        print '\n4.5.2.2.3.2.5 get accurate weight...',max_weight_dimension
        return max_weight_dimension

    def get_freight(shipment):
        print '\n4.5.2.2.3.2.6 get freight...',shipment.airwaybill_number
        minwt = minactualweight.filter(customer=shipment.shipper)
        ps = shipment.order_price_set.all()
        if ps.count() > 0:
            fc = ps[0].freight_charge
        else:
            fc = 0
        print '\n4.5.2.2.3.2.7 get freight...',round(fc, 2)
        return round(fc, 2)

    def get_cod(shipment):
        print '\n4.5.2.2.3.2.8 get cod...',shipment.airwaybill_number
        cod = shipment.codcharge_set.all()
        if cod.count() > 0:
            cod = shipment.codcharge_set.all()[0].cod_charge
        else:
            cod = 0
        if shipment.return_shipment == 3:
            print '\n4.5.2.2.3.2.9 get cod...',round(cod, 2)
            return round(0-cod, 2)
        print '\n4.5.2.2.3.2.10 get cod...',round(cod, 2)
        return round(cod, 2)

    def get_others(op):
        print '\n4.5.2.2.3.2.11 get others...'
        if not op:
            return 0
        if not op.sdl_charge:
            op.sdl_charge = 0
        other_price = op.sdl_charge + \
                op.rto_charge + \
                op.to_pay_charge + \
                op.valuable_cargo_handling_charge
        print '\n4.5.2.2.3.2.12 get others...',round(other_price, 2)
        return round(other_price, 2)

    def get_total(shipment):
        print '\n4.5.2.2.3.2.13 get total...',shipment.airwaybill_number
        op = shipment.order_price_set.all()[0]
        if not op.sdl_charge:
            op.sdl_charge = 0
        total_op = op.sdl_charge + \
                op.rto_charge + \
                op.to_pay_charge + \
                op.freight_charge + \
                op.valuable_cargo_handling_charge
        if shipment.codcharge_set.all():
            codcharge = shipment.codcharge_set.all()[0].cod_charge
        else:
            codcharge = 0
        print '\n4.5.2.2.3.2.14 get total...',round(total_op + codcharge, 2)
        return round(total_op + codcharge, 2)

    print '4.5.2.2.3.2.15 getting awb table data...'

    awb_table_data = [
        [i,
         get_sub_cust_code(shipment),
         shipment.airwaybill_number,
         shipment.order_number,
         shipment.added_on.strftime('%d %b, %Y'),
         shipment.product_type,
         get_destination(shipment),
         get_accurate_weight(shipment),
         get_freight(shipment),
         get_cod(shipment),
         get_others(shipment.order_price_set.all()[0]),
         get_total(shipment)]
        for i, shipment in enumerate(shipments.all(), start=index)]

    print '4.5.2.2.3.2.16 returning awb table data...'
    return awb_table_data


def get_awb_chunk_table(shipments, index):
    print '4.5.2.2.3.1 inside chunk table data ..index  :', index
    awb_table_headers = [
         Paragraph('<b>Sl No</b>', styles["AWB_heading"]),
         Paragraph('<b>Cust/Sub Cust Code</b>', styles["AWB_heading"]),
         Paragraph('<b>Air Waybill No</b>', styles["AWB_heading"]),
         Paragraph('<b>Order No</b>', styles["AWB_heading"]),
         Paragraph('<b>Date</b>', styles["AWB_heading"]),
         Paragraph('<b>Service</b>', styles["AWB_heading"]),
         Paragraph('<b>Destination</b>', styles["AWB_heading"]),
         Paragraph('<b>Weight</b>', styles["AWB_heading"]),
         Paragraph('<b>Freight</b>', styles["AWB_heading"]),
         Paragraph('<b>COD</b>', styles["AWB_heading"]),
         Paragraph('<b>Others</b>', styles["AWB_heading"]),
         Paragraph('<b>Total</b>', styles["AWB_heading"])
    ]

    print '4.5.2.2.3.2 get chunk table data ..', index
    awb_table_data = get_awb_chunk_table_data(shipments, index)
    print '4.5.2.2.3.3 g0t chunk table data ..', index
    awb_table_data.insert(0, awb_table_headers)
    awb_table = Table(awb_table_data,
            splitByRow=True,
            repeatRows=1,
            colWidths=(40, 100, 60, 40, 40, 40, 50, 40, 40, 40, 40, 30))
    awb_table.setStyle(TableStyle([
        ('ALIGN',(0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING',(2, 0), (2, -1), 1),
        ('FONTSIZE',(0, 0),(-1, 0), 6),
        ('FONTSIZE',(0, 1),(-1, -1), 6),
        ]))

    print '4.5.2.2.3.4 return from chunk table data ..', index
    return awb_table


def generate_awb_pdf(shipments, billing, index):
    """ This function will take a chunk(500 for eg) of shipments
    and generate awb_wise pdf file
    generate_awb_pdf(shipments, billing, index) --> return file_name
    """
    print '4.5.2.2.1 chunk..generating..pdf.. bid, index',billing.pk, index
    # generate pdf file name
    billing_date = billing.billing_date.strftime('%Y_%m_%d')
    month = billing.billing_date.strftime('%m')
    file_name = '%s/awb_wise_%s_%s.pdf' % (
        str(month), str(billing_date), str(index))
    full_file_name = os.path.join(pdf_home, file_name)
    print '4.5.2.2.2 chunk...full file name  ',full_file_name

    doc = SimpleDocTemplate(full_file_name, pagesize=A4)
    # container for the 'Flowable' objects we add the para, tables to this
    # flowable and generate pdf at the end
    elements = []
    # page header
    if index == 1:
        page_header = Paragraph('<b>AirwayBill wise charges</b>', styles["AWB_heading"])
        elements.append(page_header)
        elements.append(Spacer(1, 12))

    # invoice head - customer and billing details
    print '4.5.2.2.3 getting chunk display table data..'
    awb_table = get_awb_chunk_table(shipments, index)
    elements.append(awb_table)
    doc.build(elements)

    print '4.5.2.2.4 chunk pdf created'
    return full_file_name


def generate_awb_pdf_chunks(billing):
    """ This function will generate a number of pdfs for shipments
    group of 5000.
    generate_awb_pdf_chunks(<billing obj>) --> list of awb pdf files
    """
    print '4.5.2.1 generating awb details pdf chunks...',billing.pk
    all_shipments = billing.shipments.all()
    if not all_shipments.count():
        return []
    ships_count = all_shipments.count()
    files = []
    for index in range(1, ships_count+1, 500):
        print '4.5.2.2 chunk.group..generating.. bid, index',billing.pk, index
        ships = all_shipments.all()[:500]
        all_shipments = all_shipments[500:]
        file_name = generate_awb_pdf(ships, billing, index)
        files.append(file_name)
        print '4.5.2.3 chunk...generated.. filename',file_name

    print '4.5.2.4 all chunks...generated.. files ',files
    return files


def get_pdf_filename(customer, billing):
    customer_id = customer.pk
    billing_date = billing.billing_date.strftime('%Y_%m_%d')
    month = billing.billing_date.strftime('%m')
    file_name = '%s/awb_wise_%s_%s_%s.pdf' % (
        str(month), str(customer_id), str(billing.pk), str(billing_date))
    full_file_name = os.path.join(pdf_home, file_name)
    return full_file_name


def generate_awb_details(awb_data):
    print '4.5.1 inside generating awb details pdf...'
    # create multiple pdf files for 500 shipments each and get all file names.
    print '4.5.2 generating awb details pdf chunks...'
    files = generate_awb_pdf_chunks(awb_data['billing'])
    print '4.5.3 awb details pdf chunks received...', files

    #combine all filenames and create combined pdf file
    print '4.5.4 combining all awb details pdf chunks ...'
    full_file_name = get_pdf_filename(awb_data['customer'], awb_data['billing'])
    file_name = generate_combined_pdf(files, full_file_name)
    print '4.5.5 combined pdf generated ...', file_name
    return file_name


def get_bill_header():
    left_head = Paragraph('''
                          <para>
                          <img src="%s" width="48" height="20" valign="0"/><br/>
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
    header_table = Table(header_data, colWidths=(200, 200, 200))
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (1, 0), 'MIDDLE')]))

    return header_table


def get_bill_invoice_table(customer,
                           billing,
                           total_amount,
                           due_date):
    invoice_bill_data = '''
        <para spaceb=3>
        <b>Bill No.</b>: {0}<br/>
        <b>Bill Period</b>: {1} to {2}<br/>
        <b>Bill Date:</b> {3}<br/>
        <b>Total amount Due:</b> {4}<br/>
        <b>Pay by:</b> {5}<br/>
        </para>'''.format(billing.id,
                          billing.billing_date_from,
                          billing.billing_date,
                          billing.billing_date,
                          round(total_amount, 2),
                          due_date)
    invoice_bill_para = Paragraph(invoice_bill_data, styles["InvoicePara"])

    invoice_cust_data = '<para spaceb=3>{0}<br/>{1}<br/>'.\
        format(customer.code, customer.name)
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
        invoice_cust_data = invoice_cust_data + customer.address.phone\
            + '<br/>'

    invoice_cust_data = invoice_cust_data + '</para>'

    invoice_cust_para = Paragraph(invoice_cust_data,
                                  styles["InvoicePara"])
    invoice_header_data = [[invoice_cust_para, '', invoice_bill_para]]
    invoice_header_table = Table(invoice_header_data, colWidths=(200, 200, 200))
    invoice_header_table.setStyle(TableStyle(
        [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
         ('LEFTPADDING', (0, 0), (-1, -1), 3),
         ('VALIGN', (0, 0), (1, 0), 'MIDDLE')]))

    return invoice_header_table


def get_bill_account_summary_table(billing,
                                   total_amount):
    account_summary_data = [
        ['Previous Balance',
         'Payments Received',
         'Adjustments (Dr)',
         'Adjustments (Cr)',
         'Current Billing',
         'Total amount Due by Date'],
        [round(billing.balance, 2),
         round(billing.received, 2),
         round(billing.adjustment, 2),
         round(billing.adjustment_cr, 2),
         round(billing.total_payable_charge, 2),
         round(total_amount, 2)]]

    account_summary_table = Table(account_summary_data,
            colWidths=(70, 80, 70, 70, 60, 100))
    account_summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))

    return account_summary_table


def get_bill_soc_table_left(billing):

    soc_table_data = [
        ['Freight', round(billing.freight_charge, 2)],
        ['Fuel Surcharge', round(billing.fuel_surcharge, 2)],
        ['Special Delivery Location', round(billing.sdl_charge, 2)],
        ['COD applied', round(billing.cod_applied_charge, 2)],
        ['COD reversed', round(billing.cod_subtract_charge, 2)],
        ['Valuable Cargo Handling Charge',
         round(billing.valuable_cargo_handling_charge, 2)]]
    soc_table_left = Table(soc_table_data, colWidths=(150, 50))
    soc_table_left.setStyle(TableStyle([
        ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ]))
    return soc_table_left


def get_bill_soc_table_right(billing):

    soc_table_data = [
        ['Amount Before Tax', round(billing.total_charge_pretax, 2)],
        ['Service Tax', round(billing.service_tax, 2)],
        ['Education Cess', round(billing.education_secondary_tax, 2)],
        ['HSE Cess', round(billing.cess_higher_secondary_tax, 2)],
        ['Total', round(billing.total_payable_charge, 2)]]
    soc_table_right = Table(soc_table_data, colWidths=(150, 50))
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
        <para spaceb=3>
        Important Information:<br/>
    	1. This is a computerised generated Invoice and does not require
        any official signature.  Kindly notify us immediately in case of
        any discrepancy in the Invoice.<br/>
    	2. Delay in payments shall attract Interest @ 2% per month.<br/>
	    3. The average Brent Crude Oil price per barrel in the previous
        month was $110.<br/>
        </para>'''

    return Paragraph(imp_info_data, styles["ImpPara"])


def get_cust_code_summary_table(billing_subcustomer, billing):
    print '4.3.8.1 customer summery table'
    cust_code_table_headers = [
            'Sr.',
            'Sub Customer Code',
            'Customer Name',
            'No of Ships',
            'Freight',
            'FuelSC',
            'SDL',
            'COD Applied',
            'COD Subtract',
            'VCHC',
            'Total']

    def get_subcustomer_code(customer):
        print '4.3.8.2 getting subcustomer --',customer.subcustomer
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
            sbilling.sdl_charge
        return round(total_sbilling, 2)

    cust_code_table_data = [
        [index,
         get_subcustomer_code(customer),
         truncate(customer.subcustomer.name),
         customer.shipments.count(),
         round(customer.freight_charge, 2),
         round(customer.fuel_surcharge, 2),
         round(customer.sdl_charge, 2),
         round(customer.cod_applied_charge, 2),
         round(customer.cod_subtract_charge, 2),
         round(customer.valuable_cargo_handling_charge, 2),
         make_bold_right(get_total(customer))]
        for index, customer in enumerate(billing_subcustomer, start=1)]

    cust_code_table_total = ['',
            '',
            'Total',
            billing.shipments.count(),
            round(billing.freight_charge, 2),
            round(billing.fuel_surcharge, 2),
            round(billing.sdl_charge, 2),
            round(billing.cod_applied_charge, 2),
            round(billing.cod_subtract_charge, 2),
            round(billing.valuable_cargo_handling_charge, 2),
            round(billing.total_charge_pretax, 2)]

    cust_code_table_total = [make_bold_right(val) for val in cust_code_table_total]

    cust_code_table_data.insert(0, cust_code_table_headers)
    cust_code_table_data.append(cust_code_table_total)
    cust_code_table = Table(cust_code_table_data,
            splitByRow=True,
            repeatRows=1,
            colWidths=(20, 70, 100, 40, 50, 50, 40, 50, 50, 50, 50))

    cust_code_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (0, -2), 'RIGHT'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (1, 1), (2, -2), 'LEFT'),
        #('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
        ('FONTSIZE',(0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.6, 0.6, 0.6)),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.8, 0.8, 0.8)),
        ('INNERGRID', (0,0), (-1, -1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))

    return cust_code_table


def generate_bill_details(bill_data):
    print '4.3.1 inside generating bill details pdf...'
    customer_id = bill_data['customer'].pk
    billing = bill_data['billing']
    billing_date = billing.billing_date.strftime('%Y_%m_%d')
    print '4.3.2 billing is ', customer_id, billing.pk
    month = billing.billing_date.strftime('%m')
    file_name = '%s/bill_wise_%s_%s_%s.pdf' % (
        str(month), str(customer_id), str(billing.pk), str(billing_date))

    full_file_name = os.path.join(pdf_home, file_name)
    doc = SimpleDocTemplate(full_file_name, pagesize=A4)
    print '4.3.3 pdf doc generated ',file_name
    # container for the 'Flowable' objects
    elements = []

    # header
    header_table = get_bill_header()
    elements.append(header_table)
    elements.append(Spacer(1, 12))

    # invoice heading
    invoice = Paragraph('<b>INVOICE</b>', styles["InvoiceHead"])
    elements.append(invoice)
    elements.append(Spacer(1, 12))

    # invoice head - customer and billing details
    print '4.3.4 invoice head - customer and billing details'
    invoice_header_table = get_bill_invoice_table(
        bill_data['customer'],
        bill_data['billing'],
        bill_data['total_amount'],
        bill_data['due_date']
    )
    print '4.3.4 invoice head - table ', invoice_header_table
    elements.append(invoice_header_table)
    elements.append(Spacer(1, 12))

    # account summary section
    print '4.3.5 account summary section'
    account_summary_header = Table([['Account Summary']], colWidths=(450))
    account_summary_header.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0 ,0), (-1, -1), 0.25, colors.black),
        ]))
    elements.append(account_summary_header)

    print '4.3.6 get account summary table'
    account_summary_table = get_bill_account_summary_table(
        bill_data['billing'],
        bill_data['total_amount'])
    print '\n4.3.6.0 get account summary table  '

    elements.append(account_summary_table)
    elements.append(Spacer(1, 40))

    # summary of charges section
    soc_heading = Paragraph('<font size=8><b>Summary Of Charges<b></font>', styles["LJustify"])
    elements.append(soc_heading)
    elements.append(Spacer(1, 12))

    soc_table_left = get_bill_soc_table_left(bill_data['billing'])
    print '\n4.3.7 soc table left  ', soc_table_left
    #elements.append(soc_table_left)
    #elements.append(Spacer(1, 12))

    soc_table_right = get_bill_soc_table_right(bill_data['billing'])
    print '\n4.3.8 soc table right  ', soc_table_right
    #elements.append(soc_table_right)
    #elements.append(Spacer(1, 40))

    soc_table = Table([[soc_table_left, '', soc_table_right]], colWidths=(250, 50, 250))
    soc_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
    elements.append(soc_table)


    # important information section
    imp_info_para = get_bill_important_info_para()
    elements.append(imp_info_para)
    elements.append(Spacer(1, 40))

    # customer code airwaybill section
    cust_code_header = Table([[Paragraph(
        '<b>Customer Code/Sub-Code wise Summary</b>',
        styles["CustCodeHead"])]],
        colWidths=(570))
    cust_code_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.Color(0.4, 0.4, 0.4)),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
    elements.append(cust_code_header)

    cust_code_wise_summary_table = get_cust_code_summary_table(
        bill_data['billingsubcustomer'],
        bill_data['billing'])
    print '\n4.3.9 customer code wise summary ',cust_code_wise_summary_table
    elements.append(cust_code_wise_summary_table)
    elements.append(Spacer(1, 40))

    doc.build(elements)

    print '4.3.10 bill details pdf generated...',file_name

    return file_name


def generate_awb_excel_file(billing):
    print '\n4.6.1 generating excel file...'
    data_list = get_awb_table_data(billing.pk)
    print '\n4.6.2 awb data list received...'
    col_heads = (
        'Sl No',
        'Cust/Sub Cust Code',
        'Air Waybill No',
        'Order No',
        'Date',
        'Service',
        'Destination',
        'Weight',
        'Freight',
        'COD',
        'Others',
        'Total')
    customer_id = billing.customer.pk
    print '\n4.6.3 awb data list received...cid',customer_id
    billing_date = billing.billing_date.strftime('%Y_%m_%d')
    # add filename and set save file path
    file_name = 'awb_excel_%s_%s_%s.xlsx' % (
        str(customer_id), str(billing.pk), str(billing_date))
    path_to_save = os.path.join(pdf_home, file_name)
    #path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    print '\n4.6.4 awb data list received...bid, path to save, file name',billing.pk,path_to_save,file_name
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format()
    header_format.set_bg_color('yellow')
    header_format.set_bold()
    plain_format = workbook.add_format()

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, 12, 12) # set column width
    sheet.write(0, 2, "AirwayBill Wise Charges")
    for col,name in enumerate(col_heads):
        sheet.write(2, col, name, header_format)

    # write data to excel sheet
    print '\n4.6.5 writing data to excel file..'
    for row, data_list in enumerate(data_list, start=3):
        for col, val in enumerate(data_list):
            print '\n4.6.5.1 writing data to excel file..',str(val)
            sheet.write_string(row,col,str(val))

    workbook.close()
    print '\n4.6.6 excel file generated..',file_name
    return file_name


def generate_pdfs(code, bid):
    # preapre the data to be written to pdf
    customer = Customer.objects.get(code=code)
    print '\n4.1 generating pdfs and excel for customer ',customer.name

    billing = Billing.objects.get(id=bid)
    shipper = customer.shipper_set.all()
    billingsubcustomer = BillingSubCustomer.objects.filter(
        subcustomer__in=shipper,
        billing=billing,
        billing_date=billing.billing_date).distinct()

    print '\n4.2 -- billing -->',billing.__dict__
    print '\n4.2 -- shipper -->',shipper.count()
    download_files = []

    if billing.billing_date:
        due_date = billing.billing_date + datetime.timedelta(10)
    else:
        due_date = ""

    if not billing.balance:
        billing.balance = 0

    if not billing.total_payable_charge:
        billing.total_payable_charge = 0

    if not billing.adjustment:
        billing.adjustment = 0

    if not billing.received:
        billing.received = 0

    billing.save()

    total_amount = billing.balance +\
             billing.total_payable_charge +\
             billing.adjustment -\
             billing.received
    # write bill details to pdf
    bill_data = {'customer':customer,
         'due_date':due_date,
         'total_amount':total_amount - billing.adjustment_cr,
         'due_date':due_date,
         'billing':billing,
         'billingsubcustomer':billingsubcustomer}

    print '\n4.3 generating bill details pdf... for billing, customer ',billing.pk, customer.name
    bill_file = generate_bill_details(bill_data)
    print '\n4.4 bill pdf generated ...', bill_file
    download_files.append(bill_file)

    # write awb details to pdf
    awb_data = {'customer':customer,
         'due_date':due_date,
         'total_amount':total_amount,
         'due_date':due_date,
         'billing':billing,
         'billingsubcustomer':billingsubcustomer}

    print '\n4.5 generate awb details pdf for %s' % customer.name
    awb_file = generate_awb_details(awb_data)
    print '\n4.6 generate awb details excel for %s' % customer.name
    awb_excel_file = generate_awb_excel_file(awb_data['billing'])
    print '\n4.7 awb details excel generated ',awb_excel_file
    download_files.append(awb_file)
    download_files.append(awb_excel_file)

    print '\n4.8 pdf generation completed for %s files are %s ' %(customer.name, str(download_files))
    return download_files


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


def read_excel_file(up_file):
    book = xlrd.open_workbook(file_contents=up_file)
    work_sheet = book.sheet_by_index(0)

    # row values in excel file is assumed to be in the following order
    #    -Customer code 0
    #    -Customer Name 1
    #    -Opening Balance 2
    #    -Payment Received 3
    #    -Balance 4
    #    -Adjustments(Dr) 5
    #    -Adjustments(Cr) 6
    #    -Bill Date 7

    sheet_data = []
    for x in range(1, work_sheet.nrows):
        row_data = []
        for y in range(work_sheet.ncols):
            cell_value = work_sheet.cell_value(x, y)
            # if the data type is date then we have to convert it
            # to date format
            if y == 7 and cell_value:
                date_time = datetime.datetime(*xlrd.xldate_as_tuple(cell_value, book.datemode))
                cell_value = datetime.datetime.strftime(date_time, '%Y-%m-%d')
            row_data.append(cell_value)
        sheet_data.append(row_data)

    return sheet_data


def read_excel_n_generate_pdf(date_from, date_to, up_file):
    """
    This function read an excel file and generate bill for each customer
    in the excel file, and provide a consolidated pdf file of the bill generated
    for all customers
    """
    # read excel file
    sheet_data =  read_excel_file(up_file) # keep each row data from excel sheet
    #remove last row values. last row is total
    sheet_data = sheet_data[:-1]
    download_files = [] # keep list of files to be downloaded
    bills_list = [] # keep the list of bills generated

    print 'GENERATING BILLS...'
    customers_from_excel = [int(row[0]) for row in sheet_data]
    customers = Customer.objects.all()
    all_customers = (c.code for c in customers if c.code not in customers_from_excel)
    #all_customers = (c.code for c in customers)
    # for each row in excel file/for each customer, read the values and
    # generate bill and write to pdf file
    sheet_data = [] # temporary , remove this line
    for row in sheet_data:
        print '1. start  bill generation process for ... %s' %row[0]
        if isinstance(row[0], float) and \
                isinstance(row[2], float) and \
                isinstance(row[3], float) and \
                isinstance(row[5], float) and \
                isinstance(row[6], float) and \
                isinstance(row[7], str):
            print '2.Lets generate bill'
            billing = generate_bill(code=int(row[0]), balance=row[2],
                    payment=row[3], adjustments=row[5], adjust_cr=row[6],
                    date=row[7], date_from=date_from, date_to=date_to,
                    from_excel=True)
            if not billing:
                print 'ERROR: Billing not generated'
                continue
            print '3. bill received in excel reading for loop .'
            bills_list.append(billing.pk)
            print '4. now generate pdfs..'
            download_files.append(generate_pdfs(int(row[0]), billing.pk))
            print '5. Bill generaion and pdf generation completed for customer....\n\n'

    # generate bill for customers not in excel file
    #print 'bill for all customers..'
    for code in all_customers:
        print '1. start  bill generation process for ... %s' % code
        print '2.Lets generate bill'
        billing = generate_bill(code=code, date_from=date_from,
                date_to=date_to, from_excel=False)
        if not billing:
            print 'ERROR: Billing not generated'
            continue
        print '3. bill received in excel reading for loop .'
        bills_list.append(billing.pk)
        print '4. now generate pdfs..'
        #download_files.append(generate_pdfs(code, billing.pk))
        print '5. Bill generaion and pdf generation completed for customer....\n\n'

    print '6. pdfs generation finished.. now generate combined pdfs'
    #download_files = [pdf_home + item for sublist in download_files for item in sublist]

    # generate an aggregate pdf book containing all billwise
    # and awb wise bills
    filename = pdf_home + combined_pdf_name
    file_name = generate_combined_pdf(download_files, filename)
    #download_files.append(file_name)

    print '7. combined pdfs generated.. now send emails..'
    # email the result
    email_msg = '  '.join(download_files)
    email_msg = 'Please download the bill generation pdfs from the following links' + email_msg
    to_email = ("samar@prtouch.com", "jignesh@prtouch.com", "sravank@ecomexpress.in")
    from_email = "support@ecomexpress.in"
    send_mail("Bills Generated", email_msg, from_email, to_email)
    print '8. Email send...'
    return True

def handle_uploaded_file(f):
    path = pdf_home + 'bill.xls'
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path

def start_bill_generation_process(*args, **kwargs):
    date_from, date_to, up_file = args
    #doc = BillDocument.objects.get(id=doc_id)
    #with open(settings.MEDIA_ROOT + '/' + doc.excel_file.name, 'r') as f:
        #data = f.read()

    #path = handle_uploaded_file(up_file)
    with open(up_file, 'r') as f:
        data = f.read()
    print 'Lets generate bill now...'
    read_excel_n_generate_pdf(date_from, date_to, data)
