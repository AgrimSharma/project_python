from django import template
from track_me.models import *
from service_centre.models import *
from django.db.models.loading import get_model
import re

register = template.Library()
import datetime

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

@register.filter(name="otherfreight")
def otherfreight(request):
    op = request
    if not op:
         return 0 
    if not op.sdl_charge:
         op.sdl_charge = 0 
    other_price = op.sdl_charge + op.rto_charge + op.to_pay_charge + op.valuable_cargo_handling_charge 
    return other_price

@register.filter(name="totalcharges")
def totalcharges(request):
    a =  request
    op = a.order_price_set.all()[0]
    if not op.sdl_charge:
         op.sdl_charge = 0 
    total_op = op.sdl_charge + op.rto_charge + op.to_pay_charge + op.freight_charge + op.valuable_cargo_handling_charge
    if a.codcharge_set.all():
         codcharge = a.codcharge_set.all()[0].cod_charge
    else: 
         codcharge = 0
    if a.rts_status == 1:
        return total_op - codcharge
    else:
        return total_op + codcharge



@register.filter(name="subtractfilter")
def subtractfilter(request, b):
    a =  request
    return a - b

@register.filter(name="subcustomer_total")
def subcustomer_total(request):
    sbilling =  request
    total_sbilling = sbilling.rto_charge + sbilling.to_pay_charge + sbilling.freight_charge + sbilling.valuable_cargo_handling_charge + sbilling.demarrage_charge + sbilling.fuel_surcharge + sbilling.cod_applied_charge - sbilling.cod_subtract_charge + sbilling.sdl_charge +   sbilling.sdd_charge  + sbilling.reverse_charge
    return total_sbilling

@register.filter(name="accurate_weight")
def accurate_weight(request):
    shipment = request
    if MinActualWeight.objects.filter(customer=shipment.shipper):
        min_actual_weight = MinActualWeight.objects.get(customer=shipment.shipper).weight
    else: 
        min_actual_weight = 0

    max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
    if min_actual_weight:
        if max_weight_dimension <= min_actual_weight: 
            max_weight_dimension =  shipment.actual_weight
        else:
            max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
    else:
        max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
    return max_weight_dimension    




@register.filter(name="get_employee_code")
def get_employee_code(request):
    shipment = request
    if shipment.status == 7:
        os = shipment.deliveryoutscan_set.latest("added_on")
        return os.employee_code.employee_code

@register.filter(name="get_employee_name")
def get_employee_name(request):
    shipment = request
    if shipment.status == 7:
        os = shipment.deliveryoutscan_set.latest("added_on")
        return os.employee_code.firstname + " " + os.employee_code.lastname

@register.filter(name="get_outscan_number")
def get_outscan_number(request):
    shipment = request
    if shipment.status == 7:
        os = shipment.deliveryoutscan_set.latest("added_on")
        return os.id

@register.filter(name="get_address")
def get_address(request):
    address = request
    if address:
        address = re.sub('[^A-Za-z0-9]+',' ',address)
    return address

@register.filter(name="get_sequence_number")
def get_sequence_number(request):
    sh = request
    if sh.status == 7:
       from service_centre.models import OutscanShipments
       try:
           return OutscanShipments.objects.get(outscan = sh.deliveryoutscan_set.latest('id').id, awb = sh.airwaybill_number).serial
       except:
           return 0

@register.filter(name="get_addresss")
def update_address(request):
    address = request
    if address:
      address = removeNonAscii(address)
    return address

