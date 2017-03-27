from django.conf import settings

from apps.scrumdocelery import app
from rollbardecorator import catchlogexception
from mailer import send_mail
from apps.emailconfirmation.models import EmailAddress
from apps.email_notifications.models import EmailOptions
from apps.organizations.models import Organization
import mailchimp
import mixpanel
from intercom import Intercom
from intercom.user import User as IntercomUser

Intercom.app_id = '5pg688sj'
Intercom.app_api_key = Intercom.api_key = 'a22ee0fc0a4661f73bc9e2ff8bbc76c18b3c5f2b'

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)

MAILCHIMP_KEY = "5a7ad557fddbdb4c71b426cfb6bdc273-us2"

@app.task
def unsubscribeEmailAddress(email, reason):
    try:
        _unsubscribeScrumDo(email)
    except:
        logger.error("Could not unsubscribe email")

    try:
        _unsubscribeMailchimp(email)
    except:
        logger.error("Could not unsubscribe mailchimp")

    try:
        _unsubscribeMixpanel(email)
    except:
        logger.error("Could not unsubscribe mixpanel")

    try:
        _unsubscribeIntercom(email)
    except:
        logger.error("Could not unsubscribe intercom")


@catchlogexception
def _unsubscribeMixpanel(email):
    for org in Organization.objects.filter(creator__email__iexact=email):
        mp.people_set(org.slug, {'$unsubscribed': True})


def _unsubscribeScrumDo(email):
    for address in EmailAddress.objects.filter(email__iexact=email):
        user = address.user
        for option in EmailOptions.objects.filter(user=user):
            option.marketing = False
            option.save()


@catchlogexception
def _unsubscribeMailchimp(email):
    api = mailchimp.Mailchimp(MAILCHIMP_KEY)
    lists = api.lists.list()
    for list in lists['data']:
        listId = list["id"]
        # id, email, delete_member=False, send_goodbye=True, send_notify=True
        try:
            api.lists.unsubscribe(listId, {'email': email}, False, False, False)
        except:
            pass # Was not subscribed?



@catchlogexception
def _unsubscribeIntercom(email):
    user = IntercomUser.User.find(email=email)
    user.unsubscribed_from_emails = True
    user.save()
