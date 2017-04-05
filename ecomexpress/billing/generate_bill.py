import calendar
import datetime
import xlrd

from django.conf import settings
from django.db.models import Count, Sum, Q

from billing.models import BillingSubCustomer, Billing, ProductBilling, Taxes
from billing.models import BillingPreview, BillingQueue, CustomerBillingReport
from customer.models import Customer, Product
from service_centre.models import Shipment

from billing.generate_bill_pdf import generate_bill_summary_xls
from billing.update_billing import read_excel_n_update_billing
from billing.product_billing_update import update_productbilling
from billing.jasper_billing import normal_reverse_billing


def get_sum(*args):
    return sum([x for x in args if x])

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


    freight_data = dict(shipments.aggregate(
        Count('id'),
        total_chargeable_weight = Sum('chargeable_weight'),
        op_freight = Sum('order_price__freight_charge'),
        op_sdl = Sum('order_price__sdl_charge'),
        op_fuel = Sum('order_price__fuel_surcharge'),
        op_rto_price = Sum('order_price__rto_charge'),
        op_sdd_charge = Sum('order_price__sdd_charge'),
        op_reverse_charge = Sum('order_price__reverse_charge'),
        op_valuable_cargo_handling_charge = Sum('order_price__valuable_cargo_handling_charge'),
        op_to_pay = Sum('order_price__to_pay_charge')))

    cod_charges = dict(shipments.exclude(rts_status = 1).\
        aggregate(cod_charge = Sum('codcharge__cod_charge')))

    cod_charges_negative = dict(shipments.filter(rts_status = 1).\
        aggregate(cod_charge = Sum('codcharge__cod_charge')))

    if not cod_charges["cod_charge"]:
        cod_charges["cod_charge"] = 0

    if not cod_charges_negative["cod_charge"]:
        cod_charges_negative["cod_charge"] = 0
    today = datetime.datetime.now()

    total_charge_pretax = get_sum(
        freight_data["op_freight"], freight_data["op_sdl"],
        freight_data["op_fuel"], freight_data["op_valuable_cargo_handling_charge"],
        freight_data["op_to_pay"], freight_data["op_rto_price"],
        freight_data["op_sdd_charge"], freight_data["op_reverse_charge"],
        cod_charges["cod_charge"]) - cod_charges_negative["cod_charge"]

    tax  = Taxes.objects.filter(effective_date__lte=billing_date).latest('id')
    service_tax_rate = float(tax.service_tax)
    #service_tax = total_charge_pretax * 0.12
    #education_secondary_tax =  service_tax * 0.02
    #cess_higher_secondary_tax =  service_tax * 0.01
    service_tax = total_charge_pretax * service_tax_rate
    education_secondary_tax =  0
    cess_higher_secondary_tax = 0
    total_payable_charge = get_sum(total_charge_pretax, service_tax, education_secondary_tax, cess_higher_secondary_tax)

    billing = Billing.objects.create(
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
        cod_applied_charge = cod_charges["cod_charge"],
        cod_subtract_charge = cod_charges_negative["cod_charge"],
        total_cod_charge = cod_charges["cod_charge"] - cod_charges_negative["cod_charge"],
        billing_date = billing_date,
        billing_date_from = billing_date_from,
        shipment_count = freight_data["id__count"],
        total_chargeable_weight=freight_data['total_chargeable_weight'],
        total_charge_pretax=total_charge_pretax,
        service_tax=service_tax,
        education_secondary_tax=education_secondary_tax,
        cess_higher_secondary_tax=cess_higher_secondary_tax,
        total_payable_charge=total_payable_charge,
        generation_status=1)

    billing.shipments.add(*(list(shipments)))
    shipments.update(billing=billing)
    shipments = billing.shipments.all()

    freight_data = list(shipments.values("pickup__subcustomer_code_id").\
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
                op_to_pay = Sum('order_price__to_pay_charge')))

    cod_charges = dict(shipments.exclude(rts_status = 1).values("pickup__subcustomer_code_id").\
        annotate(cod_charge=Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code_id', 'cod_charge'))

    cod_charges_negative = dict(shipments.filter(rts_status = 1).\
            values("pickup__subcustomer_code_id").\
            annotate(cod_charge = Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code_id', 'cod_charge'))

    cod_charge = 0
    cod_charge_negative = 0
    for fd in freight_data:
        subsc_id = fd["pickup__subcustomer_code_id"]
        # get the cod charge for the subcustomer
        cod_charge = cod_charges.get(subsc_id)
        cod_charge = cod_charge if cod_charge else 0

        # get the negative cod charge for the subcustomer
        cod_charge_negative = cod_charges_negative.get(subsc_id)
        cod_charge_negative = cod_charge_negative if cod_charge_negative else 0

        total_charge = get_sum(
            fd["op_freight"], fd["op_sdl"],
            fd["op_fuel"], fd["op_valuable_cargo_handling_charge"],
            fd["op_to_pay"], fd["op_rto_price"],
            fd["op_sdd_charge"], fd["op_reverse_charge"], cod_charge
        ) - cod_charge_negative

        sbilling = BillingSubCustomer.objects.create(
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
            cod_applied_charge=cod_charge,
            cod_subtract_charge=cod_charge_negative,
            total_cod_charge=cod_charge - cod_charge_negative,
            billing_date=billing_date,
            billing_date_from=billing_date_from,
            shipment_count=fd["id__count"],
            total_charge=total_charge,
            generation_status=1,
            billing_id=billing.id)

        #sub_shipments = shipments.filter(pickup__subcustomer_code_id=subsc_id)
        #sbilling.shipments.add(*(list(sub_shipments)))
        #sub_shipments.update(sbilling=sbilling)

    return (billing.id, code)

def generate_customer_bill(billing_from, billing_to, customer):
    cid = customer.id

    if billing_from > billing_to:
        return None

    shipments = Shipment.objects.filter(
        shipper__id=cid, shipment_date__range=(billing_from, billing_to), 
        billing=None)

    if not shipments.exists():
        print 'no shipments to bill'
        return None

    freight_data = dict(shipments.aggregate(
        Count('id'),
        total_chargeable_weight = Sum('chargeable_weight'),
        op_freight = Sum('order_price__freight_charge'),
        op_sdl = Sum('order_price__sdl_charge'),
        op_fuel = Sum('order_price__fuel_surcharge'),
        op_rto_price = Sum('order_price__rto_charge'),
        op_sdd_charge = Sum('order_price__sdd_charge'),
        op_reverse_charge = Sum('order_price__reverse_charge'),
        op_valuable_cargo_handling_charge = Sum('order_price__valuable_cargo_handling_charge'),
        op_to_pay = Sum('order_price__to_pay_charge')))

    cod_charges = dict(shipments.exclude(rts_status = 1).aggregate(cod_charge = Sum('codcharge__cod_charge')))
    cod_charges_negative = dict(shipments.filter(rts_status = 1).aggregate(cod_charge = Sum('codcharge__cod_charge')))

    if not cod_charges["cod_charge"]:
        cod_charges["cod_charge"] = 0

    if not cod_charges_negative["cod_charge"]:
        cod_charges_negative["cod_charge"] = 0
    today = datetime.datetime.now()

    cod_plus = cod_charges["cod_charge"]
    cod_neg = cod_charges_negative["cod_charge"]
    cod_plus = cod_plus if cod_plus else 0
    cod_neg = cod_neg if cod_neg else 0
    cod_total = cod_plus - cod_neg

    total_charge_pretax = get_sum(
        freight_data["op_freight"], freight_data["op_sdl"],
        freight_data["op_fuel"], freight_data["op_valuable_cargo_handling_charge"],
        freight_data["op_to_pay"], freight_data["op_rto_price"],
        freight_data["op_sdd_charge"], freight_data["op_reverse_charge"], cod_total) 

    tax  = Taxes.objects.filter(effective_date__lte=billing_to).latest('id')
    service_tax_rate = float(tax.service_tax)
    #service_tax = total_charge_pretax * 0.12
    #education_secondary_tax =  service_tax * 0.02
    #cess_higher_secondary_tax =  service_tax * 0.01
    service_tax = total_charge_pretax * service_tax_rate
    education_secondary_tax =  0
    cess_higher_secondary_tax = 0
    total_payable_charge = get_sum(
        total_charge_pretax, service_tax, education_secondary_tax, 
        cess_higher_secondary_tax)

    billing = Billing.objects.create(
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
        cod_applied_charge = cod_plus,
        cod_subtract_charge = cod_neg,
        total_cod_charge = cod_total,
        billing_date = billing_to,
        billing_date_from = billing_from,
        shipment_count = freight_data["id__count"],
        total_chargeable_weight = freight_data['total_chargeable_weight'],
        total_charge_pretax=total_charge_pretax,
        service_tax=service_tax,
        education_secondary_tax=education_secondary_tax,
        cess_higher_secondary_tax=cess_higher_secondary_tax,
        total_payable_charge=total_payable_charge,
        generation_status=1)

    billing.shipments.add(*(list(shipments)))
    shipments.update(billing = billing)
    #shipments = billing.shipments.all()

    shipments = Shipment.objects.filter(
        shipper__id=cid, shipment_date__range=(billing_from, billing_to), 
        billing_id=billing.id)
    print 'shipments count {0}  {1}'.format(billing.id, shipments.count())

    freight_data = list(shipments.values("pickup__subcustomer_code_id").\
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
                op_to_pay = Sum('order_price__to_pay_charge')))

    cod_charges = dict(shipments.exclude(rts_status = 1).values("pickup__subcustomer_code_id").\
        annotate(cod_charge=Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code_id', 'cod_charge'))

    cod_charges_negative = dict(shipments.filter(rts_status = 1).\
            values("pickup__subcustomer_code_id").\
            annotate(cod_charge = Sum('codcharge__cod_charge')).values_list('pickup__subcustomer_code_id', 'cod_charge'))

    cod_charge = 0
    cod_charge_negative = 0
    for fd in freight_data:
        subsc_id = fd["pickup__subcustomer_code_id"]
        # get the cod charge for the subcustomer
        cod_charge = cod_charges.get(subsc_id)
        cod_charge = cod_charge if cod_charge else 0

        # get the negative cod charge for the subcustomer
        cod_charge_negative = cod_charges_negative.get(subsc_id)
        cod_charge_negative = cod_charge_negative if cod_charge_negative else 0
        cod_total = cod_charge - cod_charge_negative 

        total_charge = get_sum(
            fd["op_freight"], fd["op_sdl"],
            fd["op_fuel"], fd["op_valuable_cargo_handling_charge"],
            fd["op_to_pay"], fd["op_rto_price"],
            fd["op_sdd_charge"], fd["op_reverse_charge"], cod_total)

        sbilling = BillingSubCustomer.objects.create(
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
            cod_applied_charge=cod_charge,
            cod_subtract_charge=cod_charge_negative,
            total_cod_charge=cod_total,
            billing_date=billing_to,
            billing_date_from=billing_from,
            shipment_count=fd["id__count"],
            total_charge=total_charge, 
            generation_status=1,
            billing_id=billing.id)

        #sub_shipments = shipments.filter(pickup__subcustomer_code_id=subsc_id)
        #sbilling.shipments.add(*(list(sub_shipments)))
        #sub_shipments.update(sbilling=sbilling)

    update_productbilling(billing.id)
    return billing


def update_customer_reports(queue):
    reports = []
    for bill in queue.bills.all():
        try:
            CustomerBillingReport.objects.get(billqueue=queue, customer=bill.customer, billing=bill) 
        except CustomerBillingReport.DoesNotExist:
            reports.append(CustomerBillingReport(billqueue=queue, customer=bill.customer, billing=bill))
    CustomerBillingReport.objects.bulk_create(reports)
    return True

def do_billing(queue_id, *args, **kwargs):
    print 'start processing queue'
    queue = BillingQueue.objects.get(id=queue_id)

    billing_from = queue.billing_from
    billing_to = queue.billing_to
    customers = Customer.objects.exclude(id__in=[6, 12, 149])
    customers = []

    for customer in customers:
        print 'processing customer :', customer, billing_from, billing_to
        billing = generate_customer_bill(
            billing_from=billing_from, 
            billing_to=billing_to, customer=customer)
        if billing:
            print 'billing object :', billing.id
            queue.bills.add(billing)

    # following 2 lines are for normal, reverse separate billing
    print 'start jasper billing'
    fwb_bill, rev_bill = normal_reverse_billing(billing_from, billing_to, 6)
    if fwb_bill: queue.bills.add(fwb_bill)
    if rev_bill: queue.bills.add(rev_bill)
    print 'creating reverse bill / fwd bill for 149'
    fwb_bill, rev_bill = normal_reverse_billing(billing_from, billing_to, 149)
    if fwb_bill: queue.bills.add(fwb_bill)
    if rev_bill: queue.bills.add(rev_bill)
    print 'all billing done.. updating data from bill outstanding file..'
    # update Bill file that naresh provides
    read_excel_n_update_billing(billing_from.year, billing_from.month)

    # update customer billing reports queue
    update_customer_reports(queue)

    return True


def process_billqueue():
    queue = BillingQueue.objects.filter(status=0) 
    for q in queue:
        print 'processing queue ', q.id
        BillingQueue.objects.filter(id=q.id).update(status=1)
        done = do_billing(q.id)
        if done:
            print 'billing done'
            BillingQueue.objects.filter(id=q.id).update(status=2)
    return True
