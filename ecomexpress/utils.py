from math import ceil
import datetime
from datetime import timedelta

from django.db.models import *
from django.core.mail import send_mail
from django.db.models.loading import get_model
from django.core.exceptions import PermissionDenied
from delivery.models import *
from reports.models import *
from airwaybill.models import AirwaybillNumbers
from customer.models import *
from service_centre.models import *
from billing.models import *
from billing.charge_calculations import add_to_shipment_queue
from reports.models import ShipmentBagHistory

now=datetime.datetime.now()
t8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
t3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)

def get_bill_history_model(shipment):
    upd_time = shipment.added_on
    monthdir = upd_time.strftime("%Y_%m")
    shipment_history = get_model('billing', 'BillingHistory_%s'%(monthdir))
    return shipment_history()

def is_cutoff_passed(shipment):
    """ Return True if the given shipment's inscan date is
    greater than 1st day 7am of current month"""
    if shipment.status < 2:
        return False
    month = datetime.date.today().month
    year = datetime.date.today().year
    cutoff_date = datetime.datetime(year, month, 1, 7, 0, 0)
    if now < cutoff_date:
        return False
    return shipment.inscan_date <= cutoff_date

def is_changeable(shipment):
    """ Return True if the given shipment's inscan date is
    greater than 1st day 7am of current month"""
    if shipment.status < 2:
        return False
    month = datetime.date.today().month
    year = datetime.date.today().year
    cutoff_date = datetime.datetime(year, month, 1, 7, 0, 0)
    return shipment.inscan_date > cutoff_date


def update_billing(cid, date):
    if Billing.objects.filter(customer__id = cid, generation_status = 0):
        billing =   Billing.objects.get(customer__id = cid, generation_status = 0)
    else:
        billing =   Billing(customer__id = cid, generation_status = 0)
        billing.save()
    billing.freight_charge = 0
    billing.sdl_charge = 0
    billing.fuel_surcharge = 0
    billing.valuable_cargo_handling_charge = 0
    billing.to_pay_charge = 0
    billing.rto_charge = 0
    billing.total_charge = 0
    #billing.demarrage_charge = 0
    billing.cod_applied_charge = 0
    billing.cod_subtract_charge = 0
    billing.total_cod_charge = 0
    #billing.demarrage_charge = 0
    billing.save()

    for billed_shipments in billing.shipments.all():
        billing.shipments.remove(billed_shipments)

    shippers = Shipper.objects.filter(customer=billing.customer)

    for shipper in shippers:
        if BillingSubCustomer.objects.filter(subcustomer=shipper, generation_status=0) :
            sbilling = BillingSubCustomer.objects.get(subcustomer=shipper, generation_status=0)
            sbilling.freight_charge = 0
            sbilling.sdl_charge = 0
            sbilling.fuel_surcharge = 0
            sbilling.valuable_cargo_handling_charge = 0
            sbilling.to_pay_charge = 0
            sbilling.rto_charge = 0
            sbilling.total_charge = 0
            #sbilling.demarrage_charge = 0
            sbilling.cod_applied_charge = 0
            sbilling.cod_subtract_charge = 0
            sbilling.total_cod_charge = 0
            sbilling.save()

            for sbilled_shipments in sbilling.shipments.all():
                sbilling.shipments.remove(sbilled_shipments)

    if billing.billing_date_from:
        bill_date = billing.billing_date_from
    else:
        bill_date = billing.customer.created_on
        billing.billing_date_from = billing.customer.created_on
        billing.save()

    if date:
        nextmonth_date = date.strftime('%Y-%m-%d 07:00:00')
        report_date = billing.billing_date_from.strftime('%Y-%m-%d 07:00:00')
        shipments = Shipment.objects.filter(shipper=billing.customer, inscan_date__range=(report_date, nextmonth_date))
        #return shipments.count()
    else:
        shipments = Shipment.objects.filter(shipper=billing.customer, inscan_date__gt=bill_date)


    for shipment in shipments:
        if shipment.order_price_set.all():
            shipment_charges = shipment.order_price_set.all()[0]
            billing.freight_charge = billing.freight_charge + shipment_charges.freight_charge
            billing.sdl_charge = billing.sdl_charge + shipment_charges.sdl_charge
            billing.fuel_surcharge = billing.fuel_surcharge + shipment_charges.fuel_surcharge
            billing.rto_charge = billing.rto_charge +shipment_charges.rto_charge
            billing.to_pay_charge =  billing.to_pay_charge + shipment_charges.to_pay_charge
        else:
            shipment_charges = False

        if shipment.product_type == "cod":
            if shipment.codcharge_set.all():
                cod_charges_obj = shipment.codcharge_set.all()[0]
                cod_charges = cod_charges_obj.cod_charge
            else:
                cod_charges = 0
            if cod_charges:
                if shipment.rts_status==1:
                    billing.cod_subtract_charge =  billing.cod_subtract_charge + cod_charges
                    billing.total_cod_charge =  billing.total_cod_charge - cod_charges
                else:
                    billing.cod_applied_charge =  billing.cod_applied_charge + cod_charges
                    billing.total_cod_charge =  billing.total_cod_charge + cod_charges

        shipment_status_updates = StatusUpdate.objects.filter(shipment=shipment, reason_code__in=[1,5,6]).order_by("-date")

        billing.save()
        if shipment.order_price_set.all():
            billing.shipments.add(shipment)

        subcustomer=shipment.pickup.subcustomer_code
	if subcustomer:
            if BillingSubCustomer.objects.filter(subcustomer=subcustomer, generation_status=0):
               sbilling = BillingSubCustomer.objects.get(subcustomer=subcustomer, generation_status=0)
            else:
               sbilling = BillingSubCustomer(subcustomer=subcustomer, generation_status=0)
               sbilling.save()

            if shipment_charges:
                sbilling.freight_charge = sbilling.freight_charge + shipment_charges.freight_charge
                sbilling.sdl_charge = sbilling.sdl_charge + shipment_charges.sdl_charge
                sbilling.fuel_surcharge = sbilling.fuel_surcharge + shipment_charges.fuel_surcharge
                sbilling.rto_charge = sbilling.rto_charge +shipment_charges.rto_charge
                sbilling.to_pay_charge =  sbilling.to_pay_charge + shipment_charges.to_pay_charge
            if shipment.product_type == "cod":
                if shipment.rts_status==1:
                    sbilling.cod_subtract_charge =  sbilling.cod_subtract_charge + cod_charges
                    sbilling.total_cod_charge =  sbilling.total_cod_charge - cod_charges
                else:
                    sbilling.cod_applied_charge =  sbilling.cod_applied_charge + cod_charges
                    sbilling.total_cod_charge =  sbilling.total_cod_charge - cod_charges

            #if demarrage_days:
            #    sbilling.demarrage_charge = sbilling.demarrage_charge + demarrage_charge_per_day * demarrage_days.days

            sbilling.save()
            sbilling.shipments.add(shipment)

    #VCHC
    return billing

