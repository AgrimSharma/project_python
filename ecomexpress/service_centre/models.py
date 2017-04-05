import time
from math import ceil

from django.db.models import *
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User

from customer.models import *
from location.models import *
from pickup.models import *
from ecomm_admin.models import *
#from octroi.models import * 

today = datetime.datetime.today()
last_month = (today - datetime.timedelta(days=10)).strftime('%Y-%m-%d')


def _update_or_create(self, **kwargs):
    assert kwargs, \
            'update_or_create() must be passed at least one keyword argument'
    obj, created = self.get_or_create(**kwargs)
    defaults = kwargs.pop('defaults', {})
    if created:
        return obj, True, False
    else:
        try:
            params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
            params.update(defaults)
            for attr, val in params.items():
                if hasattr(obj, attr):
                    setattr(obj, attr, val)
            sid = transaction.savepoint()
            obj.save(force_update=True)
            transaction.savepoint_commit(sid)
            return obj, False, True
        except IntegrityError, e:
            transaction.savepoint_rollback(sid)
            try:
                return self.get(**kwargs), False, False
            except self.model.DoesNotExist:
                raise e

# Create your models here.
class Shipment(models.Model):
    pickup = models.ForeignKey(PickupRegistration, null=True, blank=True, related_name='shipment_pickup')
    reverse_pickup = models.BooleanField(default=False)
    return_shipment = models.SmallIntegerField(default=False)
    airwaybill_number=models.BigIntegerField()

    order_number=models.CharField(max_length=20)
    product_type = models.CharField(max_length=10, null=True, blank=True)

    shipper = models.ForeignKey(Customer, null=True, blank=True)

    consignee=models.CharField(max_length=100, null=True, blank=True)

    consignee_address1=models.CharField(max_length=400, null=True, blank=True)
    consignee_address2=models.CharField(max_length=400, null=True, blank=True)
    consignee_address3=models.CharField(max_length=400, null=True, blank=True)
    consignee_address4=models.CharField(max_length=400, null=True, blank=True)
    destination_city = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    manifest_location = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="manifest_location")
    service_centre = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="shipment_sc")
    current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc")
    state = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.BigIntegerField(default=0, null=True, blank=True)
    telephone = models.CharField(default=0, max_length=100, null=True, blank=True)
    item_description=models.CharField(max_length=400, null=True, blank=True)
    pieces=models.IntegerField(null=True, blank=True)

    collectable_value=models.FloatField(null=True, blank=True)
    declared_value=models.FloatField(null=True, blank=True)

    actual_weight=models.FloatField(default=0.0, null=True, blank=True)
    volumetric_weight=models.FloatField(default=0.0, null=True, blank=True)

    length=models.FloatField(default=0.0, null=True, blank=True)
    breadth=models.FloatField(default=0.0, null=True, blank=True)
    height=models.FloatField(default=0.0, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    status_type = models.IntegerField(default=0, null=True, blank=True)
    reason_code = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True)
    remark = models.CharField(max_length=400, null=True, blank=True)
    expected_dod=models.DateTimeField(null=True, blank=True)
    ref_airwaybill_number = models.BigIntegerField(null=True, blank=True)
    original_dest = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="shipment_origin_sc")
    rts_reason = models.CharField(max_length=100, null=True, blank=True)
    rts_date=models.DateTimeField(null=True, blank=True)
    inscan_date=models.DateTimeField(null=True, blank=True)
    rts_status = models.SmallIntegerField(default=0, null=True, blank=True)
    rd_status = models.SmallIntegerField(default=0, null=True, blank=True)
    rto_status = models.SmallIntegerField(default=0, null=True, blank=True)
    sdd = models.SmallIntegerField(default=0, null=True, blank=True)
    rejection = models.SmallIntegerField(default=0, null=True, blank=True)
    billing = models.ForeignKey('billing.Billing', null=True, blank=True, related_name='billing_ships')
    sbilling = models.ForeignKey('billing.BillingSubCustomer', null=True, blank=True, related_name='subbilling_ships')
    sdl = models.SmallIntegerField(default=0, null=True, blank=True)
    tab = models.SmallIntegerField(default=0, null=True, blank=True)
    chargeable_weight = models.FloatField(null=True, blank=True, default=0)
    shipment_date = models.DateField(null=True, blank=True)

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Shipment._meta.fields]

    @property
    def get_latest_deliveryoutscan(self):
        del_outs = self.deliveryoutscan_set.all()
        del_count = del_outs.count()
        if del_count == 0:
            return None
        elif del_count == 1:
            return del_outs[0]
        else:
            return del_outs.latest('id')

    @property
    def change_chargeable_weight(self):
        minwt = MinActualWeight.objects.filter(customer=self.shipper)
        min_actual_weight = minwt[0].weight if minwt else 0
        max_weight_dimension = max(float(self.volumetric_weight), self.actual_weight)
        if min_actual_weight and max_weight_dimension <= min_actual_weight:
            max_weight_dimension =  self.actual_weight
        Shipment.objects.filter(pk=self.id).update(chargeable_weight = max_weight_dimension)
        return self.chargeable_weight

    @property
    def change_shipment_date(self):
       if not self.inscan_date:
            return None
       check_time = datetime.time(07,00,00)
       if self.inscan_date.time() > check_time:
           Shipment.objects.filter(id=self.id).update(shipment_date=self.inscan_date.date())
       else:
           Shipment.objects.filter(id=self.id).update(shipment_date=self.inscan_date.date() - datetime.timedelta(days=1))
       return self.shipment_date


    @property
    def set_chargeable_weight(self):
        vol_div = VolumetricWeightDivisor.objects.filter(customer=self.shipper)
        if vol_div.exists():
            volumetric_weight_divisor = vol_div[0].divisor
        else:
            volumetric_weight_divisor = 5000
        if not self.volumetric_weight:
            if self.length and self.breadth and self.height:
                volume = (float(self.length) * float(self.breadth) * float(self.height)) / volumetric_weight_divisor
                self.volumetric_weight = volume
        #self.volumetric_weight = ceil(2*self.volumetric_weight)/2.0 # why multiply and then divide by 2?
        #if self.actual_weight:
        #    self.actual_weight = ceil(2*self.actual_weight)/2.0
        if not self.actual_weight:
            self.actual_weight = self.volumetric_weight

        minwt = MinActualWeight.objects.filter(customer=self.shipper)
        min_actual_weight = minwt[0].weight if minwt else 0
        max_weight_dimension = max(float(self.volumetric_weight), self.actual_weight)
        if min_actual_weight and self.actual_weight <= min_actual_weight:
            max_weight_dimension =  self.actual_weight

        #fss = self.shiper.freightslab_set.all().order_by("range_from")
        #if self.shipper_id == 7,224]:
        if self.shipper_id == 7 and self.actual_weight <= 0.250:
            max_weight_dimension = 0.250
        elif self.shipper_id == 224 and self.actual_weight <= 0.750 and self.pickup.service_centre.city.zone_id <> 7:
            max_weight_dimension = 0.750
        else: 
            max_weight_dimension = ceil(2*max_weight_dimension)/2.0
        

        Shipment.objects.filter(pk=self.id).update(chargeable_weight=max_weight_dimension,
                                                   volumetric_weight=self.volumetric_weight,
                                                   actual_weight=self.actual_weight)
        return max_weight_dimension

    @property
    def set_shipment_date(self):
       if self.shipment_date:
            return self.shipment_date
       if not self.inscan_date:
            return None
       check_time = datetime.time(07,00,00)
       if self.inscan_date.time() > check_time:
           Shipment.objects.filter(id=self.id).update(shipment_date=self.inscan_date.date())
       else:
           #self.shipment_date = self.inscan_date - datetime.timedelta(days=1)
           Shipment.objects.filter(id=self.id).update(shipment_date=self.inscan_date.date() - datetime.timedelta(days=1))
       return self.shipment_date


