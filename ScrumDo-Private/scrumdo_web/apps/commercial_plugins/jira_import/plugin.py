# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is not licensed for redistribution in any form.

from apps.extras.interfaces import ScrumdoProjectExtra
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.template.defaultfilters import slugify


from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


from apps.attachments.models import Attachment

import urllib2
import urllib
import datetime
import logging
import sys, traceback

from apps.extras.models import StoryQueue, SyncronizationQueue, ExternalStoryMapping, ExternalTaskMapping
from apps.projects.models import *
import forms
import re
import time
import apps.extras.signals as extras_signals

from jira import Jira
import configuration

logger = logging.getLogger(__name__)

class JiraExtra( ScrumdoProjectExtra ):
    """ This Extra allows you to worl with Jira """

    def getName(self):
        "Friendly name to display in the configuration options to the user."
        return "Jira Import"

    def getLogo(self):
        return settings.SSL_STATIC_URL + "extras/jira_logo.png"

    def getSlug(self):
        "Returns a version of the name consisting of only letters, numbers, or dashes"
        return "jira-import"

    def getDescription(self):
        return "Perform a one time import from Jira"

    def doProjectConfiguration( self, request, project, stage=""):     
        return configuration.doProjectConfiguration(self, request, project, stage)    

    def isPremium(self):
        return False

    def getExtraStoryActions(self, project, story):
        return []

    def getExtraActions( self, project, **kwargs):        
        return []

    def storyDeleted( self, project, external_id, **kwargs):
        pass # not going to delete the Jira issue

    def storyCreated( self, project, story, **kwargs):
        pass # No automatic issue creation.
    
    
    def _updateStory(self, project, story, issue, config):
        pass
    
    def _createStoryQueue(self, project, issue, config ):
        pass
    
    def _buildURL( self, config, key ):
        # http://localhost:8080/browse/SCRUMDO-1
        return "%s/browse/%s" % (config[configuration.URL_FIELD],key)
      
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
    
    def getUser(self, username):
        user_map = {
            'azack':'azack',
            'aforrister':'aforrister',
            'bhartlaub':'bhartlaub',
            'chanddos':'cdoss_scholastic',
            'dvishwanathan':'deepak',
            'dlake':'diannlak',
            'fhatoum':'fedhat',
            'harisp':'harisp',
            'hweiner':'henrywiener',
            'jharris':'harrisjm3',
            'jleeman':'jleeman',
            'jwhitted':'jwhitted',
            'jbuszka':'jim_buszka',
            'jrothstein':'jrothstein',
            'jjenkins':'Jonah',
            'jfox':'jfoxgrt',
            'khor':'khor',
            'kbabetski':'KBabetski',
            'ksmith':'ksmith',
            'kmcart':'kamcart',
            'mpaul':'mpaul',
            'mravi':'meerarav',
            'modonnell':'modonnell',
            'rock':'rock',
            'melnaccash':'minaelnaccash',
            'nsingh':'nsingh00',
            'nmancini':'nmancini',
            'sblake':'shanblake',
            'tobrien':'tmo9d',
            'wliang':'wliang87',
            'yshen':'yshen',
            'jgarzon':'juangrt',
            'jhageman':'jennyh_inactive',
            'gmsith':'gsmith',
            'swinz':'swinz',
            'ksandhu':'ksandhu',
            'jaspinall':'julia_a_inactive',
            'brathakrishnan':'balarkrishnan',
            'imo001':'IraMo'
        }
        if username in user_map:
            return User.objects.get(username=user_map[username])
        else:
            return User.objects.get(username="former_jira_user")

    def initialSync( self, project):        
        logger.info("Beginning import")
        iterations = {}        
        try:                       
            config, jira = self._getConfigJira(project)


            status_map = {
                1:1,
                3:4,
                4:4,
                5:6,
                6:10,
                10000:5,
                10001:7,
                10003:8,
                10004:4,
                10005:4,
                10006:4
            }
            queue_stories = StoryQueue.objects.filter( project=project, extra_slug=self.getSlug() )
            # project_stories = self._getStoriesInProjectAssociatedWithExtra( project )        
            
            filterID = config[configuration.FILTER_FIELD]
            bugCount = jira.getIssueCount( filterID )
            logger.info("About to process %d bugs" % bugCount )
            offset = 0
            while True:
                issues = jira.getIssues(filterID, offset, 20)
                count = len(issues) 
                if count == 0:
                    break
                offset += count
                
                # if offset > 40: 
                #     return # debug 
                    
                for issue in issues:
                    # logger.info(issue)

                    try:
                        logger.info("Create story for %s" % issue['key'])


                        # logger.info(issue["fixVersions"])
                        
                        if len(issue["fixVersions"]):
                            iter_name = issue["fixVersions"][0]["name"]
                            if iter_name in iterations:
                                iteration = iterations[iter_name]
                            else:
                                iteration = Iteration(project=project, name=iter_name) #default iteration type is fine
                                iteration.save()
                                iterations[iter_name] = iteration
                        else:
                            iteration = project.get_default_iteration()
                        
                        story = Story(project=project, 
                                      iteration=iteration, 
                                      summary=issue['summary'],
                                      detail="(Imported Jira %s)  \n%s" % (issue['key'],issue['description']),
                                      rank=issue['priority'],        
                                      local_id=project.getNextId(),
                                      creator=self.getUser(issue['reporter'])                              
                                      )
                        s = int(issue['status'])
                        if s in status_map:
                            story.status = status_map[s]
                        story.save()
                        
                        tags = ""
                        if issue['type'] == '6':
                            tags += 'Epic, '
                        
                        for c in issue['components']:
                            component = c['name']
                            tags += slugify( component ) + ", "
                        
                        story.tags = tags
                        
                        for c in issue['customFieldValues']:

                            if c['customfieldId'] == 'customfield_10031':
                                story.extra_1 = c['values'][0]

                            if c['customfieldId'] == 'customfield_10003':
                                story.points = c['values'][0]
                                
                            if c['customfieldId'] == 'customfield_10033' or c['customfieldId'] == 'customfield_10032':                                
                                try:
                                    story.assignee.add( self.getUser( c['values'][0] ))
                                except:
                                    pass
                        
                        try:
                            story.assignee.add( self.getUser(issue['assignee']) )
                        except:
                            pass
                        
                        for comment in jira.getComments(issue['key']):
                            try:
                                c = StoryComment()
                                c.story = story
                                c.user = self.getUser(comment['author'])
                                c.comment = comment["body"]
                                c.save()
                            except:
                                pass
                        
                        for attachment in jira.getAttachmentsFromIssue(issue["key"]):
                            # https://samconnect.atlassian.net/secure/attachment/13025/Beta-3rd%20para%20missing%20in%20email.JPG
                            # url = "https://samconnect.atlassian.net/secure/attachment/%s/%s" % (attachment['id'], attachment['filename'])
                            
                            c = StoryComment()
                            c.story = story
                            c.user = self.getUser(attachment['author'])
                            c.comment = "Attached file %s" % attachment['filename']
                            c.save()
                           
                            #                            
                            # a = Attachment(content_object=story,
                            #                creator=self.getUser(attachment['author']),
                            #                attachment_file=img_temp )
                            # a.save()
                            # logger.info("ATTACHED FILE TO %d" % story.id)
                            

                            # a.attachment_file.save("image_%d" % a.id, File(img_temp))
                            # a.save()

                        story.resetCounts()
                    except:
                        logger.error("Could not sync issue %s" % issue.key)
                        traceback.print_exc(file=sys.stdout)

                        
            logger.info("Processed %d bugs" % offset) 
            self.setStatus(project,config,"Import successful on " + str( datetime.date.today()  ), False)            
        except:
            if config:
                self.setStatus(project,config,"Import failed on " + str( datetime.date.today()  ), False)
        

    def storyUpdated( self, project, story , **kwargs):        
        pass

    def taskStatusChange(self, project, task):
        pass



    def storyStatusChange( self, project, story, **kwargs):
        pass
            
    def storyImported(self, project, story):
        # No automatic issue creation.
        pass


    def _getExternalLink( self, story ):
        """ Searches for the ExternalStoryMapping that is associated with this extra and returns it.
            returns None if it's not found. """
        for link in story.external_links.all():
            if link.extra_slug == self.getSlug():
                return link
        return None

   
    def _getTaskLink( self, task ):
        # We don't map tasks to jira issues in this plugin
        return None
    
    def _isConfigured(self, project):
        config = self.getConfiguration( project.slug )
        return (configuration.URL_FIELD in config) and (configuration.USERNAME_FIELD in config) and (configuration.PASSWORD_FIELD in config) and (configuration.IMPORT_FIELD in config)
    
    def _getConfigJira(self, project):
        config = self.getConfiguration( project.slug )
        url = config[configuration.URL_FIELD]
        username = config[configuration.USERNAME_FIELD]
        password = config[configuration.PASSWORD_FIELD]
        jira = Jira(url, username, password)
        return (config, jira)


Plugin = JiraExtra
