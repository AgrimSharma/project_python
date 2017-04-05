import calendar
import datetime
import xlrd

from django.conf import settings
from django.db.models import Count, Sum, Q

from billing.models import BillingSubCustomer, Billing, ProductBilling
from billing.models import BillingPreview, BillingQueue, CustomerBillingReport
from customer.models import Customer, Product
from service_centre.models import Shipment

from billing.generate_bill_pdf import generate_bill_summary_xls
from billing.update_billing import read_excel_n_update_billing
from billing.product_billing_update import update_productbilling
from billing.jasper_billing import generate_bill_for_jasper


def generate_bill_for_customer(code, year, month, to_date=None):
    year = int(year)
    month = int(month)

    customer = Customer.objects.get(code=code)
    cid = customer.id
    prev_month_bill = Billing.objects.filter(customer=customer)
    if prev_month_bill.only('id').exists():
        prev_month_bill = prev_month_bill.latest("billing_date")
        billing_date_from = prev_month_bill.billing_date + datetime.timedelta(days = 1)
    else:
        billing_date_from = datetime.date(year, month, 1)

    if to_date:
        to_date_arr = to_date.split("-")
        billing_date = datetime.date(int(to_date_arr[0]), int(to_date_arr[1]), int(to_date_arr[2]))
    else:
        month_range = calendar.monthrange(year, month)
        billing_date = datetime.date(year, month, month_range[1])

    if billing_date_from > billing_date:
        return (None, code)

    shipments = Shipment.objects.filter(
        shipper__id = cid,
        shipment_date__gte = billing_date_from,
        shipment_date__lte = billing_date,
        ).exclude(billing__isnull = False)

    if not shipments.exists():
        return (None, code)


    freight_data = shipments.aggregate(
        Count('id'),
        total_chargeable_weight = Sum('chargeable_weight'),
        op_freight = Sum('order_price__freight_charge'),
        op_sdl = Sum('order_price__sdl_charge'),
        op_fuel = Sum('order_price__fuel_surcharge'),
        op_rto_price = Sum('order_price__rto_charge'),
        op_sdd_charge = Sum('order_price__sdd_charge'),
        op_reverse_charge = Sum('order_price__reverse_charge'),
        op_valuable_cargo_handling_charge = Sum('order_price__valuable_cargo_handling_charge'),
        #op_tab_charge = Sum('order_price__tab_charge'),
        op_to_pay = Sum('order_price__to_pay_charge'))

    cod_charges = shipments.exclude(rts_status = 1).\
        aggregate(cod_charge = Sum('codcharge__cod_charge'))

    cod_charges_negative = shipments.filter(rts_status = 1).\
        aggregate(cod_charge = Sum('codcharge__cod_charge'))

    if not cod_charges["cod_charge"]:
        cod_charges["cod_charge"] = 0

    if not cod_charges_negative["cod_charge"]:
        cod_charges_negative["cod_charge"] = 0
    today = datetime.datetime.now()
    billing = Billing(
        customer_id = cid,
        bill_generation_date=today,
        freight_charge = freight_data["op_freight"],
        sdl_charge = freight_data["op_sdl"],
        fuel_surcharge = freight_data["op_fuel"],
        valuable_cargo_handling_charge = freight_data["op_valuable_cargo_handling_charge"],
        to_pay_charge = freight_data["op_to_pay"],
        rto_charge = freight_data["op_rto_price"],
        sdd_charge = freight_data["op_sdd_charge"],
        reverse_charge = freight_data["op_reverse_charge"],
        #tab_charge  =  freight_data["op_tab_charge"],
        cod_applied_charge = cod_charges["cod_charge"],
        cod_subtract_charge = cod_charges_negative["cod_charge"],
        total_cod_charge = cod_charges["cod_charge"] - cod_charges_negative["cod_charge"],
        billing_date = billing_date,
        billing_date_from = billing_date_from,
        shipment_count = freight_data["id__count"],
        total_chargeable_weight = freight_data['total_chargeable_weight'])

    billing.total_charge_pretax = freight_data["op_freight"]+\
        freight_data["op_sdl"]+\
        freight_data["op_fuel"]+\
        freight_data["op_valuable_cargo_handling_charge"]+\
        freight_data["op_to_pay"]+\
        freight_data["op_rto_price"]+\
        freight_data["op_sdd_charge"]+\
        freight_data["op_reverse_charge"]+\
        cod_charges["cod_charge"]-\
        cod_charges_negative["cod_charge"]

    billing.service_tax = billing.total_charge_pretax * 0.12
    billing.education_secondary_tax =  billing.service_tax * 0.02
    billing.cess_higher_secondary_tax =  billing.service_tax * 0.01
    billing.total_payable_charge = billing.total_charge_pretax + \
        billing.service_tax + \
        billing.education_secondary_tax + \
        billing.cess_higher_secondary_tax
    billing.generation_status = 1
    billing.save()

    billing.shipments.add(*(list(shipments)))

    shipments.update(billing = billing)
    shipments = billing.shipments.all()

    freight_data = shipments.values("pickup__subcustomer_code__id").\
            annotate(
                Count('id'),
                total_cw = Sum('chargeable_weight'),
                op_freight = Sum('order_price__freight_charge'),
                op_sdl = Sum('order_price__sdl_charge'),
                op_fuel = Sum('order_price__fuel_surcharge'),
                op_rto_price = Sum('order_price__rto_charge'),
                op_sdd_charge = Sum('order_price__sdd_charge'),
                op_reverse_charge = Sum('order_price__reverse_charge'),
                op_valuable_cargo_handling_charge = Sum('order_price__valuable_cargo_handling_charge'),
                #op_tab_charge = Sum('order_price__tab_charge'),
                op_to_pay = Sum('order_price__to_pay_charge'))


    cod_charges = dict(shipments.exclude(rts_status = 1).values("pickup__subcustomer_code__id").\
        annotate(cod_charge=Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code__id', 'cod_charge'))

    cod_charges_negative = dict(shipments.filter(rts_status = 1).\
            values("pickup__subcustomer_code__id").\
            annotate(cod_charge = Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code__id', 'cod_charge'))

    cod_charge = 0
    cod_charge_negative = 0
    for fd in freight_data:
        subsc_id = fd["pickup__subcustomer_code__id"]
        # get the cod charge for the subcustomer
        cod_charge = cod_charges.get(subsc_id)
        cod_charge = cod_charge if cod_charge else 0

        # get the negative cod charge for the subcustomer
        cod_charge_negative = cod_charges_negative.get(subsc_id)
        cod_charge_negative = cod_charge_negative if cod_charge_negative else 0

        sbilling = BillingSubCustomer(
            subcustomer_id=subsc_id,
            freight_charge=fd["op_freight"],
            sdl_charge=fd["op_sdl"],
            fuel_surcharge=fd["op_fuel"],
            valuable_cargo_handling_charge=fd["op_valuable_cargo_handling_charge"],
            to_pay_charge=fd["op_to_pay"],
            rto_charge=fd["op_rto_price"],
            sdd_charge=fd["op_sdd_charge"],
            reverse_charge=fd["op_reverse_charge"],
            total_chargeable_weight=fd["total_cw"],
            #tab_charge = fd["op_tab_charge"],
            cod_applied_charge=cod_charge,
            cod_subtract_charge=cod_charge_negative,
            total_cod_charge=cod_charge - cod_charge_negative,
            billing_date=billing_date,
            billing_date_from=billing_date_from,
            shipment_count=fd["id__count"],
            billing_id=billing.id)

        sbilling.total_charge = sbilling.freight_charge +\
            sbilling.sdl_charge +\
            sbilling.fuel_surcharge +\
            sbilling.valuable_cargo_handling_charge +\
            sbilling.to_pay_charge +\
            sbilling.rto_charge +\
            sbilling.sdd_charge +\
            sbilling.reverse_charge +\
            sbilling.cod_applied_charge -\
            sbilling.cod_subtract_charge
        sbilling.generation_status = 1
        sbilling.save()

        sub_shipments = shipments.filter(pickup__subcustomer_code__id=subsc_id)
        sbilling.shipments.add(*(list(sub_shipments)))
        sub_shipments.update(sbilling=sbilling)

    return (billing.id, code)

def generate_customer_bill(billing_from, billing_to, customer):

    cid = customer.id

    if billing_from > billing_to:
        return None

    shipments = Shipment.objects.filter(
        shipper__id = cid, shipment_date__range=(billing_from, billing_to), 
        billing=None)

    if not shipments.exists():
        return None


    freight_data = shipments.aggregate(
        Count('id'),
        total_chargeable_weight = Sum('chargeable_weight'),
        op_freight = Sum('order_price__freight_charge'),
        op_sdl = Sum('order_price__sdl_charge'),
        op_fuel = Sum('order_price__fuel_surcharge'),
        op_rto_price = Sum('order_price__rto_charge'),
        op_sdd_charge = Sum('order_price__sdd_charge'),
        op_reverse_charge = Sum('order_price__reverse_charge'),
        op_valuable_cargo_handling_charge = Sum('order_price__valuable_cargo_handling_charge'),
        #op_tab_charge = Sum('order_price__tab_charge'),
        op_to_pay = Sum('order_price__to_pay_charge'))

    cod_charges = shipments.exclude(rts_status = 1).\
        aggregate(cod_charge = Sum('codcharge__cod_charge'))

    cod_charges_negative = shipments.filter(rts_status = 1).\
        aggregate(cod_charge = Sum('codcharge__cod_charge'))

    if not cod_charges["cod_charge"]:
        cod_charges["cod_charge"] = 0

    if not cod_charges_negative["cod_charge"]:
        cod_charges_negative["cod_charge"] = 0
    today = datetime.datetime.now()

    billing = Billing(
        customer_id = cid,
        bill_generation_date=today,
        freight_charge = freight_data["op_freight"],
        sdl_charge = freight_data["op_sdl"],
        fuel_surcharge = freight_data["op_fuel"],
        valuable_cargo_handling_charge = freight_data["op_valuable_cargo_handling_charge"],
        to_pay_charge = freight_data["op_to_pay"],
        rto_charge = freight_data["op_rto_price"],
        sdd_charge = freight_data["op_sdd_charge"],
        reverse_charge = freight_data["op_reverse_charge"],
        #tab_charge  =  freight_data["op_tab_charge"],
        cod_applied_charge = cod_charges["cod_charge"],
        cod_subtract_charge = cod_charges_negative["cod_charge"],
        total_cod_charge = cod_charges["cod_charge"] - cod_charges_negative["cod_charge"],
        billing_date = billing_date,
        billing_date_from = billing_date_from,
        shipment_count = freight_data["id__count"],
        total_chargeable_weight = freight_data['total_chargeable_weight'])

    billing.total_charge_pretax = freight_data["op_freight"]+\
        freight_data["op_sdl"]+\
        freight_data["op_fuel"]+\
        freight_data["op_valuable_cargo_handling_charge"]+\
        freight_data["op_to_pay"]+\
        freight_data["op_rto_price"]+\
        freight_data["op_sdd_charge"]+\
        freight_data["op_reverse_charge"]+\
        cod_charges["cod_charge"]-\
        cod_charges_negative["cod_charge"]

    billing.service_tax = billing.total_charge_pretax * 0.12
    billing.education_secondary_tax =  billing.service_tax * 0.02
    billing.cess_higher_secondary_tax =  billing.service_tax * 0.01
    billing.total_payable_charge = billing.total_charge_pretax + \
        billing.service_tax + \
        billing.education_secondary_tax + \
        billing.cess_higher_secondary_tax
    billing.generation_status = 1
    billing.save()

    billing.shipments.add(*(list(shipments)))

    shipments.update(billing = billing)
    shipments = billing.shipments.all()

    freight_data = shipments.values("pickup__subcustomer_code__id").\
            annotate(
                Count('id'),
                total_cw = Sum('chargeable_weight'),
                op_freight = Sum('order_price__freight_charge'),
                op_sdl = Sum('order_price__sdl_charge'),
                op_fuel = Sum('order_price__fuel_surcharge'),
                op_rto_price = Sum('order_price__rto_charge'),
                op_sdd_charge = Sum('order_price__sdd_charge'),
                op_reverse_charge = Sum('order_price__reverse_charge'),
                op_valuable_cargo_handling_charge = Sum('order_price__valuable_cargo_handling_charge'),
                #op_tab_charge = Sum('order_price__tab_charge'),
                op_to_pay = Sum('order_price__to_pay_charge'))


    cod_charges = dict(shipments.exclude(rts_status = 1).values("pickup__subcustomer_code__id").\
        annotate(cod_charge=Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code__id', 'cod_charge'))

    cod_charges_negative = dict(shipments.filter(rts_status = 1).\
            values("pickup__subcustomer_code__id").\
            annotate(cod_charge = Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code__id', 'cod_charge'))

    cod_charge = 0
    cod_charge_negative = 0
    for fd in freight_data:
        subsc_id = fd["pickup__subcustomer_code__id"]
        # get the cod charge for the subcustomer
        cod_charge = cod_charges.get(subsc_id)
        cod_charge = cod_charge if cod_charge else 0

        # get the negative cod charge for the subcustomer
        cod_charge_negative = cod_charges_negative.get(subsc_id)
        cod_charge_negative = cod_charge_negative if cod_charge_negative else 0

        sbilling = BillingSubCustomer(
            subcustomer_id=subsc_id,
            freight_charge=fd["op_freight"],
            sdl_charge=fd["op_sdl"],
            fuel_surcharge=fd["op_fuel"],
            valuable_cargo_handling_charge=fd["op_valuable_cargo_handling_charge"],
            to_pay_charge=fd["op_to_pay"],
            rto_charge=fd["op_rto_price"],
            sdd_charge=fd["op_sdd_charge"],
            reverse_charge=fd["op_reverse_charge"],
            total_chargeable_weight=fd["total_cw"],
            #tab_charge = fd["op_tab_charge"],
            cod_applied_charge=cod_charge,
            cod_subtract_charge=cod_charge_negative,
            total_cod_charge=cod_charge - cod_charge_negative,
            billing_date=billing_date,
            billing_date_from=billing_date_from,
            shipment_count=fd["id__count"],
            billing_id=billing.id)

        sbilling.total_charge = sbilling.freight_charge +\
            sbilling.sdl_charge +\
            sbilling.fuel_surcharge +\
            sbilling.valuable_cargo_handling_charge +\
            sbilling.to_pay_charge +\
            sbilling.rto_charge +\
            sbilling.sdd_charge +\
            sbilling.reverse_charge +\
            sbilling.cod_applied_charge -\
            sbilling.cod_subtract_charge
        sbilling.generation_status = 1
        sbilling.save()

        sub_shipments = shipments.filter(pickup__subcustomer_code__id=subsc_id)
        sbilling.shipments.add(*(list(sub_shipments)))
        sub_shipments.update(sbilling=sbilling)

    update_productbilling(billing.id)
    return billing


def update_customer_reports(queue):
    reports = [
        CustomerBillingReport(billqueue=queue, customer=bill.customer, billing=bill) 
        for bill in queue.bills]
    CustomerBillingReport.objects.bulk_create(reports)

def do_billing(queue_id, *args, **kwargs):
    try:
        queue = BillingQueue.objects.get(id=queue_id)
    except BillingQueue.DoesNotExist:
        return None

    billing_from = queue.billing_from
    billing_to = queue.billing_to

    customers = Customer.objects.exclude(id=6).values_list('id', flat=True)

    for customer in customers:
        billing = generate_customer_bill(
            billing_from=billing_from, 
            billing_to=billing_to, customer=customer)
        if billing:
            queue.bills.add(billing)

    # following 2 lines are for jasper.
    fwb_bill, rev_bill = generate_bill_for_jasper(billing_from, billing_to)
    queue.bills.add(fwb_bill)
    queue.bills.add(rev_bill)
    
    # update Bill file that naresh provides
    read_excel_n_update_billing(year, month)

    # update customer billing reports queue
    update_customer_reports(queue)

    return True


def process_billqueue():
    queue = BillingQueue.objects.filter(status=0) 
    for q in queue:
        BillingQueue.objects.filter(id=q.id).update(status=1)
        done = do_billing(q.id)
        if done:
            BillingQueue.objects.filter(id=q.id).update(status=2)
    return True