class ShipmentExtension(models.Model):
      shipment = models.OneToOneField(Shipment, primary_key=True, related_name = "shipext")
      origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name = "shipextraorg")
      subcust_code = models.ForeignKey(Shipper, null=True, blank=True)
      zone_origin = models.ForeignKey(Zone, null=True, blank=True, related_name = "shipextrazono")
      zone_destination = models.ForeignKey(Zone, null=True, blank=True, related_name = "shipextrazond")
      bagging_origin = models.ForeignKey(ServiceCenter,null=True, related_name = "shipextraborg")
      bagging_destination = models.ForeignKey(ServiceCenter,null=True, related_name = "shipextrabdes")
      delivered_on = models.DateTimeField(null=True, blank=True)
      lat = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='latitude', default = 0.0, null = True)
      lon = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='longitude', default = 0.0, null = True)
      status_bk = models.IntegerField(null = True, blank = True, db_index=True)
      current_sc_bk = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name = "shipextracsc")  #backuo status same as hist
      current_return_dest = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="shipextracod")  #rtod from
      return_date = models.DateTimeField(null = True, blank = True) #date on which shipment rtod
      updated_on = models.DateTimeField(null = True, blank = True)
      remarks = models.CharField(max_length=200, null=True, blank=True) #hist remarks
      original_pincode = models.IntegerField(null=True, blank=True)
      bag_number = models.CharField(max_length=20, null=True, blank=True)
      orig_expected_dod=models.DateTimeField(null=True, blank=True)
      recieved_by = models.CharField(max_length=20, null=True, blank=True)
      su_rem = models.CharField(max_length=200, null=True, blank=True)
      firstsu_date = models.DateTimeField(null=True, blank=True)
      firstsu_rc = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True, related_name="shipextfirstsurc")
      prev_su_date = models.DateTimeField(null=True, blank=True)
      original_act_weight = models.FloatField(null=True, blank=True)
      original_vol_weight = models.FloatField(null=True, blank=True)
      misroute_code = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True, related_name="shipextmisroutecode")
      delay_code = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True, related_name="shipextdelaycode")
      rev_shipment = models.OneToOneField(Shipment, null=True, blank=True, related_name="shipextrevshipment")

      collected_amount = models.FloatField(null=True, blank=True, default=0.0)
      upd_product_type = models.CharField(max_length=10, null=True, blank=True)
      cash_tally_status = models.IntegerField(null=True, blank=True, default=0) #0-shipment not updated from daily cash tally, 1-updated
      cash_deposit_status = models.IntegerField(null=True, blank=True, default=0) #0-not closed, 1-collected amount is successully added to coddeposit
      partial_payment = models.BooleanField(default=False)
      product = models.ForeignKey('customer.Product', null=True, blank=True, related_name='shipextproduct')

class ReverseShipment(models.Model):
    reverse_pickup = models.ForeignKey(ReversePickupRegistration, null=True, blank=True, related_name='rev_pickup')
    pickup = models.ForeignKey(PickupRegistration, null=True, blank=True, related_name='normal_pickup')
    shipment = models.ForeignKey(Shipment, null=True, blank=True, related_name='normal_shipment_pickup')
    revpickup_status = models.BooleanField(default=False)
    airwaybill_number=models.BigIntegerField(null=True, blank=True)
    order_number=models.CharField(max_length=20, null=True, blank=True)
    product_type = models.CharField(max_length=10, null=True, blank=True)

    shipper = models.ForeignKey(Customer, null=True, blank=True)
    vendor = models.ForeignKey(Shipper, null=True, blank=True)
    pickup_consignee=models.CharField(max_length=100, null=True, blank=True)

    pickup_consignee_address1=models.CharField(max_length=400, null=True, blank=True)
    pickup_consignee_address2=models.CharField(max_length=400, null=True, blank=True)
    pickup_consignee_address3=models.CharField(max_length=400, null=True, blank=True)
    pickup_consignee_address4=models.CharField(max_length=400, null=True, blank=True)

    pickup_pincode = models.IntegerField(null=True, blank=True)

    pickup_service_centre = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="rev_shipment_sc")

    current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="rev_current_sc")

    state = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.BigIntegerField(default=0, null=True, blank=True)
    telephone = models.CharField(default=0, max_length=100, null=True, blank=True)
    item_description=models.CharField(max_length=400, null=True, blank=True)
    pieces=models.IntegerField(null=True, blank=True)

    collectable_value=models.FloatField(null=True, blank=True)
    declared_value=models.FloatField(null=True, blank=True)

    actual_weight=models.FloatField(default=0.0, null=True, blank=True)
    volumetric_weight=models.FloatField(default=0.0, null=True, blank=True)

    length=models.FloatField(default=0.0, null=True, blank=True)
    breadth=models.FloatField(default=0.0, null=True, blank=True)
    height=models.FloatField(default=0.0, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(auto_now=True, null=True, blank=True)
    status_type = models.IntegerField(default=0, null=True, blank=True)
    reason_code = models.ForeignKey(PickupStatusMaster, null=True, blank=True)
    remark = models.CharField(max_length=400, null=True, blank=True)

    expected_dod=models.DateTimeField(null=True, blank=True)
    ref_airwaybill_number = models.BigIntegerField(null=True, blank=True)
    original_dest = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="rev_shipment_origin_sc")
    employee_code = models.ForeignKey(EmployeeMaster, null=True, blank=True)


