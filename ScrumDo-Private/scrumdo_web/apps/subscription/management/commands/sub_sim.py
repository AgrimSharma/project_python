#!/usr/bin/env python
# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from apps.organizations.models import Organization
from apps.subscription.models import Subscription
from apps.subscription.views import _updateOrganization

from django.core.management.base import BaseCommand, CommandError

diff = 0
ndiff = 0



# Fixed price
# def simulate(org, sub):
#     global diff, ndiff
#     users = sub.usersUsed()
#     newPrice = users * PER_USER
#     delta = newPrice - float(sub.plan.price_val)
#     print "%d\t%s\t%s\t%f" % (delta, org.slug, sub.plan.price_val, users * PER_USER)
#     diff += delta
#     if delta < 0:
#         ndiff += delta

# Tiered plans:
def simulate(org, sub):
    global diff, ndiff
    PER_USER = 10
    plans = [{'users': 10, 'price': 50}, {'users': 50, 'price': 100}, {'users': 200, 'price': 200}]

    users = sub.usersUsed()
    prices = []
    for plan in plans:
        newPrice = plan['price']
        if users > plan['users']:
            newPrice += PER_USER * (users - plan['users'])
        prices.append(newPrice)
    # print prices
    newPrice = min(prices)
    # newPrice = users * PER_USER
    delta = newPrice - float(sub.plan.price_val)
    print "%d\t%d\t%s\t%s\t%f" % (delta, users, org.slug, sub.plan.price_val, newPrice)
    diff += delta
    if delta < 0:
        ndiff += delta


class Command(BaseCommand):
    """Creates the intiial subscriptions for all organizations that previously existed."""
    def handle(self, *args, **options):
        global diff
        for organization in Organization.objects.all():
            sub = organization.subscription
            plan = sub.plan
            if plan.price_val > 1:
                if sub.active and not sub.is_trial:
                    simulate(organization, sub)
                    # print diff
        print "If everyone upgraded:"
        print diff
        print "If everyone did the 'best' thing for them:"
        print ndiff
