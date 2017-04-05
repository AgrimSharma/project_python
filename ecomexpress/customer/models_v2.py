#===============================================================================
# Copyright, 2012, All Rights Reserved.
# File Name:views.py
# Project Name:ecomm
# To create database tables for customer module
# Revision: 1
# Developer: Vish Gite
#===============================================================================
import xlrd
import os

from django.db import models
#from ecomm_admin.models import Legality
from django.contrib.auth.models import User
from authentication.models import EmployeeMaster
from ecomm_admin.models import Legality, Mode, BrandedFleet, BrandedFullTimeEmployee
from location.models import Address2, Address, ServiceCenter, Contact, Zone, Pincode, City, ZoneLabel

BILLING_CHOICES = (('Weekly','Weekly'),
                    ('Fortnight','Fortnight'), #make anothe table
                    ('Monthly','Monthly')
                   )
SHIPPER_TYPE = ((0,'Normal'),
                (1,'To Pay')
               )

class NamedUser(EmployeeMaster):
    class Meta:
        proxy=True

    def __unicode__(self):
        return self.get_name_with_employee_code()
        #return self.get_name_with_email()

class Customer(models.Model):
    name                = models.CharField(max_length=100)
    code                = models.CharField(max_length=30)
    activation_status   = models.BooleanField(blank=True)
    activation_date     = models.DateField(blank=True,null=True)
    contract_from       = models.DateField()
    contract_to         = models.DateField()
    legality            = models.ForeignKey(Legality)
    billing_schedule    = models.IntegerField(max_length=3,default=7)
    day_of_billing      = models.SmallIntegerField(default=7)
    remittance_cycle    = models.SmallIntegerField(default=7)
    credit_limit        = models.IntegerField(max_length=10,default = 10000)
    activation_by       = models.ForeignKey(User,related_name='activation_by', blank=True,null=True)
    credit_period       = models.IntegerField(max_length=3,default = 10)
    fuel_surcharge_applicable = models.BooleanField(default=True, blank=True)
    to_pay_charge       = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    vchc_rate           = models.DecimalField(max_digits=4, decimal_places=2, default=0.5)
    vchc_min            = models.DecimalField(max_digits=6, decimal_places=2, default=0.5)
    vchc_min_amnt_applied            = models.IntegerField(max_length=5,default = 5000)
    return_to_origin    = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    flat_cod_amt        = models.IntegerField(max_length=4,blank=True,null=True)
    demarrage_min_amt   = models.IntegerField(max_length=4,blank=True,null=True)
    demarrage_perkg_amt = models.IntegerField(max_length=4,blank=True,null=True)
    created_on          = models.DateTimeField(auto_now_add=True)
    created_by          = models.ForeignKey(User,related_name='created_by', blank=True,null=True)
    updated_on          = models.DateTimeField(auto_now=True)
    updated_by          = models.ForeignKey(User,related_name='updated_by', blank=True,null=True)
    address             = models.ForeignKey(Address2, blank=True,null=True)
    contact_person      = models.ForeignKey(Contact,blank=True,null=True)
    decision_maker      = models.ForeignKey(Contact, related_name="decision_maker",blank=True,null=True)
    pan_number          = models.CharField(max_length=20,blank=True,null=True)
    tan_number          = models.CharField(max_length=20,blank=True,null=True)
    website             = models.CharField(max_length=200,blank=True,null=True)
    email               = models.CharField(max_length=200,blank=True,null=True)
    #saleslead           = models.ForeignKey(User,related_name='saleslead')
    #signed              = models.ForeignKey(User,related_name='signatory')
    #approved            = models.ForeignKey(User,related_name='approver')
    #authorized          = models.ForeignKey(User,related_name='authorizer')
    saleslead           = models.ForeignKey(NamedUser,related_name='saleslead',blank=True,null=True)
    signed              = models.ForeignKey(NamedUser,related_name='signatory',blank=True,null=True)
    approved            = models.ForeignKey(NamedUser,related_name='approver',blank=True,null=True)
    authorized          = models.ForeignKey(NamedUser,related_name='authorizer',blank=True,null=True)
    bill_delivery_email = models.BooleanField(default=True)
    bill_delivery_hand  = models.BooleanField(default=True)
    invoice_date        = models.DateField(blank=True,null=True)
    next_bill_date      = models.DateField(blank=True,null=True)
    reverse_charges     = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    zone_label          = models.ForeignKey(ZoneLabel, blank=True, null=True)
    referred_by         = models.CharField(max_length=30,blank=True,null=True)

    def __unicode__(self):
        return self.name + " - " + self.code

    def get_fields(self):
       return [(field.name, field.value_to_string(self)) for field in Customer._meta.fields]

