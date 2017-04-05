import datetime

from django.db import models
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from location.models import ServiceCenterTransitMasterGroup, TransitMaster
from ecomm_admin.models import HolidayMaster
from service_centre.models import Bags, Shipment
from authentication.models import EmployeeMaster
from location.models import *
from service_centre.models import DeliveryOutscan
from reports.models import *
from utils import *
# Create your models here.

def get_expected_dod(sc):
    sctmg = ServiceCenterTransitMasterGroup.objects.filter(service_center_id=sc)
    if not sctmg.exists():
        return None

    sctmg = sctmg[0]
    tt_duration = 0
    try:
        transit_time = TransitMaster.objects.get(transit_master=sctmg.transit_master_group, dest_service_center=sc)
        cutoff = datetime.datetime.strptime(transit_time.cutoff_time, "%H%M")
        tt_duration=int(transit_time.duration)
        now = datetime.datetime.now()
        if now.time() > cutoff.time():
            tt_duration+=1
        expected_dod = now + datetime.timedelta(days=tt_duration)
#        try:
#            HolidayMaster.objects.get(date=expected_dod.date())
#            expected_dod = expected_dod + datetime.timedelta(days=1)
#        except HolidayMaster.DoesNotExist():
#            pass

        return expected_dod

    except (TransitMaster.DoesNotExist, ValueError) as e:
        return None

class CreditcardDelivery(models.Model):
    shipment = models.ForeignKey(Shipment)
    credit_card_number = models.CharField(max_length=20)
    credit_card_owner = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=50)
    transaction_date = models.DateField()
    transaction_time = models.TimeField()
    collected_amount = models.FloatField(default=0.0)
    employee = models.ForeignKey(EmployeeMaster)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class UpdateCardPayment(models.Model):
    date = models.DateField()
    payment_type = models.BooleanField()
    airwaybill_number = models.BigIntegerField()
    airwaybill_amount = models.FloatField(default=0.0)
    card_payment_recvd_amount = models.FloatField(default=0.0)
    transaction_slip_no = models.BigIntegerField()
    transaction_date = models.DateField()
    remarks = models.TextField()


class UpdateCardPaymentModified(models.Model):
    PAYMENT_TYPE_CHOICES = (
        (1, 'Single AWB'),
        (2, 'Multiple AWB'),
    )
    date = models.DateField()
    payment_type = models.IntegerField(max_length=1,
            choices=PAYMENT_TYPE_CHOICES, default=1)
    airwaybill_number = models.CharField(max_length=15)
    airwaybill_amount = models.FloatField(default=0.0)
    credit_payment_recvd_amount = models.FloatField(default=0.0)
    delivery_centre_name = models.CharField(max_length=15)
    transaction_slip_no = models.CharField(max_length=20)
    transaction_date = models.DateField()
    remarks = models.TextField()
    shipment = models.ForeignKey(Shipment)
    employee = models.ForeignKey(EmployeeMaster, related_name='employee')
    updated_employee = models.ForeignKey(
        EmployeeMaster, related_name='updated_employee', null=True, blank=True)
    updated_date = models.DateField(null=True, blank=True)
    corrected_employee = models.ForeignKey(
        EmployeeMaster, related_name='corrected_employee', null=True, blank=True)
    corrected_date = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return self.transaction_slip_no


class CreditCardPaymentDeposit(models.Model):
    PAYMENT_TYPE_CHOICES = (
        (1, 'Full Payment'),
        (0, 'Part Payment'),
    )
    entry_date = models.DateField()
    system_date = models.DateField()
    payment_type = models.SmallIntegerField(
        max_length=1, choices=PAYMENT_TYPE_CHOICES, default=1)
    transaction_slip_no = models.CharField(max_length=20)
    transaction_date = models.DateField()
    credit_card_payment_received = models.FloatField(default=0)
    terminal_id = models.CharField(max_length=30, null=True, blank=True)
    employee = models.ForeignKey('authentication.EmployeeMaster')
    updated_date = models.DateField(auto_now=True)

    def __unicode__(self):
        return self.transaction_slip_no


