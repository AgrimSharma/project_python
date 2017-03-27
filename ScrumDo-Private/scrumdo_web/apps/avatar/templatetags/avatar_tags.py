import urllib

from django import template
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from django.conf import settings
from scrumdo_utils import cache

from apps.avatar import AVATAR_DEFAULT_URL, AVATAR_GRAVATAR_BACKUP, AVATAR_GRAVATAR_DEFAULT

import hashlib

register = template.Library()


def avatar_url(user, size=80):
    try:
        if not isinstance(user, User):
            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                return AVATAR_DEFAULT_URL
        avatars = user.avatar_set.order_by('-date_uploaded')
        primary = avatars.filter(primary=True)
        if primary.count() > 0:
            avatar = primary[0]
        elif avatars.count() > 0:
            avatar = avatars[0]
        else:
            avatar = None
        if avatar is not None:
            if not avatar.thumbnail_exists(size):
                avatar.create_thumbnail(size)
            return avatar.avatar_url(size)
        else:
            if AVATAR_GRAVATAR_BACKUP:
                params = {'s': str(size)}
                params['d'] = "%s/avatar/defaultavatar/%d/%s" % (settings.SSL_BASE_URL, size, user.username)
                return "https://secure.gravatar.com/avatar/%s/?%s" % (
                    hashlib.md5(user.email).hexdigest(),
                    urllib.urlencode(params))
            else:
                return AVATAR_DEFAULT_URL
    except:
        return AVATAR_DEFAULT_URL

register.simple_tag(avatar_url)


def avatar(user, size=80):
    return real_avatar(user, size)


@cache(30)
def real_avatar(user, size):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
            alt = unicode(user)
            url = avatar_url(user, size)
        except User.DoesNotExist:
            url = AVATAR_DEFAULT_URL
            alt = _("Default Avatar")
    else:
        alt = unicode(user)
        try:
            url = avatar_url(user, size)
        except:
            url = AVATAR_DEFAULT_URL
            
    return """<img src="%s" alt="%s" width="%s" height="%s" style="max-width: %spx; max-height: %spx;" />""" % (url, alt, size, size, size, size)
register.simple_tag(avatar)


def render_avatar(avatar, size=80):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return """<img src="%s" alt="%s" width="%s" height="%s" style="max-width: %spx; max-height: %spx;"/>""" % (
        avatar.avatar_url(size), str(avatar), size, size, size, size)
register.simple_tag(render_avatar)
