import calendar
import datetime

from django.db.models import Count, Sum

from service_centre.models import *
from billing.models import BillingSubCustomer, Billing, Taxes
from billing.product_billing_update import update_productbilling
from customer.models import Customer


# bill_type : 0 - reverse pickups, 1 - forward shipments
def generate_bill(billing_from, billing_to, bill_type=0, shipper_id=6):
    customer = Customer.objects.get(id=shipper_id)
    cid = customer.id

    if isinstance(billing_from, datetime.date):
        billing_date_from = billing_from
    else:
        billing_date_from = datetime.datetime.strptime(billing_from, '%Y-%m-%d').date()

    if isinstance(billing_to, datetime.date):
        billing_date = billing_to
    else:
        billing_date = datetime.datetime.strptime(billing_to, '%Y-%m-%d').date()
    #print 'get shipments'
    if bill_type == 0:
        # reverse shipments
        shipments = Shipment.objects.filter(
            shipper__id = shipper_id,
            shipment_date__gte = billing_date_from,
            shipment_date__lte = billing_date,
            reverse_pickup=True
        ).exclude(billing__isnull = False)
    else:
        shipments = Shipment.objects.filter(
            shipper__id = shipper_id,
            shipment_date__gte = billing_date_from,
            shipment_date__lte = billing_date,
        ).exclude(billing__isnull = False).exclude(reverse_pickup=True)

    if not shipments:
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

    #print cod_charges, cod_charges_negative
    #print '*'*30
    if not cod_charges["cod_charge"]:
        cod_charge = 0
    else:
        cod_charge = cod_charges["cod_charge"]

    if not cod_charges_negative["cod_charge"]:
        cod_negative = 0
    else:
        cod_negative = cod_charges_negative["cod_charge"]
   
    #print cod_charges, cod_charges_negative

    today = datetime.datetime.now()
    billing = Billing(
        customer=customer,
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
        total_cod_charge = cod_charge - cod_negative,
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
        cod_charge - cod_negative

    tax  = Taxes.objects.filter(effective_date__lte=billing_date).latest('id')
    service_tax_rate = float(tax.service_tax)
    billing.service_tax = billing.total_charge_pretax * service_tax_rate
    billing.education_secondary_tax =  0
    billing.cess_higher_secondary_tax = 0

    #billing.service_tax = billing.total_charge_pretax * 0.12
    #billing.education_secondary_tax =  billing.service_tax * 0.02
    #billing.cess_higher_secondary_tax =  billing.service_tax * 0.01
    billing.total_payable_charge = billing.total_charge_pretax + \
        billing.service_tax + \
        billing.education_secondary_tax + \
        billing.cess_higher_secondary_tax
    billing.generation_status = 1
    billing.save()

    billing.shipments.add(*(list(shipments)))
    shipments.update(billing=billing)

    #shipments = billing.shipments.all()
    shipments = Shipment.objects.filter(
        shipper__id=cid, shipment_date__range=(billing_from, billing_to), 
        billing_id=billing.id)
    print 'shipments count {0}  {1}'.format(billing.id, shipments.count())

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
        print subsc_id,
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

        #sub_shipments = shipments.filter(pickup__subcustomer_code__id=subsc_id)
        #sbilling.shipments.add(*(list(sub_shipments)))
        #sub_shipments.update(sbilling=sbilling)

    return billing


def generate_bill_for_jasper(billing_from, billing_to):
    fwd_bill = generate_bill(billing_from, billing_to, bill_type=1)
    if fwd_bill: update_productbilling(fwd_bill.id)
    rev_bill = generate_bill(billing_from, billing_to, bill_type=0)
    if rev_bill: update_productbilling(rev_bill.id)
    return (fwd_bill, rev_bill)


# jasper and marble e-retail (6 and 149)
def normal_reverse_billing(billing_from, billing_to, shipper_id):
    fwd_bill = generate_bill(
        billing_from, billing_to, bill_type=1, shipper_id=shipper_id)
    if fwd_bill: update_productbilling(fwd_bill.id)
    rev_bill = generate_bill(
        billing_from, billing_to, bill_type=0, shipper_id=shipper_id)
    if rev_bill: update_productbilling(rev_bill.id)
    return (fwd_bill, rev_bill)
