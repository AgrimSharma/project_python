# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django import forms

from models import PayoutEvents, Payouts, Affiliates, Referrals

class PaymentForm(forms.Form):
    affiliate = forms.CharField(max_length=10, widget=forms.HiddenInput)
    referral_data = forms.CharField(max_length=100, widget=forms.HiddenInput)