def update_demarrage(cid, date):
    billing =   Billing.objects.get(customer__id = cid, generation_status = 0)
    billing.demarrage_charge = 0
    billing.save()

    shippers = Shipper.objects.filter(customer=billing.customer)

    for shipper in shippers:
        sbilling = BillingSubCustomer.objects.get(subcustomer=shipper, generation_status=0)
        sbilling.demarrage_charge = 0
        sbilling.save()

    if billing.billing_date_from:
        bill_date = billing.billing_date_from
    else:
        bill_date = billing.customer.created_on

    if date:
        status_updates = StatusUpdate.objects.filter(shipment__shipper=billing.customer, reason_code__id__in=[1, 5], date__gt=bill_date, date__lt=date)
    else:
        status_updates = StatusUpdate.objects.filter(shipment__shipper=billing.customer, reason_code__id__in=[1, 5], date__gt=bill_date)

    shipments = []
    for status_update in status_updates:
        if status_update.shipment not in shipments:
            shipments.append(status_update.shipment)

    for shipment in shipments:

        shipment_status_updates = StatusUpdate.objects.filter(shipment=shipment, reason_code__in=[1,5,6]).order_by("-date")

        if shipment_status_updates and shipment.expected_dod:
           demarrage_days = shipment_status_updates[0].date - (shipment.expected_dod.date() + timedelta(days=7))
        elif shipment.expected_dod:
           if shipment.expected_dod.date() < date:
               demarrage_days = date - shipment.expected_dod.date()
           else:
               demarrage_days = 0
        else:
           demarrage_days = 0

        if demarrage_days:
           max_weight_dimension = max(shipment.actual_weight, shipment.volumetric_weight)
           #return billing.customer.demarrage_perkg_amt
           demarrage_charge_per_day = max_weight_dimension/1000 * billing.customer.demarrage_perkg_amt
           if demarrage_charge_per_day < billing.customer.demarrage_min_amt:
               demarrage_charge_per_day = billing.customer.demarrage_min_amt
           billing.demarrage_charge = billing.demarrage_charge + demarrage_charge_per_day * demarrage_days.days

        billing.save()
        if shipment not in billing.demarrage_shipments.all():
            billing.demarrage_shipments.add(shipment)

        subcustomer=shipment.pickup.subcustomer_code
	if subcustomer:
            if BillingSubCustomer.objects.filter(subcustomer=subcustomer, generation_status=0):
               sbilling = BillingSubCustomer.objects.get(subcustomer=subcustomer, generation_status=0)
               if demarrage_days:
                   sbilling.demarrage_charge = sbilling.demarrage_charge + demarrage_charge_per_day * demarrage_days.days

               sbilling.save()
            if shipment not in sbilling.demarrage_shipments.all():
                sbilling.shipments.add(shipment)

    #VCHC
    return billing


