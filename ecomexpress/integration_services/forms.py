import datetime

from django import forms

from customer.models import Shipper, ShipperMapping, Customer
from location.models import Pincode, Address, ServiceCenter
from integration_services.utils import get_or_create_vendor
from .models import PickupEnroll


class PickupEnrollForm(forms.ModelForm):
    """
    Frontend for the PickupEnroll model
    """
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(activation_status=True),
        widget=forms.Select(attrs={'class': 'form-control'}))
    delivery_service_centre = forms.ModelChoiceField(
        queryset=ServiceCenter.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))
    vendor_name = forms.CharField(widget=forms.TextInput(attrs={'size': 10, 'class': 'form-control'}))
    pincode = forms.CharField(widget=forms.TextInput(attrs={'size': 10, 'class': 'form-control'}))
    shipment_count = forms.CharField(widget=forms.TextInput(attrs={'size': 10, 'class': 'form-control', 'value': 0}))
    pickup_date = forms.DateField(widget=forms.TextInput(attrs={'size': 10, 'class': 'form-control'}))

    class Meta:
        model = PickupEnroll
        fields = [
            'customer', 'pincode', 'delivery_service_centre', 'vendor_name', 
            'address', 'shipment_count', 'pickup_date']

    def clean_pincode(self):
         cleaned_data = super(PickupEnrollForm, self).clean()
         pincode = cleaned_data.get("pincode")

         import re
         # pattern = re.compile(r'(^|[1-9])[0-9]{4}($|[1-9])')
	 pattern = re.compile(r'[1-9][0-9][0-9][0-9][0-9][1-9]')
         if not pattern.match(pincode):
             # Only accept if Pincode is 6 digits and
             # doesn't start or end with 0 
             raise forms.ValidationError("Incorrect pincode format")

         return pincode

    def clean_pickup_date(self):
         cleaned_data = super(PickupEnrollForm, self).clean()
         pickup_date = cleaned_data.get("pickup_date")
         
         if not pickup_date >= datetime.date.today():
             raise forms.ValidationError("Pickup date can't be in the past")
 
         return pickup_date


    def save(self, user):
        pickup_enroll = super(PickupEnrollForm, self).save(commit=False)
        pickup_enroll.created_by = user.employeemaster
        
        # get shipper. if vendor name & pincode combination exists 
        # use it else create it
        shipper = get_or_create_vendor(
            name=pickup_enroll.vendor_name, customer=pickup_enroll.customer, 
            pincode=pickup_enroll.pincode, address=pickup_enroll.address)
        pickup_enroll.shipper = shipper
        pickup_enroll.save()
        return pickup_enroll
