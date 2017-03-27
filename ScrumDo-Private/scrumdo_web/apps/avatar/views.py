from django.http import HttpResponse
from django.conf import settings

from django.views.decorators.cache import cache_page, cache_control


from templatetags import avatar_tags
from django.views.decorators.http import condition
from PIL import Image, ImageDraw, ImageFont

from managers import get_avatar

import urllib2
import datetime


def _avatar_etag(request, size, username=None):
    if username is None or username == '':
        avatarUrl = "http://scrumdo-cdn.s3.amazonaws.com/manual_uploads/logos/{size}.png".format(size=size)
    else:
        avatarUrl = avatar_tags.avatar_url(username, int(size))
        p = avatarUrl.find('Expires')
        if p > 0:
            avatarUrl = avatarUrl[0:p]
    return avatarUrl


def _avatar_last_modified(request, size, username=None):
    avatar = get_avatar(username)
    if avatar is None:
        # If the user doesn't have an avatar, they're using either the gravatar or our default avatar.
        # For the default, it never changes.
        # For gravatar, it could change, but we can't know that here
        # So we're going to compromise and just send 1am yesterday so we only update avatars once a day
        d = datetime.datetime.now() - datetime.timedelta(days=1)
        return d.replace(hour=1, minute=0, second=0, microsecond=0)
    return avatar.date_uploaded


@condition(etag_func=_avatar_etag, last_modified_func=_avatar_last_modified)
@cache_control(private=True, max_age=120)
def avatar_redirect(request, size, username=None):
    # Find out the correct avatar URL and redirect to there
    if username is None or username == '':
        # This is the scrumdo logo
        avatarUrl = "http://scrumdo-cdn.s3.amazonaws.com/manual_uploads/logos/{size}.png".format(size=size)
    else:
        avatarUrl = avatar_tags.avatar_url(username, int(size))

    try:
        response = urllib2.urlopen(avatarUrl)
    except:
        return avatar_default(request, size, username)

    response = HttpResponse(response.read(), content_type=response.info().gettype())
    response.skip_vary = True
    return response


def avatar_default(request, size, username):
    # This is the default avatar if a user doesn't have one set.
    size = int(size)
    colors = ["#f6764e", "#9b59b6", "#1abc9c", "#3498dd", "#c0392b"]
    firstLetter = username.upper()[0]
    secondLetter = username[1]
    color = colors[ord(secondLetter) % len(colors)]

    img = Image.new("RGB", (size, size), color)

    draw = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(settings.AVATAR_FONT, size)
    w, h = draw.textsize(firstLetter, fnt)
    h += round(size/3)
    draw.text(((size-w)/2, (size-h)/2), firstLetter, font=fnt, fill=(255, 255, 255, 255))

    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    response.skip_vary = True
    return response