class CreditPaymentAwbDetails(models.Model):
    creditcardpaymentdeposit = models.ForeignKey(CreditCardPaymentDeposit)
    shipment = models.ForeignKey(Shipment)
    airwaybill_amount = models.FloatField(default=0.0)
    credit_card_payment_received = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)
    delivery_centre = models.ForeignKey('location.ServiceCenter')
    remarks = models.CharField(max_length=200, null=True, blank=True)


class DashboardVisiblity(models.Model):
      employee = models.ForeignKey(EmployeeMaster, null = True, blank = True,)
     #employee = models.ForeignKey(EmployeeMaster, null = True, blank = True,
     #            limit_choices_to={'email__in': ['rakeshl@ecomexpress.in', 'yogeshk@ecomexpress.in',
     #            'vikasks@ecomexpress.in', 'lokeshr@ecomexpress.in','chandrashekarb@ecomexpress.in',
     #            'rajendranm@ecomexpress.in','lokanathanm@ecomexpress.in','himanshum@ecomexpress.in',
     #            'rajas@ecomexpress.in','suneetk@ecomexpress.in','sandeepku@ecomexpress.in',
     #            'pawankn@ecomexpress.in','bilala@ecomexpress.in','sunilr@ecomexpress.in',
     #            'rakeshp@ecomexpress.in','sbabaria@ecomexpress.in','veenav@ecomexpress.in',
     #            'shalinia@ecomexpress.in','manojks@ecomexpress.in','Praveen.Joshi@ecomexpress.in',
     #            'vedprakash@ecomexpress.in','sunainas@ecomexpress.in','rameshw@ecomexpress.in']})
      state = models.ForeignKey(State, null = True, blank = True)
      ncr_state = models.IntegerField(default=0, max_length = 1, null=True, blank=True)

def get_bag_history(bag, bag_number=False):
    if bag_number:
        bag = Bags.objects.get(bag_number=bag)
    
    added_on = bag.added_on.strftime('%Y_%m')
    bag_history = models.get_model('delivery', 'BaggingHistory_%s'%(added_on))
    history = bag_history.objects.filter(bag=bag).order_by('-updated_on')
    return history

class BaggingHistory(models.Model):
    """
    status 0 - not updated
           1 - bag created (SC)
           2 - shipment added (SC)
           3 - bag closed (SC)
           4 - added to connection (SC)
           5 - bag delinked from  connection (SC)
           6 - connection closed (SC)

           7 - bag created (HUB)
           8 - shipment added (HUB)
           9 - bag closed (HUB)
           10 - added to connection (HUB)
           11 - bag delinked from  connection (HUB)
           12 - connection closed (HUB)

           14 - bag scanned (DC)
           15 - bag scanned (HUB)

           16 - Mass updation

           17 - shipment debagged (DC)
           18 - shipment debagged (HUB)
    """

    bag = models.ForeignKey(Bags)
    employee = models.ForeignKey(EmployeeMaster, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True) # bag status
    updated_on = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=200, null=True, blank=True)
    expected_dod = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    bag_sc = models.ForeignKey(ServiceCenter, null=True, blank=True) # current sc of bag while the object is getting created
    reason_code = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True) # current rc of bag while the object is getting created

    class Meta:
        abstract = True

def get_remarks(bag_number, action):
    base_remark = 'Bag {0} {1}'
    remarks = base_remark.format(bag_number, action)
    return remarks


