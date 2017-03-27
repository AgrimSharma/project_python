from django.core.exceptions import PermissionDenied
from django.conf import settings

from models import SingleUseCode, SubCode, SubCodeUsage

import mixpanel

import datetime
import random
import string

def valid_code(key, campaign):
    """
    :param key: Secret key to look up
    :param campaign: Campaign that this key is part of
    :return: The SingleUseCode if value, None if not
    """
    try:
        code = SingleUseCode.objects.get(code=key, campaign=campaign)
        if code.used or code.expiration < datetime.date.today():
            return None
        return code
    except SingleUseCode.DoesNotExist:
        return None


def generate_code(campaign, user, expiration_days):
    """Generates a SingleUserCode record"""
    key = ''.join(random.choice(string.letters + string.digits) for i in xrange(30))
    while True:
        try:
            SingleUseCode.objects.get(code=key, campaign=campaign)
            key = ''.join(random.choice(string.letters + string.digits) for i in xrange(30))
        except SingleUseCode.DoesNotExist:
            break

    code = SingleUseCode(campaign=campaign, user=user, code=key, expiration=datetime.date.today() + datetime.timedelta(days=expiration_days))
    code.save()
    return code


def consume_code(key, campaign):
    """Sets a SingleUseCode as used and returns it.  Throws PermissionDenied if not a valid code."""
    code = valid_code(key, campaign)
    if not code:
        raise PermissionDenied('That code was already used.')
    code.used = True
    code.save()
    return code


class CodeAlreadyUsedException(Exception):
    pass


def apply_subscription_code(org, code):
        subscription = org.subscription

        subcode = SubCode.objects.get(code__iexact=code, expiration__gte=datetime.date.today())

        previous_usages = SubCodeUsage.objects.filter(organization=org, code=subcode).count()
        if previous_usages > 0:
            raise CodeAlreadyUsedException('Already Used')

        if subscription.is_trial:
            subscription.expires = subscription.expires + datetime.timedelta(days=subcode.trial_days)
            subscription.save()
            SubCodeUsage(organization=org, code=subcode).save()
            mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
            mp.people_set_once(org.slug, {'Sub Code': code})
            mp.track(org.slug, 'Subscription Code', {'Sub Code': code})