class CODChargeManager(models.Manager):
    update_or_create = _update_or_create

class CODCharge(models.Model):
    shipment = models.ForeignKey(Shipment)
    cod_charge      = models.FloatField(blank=True,null=True, default=0)
    updated_on=       models.DateTimeField(auto_now_add = True)
    status = models.IntegerField(blank=True,null=True, default=0)
    remittance_status = models.IntegerField(default=0, null=True, blank=True)
    remitted_on =       models.DateTimeField(null=True, blank=True)
    remitted_amount = models.FloatField(blank=True,null=True, default=0)
    objects = CODChargeManager()

class RemittanceCODCharge(models.Model):
    remittance        = models.ForeignKey('customer.Remittance')
    codcharge        = models.ForeignKey(CODCharge)
    added_on          = models.DateTimeField(auto_now_add=True)
    bank_name = models.CharField(max_length=50)
    bank_ref_number = models.CharField(max_length=50)


class CODDeposits(models.Model):
    slip_number = models.CharField(max_length=20, null=True, blank=True)
    codd_code = models.CharField(max_length=20, null=True, blank=True)
    total_amount = models.FloatField(default=0.0)
    collected_amount = models.FloatField(default=0.0)
    bank_code = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateField(auto_now_add = True, null=True, blank=True)
    time=models.TimeField(auto_now_add = True, null=True, blank=True)
    denomination = models.ManyToManyField('Denomination', related_name="codd_denomination")
    cod_shipments = models.ManyToManyField('Shipment', related_name="codd_shipments")
    status = models.IntegerField(default=0, null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="codd_origin")
    deposited_on = models.DateTimeField(null=True, blank=True)

    def update_do_unupdated_count(self):
        ships = self.cod_shipments.all()
        outscans = []
        for s in ships:
            #do = s.deliveryoutscan_set.latest('added_on')
            do = DOShipment.objects.filter(shipment=s, status=1)
            if do.exists():
                outscans.append(do[0].deliveryoutscan.id)

        del_outscans = list(set(outscans))
        if del_outscans:
            outscans_update_for_cash_tally(del_outscans)

        #outscans = DeliveryOutscan.objects.filter(id__in=del_outscans)
        #for outscan in outscans:
            #outscan.update_amount_tobe_collected()
            #outscan.update_collected_amount()
            #outscan.update_unupdated_count()
            #outscan_update_for_cash_tally()
        return True

    def update_shipments_status(self):
        # update the cash deposit status of shipments
        if self.status != 1:
            return False
        ships = self.cod_shipments.all()

        for ship in ships:
            # handle if it is full payment
            if ship.shipext.partial_payment == False:
                ShipmentExtension.objects.filter(shipment=ship).update(cash_deposit_status=1)
            else:
                # for partial payment, update only those shipments whose pending amount is zero
                if int(ship.shipext.collected_amount) == int(ship.collectable_value):
                    ShipmentExtension.objects.filter(shipment=ship).update(cash_deposit_status=1)
        return True


class CODDepositShipments(models.Model):
    shipments = models.ManyToManyField('Shipment')
    status = models.IntegerField(default=0, null=True, blank=True) # 0 - not added to any coddeposit yet, 1 - added to coddeposit
    coddeposit = models.ForeignKey(CODDeposits, null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def add_shipment(self, shipment):
        if not shipment in self.shipments.all():
            self.shipments.add(shipment)
        return self

    def get_total(self):
        non_pp_total = self.shipments.filter(shipext__partial_payment=False).aggregate(amt=Sum('shipext__collected_amount')).get('amt')
        pp_ships = self.shipments.filter(shipext__partial_payment=True)
        if pp_ships.exists():
            pp_total = CashTallyHistory.objects.get_shipments_last_collection_sum(shipments=pp_ships)
        else:
            pp_total = 0

        non_pp_total = non_pp_total if non_pp_total else 0
        pp_total = pp_total if pp_total else 0
        return non_pp_total + pp_total


class CODDepositsRemovedShipment(models.Model):
    """
    This model keep track of shipments removed from CODDeposits
    through delivery cash tally.
    status - 0 -> added back
             1 -> removed
    """
    shipment = models.ForeignKey(Shipment)
    status = models.IntegerField(default=1)
    user = models.ForeignKey(User)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class Denomination(models.Model):
    type=models.IntegerField()
    quantity=models.IntegerField()

class Order_priceManager(models.Manager):
    update_or_create = _update_or_create

class Order_price(models.Model):
    shipment = models.ForeignKey(Shipment)
    freight_charge = models.FloatField(null=True, blank=True, default=0)
    fuel_surcharge = models.FloatField(null=True, blank=True, default=0)
    valuable_cargo_handling_charge = models.FloatField(blank=True,null=True, default=0)
    to_pay_charge = models.FloatField(null=True, blank=True, default=0)
    rto_charge = models.FloatField(null=True, blank=True, default=0)
    sdl_charge = models.FloatField(null=True, blank=True, default=0)
    sdd_charge = models.FloatField(null=True, blank=True, default=0)
    reverse_charge = models.FloatField(null=True, blank=True, default=0)
    tab_charge = models.FloatField(null=True, blank=True, default=0)
    objects = Order_priceManager()

class RTSPrice(models.Model):
    customer = models.ForeignKey(Customer, null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="rts_origin")
    destination = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="rts_dest")
    charge_apply= models.BooleanField(default=False)
    rate = models.FloatField(default=0, null=True, blank=True)

