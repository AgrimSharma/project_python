from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import timedelta

from django.shortcuts import get_object_or_404
from apps.brake.decorators import ratelimit
import apps.projects.access as access
from apps.projects.models import Project, ProjectShare, Iteration
from models import CellMovement, StepMovement, BacklogHistorySnapshot
from apps.subscription.decorators import expired_subscription_check
from django.conf import settings

import managers
import logging
logger = logging.getLogger(__name__)



@ratelimit(rate='20/m', block=True, method=['GET'])
@ensure_csrf_cookie
def shared_board(request, share_key):
    share = get_object_or_404(ProjectShare, key=share_key)
    return render_to_response("kanban/kanban_board_shared.html", {
        "project": share.project,
        "iteration": share.iteration,
        "CAN_WRITE" : False,
        "CAN_EDIT" : False,
        "ITERATION_ID": share.iteration_id,
        "organization": share.project.organization,
        "backlog_iteration_id": share.project.get_default_iteration().id,
        "share_key": share_key
    }, context_instance=RequestContext(request))

@ratelimit(rate='20/m', block=True, method=['GET'])
@ensure_csrf_cookie
def shared_project(request, share_key):
    project = get_object_or_404(Project, shared=share_key)
    shares = ProjectShare.objects.filter(project=project).order_by('iteration__start_date')
    return render_to_response("kanban/kanban_project_shared.html", {
        "shares": shares,
        "project": project,
        "organization": project.organization,
        "baseurl": settings.SSL_BASE_URL
    }, context_instance=RequestContext(request))


@login_required
@expired_subscription_check
@ensure_csrf_cookie
def kanban_board(request, project_slug):
    project = Project.objects.filter(slug=project_slug).select_related('organization')[0]

    access.read_access_or_403(project, request.user)

    iterationId = request.GET.get("iterationId", None)
    if iterationId is None:
        currentIteration = project.get_current_iterations(project.organization)
        if len(currentIteration) > 0:
            iterationId = currentIteration[0].id
        else:
            # There might not be a current iteration, so just pick the first work iteration for the default.
            work_iterations = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK)
            iterationId = work_iterations[0].id if work_iterations else None

    if iterationId:
        url = '{}#/iteration/{}/board'.format(reverse('project_app', kwargs={'project_slug':project_slug}), iterationId)
    else:
        url = '{}#/planning/planningcolumn?newIteration=true'.format(reverse('project_app', kwargs={'project_slug':project_slug}))
    return redirect(url)


def kanban_reports(request, project_slug):
    url = '{}#/reports/cfd'.format(reverse('project_app', kwargs={'project_slug':project_slug}))
    return redirect(url)


@login_required
@staff_member_required
def debug_rewind(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    access.write_access_or_403(project, request.user )
    for movement in StepMovement.objects.filter(workflow__project=project):
        movement.created = movement.created - timedelta(days=1)
        movement.save()
    for movement in CellMovement.objects.filter(story__project=project):
        movement.created = movement.created - timedelta(days=1)
        movement.save()
    managers.takeBacklogSnapshot(project)
    for snapshot in BacklogHistorySnapshot.objects.filter(backlog__project=project):
        snapshot.created = snapshot.created - timedelta(days=1)
        snapshot.save()
    return HttpResponse("ok")



