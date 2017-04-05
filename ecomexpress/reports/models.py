import datetime
from django.db import models

from service_centre.models import Bags, Shipment, DeliveryOutscan, Order_price
from service_centre.models import CODCharge

# Create your models here.

class DaywiseCustomerReport(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30)
    shipment_count = models.BigIntegerField()
    shipment_date = models.DateTimeField(null=True)

class GenericQuery(models.Model):
    airwaybill_number = models.BigIntegerField(primary_key=True, db_index=True)
    order_number = models.CharField(max_length=80, null=True, blank=True)
    product_type = models.ForeignKey('customer.Product', null=True, blank=True, db_index=True)
    weight = models.FloatField(default=0.0, null=True, blank=True)
    vol_weight = models.FloatField(default=0.0, null=True, blank=True)
    cod_amount = models.FloatField(default=0.0, null=True, blank=True)
    declared_value = models.FloatField(default=0.0, null=True, blank=True)
    origin = models.ForeignKey('location.ServiceCenter', null=True, blank=True)
    customer = models.ForeignKey('customer.Customer', null=True, blank=True)
    subcustomer = models.ForeignKey('customer.Shipper', null=True, blank=True)
    consignee = models.CharField(max_length=100, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    pickup_date = models.DateTimeField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=80, null=True, blank=True)
    expected_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True, db_index=True)
    remarks = models.TextField(null=True, blank=True)
    reason_code = models.IntegerField(max_length=5, null=True, blank=True, db_index=True)
    reason = models.TextField(max_length=80, null=True, blank=True)
    received_by = models.CharField(max_length=200, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True, db_index=True)
    delivery_time = models.TimeField(null=True, blank=True)
    ref_airwaybill_number = models.BigIntegerField(null=True, blank=True)
    return_status = models.CharField(max_length=80, null=True, blank=True)
    return_updated_on = models.DateTimeField(null=True, blank=True, db_index=True)
    rts_status = models.IntegerField(max_length=1, null=True, blank=True, db_index=True)
    rto_status = models.IntegerField(max_length=1, null=True, blank=True, db_index=True)
    prud_date = models.DateTimeField(null=True, blank=True, db_index=True)
    first_attempt_status = models.CharField(max_length=80, null=True, blank=True, db_index=True)
    first_attempt_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True

class GenericQuery_2014_01(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_01')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_01')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_02(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_02')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_02')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_03(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_03')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_03')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_04(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_04')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_04')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_05(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_05')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_05')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_06(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_06')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_06')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_07(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_07')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_07')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_08(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_08')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_08')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_09(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_09')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_09')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_10(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_10')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_10')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_11(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_11')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_11')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2014_12(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_14_12')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_14_12')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_01(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_01')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_01')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_02(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_02')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_02')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_03(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_03')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_03')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_04(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_04')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_04')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_05(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_05')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_05')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_06(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_06')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_06')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_07(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_07')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_07')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_08(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_08')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_08')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_09(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_09')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_09')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_10(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_10')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_10')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_11(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_11')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_11')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2015_12(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_15_12')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_15_12')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_01(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_01')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_01')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_02(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_02')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_02')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_03(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_03')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_03')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_04(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_04')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_04')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_05(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_05')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_05')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_06(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_06')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_06')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_07(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_07')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_07')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_08(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_08')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_08')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_09(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_09')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_09')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_10(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_10')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_10')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_11(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_11')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_11')
    update_on = models.DateTimeField(auto_now=True)

class GenericQuery_2016_12(GenericQuery):
    sub_customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='subcustomer_16_12')
    destination = models.ForeignKey('location.ServiceCenter', null=True, blank=True, related_name='generic_destination_16_12')
    update_on = models.DateTimeField(auto_now=True)

class CustomerRemittance(models.Model):
    customer_code = models.IntegerField(max_length=7)
    customer_id = models.IntegerField(max_length=3)
    current_day = models.IntegerField(max_length=1)
    to_day = models.IntegerField(max_length=1)

class DailyUndeliveredCount(models.Model):
    customer=models.ForeignKey('customer.Customer')
    service_center=models.ForeignKey('location.ServiceCenter')
    undelivered_count = models.BigIntegerField()
    date = models.DateField(null=True, blank=True)