class Bags(models.Model):
    bag_type = models.CharField(max_length=50, null=True, blank=True)
    bag_size = models.CharField(max_length=50, null=True, blank=True)

    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="bag_origin")
    hub = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="bag_hub")
    destination = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="bag_dest")
    #bag_number = models.CharField(max_length=20)
    bag_number = models.CharField(max_length=20, null=True, blank=True)
    shipments = models.ManyToManyField('Shipment')
    ship_data = models.ManyToManyField('Shipment', related_name="shipment_data")
    bag_status = models.IntegerField(default=0, null=True, blank=True)
    status_type = models.IntegerField(default=0, null=True, blank=True)
    actual_weight = models.FloatField(default=0.0, blank=True,null=True)
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="bag_sc")
    employee_code=models.ForeignKey(EmployeeMaster, null=True, blank=True)
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Bags._meta.fields]

    def __unicode__(self):
        return str(self.bag_number)

    @property
    def get_latest_connection_id(self):
        try:
            return self.connection_set.latest('id').id
        except Connection.DoesNotExist:
            return None

    def get_shipments_count(self):
        return self.shipments.filter(
           status__in=[3,5]
        ).exclude(rts_status=2).exclude(status=9).exclude(
            reason_code__code__in=[111, 777, 999, 888, 333, 310, 200,208, 302,311])


class Connection(models.Model):
    coloader = models.ForeignKey(Coloader, null=True, blank=True, related_name="connection_coloader")
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="conn_origin")
    destination = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="connection_dest")
   # destination = models.ManyToManyField(ServiceCenter, null=True, blank=True, related_name="conn_dest")
    bags = models.ManyToManyField('Bags')
    vehicle_number = models.CharField(max_length=100, null=True, blank=True)
    connection_status = models.IntegerField(default=0, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)

class Octroi(models.Model):
    shipper = models.ForeignKey(Customer, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add = True)
    origin = models.ForeignKey(ServiceCenter, related_name="oct_origin")
    octroi_slip_no = models.CharField(max_length=100,null=True, blank=True)
    date = models.DateField(auto_now_add = True, null=True, blank=True)
    total_amount = models.IntegerField(default=0, null=True, blank=True)
    total_ship = models.IntegerField(default=0)
    #shipments = models.ManyToManyField('Shipment', related_name="oct_shipments")
    status = models.IntegerField(default=0)

class OctroiShipments(models.Model):
    shipment = models.ForeignKey(Shipment, unique=True)
    octroi = models.ForeignKey(Octroi)
    serial_no = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    shipper = models.ForeignKey(Customer, null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter)
    octroi_billing = models.ForeignKey('octroi.OctroiBilling', null=True, blank=True, related_name='octroi_billing')
    octroi_charge = models.FloatField(default=0,blank=True,null=True)
    octroi_ecom_charge = models.FloatField(default=0,blank=True,null=True)
    status = models.IntegerField(default=0) #0-charges are not yet added, 1-charges added
    receipt_number = models.CharField(max_length=20, default="")

class OctroiAirportConfirmation(models.Model):
    airportconfirmation = models.ForeignKey('AirportConfirmation')
    shipment = models.ForeignKey(Shipment, unique=True)
    status = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter)


class NFormAirportConfirmation(models.Model):
    airportconfirmation = models.ForeignKey('AirportConfirmation')
    shipment = models.ForeignKey(Shipment, unique=True)
    status = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter)


class NForm(models.Model):
    shipper = models.ForeignKey(Customer, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add = True)
    origin = models.ForeignKey(ServiceCenter, related_name="nhform_origin")
    nform_slip_no = models.CharField(max_length=100,null=True, blank=True)
    date = models.DateField(auto_now_add = True, null=True, blank=True)
    total_amount = models.IntegerField(default=0, null=True, blank=True)
    total_ship = models.IntegerField(default=0)
    #shipments = models.ManyToManyField('Shipment', related_name="oct_shipments")
    status = models.IntegerField(default=0)

class NFormShipments(models.Model):
    shipment = models.ForeignKey(Shipment, unique=True)
    nhform = models.ForeignKey(NForm)
    serial_no = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    shipper = models.ForeignKey(Customer, null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter)

class RunCode(models.Model):
    coloader = models.ForeignKey(Coloader, null=True, blank=True, related_name="runcode_coloader")
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="runcode_origin")
    destination = models.ManyToManyField(ServiceCenter, null=True, blank=True, related_name="runcode_dest")
    connection = models.ManyToManyField('Connection')
    vehicle_number = models.CharField(max_length=100, null=True, blank=True)
    runcode_status = models.IntegerField(default=0, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)

class AirportConfirmation(models.Model):
    date = models.DateField(auto_now_add = True, null=True, blank=True)
    run_code = models.ForeignKey(RunCode, null=True, blank=True)
    flight_num = models.CharField(max_length=100,null=True, blank=True)
    std = models.CharField(max_length=100,null=True, blank=True)
    atd = models.CharField(max_length=100,null=True, blank=True)
    num_of_bags = models.CharField(max_length=100,null=True, blank=True)
   # coloader_name = models.ForeignKey(Coloader, null=True, blank=True, related_name="airport_coloader")
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="origin_ac")
    cnote = models.CharField(max_length=100,null=True, blank=True)
    status_code = models.IntegerField(default=0, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in AirportConfirmation._meta.fields]

