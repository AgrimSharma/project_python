from django.db import models
from django.db.models import Count

from service_centre.models import Shipment


class FetchAirwayBillBatch(models.Model):
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    employee_code = models.CharField(default=0, max_length=100, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True, db_index=True)
    total_count = models.IntegerField(default=0, null=True, blank=True, db_index=True)
    processed_count = models.IntegerField(default=0, null=True, blank=True, db_index=True)
    correct_count = models.IntegerField(default=0, null=True, blank=True, db_index=True)
    not_found_count = models.IntegerField(default=0, null=True, blank=True, db_index=True)
    location = models.CharField(default='', max_length=100, null=True, blank=True)
    pincode = models.CharField(default=0, max_length=10, null=True, blank=True)

    def refresh(self):
        awbs = self.fetchairwaybill_set.filter(
            status=0).values_list('airwaybill_number', flat=True)
        for awb in awbs:
            try:
                Shipment.objects.get(airwaybill_number=awb)
                FetchAirwaybill.objects.filter(
                    airwaybill_number=awb).update(status=1)
            except Shipment.DoesNotExist:
                pass     

        return self.fetchairwaybill_set.filter(status=1).aggregate(
            ct=Count('id'))['ct']
 

class FetchAirwayBill(models.Model):
    fetch_airwaybill_batch=models.ForeignKey(FetchAirwayBillBatch)
    airwaybill_number=models.CharField(db_index=True, max_length=20)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.IntegerField(default=0, null=True, blank=True, db_index=True)


class PickupEnroll(models.Model):
    """
    New pickup registration module. Where pickup can be registered by CS people
    or using SRUTi api. 
    Once the pickup has registered, it can be updated as 'Yes' - picked up, 
    'Cancelled' - Pickup canceled or 'Reschedule' - reschedule for another day. 
    Which will be indicated by 'status' field.
    """
    customer = models.ForeignKey('customer.Customer')
    vendor_name = models.CharField(max_length=100)
    manifest_id = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    pincode = models.CharField(max_length=10)
    shipment_count = models.IntegerField(default=0)
    pickup_date = models.DateField(blank=True, null=True)
    added_on = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey('authentication.EmployeeMaster', null=True, blank=True)
    created_by = models.ForeignKey('authentication.EmployeeMaster', related_name='pickup_enroll')
    delivery_service_centre = models.ForeignKey('location.ServiceCenter')
    shipper = models.ForeignKey('customer.Shipper', related_name='pickup_enroll')
    return_subcustomer = models.ForeignKey('customer.Shipper', null=True, blank=True)
    # sruti (2) / customer service creation (1)
    request_source = models.SmallIntegerField(default=1)  
    # 0 - cancelled, 1 - created, 2 - rescheduled, 3 - complete
    status = models.SmallIntegerField(default=1)

    def __unicode__(self):
        return '{0} - {1}'.format(self.customer.name, self.get_status)

    @property
    def get_status(self):
        if self.status == 0:
            return 'Cancelled'
        elif self.status == 1:
            return 'Created'
        elif self.status == 2:
            return 'Rescheduled'
        elif self.status == 3:
            return 'Complete'
        else:
            return 'Unknown'

class Add_Coords(models.Model):
    '''
    model for Ecom_Premises Address.
    '''
    from service_centre.models import ServiceCenter
    lat = models.FloatField(max_length=10, null=False, blank=False)
    lng = models.FloatField(max_length=10, null=False, blank=False)
    dc = models.ForeignKey(ServiceCenter, unique=True)
    address = models.TextField(null=False, blank=False)

    @property
    def get_dc(self):
        return dc

    def __unicode__(self):
	return '{0} - {1}'.format(self.dc.center_name, self.address.encode('utf-8'))