def order_pricing_update(shipment):
     order = shipment
     if order.length and order.breadth and order.height:
         if order.shipper_id == 7 or order.shipper_id == 4:
             volume = (float(order.length)*float(order.breadth)*float(order.height))/6000
         else:
             volume = (float(order.length)*float(order.breadth)*float(order.height))/5000
         order.volumetric_weight = volume
     order.volumetric_weight = ceil(2*order.volumetric_weight)/2.0
     order.actual_weight = ceil(2*order.actual_weight)/2.0
     order.save()
     max_weight_dimension = max(float(order.volumetric_weight), order.actual_weight)

     shipper = Customer.objects.get(id=shipment.shipper.id)
     org_zone = shipment.pickup.service_centre.city.zone
     dest_zone = shipment.service_centre.city.zone
     customer = shipment.pickup.customer_code
     subcustomer=shipment.pickup.subcustomer_code

     freight_charge = 0
     chargeable_weight = max_weight_dimension*1000
     freight_slabs = FreightSlab.objects.filter(customer=customer, range_from__lte=chargeable_weight).order_by("range_from")
     for freight_slab in freight_slabs:
        if chargeable_weight:
            if chargeable_weight > freight_slab.range_to:
                chargeable_weight = chargeable_weight - freight_slab.range_to
                weight_for_this_slab = freight_slab.range_to
            else:
                weight_for_this_slab = chargeable_weight
                chargeable_weight = 0
            fs_zones = FreightSlabZone.objects.filter(freight_slab = freight_slab, zone_org = org_zone, zone_dest = dest_zone).order_by("-rate_per_slab")
            if fs_zones:
               fs_zone = fs_zones[0]
               freight_rate = fs_zone.rate_per_slab
            else:
               freight_rate = freight_slab.weight_rate
            freight_charge = freight_charge + (weight_for_this_slab / (freight_slab.slab)) * freight_rate


     if Order_price.objects.filter(shipment = shipment):

          shipment_charges = Order_price.objects.get(shipment = shipment)
          shipment_charges.freight_charge = freight_charge
          shipment_charges.save()
     else:

          shipment_charges = Order_price.objects.create(shipment = shipment, freight_charge = freight_charge)
          shipment_charges.save()

     #print freight_charge, max_weight_dimension , "freight_charge"
     if customer.fuel_surcharge_applicable:
        if customer.fuelsurcharge_set.all():
            fsurcharge = customer.fuelsurcharge_set.all()[0]
            min_brent_rate = fsurcharge.fuelsurcharge_min_fuel_rate
            if fsurcharge.fuelsurchargezone_set.filter( f_zone_org = org_zone, f_zone_dest = dest_zone):
                fsurcharge = fsurcharge.fuelsurchargezone_set.filter( f_zone_org = org_zone, f_zone_dest = dest_zone)[0]
            if fsurcharge.flat_fuel_surcharge:
                freight_surcharge = (fsurcharge.flat_fuel_surcharge * freight_charge)
            elif fsurcharge.fuelsurcharge_min_rate == 0 and fsurcharge.max_fuel_surcharge == 0 and fsurcharge.flat_fuel_surcharge == 0:
                freight_surcharge = 0
            else:
                br = Brentrate.objects.all().order_by('-todays_date')[:1][0]
                if br.todays_rate > min_brent_rate:
                    fuel_surcharge_percentage = ((ceil((br.todays_rate - min_brent_rate)/br.fuel_cost_increase) * br.percentage_increase) + fsurcharge.fuelsurcharge_min_rate) 
                    freight_surcharge = ((fuel_surcharge_percentage * freight_charge)/100)
                    if fsurcharge.max_fuel_surcharge:
                        if fuel_surcharge_percentage > fsurcharge.max_fuel_surcharge:
                            freight_surcharge = ((fsurcharge.max_fuel_surcharge * freight_charge)/100)
                else:
                    freight_surcharge = ((fsurcharge.fuelsurcharge_min_rate * freight_charge)/100)

        else:
           pass
     else:
        freight_surcharge = 0

     #print freight_surcharge , "fuel_charge"
     shipment_charges.fuel_surcharge = freight_surcharge
     shipment_charges.save()


     if order.rts_status==1:
        try:
          rto_charge = (max_weight_dimension / fs.slab) * customer.return_to_origin
        except:
          rto_charge=0
     else:
        rto_charge = 0

     shipment_charges.rto_charge = rto_charge
     shipment_charges.save()

     if order.pickup.to_pay == 1:
        to_pay_charge = (max_weight_dimension / fs.slab) * customer.to_pay_charge
     else:
        to_pay_charge = 0

     shipment_charges.to_pay_charge = to_pay_charge
     shipment_charges.save()

     vchc_min = customer.vchc_min
     vchc_rate = customer.vchc_rate
     vchc_min_amnt_applied = customer.vchc_min_amnt_applied

     if not shipment.declared_value:
         shipment.declared_value=shipment.collectable_value
     if shipment.declared_value/shipment.actual_weight >= vchc_min_amnt_applied:
          vchc_charges = float(shipment.declared_value/shipment.actual_weight - vchc_min_amnt_applied) * float(shipment.actual_weight) * float(vchc_rate/100)
          if vchc_charges < vchc_min:
             vchc_charges = vchc_min
     else:
          vchc_charges = 0

     shipment_charges.valuable_cargo_handling_charge = vchc_charges
     shipment_charges.save()

     if shipment.product_type.lower() == "cod":
         if customer.flat_cod_amt:
            cod_charges = customer.flat_cod_amt

         else :
            cods = CashOnDelivery.objects.filter(customer=customer, start_range__lte=shipment.collectable_value, end_range__gte=shipment.collectable_value).order_by("-COD_service_charge", "-flat_COD_charge")[:1]
            if cods:
                cod = cods[0]
                if cod.flat_COD_charge:
                    cod_charges = cod.flat_COD_charge
                else:
                    cod_charges = shipment.collectable_value * (cod.COD_service_charge/100)
                    if cod_charges < cod.minimum_COD_charge:
                        cod_charges = cod.minimum_COD_charge
            else:
                cod_charges = 0

         if CODCharge.objects.filter(shipment=shipment):
             cod_charge_obj = CODCharge.objects.get(shipment=shipment)
             cod_charge_obj.cod_charge = cod_charges
             #cod_charge_obj.updated_on = now
             cod_charge_obj.save()
         else:
             CODCharge.objects.create(shipment=shipment, cod_charge=cod_charges)

     #print cod_charges , "cod_charge"

     if Billing.objects.filter(customer=customer, generation_status=0):
        billing = Billing.objects.get(customer=customer, generation_status=0)
     else:
        billing = Billing.objects.create(customer=customer)

     billing.freight_charge = billing.freight_charge + shipment_charges.freight_charge
     billing.fuel_surcharge = billing.fuel_surcharge + shipment_charges.fuel_surcharge
     billing.rto_charge = billing.rto_charge +shipment_charges.rto_charge
     billing.to_pay_charge =  billing.to_pay_charge + shipment_charges.to_pay_charge
     if shipment.product_type.lower() == "cod":
         if shipment.rts_status==1:
             billing.cod_subtract_charge =  billing.cod_subtract_charge - cod_charges
         else:
             billing.cod_applied_charge =  billing.cod_applied_charge + cod_charges

     billing.save()
     billing.shipments.add(order)

     if BillingSubCustomer.objects.filter(subcustomer=subcustomer, generation_status=0):
        billing = BillingSubCustomer.objects.get(subcustomer=subcustomer, generation_status=0)
     else:
        billing =BillingSubCustomer.objects.create(subcustomer=subcustomer)

     billing.freight_charge = billing.freight_charge + shipment_charges.freight_charge
     billing.fuel_surcharge = billing.fuel_surcharge + shipment_charges.fuel_surcharge
     billing.rto_charge = billing.rto_charge +shipment_charges.rto_charge
     billing.to_pay_charge =  billing.to_pay_charge + shipment_charges.to_pay_charge
     if shipment.product_type == "cod":
         if shipment.rts_status==1:
             billing.cod_subtract_charge =  billing.cod_subtract_charge - cod_charges
         else:
             billing.cod_applied_charge =  billing.cod_applied_charge + cod_charges

     billing.save()
     billing.shipments.add(order)
     return "Updated"

