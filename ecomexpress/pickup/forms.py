'''
Created on Sep 27, 2012

@author: Sirius
'''
from django import forms
from pickup.models import *
from customer.models import Customer
from django.contrib.admin import widgets
from pickup.time import SelectTimeWidget


#class PickupForm(forms.ModelForm):
#    def __init__(self, *args, **kwargs):
#        super(PickupForm, self).__init__(*args, **kwargs)
#        #self.fields['customer_code']=forms.ModelChoiceField(queryset=Customer.objects.filter())
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    if field.required:
#                      if field.label == "Total weight":
#                          field.label = field.label + " (gms)"
#                        
#                      field.label = field.label + "*"  
#                      field.widget = forms.TextInput(attrs={'placeholder': field.label})
#                    else:
#                      field.widget = forms.TextInput(attrs={'placeholder': field.label})
#              
#  #  dob = forms.DateField(widget=SelectDateWidget(years=range(2014,1940,-1)))
#
#    class Meta:
#        model = Pickup
#        exclude = ('customer')
        
class PickupRegistrationForm(forms.ModelForm):
    #pickup_time = forms.DateField(widget=forms.DateInput(attrs={'class':'timepicker'}))
    
    def __init__(self, *args, **kwargs):
        super(PickupRegistrationForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            self.fields['pickup_time'].widget = widgets.AdminTimeWidget()
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                      if field.label == "Total weight":
                          field.label = field.label + " (gms)"
                        
                      field.label = str(field.label) + "*"  
                      field.widget = forms.TextInput(attrs={'placeholder': field.label})
                    else:
                      field.widget = forms.TextInput(attrs={'placeholder': field.label})
                    
  #  dob = forms.DateField(widget=SelectDateWidget(years=range(2014,1940,-1)))
    pickup_time = forms.TimeField(widget=SelectTimeWidget(minute_step=10, second_step=10))
    class Meta:
        model = PickupRegistration

