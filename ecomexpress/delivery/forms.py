from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button

from django import forms
from django.forms.formsets import formset_factory

from service_centre.models import CODDeposits
from service_centre.models import Shipment, ShipmentExtension, CODCharge
from service_centre.models import outscans_update_for_cash_tally
from service_centre.models import DOShipment, CashTallyHistory
from authentication.models import EmployeeMaster
from location.models import ServiceCenter
from .models import CreditCardPaymentDeposit, CreditPaymentAwbDetails, CreditcardDelivery


class CreditcardDeliveryForm(forms.ModelForm):
    airwaybill_number = forms.CharField()
    employee_code = forms.CharField()

    class Meta:
        model = CreditcardDelivery
        fields = (
            'employee_code', 'airwaybill_number', 'credit_card_number', 
            'credit_card_owner', 'bank_name','collected_amount',
            'transaction_id', 'transaction_date', 'transaction_time')

    def save(self, commit=False):
        super(CreditcardDeliveryForm, self).save(commit=False)

        airwaybill_number = self.cleaned_data.pop('airwaybill_number')
        emp_code = self.cleaned_data.pop('employee_code')
        collected_amount = self.cleaned_data.get('collected_amount')
        shipment = Shipment.objects.get(airwaybill_number=airwaybill_number)
        employee = EmployeeMaster.objects.get(employee_code=emp_code)

        credit = CreditcardDelivery.objects.create(
                shipment=shipment, employee=employee, 
                **self.cleaned_data
        )

        CashTallyHistory.objects.create(shipment=shipment, current_collection=collected_amount)
        ShipmentExtension.objects.filter(shipment=shipment).update(
                cash_tally_status=1, cash_deposit_status=1, 
                collected_amount=shipment.collectable_value
        )
        CODCharge.objects.filter(shipment=shipment).update(status=1)
        outscans = DOShipment.objects.filter(shipment=shipment, status=1).values_list('deliveryoutscan__id', flat=True)
        outscans_update_for_cash_tally(outscans)
        return credit


class CreditAwbDetailForm(forms.Form):
    airwaybill_number = forms.CharField()
    airwaybill_amount = forms.CharField()
    credit_card_payment_received = forms.CharField()
    balance = forms.CharField()
    delivery_centre = forms.CharField()
    remarks = forms.CharField()             
    
class CreditPaymentAwbDetailsForm(forms.Form):
    airwaybill_number = forms.CharField(max_length=15,
        widget=forms.TextInput(attrs={'class':'awbno'}))
    airwaybill_amount = forms.FloatField(
        widget=forms.TextInput(attrs={'class':'awb_amount'}))
    credit_card_payment_received = forms.FloatField(widget=forms.TextInput(
        attrs={'class' : 'credit_card_payment_received'}))
    balance = forms.FloatField(
        widget=forms.TextInput(attrs={'class':'balance'}))
    delivery_centre = forms.CharField(
        widget=forms.TextInput(attrs={'class':'dc'}))
    remarks = forms.CharField(max_length=200, required=False,
        widget=forms.TextInput(attrs={'class':'remarks'}))

    def save(self, credit, commit=True):
        data = self.cleaned_data
        airwaybill_number = data.get('airwaybill_number')
        airwaybill_amount = data.get('airwaybill_amount')
        credit_card_payment_received = data.get('credit_card_payment_received')
        balance = data.get('balance')
        delivery_centre = data.get('delivery_centre')
        dc = ServiceCenter.objects.get(center_name=delivery_centre)
        remarks = data.get('remarks')

        shipment = Shipment.objects.get(airwaybill_number=airwaybill_number)
        awbdetail = CreditPaymentAwbDetails.objects.create(
            creditcardpaymentdeposit=credit,
            shipment=shipment, 
            credit_card_payment_received=credit_card_payment_received,
            balance=balance,
            delivery_centre=dc,
            remarks=remarks)
        return awbdetail

CreditAwbDetailFormSet = formset_factory(CreditPaymentAwbDetailsForm, extra=1) 

# form 1
class CreditDateForm(forms.Form):
    entry_date = forms.DateField()
    system_date = forms.DateField(widget=forms.TextInput(attrs={'readonly':True}) )
    payment_type = forms.ChoiceField(
        choices=(
            (1, 'Full Payment'), 
            (0, 'Partial Payment')))


# form 3
class CreditPaymentDetailForm(forms.Form):
    transaction_date = forms.DateField()
    transaction_slip_no = forms.CharField()
    credit_card_payment_received = forms.FloatField()
    terminal_id = forms.CharField(max_length=30, required=False)

class CreditCardPaymentDepositForm(forms.Form):
    PAYMENT_TYPE_CHOICES = (
        (1, 'Full Payment'),
        (0, 'Part Payment'),
    )
    entry_date = forms.DateField()
    system_date = forms.DateField()
    payment_type = forms.ChoiceField(choices=PAYMENT_TYPE_CHOICES)
    transaction_slip_no = forms.CharField(max_length=20)
    transaction_date = forms.DateField()
    credit_card_payment_received = forms.FloatField()
    terminal_id = forms.CharField(max_length=30)

    def save(self, employee, commit=True):
        data = self.cleaned_data
        entry_date = data.get('entry_date')
        system_date = data.get('system_date')
        payment_type = data.get('payment_type')
        transaction_slip_no = data.get('transaction_slip_no')
        transaction_date = data.get('transaction_date')
        credit_card_payment_received = data.get('credit_card_payment_received')
        terminal_id = data.get('terminal_id')

        credit = CreditCardPaymentDeposit.objects.create(
            entry_date=entry_date,
            system_date=system_date,
            payment_type=payment_type,
            transaction_slip_no=transaction_slip_no,
            transaction_date=transaction_date,
            credit_card_payment_received=credit_card_payment_received,
            terminal_id=terminal_id,
            employee=employee)
        return credit

    def __unicode__(self):
        return self.transaction_slip_no


class CODDepositSearchForm(forms.Form):
    scs = ServiceCenter.objects.values_list('id', 'center_name')
    deposit_from = forms.DateField()
    deposit_to = forms.DateField()
    origin = forms.ChoiceField(choices=scs)

    def __init__(self, *args, **kwargs):
        super(CODDepositSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id_codpanel_coddeposit_form'
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            'deposit_from', 'deposit_to', 'origin',
            Button(
                'search', "Search",
                css_class='tm10 btn btn-primary',
                css_id="id_coddeposit_search_button"))

    def search(self):
        from_date = self.cleaned_data.get('deposit_from')
        to_date = self.cleaned_data.get('deposit_to')
        origin = self.cleaned_data.get('origin')
        return CODDeposits.objects.filter(
            date__range=(from_date, to_date), origin_id=origin)