def update_sdl_billing(shipment):
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

    sdl_charge=0
    max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
    customer = shipment.shipper
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
    shipment_charges = Order_price.objects.get(shipment = shipment)
    shipment_charges.sdl_charge = sdl_charge
    bill_history_obj.sdl_charge = sdl_charge
    bill_history_obj.save()
    if not cutoff_passed:
        shipment_charges.save()

def freight_charge(shipment):
     freight_charge = 0

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

     customer = shipment.shipper
     org_zone = shipment.pickup.service_centre.city.zone
     dest_zone = shipment.original_dest.city.zone
     chargeable_weight = max_weight_dimension*1000
     freight_slabs = FreightSlab.objects.filter(customer=customer, range_from__lte=chargeable_weight).order_by("range_from")
     for freight_slab in freight_slabs:
        if chargeable_weight:
            if chargeable_weight > freight_slab.range_to:
                chargeable_weight = chargeable_weight - freight_slab.range_to
                weight_for_this_slab = freight_slab.range_to
            else:
                weight_for_this_slab = chargeable_weight
                chargeable_weight = 0
            fs_zones = FreightSlabZone.objects.filter(freight_slab = freight_slab, zone_org = org_zone, zone_dest = dest_zone).order_by("-rate_per_slab")
            if fs_zones:
               fs_zone = fs_zones[0]
               freight_rate = fs_zone.rate_per_slab
            else:
               freight_rate = freight_slab.weight_rate
            freight_charge = freight_charge + ceil(weight_for_this_slab / float(freight_slab.slab)) * freight_rate

     bill_history_obj.freight_charge = freight_charge
     if Order_price.objects.filter(shipment = shipment):
          shipment_charges = Order_price.objects.get(shipment = shipment)
          shipment_charges.freight_charge = freight_charge
          if not cutoff_passed:
           shipment_charges.save()
     else:
          shipment_charges = Order_price.objects.create(shipment = shipment, freight_charge = freight_charge)
          if not cutoff_passed:
              shipment_charges.save()
     bill_history_obj.save()
     return freight_charge

def fuel_surcharge(shipment):
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

     customer = shipment.shipper
     org_zone = shipment.pickup.service_centre.city.zone
     dest_zone = shipment.original_dest.city.zone
     ship_charge = shipment.order_price_set.all()[0]
     if shipment.rts_status == 1:
         ffreight_charge = ship_charge.freight_charge
     else:
         ffreight_charge = ship_charge.freight_charge+ship_charge.sdd_charge+ship_charge.to_pay_charge+ship_charge.reverse_charge
     if customer.fuel_surcharge_applicable:
        if customer.fuelsurcharge_set.all():
            fsurcharge = customer.fuelsurcharge_set.all()[0]
            if fsurcharge.fuelsurchargezone_set.filter( f_zone_org = org_zone, f_zone_dest = dest_zone):
                fsurcharge = fsurcharge.fuelsurchargezone_set.filter( f_zone_org = org_zone, f_zone_dest = dest_zone)[0]
            if fsurcharge.flat_fuel_surcharge:
                freight_surcharge = (fsurcharge.flat_fuel_surcharge * ffreight_charge)/100
            elif fsurcharge.fuelsurcharge_min_rate == 0 and fsurcharge.max_fuel_surcharge == 0 and fsurcharge.flat_fuel_surcharge == 0:
                freight_surcharge = 0
            else:
                br = Brentrate.objects.all().order_by('-todays_date')[:1][0]
                if br.todays_rate > fsurcharge.fuelsurcharge_min_fuel_rate:
                    fuel_surcharge_percentage = (((br.todays_rate - fsurcharge.fuelsurcharge_min_fuel_rate)/br.fuel_cost_increase * br.percentage_increase) + fsurcharge.fuelsurcharge_min_rate) * ffreight_charge
                    if fuel_surcharge_percentage < fsurcharge.max_fuel_surcharge:
                        freight_surcharge = ((fuel_surcharge_percentage * ffreight_charge)/100)
                    else:
                        freight_surcharge = ((fsurcharge.max_fuel_surcharge * ffreight_charge)/100)
                else:
                    freight_surcharge = ((fsurcharge.fuelsurcharge_min_rate * ffreight_charge)/100)

        else:
           pass
     else:
        freight_surcharge = 0
     shipment_charges = Order_price.objects.get(shipment = shipment)
     shipment_charges.fuel_surcharge = freight_surcharge
     bill_history_obj.fuel_surcharge = freight_surcharge
     bill_history_obj.save()
     if not cutoff_passed:
         shipment_charges.save()

def rto_charge(shipment):
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

    max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
    customer = shipment.shipper
    chargeable_weight = max_weight_dimension*1000
    if shipment.rts_status==1:
        try:
          freight_slabs = FreightSlab.objects.filter(customer=customer, range_from__lte=chargeable_weight).order_by("range_from")
     #     print freight_slabs[0], customer.return_to_origin
          rto_charge = (max_weight_dimension / freight_slabs[0]) * customer.return_to_origin
        except:
          rto_charge=0
    else:
        rto_charge = 0
    shipment_charges = Order_price.objects.get(shipment = shipment)
    shipment_charges.rto_charge = rto_charge
    bill_history_obj.rto_charge = rto_charge
    bill_history_obj.save()
    if not cutoff_passed:
        shipment_charges.save()

def to_pay(shipment):
     max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
     customer = shipment.shipper
     chargeable_weight = max_weight_dimension*1000
     if shipment.pickup.to_pay == 1:
        freight_slabs = FreightSlab.objects.filter(customer=customer, range_from__lte=chargeable_weight).order_by("range_from")
        to_pay_charge = (max_weight_dimension / freight_slabs[0]) * customer.to_pay_charge
     else:
        to_pay_charge = 0
     shipment_charges = Order_price.objects.get(shipment = shipment)
     shipment_charges.to_pay_charge = to_pay_charge
     shipment_charges.save()

