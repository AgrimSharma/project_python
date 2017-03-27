# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

import apps.organizations.tz as tz
from apps.projects.calculation import onDemandCalculateVelocity
from apps.projects.forms import *
from apps.projects.access import *
from apps.subscription.decorators import *
import apps.projects.import_export as import_export
from story_views import handleAddStory

import json
import logging



logger = logging.getLogger(__name__)

@login_required
@expired_subscription_check
def iteration(request, group_slug, iteration_id):
    url = '{}#/iteration/{}/cards'.format(reverse('project_app', kwargs={'project_slug':group_slug}), iteration_id)
    return redirect(url)


@login_required
def iteration_import(request, group_slug, iteration_id):
    project = get_object_or_404(Project, slug=group_slug)
    iteration = get_object_or_404(Iteration, id=iteration_id)

    if iteration.locked:
        form_class = IterationImportFormWithUnlock
    else:
        form_class = IterationImportForm

    write_access_or_403(iteration.project,request.user)
    if request.method == "POST":
        form = form_class(request.POST)
        import_file = request.FILES.get("import_file",None)
        if form.is_valid() and import_file != None:
            unlock = form.cleaned_data.get("unlock_iteration",False)
            if unlock:
                iteration.locked = False
                iteration.save()
            imported, failed = import_export.importIteration(iteration, import_file, request.user )
            onDemandCalculateVelocity( project )
        return HttpResponse(json.dumps({'imported':imported, 'failed':failed}), content_type="application/json")
    else:
        form = form_class(  )

    return render_to_response('projects/import_options.html', { 'project':project, 'iteration':iteration, 'form': form,  }, context_instance=RequestContext(request))