class ShipmentBagHistoryManager(models.Manager):
    """
           1 - bag created (SC) - 1
           2 - shipment added (SC)
           3 - bag closed (SC) - 2
           4 - added to connection (SC) - 6
           5 - bag delinked from  connection (SC) - 5
           6 - connection closed (SC) -

           7 - bag created (HUB) - 7
           8 - shipment added (HUB)
           9 - bag closed (HUB)
           10 - added to connection (HUB)
           11 - bag delinked from  connection (HUB)
           12 - connection closed (HUB)

           14 - bag scanned (DC) - 14
           15 - bag scanned (HUB) 15

           16 - Mass updation - 16
           17 - inscan shipment at DC without shipment inscan
           18 - debagged at hub - direct shipment inscan without bag inscan
    """

    def add_record(self, awb, emp):
        ship_history = ShipmentBagHistory.objects.get_or_create(awb=awb)
        ship = Shipment.objects.get(airwaybill_number=awb)
        now = datetime.datetime.now()
        vendor_name, subcustomer_code = \
            (ship.pickup.subcustomer_code.name, ship.pickup.subcustomer_code.id) \
            if ship.pickup.subcustomer_code else ('', '')
        
        try:
            ship_history = ShipmentBagHistory.objects.get(awb=ship.airwaybill_number)
            from utils import get_shipment_history
            sc = get_shipment_history(ship).objects.filter(shipment=ship, status=0)[0].current_sc
            ship_added_on_sc=sc.center_shortcode
            ship_origin_city=sc.city.city_name
        except IndexError:
            ship_added_on_sc = ship.pickup.service_centre.center_shortcode
            ship_origin_city = ship.pickup.service_centre.city.city_name

        ShipmentBagHistory.objects.filter(awb=awb).update(
            record_update=now,
            ship_added_on_sc=ship_added_on_sc,
            ship_added_on_time=ship.added_on,
            ship_original_dest=ship.original_dest.center_shortcode,
            ship_rts_status=ship.rts_status,
            ship_shipper_name=ship.shipper.name,
            vendor_name=vendor_name,
            ship_shipper_code=ship.shipper.code,
            ship_rvp_flag=ship.reverse_pickup,
            ship_origin_city=ship_origin_city,
            ship_dest_city=ship.original_dest.city.city_name,
            collectable_value= ship.collectable_value,
            chargeable_weight=ship.chargeable_weight,
            subcustomer_code=subcustomer_code)
        ship_history = ShipmentBagHistory.objects.get(awb=awb)
        return ship_history

    def update_bill_records(self, awb, emp):
        ship = Shipment.objects.get(airwaybill_number=awb)
        try:
            ship_history = ShipmentBagHistory.objects.get(awb=ship.airwaybill_number)
        except ShipmentBagHistory.DoesNotExist:
            ship_history = ShipmentBagHistory.objects.add_record(ship.airwaybill_number, emp)
        try:
            op = ship.order_price_set.get()
            now = datetime.datetime.now()
            try:
                cod = ship.codcharge_set.get().cod_charge
            except CODCharge.DoesNotExist:
                cod = 0

            fuel_surcharge = op.fuel_surcharge if op.fuel_surcharge else 0
            valuable_cargo_handling_charge = op.valuable_cargo_handling_charge if op.valuable_cargo_handling_charge else 0
            to_pay_charge = op.to_pay_charge if op.to_pay_charge else 0
            rto_charge = op.rto_charge if op.rto_charge else 0
            sdl_charge = op.sdl_charge if op.sdl_charge else 0
            sdd_charge = op.sdd_charge if op.sdd_charge else 0
            reverse_charge = op.reverse_charge if op.reverse_charge else 0
            cod_charge = cod if cod else 0
            total_charge = sum([freight_charge, fuel_surcharge,
                    valuable_cargo_handling_charge, to_pay_charge, rto_charge,
                    sdl_charge, sdd_charge, reverse_charge])
            if ship.rts_status == 1:
                total_charge = total_charge - cod_charge
            else:
                total_charge = total_charge + cod_charge

            ShipmentBagHistory.objects.filter(awb=awb).update(
                freight_charge = op.freight_charge,
                fuel_surcharge = op.fuel_surcharge,
                valuable_cargo_handling_charge = op.valuable_cargo_handling_charge,
                to_pay_charge = op.to_pay_charge,
                rto_charge = op.rto_charge,
                sdl_charge = op.sdl_charge,
                sdd_charge = op.sdd_charge,
                reverse_charge = op.reverse_charge,
                cod_charge = cod_charge,
                total_charge = total_charge,
                product_name = ship.shipext.product.product_name,
                expected_dod = ship.expected_dod)

        except Order_price.DoesNotExist:
            pass

    def update_bag_records(self, bag, status, emp, updated_on=None):
        if updated_on:
            now = updated_on
        else:
            now = datetime.datetime.now()
        for ship in bag.ship_data.all():
            try:
                ship_history = ShipmentBagHistory.objects.get(awb=ship.airwaybill_number)
            except ShipmentBagHistory.DoesNotExist:
                ship_history = ShipmentBagHistory.objects.add_record(ship.airwaybill_number, emp)

            if status == 2: # bag closed at sc
                ShipmentBagHistory.objects.filter(
                    awb=ship.airwaybill_number
                ).update(
                    last_added_bag_number=bag.bag_number
                )
                if ship_history.bag_first_close_time is None:
                    ShipmentBagHistory.objects.filter(
                        awb=ship.airwaybill_number
                    ).update(
                        bag_first_close_time=now,
                        first_added_bag_number=bag.bag_number,
                        bag_first_close_sc=emp.service_centre.center_shortcode
                    )

            elif status == 6: # bag included in connection at sc
                if not ship_history.bag_first_sc_connection_time:
                    ShipmentBagHistory.objects.filter(
                        awb=ship.airwaybill_number
                    ).update(bag_first_sc_connection_time=now)
            elif status == 9: # bag closed at hub
                ShipmentBagHistory.objects.filter(
                    awb=ship.airwaybill_number
                ).update(last_added_bag_number=bag.bag_number)
            elif status == 12: # bag included in connection at hub: connection close
                if not ship_history.bag_first_hub_connection_time:
                    ShipmentBagHistory.objects.filter(
                        awb=ship.airwaybill_number
                    ).update(bag_first_hub_connection_time=now)
                # bag latest hub connection time
                ShipmentBagHistory.objects.filter(
                    awb=ship.airwaybill_number
                ).update(bag_latest_hub_connection_time=now)
            elif status == 14: # bag scanned at DC
                ShipmentBagHistory.objects.filter(
                    awb=ship.airwaybill_number
                ).update(
                    bag_latest_inscan_dc_sc=emp.service_centre.center_shortcode,
                    bag_latest_inscan_dc_time=now, ship_latest_debag_time=now,
                )
            elif status == 15: # bag scanned at HUB
                if ship_history.bag_first_hub_inscan_time is None:
                    ShipmentBagHistory.objects.filter(
                        awb=ship.airwaybill_number
                    ).update(
                        bag_first_hub_inscan_time=now,
                        bag_first_hub_inscan_sc=emp.service_centre.center_shortcode,
                        bag_latest_inscan_hub_time=now,
                        bag_latest_inscan_hub_sc=emp.service_centre.center_shortcode,
                   )
                ShipmentBagHistory.objects.filter(
                    awb=ship.airwaybill_number
                ).update(
                    bag_latest_inscan_hub_time=now,
                    bag_latest_inscan_hub_sc=emp.service_centre.center_shortcode,
                )
            ShipmentBagHistory.objects.filter(awb=ship.airwaybill_number).update(
                record_update=now, ship_current_status=ship.status)
        return True

    def update_outscan_details(self, awb):
        ship = Shipment.objects.get(airwaybill_number=awb)
        outscans = ship.deliveryoutscan_set.all()
        if not outscans:
            return False

        first_outscan = outscans.order_by('id')[0]
        last_outscan = outscans.order_by('-id')[0]
        no_outscan = outscans.count()

        ship_latest_outscan_emp = last_outscan.employee_code.employee_code
        ship_first_outscan_time_dc = first_outscan.added_on
        ship_last_outcan_time_dc = last_outscan.added_on
        ship_latest_debag_sc = last_outscan.employee_code.service_centre.center_shortcode

        ShipmentBagHistory.objects.filter(awb=awb).update(
            ship_first_outscan_time_dc=ship_first_outscan_time_dc,
            ship_last_outcan_time_dc=ship_last_outcan_time_dc,
            ship_latest_outscan_emp=ship_latest_outscan_emp,
            ship_latest_debag_sc=ship_latest_debag_sc,
            no_outscan=no_outscan)
        return True


    def update_ship_history(self, awb, status, emp, reason_code, remarks=None, updated_on=None):
        if not updated_on:
            now = datetime.datetime.now()
        else:
            now = updated_on

        try: #last_removed_bag_number
            hist = ShipmentBagHistory.objects.get(awb=awb)
        except ShipmentBagHistory.DoesNotExist:
            hist = ShipmentBagHistory.objects.add_record(awb, emp)

        ship = Shipment.objects.get(airwaybill_number=awb)

        # delivery inscan
        if status == 6:
            try:
                last_removed_bag_number = ship.shipment_data.latest('id').bag_number
            except Bags.DoesNotExist:
                last_removed_bag_number = ''

            ShipmentBagHistory.objects.filter(awb=awb).update(
                last_removed_bag_number=last_removed_bag_number,
                ship_latest_inscan_dc_sc=emp.service_centre.center_shortcode
            )
        # delivery outscan
        elif status == 7:
            ShipmentBagHistory.objects.update_outscan_details(awb=awb)
            #try:
                #ship_latest_outscan_emp = ship.deliveryoutscan_set.latest('id').employee_code.employee_code
            #except DeliveryOutscan.DoesNotExist:
                #ship_latest_outscan_emp = ''

            #if not hist.ship_first_outscan_time_dc:
                #ShipmentBagHistory.objects.filter(awb=awb).update(
                    #ship_first_outscan_time_dc=now,
                    #ship_last_outcan_time_dc=now, no_outscan=1,
                    #ship_latest_outscan_emp=ship_latest_outscan_emp
                #)
            #else:
                #ShipmentBagHistory.objects.filter(awb=awb).update(
                    #ship_last_outcan_time_dc=now,
                    #no_outscan=ship.deliveryoutscan_set.count(),
                    #ship_latest_outscan_emp=ship_latest_outscan_emp
                #)
        # delivered or undelivered
        elif status == 8 or status == 9:
            if not hist.ship_first_outscan_time_dc:
                ShipmentBagHistory.objects.update_outscan_details(awb=awb)
            if not hist.ship_first_status_update_reason_code:
                ShipmentBagHistory.objects.filter(awb=awb).update(
                    ship_first_status_update_reason_code=reason_code,
                    ship_first_status_update_time=now,
                    ship_latest_status_update_reason_code=reason_code,
                    ship_latest_status_update_time=now)
            else:
                ShipmentBagHistory.objects.filter(awb=awb).update(
                    ship_latest_status_update_reason_code=reason_code,
                    ship_latest_status_update_time=now)
            if reason_code == 777 or  reason_code == 999:
                ShipmentBagHistory.objects.filter(awb=awb).update(
                    ship_closed_time=now, ship_rts_status=ship.rts_status)
        # mass updation
        elif status == 40:
            ShipmentBagHistory.objects.filter(awb=awb).update(
                mass_updation_status=reason_code,
                mass_updation_hub=emp.service_centre.center_shortcode
            )
        if reason_code:
            ShipmentBagHistory.objects.filter(awb=awb).update(
                ship_current_status_code=reason_code)
            if reason_code == 777:
                ShipmentBagHistory.objects.filter(awb=awb).update(
                    ship_rts_date=now, ship_rts_status=ship.rts_status)
        if remarks:
            ShipmentBagHistory.objects.filter(awb=awb).update(
                ship_remarks=remarks[:200])
        ShipmentBagHistory.objects.filter(awb=awb).update(
            record_update=now, ship_current_status=ship.status)
        return True

