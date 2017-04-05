from django.db import models
from django.contrib.auth.models import User
from service_centre.models import Shipment
from customer.models import Customer
from authentication.models import EmployeeMaster
from ecomexpress import settings
from ecomm_admin.models import *

# Create your models here.
class Complaints(models.Model):
    ref_id = models.IntegerField()
    awb_number = models.IntegerField()
    shipment = models.ForeignKey(Shipment)
    shipper = models.ForeignKey(Customer)
    consignee_name = models.CharField(max_length=50)
    contact_mobile = models.CharField(max_length = 20,null=True, blank=True)
    contact_email = models.CharField(max_length=40, null=True, blank=True)
    complaint = models.TextField(max_length=1000)
    status=models.BooleanField(default=False)#0:open, 1:closed
    added_on=models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(EmployeeMaster, null=True, blank=True)

class ComplaintsHistory(models.Model):
    complaint = models.ForeignKey(Complaints)
    updated_on=models.DateTimeField(auto_now_add=True)
    addressed_by = models.ForeignKey(EmployeeMaster, null=True, blank=True)
    status=models.BooleanField(default=False)#1:ecomm, 0:consignee
    remarks = models.CharField(max_length=300, null=True, blank=True)

class AlternateInstruction(models.Model):
    instruction_type= models.BooleanField(default=False)#1:normal, 0:alternate
    employee_code = models.ForeignKey(EmployeeMaster, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time=models.TimeField(null=True, blank=True)
    shipments = models.ManyToManyField(Shipment)
    comments = models.CharField(max_length=500, null=True, blank=True)

class BatchInstruction(models.Model):
    file_name=models.CharField(max_length=100, blank=True, null=True)
    file_path = models.FileField(max_length=255, upload_to=settings.FILE_UPLOAD_TEMP_DIR, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add=True)
    employee_code = models.ForeignKey(EmployeeMaster, null=True, blank=True)

class BatchInstructionAWB(models.Model):
    batch_instruction= models.ForeignKey(BatchInstruction, null=True, blank=True)
    shipments = models.ForeignKey(Shipment)

class InstructionAWB(models.Model):
    batch_instruction = models.ForeignKey(BatchInstructionAWB, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add=True)
    instruction = models.CharField(max_length=500, null=True, blank=True)
    status=models.BooleanField(default=False)#1:updates, 0:not updated
    reason_code = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True)

class RTOInstructionUpdate(models.Model):
    shipment = models.ForeignKey(Shipment)
    modified_by = models.ForeignKey(User)
    alternateinstruction = models.ForeignKey(AlternateInstruction)
    updated_at = models.DateTimeField(auto_now=True)

class TeleCallingReport(models.Model):
    shipment = models.ForeignKey(Shipment)
    added_on=models.DateField(auto_now_add=True)
    comments = models.CharField(max_length=300)
    updated_by = models.ForeignKey(EmployeeMaster, null=True, blank=True)

class CallCentreComment(models.Model):
    employee_code = models.ForeignKey(EmployeeMaster, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    shipments = models.ForeignKey(Shipment)
    comments = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
