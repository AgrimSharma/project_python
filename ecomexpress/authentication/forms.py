'''
Created on Sep 21, 2012

@author: Sirius
'''
from django import forms
from authentication.models import *
from authentication.widgets import SelectDateWidget

from customer.forms import Customer
from authentication.models import EmployeeMasterCustomer

CUSTOMERS = [(c.id, c.name) for c in Customer.objects.all()]

LOGIN_CHOICES = (
    (0, 'False'),
    (1, 'True')
)


class EmployeeMasterForm(forms.ModelForm):

    customer = forms.MultipleChoiceField(choices=CUSTOMERS, widget=forms.SelectMultiple, required=False)
    query_limit = forms.CharField(max_length=5, label='Query Limit (Default 50)', required=False)

    def __init__(self, *args, **kwargs):
        super(EmployeeMasterForm, self).__init__(*args, **kwargs)
        self.fields['service_centre'] = forms.ModelChoiceField(queryset=ServiceCenter.objects.filter(),
                empty_label="Select Service Centre (Required)", required=False)
        self.fields['base_service_centre'] = forms.ModelChoiceField(queryset=ServiceCenter.objects.filter(),
                  empty_label="Select Base Service Centre (Required)", required=False)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                      field.widget = forms.TextInput(attrs={'placeholder': field.label+' (required)'})
                    else:
                      field.widget = forms.TextInput(attrs={'placeholder': field.label})

        # while form is editing prefill form with customers multiselect box
        instance = kwargs.get('instance')

        if instance:
            customers = [e.customer.pk for e in EmployeeMasterCustomer.objects.filter(employee_master=instance)]
            self.fields['customer'].initial = customers

    class Meta:
        model = EmployeeMaster
        fields = ('employee_code', 'firstname', 'lastname', 'user_type', 'department',
                'customer', 'email','address1','address2', 'address3','service_centre','base_service_centre',
                'mobile_no', 'temp_emp_status','temp_days','allow_concurent_login', 'query_limit', 'ebs', 'ebs_customer')

    def save(self, commit=True):
        instance = super(EmployeeMasterForm, self).save(commit=False)

        if commit:
            customer_ids = self.cleaned_data.get('customer')
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('employee_code')

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(username=email,email=email,password=password)

            instance.user = user
            instance.save()

            for cid in customer_ids:
                if int(cid) == 0:
                    continue
                cust = Customer.objects.get(pk=int(cid))
                EmployeeMasterCustomer.objects.create(customer=cust, employee_master=instance)

        return instance

class OutscanEmployeeForm(forms.ModelForm):
    class Meta:
        model = EmployeeMaster
        exclude = ('user', 'customer', 'email','address1','address2',
                'address3','mobile_no','login_active','staff_status')