class ReverseOutscan(models.Model):
    employee_code= models.ForeignKey(EmployeeMaster, null=True, blank=True)
    route = models.CharField(max_length=100, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True) #1:closed
    added_on=models.DateTimeField(auto_now_add = True)
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="revoutscan_origin")

class ReverseOutscanShipment(models.Model):
    reverseshipment = models.ForeignKey(ReverseShipment)
    outscan = models.ForeignKey(ReverseOutscan)
    status = models.IntegerField(default = 0)
    serial = models.IntegerField(default = 0)
    updated_on = models.DateTimeField(null = True, blank = True)

class DeliveryOutscanManager(models.Manager):

    def get_incomplete_closures_for_sc(self, origin):
        return DeliveryOutscan.objects.using('local_ecomm').filter(added_on__gte=last_month, origin_id=origin, status=1).exclude(unupdated_count=0).order_by('-added_on')

    def get_cash_tally_shipments(self, origin):
        outscans = DeliveryOutscan.objects.get_incomplete_closures_for_sc(origin=origin)
        #ships = list(outscans.values_list('shipments', flat=True))
        shipments = []
        for os in outscans:
            for s in Shipment.objects.using('local_ecomm').filter( status=9, rts_status=0, product_type='cod', current_sc=origin, shipext__cash_deposit_status=0, deliveryoutscan = os).exclude(reverse_pickup=1):
                shipments.append(s)

        return list(set(shipments))
       #return Shipment.objects.filter(id__in=ships, status=9,
       #    rts_status=0, product_type='cod', current_sc=origin,
       #    shipext__cash_deposit_status=0).exclude(reverse_pickup=1)

    def get_coddeposit_shipments(self, origin):
        return DeliveryOutscan.objects.get_cash_tally_shipments(origin=origin).filter(shipext__collected_amount__gt=0)

class DeliveryOutscan(models.Model):
    employee_code= models.ForeignKey(EmployeeMaster, null=True, blank=True)
    route = models.CharField(max_length=100, null=True, blank=True)
    shipments = models.ManyToManyField('Shipment')
    status = models.IntegerField(default=0, null=True, blank=True) #1:closed
    added_on=models.DateTimeField(auto_now_add = True)
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="outscan_origin")
    collection_status = models.IntegerField(default=0, null=True, blank=True) #1:amount collected, 2:amount mismatch
    amount_to_be_collected = models.FloatField(default=0,blank=True,null=True)
    amount_collected = models.FloatField(default=0, blank=True,null=True)
    amount_mismatch = models.FloatField(default=0, blank=True,null=True)
    mismatch = models.IntegerField(default=0, null=True, blank=True)
    cod_status = models.IntegerField(max_length=1,default=0, null=True, blank=True) #1:include in codd
    unupdated_count = models.IntegerField(default=-1, null=True, blank=True)
    mobile_no = models.CharField(max_length=15,null=True, blank=True)

    objects = DeliveryOutscanManager()

    def dos_unupdated_count(self):
        dos_unupdated = self.doshipment_set.filter(status = 0)
        return dos_unupdated

    def dos_updated_count(self):
        dos_unupdated = self.doshipment_set.filter(status__gte = 1)
        return dos_unupdated

    def get_collectable_shipments(self):
        ships = DOShipment.objects.filter(deliveryoutscan=self, status=1,
                shipment__reason_code_id=1, shipment__product_type='cod').\
                exclude(shipment__rts_status=0).\
                exclude(shipment__reverse_pickup=1)
        return ships

    def get_uncollectable_shipments(self):
        ships = DOShipment.objects.filter(deliveryoutscan=self).exclude(status=1)
        return ships

    def update_amount_tobe_collected(self):
        amount_to_be_collected = DOShipment.objects.filter(deliveryoutscan=self,
                status=1, shipment__reason_code_id=1,
                shipment__product_type='cod').\
                        exclude(shipment__rts_status=1).\
                        exclude(shipment__reverse_pickup=1).aggregate(total=Sum('shipment__collectable_value'))['total']
        if not amount_to_be_collected:
               amount_to_be_collected = 0.0
        DeliveryOutscan.objects.filter(id=self.id).update(amount_to_be_collected=amount_to_be_collected)
        return amount_to_be_collected

    def update_collected_amount(self):
        doships = DOShipment.objects.filter(deliveryoutscan=self,
                status=1, shipment__reason_code_id=1, shipment__product_type='cod').\
                exclude(shipment__rts_status=1).exclude(shipment__reverse_pickup=1)
        awbs = list(doships.values_list('shipment__airwaybill_number', flat=True))
        amount_collected = Shipment.objects.filter(airwaybill_number__in=awbs).aggregate(ac=Sum('shipext__collected_amount'))['ac']
        amount_collected = 0 if not amount_collected else amount_collected
        uc = DOShipment.objects.filter(deliveryoutscan=self,
                status=1, shipment__reason_code_id=1, shipment__product_type='cod', shipment__shipext__cash_deposit_status=0).\
                exclude(shipment__rts_status=1).exclude(shipment__reverse_pickup=1).only('id').count()
        codstatus = 1 if uc == 0 else 0
        amount_mismatch = int(self.amount_to_be_collected) - int(amount_collected)
        collection_status = 1 if amount_mismatch == 0 else 2
        DeliveryOutscan.objects.filter(id=self.id).update(amount_collected=amount_collected,
                    collection_status=collection_status, cod_status=codstatus, unupdated_count=uc, amount_mismatch=0)
        return True

    def update_unupdated_count(self):
        uc = DOShipment.objects.filter(deliveryoutscan=self,
                status=1, shipment__reason_code_id=1, shipment__product_type='cod', shipment__shipext__cash_deposit_status=0).\
                exclude(shipment__rts_status=1).exclude(shipment__reverse_pickup=1).only('id').count()

        DeliveryOutscan.objects.filter(id=self.id).update(unupdated_count=uc)
        return True

