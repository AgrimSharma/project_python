from .common import *
from apps.subscription.models import *
from apps.organizations.models import Organization
from apps.subscription.templatetags.subscription_tags import daysuntil
from apps.subscription.spreedly import Spreedly
from apps.subscription.code_util import CodeAlreadyUsedException, apply_subscription_code
import apps.projects.limits as limits

import mixpanel
from urllib2 import HTTPError
from datetime import timedelta

def _available_plans():
        return {
            'monthly': SubscriptionPlan.objects.filter(active=True, yearly=False, price_val__gt=0),
            'annual': SubscriptionPlan.objects.filter(active=True, yearly=True),
        }




class SubscriptionPlanHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = SubscriptionPlan
    fields = ('yearly', 'epic_tool', 'planning_poker', 'kanban', 'premium_integrations', 'live_updates', 'id', 'price_val', 'tagline', 'storage', 'featured_plan', 'special_allowed', 'users', 'spreedly_id', 'price', 'premium_plan', 'show_in_grid', 'active', 'emails', 'projects', 'name', 'time_tracking', 'feature_level', 'custom_status', 'order')

    def read(self, request):
        return {'available_plans':_available_plans()}


class SubscriptionCodeHandler(BaseHandler):
    allowed_methods = ('POST', )

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug):
        org = Organization.objects.get(slug=organization_slug)

        if not org.hasStaffAccess(request.user):
            raise PermissionDenied('Only staff members can do this')

        code = request.data['code'].upper()
        subscription = org.subscription

        try:
            apply_subscription_code(org, code)
        except SubCode.DoesNotExist:
            return {'status': 'Code Not Found', 'subscription': subscription}
        except CodeAlreadyUsedException:
            return {'status': 'You have already used this code.', 'subscription': subscription}

        return {'status': 'Subscription Code Applied', 'subscription': subscription}



class SubscriptionHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('id',
              'can_upload',
              'can_kanban',
              'can_email', 'can_poker',
              'can_custom_status',
              'can_time_track',
              'days_left',
              'is_trial',
              'users_used',
              'available_plans',
              'spreedly_url',
              'token',
              'account_url',
              'billing',
              'can_live_update', ('plan',('id',
                                          'yearly',
                                          'name',
                                          'price_val',
                                          'price',
                                          'users',
                                          'isFree',
                                          'projects',
                                          'storage',
                                          'spreedly_id',
                                          'active',
                                          'premium_plan')))
    model = Subscription

    @staticmethod
    def spreedly_url(sub):
        return settings.SPREEDLY_PATH

    @staticmethod
    def account_url(sub):
        return sub.getAccountURL()

    @staticmethod
    def users_used(sub):
        return sub.usersUsed()


    @staticmethod
    def available_plans(sub):
        return _available_plans()


    @staticmethod
    def days_left(sub):
        if sub.expires is None:
            return 0
        return daysuntil(sub.expires)

    @staticmethod
    def can_upload(sub):
        return limits.org_storage_limit.increaseAllowed(organization=sub.organization)

    @staticmethod
    def can_kanban(sub):
        return True

    @staticmethod
    def can_email(sub):
        return limits.org_email_limit.increaseAllowed(organization=sub.organization)

    @staticmethod
    def can_poker(sub):
        return limits.org_planning_poker.increaseAllowed(organization=sub.organization)

    @staticmethod
    def can_custom_status(sub):
        return limits.org_custom_status.increaseAllowed(organization=sub.organization)

    @staticmethod
    def can_time_track(sub):
        return limits.org_time_tracking.increaseAllowed(organization=sub.organization)

    @staticmethod
    def can_live_update(sub):
        return limits.org_live_updates.increaseAllowed(organization=sub.organization)


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug):
        base = Organization.objects
        org = base.get(slug=organization_slug)
        if not org.hasReadAccess(request.user):
           raise PermissionDenied("You don't have access to that Organization")

        spreedly = Spreedly()
        try:
            account = spreedly.getSubscriptionForOrganization(org)
            org.subscription.billing = {
                'active': account['account_active'],
                'recurring': account['recurring'],
            }
        except HTTPError as e:
            org.subscription.billing = {
                'active': False,
                'recurring': False
            }

        return org.subscription

