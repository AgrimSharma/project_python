# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is not licensed for redistribution in any form.

from suds.client import Client
from suds.sax.date import DateTime as sudsdatetime
from django.core.cache import cache
import logging
import datetime
from django.core.urlresolvers import reverse
import hashlib
logger = logging.getLogger(__name__)
logging.getLogger('suds').setLevel(logging.WARN)

# How long to cache auth credentials for (10 minutes)
CACHE_AUTH_SECONDS = 600

class Jira(object):    
    def __init__(self, baseURL, username, password):
        self.baseURL = baseURL
        self.soap = Client(baseURL + "/rpc/soap/jirasoapservice-v2?wsdl")
        key = hashlib.sha224(baseURL + username + password).hexdigest()
        logger.debug(key)
        self.auth = cache.get( key )
        logger.debug(self.auth)
        if None == self.auth:
            self.auth = self.soap.service.login(username, password)
            cache.set(key, self.auth, CACHE_AUTH_SECONDS)
        logger.debug("Jira AUTH: %s" % self.auth)

    def getStatuses(self):
        return self.soap.service.getStatuses( self.auth )
    
    def createIssue(self, projectId, summary, desc):
        issue = dict(project=projectId, type="1", description=desc, summary=summary)
        logger.debug(issue)
        return self.soap.service.createIssue( self.auth, issue )
    
    def updateIssue(self, summary, detail, key):
        fields = [ dict(id="description", values=[detail]), dict(id="summary", values=[summary]) ]
        return self.soap.service.updateIssue( self.auth, key , fields )
    
    def addComment(self, key, comment):
        comment = dict( body=comment )
        return self.soap.service.addComment(self.auth, key, comment) 

    def getAttachmentsFromIssue(self, issue_key):
        return self.soap.service.getAttachmentsFromIssue(self.auth, issue_key)
    
    def getLinks(self, issue_key):
        return self.soap.service.getAllLinkedIssues(self.auth, issue_key)
        
        
    def getComments(self, issue_key):
        return self.soap.service.getComments(self.auth, issue_key)
        
    def getIssues(self, filterID, offset, maxResults):
        return self.soap.service.getIssuesFromFilterWithLimit(self.auth,
                                                              filterID,
                                                              offset,
                                                              maxResults)

    def getIssueCount(self, filterID):
        return self.soap.service.getIssueCountForFilter(self.auth, filterID)
    
    def getFavouriteFilters(self):
        return self.soap.service.getFavouriteFilters(self.auth)
        
    def getProjects(self):
        return self.soap.service.getProjectsNoSchemes(self.auth)

    def getFilters(self):
        return self.soap.service.getFavouriteFilters(self.auth)
        