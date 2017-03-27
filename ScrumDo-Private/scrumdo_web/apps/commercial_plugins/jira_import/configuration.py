# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.conf import settings
import logging
from jira import Jira
import forms
from apps.extras.models import SyncronizationQueue

IMPORT_FIELD="import"
URL_FIELD="url"
USERNAME_FIELD="username"
PASSWORD_FIELD="password"
CONFIGURED_FIELD="configured"
FILTER_FIELD="filter"
FILTER_NAME_FIELD="filterName"
PROJECT_FIELD="project"
STATUS_FIELD="status"

STATUS_TODO="todo"
STATUS_DONE="done"
STATUS_REVIEWING="review"
STATUS_DOING="doing"

logger = logging.getLogger(__name__)

def doProjectConfiguration(extra, request, project, stage=""):
    configuration = extra.getConfiguration( project.slug )
    
    if stage == "import":    
        # logger.debug("Setting to sync")
        configuration[STATUS_FIELD] = "Importing..."
        extra.manager.queueSyncAction( extra.getSlug(), project, SyncronizationQueue.ACTION_INITIAL_SYNC )
        return doConfigurationSummary(extra, request, project, configuration)
    
    
    isConfigured = configuration.get( CONFIGURED_FIELD )
    
    if isConfigured and (URL_FIELD in configuration) and stage == "report":
        return doReportBug(extra, request, project, configuration)
    
    if stage == "" and isConfigured:
        return doConfigurationSummary(extra, request, project, configuration)
    
    if stage == "filter":
        return doFilterConfiguration(extra, request, project, configuration)

    if stage == "statuses":
        return doStatusConfiguration(extra, request, project, configuration)

    if stage == "summary":
        return doConfigurationSummary(extra, request, project, configuration)

    return doCredentialsConfiguration(extra, request, project, configuration)


        
        

def doStatusConfiguration(extra, request, project, configuration):
    url = configuration[URL_FIELD]
    username = configuration[USERNAME_FIELD]
    password = configuration[PASSWORD_FIELD]
    jira = Jira(url, username, password)
    statuses = jira.getStatuses()
    form = forms.StatusForm( statuses )
    if request.method == "POST":
        form = forms.StatusForm( statuses, request.POST )
        if form.is_valid():
            configuration[STATUS_TODO] =      form.cleaned_data["todoStatus"]
            configuration[STATUS_DONE] =      form.cleaned_data["doneStatus"]
            configuration[STATUS_REVIEWING] = form.cleaned_data["reviewingStatus"]
            configuration[STATUS_DOING] =     form.cleaned_data["doingStatus"]
            logger.debug(configuration)
            extra.saveConfiguration( project.slug, configuration )
            return HttpResponseRedirect( reverse('configure_extra_with_stage', args=[extra.getSlug(), project.slug, "summary"]) )
    else:
        form = forms.StatusForm( statuses )
        
    return render_to_response("plugins/jira/config_status.html",
        {"project":project,
          "extra":extra,
          "form":form
        }, context_instance=RequestContext(request))

def doConfigurationSummary(extra, request, project, configuration):
    return render_to_response("plugins/jira/config_summary.html",
        {"project":project,
          "extra":extra,
          "configuration":configuration,          
        }, context_instance=RequestContext(request))
    

def doFilterConfiguration(extra, request, project, configuration):
    url = configuration[URL_FIELD]
    username = configuration[USERNAME_FIELD]
    password = configuration[PASSWORD_FIELD]
    jira = Jira(url, username, password)
    projects = jira.getProjects()
    projects = [(p.key, p.name) for p in projects]
    filters = jira.getFavouriteFilters()
    choices = [(choice.id, choice.name) for choice in filters]
    if request.method == "POST":
        form = forms.FilterForm(choices, projects, request.POST)
        if form.is_valid():
            configuration[CONFIGURED_FIELD] = True
            configuration[STATUS_FIELD] = "Configured"
            configuration[FILTER_FIELD] = form.cleaned_data["jiraFilter"]            
            configuration[FILTER_NAME_FIELD] = [choice[1] for choice in choices if choice[0] == form.cleaned_data["jiraFilter"] ][0]
            extra.saveConfiguration( project.slug, configuration )
            return HttpResponseRedirect( reverse('configure_extra_with_stage', args=[extra.getSlug(), project.slug, "summary"]) )            
    else:
        form = forms.FilterForm(choices, projects)
    return render_to_response("plugins/jira/config_filter.html",
        {"project":project,
          "extra":extra,
          "form":form
        }, context_instance=RequestContext(request))
    
    
def doCredentialsConfiguration(extra, request, project, configuration):
    """Prompts the user for url, username, password.  Verifies that those work and
     redirects to the next stage """

    if request.method == "POST":
        form = forms.CredentialsForm(request.POST)
        if form.is_valid():
            configuration[CONFIGURED_FIELD] = False
            configuration[USERNAME_FIELD] = form.cleaned_data['username']
            configuration[URL_FIELD] = form.cleaned_data['url']
            configuration[PASSWORD_FIELD] = form.cleaned_data['password']
            configuration[FILTER_FIELD] = ""
            extra.saveConfiguration( project.slug, configuration )
            return HttpResponseRedirect( reverse('configure_extra_with_stage', args=[extra.getSlug(), project.slug, "filter"]) )
            
    else:
        form = forms.CredentialsForm()

    return render_to_response("plugins/jira/config_credentials.html",
        {"project":project,
          "extra":extra,
          "form":form
        }, context_instance=RequestContext(request))