def vchc(shipment):
     customer = shipment.shipper
     vchc_min = customer.vchc_min
     vchc_rate = customer.vchc_rate
     vchc_min_amnt_applied = customer.vchc_min_amnt_applied

     if not shipment.declared_value:
         shipment.declared_value=shipment.collectable_value
     if shipment.declared_value/shipment.actual_weight >= vchc_min_amnt_applied:
          vchc_charges = float(shipment.declared_value/shipment.actual_weight - vchc_min_amnt_applied) * float(shipment.actual_weight) * float(vchc_rate/100)
          if vchc_charges < vchc_min:
             vchc_charges = vchc_min
     else:
          vchc_charges = 0
     shipment_charges = Order_price.objects.get(shipment = shipment)
     shipment_charges.valuable_cargo_handling_charge = vchc_charges
     shipment_charges.save()


def cod_charge(shipment):
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

     customer = shipment.shipper
     org_zone = shipment.pickup.service_centre.city.zone
     dest_zone = shipment.original_dest.city.zone


     if shipment.product_type.lower() == "cod":
        #if shipment.rts_status == 1:
        #   cod_charges = CODCharge.objects.get(shipment__airwaybill_number=shipment.ref_airwaybill_number).cod_charge   
        #elif customer.flat_cod_amt:
        #   cod_charges = customer.flat_cod_amt

         if customer.flat_cod_amt:
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



#    if shipment.product_type.lower() == "cod":
#        if customer.flat_cod_amt:
#           cod_charges = customer.flat_cod_amt
#        else :
#             if CashOnDeliveryZone.objects.filter(customer=customer, start_range__lte=shipment.collectable_value, end_range__gte=shipment.collectable_value, c_zone_org = org_zone, c_zone_dest = dest_zone):
#                   cods = CashOnDeliveryZone.objects.filter(customer=customer, start_range__lte=shipment.collectable_value, end_range__gte=shipment.collectable_value, c_zone_org = org_zone, c_zone_dest = dest_zone)[0]
#                   if cods.flat_COD_charge:
#                     cod_charges = cods.flat_COD_charge
#                   else:
#                     cod_charges = shipment.collectable_value * (cods.COD_service_charge/100)
#                     if cod_charges < cods.minimum_COD_charge:
#                         cod_charges = cods.minimum_COD_charge

#             elif CashOnDelivery.objects.filter(customer=customer, start_range__lte=shipment.collectable_value, end_range__gte=shipment.collectable_value):
#                   cod = CashOnDelivery.objects.filter(customer=customer, start_range__lte=shipment.collectable_value, end_range__gte=shipment.collectable_value).order_by("-COD_service_charge", "-flat_COD_charge")[:1][0]
#                   if cod.flat_COD_charge:
#                      cod_charges = cod.flat_COD_charge
#                   else:
#                       cod_charges = shipment.collectable_value * (cod.COD_service_charge/100)
#                       if cod_charges < cod.minimum_COD_charge:
#                          cod_charges = cod.minimum_COD_charge
#             else:
#                 cod_charges = 0
#        bill_history_obj.cod_charge = cod_charges
#        bill_history_obj.save()
#        if CODCharge.objects.filter(shipment=shipment):
#            cod_charge_obj = CODCharge.objects.get(shipment=shipment)
#            cod_charge_obj.cod_charge = cod_charges
#            cod_charge_obj.updated_on = now
#            if not cutoff_passed:
#                cod_charge_obj.save()
#        else:
#            CODCharge.objects.create(shipment=shipment, cod_charge=cod_charges)


def bkup_cod_charge(shipment):
     customer = shipment.shipper
     if shipment.product_type.lower() == "cod":
         if customer.flat_cod_amt:
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
         return cod_charges
      #   if CODCharge.objects.filter(shipment=shipment):
      #       cod_charge_obj = CODCharge.objects.get(shipment=shipment)
      #       cod_charge_obj.cod_charge = cod_charges
      #       cod_charge_obj.updated_on = now
      #       cod_charge_obj.save()
      #   else:
      #       CODCharge.objects.create(shipment=shipment, cod_charge=cod_charges)


def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)



def api_auth(request):
    if request.GET.get('username') or request.POST.get('username') :
        #customer_api = CustomerAPI.objects.get(username=request.POST['username'])
        if request.GET.get('username'):
            username = request.GET.get('username')
            password = request.GET.get('password')
        if request.POST.get('username'):
            username = request.POST.get('username')
            password = request.POST.get('password')
        try:
            customer_api = CustomerAPI.objects.get(username=username)
            if customer_api.password == password:
                if customer_api.ipaddress != "0":
                    ip_list    =  customer_api.ipaddress.split(",")
                    request_ip =  request.META.get('REMOTE_ADDR').strip()
                    if request_ip in ip_list:
                        return customer_api
                    else:
                        return False
                else:
                    return customer_api
        except CustomerAPI.DoesNotExist:
            return False
    else:
        return False

def price_updated(shipment):
  #cutoff_date = get_latest_billing_cutoff()
  today = datetime.datetime.now()
  cutoff_passed = is_cutoff_passed(shipment)
  #print 'setting chargeable weight and shipment date...'
  shipment.set_chargeable_weight
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
        Shipment.objects.filter(pk=order.id).\
                         update(actual_weight=order.actual_weight,
                                volumetric_weight=order.volumetric_weight)

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
     add_to_shipment_queue(shipment.airwaybill_number)
     return True
     customer = shipment.shipper
     subcustomer=shipment.pickup.subcustomer_code

     sdd_charge = 0
     freight_charge = 0
     chargeable_weight = max_weight_dimension*1000
     # add shipments chargeable weight here.
     product_type = "all"
     freight_slabs = FreightSlab.objects.filter(customer=customer,
         range_from__lte=chargeable_weight).order_by("range_from")

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
            #print fs_zones
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
   #  if not cutoff_passed:
   #     shipment_charges.save()

     if (customer.reverse_charges and shipment.reverse_pickup == 1):
             reverse_charge = customer.reverse_charges
     else:
             reverse_charge = 0

  #   shipment_charges.reverse_charge = reverse_charge
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


