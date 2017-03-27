#!/usr/bin/env python
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from datetime import datetime, date, time, timedelta

from apps.organizations.models import Organization
from apps.subscription.models import Subscription, SubscriptionStats, SpreedlyInfo, SubscriptionPlan
from apps.subscription.spreedly import Spreedly
from apps.affiliates.models import Affiliates, Referrals

from decimal import Decimal, ROUND_UP
from django.contrib.auth.models import User

from django.core.management.base import BaseCommand, CommandError
import traceback
import sys
import logging

from rollbardecorator import logexception

import mixpanel
from django.conf import settings

logger = logging.getLogger(__name__)
logging.basicConfig()

class Command(BaseCommand):

    @logexception
    def handle(self, *args, **options):

        try:
            self.updateStats()
        except Exception as e:
            logger.error("Could not update stats")
            logger.error(e)

        self.updateTransactions()

    def updateTransactions(self):
        info = SpreedlyInfo.objects.get(id=1)
        spreedly = Spreedly()
        transactions = spreedly.getTransactions(info.last_transaction_fetched).getElementsByTagName("transaction")
        count = 0
        for transaction in transactions:
            try:
                trans_id = _getText(transaction.getElementsByTagName("id")[0])
                trans_succeeded = _getText(transaction.getElementsByTagName("succeeded")[0])
                trans_sub_id = int(_getText(transaction.getElementsByTagName("subscriber-customer-id")[0]))
                trans_amount = _getText(transaction.getElementsByTagName("amount")[0])
                trans_type = _getText(transaction.getElementsByTagName("detail-type")[0])
                transaction_time = _getText(transaction.getElementsByTagName("updated-at")[0])
                org = Organization.objects.get(id=trans_sub_id)                
                info.last_transaction_fetched = int(trans_id)
                if trans_succeeded == "true" and trans_amount != "0.0":
                    org.subscription.total_revenue = org.subscription.total_revenue + Decimal(trans_amount)
                    org.subscription.save()
                    source = org.source.split("/")
                    
                    try:
                        mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
                        mp.people_track_charge(org.slug, trans_amount, {})
                        mp.track(org.slug, 'Billed', {
                            'Plan': org.subscription.plan.feature_level,
                            'Amount': trans_amount
                        })
                    except:
                        traceback.print_exc(file=sys.stdout)    
                        logger.info("Could not update MIX")
                    
                    if len(source)==2 and source[1].strip()=="affiliate":
                        transaction_time = datetime.strptime(transaction_time, "%Y-%m-%dT%H:%M:%SZ")
                        year = timedelta(days=365)
                        if transaction_time < (org.created + year):
                            affiliate = Affiliates.objects.get(affiliate_id=source[0].strip())
                            affiliate.amount_earned = affiliate.amount_earned + (Decimal(trans_amount)/2).quantize(Decimal('.01'), rounding=ROUND_UP)
                            affiliate.save()
                            try:
                                referral = Referrals.objects.get(organization=org)
                                referral.amount_earned = referral.amount_earned + (Decimal(trans_amount)/2).quantize(Decimal('.01'), rounding=ROUND_UP)
                            except:
                                referral = Referrals(affiliate=affiliate, organization=org, amount_earned=(Decimal(trans_amount)/2).quantize(Decimal('.01'), rounding=ROUND_UP))
                            referral.save()
                        
                    
                logger.debug("%s %s %s %s %s" % (trans_id, trans_succeeded, org.name,trans_amount, trans_type) )
                count+=1
            except:
                pass

        logger.debug("Processed %d to transaction %d" % (count,info.last_transaction_fetched) )
        info.save()
        
    def updateStats(self):
        spreedly = Spreedly()
        subscribers_result = spreedly.getSubscribers()
        subscribers = subscribers_result.getElementsByTagName("subscriber")
        trial=0
        recurring=0
        paid=0
        expected=0
        trial_rev=0
        
        for subscriber in subscribers:            
            if( _getText(subscriber.getElementsByTagName("active")[0]) == "true" ):
                level = _getText(subscriber.getElementsByTagName("feature-level")[0])
                trial_user = ("true" == _getText(subscriber.getElementsByTagName("on-trial")[0]) )
                recurring_user = ("true" == _getText(subscriber.getElementsByTagName("recurring")[0]) )
                try:
                    planVersion = subscriber.getElementsByTagName("subscription-plan-version")[0]
                    planId = _getText(planVersion.getElementsByTagName("subscription-plan-id")[0])
                except IndexError:
                    continue

                if trial_user:
                    trial += 1
                else:
                    paid += 1
                if recurring_user:
                    # logger.debug( subscriber.toxml() )
                    try:
                        plan = SubscriptionPlan.objects.filter(spreedly_id=planId)[0]

                        recurring += 1
                        fee = plan.price_val
                        expected += fee
                        if trial_user:
                            trial_rev += fee
                    except:
                        logger.warn("Didn't know what to do with feature level %s" % level)

        today = date.today()
        for subscription in Subscription.objects.filter(is_trial=True, expires__gte=today):
            # logger.debug("Trial += %s %s" % (subscription.plan.price_val,subscription.organization.slug) )
            # New way of trials            
            expected += subscription.plan.price_val
            trial_rev += subscription.plan.price_val

        stats = SubscriptionStats(trial_monthly_revenue="%f" % trial_rev, trial_orgs=trial, recurring_orgs=recurring, paid_orgs=paid, expected_monthly_revenue="%f" % expected, active_orgs=Organization.objects.count() )
        stats.save()

        
def _getText(nodelist):
  rc = []
  for node in nodelist.childNodes:
      if node.nodeType == node.TEXT_NODE:
          rc.append(node.data)
  return ''.join(rc)
        
