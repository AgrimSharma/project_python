
#===============================================================================
# Copyright, 2012, All Rights Reserved. 
# File Name:views.py
# Project Name:ecomm
# To create forms for customer module
# Revision: 1
# Developer: Vish Gite
#===============================================================================

from django import forms
#from django.forms import formsets, widgets
from customer.models import *
from ecomm_admin.models import Brentrate
#from django.forms.extras.widgets import SelectDateWidget
from django.forms.models import modelformset_factory
from django.forms.widgets import HiddenInput
from django.core.exceptions import ValidationError


class AddCustomerForm(forms.ModelForm):
    day_of_billing = forms.ChoiceField()
    remittance_cycle = forms.ChoiceField()
    contract_from = forms.DateField(input_formats=['%d/%m/%Y']) 
    contract_to = forms.DateField(input_formats=['%d/%m/%Y']) 

    def __init__(self, *args, **kwargs):
        super(AddCustomerForm, self).__init__(*args, **kwargs)
        self.fields['contract_from'].widget.format = '%d/%m/%Y'
        self.fields['contract_to'].widget.format = '%d/%m/%Y'
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                        field.widget = forms.TextInput(attrs={'class':'input-medium'})

        self.fields['day_of_billing'].choices = [(i, i) for i in range(1,32,1)]
        self.fields['remittance_cycle'].choices = [(i, i) for i in range(1,8,1)]
    #contract_from = forms.DateField(widget=SelectDateWidget(years=range(2050,2000,-1)))
    #contract_to = forms.DateField(widget=SelectDateWidget(years=range(2050,2000,-1)))
    
#   def clean_name(self):
#       name = self.cleaned_data['name']
#       try:
#               Customer.objects.get(name=name)
#       except Customer.DoesNotExist:
#               return name
#       raise forms.ValidationError("Customer exists please use other.")

    
    
    class Meta:
        model = Customer
        exclude = ['fuel_surcharge_applicable','to_pay_charge','vchc_rate','vchc_min','return_to_origin','code','created_on','updated_on','created_by','updated_by', 'address','contact_person','decision_maker','activation_date', 'activation_by', 'activation_status','vchc_min_amnt_applied']        


class AddPriceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddPriceForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Customer
        exclude = ['name','code','activation_status','activation_date','activation_by','contract_from','contract_to','legality',
                   'billing_schedule','day_of_billing','credit_limit','credit_period','created_on','updated_on','created_by',
                   'updated_by', 'address','contact_person','decision_maker','activation_date', 'activation_by', 'activation_status',
                   'pan_number','tan_number','website','email','saleslead','approved','authorized','signed','bill_delivery_email',
                   'bill_delivery_hand','invoice_date','next_bill_date', 'remittance_cycle','vchc_min_amnt_applied']

class AddFreightSlabZoneForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddFreightSlabZoneForm, self).__init__(*args, **kwargs)
    class Meta:
        model = FreightSlabZone



#class CustomerWeightRateForm(forms.ModelForm):
#    customer = forms.IntegerField(widget=HiddenInput)
#    def __init__(self, *args, **kwargs):
##        self.queryset=CustomerWeightRate.objects.none()
#        super(CustomerWeightRateForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    if field.required:
#                        if "eight" in field.label and "rate" not in field.label:
#                            field.label = field.label + " (gms)"
#                        
#                        field.widget = forms.TextInput(attrs={'class':'input-small' ,'id':'prependedInput','size':5})
#                    else:
#                        field.widget = forms.TextInput(attrs={'class':'input-small' ,'id':'prependedInput','size':5})
#
#                        
#    def clean_customer(self):
#        customer_id = self.cleaned_data.get('customer',1)
#        customer    = Customer.objects.get(pk=customer_id)
#        return customer
#
#
#    class Meta:
#        model = CustomerWeightRate
        #  exclude = ('customer')

#WeightrateFormset =formsets.formset_factory(CustomerWeightRateForm, extra=5,)
#WeightrateFormset = modelformset_factory(CustomerWeightRate, CustomerWeightRateForm,extra=5)
#class CustomerDimensionRateForm(forms.ModelForm):
#    def __init__(self, *args, **kwargs):
#        super(CustomerDimensionRateForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    if field.required:
#                        field.widget = forms.TextInput(attrs={'placeholder': field.label+' (Required)'})
#                    else:
#                        field.widget = forms.TextInput(attrs={'placeholder': field.label})
#                        
#
#    
#    class Meta:
#        model = CustomerDimensionRate
#        exclude = ('customer')

        
        
#class ValueCargoHandlingChargeForm(forms.ModelForm):
#    def __init__(self, *args, **kwargs):
#        super(ValueCargoHandlingChargeForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    field.widget = forms.TextInput(attrs={'class':'input-small' ,'id':'prependedInput','size':5})
#
#    
#    class Meta:
#        model = ValueCargoHandlingCharge
#        exclude = ('customer')
        

class BrentrateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BrentrateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                        field.widget = forms.TextInput(attrs={'class':'input-small' ,'id':'prependedInput','size':5})
    
    
    class Meta:
        model = Brentrate
        exclude = ('customer')
     



        
class FuelSurchargeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FuelSurchargeForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    field.widget = forms.TextInput(attrs={'class':'input-medium'})

    
    
    class Meta:
        model = FuelSurcharge



#class BrandedVehicleRateForm(forms.ModelForm):
#    customer = forms.IntegerField(widget=HiddenInput)
#    def __init__(self, *args, **kwargs):
#        super(BrandedVehicleRateForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    field.widget = forms.TextInput(attrs={'class':'input-medium'})
#
#    
#    def clean_customer(self):
#        customer_id = self.cleaned_data.get('customer',1)
#        customer    = Customer.objects.get(pk=customer_id)
#        return customer
#                        
#    class Meta:
#        model =   BrandedVehicleRate
        
        

#class BrandedStaffRateForm(forms.ModelForm):
#    customer = forms.IntegerField(widget=HiddenInput)
#    def __init__(self, *args, **kwargs):
#        super(BrandedStaffRateForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    field.widget = forms.TextInput(attrs={'class':'input-medium'})
#
##                    if field.required:
##                        field.widget = forms.TextInput(attrs={'placeholder': field.label+' (Required)'})
##                    else:
##                        field.widget = forms.TextInput(attrs={'placeholder': field.label})
#                       
#    def clean_customer(self):
#        customer_id = self.cleaned_data.get('customer',1)
#        customer    = Customer.objects.get(pk=customer_id)
#        return customer
#                                                                                  
#    class Meta:
#        model = BrandedStaffRate
       



#class NumberOfBrandedStaffForm(forms.ModelForm):
#    def __init__(self, *args, **kwargs):
#        super(NumberOfBrandedStaffForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    field.widget = forms.TextInput(attrs={'class':'input-medium'})
#
#                                                                                                     
#    class Meta:
#        model = NumberOfBrandedStaff
#        exclude = ('customer')


#class NumberOfVehicleForm(forms.ModelForm):
#    def __init__(self, *args, **kwargs):
#        super(NumberOfVehicleForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    field.widget = forms.TextInput(attrs={'class':'input-medium'})
#
#                                                                                                     
#    class Meta:
#        model = NumberOfVehicle
#        exclude = ('customer')



#class StandardOperatingProcedureForm(forms.ModelForm):
#    customer = forms.IntegerField(widget=HiddenInput)
#    def __init__(self, *args, **kwargs):
#        super(StandardOperatingProcedureForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    field.widget = forms.TextInput(attrs={'class':'input-medium'})
#
#    
#    def clean_customer(self):
#        customer_id = self.cleaned_data.get('customer',1)
#        customer    = Customer.objects.get(pk=customer_id)
#        return customer
#                                                                                                     
#    class Meta:
#        model = StandardOperatingProcedure


#
#class RemmitanceCycleForCODForm(forms.ModelForm):
#    def __init__(self, *args, **kwargs):
#        super(RemmitanceCycleForCODForm, self).__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)  
#            if field:
#                if type(field.widget) in (forms.TextInput, forms.DateInput):
#                    field.widget = forms.TextInput(attrs={'class':'input-medium'})
#                                                                                                     
#    class Meta:
#        model = RemmitanceCycleForCOD
#        exclude = ('customer')



class ExceptionMasterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExceptionMasterForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    field.widget = forms.TextInput(attrs={'class':'input-medium'})

                                                                                                     
    class Meta:
        model = ExceptionMaster
        exclude = ('customer')
        
        
        
class ShipperForm(forms.ModelForm):
    name = forms.CharField()
    def __init__(self, *args, **kwargs):
        super(ShipperForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    field.widget = forms.TextInput(attrs={'class':'input-medium'})

                                                                                                     
    class Meta:
        model = Shipper
        exclude = ('customer',)

    def save(self, customer, address, commit=True):
        shipper = super(ShipperForm, self).save(commit=False)

        shipper.customer = customer
        shipper.name = self.cleaned_data['name']  # name of shipper
        shipper.address = address # address object
        shipper.type = self.cleaned_data['type'] # type of customer, normal (0) or paid (1)

        if commit:
            shipper.save()
            return shipper

class SubCustomerUploadForm(forms.ModelForm):
    filepath = forms.FileField(
        label='Select a file',
        help_text='Only excel files are supported. Please add columns in your excel file in the \
                following order; name, address, phone, pincode, return pincode, alias code. Add any extra colums after these colums.'
    )

    class Meta:
        model = SubcustomerDetailsUpload
        exclude = ('customer',)
        
