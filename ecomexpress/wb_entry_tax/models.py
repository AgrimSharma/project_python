from django.db import models
from service_centre.models import *

ENTRY_TAX_RATES = ((3.5,3.5),
                (5.5,5.5))


class WBTax(models.Model):
    shipper = models.ForeignKey(Customer, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add = True)
    origin = models.ForeignKey(ServiceCenter, related_name="wbtax_origin")
    wbtax_slip_no = models.CharField(max_length=100,null=True, blank=True)
    date = models.DateField(auto_now_add = True, null=True, blank=True)
    total_amount = models.IntegerField(default=0, null=True, blank=True)
    total_ship = models.IntegerField(default=0)
    #shipments = models.ManyToManyField('Shipment', related_name="oct_shipments")
    status = models.IntegerField(default=0)


class WBTaxShipments(models.Model):
    shipment = models.ForeignKey(Shipment, unique=True)
    wb_tax = models.ForeignKey(WBTax)
    serial_no = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    shipper = models.ForeignKey(Customer, null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter)
    #btax_billing = models.ForeignKey(WBTaxBilling, null=True, blank=True, related_name='tax_billing')
    wbtax_charge = models.FloatField(default=0,blank=True,null=True)
    wbtax_ecom_charge = models.FloatField(default=0,blank=True,null=True)
    status = models.IntegerField(default=0) #0-charges are not yet added, 1-charges added
    receipt_number = models.CharField(max_length=20, default="")
 
class WBTaxBilling(models.Model):
    customer = models.ForeignKey(Customer)
    etax_id=models.CharField(max_length=10, unique=True)
    etax_charge=models.FloatField()
    etax_ecom_charge=models.FloatField()
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
    shipments=models.ManyToManyField(WBTaxShipments)

class WestBengalAirportConfirmation(models.Model):
    airportconfirmation = models.ForeignKey(AirportConfirmation,related_name="wb_airport_confirmation")
    shipment = models.ForeignKey(Shipment, unique=True)
    status = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    origin = models.ForeignKey(ServiceCenter)

class CustomerEntryTaxHandlingCharges(models.Model):
    customer= models.ForeignKey(Customer)
    octroi_rate=models.FloatField(default=3.5, choices=ENTRY_TAX_RATES)
    octroi_charge=models.FloatField(help_text="Entry tax handling charges per Rs 100. Eg:- 5 means Entry tax handling of Rs 5 per Rs 100")

class EntryTaxCustomer(models.Model):
    reciept_number=models.CharField(max_length=20)
    customer= models.ForeignKey(Customer)
    wbtax=models.ForeignKey(WBTax)
    number_ofshipments=models.IntegerField(default=0, null=True, blank=True)
    octroi_paid=models.FloatField()#octroi_paid=models.FloatField()