class OutscanShipments(models.Model):
      outscan = models.IntegerField(default=0)
      awb = models.BigIntegerField(default=0)
      serial = models.IntegerField(default=0)
      class Meta:
        unique_together = (('outscan','awb'),)
        unique_together = (('outscan','serial'),)

class DOShipment(models.Model):
    shipment = models.ForeignKey(Shipment)
    deliveryoutscan = models.ForeignKey(DeliveryOutscan)
    status = models.IntegerField(default=0, null=True, blank=True)#2:undelivered, 1:delivered, 0:not updated
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    class Meta:
        unique_together = (('shipment','deliveryoutscan'),)


class CODDepositsOutscan(models.Model):
    coddeposit = models.ForeignKey(CODDeposits)
    deliveryoutscan = models.ForeignKey(DeliveryOutscan)
    status = models.IntegerField(default=0, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)

class CashAdjustment(models.Model):
    deliveryoutscan = models.ForeignKey(DeliveryOutscan)
    status = models.IntegerField(default=0, null=True, blank=True)
    remark = models.CharField(max_length=255,null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True)


class StatusUpdate(models.Model):
    shipment = models.ForeignKey(Shipment)
    data_entry_emp_code = models.ForeignKey(EmployeeMaster, null=True, blank=True, related_name="statsupd_dataemp")
    delivery_emp_code = models.ForeignKey(EmployeeMaster, null=True, blank=True, related_name="statsupd_deliveryemp")
    reason_code = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    recieved_by = models.CharField(max_length=200, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True)#1:undelivered, 2:delivered 3:pod reversal undelivered
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="statsupd_origin")
    remarks = models.CharField(max_length=200, null=True, blank=True)
    ajax_field = models.CharField(max_length=20, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True)

class ShipmentAtLocation(models.Model):
    data_entry_emp_code =  models.ForeignKey(EmployeeMaster, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    scanned_shipments = models.ManyToManyField('Shipment', related_name="sal_scanned")
    total_undelivered_shipment = models.ManyToManyField('Shipment', related_name="sal_total_undelivered")
    status = models.IntegerField(default=0, null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="sal_origin")
    added_on=models.DateTimeField(auto_now_add = True)

class SALScanType(models.Model):
    sal = models.ForeignKey(ShipmentAtLocation,null=True, blank=True)
    shipment = models.ForeignKey(Shipment, null=True, blank=True)
    sc = models.ForeignKey(ServiceCenter, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add = True)
    scan_type = models.IntegerField(default=0, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True)
    emp = models.ForeignKey(EmployeeMaster, null=True, blank=True)

    class Meta:
        unique_together = (('sal','shipment'),)


class AirwaybillTally(models.Model):
    shipment = models.ForeignKey('Shipment', related_name="awbt_scanned")
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="awbt_origin")
    cash_tally_emp_code =models.ForeignKey(EmployeeMaster, null=True, blank=True, related_name="awbt_cashemp")
    delivery_emp_code =models.ForeignKey(EmployeeMaster, null=True, blank=True, related_name="awbt_delemp")
    collectable_value = models.FloatField(blank=True,null=True)
    amount_collected = models.FloatField(blank=True,null=True)
    status = models.IntegerField(default=0, null=True, blank=True)
    reason_code = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True)
    updated_on = models.DateField(auto_now_add = True, null=True, blank=True)

class DeliveryDeposits(models.Model):
    bank_code = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=50, null=True, blank=True)
    emp_code = models.ForeignKey(EmployeeMaster, null=True, blank=True)
    emp_name = models.CharField(max_length=50, null=True, blank=True)
    amount =  models.FloatField(blank=True,null=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    codd = models.ForeignKey('CODDeposits', null=True, blank=True)
    sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="dd_origin")

class CashTallyHistoryManager(models.Manager):

    def get_last_collection(self, shipment):
        cash_history = CashTallyHistory.objects.filter(shipment=shipment, coddeposit=None)
        if cash_history.exists():
            return cash_history.latest('id').current_collection
        else:
            return 0

    def get_collection_sum(self, shipment):
        cash_history = CashTallyHistory.objects.filter(shipment=shipment)
        total = cash_history.aggregate(amt=Sum('current_collection'))
        return total.get('amt') if total.get('amt') else 0

    def get_shipments_last_collection_sum(self, shipments):
        cash_history = CashTallyHistory.objects.filter(shipment__in=shipments, coddeposit=None)
        total = cash_history.aggregate(amt=Sum('current_collection'))
        return total.get('amt') if total.get('amt') else 0