def update_bag_history(bag, *args, **kwargs):
    """
    status 0 - not updated
           1 - bag created (SC)
           2 - shipment added (SC)
           3 - bag closed (SC)
           4 - added to connection (SC)
           5 - bag delinked from  connection (SC)
           6 - connection closed (SC)

           7 - bag created (HUB)
           8 - shipment added (HUB)
           9 - bag closed (HUB)
           10 - added to connection (HUB)
           11 - bag delinked from  connection (HUB)
           12 - connection closed (HUB)

           14 - bag scanned (DC)
           15 - bag scanned (HUB)

           16 - Mass updation

           17 - shipment debagged (DC)
           18 - shipment debagged (HUB)
    """
    employee = kwargs.pop('employee')
    content_object = kwargs.pop('content_object')
    action = kwargs.pop('action')
    status = kwargs.get('status', 0)
    status = status if status else 0
    reason_code = kwargs.pop('reason_code') if 'reason_code' in kwargs else None

    sc = employee.service_centre
    bag_number = bag.bag_number
    if not bag_number:
        bag_number = bag.id

    remarks = get_remarks(bag_number, action)
    added_on = bag.added_on.strftime('%Y_%m')
    bag_history = models.get_model('delivery', 'BaggingHistory_%s'%(added_on))
    bag_history.objects.create(
        bag=bag, employee=employee, status=status, remarks=remarks,
        content_object=content_object, reason_code=reason_code, bag_sc=sc
    )
    ShipmentBagHistory.objects.update_bag_records(bag, status, employee)
    return True


def update_bag_remarks(bag_number, status=1):
    if status == 1:
        action = 'created'
        history = get_bag_history(bag_number, bag_number=True)
        remarks = get_remarks(bag_number, action)
        updated = history.filter(status=1).update(remarks=remarks)
        if not updated:
            history.filter(status=7).update(remarks=remarks)

def update_trackme_bagging_remarks(bag_number):
    bag = Bags.objects.get(bag_number=bag_number)
    if bag.hub:
        dest = bag.hub
    else:
        dest = bag.destination

    for ship in bag.shipments.all():
        added_on = ship.added_on.strftime('%Y_%m')
        history_model = models.get_model('service_centre', 'ShipmentHistory_%s'%(added_on))
        history = history_model.objects.filter(shipment=ship, status__in=[2,3,4,5]).only('id', 'remarks', 'status')
        for sh in history:
            remarks = sh.remarks.replace(str(bag.id), bag_number)
            history_model.objects.filter(id=sh.id).update(remarks=remarks)
    return True

def cashtally_deliveryoutscan_details(del_id):

    del_outscan = DeliveryOutscan.objects.filter(id=del_id)
    if not del_outscan.exists():
        return {'message':'Invalid delivery outscan id', success:False}
    data = del_outscan.annotate(ship_count=Count('shipments__id')).values(
        'origin__center_name', 'unupdated_count', 'collection_status',
        'amount_to_be_collected', 'amount_collected', 'amount_mismatch',
        'ship_count', 'id'
    )
    d = data[0]

    collection_status = d.get('collection_status')
    if collection_status == 0:
        coll_status = 'Pending'
    elif collection_status == 1:
        coll_status = 'Collected'
    elif collection_status:
        coll_status = 'Mismatch'

    unupdated_count = d.get('unupdated_count')
    if unupdated_count == -1:
        unupdated_count = "No Shipments updated"
    elif unupdated_count == 0:
        unupdated_count = "All Shipments updated"
    unupdated_awbs = del_outscan[0].get_collectable_shipments().filter(
        shipext__cash_deposit_status=0).values_list('airwaybill_number', flat=True)
    return {
        'id': d.get('id'),
        'success': True,
        'origin': d.get('origin__center_name'),
        'unupdated_count': unupdated_count,
        'collection_status': coll_status,
        'amount_to_be_collected': d.get('amount_to_be_collected'),
        'amount_collected': d.get('amount_collected'),
        'amount_mismatch': d.get('amount_mismatch'),
        'shipments_count': d.get('ship_count'),
        'unupdated_awbs': ', '.join(map(str, unupdated_awbs))
    }


