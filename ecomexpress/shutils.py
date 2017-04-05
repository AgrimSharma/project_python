import os
import csv
from math import ceil
import datetime
import sys, traceback
from datetime import timedelta

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.db.models.loading import get_model
from django.core.exceptions import PermissionDenied

from airwaybill.models import AirwaybillNumbers
from customer.models import *
from service_centre.models import *
from billing.models import *
from billing.charge_calculations import add_to_shipment_queue
from django.db import transaction, IntegrityError

now=datetime.datetime.now()
t8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
t3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)

def get_slabs(awb, max_weight_dimension):
    shipment = Shipment.objects.get(airwaybill_number = awb)
    shipment.chargeable_weight = order.set_chargeable_weight
    max_weight_dimension = shipment.chargeable_weight
    org_zone = shipment.pickup.service_centre.city.zone
    org_city = shipment.pickup.service_centre.city
    if shipment.original_dest:
        dest_zone = shipment.original_dest.city.zone
        dest_city = shipment.original_dest.city
    else:
        subject = "Pricing for shipment not having original destination(Original Dest Updated)"
        from_email = "support@ecomexpress.in"
        to_email = ("samar@prtouch.com", "jignesh@prtouch.com")
        email_msg = str(shipment.airwaybill_number)
        send_mail(subject,email_msg,from_email,to_email)
        dest_zone = shipment.service_centre.city.zone
        dest_city = shipment.service_centre.city
        Shipment.objects.filter(id=shipment.id).update(original_dest=shipment.service_centre)
   # dest_zone = shipment.original_dest.city.zone
    shipment.set_shipment_date
    customer = shipment.shipper
    subcustomer=shipment.pickup.subcustomer_code

    sdd_charge = 0
    freight_charge = 0
    chargeable_weight = max_weight_dimension*1000
    # add shipments chargeable weight here.
    product_type = "all"
    #freight_slabs = FreightSlab.objects.filter(customer=customer,
    #    range_from__lte=chargeable_weight).order_by("range_from")
    freight_slabs = FreightSlabZone.objects.filter(freight_slab__customer__id=customer.id,
                zone_org = org_zone,
                zone_dest = dest_zone,
        freight_slab__range_from__lte=chargeable_weight).order_by("freight_slab__range_from")

    #### City Wise Charges
    freight_slabs_city = FreightSlabCity.objects.filter(customer__id=customer.id,
                                                     city_org = org_city,
                                                     city_dest = dest_city,
                                                     product__product_name=shipment.product_type,
                                                     range_from__lte=chargeable_weight).\
                                                     order_by("range_from")
    if freight_slabs_city:
        freight_slabs = freight_slabs_city
        product_type = "city_wise_freight"

    #### Origin Zone Charges
    freight_slabs_org_zone = FreightSlabOriginZone.objects.filter(customer__id=customer.id,
                                                     org_zone = shipment.pickup.service_centre.city.zone,
                                                     city_dest = dest_city,
                                                     product__product_name=shipment.product_type,
                                                     range_from__lte=chargeable_weight).\
                                                     order_by("range_from")
    if freight_slabs_org_zone:
        freight_slabs =freight_slabs_org_zone
        product_type = "zone_city_wise_freight"     #### stop City Wise Charges


    #### Dest Zone Charges
    freight_slabs_dest_zone = FreightSlabDestZone.objects.filter(customer__id=customer.id,
                                                     dest_zone = dest_zone,
                                                     city_org = org_city,
                                                     product__product_name=shipment.product_type,
                                                     range_from__lte=chargeable_weight).\
                                                     order_by("range_from")
    if freight_slabs_dest_zone:
        freight_slabs =freight_slabs_dest_zone
        product_type = "dest_zone_wise_freight"     #### stop City Wise Charges

    if shipment.product_type == "cod":
       cod_freight_slabs = CODFreightSlabZone.objects.filter(freight_slab__customer__id=customer.id,
                                                     zone_org = org_zone,
                                                     zone_dest = dest_zone,
                                                     freight_slab__range_from__lte=chargeable_weight).\
                                                     order_by("freight_slab__range_from")
       if cod_freight_slabs:
           freight_slabs = cod_freight_slabs
           product_type = "cod"
    if shipment.rts_status == 1:
       rts_freight_slabs_zone = RTSFreightSlabZone.objects.filter(freight_slab__customer__id=customer.id,
                                                     zone_org = org_zone,
                                                     zone_dest = dest_zone,
                                                     freight_slab__range_from__lte=chargeable_weight).\
                                                     order_by("freight_slab__range_from")
       if rts_freight_slabs_zone:
           freight_slabs = rts_freight_slabs_zone
           product_type = "rts"
    if shipment.reverse_pickup == 1:
       rev_freight_slabs = ReverseFreightSlab.objects.filter(freight_slab__customer__id=customer.id,
                                                         zone_org = org_zone,
                                                         zone_dest = dest_zone,
                                                         freight_slab__range_from__lte=chargeable_weight).\
                                                         order_by("freight_slab__range_from")
       if rev_freight_slabs:
           freight_slabs = rev_freight_slabs
           product_type = "reverse"


    return freight_slabs 
