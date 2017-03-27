from .common import *
from apps.realtime.util import channelName
from apps.projects.models import MilestoneAssignment
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db.models import Q
from hashlib import sha256
from apps.favorites.models import Favorite
import pytz
import datetime

class UserHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('id',
              'email',
              'base_url',
              'organization',
              'username',
              'staff',
              'first_name',
              'last_name',
              'project_access',
              'avatar',
              "timezone",
              "staff_orgs",
              "milestone_statuses",
              "new_user")

    @staticmethod
    def new_user(user):
        days30 = datetime.timedelta(days=30)
        today = datetime.datetime.now()
        d = today - user.date_joined
        return (today - user.date_joined) < days30

    @staticmethod
    def milestone_statuses(user):
        return {status[0]: status[1] for status in MilestoneAssignment.STATUS}

    @staticmethod
    def base_url(user):
        return settings.BASE_URL

    @staticmethod
    def organization(user):
        org = user.org
        return {
            'planning_mode': org.planning_mode,
            'name': org.name,
            'slug': org.slug,
            'id': org.id,
            'subscription': UserHandler._get_sub_info(org)
        }


    @staticmethod
    def _get_sub_info(org):
        subscription = org.subscription
        mode = 'expired'
        if subscription.usersUsed() > subscription.planUsers():
            mode = 'overlimit'
        elif subscription.is_billed:
            mode = 'invoiced'
        elif subscription.is_trial:
            mode = 'trial'
        elif subscription.active:
            mode = 'paid'


        return {
            'mode': mode,
            'expires': (subscription.expires - datetime.date.today()).days if subscription.expires is not None else 999,
            'grace': (subscription.grace_until - datetime.date.today()).days if subscription.grace_until is not None else 0,
            'users': subscription.planUsers(),
            'premium_plan': subscription.plan.premium_plan,
            'projects': subscription.plan.projects
        }




    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug):
        org = Organization.objects.get(slug=organization_slug)

        if not org.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that Organization")

        user = request.user

        user.staff = org.hasStaffAccess(user)

        user.project_access = {}
        #for project in org.projects.filter(Q(project_type=Project.PROJECT_TYPE_KANBAN) | Q(project_type=Project.PROJECT_TYPE_PORTFOLIO), active=True):
        projects = get_users_cached_projects(org, request.user)
        for project in projects:
            if has_read_access(project, request.user):
                # always get fresh project from DB
                try:
                    updatedProject = org.projects.get(id = project.id)

                    user.project_access[project.slug] = {
                        'canRead': True,
                        'canAdmin': has_admin_access(project, request.user),
                        'canWrite': has_write_access(project, request.user),
                        'channel': channelName(project),
                        'subscribeKey': settings.PUBNUB_SUB_KEY,
                        'publishKey': settings.PUBNUB_PUB_KEY,
                        'uuid': sha256("%s%d" % (settings.SECRET_KEY, request.user.id)).hexdigest(),
                        'name': updatedProject.name,
                        'slug': project.slug,
                        'prefix': updatedProject.prefix,
                        'category': updatedProject.category,
                        'color': updatedProject.color,
                        'icon': updatedProject.icon,
                        'continuous_flow': project.continuous_flow_iteration is not None,
                        'isPortfolio': True if project.project_type == 2 else False,
                        'portfolioSlug':  project.portfolio_level.portfolio.root.slug if project.portfolio_level is not None else None,
                        'portfolioLevel': project.portfolio_level.level_number if project.portfolio_level is not None else None,
                        'project_type': project.project_type,
                        'favorite': Favorite.getFavorite(request.user, project) is not None
                    }
                except ObjectDoesNotExist:
                    # project get deleted or moved from Org
                    pass

        staffOrgs = []
        for o in Organization.getStaffOrganizationsForUser(request.user):
            staffOrgs.append({'name': o.name, 'slug': o.slug, 'id': o.id})

        user.org = org
        user.staff_orgs = staffOrgs
        user.avatar = "%s/avatar/avatar/24/%s" % (settings.SSL_BASE_URL, request.user.username)
        user.timezone = org.timezone
        return request.user

