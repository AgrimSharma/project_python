from django.contrib.admin import widgets

from django import forms
from location.models import ServiceCenter, City, Zone, State
from customer.models import Customer, Product

class GenericQueryForm(forms.Form):
    SC_CHOICES = [(sc.id, sc.center_name) for sc in ServiceCenter.objects.all().order_by('center_name')]
    CUSTOMERS = [(customer.id, customer.name) for customer in Customer.objects.filter(activation_status=True).order_by('name')]
    #CITIES = [(city.id, city.city_name) for city in City.objects.all().order_by('city_name')]
    ZONES = [(zone.id, zone.zone_name) for zone in Zone.objects.all().order_by('zone_name')]
    DEST_ZONES = [(zone.id, zone.zone_name) for zone in Zone.objects.all().order_by('zone_name')]
    STATES = [(state.id, state.state_name) for state in State.objects.all().order_by('state_name')]
    PRODUCTS = [(product.id, product.product_name) for product in Product.objects.all().order_by('product_name')]
    STATES = [(state.id, state.state_name) for state in State.objects.all().order_by('state_name')]
    STATUS_CHOICES = [(9, 'Delivered'), (8, 'Undelivered'), (10, "Returned")]

    SC_CHOICES.insert(0, ('','-----'))
    CUSTOMERS.insert(0, ('', '-----'))
    #CITIES.insert(0, ('', '-----'))
    #ZONES.insert(0, ('', '-----'))
    STATES.insert(0, ('', '-----'))
    PRODUCTS.insert(0, ('', '-----'))
    STATUS_CHOICES.insert(0, ('', '-----'))

    origin = forms.ChoiceField(choices=SC_CHOICES, required=False)
    shipper = forms.ChoiceField(choices=CUSTOMERS, required=False)
    zone = forms.ChoiceField(choices=ZONES, required=False)
    destination_zone = forms.ChoiceField(choices=DEST_ZONES, required=False)
    #city = forms.ChoiceField(choices=CITIES, required=False)
    destination = forms.ChoiceField(choices=SC_CHOICES, required=False)
    origin_state = forms.ChoiceField(choices=STATES, required=False)
    destination_state = forms.ChoiceField(choices=STATES, required=False)
    pickup_date_from = forms.DateField(widget=widgets.AdminDateWidget, required=True)
    pickup_date_to = forms.DateField(widget=widgets.AdminDateWidget, required=True)
    product_type = forms.ChoiceField(choices=PRODUCTS, required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)

    def clean(self):
        cleaned_data = super(GenericQueryForm, self).clean()
        pickup_date_from = cleaned_data.get('pickup_date_from', None)
        pickup_date_to = cleaned_data.get('pickup_date_to', None)
        if pickup_date_from and pickup_date_to:
            if pickup_date_from.month != pickup_date_to.month:
                raise forms.ValidationError('Both date should be from same month!')
        return cleaned_data


class CallCentreEntryForm(forms.Form):
    call_centre_date = forms.DateField(required=True)
