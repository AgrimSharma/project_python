import datetime

from django import forms
from django.db.models import Sum, Count

from octroi.models import OctroiBilling
from service_centre.models import OctroiShipments, Shipment
from customer.models import Customer



class OctroiBillingForm(forms.Form):
    #billing_date = forms.DateField(label="Billing Date")
    customer = forms.CharField(widget=forms.HiddenInput())

    def save(self, commit=True):
        customer_id = self.cleaned_data['customer']

        billingdate = datetime.datetime.now()
        customer = Customer.objects.get(id=customer_id)

        oct_ships = OctroiShipments.objects.filter(shipper__id=customer_id, octroi_billing=None, status=1).exclude(receipt_number="")
        if oct_ships.count() == 0:
            return None

        charges = oct_ships.aggregate(oct_charge=Sum('octroi_charge'), ecom_charge=Sum('octroi_ecom_charge'))
        octroi_charge_sum = charges.get('oct_charge') if charges.get('oct_charge') else 0
        octroi_ecom_charge_sum = charges.get('ecom_charge') if charges.get('ecom_charge') else 0

        total_charge_pretax = octroi_charge_sum + octroi_ecom_charge_sum

        service_tax = octroi_ecom_charge_sum * 0.12
        education_secondary_tax =  service_tax * 0.02
        cess_higher_secondary_tax =  service_tax * 0.01
        total_payable_charge = total_charge_pretax + service_tax + education_secondary_tax + cess_higher_secondary_tax

        oct_billing = OctroiBilling.objects.create(customer=customer,
                octroi_charge=octroi_charge_sum,
                octroi_ecom_charge=octroi_ecom_charge_sum,
                education_secondary_tax=education_secondary_tax,
                cess_higher_secondary_tax=cess_higher_secondary_tax,
                service_tax=service_tax,
                total_charge_pretax=total_charge_pretax,
                total_payable_charge=total_payable_charge,
                bill_generation_date=billingdate)

        oct_billing.shipments = oct_ships
        oct_billing.bill_id = 'OC' + str(oct_billing.id)
        oct_billing.save()

        oct_ships.update(octroi_billing=oct_billing)
        return oct_billing
