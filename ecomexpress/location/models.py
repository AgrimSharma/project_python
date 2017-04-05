#===============================================================================
# Copyright, 2012, All Rights Reserved.
# File Name:views.py
# Project Name:ecomm
# models in the customer module
# Revision: 1
# Developer: Jignesh Vasani
#===============================================================================

from django.db import models
from ecomm_admin.models import Mode
from ecomm_admin.models import *


class Region(models.Model):
    region_name        = models.CharField(max_length=30)
    region_shortcode   = models.CharField(max_length=20)

    def __unicode__(self):
        return self.region_name

class ZoneLabel(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name 

    def __unicode__(self):
        return self.name  

class Zone(models.Model):
    LOCATION_TYPE_CHOICES = ((0,"Regular Location"),(1,"UP Location"))
    zone_name       = models.CharField(max_length=30)
    zone_shortcode  = models.CharField(max_length=20)
    code  = models.CharField(max_length=2, null=True, blank=True)
    label           = models.ForeignKey(ZoneLabel, null=True, blank=True)
    location_type = models.SmallIntegerField(max_length=1, choices=LOCATION_TYPE_CHOICES, default=0)

    def __unicode__(self):
        return self.zone_name

class State(models.Model):
    state_name      = models.CharField(max_length=30)
    state_shortcode = models.CharField(max_length=20)

    def __unicode__(self):
        return self.state_name

class City(models.Model):
    city_name       = models.CharField(max_length=30)
    city_shortcode  = models.CharField(max_length=30)
    state           = models.ForeignKey(State)
    zone            = models.ForeignKey(Zone)
    region          = models.ForeignKey(Region)
    labeled_zones   = models.ManyToManyField(Zone, related_name='label_city')

    def __unicode__(self):
        return self.city_name

class Branch(models.Model):
    TYPE_CHOICES    = (('HeadOffice','HeadOffice'),
                       ('Branch','Branch'),)
    branch_name     = models.CharField(max_length=30)
    branch_shortcode= models.CharField(max_length=30)
    branch_type     = models.CharField(max_length=13,choices=TYPE_CHOICES,default=1)
    city            = models.ForeignKey(City)
    #employees will be mapped to this branch.

    def __unicode__(self):
        return self.branch_name

class AreaMaster(models.Model):
    area_name       = models.CharField(max_length=30)
    area_shortcode  = models.CharField(max_length=30)
    branch          = models.ForeignKey(Branch)
    city            = models.ForeignKey(City)

    def __unicode__(self):
        return self.area_name

class Address(models.Model):
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, default="", blank=True)
    address3 = models.CharField(max_length=100, default="", blank=True)
    address4 = models.CharField(max_length=100, default="", blank=True)
    city     = models.ForeignKey(City)
    state    = models.ForeignKey(State)
    pincode  = models.CharField(max_length=15, default="", blank=True)
    phone = models.CharField(max_length=100, default="", blank=True)

    def __unicode__(self):
        return self.address1 + ", " + self.address2 + ", " + self.address3 + ", " + self.address4 + ", " + str(self.city) + ", " + str(self.state) + ", " + str(self.pincode)

    def get_fields(self):
       return [(field.name, field.value_to_string(self)) for field in Address._meta.fields]

class Address2(models.Model):
    address1 = models.CharField(max_length=100,)
    address2 = models.CharField(max_length=100, default="", blank=True)
    address3 = models.CharField(max_length=100, default="", blank=True)
    address4 = models.CharField(max_length=100, default="", blank=True)
    city     = models.CharField(max_length=100, default="", blank=True)
    state    = models.CharField(max_length=100, default="", blank=True)
    pincode  = models.CharField(max_length=100, default="", blank=True)
    phone = models.CharField(max_length=100, default="", blank=True)
    def __unicode__(self):
        return self.address1 + ", " + self.address2 + ", " + self.address3 + ", " + self.address4 + ", " + str(self.city) + ", " + str(self.state) + ", " + str(self.pincode) + ", Phone:" + str(self.phone)

    def get_fields(self):
       return [(field.name, field.value_to_string(self)) for field in Address._meta.fields]

class Contact(models.Model):
    name     = models.CharField(max_length=100)
    designation = models.CharField(max_length=100,blank=True,null=True)
    email    = models.CharField(max_length=100, default="", blank=True,null=True)
    address1 = models.CharField(max_length=100, default="", blank=True,null=True)
    address2 = models.CharField(max_length=100, default="", blank=True,null=True)
    address3 = models.CharField(max_length=100, default="", blank=True,null=True)
    address4 = models.CharField(max_length=100, default="", blank=True,null=True)
    city     = models.ForeignKey(City,blank=True,null=True)
    state    = models.ForeignKey(State,blank=True,null=True)
    pincode  = models.CharField(max_length=15, default="",blank=True,null=True)
    phone = models.CharField(max_length=15, default="",blank=True,null=True)
    date_of_birth = models.DateField(default="0000-00-00",blank=True,null=True)

    def __unicode__(self):
        return self.name

