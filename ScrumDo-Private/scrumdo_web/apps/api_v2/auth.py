from piston.authentication import *
from django.utils.crypto import constant_time_compare
from django.conf import settings
from django.utils.http import is_same_domain

import logging
import re

logger = logging.getLogger(__name__)

REASON_NO_REFERER = "Referer checking failed - no Referer."
REASON_BAD_REFERER = "Referer checking failed - %s does not match %s."
REASON_NO_CSRF_COOKIE = "CSRF cookie not set."
REASON_BAD_TOKEN = "CSRF token missing or incorrect."
CSRF_KEY_LENGTH = 32

def _sanitize_token(token):
    if len(token) > CSRF_KEY_LENGTH:
        return None
    return re.sub('[^a-zA-Z0-9]+', '', str(token.decode('ascii', 'ignore')))


def _check_csrf(request):
    """ Logic stolen from django.middleware.csrf
    :param request:
    :return: True if the request should be allowed, false otherwise.
    """

    # Assume that anything not defined as 'safe' by RC2616 needs protection
    if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):

        try:
            csrf_token = _sanitize_token(request.COOKIES[settings.CSRF_COOKIE_NAME])
        except KeyError:
            csrf_token = None

        if getattr(request, '_dont_enforce_csrf_checks', False):
            # Mechanism to turn off CSRF checks for test suite.
            # It comes after the creation of CSRF cookies, so that
            # everything else continues to work exactly the same
            # (e.g. cookies are sent, etc.), but before any
            # branches that call reject().
            return True

        if request.is_secure():
            # Suppose user visits http://example.com/
            # An active network attacker (man-in-the-middle, MITM) sends a
            # POST form that targets https://example.com/detonate-bomb/ and
            # submits it via JavaScript.
            #
            # The attacker will need to provide a CSRF cookie and token, but
            # that's no problem for a MITM and the session-independent
            # nonce we're using. So the MITM can circumvent the CSRF
            # protection. This is true for any HTTP connection, but anyone
            # using HTTPS expects better! For this reason, for
            # https://example.com/ we need additional protection that treats
            # http://example.com/ as completely untrusted. Under HTTPS,
            # Barth et al. found that the Referer header is missing for
            # same-domain requests in only about 0.2% of cases or less, so
            # we can use strict Referer checking.
            referer = request.META.get('HTTP_REFERER')
            if referer is None:
                logger.warning('Forbidden (%s): %s',
                               REASON_NO_REFERER, request.path,
                    extra={
                        'status_code': 403,
                        'request': request,
                    }
                )
                return False

            # Note that request.get_host() includes the port.
            # good_referer = request.get_host()
            # if not is_same_domain(referer, good_referer):
            #     reason = REASON_BAD_REFERER % (referer, good_referer)
            #     logger.warning('Forbidden (%s): %s', reason, request.path,
            #         extra={
            #             'status_code': 403,
            #             'request': request,
            #         }
            #     )
            #     return False

        if csrf_token is None:
            # No CSRF cookie. For POST requests, we insist on a CSRF cookie,
            # and in this way we can avoid all CSRF attacks, including login
            # CSRF.
            logger.warning('Forbidden (%s): %s',
                           REASON_NO_CSRF_COOKIE, request.path,
                extra={
                    'status_code': 403,
                    'request': request,
                }
            )
            return False

        # Check non-cookie token for match.
        request_csrf_token = ""
        if request.method == "POST":
            request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')

        if request_csrf_token == "":
            # Fall back to X-CSRFToken, to make things easier for AJAX,
            # and possible for PUT/DELETE.
            request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

        if not constant_time_compare(request_csrf_token, csrf_token):
            logger.warning('Forbidden (%s): %s',
                           REASON_BAD_TOKEN, request.path,
                extra={
                    'status_code': 403,
                    'request': request,
                }
            )
            return False
    return True


class ScrumDoAuthentication(object):
    def __init__(self, realm='API'):
        self.auth_mechanisms = [
            OAuthAuthentication(realm=realm),
            HttpBasicAuthentication(realm=realm)
        ]

    def is_authenticated(self, request):
        for auth in self.auth_mechanisms:
            result = auth.is_authenticated(request)
            if result:
                # ok, yay, the user has authenticated with either OAuth or HTTP Basic
                # we shouldn't have to worry about CSRF attacks since the request explicitly
                # has authentication info in it.
                return result

        if request.user.is_authenticated():
            # allow normal session authentication.
            # BUT WHOA!  This could be a CSRF attack.  So let's make sure everything checks out.
            return settings.DEBUG or _check_csrf(request)
        return False


    def challenge(self, request=None):
        return self.auth_mechanisms[0].challenge()  # we'll only challenge on HTTP Basic

