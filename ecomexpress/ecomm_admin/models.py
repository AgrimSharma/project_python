from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import ForeignKey

from location.models import *

class Brentrate(models.Model):
    min_brent_rate      = models.FloatField(blank=True,null=True, default=109, help_text="Minimum crude oil per barrel in $")
    min_fuel_surcharge  = models.FloatField(blank=True,null=True, default=20, help_text="Minimum Rate applicable in %")
    fuel_cost_increase          = models.FloatField(default=4, help_text="$/Barrel increase ($)")
    percentage_increase         = models.FloatField(default=2.5, help_text="Increase in fuel Surcharge (%)")
    todays_rate                = models.FloatField()
    todays_date                = models.DateField()
    rate_date = models.DateField(auto_now_add=True)
    def __unicode__(self):
        return str(self.todays_date) + " - $" + str(self.todays_rate)

class BrentrateHistory(models.Model):
    current_rate                = models.FloatField()
    rate_date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.current_rate

class Legality(models.Model):
    legality_type= models.CharField(max_length=40)

    def __unicode__(self):
        return self.legality_type

class ValueAddedCargoHandlingSurcharge(models.Model):
    ratio                   = models.FloatField(blank=True,null=True)
    min_cost                = models.FloatField(blank=True,null=True)
    cost_increase           = models.FloatField()
    percentage_cost_increase= models.FloatField()

class SOPDays(models.Model):
    default_min_amt = models.FloatField(max_length=5)
    default_rate = models.FloatField(max_length=5)
    default_slab = models.IntegerField(max_length=5)

class ShipmentStatusMaster(models.Model):
    code = models.IntegerField(max_length=5)
    code_description = models.CharField(max_length=200)
    code_redirect = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return str(self.code) + " - " + self.code_description

    class Meta:
        ordering = ["code"]

class PickupStatusMaster(models.Model):
    code = models.IntegerField(max_length=5)
    code_description = models.CharField(max_length=200)
    code_redirect = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return str(self.code) + ":" + self.code_description

class Mode(models.Model):
    mode = models.IntegerField(max_length=1)
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return str(self.name)

class BrandedFleet(models.Model):
    rate = models.FloatField(max_length=5)
    type = models.CharField(max_length=200)
    def __unicode__(self):
        return str(self.rate) + ":" + self.type

class BrandedFullTimeEmployee(models.Model):
    rate = models.FloatField(max_length=5)
    type = models.CharField(max_length=200)
    def __unicode__(self):
        return str(self.rate) + ":" + self.type

class Coloader(models.Model):
    name = models.CharField(max_length=200)
    type = models.IntegerField(max_length=0)
    def __unicode__(self):
        return str(self.name)

class HolidayMaster(models.Model):
    date=models.DateField()
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=300, null=True, blank=True)

class ServiceTax(models.Model):
    date                   = models.DateField()
    name                   = models.CharField(max_length=50)
    tax_in_percentage      = models.FloatField(blank=True,null=True)

class ChangeLogManager(models.Manager):

    def get_previous_value(self, obj, field_name, n=0):
        obj_type = ContentType.objects.get_for_model(obj)
        cl = ChangeLogs.objects.filter(content_type__id=obj_type.id,
                field_name=field_name, object_id=obj.id).order_by('-updated_on')
        if cl.exists():
            return cl[int(n)].change_message
        else:
            return None

    def exist_field(self, obj, field_name):
        obj_type = ContentType.objects.get_for_model(obj)
        return ChangeLogs.objects.filter(content_type__id=obj_type.id,
                field_name=field_name, object_id=obj.id).exists()

    def get_changes_list(self, obj, field_name):
        obj_type = ContentType.objects.get_for_model(obj)
        return ChangeLogs.objects.filter(content_type__id=obj_type.id,
                field_name=field_name, object_id=obj.id).order_by('-updated_on').\
                        values_list('change_message', flat=True)

    def get_shipment_changes(self):
        obj_type = ContentType.objects.get(app_label='service_centre', model='shipment')
        return ChangeLogs.objects.filter(content_type=obj_type)

    def get_object_changes(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        return ChangeLogs.objects.filter(content_type__id=obj_type.id,
                object_id=obj.id).order_by('-updated_on').\
                        values_list('change_message', flat=True)

class ChangeLogs(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    customer = models.ForeignKey('customer.Customer')
    field_name = models.CharField(max_length=100)
    change_message = models.TextField(blank=True, null=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    remittance_status = models.IntegerField(max_length=2, null=True, blank=True)
    status_intime = models.IntegerField(max_length=2, null=True, blank=True)

    objects = ChangeLogManager()

def get_fk_model(model, fieldname):
    '''returns None if not foreignkey, otherswise the relevant model'''
    field_object, model, direct, m2m = model._meta.get_field_by_name(fieldname)
    if not m2m and direct and isinstance(field_object, ForeignKey):
        return field_object.rel.to
    return None

def update_changelog(obj, field_name, customer, user, value):
    fk_model = get_fk_model(obj, field_name)

    remittance_status = None
    if obj._meta.object_name == 'Shipment' and obj.product_type == "cod":
        remittance_status = obj.codcharge_set.get().remittance_status

    if not ChangeLogs.objects.exist_field(obj, field_name):
        # create an initial change log with existing value and then create
        # change log with given value
        if fk_model:
            cm = obj.__dict__[field_name+'_id']
        else:
            cm = obj.__dict__[field_name]

        ChangeLogs.objects.create(customer=customer, user=user,
            field_name=field_name, content_object=obj,
            change_message=cm, status_intime=obj.status,
            remittance_status=remittance_status)

    prev_value = ChangeLogs.objects.get_previous_value(obj, field_name)
    if prev_value == str(value):
        return

    ChangeLogs.objects.create(customer=customer, user=user,
            field_name=field_name, content_object=obj,
            change_message=value, status_intime=obj.status,
            remittance_status=remittance_status)

def update_shipment_changelog(shipment, field_name, user, current_value, prev_value=''):
    if not shipment._meta.object_name == 'Shipment':
        return False

    if shipment.product_type == "cod":
        remittance_status = shipment.codcharge_set.get().remittance_status
    else:
        remittance_status = None

    if not ChangeLogs.objects.exist_field(shipment, field_name):
        # create an initial change log with existing value and then create
        # change log with given value
        ChangeLogs.objects.create(customer=shipment.shipper, user=user,
            field_name=field_name, content_object=shipment,
            change_message=prev_value, status_intime=shipment.status,
            remittance_status=remittance_status)

    if not prev_value:
        prev_value = ChangeLogs.objects.get_previous_value(shipment, field_name)

    if prev_value == str(current_value):
        return False

    ChangeLogs.objects.create(customer=shipment.shipper, user=user,
            field_name=field_name, content_object=shipment,
            change_message=current_value, status_intime=shipment.status,
            remittance_status=remittance_status)
    return True
