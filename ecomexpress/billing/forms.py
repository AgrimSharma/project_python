'''
Created on 01-Jun-2013

@author: prtouch
'''
import datetime
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button, Field

from billing.models import BillingCutOff, BillingReportQueue
from customer.models import Customer
from billing.generate_billing_preview import preview_billing

class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    excel_file  = forms.FileField()


class CutOffForm(forms.ModelForm):
    class Meta:
        model = BillingCutOff
        fields = ['cutoff_date']

    def save(self, commit=True):
        instance = super(CutOffForm, self).save(commit=False)
        cut_date = self.cleaned_data['cutoff_date']
        instance.cutoff_date = cut_date
        instance.added_on = datetime.datetime.now()
        if commit:
            instance.save()
        return instance

CUSTOMER_LIST = Customer.objects.filter(activation_status=True).values_list('id', 'name')
MONTH_LIST = [
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December')]

YEARS = [(y, y) for y in reversed(range(2013, 2015))]

class BillingPreviewForm(forms.Form):
    customer = forms.ChoiceField(choices=CUSTOMER_LIST)
    year = forms.ChoiceField(choices=YEARS)
    month = forms.ChoiceField(choices=MONTH_LIST)

    def save(self, commit=False):
        data = self.cleaned_data
        month = data.get('month')
        month = datetime.date(2014, int(month), 01).strftime('%m')
        file_name = preview_billing(data)
        return (file_name, month)

class BillingReportsForm(forms.Form):
    report_customer = forms.ChoiceField(label="Customer", choices=CUSTOMER_LIST)
    report_year = forms.ChoiceField(label="Year", choices=YEARS)
    report_month = forms.ChoiceField(label="Month", choices=MONTH_LIST)


class BillingGenerationForm(forms.Form):
    #customer = forms.ChoiceField(choices=CUSTOMER_LIST)
    billing_from = forms.DateField(
        widget=forms.TextInput(attrs={'class':'date form-control'}))
    billing_to = forms.DateField(
        widget=forms.TextInput(attrs={'class':'date form-control'}))


class ProvisionalBillingGenerationForm(forms.Form):
    #customer = forms.ChoiceField(choices=CUSTOMER_LIST)
    provisional_billing_from = forms.DateField(
        label="Billing From",
        widget=forms.TextInput(attrs={'class':'date form-control'}))
    provisional_billing_to = forms.DateField(
        label="Billing To",
        widget=forms.TextInput(attrs={'class':'date form-control'}))

class BillingReportQueueForm(forms.ModelForm):
    CUSTOMERS = list(Customer.objects.values_list('id', 'name'))
    CUSTOMERS.insert(0, (0, 'All'))
    customer = forms.ChoiceField(
        choices=CUSTOMERS,
        widget=forms.Select(attrs={'class':'select form-control'}),
        required=False)

    class Meta:
        model = BillingReportQueue
        fields = (
            'invoice_report', 'headless_invoice_report',
            'awb_pdf_report', 'awb_excel_report', 'ebs_invoice_report',
            'headless_ebs_invoice_report', 'summary', 'msr')

    def save(self, bill_queue, commit=False):
        report_queue = super(BillingReportQueueForm, self).save(commit=False)
        report_queue.billqueue = bill_queue
        report_queue.save()
        return report_queue


from billing.widgets import MonthYearWidget
from billing.charge_verification import verify_freight

class ChargeVerificationForm(forms.Form):
    customers = Customer.objects.filter(
        activation_status=True).order_by('name')
    customer = forms.ModelChoiceField(queryset=customers)
    year_month = forms.DateField(widget=MonthYearWidget)

    def __init__(self, *args, **kwargs):
        super(ChargeVerificationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id_charge_verification_form'
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            'customer', 'year_month',
            Button(
                'search', "Search",
                css_class='tm10 btn btn-primary',
                css_id="id_charge_verification_search"),
            Button(
                'download', "Download",
                css_class='tm10 btn btn-primary',
                css_id="id_charge_verification_download"))

    def search(self):
        customer = self.cleaned_data.get('customer')
        year_month = self.cleaned_data.get('year_month')
        return verify_freight(customer, year_month.year, year_month.month)
