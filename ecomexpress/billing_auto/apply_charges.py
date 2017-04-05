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
from django.db import transaction, IntegrityError
from utils import *

now=datetime.datetime.now()
t8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
t3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)

def update_chargeable_original_wt(shipment):
    vol_div = VolumetricWeightDivisor.objects.filter(customer=shipment.shipper)
    if vol_div.exists():
        volumetric_weight_divisor = vol_div[0].divisor
    else:
        volumetric_weight_divisor = 5000
    #if not shipment.volumetric_weight:
    if shipment.length and shipment.breadth and shipment.height:
        volume = (float(shipment.length) * float(shipment.breadth) * float(shipment.height)) / volumetric_weight_divisor
        shipment.volumetric_weight = volume
    #min_actual_weight=0
    #shipment.volumetric_weight = ceil(2*shipment.volumetric_weight)/2.0 # why multiply and then divide by 2?
    if shipment.actual_weight and shipment.shipext.original_act_weight and shipment.shipext.original_act_weight < 20:
        shipment.actual_weight = shipment.shipext.original_act_weight

        minwt = MinActualWeight.objects.filter(customer=shipment.shipper)
        min_actual_weight = minwt[0].weight if minwt else 0
        max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        if min_actual_weight and max_weight_dimension <= min_actual_weight:
            max_weight_dimension =  shipment.actual_weight
        Shipment.objects.filter(pk=shipment.id).update(chargeable_weight=max_weight_dimension, volumetric_weight=shipment.volumetric_weight, actual_weight=shipment.actual_weight)
    return max_weight_dimension


def price_updated_special(shipment):
  #cutoff_date = get_latest_billing_cutoff()
  today = datetime.datetime.now()
  cutoff_passed = is_cutoff_passed(shipment)
  bill_history_obj = get_bill_history_model(shipment)
  bill_history_obj.shipment = shipment
  bill_history_obj.subcustomer = shipment.pickup.subcustomer_code
  bill_history_obj.collectable_value = shipment.collectable_value
  bill_history_obj.inscan_date = shipment.inscan_date
  bill_history_obj.original_dest = shipment.original_dest
  #print 'setting chargeable weight and shipment date...'
  #shipment.set_chargeable_weight
 # shipment.set_shipment_date
  #print 'statrt update'

  if not shipment.billing:
     order=shipment
     #vol_div = VolumetricWeightDivisor.objects.filter(customer=order.shipper)
     #if vol_div:
        #volumetric_weight_divisor = vol_div[0].divisor
     #else:
        #volumetric_weight_divisor = 5000
