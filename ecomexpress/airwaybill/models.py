from django.db import models
from customer.models import Customer
# Create your models here.
from django.db import models


AWB_TYPES = [
    ('1', 'PPD'),
    ('2', 'COD'),
    ('3', 'Reverse Shipment'),
    ('4', 'EBS PPD'),
    ('5', 'EBS COD'),
]

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-
    .
    updating ``created`` and ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class AirwaybillNumbers(models.Model):    
    airwaybill_number = models.BigIntegerField(unique=True)
    status = models.BooleanField(default=False)#0 unused, 1 used

class AirwaybillCustomer(models.Model):
    customer = models.ForeignKey(Customer)
    type = models.CharField(max_length=15, choices=AWB_TYPES, blank=True)
    quantity = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add = True)
    airwaybill_number = models.ManyToManyField('AirwaybillNumbers', related_name="awbc_info")
    
class PPD(models.Model):
    id = models.AutoField(primary_key=True)     
    
class PPDZero(models.Model):
    id = models.AutoField(primary_key=True)     

class COD(models.Model):
    id = models.AutoField(primary_key=True)         

class CODZero(models.Model):
    id = models.AutoField(primary_key=True)         

class ReversePickup(models.Model):
    id = models.AutoField(primary_key=True)       

class APIAwbOrderNumberHistory(models.Model):
    airwaybill_number = models.BigIntegerField(unique=True)
    order_number=models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.airwaybill_number