def sal_exception(request):
    sal = ShipmentAtLocation.objects.filter().exclude(status = 1).order_by('-date')
    mismatch_sal = []
    for a in sal:
        if a.status == 0:
             stat = "Not Closed"
        elif a.status == 2:
             stat = "Count Mismatch"
        u = (a.id, a.origin, stat, a.date)
        mismatch_sal.append(u)

    subject = "Exception Report for SAL "
    if sal:
         email_msg = "Given below are the mismatch SAL id and their service centre:\n"+"\n".join(['%s, %s, %s, %s' % (a[0], a[1], a[2], a[3]) for a in mismatch_sal])
       # email_msg = "<html><body>Following airwaybill were not verified into the system:<br><table><tr><th>Air Waybill Number</tr></th></table></body></html>"
         to_email = "exception@ecomexpress.in"
         from_email = "support@ecomexpress.in"
         send_mail(subject,email_msg,from_email,[to_email])

def history_update(shipment, status, request, remarks="", sc=None,reason_code=None):
    """
    This file is modified to add bag history to shipment history.
    """
    employee_code = request.user.employeemaster
    if not sc:
       current_sc = request.user.employeemaster.service_centre
    else:
       current_sc = sc  
    status = status
    remarks = remarks
    if not shipment.added_on:
       shipment.added_on = now
    upd_time = shipment.added_on
    monthdir = upd_time.strftime("%Y_%m")
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
    shipment_history.objects.create(
        shipment=shipment, status=status, employee_code=employee_code,
        current_sc=current_sc, expected_dod=shipment.expected_dod, 
        reason_code=reason_code, remarks=remarks, 
    )
    ShipmentExtension.objects.filter(shipment_id=shipment.id).update(
        status_bk=status, current_sc_bk=current_sc, 
        remarks=remarks, updated_on=now)

    reason = reason_code.code if reason_code else ''

    ShipmentBagHistory.objects.update_ship_history(
        shipment.airwaybill_number, status, employee_code, reason, remarks)

def update_pricing(shipment):
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

     #min_ratio = max_weight_dimension/order.collectable_value
     #shipment = order
  #   if not shipment.original_dest:
  #     upd_time = shipment.added_on
  #     monthdir = upd_time.strftime("%Y_%m")
  #     shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
  #     destination=shipment_history.objects.filter(shipment=shipment, status=6).order_by("updated_on")[0]
  #     shipment.original_dest = destination.current_sc
  #     shipment.save()
     shipper = Customer.objects.get(id=shipment.shipper.id)
     org_zone = shipment.pickup.service_centre.city.zone
     if shipment.original_dest:
         dest_zone = shipment.original_dest.city.zone
     else:
         subject = "RTS pricing for shipment not having original destination"
         from_email = "support@ecomexpress.in"
         to_email = ("samar@prtouch.com", "jignesh@prtouch.com")
         email_msg = str(shipment.airwaybill_number)
         send_mail(subject,email_msg,from_email,to_email)
         dest_zone = shipment.service_centre.city.zone
     customer = shipment.pickup.customer_code
     subcustomer=shipment.pickup.subcustomer_code

     freight_charge = 0
     chargeable_weight = max_weight_dimension*1000
     freight_slabs = FreightSlab.objects.filter(customer=customer, range_from__lte=chargeable_weight).order_by("range_from")
     for freight_slab in freight_slabs:
        if chargeable_weight:
            if chargeable_weight > freight_slab.range_to:
                chargeable_weight = chargeable_weight - freight_slab.range_to
                weight_for_this_slab = freight_slab.range_to
            else:
                weight_for_this_slab = chargeable_weight
                chargeable_weight = 0
            fs_zones = FreightSlabZone.objects.filter(freight_slab = freight_slab, zone_org = org_zone, zone_dest = dest_zone).order_by("-rate_per_slab")
            if fs_zones:
               fs_zone = fs_zones[0]
               freight_rate = fs_zone.rate_per_slab
            else:
               freight_rate = freight_slab.weight_rate
            freight_charge = freight_charge + ceil(weight_for_this_slab / float(freight_slab.slab)) * freight_rate

     if Order_price.objects.filter(shipment = shipment):

          shipment_charges = Order_price.objects.get(shipment = shipment)
          shipment_charges.freight_charge = freight_charge
          shipment_charges.save()
     else:
          shipment_charges = Order_price.objects.create(shipment = shipment, freight_charge = freight_charge)
          shipment_charges.save()



     sdl_charge = 0
     if Pincode.objects.filter(pincode = shipment.pincode):
        pincode = Pincode.objects.get(pincode = shipment.pincode)
        if pincode.sdl:
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


            if Order_price.objects.filter(shipment = shipment):

                 shipment_charges = Order_price.objects.get(shipment = shipment)
                 shipment_charges.sdl_charge = sdl_charge
                 shipment_charges.save()
            else:
                 shipment_charges = Order_price.objects.create(shipment = shipment, sdl_charge = sdl_charge)
                 shipment_charges.save()


     if customer.fuel_surcharge_applicable:
        if customer.fuelsurcharge_set.all():
            fsurcharge = customer.fuelsurcharge_set.all()[0]
            if fsurcharge.fuelsurchargezone_set.filter( f_zone_org = org_zone, f_zone_dest = dest_zone):
                fsurcharge = fsurcharge.fuelsurchargezone_set.filter( f_zone_org = org_zone, f_zone_dest = dest_zone)[0]
            if fsurcharge.flat_fuel_surcharge:
                freight_surcharge = (fsurcharge.flat_fuel_surcharge * freight_charge) / 100
            elif fsurcharge.fuelsurcharge_min_rate == 0 and fsurcharge.max_fuel_surcharge == 0 and fsurcharge.flat_fuel_surcharge == 0:
                freight_surcharge = 0
            else:
                br = Brentrate.objects.all().order_by('-todays_date')[:1][0]
                if br.todays_rate > fsurcharge.fuelsurcharge_min_fuel_rate:
                    fuel_surcharge_percentage = (((br.todays_rate - fsurcharge.fuelsurcharge_min_fuel_rate)/br.fuel_cost_increase * br.percentage_increase) + fsurcharge.fuelsurcharge_min_rate)
                    if fuel_surcharge_percentage < fsurcharge.max_fuel_surcharge or fsurcharge.max_fuel_surcharge == 0:
                        freight_surcharge = ((fuel_surcharge_percentage * freight_charge)/100)
                    else:
                        freight_surcharge = ((fsurcharge.max_fuel_surcharge * freight_charge)/100)
                else:
                    freight_surcharge = ((fsurcharge.fuelsurcharge_min_rate * freight_charge)/100)

        else:
           pass
     else:
        freight_surcharge = 0

     shipment_charges.fuel_surcharge = freight_surcharge
     shipment_charges.save()


     if shipment.rts_status==1:
        try:
          rto_charge = (max_weight_dimension / fs.slab) * customer.return_to_origin
        except:
          rto_charge=0
     else:
        rto_charge = 0

     shipment_charges.rto_charge = rto_charge
     shipment_charges.save()

     if shipment.pickup.to_pay == 1:
        to_pay_charge = (max_weight_dimension / fs.slab) * customer.to_pay_charge
     else:
        to_pay_charge = 0

     shipment_charges.to_pay_charge = to_pay_charge
     shipment_charges.save()

     vchc_min = customer.vchc_min
     vchc_rate = customer.vchc_rate
     vchc_min_amnt_applied = customer.vchc_min_amnt_applied

     if not shipment.declared_value:
         shipment.declared_value=shipment.collectable_value
     if shipment.declared_value/shipment.actual_weight >= vchc_min_amnt_applied:
          vchc_charges = float(shipment.declared_value/shipment.actual_weight - vchc_min_amnt_applied) * float(shipment.actual_weight) * float(vchc_rate/100)
          if vchc_charges < vchc_min:
             vchc_charges = vchc_min
     else:
          vchc_charges = 0

     shipment_charges.valuable_cargo_handling_charge = vchc_charges
     shipment_charges.save()

     if shipment.product_type.lower() == "cod":
         if customer.flat_cod_amt:
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

         if CODCharge.objects.filter(shipment=shipment):
             cod_charge_obj = CODCharge.objects.get(shipment=shipment)
             cod_charge_obj.cod_charge = cod_charges
             cod_charge_obj.updated_on = now
             cod_charge_obj.save()
         else:
             CODCharge.objects.create(shipment=shipment, cod_charge=cod_charges)

     return True

