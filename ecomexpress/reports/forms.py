from django import forms
from datetime import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.layout import Button, Div, Column, Field

from location.models import ServiceCenter, Region, State
from customer.models import Customer

#not used
class JQueryUIDatepickerWidget(forms.DateInput):
    def __init__(self, **kwargs):
        super(forms.DateInput, self).__init__(attrs={"class":"date","width":"88px"}, **kwargs)

    class Media:
        css = {"all":("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/themes/redmond/jquery-ui.css",)}
        js = ("http://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js",
              "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/jquery-ui.min.js",)


class ShipmentSearchForm(forms.Form):
   destination = forms.ChoiceField(choices=[])
   from_date = forms.DateField(widget=forms.DateInput(attrs={'class':'date from_date','width':'88px'}),required=True)
   to_date = forms.DateField(widget=forms.DateInput(attrs={'class':'date to_date','width':'88px'}),required=False)
   def __init__(self, *args, **kwargs):
        super(ShipmentSearchForm, self).__init__(*args, **kwargs)
	self.fields['destination'].choices = ServiceCenter.objects.values_list('id','center_name')
   def clean(self):
        destination = self.cleaned_data['destination']
	from_date = self.cleaned_data['from_date']
	to_date = self.cleaned_data['to_date']
	if to_date == None:
	    to_date = datetime.now()
	if from_date > to_date:
	    raise forms.ValidationError('From date cannot be greater than To Date')
	return self.cleaned_data 


class ReportSearchForm(forms.Form):
    reports_list = (
        (0, 'Reports'),
        (1, 'NDR'),
        (2, 'Daily sales Register'),
        (3, 'Customer-wise Day-wise Sales Summary'),
        (4, 'Customer-wise Bill Summary'),
        (5, 'Performance Analysis'),
        (6, 'Performance Analysis - Location'),
        (7, 'Performance Analysis - Customer'),
        (8, 'Strike Rate Analysis(Location)'),
        (9, 'Strike Rate Analysis(Customer)'),
        (10, 'Ageing Sop'),
        (11, 'No-Information'),
        (12, 'Customer Reconciliation Report'),
        (13, 'Back Dated Reports'),
        (14, 'Previous Day Delivery'),
        (15, 'COD Collection Exception'),
        (16, 'COD Collection POD'),
        (17, 'COD Collection POD rev'),
        (18, 'COD Collection Day Tally'),
        (19, 'Delivery Dispatch Reports'),
        (20, 'Day-wise Count'),
        (21, 'Delivery Performance Report'),
        (22, 'Not Out Scan Report'),
        (23, 'Bag Detail Report'),
        (24, 'Bag Exception Report'),
        (25, 'Data uploaded status Report'),
        (26, 'Shipment Pickuped Status Report'),
        (27, 'PPC Not Outscan Report'),
        (28, 'Pending Outscan Report'),
        (29, 'Hub Not Outscan Report'),
        (30, 'Bag-Inbound Report'),
        (31, 'Bag-Outbound Report'),
        (32, 'Outscans Report'),
        (33, 'Subcustomers Report'),
        (34, 'COD Deposits Confirmation Report'),
        (35, 'Inscans Report'),
        (36, 'Weekly Report'),
        (37, 'Previous Day Load Report'),
        (38, 'Daily Report'),
        (39, 'Missed Pickup Report'),
        (40, 'RTO Status Report'),
        (41, 'Outscan Performance Report'),
        (42, 'Correction Report'),
        (43, 'Tally Input XML'),
        (44, 'Telecalling Report'),
        (45, 'Pickup MIS Report'),
        (46, 'Overage Report'),
        (47, 'Shortage Report'),
        (48, 'Trf Invoice Report'),
        (49, 'Daily Cash Tally Report'),
        (50, 'West Bengal Report'),
        (51, 'Daywise report'))

    customer_list = list(Customer.objects.using('local_ecomm').values_list('id', 'name'))
    customer_list.insert(0, ('', 'Customers'))
    city_list = list(ServiceCenter.objects.using('local_ecomm').values_list('id', 'center_name'))
    region_list = list(Region.objects.using('local_ecomm').values_list('id', 'region_name'))
    region_list.insert(0, ('', 'Select Region'))
    state_list = list(State.objects.using('local_ecomm').values_list('id', 'state_name'))
    state_list.insert(0, ('', 'Select State'))

    reports = forms.ChoiceField(choices=reports_list)
    customers = forms.ChoiceField(choices=customer_list, required=False)
    origin_city = forms.ChoiceField(widget=forms.SelectMultiple(attrs={'width':'10px'}),choices=city_list, required=False)
    dest_city = forms.ChoiceField(widget=forms.SelectMultiple(attrs={'width':'10px'}),choices=city_list, required=False)
    origin_state = forms.ChoiceField(choices=state_list, required=False)
    dest_state = forms.ChoiceField(choices=state_list, required=False)
    origin_region = forms.ChoiceField(choices=region_list, required=False)
    dest_region = forms.ChoiceField(choices=region_list, required=False)
    from_date = forms.DateField()
    to_date = forms.DateField()
 
    def __init__(self, user, *args, **kwargs):
        super(ReportSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline well'
        self.helper.form_tag = False
        self.helper.form_id = 'id-report-search-form'
        self.helper.layout = Layout(
            'reports', 'customers', 'origin_city', 'dest_city', 'origin_state', 'dest_state',
            'origin_region', 'dest_region', 'from_date', 'to_date',
            Button(
               'download', "Download",
               css_class='btn btn-primary',
               css_id="id_report_download_button"))