class ServiceCenter(models.Model):
    TYPE_CHOICES    = ((0,'Service Centre'),
                       (1,'Hub'),
                       (2,'Head Quarter'),
                       (3,'Processing Centre'),
                       )
    center_name      = models.CharField(max_length=30)
    center_shortcode = models.CharField(max_length=30)
    address          = models.ForeignKey(Address)
    city            = models.ForeignKey(City)
    contact          = models.OneToOneField(Contact, blank=True,null=True)
    type = models.IntegerField(max_length=1, choices=TYPE_CHOICES, default=0)
    processing_center = models.BooleanField(blank=False)
    #hub  yes now


    def __unicode__(self):
        return self.center_name

    class Meta:
        ordering = ["center_shortcode"]

class HubServiceCenter(models.Model):
      hub = models.ForeignKey('ServiceCenter', related_name="hub_hubsc")
      sc = models.ForeignKey('ServiceCenter', related_name="sc_hubsc")
      status = models.IntegerField(default=0)
      added_on = models.DateTimeField(auto_now_add=True)

      class Meta:
          unique_together = ('hub','sc')

class InnerMumbaiOctroiSc(models.Model):
      sc = models.ForeignKey('ServiceCenter', related_name="inmumsc_hubsc")
      status = models.IntegerField(default=0)
      added_on = models.DateTimeField(auto_now_add=True)

class OuterMumbaiOctroiSc(models.Model):
      sc = models.ForeignKey('ServiceCenter', related_name="outmumsc_hubsc")
      status = models.IntegerField(default=0)
      added_on = models.DateTimeField(auto_now_add=True)

class PinRoutes(models.Model):
    pinroute_name   = models.CharField( max_length=50 )

    def __unicode__(self):
        return self.pinroute_name

class Pincode(models.Model):
    pincode         = models.IntegerField()
    service_center  = models.ForeignKey(ServiceCenter)
    pickup_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name='pickup')
    return_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name='return')
    pin_route       = models.ForeignKey(PinRoutes,blank=True,null=True)
    area            = models.CharField(max_length=255, default="", blank=True,null=True)
    status          = models.IntegerField(max_length=1, default=1)
    sdl             = models.IntegerField(max_length=1, default=0, help_text="Special Delivery Location. 0 is no and 1 is yes")
    date_of_discontinuance = models.DateTimeField(blank=True,null=True)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)

    def __unicode__(self):
        return str(self.pincode)


# this is for creating pickup for a pincode on dashboard of service centre defined in this 
class PickupPincodeServiceCentreMAP(models.Model):
    pincode         = models.IntegerField()
    service_center  = models.ForeignKey(ServiceCenter)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.pincode) + self.service_center.center_name

# this is for creating pickup for a pincode on dashboard of service centre defined in this 
class RTSPincodeServiceCentreMAP(models.Model):
    pincode         = models.IntegerField()
    service_center  = models.ForeignKey(ServiceCenter)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.pincode) + self.service_center.center_name

# this is for creating pickup for a pincode on dashboard of service centre defined in this 
class RTOPincodeServiceCentreMAP(models.Model):
    pincode         = models.IntegerField()
    service_center  = models.ForeignKey(ServiceCenter)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.pincode) + self.service_center.center_name







class TransitMasterGroup(models.Model):
    name = models.CharField( max_length=10 )

    def __unicode__(self):
        return str(self.name)

class TransitMaster(models.Model):
    transit_master = models.ForeignKey(TransitMasterGroup)
    org_service_center = models.ForeignKey(ServiceCenter, related_name='service_center_org', blank=True,null=True)
    dest_service_center = models.ForeignKey(ServiceCenter, related_name='service_center_dest')
    duration = models.IntegerField(max_length=1, default = 1)
    cutoff_time = models.CharField(max_length=5, default = "19:00")
    mode = models.ForeignKey(Mode)

    def __unicode__(self):
        return str(self.dest_service_center.center_name) + " - " + str(self.duration) + str(self.mode)

class ServiceCenterTransitMasterGroup(models.Model):
    transit_master_group = models.ForeignKey(TransitMasterGroup)
    service_center = models.ForeignKey(ServiceCenter)

    def __unicode__(self):
        return str(self.service_center.center_name) + " - "+ str(self.transit_master_group.name)


class TransitMasterCutOff(models.Model):
    transit_master_orignal = models.ForeignKey(TransitMasterGroup, related_name='transit_master_orignal')
    transit_master_dest = models.ForeignKey(TransitMasterGroup, related_name='transit_master_dest')
    #dest_service_center = models.ForeignKey(ServiceCenter, related_name='service_center_dest_cutoff')
    cutoff_time = models.CharField(max_length=5, default = "19:00")
    mode = models.ForeignKey(Mode)

    def __unicode__(self):
        return str(self.transit_master_orignal) + " - " + str(self.transit_master_dest)+ " - "  +str(self.cutoff_time)+ " - " + str(self.mode)


class TransitMasterClusterBased(models.Model):
    transit_master_orignal = models.ForeignKey(TransitMasterGroup, related_name='transit_master_orignal_cm')
    transit_master_dest = models.ForeignKey(TransitMasterGroup, related_name='transit_master_dest_cm')
    customer = models.ForeignKey('customer.Customer', null=True, blank=True)
    duration = models.IntegerField(max_length=1, default = 1)
    cutoff_time = models.CharField(max_length=5, default = "1900")
    mode = models.ForeignKey(Mode)
    added_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.transit_master_orignal) + " - " + str(self.transit_master_dest)+ " - "  +str(self.cutoff_time)+ " - " + str(self.mode)