class Shipper(models.Model):
    customer   = models.ForeignKey(Customer)
    alias_code = models.CharField(max_length=10,blank=True,null=True)
    name       = models.CharField(max_length=100)
    address    = models.ForeignKey(Address, blank=True,null=True)
    type       = models.IntegerField(default=0, choices=SHIPPER_TYPE)

    def __unicode__(self):
        return self.name
    def get_fields(self):
       return [(field.name, field.value_to_string(self)) for field in Shipper._meta.fields]

class ShipperMapping(models.Model):
    shipper = models.ForeignKey(Shipper) 
    forward_pincode = models.IntegerField(max_length = 8)
    return_pincode =  models.IntegerField(max_length = 8)

class Product(models.Model):
    product_name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.product_name


class CashOnDelivery(models.Model):
    customer            = models.ForeignKey(Customer)
    COD_service_charge  = models.FloatField() #%
    start_range      = models.FloatField()
    end_range        = models.FloatField()
    flat_COD_charge     = models.FloatField()
    minimum_COD_charge     = models.FloatField()
    def __unicode__(self):
        return self.customer.name + "| Rate: "  + str(self.COD_service_charge)

class CashOnDeliveryZone(models.Model):
    customer            = models.ForeignKey(Customer)
    c_zone_org       = models.ForeignKey(Zone, related_name = "c_zone_org")
    c_zone_dest        = models.ForeignKey(Zone, related_name = "c_zone_dest")
    COD_service_charge  = models.FloatField() #%
    start_range      = models.FloatField()
    end_range        = models.FloatField()
    flat_COD_charge     = models.FloatField()
    minimum_COD_charge     = models.FloatField()
    def __unicode__(self):
        return self.customer.name + "| Rate: "  + str(self.COD_service_charge)

#to be added exception table,, field added, exception, contact, exception admin/contact, action, meaning
class FuelSurcharge(models.Model):
    customer            = models.ForeignKey(Customer)
    fuelsurcharge_min_rate      = models.FloatField()
    fuelsurcharge_min_fuel_rate = models.FloatField()
    flat_fuel_surcharge = models.FloatField(blank=True,null=True)#stored as percentage,
    max_fuel_surcharge  = models.FloatField(blank=True,null=True)

    def __unicode__(self):
        return self.customer.name

class FuelSurchargeZone(models.Model):
    fuelsurcharge    = models.ForeignKey(FuelSurcharge)
    f_zone_org       = models.ForeignKey(Zone, related_name = "f_zone_org")
    f_zone_dest        = models.ForeignKey(Zone, related_name = "f_zone_dest")
    fuelsurcharge_min_rate      = models.FloatField()
    fuelsurcharge_min_fuel_rate = models.FloatField()
    flat_fuel_surcharge = models.FloatField(blank=True, null=True)#stored as percentage,
    max_fuel_surcharge  = models.FloatField(blank=True, null=True)
    product = models.ManyToManyField(Product, blank=True, null=True)

    #def __unicode__(self):
    #    return self.fuelsurcharge.customer.name + " " + self.f_zone_org + " " + self.f_zone_dest

