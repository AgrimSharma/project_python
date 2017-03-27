from django.core.exceptions import PermissionDenied
from django.core.validators import validate_email, ValidationError
from apps.projects.limits import org_user_limit
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User

from models import TeamInvite

from django.conf import settings

import traceback
import random
import string
import logging

logger = logging.getLogger(__name__)

import mixpanel

def invite_user(address, team, inviter):
    logger.debug("invite [%s]" % address)
    try:
        validate_email(address)
    except ValidationError:
        return

    key = ''.join(random.choice(string.letters + string.digits) for i in xrange(8))
    invite = TeamInvite(email_address=address, team=team, key=key)
    invite.save()
    invite_url = "%s/organization/accept/%s" % (settings.BASE_URL, key)
    context = {
        "invite": invite,
        "inviter": inviter,
        "base_url": settings.BASE_URL,
        "organization": invite.team.organization,
        "invite_url": invite_url
        }

    try:
        logger.debug("Sending invite email to %s " % address)

        body = render_to_string("organizations/team_invite_email.html", context)
        text_body = render_to_string("organizations/team_invite_email.txt", context)

        subject = "Invitation to ScrumDo team"

        msg = EmailMultiAlternatives(subject, text_body, "support@scrumdo.com", [address], headers={'format': 'flowed'})
        msg.attach_alternative(body, "text/html")
        msg.send()

        mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
        mp.track(team.organization.slug, 'Invite User')
    except:
        traceback.print_exc()
        logger.warn("Failed to send an email")

def notify_user(user, team, inviter):
    org_url = "%s/organization/%s/dashboard" % (settings.BASE_URL, team.organization.slug)
    context = {
        "team": team,
        "inviter": inviter,
        "org_url": org_url
        }
    try:
        logger.debug("Sending invite email to %s " % user.email)

        body = render_to_string("organizations/team_added_email.html", context)
        text_body = render_to_string("organizations/team_added_email.txt", context)

        subject = "Added to ScrumDo team"
        msg = EmailMultiAlternatives(subject, text_body, "support@scrumdo.com", [user.email], headers={'format': 'flowed'})
        msg.attach_alternative(body, "text/html")
        msg.send()

        mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
        mp.track(team.organization.slug, 'Added User')
    except:
        traceback.print_exc()
        logger.warn("Failed to send an email")

def team_invite(organization, team, userinput, user):
    if team.organization != organization:
        raise PermissionDenied()  # Shenanigans!

    if userinput == "":
        return False, 'Please specify a username or email address'

    users = User.objects.filter(username__iexact=userinput)
    if len(users) == 0:
        users = User.objects.filter(email__iexact=userinput)

    if len(users) > 0:
        new_member = users[0]

        if org_user_limit.increaseAllowed(userToAdd=new_member, organization=organization):
            team.members.add(new_member)
            team.save()
            notify_user(new_member, team, user)
            return True, 'User Added'
        else:
            return False, "Can not add more users at your current subscription level"

    try:
        validate_email(userinput)
        invite_user(userinput, team, user)
        return True, 'Invitation Sent'
    except ValidationError:
        return False, "User not found"