def rts_pricing(shipment):
    price_updated(shipment)
    return True
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


def admin_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.employeemaster.employee_code in [ '124','12114','10004']:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner

def update_weights(function):
   def _inner(request, *args, **kwargs):
      if not request.user.employeemaster.employee_code in ['124','12114','10004','10320','10500']:
           raise PermissionDenied
      return function(request, *args, **kwargs)
   return _inner

def admin_and_others(function):
    def _inner(request, *args, **kwargs):
        if not request.user.employeemaster.employee_code in ['12115','10363','124','217','119','12114','10004','10320','10500']:
              raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner

def password_reset(function):
    def _inner(request, *args, **kwargs):
        if not request.user.employeemaster.employee_code in ['11446','124','10904','10549','14239','11231', '10004']:
              raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner 

def reverse_shipment_closure(function):
    def _inner(request, *args, **kwargs):
         if not request.user.employeemaster.employee_code in ['124','10320','63392', '11285', '11324']:
              raise PermissionDenied
         return function(request, *args, **kwargs)
    return _inner    

def developers_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.employeemaster.employee_code in ['32231','124','10943','10320', '12114','26388', '12534']:
              raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner

def director_only(function):
    def _inner(request, *args, **kwargs):
        if request.user.employeemaster.user_type not in ['Director', 'Sr Manager']:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner


def chargeable_weight(shipment):
     order = shipment
     if MinActualWeight.objects.filter(customer=order.shipper):
        min_actual_weight = MinActualWeight.objects.get(customer=order.shipper).weight
     else:
        min_actual_weight = 0

     max_weight_dimension = max(float(order.volumetric_weight), order.actual_weight)
     if min_actual_weight:
        if max_weight_dimension <= min_actual_weight:
            max_weight_dimension =  order.actual_weight
        else:
            max_weight_dimension = max(float(order.volumetric_weight), order.actual_weight)
     else:
        max_weight_dimension = max(float(order.volumetric_weight), order.actual_weight)
     return max_weight_dimension

def sdl_charge(shipment):
    cutoff_date = get_latest_billing_cutoff()
    today = datetime.datetime.now()
    cutoff_passed = is_cutoff_passed(shipment)
    bill_history_obj = get_bill_history_model(shipment)
    bill_history_obj.shipment = shipment
    bill_history_obj.subcustomer = shipment.pickup.subcustomer_code
    bill_history_obj.collectable_value = shipment.collectable_value
    bill_history_obj.inscan_date = shipment.inscan_date
    bill_history_obj.original_dest = shipment.original_dest

    sdl_charge = 0
    if shipment:
        max_weight_dimension = chargeable_weight(shipment)
        customer = shipment.shipper
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


        if Order_price.objects.filter(shipment = shipment):

             shipment_charges = Order_price.objects.get(shipment = shipment)
             shipment_charges.sdl_charge = sdl_charge
             bill_history_obj.sdl_charge = sdl_charge
             bill_history_obj.save()
             if not cutoff_passed and  not shipment.billing:
                     shipment_charges.save()

def chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start+n]



