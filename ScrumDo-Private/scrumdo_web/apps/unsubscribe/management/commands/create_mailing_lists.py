from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from apps.unsubscribe.models import *
from apps.subscription.models import Subscription
from apps.activities.models import NewsItem
from optparse import make_option
from apps.classic.models import NewsItem as ClassicNewsItem

from apps.organizations.models import Organization
from apps.email_notifications.models import EmailOptions
import datetime

import logging

logger = logging.getLogger(__name__)
today = datetime.date.today()
now = datetime.datetime.now()
last_week = today - datetime.timedelta(days=7)
past_month = today - datetime.timedelta(days=30)
past_3_months = today - datetime.timedelta(days=90)

organization_cutoff = today - datetime.timedelta(days=30*7)  #days=7)  # only pull orgs created before this.

MIN_DAYS = 7


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--mailing', '-m', dest='mailing', help='What mailing to send?'),
        make_option('--count', '-c', dest='count', help='How many to pull?'),
    )


    def handle(self, *args, **options):
        addresses = []
        c = 0
        try:
            MAILING_ID = options['mailing']
            MAILING_COUNT = int(options['count'])
        except:
            print "Usage: mailingID  userCount"
            return
        print "Pulling %d addresses for %s" % (MAILING_COUNT, MAILING_ID)

        for member in User.objects.all().order_by('-last_login'):
            if len(addresses) >= MAILING_COUNT:
                break  # Already got enough
            email = member.email
            if not self.validEmail(email):
                continue  # Is it valid?
            # Do user/email filtering here...
            if not self.canEmail(member):
                continue  # Are we allowed to email this address?

            logger.info(u"%d %d %s" % (len(addresses), c, email))
            addresses.append((member,email))

        # orgs = Organization.objects.filter(created__lt=organization_cutoff).order_by("?")
        #
        # for org in orgs:
        #     if len(addresses) >= MAILING_COUNT:
        #         break  # Already got enough
        #
        #     # Do organization filtering here
        #     # if org.memberCount() < 10:
        #     #     continue  # only want larger orgs
        #
        #     for member in org.members():
        #         email = member.email
        #         if not self.validEmail(email):
        #             continue  # Is it valid?
        #         # Do user/email filtering here...
        #         if email in addresses:
        #             continue  # already got him!
        #         if not self.canEmail(member):
        #             continue  # Are we allowed to email this address?
        #         if self.isCustomerEmail(email):
        #             break  # Check to see if they are already paying us, don't bug them!  We break since most likely the whole org is paying
        #         if self.isActiveEmail(email):
        #             continue  # Just targetting inactive people for this one.
        #
        #         logger.info(u"%d %d %s %s" % (len(addresses), c, org.slug, email))
        #         addresses.append((member,email))

        self.createList(addresses, MAILING_ID)

    def isActiveEmail(self, email):
        for user in User.objects.filter(email=email):
            if self.isActiveUser(user):
                return True
        return False

    @staticmethod
    def isActiveUser(user):
        """Checks all organizations a user is part of and returns true if they are active in the past 3 months."""
        c = NewsItem.objects.filter(user=user, created__gt=past_3_months)[:1].count()
        if c > 0:  # NewsItem query has an index, so check it first.  Classic doesn't, so it's slow
            return True
        c += ClassicNewsItem.objects.filter(user=user, created__gt=past_3_months)[:1].count()
        return c > 0

    def isCustomerEmail(self, email):
        """Returns true if this email belongs to an active customer."""
        for user in User.objects.filter(email=email):
            if self.isCustomerUser(user):
                return True
        return False

    @staticmethod
    def isCustomerUser(user):
        """Checks all organizations a user is part of and returns true if they are a customer."""
        for org in Organization.getOrganizationsForUser(user):
            try:
                if org.subscription.active and org.subscription.token:
                    return True
            except Subscription.DoesNotExist:
                pass
        return False


    @staticmethod
    def validEmail(email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    @staticmethod
    def createList(addresses, MAILING_ID):
        for user, email in addresses:
            rec = AddressPulled(user=user, email=email, newsletter=MAILING_ID)
            rec.save()
            print email
        print len(addresses)

    def canEmail(self, creator):
        if not creator.is_active:
            return False
        if creator.email is None or creator.email == '':
            return False
        if not self.lastPulledValid(creator.email):
            return False
        if not self.lastSentValid(creator.email):
            return False
        if self.doNotEmail(creator.email):
            return False
        if not self.subscribed(creator):
            return False
        return True

    @staticmethod
    def subscribed(user):
        try:
            options = EmailOptions.objects.get(user=user)
        except EmailOptions.MultipleObjectsReturned:
            options = EmailOptions.objects.filter(user=user)[0]
        except EmailOptions.DoesNotExist:
            return True
        return options.marketing

    @staticmethod
    def doNotEmail(email):
        return UnsubscribeRequest.objects.filter(email__iexact=email).count() > 0

    @staticmethod
    def lastPulledValid(email):
        lastSend = AddressPulled.objects.filter(email__iexact=email).order_by("-created")[:1]
        if len(lastSend) == 0:
            return True
        lastSend = lastSend[0]
        return (now - lastSend.created) > datetime.timedelta(days=MIN_DAYS)

    @staticmethod
    def lastSentValid(email):
        lastSend = NewsletterSent.objects.filter(email__iexact=email).order_by("-created")[:1]
        if len(lastSend) == 0:
            return True
        lastSend = lastSend[0]
        return (now - lastSend.created) > datetime.timedelta(days=MIN_DAYS)





