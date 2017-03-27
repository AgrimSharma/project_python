# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test

from django.conf import settings
import json
import pprint
import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.models import User
from apps.affiliates.models import Affiliates, Referrals, PayoutEvents, Payouts
from apps.affiliates.forms import PaymentForm

pp = pprint.PrettyPrinter(indent=4)

@login_required
def affilates(request):
    logged_user = request.user
    context = {}
    total_earned = total_paid = 0
    try:
        affiliate = Affiliates.objects.get(user = logged_user)    
    except:
        affiliate = Affiliates(user=logged_user, amount_earned='0.0', amount_paid='0.0')
        affiliate.save()
    context['all_referrals'] = affiliate.referrals_set.all()
    context['affiliate_id'] = affiliate.affiliate_id
    if len(context['all_referrals'])>0:
        total_earned = reduce(lambda x, y: x+y, map(lambda x: x.amount_earned, context['all_referrals']))
        total_paid = reduce(lambda x, y: x+y, map(lambda x: x.amount_paid, context['all_referrals']))
    context['total_earned'] = total_earned
    context['total_paid'] = total_paid
    context['balance'] = context['total_earned'] - context['total_paid']
    context['base_url'] = settings.BASE_URL
    return render_to_response("affiliates/affiliate.html",  context , context_instance=RequestContext(request) )
    
@user_passes_test(lambda u: u.is_staff)
def affilates_admin(request):
    context = {}
    affiliates = Affiliates.objects.all()
    affiliates = sorted(affiliates, key = lambda x : -x.amount_owed)
    affilliate_group = []
    for aff in affiliates:    
        all_referrals = aff.referrals_set.all()
        all_referrals = filter(lambda x: x.amount_earned > x.amount_paid, all_referrals)
        if len(all_referrals)>0:
            aff_bundle = {}
            aff_bundle['affiliate'] = aff
            aff_bundle['referrals'] = all_referrals
            aff_bundle['total_earned'] = aff.amount_earned
            aff_bundle['total_paid'] = aff.amount_paid
            aff_bundle['balance'] = aff.amount_owed
            referral_data = str(aff_bundle['balance'])
            for ref in all_referrals:
                referral_data += "::::" + str(ref.id) + "|" + str(ref.amount_earned - ref.amount_paid)
            aff_bundle['referral_data'] = referral_data
            affilliate_group.append(aff_bundle)
            
    context['all_affiliates'] = affilliate_group
    
    return render_to_response("affiliates/affiliate_admin.html",  context , context_instance=RequestContext(request) )
 
@user_passes_test(lambda u: u.is_staff)
def affilates_admin_pay(request):
    logged_user = request.user
    context = {}
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            referral_data = form.cleaned_data['referral_data']
            parts = referral_data.split("::::")
            total = parts[0]
            if total.strip() != '0.00':
                payout_event = PayoutEvents(staff=logged_user, payout_date=datetime.today(), dollar_amount=Decimal(total))
                payout_event.save()
            for ref in parts[1:]:
                ref_parts = ref.split("|")
                if ref_parts[1].strip() !="0.00":
                    referral = Referrals.objects.get(id=ref_parts[0].strip())
                    referral.amount_paid = referral.amount_paid + Decimal(ref_parts[1].strip())
                    referral.save()                    
                    
                    affiliate = Affiliates.objects.get(affiliate_id=form.cleaned_data['affiliate'])
                    affiliate.amount_paid = affiliate.amount_paid + Decimal(ref_parts[1].strip())
                    affiliate.save()
                    payout = Payouts(affiliate =affiliate, referral=referral, payout_date=datetime.today(), \
                    dollar_amount=Decimal(ref_parts[1].strip()), payout_event=payout_event)
                    payout.save()
                               
            
            return HttpResponseRedirect('/affiliates/admin')


