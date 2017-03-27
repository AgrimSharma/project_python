# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is not licensed for redistribution in any form.

from apps.extras.interfaces import ScrumdoProjectExtra
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import urllib2
import datetime
import string
import logging
import sys, traceback

from apps.extras.models import StoryQueue, SyncronizationQueue, ExternalStoryMapping, ExternalTaskMapping
from apps.projects.models import Story, Task
import apps.flowdock
import forms
import re
import time
import apps.extras.signals as extras_signals
import re

from django.contrib import messages # django 1.4


# import configuration

logger = logging.getLogger(__name__)

class FlowdockPlugin( ScrumdoProjectExtra ):
    """ This Extra allows you to work with Flowdock """

    def getName(self):
        "Friendly name to display in the configuration options to the user."
        return "Flowdock"

    def getLogo(self):
        return settings.SSL_STATIC_URL + "extras/flowdock_logo.png"

    def getSlug(self):
        "Returns a version of the name consisting of only letters, numbers, or dashes"
        return "flowdock"

    def getDescription(self):
        return "Post updates from ScrumDo to your Flowdock account"

    def doProjectConfiguration( self, request, project, stage=""):
        configuration = self.getConfiguration( project.slug )
        form = forms.SetupForm(initial=configuration)
        if request.POST:
            form = forms.SetupForm(request.POST)
            if form.is_valid():
                configuration['key'] = form.cleaned_data['key']
                self.saveConfiguration( project.slug, configuration )
                messages.add_message(request, messages.INFO, "Flowdock has been configured") # django 1.4

        return render_to_response("plugins/flowdock/configure.html", {
            "project": project,
            "form": form
          }, context_instance=RequestContext(request))

    def isPremium(self):
        return True

    def getExtraStoryActions(self, project, story):
        """ Should return a list of tupples with a label, url, silk icon, that represent actions that a user can manually
            invoke for this extra on a story. Example: ('Syncronize','/blah/blah/syncronize','') """
        return []

    def getExtraActions( self, project, **kwargs):        
        return []  

    def storyDeleted( self, project, external_id, **kwargs):
        pass #ignoring deleted stories

    def storyCreated( self, project, story, **kwargs):
        pass

    
      
    def _createStory(self, project, story, config):
        pass
        
    def associate( self, project):
        pass

    def unassociate( self, project):
        pass

    def getShortStatus(self, project):
        try:
            configuration = self.getConfiguration( project.slug )
            return configuration.get("status")
        except:
            return "Not configured"
        

    def pullProject( self, project ):
        pass
        

    def _updateStoryStatus(self, story, statusID, config):        
        pass
            
    def setStatus(self, project, config, status, in_progress):        
        config["status"] = status
        config["in_progress"] = in_progress
        self.saveConfiguration( project.slug, config )
        

    def initialSync( self, project):        
        pass

    def storyUpdated( self, project, story , **kwargs):        
        pass

    def taskStatusChange(self, project, task):
        pass


    def storyStatusChange( self, project, story, **kwargs):
        pass

    def _generateSubject(self, icon, story):
                
        if icon == "chart_organisation":
            return "Modified epic"
            
        if icon == "chart_organisation_add":
            return "Created epic"
        
        if icon == "chart_org_delete":
            return "Deleted epic"

        if story and icon == "drive_add":
            return "Created task on story %s-%d" % (story.project.prefix ,story.local_id)

        if story and icon == "drive_delete":
            return "Deleted task on story %s-%d" % (story.project.prefix ,story.local_id)

        if story and icon == "drive_edit":
            return "Edited task on story %s-%d" % (story.project.prefix ,story.local_id)

        if story and icon == "drive_go":
            return "Edited task on story %s-%d" % (story.project.prefix ,story.local_id)

        if story and icon == "flag_red":
            return "Scrum log posted"
            
        if story and icon == "comment_add":
            return "Comment on story %s-%d" % (story.project.prefix ,story.local_id)
        
        if story and icon == "script_add":
            return "Story %s-%d created" % (story.project.prefix ,story.local_id)
            
        if story and icon == "script_go":
            return "Story %s-%d moved" % (story.project.prefix ,story.local_id)
        
        if story and icon == "script_edit":
            return "Story %s-%d edited" % (story.project.prefix ,story.local_id)
        
        if story and icon == "script_code":
            return "Story %s-%d marked %s" % (story.project.prefix, story.local_id, story.statusText())
        return "ScrumDo update"

    def newsItemPosted(self, project, newsItem):
        "Called when a news item is posted to a project"
        if newsItem.icon == "group":
            return
        configuration = self.getConfiguration( project.slug )
        project_name = re.sub(r'[^a-zA-Z0-9_]', '', project.name)
        story = newsItem.related_story
        if story:
            link = "%s%s" % (settings.SSL_BASE_URL, story.get_absolute_url())
        else:
            link = settings.SSL_BASE_URL
        
        if newsItem.user:
            from_name = str(newsItem.user)
            body = "%s %s" % (from_name, newsItem.text)
        else:
            from_name = None
            body = newsItem.text  
        body = string.replace(body,'href="/','href="http://www.scrumdo.com/')
        flowdock.post(configuration['key'],
                      "ScrumDo",
                      "scrumdo@scrumdo.com",
                      self._generateSubject(newsItem.icon, newsItem.related_story),
                      body,
                      from_name,
                      project_name,
                      link)


    
    
    def _post(self, key, story, summary):
        if story.assignees_cache:
            message = "Assigned: %s<br/>%s<br/>%s" % (story.assignees_cache, story.summary, story.detail)
        else:
            message = "%s<br/>%s" % (story.summary,story.detail)
            
        link = "%s%s" % (settings.SSL_BASE_URL, story.get_absolute_url())
        project_name = re.sub(r'[^a-zA-Z0-9_]', '', story.project.name)
        flowdock.post(key,
                      "ScrumDo",
                      "scrumdo@scrumdo.com",
                      summary,
                      message,
                      None,
                      project_name,
                      link)
    def storyImported(self, project, story):
        pass




Plugin = FlowdockPlugin