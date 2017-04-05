from django.db.models import *

from authentication.models import EmployeeMaster
from pickup.models import *
from service_centre.models import *

# Create your models here.
class ItemInformation(models.Model):
    '''
    <ItemID>
    <CartonQuantity>
    <PalletQuantity>
    '''
    itemid = models.CharField(max_length=15, db_index=True)
    cartonquantity = models.IntegerField(max_length=15)
    palletquantity = models.IntegerField(max_length=15)
	

class ShipmentStatus(models.Model):
    '''
    Contains ItemInformation
    '''
    shipmentidentification = models.ForeignKey(Shipment, related_name="am_status_shipment")
    # locationcode = models.ForeignKey(shipmenthistory_date)	# shipmenthistory_date.current_sc_id

    # <ShipmentStatusInformation>
    # statuscategory = models.ForeignKey(Shipment)	# status_type
    status = models.ForeignKey(Shipment)	# status Shipment Status Code. All possible status codes are in Status_Code tab
    referenceid = models.ForeignKey(Pickup, related_name="am_status_pickup")	# PICKUP_MANIFEST_ID
    statusreason = models.ForeignKey(Shipment)	# Shipment Status Reason Code. All possible status reason code are in Status_Reason_Code tab 

    appointmentstatus = models.CharField() 
    appointmentstatusreason = models.CharField()
    
    # Add fields that can't be mapped as foreignkeys to database.
    recipientidentifier = models.CharField(default="AMAZON")	# Always AMAZON
    messagereferencenum = models.CharField()	# CharField
    amazonreferencenumber = models.CharField()	# ARN - Amazon Reference Number

    # <TransportInformation>
    stagecode = models.CharField(null=True, blank=True)
    trailernumber = models.CharField(null=True, blank=True)
    transportmode = models.CharField()    # Reference of Ship Method. It can be the ship method name from the manifest
    carrierscac = models.CharField(max_length=20)	# SCAC code of the carrier
    sealnumber = models.CharField(null=True, blank=True)

    # <PurchaseOrderSeq>		
    purchaseordernumber = models.IntegerField(null=True, blank=True)
    
    # <DateTimePeriodInformation>
    datetimeperiodcode = models.ForeignKey(EstimatedDeliveryDateTime)
    datetimeperioddescription =  models.ForeignKey(EstimatedDeliveryDateTime)
    datetimeperiodformat = models.ForeignKey(EstimatedDeliveryDateTime)
    datetimeperiodvalue = models.DateTimeField(max_length=14)

    # <<EstimatedDeliveryDateTime>
    estimateddeliverydatetime = models.ForeignKey(EstimatedDeliveryDateTime)
       
    # <TransportEquipmentInformation>
    equipmentcode = models.CharField(null=True, blank=True)
    equipmenttype = models.CharField(null=True, blank=True)

    # <MeasurementInformation>
    measurementcode = models.CharField(null=True, blank=True)
    measurementvalue = models.IntegerField(null=True, blank=True)
    grossweightuom = models.CharField(null=True, blank=True)
    grossweightvalue = models.FloatField(null=True, blank=True)
    measurementinformation = models.TextField(null=True, blank=True)

    iteminformation = models.ForeignKey(ItemInformation)
    # <ShipmentReferenceSequence>
        # <ShipmentReference>
    referenceid = models.CharField(null=True, blank=True)
    referenceidtype = models.CharField(null=True, blank=True)

    # <LadingHandlingReqSeq>
        # <LadingHandlingRequirements>
    handlingcode = models.CharField(null=True, blank=True)
    specialservicescode = models.CharField(null=True. blank=True)
    handlingdescription = models.TextField(null=True, blank=True)
    # <LadingExceptionSeq>
        # <LadingException>
    ladingexceptioncode = models.CharField(max_length=20, null=True, blank=True)
    packagingformcode = models.CharField(max_length=20, null=True, blank=True)
    ladingquantity = models.IntegerField(max_length=10, null=True, blank=True)

    @property
    def get_locationcode(self, date_time):
        # date = check date in proper format.
        # if format improper, return error
        # else check shipmenthistory_date.current_sc_id
        try:
            ship_date = datetime.datetime.strftime(date_time, "%Y_%m")
	except:
	    return "Invalid date"

	from django.db.models import get_model
	ship_hists = get_model('service_centre', 'ShipmentHistory_'+ship_date)
	ships = ship_hists.filter(shipment=self.shipmentidentification)
	return [ship.current_sc_id for ship in ships if ship.updated_on==date_time][0]


class ShipmentInfo(models.Model):
    '''
    Contains ShipmentStatus objects
    '''
    messagereferencenum = models.IntegerField(max_length=15)
    # carriertrackingnum = models.ForeignKey(airwaybill.AirwaybillNumbers)
    amazonreferencenumber = models.IntegerField(max_length=15)
    shipment_status = models.ForeignKey(ShipmentStatus)


class EstimatedDeliveryDateTime(models.Model):
    '''
    <EstimatedDeliveryDateTime>
    '''
    datetimeperiodcode = models.IntegerField(default=203)
    estimateddeliverydatetimetz = models.CharField(default="IST")
    estimateddeliverydatetimeformat = models.CharField(default="YYYYMMDDHHMMSS")
    estimateddeliverydatetimevalue = models.DateTimeField(max_length=14)

