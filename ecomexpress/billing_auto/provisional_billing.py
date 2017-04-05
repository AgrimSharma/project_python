import datetime

from django.db.models import Count, Sum, Q

from billing.models import BillingPreview, ProvisionalBillingQueue
from billing.models import ProvisionalProductBilling
from customer.models import Customer, Product
from service_centre.models import Shipment


def customer_provisional_billing(*args, **kwargs):
    customer = kwargs.get('customer')
    billing_date_from = kwargs.get('billing_from')
    billing_date_to = kwargs.get('billing_to')
    print customer

    shipments = Shipment.objects.filter(
        shipper__id=customer, 
        shipment_date__gte = billing_date_from,
        shipment_date__lte = billing_date_to)

    if not shipments.exists():
        print 'no shipments'
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
        op_to_pay = Sum('order_price__to_pay_charge'))

    cod_charges = shipments.exclude(rts_status = 1).\
        aggregate(cod_charge = Sum('codcharge__cod_charge'))

    cod_charges_negative = shipments.filter(rts_status = 1).\
        aggregate(cod_charge = Sum('codcharge__cod_charge'))

    if not cod_charges["cod_charge"]:
        cod_charges["cod_charge"] = 0

    if not cod_charges_negative["cod_charge"]:
        cod_charges_negative["cod_charge"] = 0

    total_charge_pretax = freight_data["op_freight"]+\
        freight_data["op_sdl"]+\
        freight_data["op_fuel"]+\
        freight_data["op_valuable_cargo_handling_charge"]+\
        freight_data["op_to_pay"]+\
        freight_data["op_rto_price"]+\
        freight_data["op_sdd_charge"]+\
        freight_data["op_reverse_charge"]+\
        cod_charges["cod_charge"]-\
        cod_charges_negative["cod_charge"]

    service_tax = total_charge_pretax * 0.12
    education_secondary_tax =  service_tax * 0.02
    cess_higher_secondary_tax = service_tax * 0.01
    total_payable_charge = total_charge_pretax + service_tax + education_secondary_tax + cess_higher_secondary_tax
    today = datetime.datetime.now()

    billing = BillingPreview.objects.create(
        customer_id = customer,
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
        billing_date = billing_date_to,
        billing_date_from = billing_date_from,
        shipment_count = freight_data["id__count"],
        total_chargeable_weight = freight_data['total_chargeable_weight'],
        total_charge_pretax = total_charge_pretax,
        service_tax = service_tax,
        education_secondary_tax = education_secondary_tax,
        cess_higher_secondary_tax = cess_higher_secondary_tax,
        total_payable_charge = total_payable_charge,
        generation_status = 1
    )

    # product billing section

    product_types = Product.objects.all()
    for product in product_types:
        prod_shipments = shipments.filter(shipext__product=product)

        if prod_shipments.count() == 0:
            continue

        # calculate order price charges
        ship_data = prod_shipments.aggregate(
            Count('id'),
            total_chargeable_weight=Sum('chargeable_weight'),
            op_freight=Sum('order_price__freight_charge'),
            op_sdl=Sum('order_price__sdl_charge'),
            op_fuel=Sum('order_price__fuel_surcharge'),
            op_rto_price=Sum('order_price__rto_charge'),
            op_sdd_charge=Sum('order_price__sdd_charge'),
            op_reverse_charge=Sum('order_price__reverse_charge'),
            op_valuable_cargo_handling_charge=Sum('order_price__valuable_cargo_handling_charge'),
            op_to_pay=Sum('order_price__to_pay_charge'))
    
        # calculate cod charges
        cod_charges = prod_shipments.exclude(rts_status = 1).aggregate(cod_charge=Sum('codcharge__cod_charge'))['cod_charge']
        cod_charges_negative = prod_shipments.filter(rts_status = 1).aggregate(cod_charge=Sum('codcharge__cod_charge'))['cod_charge']
    
        # cod product type billing
        codcharge = cod_charges if cod_charges else 0
        codcharge_negative = cod_charges_negative if cod_charges_negative else 0
    
        total_charge_pretax = ship_data.get("op_freight", 0)+\
            ship_data.get("op_sdl", 0)+\
            ship_data.get("op_fuel", 0)+\
            ship_data.get("op_valuable_cargo_handling_charge", 0)+\
            ship_data.get("op_to_pay", 0)+\
            ship_data.get("op_rto_price", 0)+\
            ship_data.get("op_sdd_charge", 0)+\
            ship_data.get("op_reverse_charge", 0) +\
            codcharge-\
            codcharge_negative
    
        service_tax = total_charge_pretax * 0.12
        education_secondary_tax =  service_tax * 0.02
        cess_higher_secondary_tax =  service_tax * 0.01
        total_payable_charge = total_charge_pretax + \
            service_tax + education_secondary_tax + cess_higher_secondary_tax

        ProvisionalProductBilling.objects.create(
            billing=billing,
            product=product,
            freight_charge=ship_data.get("op_freight", 0),
            sdl_charge=ship_data.get("op_sdl", 0),
            fuel_surcharge=ship_data.get("op_fuel", 0),
            valuable_cargo_handling_charge=ship_data.get("op_valuable_cargo_handling_charge", 0),
            to_pay_charge=ship_data.get("op_to_pay", 0),
            rto_charge=ship_data.get("op_rto_price", 0),
            sdd_charge=ship_data.get("op_sdd_charge", 0),
            reverse_charge=ship_data.get("op_reverse_charge", 0),
            shipment_count=ship_data.get('id__count'),
            cod_applied_charge=codcharge,
            cod_subtract_charge=codcharge_negative,
            total_cod_charge=codcharge - codcharge_negative,
            total_chargeable_weight=ship_data.get('total_chargeable_weight', 0),
            total_charge_pretax=total_charge_pretax,
            service_tax=service_tax,
            education_secondary_tax=education_secondary_tax,
            cess_higher_secondary_tax= cess_higher_secondary_tax,
            total_payable_charge=total_payable_charge)
    print 'return ', billing
    return billing
    

def do_provisional_billing(queue_id, *args, **kwargs):
    try:
        queue = ProvisionalBillingQueue.objects.get(id=queue_id)
    except ProvisionalBillingQueue.DoesNotExist:
        return None

    billing_from = queue.billing_from
    billing_to = queue.billing_to

    customers = Customer.objects.exclude(id=6).values_list('id', flat=True)

    for customer in customers:
        billing = customer_provisional_billing(
            billing_from=billing_from, 
            billing_to=billing_to, customer=customer)
        print billing
        if billing:
            queue.bills.add(billing)
    return True


def process_provisional_billqueue():
    queue = ProvisionalBillingQueue.objects.filter(status=0) 
    for q in queue:
        ProvisionalBillingQueue.objects.filter(id=q.id).update(status=1)
        done = do_provisional_billing(q.id)
        if done:
            ProvisionalBillingQueue.objects.filter(id=q.id).update(status=2)
    return True