#
     #if not order.volumetric_weight:
        #if order.length and order.breadth and order.height:
            #volume = (float(order.length)*float(order.breadth)*float(order.height))/volumetric_weight_divisor
            #order.volumetric_weight = volume
     #order.volumetric_weight = ceil(2*order.volumetric_weight)/2.0 # why multiply and then divide by 2?
                                                                   ## cant we directly find the ceil of the value
     #order.actual_weight = ceil(2*order.actual_weight)/2.0
     if not cutoff_passed:
      #  shipment.set_chargeable_weight
        shipment.set_shipment_date
        bill_history_obj.volumetric_weight = order.volumetric_weight
        bill_history_obj.actual_weight = order.actual_weight
        Shipment.objects.filter(pk=order.id).\
                         update(actual_weight=order.actual_weight,
                                volumetric_weight=order.volumetric_weight)

     #shipment.chargeable_weight = order.set_chargeable_weight
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
     freight_slabs = FreightSlab.objects.filter(customer=customer,
         range_from__lte=chargeable_weight, freightslabzone__zone_org = org_zone, freightslabzone__zone_dest = dest_zone).order_by("range_from")

     #return freight_slabs

     #### City Wise Charges
     freight_slabs_city = FreightSlabCity.objects.filter(customer=customer,
                                                      city_org = org_city,
                                                      city_dest = dest_city,
                                                      product__product_name=shipment.product_type,
                                                      range_from__lte=chargeable_weight).\
                                                      order_by("range_from")
     if freight_slabs_city:
         freight_slabs = freight_slabs_city
         product_type = "city_wise_freight"

     #### Origin Zone Charges
     freight_slabs_org_zone = FreightSlabOriginZone.objects.filter(customer=customer,
                                                      org_zone = shipment.pickup.service_centre.city.zone,
                                                      city_dest = dest_city,
                                                      product__product_name=shipment.product_type,
                                                      range_from__lte=chargeable_weight).\
                                                      order_by("range_from")
     if freight_slabs_org_zone:
         freight_slabs =freight_slabs_org_zone
         product_type = "zone_city_wise_freight"     #### stop City Wise Charges
 

     #### Dest Zone Charges
     freight_slabs_dest_zone = FreightSlabDestZone.objects.filter(customer=customer,
                                                      dest_zone = dest_zone,
                                                      city_org = org_city,
                                                      product__product_name=shipment.product_type,
                                                      range_from__lte=chargeable_weight).\
                                                      order_by("range_from")
     if freight_slabs_dest_zone:
         freight_slabs =freight_slabs_dest_zone
         product_type = "dest_zone_wise_freight"     #### stop City Wise Charges
 
     if shipment.product_type == "cod":
        cod_freight_slabs = CODFreightSlab.objects.filter(customer=customer,
                                                      range_from__lte=chargeable_weight).\
                                                      order_by("range_from")
        if cod_freight_slabs:
            freight_slabs = cod_freight_slabs
            product_type = "cod"
     if shipment.rts_status == 1:
        rts_freight_slabs_zone = RTSFreightSlabZone.objects.filter(freight_slab__customer=customer,
                                                      zone_org = org_zone,
                                                      zone_dest = dest_zone,
                                                      freight_slab__range_from__lte=chargeable_weight).\
                                                      order_by("freight_slab__range_from")
        if rts_freight_slabs_zone:
            freight_slabs = RTSFreightSlab.objects.filter(customer=customer,
                                                      range_from__lte=chargeable_weight).\
                                                      order_by("range_from")
           # freight_slabs = rts_freight_slabs
            product_type = "rts"
     if shipment.reverse_pickup == 1:
        rev_freight_slabs = ReverseFreightSlab.objects.filter(customer=customer,
                                                          range_from__lte=chargeable_weight).\
                                                          order_by("range_from")
        if rev_freight_slabs:
            freight_slabs = rev_freight_slabs
            product_type = "reverse"


     #print freight_slabs
     for freight_slab in freight_slabs:
        if chargeable_weight:
            if chargeable_weight > (freight_slab.range_to - freight_slab.range_from) + 1:
                if freight_slab.range_from == 0:
                    chargeable_weight = chargeable_weight - freight_slab.range_to
                    weight_for_this_slab = freight_slab.range_to
                else:
                    weight_for_this_slab = (freight_slab.range_to - freight_slab.range_from) + 1
                    chargeable_weight = chargeable_weight - weight_for_this_slab
            else:
                weight_for_this_slab = chargeable_weight
                chargeable_weight = 0

            if product_type == "city_wise_freight":
               fs_zones = [freight_slab]
            elif product_type == "zone_city_wise_freight":
               fs_zones = [freight_slab]
            elif product_type == "dest_zone_wise_freight":
               fs_zones = [freight_slab]
            elif product_type == "cod":
               fs_zones = CODFreightSlabZone.objects.filter(
                   freight_slab = freight_slab,
                   zone_org = org_zone,
                   zone_dest = dest_zone).order_by("-rate_per_slab")
            elif product_type == "rts":
               fs_zones = RTSFreightSlabZone.objects.filter(
                   freight_slab = freight_slab,
                   zone_org = org_zone,
                   zone_dest = dest_zone).order_by("-rate_per_slab")
            elif product_type == "reverse":
               fs_zones = ReverseFreightSlabZone.objects.filter(
                   freight_slab = freight_slab,
                   zone_org = org_zone,
                   zone_dest = dest_zone).order_by("-rate_per_slab")
            elif product_type == "all":
               fs_zones = FreightSlabZone.objects.filter(freight_slab = freight_slab,
                   zone_org = org_zone,
                   zone_dest = dest_zone).order_by("-rate_per_slab")
           # print fs_zones
            if fs_zones:
               fs_zone = fs_zones[0]
               freight_rate = fs_zone.rate_per_slab
            else:
               freight_rate = freight_slab.weight_rate
            freight_charge = freight_charge + ceil(weight_for_this_slab / float(freight_slab.slab)) * freight_rate

     ### SDD calculations
     chargeable_weight = max_weight_dimension*1000
     freight_slabs = FreightSlab.objects.filter(customer=customer, range_from__lte=chargeable_weight).order_by("range_from")
     for freight_slab in freight_slabs:
        if chargeable_weight:
            if chargeable_weight > freight_slab.range_to:
                if freight_slab.range_from == 0:
                    chargeable_weight = chargeable_weight - freight_slab.range_to
                    weight_for_this_slab = freight_slab.range_to
                else:
                    weight_for_this_slab = freight_slab.range_to - freight_slab.range_from + 1
                    chargeable_weight = chargeable_weight - weight_for_this_slab
            else:
                weight_for_this_slab = chargeable_weight
                chargeable_weight = 0
        sdd_zones = SDDSlabZone.objects.filter(freight_slab=freight_slab,
                                               sddzone__pincode__pincode=shipment.pickup.subcustomer_code.address.pincode).\
                                        filter(freight_slab=freight_slab,
                                               sddzone__pincode__pincode=shipment.pincode)

   #    sdd_zones = SDDSlabZone.objects.filter(freight_slab = freight_slab, zone_org = org_zone, zone_dest = dest_zone).order_by("-rate_per_slab")
        if (sdd_zones and (shipment.added_on.time() >= t8am.time() and \
                    shipment.added_on.time() <= t3pm.time()) and \
                    (shipment.rts_status <> 1) and (shipment.reverse_pickup <> 1)):
      # if (sdd_zones and (shipment.added_on.time().hour >= 8 and shipment.added_on.time().hour <=15)):
               sdd_zone = sdd_zones[0]
               sdd_charge = sdd_charge + ceil(weight_for_this_slab / float(freight_slab.slab)) * sdd_zone.rate_per_slab
              # shipment.sdd = 1
               Shipment.objects.filter(pk=shipment.id).update(sdd=1)
        else:
            sdd_rate = 0

     bill_history_obj.freight_charge = freight_charge
  #   if not cutoff_passed:
  #     op = Order_price.objects.update_or_create(shipment = shipment, defaults={'freight_charge':freight_charge, 'sdd_charge' : sdd_charge})
   #  if Order_price.objects.filter(shipment = shipment):
   #       shipment_charges = Order_price.objects.get(shipment = shipment)
   #       shipment_charges.freight_charge = freight_charge
   #       shipment_charges.sdd_charge = sdd_charge #changed
     #     if not cutoff_passed:
     #         shipment_charges.save()
    # else:
    #      shipment_charges = Order_price.objects.create(shipment = shipment, freight_charge = freight_charge)
    #      if not cutoff_passed:
    #          shipment_charges.save()

     sdl_charge = 0
     if shipment.rts_status <> 1:
       pincode = shipment.shipext.original_pincode if shipment.shipext.original_pincode else shipment.pincode
       if Pincode.objects.filter(pincode = pincode):
          pincode = Pincode.objects.get(pincode = pincode)
          if pincode.sdl:
            Shipment.objects.filter(pk=shipment.id).update(sdl=1)
            sdl_chargeable_weight = max_weight_dimension*1000
            sdl_slabs = SDLSlabCustomer.objects.filter(customer=customer,range_from__lte=sdl_chargeable_weight).order_by("range_from")
            if not sdl_slabs:
               sdl_slabs = SDLSlab.objects.filter(range_from__lte=sdl_chargeable_weight).order_by("range_from")
            for sdl_slab in sdl_slabs:
               if sdl_chargeable_weight:
                   if sdl_chargeable_weight > sdl_slab.range_to:
                       sdl_chargeable_weight = sdl_chargeable_weight - sdl_slab.range_to
                       weight_for_this_slab = sdl_slab.range_to
                   else:
                       weight_for_this_slab = sdl_chargeable_weight
                       sdl_chargeable_weight = 0
                   sdl_rate = sdl_slab.weight_rate
                   sdl_charge = sdl_charge + ceil(weight_for_this_slab/float(sdl_slab.slab)) * sdl_rate


            bill_history_obj.sdl_charge = sdl_charge
          #  if not cutoff_passed:
          #     op = Order_price.objects.update_or_create(shipment = shipment, defaults={'sdl_charge' : sdl_charge})

        #    if Order_price.objects.filter(shipment = shipment): # and date not passed
        #         shipment_charges = Order_price.objects.get(shipment = shipment)
        #         shipment_charges.sdl_charge = sdl_charge
        #         if not cutoff_passed:
        #            shipment_charges.save()
        #    else:
        #         shipment_charges = Order_price.objects.create(shipment = shipment, sdl_charge = sdl_charge)
        #         if not cutoff_passed:
        #            shipment_charges.save()

     if order.pickup.to_pay == 1 and shipment.rts_status <> 1:
        to_pay_charge = (max_weight_dimension / fs.slab) * customer.to_pay_charge
     else:
        to_pay_charge = 0

   #  shipment_charges.to_pay_charge = to_pay_charge
     bill_history_obj.to_pay_charge = to_pay_charge
   #  if not cutoff_passed:
   #     shipment_charges.save()

     if (customer.reverse_charges and shipment.reverse_pickup == 1):
             reverse_charge = customer.reverse_charges
     else:
             reverse_charge = 0

  #   shipment_charges.reverse_charge = reverse_charge
     bill_history_obj.reverse_charge = reverse_charge
  #   if not cutoff_passed:
  #      op = Order_price.objects.update_or_create(shipment = shipment, defaults={'to_pay_charge' : to_pay_charge, 'reverse_charge':reverse_charge})
       # shipment_charges.save()

     tot_charge = freight_charge+sdd_charge+to_pay_charge+reverse_charge
     freight_surcharge = 0
     if customer.fuel_surcharge_applicable:
        if customer.fuelsurcharge_set.all():
            fsurcharge = customer.fuelsurcharge_set.all()[0]
            min_brent_rate = fsurcharge.fuelsurcharge_min_fuel_rate
            if fsurcharge.fuelsurchargezone_set.filter(f_zone_org=org_zone,
                                                       f_zone_dest = dest_zone,
                                                       product__product_name=shipment.product_type):
                fsurcharge = fsurcharge.fuelsurchargezone_set.filter( f_zone_org = org_zone, f_zone_dest = dest_zone)[0]
            elif fsurcharge.fuelsurchargezone_set.filter(f_zone_org=org_zone,
                                                         f_zone_dest=dest_zone,
                                                         product=None):
                fsurcharge = fsurcharge.fuelsurchargezone_set.filter( f_zone_org = org_zone, f_zone_dest = dest_zone)[0]
            if fsurcharge.flat_fuel_surcharge:
                freight_surcharge = (fsurcharge.flat_fuel_surcharge * tot_charge) / 100
            elif fsurcharge.fuelsurcharge_min_rate == 0 and fsurcharge.max_fuel_surcharge == 0 and fsurcharge.flat_fuel_surcharge == 0:
                freight_surcharge = 0
            else:
                br = Brentrate.objects.all().order_by('-todays_date')[:1][0]
                if br.todays_rate > fsurcharge.fuelsurcharge_min_fuel_rate:
                    fuel_surcharge_percentage = ((ceil((br.todays_rate - min_brent_rate)/br.fuel_cost_increase) * br.percentage_increase) + fsurcharge.fuelsurcharge_min_rate)
                    freight_surcharge = ((fuel_surcharge_percentage * tot_charge)/100)
                    if fsurcharge.max_fuel_surcharge:
                        if fuel_surcharge_percentage > fsurcharge.max_fuel_surcharge:
                            freight_surcharge = ((fsurcharge.max_fuel_surcharge * tot_charge)/100)
                else:
                    freight_surcharge = ((fsurcharge.fuelsurcharge_min_rate * tot_charge)/100)
        else:
           pass
     else:
        freight_surcharge = 0

    # shipment_charges.fuel_surcharge = freight_surcharge
    # shipment_charges.save()
     #shipment_charges.fuel_surcharge = freight_surcharge
     bill_history_obj.fuel_surcharge = freight_surcharge
    # if not cutoff_passed:
      #   op = Order_price.objects.update_or_create(shipment = shipment, defaults={'fuel_surcharge' : freight_surcharge})
       # shipment_charges.save()

     if order.rts_status==1:
        try:
          rto_charge = (max_weight_dimension / fs.slab) * customer.return_to_origin
        except:
          rto_charge=0
     else:
        rto_charge = 0

    # shipment_charges.rto_charge = rto_charge
     bill_history_obj.rto_charge = rto_charge
     #if not cutoff_passed:
         
      #  shipment_charges.save()

    # if order.pickup.to_pay == 1:
    #    to_pay_charge = (max_weight_dimension / fs.slab) * customer.to_pay_charge
    # else:
    #    to_pay_charge = 0

    # shipment_charges.to_pay_charge = to_pay_charge
    # shipment_charges.save()

     vchc_min = customer.vchc_min
     vchc_rate = customer.vchc_rate
     vchc_min_amnt_applied = customer.vchc_min_amnt_applied

     if not shipment.declared_value:
         shipment.declared_value=shipment.collectable_value
     if shipment.actual_weight and shipment.declared_value/shipment.actual_weight >= vchc_min_amnt_applied:
          vchc_charges = float(shipment.declared_value/shipment.actual_weight - vchc_min_amnt_applied) * float(shipment.actual_weight) * float(vchc_rate/100)
          if vchc_charges < vchc_min:
             vchc_charges = vchc_min
     else:
          vchc_charges = 0

   #  shipment_charges.valuable_cargo_handling_charge = vchc_charges
     bill_history_obj.valuable_cargo_handling_charge = vchc_charges
  #   if not cutoff_passed:
   #     shipment_charges.save()

     if shipment.product_type.lower() == "cod":
         if shipment.rts_status == 1:
            cod_charges = CODCharge.objects.get(shipment__airwaybill_number=shipment.ref_airwaybill_number).cod_charge   
         elif customer.flat_cod_amt:
            cod_charges = customer.flat_cod_amt

         else :
              if CashOnDeliveryZone.objects.filter(customer=customer, start_range__lte=shipment.collectable_value, end_range__gte=shipment.collectable_value, c_zone_org = org_zone, c_zone_dest = dest_zone):
                    cods = CashOnDeliveryZone.objects.filter(customer=customer, start_range__lte=shipment.collectable_value, end_range__gte=shipment.collectable_value, c_zone_org = org_zone, c_zone_dest = dest_zone)[0]
                    if cods.flat_COD_charge:
                      cod_charges = cods.flat_COD_charge
                    else:
                      cod_charges = shipment.collectable_value * (cods.COD_service_charge/100)
                      if cod_charges < cods.minimum_COD_charge:
                          cod_charges = cods.minimum_COD_charge

              elif CashOnDelivery.objects.filter(customer=customer, start_range__lte=shipment.collectable_value, end_range__gte=shipment.collectable_value):
                    cod = CashOnDelivery.objects.filter(customer=customer, start_range__lte=shipment.collectable_value, end_range__gte=shipment.collectable_value).order_by("-COD_service_charge", "-flat_COD_charge")[:1][0]
                    if cod.flat_COD_charge:
                       cod_charges = cod.flat_COD_charge
                    else:
                        cod_charges = shipment.collectable_value * (cod.COD_service_charge/100)
                        if cod_charges < cod.minimum_COD_charge:
                           cod_charges = cod.minimum_COD_charge
              else:
                  cod_charges = 0

         bill_history_obj.cod_charge = cod_charges

         #if CODCharge.objects.filter(shipment=shipment):
         #    cod_charge_obj = CODCharge.objects.get(shipment=shipment)
         #    cod_charge_obj.cod_charge = cod_charges
         #    cod_charge_obj.updated_on = now
         #    if not cutoff_passed:
         #        cod_charge_obj.save()
         #else:
         #    if not cutoff_passed:
         if not cutoff_passed:
      #       co =   CODCharge.objects.filter(shipment=shipment).update(cod_charge=cod_charges, updated_on=now)
       #      if not co:
     #           co = CODCharge.objects.create(shipment=shipment, cod_charge=cod_charges, updated_on=now)
            co =   CODCharge.objects.update_or_create(shipment=shipment, defaults={'cod_charge':cod_charges, 'updated_on':now})
         bill_history_obj.save()
     
     #Final price saving
     if not cutoff_passed:
 #        op = Order_price.objects.filter(shipment = shipment).update(freight_charge=freight_charge, sdd_charge = sdd_charge, fuel_surcharge = freight_surcharge, valuable_cargo_handling_charge = vchc_charges, to_pay_charge = to_pay_charge, rto_charge=rto_charge, reverse_charge=reverse_charge, sdl_charge= sdl_charge)
  #       if not op:
   #          op = Order_price.objects.create(shipment = shipment, freight_charge=freight_charge, sdd_charge = sdd_charge, fuel_surcharge = freight_surcharge, valuable_cargo_handling_charge = vchc_charges, to_pay_charge = to_pay_charge, rto_charge=rto_charge, reverse_charge=reverse_charge, sdl_charge= sdl_charge)
        op = Order_price.objects.update_or_create(shipment = shipment, defaults={'freight_charge':freight_charge, 'sdd_charge' : sdd_charge, 'fuel_surcharge' : freight_surcharge, 'valuable_cargo_handling_charge' : vchc_charges, 'to_pay_charge' : to_pay_charge, 'rto_charge':rto_charge, 'reverse_charge':reverse_charge, 'sdl_charge' : sdl_charge})

