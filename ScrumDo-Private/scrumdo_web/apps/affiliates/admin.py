# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.contrib import admin
from apps.affiliates.models import Affiliates, Referrals, Payouts


class AffiliatesAdmin(admin.ModelAdmin):
    list_display = ('user', 'affiliate_id', 'amount_earned', 'amount_paid')
    search_fields = ('user', 'affiliate_id')
    
class ReferralsAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'organization', 'amount_earned', 'amount_paid')
    search_fields = ('affiliate', 'organization')


class PayoutsAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'referral', 'payout_date', 'dollar_amount')
    search_fields = ('affiliate', 'referral')
    

admin.site.register(Affiliates, AffiliatesAdmin)
admin.site.register(Referrals, ReferralsAdmin)
admin.site.register(Payouts, PayoutsAdmin)

