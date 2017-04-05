from django.db import models
from service_centre.models import Shipment
from location.models import *
from customer.models import Customer
from authentication.models import EmployeeMaster
from ecomexpress import settings
from ecomm_admin.models import *


class WeigthUpdateHistory(models.Model):
    airwaybill_number=models.BigIntegerField(db_index=True)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    update_date = models.DateField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now_add=True)
    length=models.FloatField(default=0.0, null=True, blank=True)
    breadth=models.FloatField(default=0.0, null=True, blank=True)
    height=models.FloatField(default=0.0, null=True, blank=True) 
    actual_weight=models.FloatField(default=0.0, null=True, blank=True)
    volumetric_weight=models.FloatField(default=0.0, null=True, blank=True)
    volume = models.IntegerField(default=0, null=True, blank=True)
    employee_code = models.CharField(default=0, max_length=100, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True, db_index=True)

class ServiceCentreAPI(models.Model):
    shipment = models.ForeignKey(Shipment)
    status = models.IntegerField(max_length=1,default=0,db_index=True)
    added_on = models.DateTimeField(auto_now_add = True)
    updated_on = models.DateTimeField(null=True)
    api_user_name = models.CharField(max_length=100)
    rts_by_employee_code = models.ForeignKey(EmployeeMaster)
    remarks = models.CharField(max_length=100)
