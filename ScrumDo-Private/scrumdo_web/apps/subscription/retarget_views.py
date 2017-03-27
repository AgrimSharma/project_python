from apps.brake.decorators import ratelimit

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login as auth_login
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from apps.organizations.models import Organization
from .code_util import apply_subscription_code

from tutorial import createTutorialProject

from apps.classic.models import Project as ClassicProject
from apps.projects.models import Project
from apps.kanban.tasks import scheduleConvertClassicProject

import datetime
import mixpanel

from .code_util import valid_code, consume_code

CAMPAIGN = "USER_REACTIVATE"


def _setup_projects(organization):
    pass


@login_required
def retarget_upgrade(request):
    slug = request.POST.get('slug')
    organization = Organization.objects.get(slug=slug)
    if not organization.hasStaffAccess(request.user):
        raise PermissionDenied('You do not have access to that organization')

    subscription = organization.subscription
    subscription.is_trial = True
    subscription.plan_id = 3037
    subscription.expires = datetime.date.today() + datetime.timedelta(days=31)
    subscription.save()
    apply_subscription_code(organization, 'REDESIGN15')

    if Project.objects.filter(organization=organization).count() == 0:
        createTutorialProject(organization, request.user)
        for project in ClassicProject.objects.filter(active=True, organization=organization):
            scheduleConvertClassicProject(organization, project.id, request.user, 'temp')

    try:
        mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
        mp.track(organization.slug, 'Retarget upgrade')
    except:
        pass

    return render_to_response("subscription/retarget_upgrade.html",
                              {'organization':organization},
                              context_instance=RequestContext(request))


@login_required
def retarget_org_choose(request):
    orgs = list(Organization.getStaffOrganizationsForUser(request.user))
    return render_to_response("subscription/retarget_org_choose.html",
                              {'orgs': orgs},
                              context_instance=RequestContext(request))


@ratelimit(rate='20/m', block=True)
def retarget(request, key):
    code = valid_code(key, CAMPAIGN)

    if not code:
        if request.user.is_authenticated():
            return redirect("/")

        return render_to_response("subscription/retarget_invalid_code.html", context_instance=RequestContext(request))

    user = code.user

    password = request.POST.get('password', '')
    if len(password) > 3:
        consume_code(code.code, CAMPAIGN)
        user.set_password(password)
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        return redirect('retarget_org_choose')

    return render_to_response("subscription/retarget_valid_code.html",
                              {'code':code},
                              context_instance=RequestContext(request) )
