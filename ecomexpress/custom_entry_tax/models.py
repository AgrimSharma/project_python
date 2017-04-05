from django.db import models
from service_centre.models import *
# Create your models here.


class EntryTaxItems(models.Model):
  name=models.CharField(max_length=200)
  def __unicode__(self):
        return self.name

class EntrytaxModule(models.Model):
  service_center=models.ManyToManyField(ServiceCenter,related_name="applicable_sc")
  handling_sc=models.ForeignKey(ServiceCenter)
  name_of_tax=models.CharField(max_length=30)
  default_charge=models.FloatField()
  ecomm_charge=models.FloatField(default=5.0)
  restricted_items=models.ManyToManyField(EntryTaxItems,related_name="restricted_items")
  excluded_items=models.ManyToManyField(EntryTaxItems,related_name="excluded_items")
  def __unicode__(self):
        return self.name_of_tax
 
class CustomEntryTax(models.Model):
   customer= models.ForeignKey(Customer)
   custom_tax_rate=models.FloatField()
   custom_tax_handling_charges=models.FloatField(help_text="Handling charges per Rs 100. Eg:- 5 means Handling  charges of Rs 5 per Rs 100")
   tax_name=models.ForeignKey(EntrytaxModule)
   def __unicode__(self):
        return self.customer.name+" - "+self.tax_name.name_of_tax


class CustomEntryTaxConfirmation(models.Model):
    custom_entrytax=models.ForeignKey(CustomEntryTax)
    airportconfirmation = models.ForeignKey(AirportConfirmation,related_name="custom_airport_confirmation")
    shipment = models.ForeignKey(Shipment, unique=True)
    status = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter)


class CustomTax(models.Model):
    shipper = models.ForeignKey(Customer, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add = True)
    origin = models.ForeignKey(ServiceCenter)
    custom_entrytax=models.ForeignKey(CustomEntryTax)
    slip_no = models.CharField(max_length=100,null=True, blank=True)
    date = models.DateField(auto_now_add = True, null=True, blank=True)
    total_amount = models.IntegerField(default=0, null=True, blank=True)
    total_ship = models.IntegerField(default=0)
    status = models.IntegerField(default=0)

class CustomTaxShipments(models.Model):
    custom_entrytax=models.ForeignKey(CustomTax)
    shipment = models.ForeignKey(Shipment, unique=True)
    serial_no = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    shipper = models.ForeignKey(Customer, null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter)
    status = models.IntegerField(default=0) #0-charges are not yet added, 1-charges added
    receipt_number = models.CharField(max_length=20, default="")


#class CustomTax(models.Model):
 #   shipper = models.ForeignKey(Customer, null=True, blank=True)
  #  added_on = models.DateTimeField(auto_now_add = True)
  #  origin = models.ForeignKey(ServiceCenter)
  #  custom_entrytax=models.ForeignKey(CustomEntryTax)
  #  slip_no = models.CharField(max_length=100,null=True, blank=True)
  #  date = models.DateField(auto_now_add = True, null=True, blank=True)
  #  total_amount = models.IntegerField(default=0, null=True, blank=True)
  #  total_ship = models.IntegerField(default=0)
  #  status = models.IntegerField(default=0)


class CustomTaxBilling(models.Model):
    customer = models.ForeignKey(Customer)
    service_tax = models.FloatField(null=True, blank=True, default=0)
    education_secondary_tax = models.FloatField(null=True, blank=True, default=0)
    cess_higher_secondary_tax = models.FloatField(null=True, blank=True, default=0)
    bill_generation_date = models.DateTimeField(null=True, blank=True)
    billing_date = models.DateField(null=True, blank=True)
    billing_date_from = models.DateField(null=True, blank=True)
    total_charge_pretax = models.FloatField(null=True, blank=True, default=0)
    total_payable_charge = models.FloatField(null=True, blank=True, default=0)
    balance = models.FloatField(null=True, blank=True, default=0)
    received = models.FloatField(null=True, blank=True, default=0)
    adjustment = models.FloatField(null=True, blank=True, default=0)
    adjustment_cr = models.FloatField(null=True, blank=True, default=0)
    shipments=models.ManyToManyField(CustomTaxShipments)
    custom_tax=models.ForeignKey(CustomTax)
    ecomm_charge=models.FloatField(null=True, blank=True, default=0)