def price_updated_rev(shipment):
  #add_to_shipment_queue(shipment.airwaybill_number)
  #cutoff_date = get_latest_billing_cutoff()
  today = datetime.datetime.now()
  cutoff_passed = is_cutoff_passed(shipment)
  cutoff_passed = False
  bill_history_obj = get_bill_history_model(shipment)
  bill_history_obj.shipment = shipment
  bill_history_obj.subcustomer = shipment.pickup.subcustomer_code
  bill_history_obj.collectable_value = shipment.collectable_value
  bill_history_obj.inscan_date = shipment.inscan_date
  bill_history_obj.original_dest = shipment.original_dest
  #print 'setting chargeable weight and shipment date...'
  shipment.chargeable_weight = shipment.set_chargeable_weight
  shipment.set_shipment_date
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
         Shipment.objects.filter(id=shipment.id).update(original_dest=shipment.service_centre)
    # dest_zone = shipment.original_dest.city.zone
         dest_city = shipment.service_centre.city

     customer = shipment.pickup.customer_code
     subcustomer=shipment.pickup.subcustomer_code

     sdd_charge = 0
     freight_charge = 0
     chargeable_weight = max_weight_dimension*1000
     # add shipments chargeable weight here.
     product_type = "all"
     freight_slabs = FreightSlab.objects.filter(customer=customer,
         range_from__lte=chargeable_weight).order_by("range_from")

     #### City Wise Charges
     freight_slabs_city = FreightSlabCity.objects.filter(customer=customer,
                                                      city_org = shipment.pickup.service_centre.city,
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
       if Pincode.objects.filter(pincode = shipment.pincode):
          pincode = Pincode.objects.get(pincode = shipment.pincode)
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

     if customer.fuel_surcharge_applicable:
        if customer.fuelsurcharge_set.all():
            fsurcharge = customer.fuelsurcharge_set.all()[0]
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
                    fuel_surcharge_percentage = ((ceil((br.todays_rate - fsurcharge.fuelsurcharge_min_fuel_rate)/br.fuel_cost_increase) * br.percentage_increase) + fsurcharge.fuelsurcharge_min_rate)
                    if fuel_surcharge_percentage < fsurcharge.max_fuel_surcharge or fsurcharge.max_fuel_surcharge == 0:
                        freight_surcharge = ((fuel_surcharge_percentage * tot_charge)/100)
                    else:
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


def rts_pricing_rev(shipment):
    price_updated_rev(shipment)

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

    op = Order_price.objects.update_or_create(shipment = shipment, defaults={'freight_charge':freight_rate, 'fuel_surcharge' : fuel_surcharge, 'sdl_charge':0})
    bill_history_obj.save()
    return True


def rts_pricing_rev_bk1(shipment):
    price_updated_rev(shipment)

    # updated:jinesh
    cutoff_date = get_latest_billing_cutoff()
    today = datetime.datetime.now()
    cutoff_passed = is_cutoff_passed(shipment)
    cutoff_passed = False
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

def shipment_mail(shipment):
         subject = "Shipment: %s updated with %s code"%(shipment.airwaybill_number, shipment.reason_code)
         from_email = "support@ecomexpress.in"
         to_email = ('surinderp@ecomexpress.in','dinesh.thonur@ecomexpress.in','jacobm@ecomexpress.in',"onkar@prtouch.com","sravank@ecomexpress.in", "sunily@ecomexpress.in", "pawant@ecomexpress.in", "mohinderk@ecomexpress.in", "pravinp@ecomexpress.in", "sandeepv@ecomexpress.in", "salima@ecomexpress.in")
         email_msg = subject
         send_mail(subject,email_msg,from_email,to_email)

def shipment_transit_time(awb,msg= None):
         subject = "Shipment: %s updated with no transit time %s"%(awb, msg)
         from_email = "support@ecomexpress.in"
         to_email = ("samar@prtouch.com",)
         email_msg = subject
         send_mail(subject,email_msg,from_email,to_email)

def validate_pickup_record():
          return True

def get_subcustomer(shid):
    shipper=Shipper.objects.get(id=shid)
    address=""
    add=shipper.address 
    if add.address1 is not None:
       address = address + add.address1    
    if add.address2 is not None:
       address = address + add.address2
    if add.address3 is not None:
       address = address + add.address3
    if add.address4 is not None:
       address = address + add.address4  
    return address,add.pincode

def create_vendor(name,address,phone,pincode,customer_code,return_pincode=0):
    #customer_code = int(customer_code)
    customer=Customer.objects.filter(code=customer_code)
    #return_pincode = int(return_pincode)
    return_pincode = str(return_pincode)
    #return HttpResponse(customer_code)
    if customer:
       customer = customer[0]
       pin = Pincode.objects.get(pincode=pincode)
       city=pin.service_center.city
       state = city.state
       address  =  Address.objects.create(city=city,state=state,address1=address,phone=phone,pincode=pincode)
       shipper = Shipper.objects.create(address=address,customer=customer,name=name)
       ShipperMapping.objects.create(shipper=shipper,forward_pincode=pincode,return_pincode=return_pincode)
       return shipper       

def get_vendor(name,address,phone,pincode,customer_code,return_pincode=0):
    #from django.http import HttpResponse
    #tmp = ""
    #return HttpResponse(name,address,phone,pincode,customer_code,return_pincode)
    #subcustomer=None
    #customer_code = int(customer_code)
    customer_code = str(customer_code)
    #pincode=int(pincode)
    pincode = str(pincode)
    shipper= Shipper.objects.filter(name=name,address__pincode=pincode,customer__code=customer_code)
    if shipper:
        subcustomer = shipper[0].id
       # for ship in shipper:
          # u=get_subcustomer(ship)
           #if u[0] == address and u[1] == pincode:
             #id=shipper[0].id
             #break;
    else:
        subcust =  create_vendor(name,address,phone,pincode,customer_code,return_pincode)
        if subcust :
           subcustomer = subcust.id
    return subcustomer


