import datetime

from math import ceil

from django.db.models import *
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User

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

class ShipmentDamageStatus(models.Model):
	shipment = models.ForeignKey(Shipment)
	status = models.IntegerField(max_length=1,default=0,db_index=True)
	recovered_amount = models.DecimalField(max_digits=8, decimal_places=2)
	recovery_from = models.CharField(max_length=100)
	added_on = models.DateTimeField(auto_now_add = True)
	updated_on = models.DateTimeField(auto_now=True)
	recovery_address = models.CharField(max_length=200)
	recovery_name = models.CharField(max_length=50)
	recovery_mobile = models.IntegerField(max_length=12, null=True, blank=True)
	actual_amount =  models.DecimalField(max_digits=8, decimal_places=2)
	recovery_recipt_number = models.CharField(max_length=100)
 	employee_code = models.ForeignKey(EmployeeMaster)
	sold_date = models.DateField(null=True, blank=True)
#  	employee_code = models.CharField(max_length=10)
