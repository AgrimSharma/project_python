# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from apps.extras.interfaces import ScrumdoProjectExtra
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.conf import settings
from apps.commercial_plugins.tasks import generateATDDFile
from django.utils.translation import ugettext_lazy as _

import datetime
import logging
import sys, traceback

from apps.projects.models import Story, FileJob
from forms import ExportForm
import apps.extras.signals as extras_signals

logger = logging.getLogger(__name__)

class ATDDExtra( ScrumdoProjectExtra ):
    def __init__(self):
        self.requiresAdmin = False

    def doProjectConfiguration( self, request, project, stage=""):
        choices = [("summary","Summary"),("detail","Detail"),("extra_1",project.extra_1_label), ("extra_2",project.extra_2_label), ("extra_3", project.extra_3_label) ]

        if request.method == "POST":
            form = ExportForm(project, choices, request.POST)
            if form.is_valid():
                iteration = form.cleaned_data['iteration']
                job = FileJob( organization=project.organization, file_type="atdd_export", owner=request.user, completed=False) 
                job.save()
                generateATDDFile.apply_async((
                    project.id, iteration.id, 
                    job.id, form.cleaned_data["field"],
                    'txt' if form.cleaned_data["type"] == 'txt' else 'feature'
                ), countdown=3)
                return HttpResponseRedirect( reverse("file_job_download", kwargs={"job_id":job.id} ) )

        form = ExportForm(project, choices, initial={'type': 'txt'})

        return render_to_response("plugins/atdd/export_page.html", {
            "project": project,
            "form": form
            }, context_instance=RequestContext(request))

                

    def getName(self):
        "Friendly name to display in the configuration options to the user."
        return "ATDD Export"

    def getLogo(self):
        return settings.SSL_STATIC_URL + "extras/atdd.png"

    def getSlug(self):        
        return "atdd"

    def getDescription(self):
        return "Export a portion of your stories suitable for ATDD tools"

    def getExtraActions( self, project, **kwargs):
        return []
        

    def storyDeleted( self, project, external_id, **kwargs):
        pass
            


    def storyCreated( self, project, story, **kwargs):
        pass        
        

    def associate( self, project):
        pass

    def unassociate( self, project):
        pass

    def getShortStatus(self, project):
        return "Ready"


    def pullProject( self, project ):
        pass
            
            

    def initialSync( self, project):        
        pass

    def storyUpdated( self, project, story , **kwargs):
        pass

    def storyStatusChange( self, project, story, **kwargs):
        pass    



Plugin = ATDDExtra