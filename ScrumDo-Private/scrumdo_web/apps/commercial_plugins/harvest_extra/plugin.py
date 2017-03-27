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
import logging
import sys, traceback

from harvest import Harvest
from apps.extras.models import StoryQueue, SyncronizationQueue, ExternalStoryMapping
from apps.projects.models import Story

import forms
import re
import time
import apps.extras.signals as extras_signals

logger = logging.getLogger(__name__)

class HarvestExtra( ScrumdoProjectExtra ):
    """ This Extra allows you to push your stories to Harvest tasks"""

    def getName(self):
        "Friendly name to display in the configuration options to the user."
        return "Harvest"

    def getLogo(self):
        return settings.SSL_STATIC_URL + "extras/harvest_logo.png"

    def getSlug(self):
        "Returns a version of the name consisting of only letters, numbers, or dashes"
        return "harvest"

    def getDescription(self):
        return "Create Harvest tasks for your ScrumDo stories.  Track your time and invoice customers in Harvest.  Does not integrate with ScrumDo time tracking."

    def doProjectConfiguration( self, request, project, stage=""):
        configuration = self.getConfiguration( project.slug )
        if request.method == "GET":
            if configuration.get("configured") == True:
                return self.doProjectDisplayConfig(request, project, configuration)
            else:
                return self.doCredentialConfiguration(request, project, configuration)


        if request.POST.get("action") == "config_auth":
            return self.doCredentialConfiguration(request,project,configuration)
        elif request.POST.get("action") == "set_project":
            return self.doProjectSelectConfiguration(request,project,configuration)
        elif request.POST.get("action") == "reset":
            return self.doCredentialConfiguration(request, project, configuration)
            
    
    def doProjectDisplayConfig(self, request, project, configuration):
        if request.GET.get("syncronize",None) != None:
            configuration["configured"] = True
            configuration["in_progress"] = True
            configuration["sync_option"] = request.GET.get("syncronize")
            configuration["status"] = "Performing sync"
            if request.GET.get("syncronize") == "upload":
                configuration["iteration"] = request.GET.get("iteration")
                configuration["status"] = "Uploading iteration tasks to Harvest"
            if request.GET.get("syncronize") == "archive":
                configuration["status"] = "Archiving iteration tasks on Harvest"                            
                configuration["iteration"] = request.GET.get("iteration")
            if request.GET.get("syncronize") == "archive_all":
                configuration["status"] = "Archiving tasks on Harvest"            
            self.saveConfiguration( project.slug, configuration )
            self.manager.queueSyncAction(self.getSlug(), project, SyncronizationQueue.ACTION_INITIAL_SYNC)
            redirect_url = reverse('configure_extra_url' , kwargs={'project_slug':project.slug, "extra_slug":self.getSlug()})
            return HttpResponseRedirect(redirect_url)

        return render_to_response("plugins/harvest/display_config.html", {
            "config":configuration,
            "project":project,
            "extra":self
          }, context_instance=RequestContext(request))
    
    def doProjectSelectConfiguration(self, request, project, configuration):
        # logger.debug("doProjectSelectConfiguration")
        harvest = Harvest(configuration["url"],configuration["username"],configuration["password"])

            
        if request.method == "POST" and request.POST.get("project"):
            self.manager.queueSyncAction(self.getSlug(), project, SyncronizationQueue.ACTION_INITIAL_SYNC)
            p = request.POST.get("project")
            m = re.match('([^|]+)\|(.*)', p)
            # logger.debug("%s , %s" % (m.group(1),m.group(2)))
            configuration["project"] = m.group(1)
            configuration["project_name"] = m.group(2)       
            configuration["configured"] = True
            configuration["in_progress"] = True
            self.saveConfiguration( project.slug, configuration )                 
            redirect_url = reverse('configure_extra_url' , kwargs={'project_slug':project.slug, "extra_slug":self.getSlug()})
            return HttpResponseRedirect(redirect_url)


        projects = []
        for harvest_project in harvest.projects():
            # logger.debug(harvest_project)
            if harvest_project.active:
                projects.append( (harvest_project.name, harvest_project.id) )
            
        return render_to_response("plugins/harvest/configure_project.html", {
            "projects":projects,
            "project":project,
            "extra":self
          }, context_instance=RequestContext(request))

    def doCredentialConfiguration(self, request, project, configuration):
        if request.method == "POST" and request.POST.get("action","") != "reset":
            form = forms.HarvestConfig( request.POST )
            if form.is_valid():
                configuration = form.cleaned_data
                configuration["status"] = "Configuration Saved"
                self.saveConfiguration( project.slug, configuration )
                return self.doProjectSelectConfiguration(request,project,configuration)
        else:
            form = forms.HarvestConfig(initial=configuration)
        return render_to_response("plugins/harvest/configure.html", {
            "project":project,
            "extra":self,
            "form":form
          }, context_instance=RequestContext(request))

    def isPremium(self):
        return True

    def getExtraActions( self, project, **kwargs):
        try:
            iteration = kwargs.get("iteration")
            configuration = self.getConfiguration( project.slug )
            track_url = "%s/daily" % configuration["url"]
            if iteration:
                return [("Upload Tasks", "%s?syncronize=upload&iteration=%d" % (reverse("configure_extra_url",kwargs={'project_slug':project.slug,'extra_slug':self.getSlug()}),iteration.id), 'icon-upload-alt'),
                        ("Archive Tasks", "%s?syncronize=archive&iteration=%d" % (reverse("configure_extra_url",kwargs={'project_slug':project.slug,'extra_slug':self.getSlug()}),iteration.id), 'icon-folder-open'),                    
                        ("Track Time", track_url, 'icon-time')]
            else:
                return [("Archive All Tasks", "%s?syncronize=archive_all" % reverse("configure_extra_url",kwargs={'project_slug':project.slug,'extra_slug':self.getSlug()}), 'icon-folder-open'),
                        ("Track Time", track_url, 'icon-time')]
        except:
            return []
        

    def storyDeleted( self, project, external_id, **kwargs):

        pass # not going to delete the harvest task since there might be time recorded against it.

    def storyCreated( self, project, story, **kwargs):
        pass # No automatic story creation.
    
    def _updateStory(self, project, story, link, config):
        try:
            harvest = Harvest(config["url"],config["username"],config["password"])
            harvest.updateTask(link.external_id, story.summary )
        except:
            logger.warn("Failed to update story %d" % story.id)

      
    def _createStory(self, project, story, config):
        harvest = Harvest(config["url"],config["username"],config["password"])
        try:
            assignment_id, task_id, harvestURL = harvest.createTaskInProject(story.summary, config["project"])
            #external_extra
            link = ExternalStoryMapping( story=story,     
                                         extra_slug=self.getSlug(),
                                         external_id=task_id,
                                         external_extra=assignment_id )
            link.save()
        except urllib2.HTTPError as e:
             logger.error("HTTP Error %d occured while creating a harvest task" % e.code)
             logger.error("%s / %d" % (project.slug, story.id) )
             logger.error(e.headers)            
             logger.error(e.read())
             traceback.print_exc(file=sys.stdout)

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
        # logger.debug("Harvest::pullProject %s" % project.slug )
        configuration = self.getConfiguration( project.slug )
        pass # we're not pulling stories form Harvest into ScrumDo
            
    def _updateAllStories(self, project, configuration):
        # logger.debug("Updating all stories")
        for story in project.stories.all():
            link = self._getExternalLink( story )
            if link:
                self._updateStory(project, story, link, configuration)    
        
    def _uploadIteration(self, project, iteration_id, configuration):
        # logger.debug("Uploading iteration")
        iteration = project.iterations.get( id=iteration_id )
        for story in iteration.stories.all():
            link = self._getExternalLink( story )
            if link:
                link.delete()
            self._createStory(project,story,configuration)
    
    def _archiveProject(self, project, config):
        # logger.debug("Archiving Project")
        harvest = Harvest(config["url"],config["username"],config["password"])
        for story in project.stories.all():
            self._archiveStory(story, harvest, config["project"])          

    def _archiveIteration(self, project, iteration_id, config):
        # logger.debug("Archiving Iteration")
        iteration = project.iterations.get( id=iteration_id )
        harvest = Harvest(config["url"],config["username"],config["password"])
        for story in iteration.stories.all():
            self._archiveStory(story, harvest, config["project"])
        
    
    def _archiveStory(self, story, harvest, project_id ):
        link = self._getExternalLink( story )
        if link:              
            try:  
                harvest.removeTaskAssignmentFromProject(link.external_extra, project_id)
                harvest.removeTask(link.external_id)
            except:
                logger.warn("Could not remove harvest task.")
            link.delete()

    def initialSync( self, project):        
        configuration = self.getConfiguration( project.slug )
        #logging.debug("Performing Harvest synchronization on %s" % project.slug)
        try:
            if "sync_option" in configuration:
                sync_option = configuration["sync_option"]
                if sync_option == "now":
                    self._updateAllStories( project , configuration)
                elif sync_option == "upload":
                    self._uploadIteration( project, configuration["iteration"], configuration)
                elif sync_option == "archive":
                    self._archiveIteration( project, configuration["iteration"], configuration)
                elif sync_option == "archive_all":
                    self._archiveProject( project, configuration)
            configuration["status"] = "Synchronization Complete"        
        except Exception as exception:
            logger.warn("Failed harvest sync %s" % sys.exc_info()[2])
            configuration["status"] = "Synchronization Failed"
            configuration["in_progress"] = False        
            self.saveConfiguration( project.slug, configuration )
            raise        
        
        configuration["in_progress"] = False        
        self.saveConfiguration( project.slug, configuration )
        

    def storyUpdated( self, project, story , **kwargs):        
        # logger.debug("Harvest::storyUpdated %s %d" % (project.slug, story.id))
        configuration = self.getConfiguration( project.slug )        
        link = self._getExternalLink(story)
        self._updateStory(project, story, link, configuration)    

    def storyStatusChange( self, project, story, **kwargs):
        # logger.debug("Harvest::storyStatusChange %s %d" % (project.slug, story.id))
        configuration = self.getConfiguration( project.slug )        
        self.storyUpdated( project, story, **kwargs) 
            
    def storyImported(self, project, story):
        pass # Not auto-creating stories anymore.

    def _getStoriesInProjectAssociatedWithExtra(self, project):
        rv = []
        for story in project.stories.all():
            if self._getExternalLink( story ) != None:
                rv.append( story )
        return rv

    def _getStory( self, external_id, queue_stories, project_stories ):
        """ Pass in an external id, list of stories in the queue, and a list of stories in the project, and will return the story if the it exists in either list. """
        story = self._getStoryFromQueue( external_id, queue_stories)
        if story != None:
            return story
        return self._getStoryFromProject( external_id, project_stories )

    def _getTaskLink( self, task ):
        for link in task.external_links.all():
            if link.extra_slug == self.getSlug():
                return link
        return None

    # TODO - is this general enough to bump up to the super class?
    def _getExternalLink( self, story ):
        """ Searches for the ExternalStoryMapping that is associated with this extra and returns it.
            returns None if it's not found. """
        for link in story.external_links.all():
            if link.extra_slug == self.getSlug():
                return link
        return None

    def _getStoryFromProject(self, external_id, project_stories ):
        """ Returns the story from the list with the given external ID for this extra. """
        for project_story in project_stories:
            for link in project_story.external_links.all():
                if link.extra_slug == self.getSlug() and str(link.external_id)==str(external_id):
                    return project_story
        return None

    def _getStoryFromQueue(self, external_id, queue_stories ):
        """ Returns the story from the list of StoryQueue objects with the given external id. """
        for queue_story in queue_stories:
            if queue_story.extra_slug == self.getSlug() and int(queue_story.external_id)==external_id:
                return queue_story
        return None

Plugin = HarvestExtra