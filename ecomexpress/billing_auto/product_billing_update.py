import calendar
import datetime
import xlrd

from django.conf import settings
from django.db.models import Count, Sum

from billing.models import BillingSubCustomer, Billing, ProductBilling
from customer.models import Customer, Product
from service_centre.models import Shipment


def producttype_billing(bill_id, product_type):
    billing = Billing.objects.get(id=bill_id)
    product = Product.objects.get(product_name=product_type)
    shipments = billing.shipments.filter(shipext__product=product)
    if shipments.count() == 0:
        return None

    # calculate order price charges
    ship_data = shipments.aggregate(
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
    cod_charges = shipments.exclude(rts_status = 1).aggregate(cod_charge=Sum('codcharge__cod_charge'))['cod_charge']
    cod_charges_negative = shipments.filter(rts_status = 1).aggregate(cod_charge=Sum('codcharge__cod_charge'))['cod_charge']

    # cod product type billing
    codcharge = cod_charges if cod_charges else 0
    codcharge_negative = cod_charges_negative if cod_charges_negative else 0

    product_billing = ProductBilling(
        billing = billing,
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
        total_chargeable_weight=ship_data.get('total_chargeable_weight', 0))

    product_billing.total_charge_pretax = ship_data.get("op_freight", 0)+\
        ship_data.get("op_sdl", 0)+\
        ship_data.get("op_fuel", 0)+\
        ship_data.get("op_valuable_cargo_handling_charge", 0)+\
        ship_data.get("op_to_pay", 0)+\
        ship_data.get("op_rto_price", 0)+\
        ship_data.get("op_sdd_charge", 0)+\
        ship_data.get("op_reverse_charge", 0) +\
        codcharge-\
        codcharge_negative

    product_billing.service_tax = product_billing.total_charge_pretax * 0.12
    product_billing.education_secondary_tax =  product_billing.service_tax * 0.02
    product_billing.cess_higher_secondary_tax =  product_billing.service_tax * 0.01
    product_billing.total_payable_charge = product_billing.total_charge_pretax + \
        product_billing.service_tax + \
        product_billing.education_secondary_tax + \
        product_billing.cess_higher_secondary_tax
    product_billing.generation_status = 1
    product_billing.save()

def update_productbilling(bill_id):
    product_types = Product.objects.values_list('product_name', flat=True)
    for product in product_types:
        producttype_billing(bill_id, product)
    return True

def update_productbilling_for_month(year, month):
    bills = Billing.objects.filter(billing_date__year=year, billing_date__month=month).values_list('id', flat=True)
    for b in bills:
        update_productbilling(b)
