#===============================================================================
# Copyright, 2012, All Rights Reserved. 
# File Name:views.py
# Project Name:ecomm express
# To create forms for location module
# Revision: 1
# Developer: Vish Gite
#===============================================================================


from django import forms
from location.models import *
from django.forms.extras.widgets import *

class RegionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RegionForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = Region
        

class ZoneForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ZoneForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = Zone
        

class StateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = State
        


class CityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CityForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = City
        


class BranchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = Branch
        
        
        
class AreaMasterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AreaMasterForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = AreaMaster
        
        
class ServiceCenterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceCenterForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = ServiceCenter
        


class PinRoutesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PinRoutesForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = PinRoutes 
        
        
class PincodeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PincodeForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = Pincode       
    
class Address2Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(Address2Form, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = Address2  
    
class AddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.label = field.label+ " *"
                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
                        
    class Meta:
        model = Address       

    def save(self, commit=True):
        address = super(AddressForm, self).save(commit=False)

        address.address1 = self.cleaned_data['address1']
        address.address2 = self.cleaned_data['address2']
        address.address3 = self.cleaned_data['address3']
        address.address4 = self.cleaned_data['address4']
        address.pincode = self.cleaned_data['pincode']
        address.phone = self.cleaned_data['phone']
        address.city = self.cleaned_data['city']
        address.state = self.cleaned_data['state']

        if commit:
            address.save()
            return address

class ContactForm(forms.ModelForm):
    date_of_birth = forms.DateField(input_formats=['%d/%m/%Y'], required=False)
#    date_of_birth = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'), input_formats=('%d/%m/%Y',))
    
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['date_of_birth'].widget.format = '%d/%m/%Y'
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    if field.required:
#                        field.widget = forms.TextInput(attrs={'class': 'input-medium'})
            
        self.fields['date_of_birth'].widget.format = '%d/%m/%Y'                    
    class Meta:
        model = Contact       

    


