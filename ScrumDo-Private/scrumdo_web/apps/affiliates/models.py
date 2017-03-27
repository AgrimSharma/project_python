# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.db import models

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.organizations.signals import organization_created


class Affiliates(models.Model):
    user = models.ForeignKey(User)
    affiliate_id = models.AutoField(primary_key=True)
    amount_earned = models.DecimalField(max_digits=6, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)
    
    @property
    def amount_owed(self):
        return (self.amount_earned - self.amount_paid)
    

class Referrals(models.Model):
    affiliate = models.ForeignKey(Affiliates)
    organization = models.ForeignKey(Organization)
    amount_earned = models.DecimalField(max_digits=6, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)

class PayoutEvents(models.Model):
    staff = models.ForeignKey(User)
    payout_date = models.DateField( auto_now_add=True )
    dollar_amount = models.DecimalField(max_digits=6, decimal_places=2) 

class Payouts(models.Model):
    affiliate = models.ForeignKey(Affiliates)
    referral = models.ForeignKey(Referrals)
    payout_date = models.DateField( auto_now_add=True )
    dollar_amount = models.DecimalField(max_digits=6, decimal_places=2)
    payout_event = models.ForeignKey(PayoutEvents)
    

def referral_signup_handler(sender, **kwargs):
    try:
        organization = kwargs["organization"]
    except:
        pass
    if organization:
        source = organization.source
        values = source.split("/")
        if len(values)>1:
            scheme = values[1].strip()
            if scheme == "affiliate":
                affiliate = Affiliates.objects.get(affiliate_id = values[0].strip())
                referral = Referrals(affiliate = affiliate, organization=organization, amount_earned=0, amount_paid=0)
                referral.save()
organization_created.connect( referral_signup_handler )