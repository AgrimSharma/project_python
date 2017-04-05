from django.db import models
from service_centre.models import *


# Create your models here.
class PickupAPIShipment(models.Model):
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    airwaybill_number=models.CharField(max_length=10, null=True, blank=True)
    pickup= models.ForeignKey(PickupRegistration, null=True, blank=True) # 
    ref_pickup=models.CharField(max_length=20, null=True, blank=True)  #Reference Pickup from API
    status=models.IntegerField(default=0, null=True, blank=True)  #0-> registered, #1-> completed, #2-> closed
    pickup_status=models.BooleanField(default=False)
    employee_code= models.ForeignKey(EmployeeMaster, null=True, blank=True)
    customer=models.ForeignKey(Customer, null=True, blank=True)  

class PickupAPIAWB(models.Model):
    airwaybill_number=models.CharField(max_length=10, null=True, blank=True)
    pickup_id=models.CharField(max_length=10, null=True, blank=True)
    
class PickupAPIHistory(models.Model):
    airwaybill_number=models.CharField(db_index=True,max_length=10, null=True, blank=True)
    ref_pickup=models.CharField(db_index=True,max_length=20, null=True, blank=True) 
    pickup=models.CharField(db_index=True,max_length=20, null=True, blank=True) 
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    shipper_code=models.CharField(max_length=10, null=True, blank=True)
    shipper_name=models.CharField(max_length=10, null=True, blank=True)
    username=models.CharField(max_length=10, null=True, blank=True)
    pickupstatus=models.CharField(max_length=10, null=True, blank=True)
    attempt_date=models.DateTimeField(null=True, blank=True)
    freight_status=models.BooleanField(default=False)
    freight_amount=models.CharField(max_length=10, null=True, blank=True)
    freight_collected=models.CharField(max_length=10, null=True, blank=True)
    server_date_time=models.CharField(max_length=30, null=True, blank=True)
    assignment_number=models.CharField(max_length=30, null=True, blank=True)