class ShipmentBagHistory(models.Model):
    awb = models.BigIntegerField(db_index=True, unique=True)
    ship_added_on_sc = models.CharField(max_length=5, null=True, blank=True, db_index=True)
    ship_added_on_time = models.DateTimeField(null=True, blank=True, db_index=True)
    ship_original_dest = models.CharField(max_length=5, null=True, blank=True, db_index=True)
    ship_manifest_dest = models.CharField(max_length=5, null=True, blank=True, db_index=True)
    ship_rts_status = models.IntegerField(null=True, blank=True, db_index=True)
    ship_shipper_name = models.CharField(max_length=250, null=True, blank=True, db_index=True)
    ship_shipper_code = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    bag_first_close_time = models.DateTimeField(null=True, blank=True, db_index=True)
    bag_first_sc_connection_time = models.DateTimeField(null=True, blank=True, db_index=True)
    bag_first_hub_inscan_time = models.DateTimeField(null=True, blank=True, db_index=True)
    bag_first_hub_inscan_sc = models.CharField(max_length=5, null=True, blank=True, db_index=True)
    bag_latest_inscan_dc_time = models.DateTimeField(null=True, blank=True, db_index=True)
    bag_latest_inscan_dc_sc = models.CharField(max_length=5, null=True, blank=True, db_index=True)
    ship_first_status_update_reason_code = models.CharField(max_length=5, null=True, blank=True, db_index=True)
    ship_first_status_update_time = models.DateTimeField(null=True, blank=True, db_index=True)
    ship_latest_status_update_reason_code = models.CharField(max_length=5, null=True, blank=True, db_index=True) #only 3 digit status master code
    ship_latest_status_update_time = models.DateTimeField(null=True, blank=True, db_index=True)
    ship_rts_date = models.DateField(null=True, blank=True, db_index=True) # WHEN TO UPDATE THIS? done
    ship_closed_time = models.DateTimeField(null=True, blank=True, db_index=True)
    ship_remarks = models.CharField(max_length=200, null=True, blank=True) # WHEN TO UPDATE THIS? done
    ship_misroute_remarks = models.CharField(max_length=10, null=True, blank=True, db_index=True) # WHEN TO UPDATE THIS?
    ship_latest_outscan_emp = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    ship_latest_inscan_dc_sc = models.CharField(max_length=10, null=True, blank=True, db_index=True) # NEED MIGRATION
    last_removed_bag_number = models.CharField(max_length=10, null=True, blank = True, db_index=True)
    first_added_bag_number = models.CharField(max_length=10, null=True, blank = True, db_index=True)
    last_added_bag_number = models.CharField(max_length=10, null= True, blank = True, db_index=True)
    record_update = models.DateTimeField(blank=True, null=True, db_index=True)

    bag_first_close_sc = models.CharField(max_length=5, null=True, blank=True, db_index=True) # first bag closed sc - done
    bag_latest_inscan_hub_time = models.DateTimeField(null=True, blank=True, db_index=True)
    bag_latest_inscan_hub_sc = models.CharField(max_length=5, null=True, blank=True, db_index=True)
    ship_latest_debag_time = models.DateTimeField(null=True, blank=True, db_index=True) # dc bag inscan time - done
    ship_latest_debag_sc = models.CharField(max_length=5, null=True, blank=True, db_index=True)# dc bag inscan sc - done
    ship_first_outscan_time_dc = models.DateTimeField(null=True, blank=True, db_index=True) # first outscan at dc done
    ship_last_outcan_time_dc = models.DateTimeField(null=True, blank=True, db_index=True) # SPELLNG CORRECTION
    ship_current_status_code = models.CharField(max_length=5, null=True, blank=True, db_index=True) # current reasoncode
    vendor_name = models.CharField(max_length=250, null=True, blank=True, db_index=True) # sub customer name
    mass_updation_status = models.CharField(max_length=5, null=True, blank=True, db_index=True) # WHEN TO UPDATE THIS:done
    mass_updation_hub = models.CharField(max_length=5, null=True, blank=True, db_index=True)# WHEN TO UPDATE THIS:done
    no_outscan = models.CharField(max_length=10, null=True, blank=True, db_index=True) # delivery outscan count

    ship_rvp_flag = models.SmallIntegerField(null=True, blank=True, db_index=True) #reverse pickup - not done
    ship_current_status = models.SmallIntegerField(null=True, blank=True, db_index=True)
    ship_origin_city = models.CharField(max_length=30, null=True, blank=True)
    ship_dest_city = models.CharField(max_length=30, null=True, blank=True)

    bag_first_hub_connection_time = models.CharField(max_length=30, null=True, blank=True)
    bag_latest_hub_connection_time = models.CharField(max_length=30, null=True, blank=True)
    chargeable_weight = models.CharField(max_length=30, null=True, blank=True)
    collectable_value = models.CharField(max_length=30, null=True, blank=True)

    freight_charge = models.FloatField(null=True, blank=True, default=0)
    fuel_surcharge = models.FloatField(null=True, blank=True, default=0)
    valuable_cargo_handling_charge = models.FloatField(blank=True,null=True, default=0)
    to_pay_charge = models.FloatField(null=True, blank=True, default=0)
    rto_charge = models.FloatField(null=True, blank=True, default=0)
    sdl_charge = models.FloatField(null=True, blank=True, default=0)
    sdd_charge = models.FloatField(null=True, blank=True, default=0)
    reverse_charge = models.FloatField(null=True, blank=True, default=0)
    cod_charge = models.FloatField(null=True, blank=True, default=0)
    total_charge = models.FloatField(null=True, blank=True, default=0, db_index=True)
    subcustomer_code = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    product_name = models.CharField(max_length=6, null=True, blank=True, db_index=True)
    expected_dod = models.DateField(null=True, blank=True)

    objects = ShipmentBagHistoryManager()


class Cluster(models.Model):
    cluster_name = models.CharField(max_length = 100)
    added_on = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return str(self.cluster_name)


class ClusterDCMapping(models.Model):
    cluster = models.ForeignKey(Cluster, null = True, blank = True)
    dc_code = models.ForeignKey('location.ServiceCenter', null = True, blank = True, db_index = True)
    added_on = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return str(self.cluster.cluster_name)


class ClusterEmailMapping(models.Model):
    cluster = models.ForeignKey(Cluster, null = True, blank = True)
    email = models.CharField(max_length = 100, null = True, blank = True)
    added_on = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return str(self.cluster.cluster_name)