class CashTallyHistory(models.Model):
    shipment = models.ForeignKey('Shipment')
    employee_code = models.ForeignKey(EmployeeMaster, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    added_on = models.DateTimeField(auto_now_add=True)
    current_collection = models.FloatField(blank=True,null=True, default=0.0)
    updated_amount = models.FloatField(blank=True,null=True, default=0.0) # no more used
    sc = models.ForeignKey(ServiceCenter, null=True, blank=True)
    coddeposit = models.ForeignKey(CODDeposits, null=True, blank=True, default=None)

    objects = CashTallyHistoryManager()


class ShipmentHistory(models.Model):
       shipment=models.ForeignKey('Shipment')
       employee_code=models.ForeignKey(EmployeeMaster, null=True, blank=True)
       reason_code=models.ForeignKey(ShipmentStatusMaster, null=True, blank=True)
       status=models.IntegerField(default=0, null=True, blank=True)
       updated_on=models.DateTimeField(auto_now_add = True)
       remarks=models.CharField(max_length=200, null=True, blank=True)
       expected_dod=models.DateTimeField(null=True, blank=True)

       class Meta:
        abstract = True


class ShipmentHistory_2019_01(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1901")


class ShipmentHistory_2013_01(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1301")

class ShipmentHistory_2013_02(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1302")

class ShipmentHistory_2013_03(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1303")

class ShipmentHistory_2013_04(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1304")

class ShipmentHistory_2013_05(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1305")

class ShipmentHistory_2013_06(ShipmentHistory):#2018_12
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1306")

class ShipmentHistory_2013_07(models.Model):
       shipment=models.ForeignKey('Shipment')
       employee_code=models.ForeignKey(EmployeeMaster, null=True, blank=True)
       reason_code=models.ForeignKey(ShipmentStatusMaster, null=True, blank=True)
       status=models.IntegerField(default=0, null=True, blank=True)
       updated_on=models.DateTimeField(auto_now_add = True)
       remarks=models.CharField(max_length=200, null=True, blank=True)
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1307")
       expected_dod=models.DateTimeField(null=True, blank=True)

class ShipmentHistory_2013_08(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1308")

class ShipmentHistory_2013_09(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1309")

class ShipmentHistory_2013_10(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1310")

class ShipmentHistory_2013_11(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1311")

class ShipmentHistory_2013_12(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1312")

class ShipmentHistory_2014_01(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1401")

class ShipmentHistory_2014_02(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1402")

class ShipmentHistory_2014_03(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1403")

class ShipmentHistory_2014_04(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1404")

class ShipmentHistory_2014_05(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1405")

class ShipmentHistory_2014_06(ShipmentHistory):#2018_12
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1406")

class ShipmentHistory_2014_07(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1407")

class ShipmentHistory_2014_08(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1408")

class ShipmentHistory_2014_09(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1409")

class ShipmentHistory_2014_10(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1410")

class ShipmentHistory_2014_11(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1411")

class ShipmentHistory_2014_12(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1412")

class ShipmentHistory_2015_01(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1501")

class ShipmentHistory_2015_02(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1502")

class ShipmentHistory_2015_03(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1503")

class ShipmentHistory_2015_04(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1504")

class ShipmentHistory_2015_05(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1505")

class ShipmentHistory_2015_06(ShipmentHistory):#2018_12
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1506")

class ShipmentHistory_2015_07(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1507")

class ShipmentHistory_2015_08(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1508")

class ShipmentHistory_2015_09(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1509")

class ShipmentHistory_2015_10(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1510")

class ShipmentHistory_2015_11(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1511")

class ShipmentHistory_2015_12(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1512")

class ShipmentHistory_2016_01(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1601")


class ShipmentHistory_2016_03(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1603")

class ShipmentHistory_2016_04(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1604")

class ShipmentHistory_2016_05(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1605")

class ShipmentHistory_2016_06(ShipmentHistory):#2018_12
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1606")

class ShipmentHistory_2016_07(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1607")

class ShipmentHistory_2016_08(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1608")

class ShipmentHistory_2016_09(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1609")

class ShipmentHistory_2016_10(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1610")

class ShipmentHistory_2016_11(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1611")

class ShipmentHistory_2016_12(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1612")


class ShipmentHistory_2017_01(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1701")

class ShipmentHistory_2017_02(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1702")

class ShipmentHistory_2017_03(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1703")

class ShipmentHistory_2017_04(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1704")

class ShipmentHistory_2017_05(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1705")

class ShipmentHistory_2017_06(ShipmentHistory):#2018_12
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1706")

class ShipmentHistory_2017_07(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1707")

class ShipmentHistory_2017_08(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1708")

class ShipmentHistory_2017_09(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1709")

class ShipmentHistory_2017_10(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1710")

class ShipmentHistory_2017_11(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1711")

class ShipmentHistory_2017_12(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1712")


class ShipmentHistory_2018_01(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1801")

class ShipmentHistory_2018_02(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1802")

class ShipmentHistory_2018_03(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1803")

class ShipmentHistory_2018_04(ShipmentHistory):
      current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1804")

class ShipmentHistory_2018_05(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1805")

class ShipmentHistory_2018_06(ShipmentHistory):#2018_12
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1806")

class ShipmentHistory_2018_07(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1807")

class ShipmentHistory_2018_08(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1808")

class ShipmentHistory_2018_09(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1809")

class ShipmentHistory_2018_10(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1810")

class ShipmentHistory_2018_11(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1811")

class ShipmentHistory_2018_12(ShipmentHistory):
       current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc_hist1812")

def get_internal_shipment_status(num):
    status_dict= {
        '0': "Shipment Uploaded",
        '1': 'Pickup Complete / Inscan',
        '2': 'Inscan completion / Ready for Bagging',
        '3': 'Bagging completed',
        '4': 'Shipment at HUB',
        '5': 'Bagging completed at Hub',
        '6': 'Shipment at Delivery Centre',
        '7': 'Outscan',
        '8': 'Undelivered',
        '9': 'Delivered / Closed',
        '11': 'alternate instruction',
        '12': 'complaint',
        '13': 'Assigned to Run Code',
        '14': 'Airport Confirmation Sucessfull, connected to destination via Service Centre',
        '15': 'Airport Confirmation Successfull, connected to destination via Hub',
        '16': 'comments',
        '17': 'return',
        '20' : 'telecalling',
        '31' : 'Reverse shipment registered.',
        '32' : 'reverse outscan',
        '33' : 'reverse outscan not complete'
    }

    return status_dict.get(str(num).strip(), None)


def update_ships():
    start = time.time()
    for ship in Shipment.objects.all():
        ship.set_shipment_date
        ship.set_chargeable_weight
    end = time.time()
    return

def get_shipment_history(shipment):
    upd_time = shipment.added_on
    monthdir = upd_time.strftime("%Y_%m")
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
    return shipment_history

def get_shipment_status_from_id(id):
    s = Shipment.objects.get(id=id)

    if s.status == 9:
        return 'Delivered / Closed'

    if s.reason_code and s.reason_code.code in [206, 777]:
        return 'Returned'

    if s.reason_code and s.reason_code.code == 310:
        return 'Returned to Vendor'

    if s.rtoinstructionupdate_set.exists():
        return 'RTO Instruction Received'

    if s.return_shipment == 3 or s.rto_status == 1 or s.rts_status in [1, 2]:
        return 'Returned'
    elif s.status in [0, 1, 2, 3, 4, 5]:
        return 'Intransit'
    else:
        return get_internal_shipment_status(s.status)

def get_last_updated_on(id):
    s = Shipment.objects.get(id=id)
    upd = s.updated_on
    if upd:
        return upd
    return get_shipment_history(s).objects.filter(shipment=s).latest('updated_on').updated_on

def update_shipment_collected_amount(ship_id, amount_collected, emp=None, sc=None):
    """Update a single shipments collected amount
    following calculation to be made:
    create a castally history, were we need to update current collection
    and total collection amount.
    """
    shipment = Shipment.objects.get(id=ship_id)
    curr_collection = float(amount_collected)

    pending_amount = int(shipment.collectable_value) - (shipment.shipext.collected_amount)
    if int(curr_collection) > int(pending_amount):
        return None

    try:
        cash_tally_history = CashTallyHistory.objects.get(shipment=shipment, coddeposit=None)
        cash_tally_history.current_collection = curr_collection
        cash_tally_history.save()
    except CashTallyHistory.DoesNotExist:
        CashTallyHistory.objects.create(shipment=shipment, current_collection=curr_collection)
        ShipmentExtension.objects.filter(shipment=shipment).update(partial_payment=True)

    #outscan = shipment.deliveryoutscan_set.latest('added_on')
    do = DOShipment.objects.filter(shipment=shipment, status=1).values_list('deliveryoutscan__id', flat=True)
    if do:
        outscan_update_for_cash_tally(do[0])
    return curr_collection

def update_shipments_collected_amount(awbs, origin, emp=None):
    """ accept a list of airwaybill numbers and update collected amount of
    corresponding shipments as collctable value. Also update the deliveryoutscan
    collected amount.
    """
    shipments = Shipment.objects.filter(airwaybill_number__in=awbs)
    cod_ships, created = CODDepositShipments.objects.get_or_create(origin=origin, status=0)

    outscans = []
    # update each shipments cash_tally_status and collected amount.
    # for full payments create cashtallyhistory object also
    for shipment in shipments:
        if shipment.shipext.partial_payment:
            cash_tally_status = 1 if int(shipment.shipext.collected_amount) == (shipment.collectable_value) else 0
            history_collection = CashTallyHistory.objects.filter(shipment=shipment).aggregate(total=Sum('current_collection'))
            collected_amount = history_collection.get('total') if history_collection.get('total') else 0
            ShipmentExtension.objects.filter(shipment=shipment).update(cash_tally_status=cash_tally_status,
                                         collected_amount=collected_amount, partial_payment=True)
        else:
            collectable_value = shipment.collectable_value
            ShipmentExtension.objects.filter(shipment=shipment).update(collected_amount=collectable_value, cash_tally_status=1)
            CashTallyHistory.objects.create(shipment=shipment, current_collection=collectable_value)

        do = DOShipment.objects.filter(shipment=shipment, status=1).values_list('deliveryoutscan__id', flat=True)
        outscans.extend(list(do))
        cod_ships.add_shipment(shipment)

    cod_ships.save()
    del_outscans = list(set(outscans))
    outscans_update_for_cash_tally(del_outscans)
    return del_outscans

def outscan_update_for_cash_tally(del_id):
    """ intake a deliveryoutscan id and update its
    amount_to_be_collected, amount_collected, amount_mismatch and unupdated_count
    """
    d = DeliveryOutscan.objects.get(id=del_id)

    # AMOUNT TO BE COLLECTED
    amount_tobe_collected = DOShipment.objects.filter(deliveryoutscan=d,
            status=1, shipment__reason_code_id=1, shipment__product_type='cod').\
            exclude(shipment__rts_status=1).\
            exclude(shipment__reverse_pickup=1).aggregate(total=Sum('shipment__collectable_value'))['total']
    amount_tobe_collected = 0 if not amount_tobe_collected else amount_tobe_collected

    # AMOUNT COLLECTED
    doships = DOShipment.objects.filter(deliveryoutscan=d,
                status=1, shipment__reason_code_id=1, shipment__product_type='cod').\
                exclude(shipment__rts_status=1).exclude(shipment__reverse_pickup=1)
    awbs = list(doships.values_list('shipment__airwaybill_number', flat=True))
    amount_collected = Shipment.objects.filter(airwaybill_number__in=awbs).aggregate(ac=Sum('shipext__collected_amount'))['ac']
    amount_collected = 0 if not amount_collected else amount_collected

    # AMOUNT MISMATCH
    amount_mismatch = int(amount_tobe_collected) - int(amount_collected)

    # UNUPDATED SHIPMENTS COUNT
    unupdated_count = DOShipment.objects.filter(deliveryoutscan=d,
            status=1, shipment__reason_code_id=1, shipment__product_type='cod', shipment__shipext__cash_deposit_status=0).\
            exclude(shipment__rts_status=1).exclude(shipment__reverse_pickup=1).only('id').count()

    # COD STATUS
    cod_status = 1 if unupdated_count == 0 else 0

    # COLLECTION STATUS
    collection_status = 1 if amount_mismatch == 0 else 2

    DeliveryOutscan.objects.filter(id=del_id).update(
            amount_to_be_collected=amount_tobe_collected,
            amount_collected=amount_collected,
            collection_status=collection_status,
            cod_status=cod_status,
            unupdated_count=unupdated_count,
            amount_mismatch=amount_mismatch)

    return True

def outscans_update_for_cash_tally(outscans):
    for outscan in outscans:
        outscan_update_for_cash_tally(outscan)
    return True


class ConnectionQueue(models.Model):
    # 0 - created, 1 - processing, 2 - updated
    connection = models.ForeignKey('service_centre.connection')
    status = models.SmallIntegerField(default=0) 
    employee = models.ForeignKey('authentication.EmployeeMaster', null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class ShipmentCancelQueue(models.Model):
    airwaybill_number = models.BigIntegerField()
    status = models.IntegerField(max_length=1, default=0,db_index=True)
    updated_on = models.DateTimeField(auto_now_add = True)
    #sms_type = models.IntegerField(max_length=1)