class FreightSlab(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
    weight_rate = models.FloatField( default=35, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    def __unicode__(self):
        return self.customer.name + " - Mode: " + str(self.mode)  + " - Slab: " + str(self.slab)  + " gms - DefaultRate: INR" + str(self.weight_rate) + " - Start: " + str(self.range_from) + " gms - End: " + str(self.range_to) + " gms"


class FreightSlabCity(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
    weight_rate = models.FloatField( default=35, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    city_org       = models.ForeignKey(City, related_name = "city_org")
    city_dest        = models.ForeignKey(City, related_name = "city_dest")
    rate_per_slab   = models.FloatField( default=20)
    product = models.ManyToManyField(Product, blank=True, null=True)

class FreightSlabOriginZone(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
    weight_rate = models.FloatField( default=35, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    org_zone    = models.ForeignKey(Zone, related_name = "org_zone")
    city_dest   = models.ForeignKey(City, related_name = "freight_city_dest")
    rate_per_slab   = models.FloatField( default=20)
    product     = models.ManyToManyField(Product, blank=True, null=True)



class FreightSlabDestZone(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
    weight_rate = models.FloatField( default=35, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    dest_zone    = models.ForeignKey(Zone, related_name = "dest_zone")
    city_org   = models.ForeignKey(City, related_name = "freight_city_org")
    rate_per_slab   = models.FloatField( default=20)
    product     = models.ManyToManyField(Product, blank=True, null=True)

class FreightSlabZone(models.Model):
    freight_slab    = models.ForeignKey(FreightSlab)
    zone_org       = models.ForeignKey(Zone, related_name = "zone_org")
    zone_dest        = models.ForeignKey(Zone, related_name = "zone_dest")
    rate_per_slab   = models.FloatField( default=20)

    def __unicode__(self):
        return str(self.freight_slab) + " - ORG Zone: " + self.zone_org.zone_name + " - DEST Zone: " + self.zone_dest.zone_name + " - Rate: " +  str(self.rate_per_slab)

#updations from Onkar begin here 8th Sept 2014

class FreightSlabZoneV2(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
    weight_rate = models.FloatField( default=35, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    zone_org       = models.ForeignKey(Zone, related_name = "zone_org")
    zone_dest        = models.ForeignKey(Zone, related_name = "zone_dest")
    rate_per_slab   = models.FloatField( default=20)

#updated phase 1/3  ends here



class FreightSlabHistory(models.Model):
      freight_slab_zone=models.ForeignKey(FreightSlabZone,blank=True,null=True)
      zone_org       = models.ForeignKey(Zone, related_name = "history_zone_org")
      zone_dest        = models.ForeignKey(Zone, related_name = "history_zone_dest")
      rate_per_slab   = models.FloatField( default=20)
      customer    = models.ForeignKey(Customer)
      mode        = models.ForeignKey(Mode)
      slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
      weight_rate = models.FloatField( default=35, help_text="Rate in INR")
      range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
      range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
      product     = models.ManyToManyField(Product, blank=True, null=True)
      active_status = models.BooleanField(default=False)
      effective_date = models.DateTimeField(null=True,blank=True)

class CODFreightSlab(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
    weight_rate = models.FloatField( default=35, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    def __unicode__(self):
        return self.customer.name + " - Mode: " + str(self.mode)  + " - Slab: " + str(self.slab)  + " gms - DefaultRate: INR" + str(self.weight_rate) + " - Start: " + str(self.range_from) + " gms - End: " + str(self.range_to) + " gms"


class CODFreightSlabZone(models.Model):
    freight_slab    = models.ForeignKey(CODFreightSlab)
    zone_org       = models.ForeignKey(Zone, related_name = "cod_zone_org")
    zone_dest        = models.ForeignKey(Zone, related_name = "cod_zone_dest")
    rate_per_slab   = models.FloatField( default=20)

    def __unicode__(self):
        return str(self.freight_slab) + " - ORG Zone: " + self.zone_org.zone_name + " - DEST Zone: " + self.zone_dest.zone_name + " - Rate: " +  str(self.rate_per_slab)

class RTSFreightSlab(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
    weight_rate = models.FloatField( default=35, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    def __unicode__(self):
        return self.customer.name + " - Mode: " + str(self.mode)  + " - Slab: " + str(self.slab)  + " gms - DefaultRate: INR" + str(self.weight_rate) + " - Start: " + str(self.range_from) + " gms - End: " + str(self.range_to) + " gms"

class RTSFreightSlabZone(models.Model):
    freight_slab    = models.ForeignKey(RTSFreightSlab)
    zone_org       = models.ForeignKey(Zone, related_name = "rts_zone_org")
    zone_dest        = models.ForeignKey(Zone, related_name = "rts_zone_dest")
    rate_per_slab   = models.FloatField( default=20)

    def __unicode__(self):
        return str(self.freight_slab) + " - ORG Zone: " + self.zone_org.zone_name + " - DEST Zone: " + self.zone_dest.zone_name + " - Rate: " +  str(self.rate_per_slab)

class ReverseFreightSlab(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
    weight_rate = models.FloatField( default=35, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    def __unicode__(self):
        return self.customer.name + " - Mode: " + str(self.mode)  + " - Slab: " + str(self.slab)  + " gms - DefaultRate: INR" + str(self.weight_rate) + " - Start: " + str(self.range_from) + " gms - End: " + str(self.range_to) + " gms"

class ReverseFreightSlabZone(models.Model):
    freight_slab    = models.ForeignKey(ReverseFreightSlab)
    zone_org       = models.ForeignKey(Zone, related_name = "rev_zone_org")
    zone_dest        = models.ForeignKey(Zone, related_name = "rev_zone_dest")
    rate_per_slab   = models.FloatField( default=20)

    def __unicode__(self):
        return str(self.freight_slab) + " - ORG Zone: " + self.zone_org.zone_name + " - DEST Zone: " + self.zone_dest.zone_name + " - Rate: " +  str(self.rate_per_slab)


class SDLSlab(models.Model):
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=1000, help_text="Weight in gms")
    weight_rate = models.IntegerField(max_length=5, default=100, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    def __unicode__(self):
        return  str(self.mode)  + " - Slab: " + str(self.slab)  + " gms - DefaultRate: INR" + str(self.weight_rate) + " - Start: " + str(self.range_from) + " gms - End: " + str(self.range_to) + " gms"

class SDDZone(models.Model):
    name      =  models.CharField(max_length=30)
    shortcode =  models.CharField(max_length=20)
    added_on  =  models.DateTimeField(auto_now_add = True)
    pincode   =  models.ManyToManyField(Pincode, related_name="sddzone_pincode")

    def __unicode__(self):
        return  str(self.name)

class SDDSlabZone(models.Model):
    freight_slab    = models.ForeignKey(FreightSlab)
    zone_org       = models.ForeignKey(Zone, blank=True,null=True, related_name = "sdd_zone_org")#not required will use sdd zone
    zone_dest        = models.ForeignKey(Zone,blank=True,null=True,  related_name = "sdd_zone_dest")
    sddzone       = models.ForeignKey(SDDZone)
    rate_per_slab   = models.FloatField( default=20)


    def __unicode__(self):
        return str(self.freight_slab) + " - Rate: " +  str(self.rate_per_slab)

#Phase 2/3 begins here updated by Onkar 2/3

class SDDSlabZoneV2(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
    weight_rate = models.FloatField( default=35, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    zone_org       = models.ForeignKey(Zone, blank=True,null=True, related_name = "sdd_zone_org")#not required will use sdd zone
    zone_dest        = models.ForeignKey(Zone,blank=True,null=True,  related_name = "sdd_zone_dest")
    sddzone       = models.ForeignKey(SDDZone)
    rate_per_slab   = models.FloatField( default=20)
    active_status = models.BooleanField(default=False)
    effective_date = models.DateTimeField(null=True,blank=True)
    activation_date=models.DateTimeField(null=True,blank=True)
    #def __unicode__(self):
    #   return str(self.freight_slab) + " - Rate: " +  str(self.rate_per_slab)

#phase 2/3 ends here


class ExceptionMaster(models.Model):
    customer        = models.ForeignKey(Customer, related_name='fk_customer')
    exception_code  = models.CharField(max_length=50)
    action          = models.CharField(max_length=50)
    meaning         = models.CharField(max_length=10)
    contact_customer= models.ForeignKey(Customer,related_name='contact_customer')
    admin_contact   = models.ForeignKey(EmployeeMaster)


class BrandedFleetCustomer(models.Model):
    customer        = models.ForeignKey(Customer)
    branded_fleet = models.ForeignKey(BrandedFleet)
    number_of_fleet = models.IntegerField(max_length=3)
    created_on      = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.customer.name) + " - Fleet Type: " + self.branded_fleet.type + " - Number: " + str(self.number_of_fleet)



class BrandedFullTimeEmployeeCustomer(models.Model):
    customer        = models.ForeignKey(Customer)
    branded_full_time_employee = models.ForeignKey(BrandedFullTimeEmployee)
    number_of_employee = models.IntegerField(max_length=3)
    created_on      = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.customer.name) + " - Fleet Type: " + self.branded_full_time_employee.type + " - Number: " + str(self.number_of_employee)


class Remittance(models.Model):
    customer        = models.ForeignKey(Customer)
    amount          = models.FloatField()
    remitted_on     = models.DateField()
    remitted_by     = models.ForeignKey(User,related_name='remitted_by', blank=True,null=True)
    updated_on       = models.DateTimeField(auto_now_add=True)
    bank_name = models.CharField(max_length=50)
    bank_ref_number = models.CharField(max_length=50)

class VolumetricWeightDivisor(models.Model):
    customer        = models.ForeignKey(Customer)
    divisor         = models.IntegerField(max_length=6, help_text='This number will be used for calculating volumetric weight')


class MinActualWeight(models.Model):
    customer        = models.ForeignKey(Customer)
    weight          = models.FloatField(help_text="Weight in Kg(s)! Minimum weight before volumetric weight to be considered")


class SDLSlabCustomer(models.Model):
    customer    = models.ForeignKey(Customer)
    mode        = models.ForeignKey(Mode)
    slab        = models.IntegerField(max_length=5, default=1000, help_text="Weight in gms")
    weight_rate = models.IntegerField(max_length=5, default=100, help_text="Rate in INR")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    def __unicode__(self):
        return  str(self.mode)  + " - Slab: " + str(self.slab)  + " gms - DefaultRate: INR" + str(self.weight_rate) + " - Start: " + str(self.range_from) + " gms - End: " + str(self.range_to) + " gms"



class CustomerAPI(models.Model):
    customer    = models.ForeignKey(Customer)
    username    = models.CharField(max_length=50, help_text="API username")
    password    = models.CharField(max_length=24,  help_text="API Password")
    ipaddress   = models.CharField(max_length=255, default=0, help_text="comma separated IP address")
    def __unicode__(self):
        return  str(self.username)

class RTSFreightZone(models.Model):
     freight_slab    = models.ForeignKey(FreightSlab)
     customer = models.ForeignKey(Customer, null=True, blank=True)
     origin = models.ForeignKey(Zone, null=True, blank=True, related_name="freight_origin")
     destination = models.ForeignKey(Zone, null=True, blank=True, related_name="freight_dest")
     rate = models.FloatField(default=0, null=True, blank=True)
     freight_charge = models.FloatField(default=0, null=True, blank=True) #percentage

     def __unicode__(self):
        return self.customer.name + " - Slab: " + str(self.freight_slab)  + " - Org: " + str(self.origin)  + " - Dest: " + str(self.destination) + " - Rate: " + str(self.rate)

#Phase 3/3 8th Sept 2014 begins
class RTSFreightZoneV2(models.Model):
     customer    = models.ForeignKey(Customer)
     mode        = models.ForeignKey(Mode)
     slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
     weight_rate = models.FloatField( default=35, help_text="Rate in INR")
     range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
     range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
     origin = models.ForeignKey(Zone, null=True, blank=True, related_name="freight_origin")
     destination = models.ForeignKey(Zone, null=True, blank=True, related_name="freight_dest")
     rate = models.FloatField(default=0, null=True, blank=True)
     freight_charge = models.FloatField(default=0, null=True, blank=True) #percentage
     active_status = models.BooleanField(default=False)
     effective_date = models.DateTimeField(null=True,blank=True)
     activation_date=models.DateTimeField(null=True,blank=True)
#Phase 3/3 8th Sept 2014 ends



class RTSFuelZone(models.Model):
     customer    = models.ForeignKey(Customer)
     mode        = models.ForeignKey(Mode)
     slab        = models.IntegerField(max_length=5, default=500, help_text="Weight in gms")
     weight_rate = models.FloatField( default=35, help_text="Rate in INR")
     range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
     range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
     origin = models.ForeignKey(Zone, null=True, blank=True, related_name="fuel_origin")
     destination = models.ForeignKey(Zone, null=True, blank=True, related_name="fuel_dest")
     rate = models.FloatField(default=0, null=True, blank=True)

class RTSFreight(models.Model):
     customer = models.ForeignKey(Customer, null=True, blank=True)
     rate = models.FloatField(default=0, null=True, blank=True)

class RTSFuel(models.Model):
     customer = models.ForeignKey(Customer, null=True, blank=True)
     rate = models.FloatField(default=0, null=True, blank=True)

class RTSFreightSlabRate(models.Model):
    customer = models.ForeignKey(Customer, null=True, blank=True)
    slab        = models.IntegerField(max_length=5, default=1000, help_text="Weight in gms")
    range_from  = models.IntegerField(max_length=6, default=0, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, default=999999, help_text="Weight in gms")
    origin = models.ForeignKey(Zone, null=True, blank=True, related_name="freightslab_origin")
    destination = models.ForeignKey(Zone, null=True, blank=True, related_name="freightslab_dest")
    rate = models.FloatField(default=0, null=True, blank=True)
    normal_applicable = models.BooleanField(blank=True)

def doc_upload_path(instance, filename):
    """
    The uploaded contacts file will be stored inside
    MEDIA_ROOT/<customer_name>/ directory
    """
    return "%s/%s" % (instance.customer.name,
                         filename.replace(' ','-'))

class CustomerReportNames(models.Model):
    customer = models.ForeignKey(Customer)
    invoice_name = models.CharField(max_length=200, null=True, blank=True)
    cash_tally_name = models.CharField(max_length=200, null=True, blank=True)

class ChargeType(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name 

class CustomerChargeMapping(models.Model):
    customer    = models.ForeignKey(Customer)
    slab        = models.IntegerField(max_length=6, help_text="Weight in gms")
    range_from  = models.IntegerField(max_length=6, help_text="Weight in gms")
    range_to    = models.IntegerField(max_length=6, help_text="Weight in gms")
    rate        = models.IntegerField(max_length=5, help_text="Weight in gms")
    charge_type = models.ForeignKey(ChargeType)
    effective_date = models.DateTimeField()


    def __unicode__(self):
        return '{0} - {1} - {2} - {3}'.format(self.customer.name, self.range_from, self.range_to, self.rate)

class SubcustomerDetailsUpload(models.Model):
     customer = models.ForeignKey(Customer)
     filepath = models.FileField(upload_to=doc_upload_path)
 
     def save(self,*args,**kwargs):
         # We are not saving subcustomer details excel files.
         # so this function is no longer used.
         super(SubcustomerDetailsUpload, self).save(*args, **kwargs)
         # TODO: check whether excel file is in correct format or not. ie the
         # fields are as specified by us.
         # update_subcustomers_list(self)