def rts_pricing_special(shipment):
    price_updated_special(shipment)

    # updated:jinesh
    cutoff_date = get_latest_billing_cutoff()
    today = datetime.datetime.now()
    cutoff_passed = is_cutoff_passed(shipment)
    bill_history_obj = get_bill_history_model(shipment)
    bill_history_obj.shipment = shipment
    bill_history_obj.subcustomer = shipment.pickup.subcustomer_code
    bill_history_obj.collectable_value = shipment.collectable_value
    bill_history_obj.inscan_date = shipment.inscan_date
    bill_history_obj.original_dest = shipment.original_dest

    orig_shipment = Shipment.objects.get(airwaybill_number=shipment.ref_airwaybill_number)
    org_zone = orig_shipment.pickup.service_centre.city.zone
    if shipment.original_dest:
         dest_zone = shipment.original_dest.city.zone
    else:
         subject = "RTS pricing for shipment not having original destination"
         from_email = "support@ecomexpress.in"
         to_email = ("samar@prtouch.com", "jignesh@prtouch.com")
         email_msg = str(shipment.airwaybill_number)
         send_mail(subject,email_msg,from_email,to_email)
         dest_zone = shipment.service_centre.city.zone
    customer = orig_shipment.shipper

   #if shipment.product_type == "cod":
   #    ref_cod_charge = CODCharge.objects.get(shipment=orig_shipment)
   #    ref_cod_charge.id = None
   #    ref_cod_charge.updated_on =now
   #    ref_cod_charge.shipment=shipment
   #    ref_cod_charge.save()

    rts_freight_rate=100.0
    rts_fuel_rate=100.0
   # print customer, org_zone, dest_zone
    if RTSFreightZone.objects.filter(customer=customer, origin=org_zone, destination=dest_zone):
    #   print RTSFreightZone.objects.filter(customer=customer, origin=org_zone, destination=dest_zone), "chk"
       rts_freight_rate = RTSFreightZone.objects.get(customer=customer, origin=org_zone, destination=dest_zone).rate
    elif RTSFreight.objects.filter(customer=customer):
       rts_freight_rate = RTSFreight.objects.filter(customer=customer)[0].rate
    if RTSFuelZone.objects.filter(customer=customer, origin=org_zone, destination=dest_zone):
       rts_fuel_rate = RTSFuelZone.objects.get(customer=customer, origin=org_zone, destination=dest_zone).rate
    elif RTSFuel.objects.filter(customer=customer):
       rts_fuel_rate = RTSFuel.objects.filter(customer=customer)[0].rate

    if Order_price.objects.filter(shipment = shipment):
          order_price = Order_price.objects.get(shipment = shipment)
    else:
         order_price = Order_price.objects.create(shipment = shipment)
       #   if not cutoff_passed:
       #       order_price.save()

    freight_rate = order_price.freight_charge*(rts_freight_rate/100.0)
    fuel_surcharge = order_price.fuel_surcharge*(rts_fuel_rate/100.0)
    order_price.freight_charge=freight_rate
    order_price.fuel_surcharge = fuel_surcharge
    order_price.sdl_charge=0

    bill_history_obj.freight_charge=freight_rate
    bill_history_obj.fuel_surcharge = fuel_surcharge
    bill_history_obj.sdl_charge=0

    if not cutoff_passed:
        op = Order_price.objects.update_or_create(shipment = shipment, defaults={'freight_charge':freight_rate, 'fuel_surcharge' : fuel_surcharge, 'sdl_charge':0})  
       # order_price.save()
  #  max_weight_dimension = chargeable_weight(shipment)
  #  freight_charge = 0
  #  chargeable_wt = max_weight_dimension*1000
  #  freight_slabs = RTSFreightSlabRate.objects.filter(customer=customer, origin = org_zone, destination = dest_zone, range_from__lte=chargeable_wt).order_by("range_from")
  #  for freight_slab in freight_slabs:
  #      if not freight_slab.normal_applicable:
  #          weight_for_this_slab = freight_slab.range_to
  #          freight_rate = freight_slabs.rate
  #          freight_charge = freight_charge + ceil(weight_for_this_slab / float(freight_slab.slab)) * freight_rate
  #          fuel_surcharge(shipment)
  #      else:
  #          freight_charge(shipment)
  #          fuel_surcharge(shipment)
  #  cod_charge(shipment)
    bill_history_obj.save()
    return True