def cashtally_shipment_details(awb):
    ship = Shipment.objects.filter(airwaybill_number=awb)
    if not ship.exists():
        return {'message':'Invalid airwaybill number', 'success':False}

    ship_data = ship.values(
        'airwaybill_number',
        'shipext__cash_tally_status',
        'shipext__cash_deposit_status',
        'shipext__collected_amount',
        'shipext__partial_payment'
    )
    data = ship_data[0]

    del_outscans = ship.values_list('deliveryoutscan__id', flat=True)
    coddeposits = ship.values_list('codd_shipments__id', 'codd_shipments__status')
    queues = ship.values_list('coddepositshipments__id', flat=True)

    if data.get('shipext__cash_tally_status'):
        daily_awb_status = 'Completed'
    else:
        daily_awb_status = 'Incomplete'

    if data.get('shipext__cash_deposit_status'):
        cash_deposit_status = 'Completed'
    else:
        cash_deposit_status = 'Incomplete'

    if data.get('shipext__partial_payment'):
        partial_payment = 'Yes'
    else:
        partial_payment = 'No'

    del_outscan_list = [v for v in del_outscans if v]
    coddeposit_list = [v[0] for v in coddeposits if v[0]]
    queue_list = [v for v in queues if v]
    return {
        'success': True,
        'airwaybill_number': awb,
        'daily_cash_tally_status': daily_awb_status,
        'cash_deposit_status': cash_deposit_status,
        'partial_payment': partial_payment,
        'delivery_outscan_list': list(del_outscan_list), #[1, 2]
        'coddeposits_list': list(coddeposit_list),
        'queues': list(queue_list),
    }


class BaggingHistory_2014_01(BaggingHistory):
    pass

class BaggingHistory_2014_02(BaggingHistory):
    pass

class BaggingHistory_2014_03(BaggingHistory):
    pass

class BaggingHistory_2014_04(BaggingHistory):
    pass

class BaggingHistory_2014_05(BaggingHistory):
    pass

class BaggingHistory_2014_06(BaggingHistory):
    pass

class BaggingHistory_2014_07(BaggingHistory):
    pass

class BaggingHistory_2014_08(BaggingHistory):
    pass

class BaggingHistory_2014_09(BaggingHistory):
    pass

class BaggingHistory_2014_10(BaggingHistory):
    pass

class BaggingHistory_2014_11(BaggingHistory):
    pass

class BaggingHistory_2014_12(BaggingHistory):
    pass

class BaggingHistory_2015_01(BaggingHistory):
    pass

class BaggingHistory_2015_02(BaggingHistory):
    pass

class BaggingHistory_2015_03(BaggingHistory):
    pass

class BaggingHistory_2015_04(BaggingHistory):
    pass

class BaggingHistory_2015_05(BaggingHistory):
    pass

class BaggingHistory_2015_06(BaggingHistory):
    pass

class BaggingHistory_2015_07(BaggingHistory):
    pass

class BaggingHistory_2015_08(BaggingHistory):
    pass

class BaggingHistory_2015_09(BaggingHistory):
    pass

class BaggingHistory_2015_10(BaggingHistory):
    pass

class BaggingHistory_2015_11(BaggingHistory):
    pass

class BaggingHistory_2015_12(BaggingHistory):
    pass


def remove_shipment_from_bag(awb):
    """ When a shipment is massupdated with reason code 305 from hub/dc,
        it has to be removed from all bags and should be able to inscan
        from hub/dc.
    """
    ship = Shipment.objects.get(airwaybill_number=awb)
    bags = ship.bags_set.all()
    for bag in bags:
        bag.shipments.remove(ship)
        bag.ship_data.remove(ship)
    return True

def remove_bag_from_connection(bag_number):
    b = Bags.objects.get(bag_number=bag_number)
    conns = b.connection_set.all() 
    for conn in conns:
        conn.remove(b)
    return True
