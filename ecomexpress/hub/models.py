from django.db import models
from service_centre.models import *

class Bag_shipment_table(models.Model):
    airwaybill_number=models.BigIntegerField()
    scanned_bag_number = models.CharField(max_length=20)
    original_bag_number = models.CharField(max_length=20, null = True, blank = True) 
    added_on=models.DateField(auto_now_add=True)
    current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True)
