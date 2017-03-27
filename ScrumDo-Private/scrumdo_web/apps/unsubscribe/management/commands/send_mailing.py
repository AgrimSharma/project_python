from django.core.management.base import BaseCommand, CommandError
from apps.unsubscribe.models import *
from apps.subscription.code_util import generate_code
import datetime
from optparse import make_option
from django.template import Engine
from django.core.mail import send_mail
from django.utils.http import urlquote
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context
import sys, traceback


import logging

logger = logging.getLogger(__name__)
today = datetime.date.today()
now = datetime.datetime.now()
week_ago = today - datetime.timedelta(days=7)

# MAILING_ID = "ScrumMaster1"
MIN_DAYS = 7
FROM = 'The ScrumDo Team <support@scrumdo.com>'


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--mailing', '-m', dest='mailing', help='What mailing to send?'),
    )

    args = "mailing"
    def handle(self, *args, **options):
        self.sent = 0
        self.skipped = 0
        self.error = 0
        MAILING_ID = options['mailing']
        if not MAILING_ID:
            print "Specify mailing id"
            return
        MAILING_ID = options['mailing']
        print "Mailing for %s" % MAILING_ID
        for address in AddressPulled.objects.filter(newsletter=MAILING_ID):
            try:
                if self.lastSentValid(address.email):
                    self.sendNewsletter(address.email, MAILING_ID, address.user)
                else:
                    self.skipped += 1
            except:
                traceback.print_exc(file=sys.stdout)
                logger.warn("Failed to send email.")
        print "%d sent, %d errors, %d skipped" % (self.sent, self.error, self.skipped)

    def sendNewsletter(self, email, MAILING_ID, user=None):
        try:
            rec = NewsletterSent(email=email, newsletter=MAILING_ID)
            rec.save()
            self.sendEmail(email, MAILING_ID, user)
            self.sent += 1
            self.logSent(email, MAILING_ID)
        except:
            self.error += 1
            traceback.print_exc(file=sys.stdout)
            logger.debug("Failed to send to %s" % email)

    def logSent(self, email, MAILING_ID):
        pass


    @staticmethod
    def extractName(email):
        return "(%s)" % email.split("@")[0]

    @staticmethod
    def sendEmail(address, MAILING_ID, user=None):
        context = {
            'email': address,
            'user': user
        }
        if user:
            context['code'] = generate_code('USER_REACTIVATE', user, 45).code

        body = open("%s.body.html" % MAILING_ID, "r").read()
        template = Engine().from_string(body) #loader.get_template_from_string(body)
        body = template.render(Context(context))

        text_version = ' '
        subject = open("%s.subject" % MAILING_ID, "r").read().strip()

        headers = {
            'List-Unsubscribe': "<https://app.scrumdo.com/unsubscribe/robot?email=%s>" % urlquote(address),
            'format': 'flowed',
            'X-MC-Autotext': 'true',
            'X-MC-Track': 'opens',
            'X-MC-Tags': MAILING_ID
        }
        msg = EmailMultiAlternatives(subject, text_version, FROM, [address], headers=headers)
        msg.attach_alternative(body, "text/html")
        msg.send()



    @staticmethod
    def lastSentValid(email):
        lastSend = NewsletterSent.objects.filter(email__iexact=email).order_by("-created")[:1]
        if len(lastSend) == 0:
            return True
        return (now - lastSend[0].created) > datetime.timedelta(days=MIN_DAYS)





