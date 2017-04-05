from django.db import models
from django.db import IntegrityError

# Create your models here.
from customer.models import *
from service_centre.models import Octroi, OctroiShipments

OCTROI_RATES = ((3.5,3.5),
                (5.5,5.5))

class CustomerOctroiCharges(models.Model):
    customer= models.ForeignKey(Customer)
    octroi_rate=models.FloatField(default=3.5, choices=OCTROI_RATES) #octroi charge
    octroi_charge=models.FloatField(help_text="Octroi handling charges per Rs 100. Eg:- 5 means Octoroi handling of Rs 5 per Rs 100") # ecomm_charge

class OctroiBilling(models.Model):
    customer = models.ForeignKey(Customer)
    bill_id = models.CharField(max_length=10, unique=True)
    octroi_charge=models.FloatField()
    octroi_ecom_charge=models.FloatField()
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
    shipments=models.ManyToManyField(OctroiShipments)

class OctroiCustomer(models.Model):
    reciept_number=models.CharField(max_length=20)
    customer= models.ForeignKey(Customer)
    octroi=models.ForeignKey(Octroi)
    number_ofshipments=models.IntegerField(default=0, null=True, blank=True)
    octroi_paid=models.FloatField()

class OctroiConnection(models.Model):
    connection = models.ForeignKey('service_centre.Connection')
    shipment = models.ForeignKey('service_centre.Shipment', unique=True)
    status = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    origin = models.ForeignKey('location.ServiceCenter')

class NFormConnection(models.Model):
    connection = models.ForeignKey('service_centre.Connection')
    shipment = models.ForeignKey('service_centre.Shipment', unique=True)
    status = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    origin = models.ForeignKey('location.ServiceCenter')


def octroi_update_for_connection(connection):
    from location.models import ServiceCenter
    bags = connection.bags.all()
    mum_sc = ServiceCenter.objects.filter(city__city_shortcode="MUM").exclude(id__in=[180, 178, 179, 192, 205, 206, 211])
    outer_mum_sc = ServiceCenter.objects.filter(id__in=[180, 178, 179, 192, 205, 206, 211])
    for bag in bags:
        for shipment in bag.shipments.filter().exclude(status=9).exclude(reason_code__code__in = [333, 888, 999]).exclude(rts_status = 2):
            if (shipment.pickup.service_centre not in mum_sc) and (shipment.service_centre in mum_sc):
                try:
                    OctroiConnection.objects.create(connection=connection, shipment=shipment, origin=connection.origin)
                except IntegrityError: 
                    pass
            elif (shipment.service_centre in outer_mum_sc):
                try:
                    NFormConnection.objects.create(connection=connection, shipment=shipment, origin=connection.origin)
                except IntegrityError: 
                    pass
    return True
