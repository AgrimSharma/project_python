# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from apps.extras.interfaces import ScrumdoProjectExtra
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.defaultfilters import strip_tags

import logging

import slumber
from slumber.exceptions import *

import urllib2
import sys, traceback

from apps.kanban import util as kanban_util
from apps.extras.models import StoryQueue, SyncronizationQueue, ExternalStoryMapping


from apps.projects.models import Story, Project

logger = logging.getLogger(__name__)

import apps.github_integration as gi
from apps.github_integration.utils import update_issue, gh_log


class Plugin(ScrumdoProjectExtra):
    """ This Extra allows you to syncronize your GitHub issues with your ScrumDo stories. """

    def getName(self):
        """Friendly name to display in the configuration options to the user."""
        return "GitHub Integration"

    def isPremium(self):
        return True

    def getLogo(self):
        return settings.SSL_STATIC_URL + "extras/github-logo.png"

    def getSlug(self):
        """Returns a version of the name consisting of only letters, numbers, or dashes"""
        return "github"

    def getDescription(self):
        "Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user."
        return "Create ScrumDo stories for any open GitHub issue.  Push ScrumDo stories to GitHub issues.  Integrate with GitHub commit messages."

    def doProjectConfiguration( self, request, project, stage=""):
        """Handles a request to do configuration for the github_issues extra.
           This displays a form asking for credentials / repository information,
           then saves that with the saveConfiguration() api in ScrumdoProjectExtra base
           class.  After a successful configuration, we redirect back to the extras page.
           (Should each extra be responsible for that?)"""

        # Redirecting to a proper app is a way easier way to go!
        return HttpResponseRedirect( reverse('github_options',kwargs={'project_slug':project.slug}) )

    def storyDeleted( self, project, external_id, **kwargs):
        pass # we no longer have enough info to handle this event here.  Check out github_integration.views.onStoryDeleted

    def storyCreated( self, project, story, **kwargs):
        """ Called when a new ScrumDo story is created. This plugin creates a GitHub issue if the upload option is enabled. """
        if not self._isConfigured(project):
            return

        if self._getExternalLink( story ) != None:
            # Already uploaded
            return
            
        try:
            api = slumber.API("https://api.github.com", append_slash=False)
            for binding in gi.models.GithubBinding.objects.filter(project=project, upload_issues=True):
                # The upload_issues=True filter makes sure we only upload to projects with the option set.
                token = gi.models.GithubCredentials.objects.get(project=project)
                target_labels = self._getTargetLabels(story, api, binding, token)

                summary = strip_tags(story.summary)
                detail = strip_tags(story.detail)
                result = api.repos(binding.github_slug).issues.post( {'labels':target_labels, 'title':summary, 'body':detail}, access_token=token.oauth_token)
                logger.info(result)
                url = result['url']
                issue_number = url.split("/")[-1:][0]
                gh_log(project, "Created issue %s from story %s-%d (%d)" % (issue_number, project.prefix, story.local_id, story.id) )
                link = ExternalStoryMapping( story=story,
                                             extra_slug="github",
                                             external_id=issue_number,
                                             external_extra=binding.github_slug,
                                             external_url="https://github.com/%s/issues/%s" % (binding.github_slug, issue_number) )
                link.save()
                                
                if kanban_util.isStoryComplete(story):
                    # if the story is done, we have to close the issue...
                    q = SyncronizationQueue(project=project, story=story, extra_slug=self.getSlug(), action=SyncronizationQueue.ACTION_STORY_STATUS_CHANGED, external_id=issue_number)
                    q.save()

        except HttpClientError as e:
            gh_log(project, traceback.format_stack() )
            gh_log(project, "Could not create issue %s" % e, increment_count=True)
        


    def associate( self, project):
        pass

    def unassociate( self, project):
        if not self._isConfigured(project):
            return
        
        token = gi.models.GithubCredentials.objects.get(project=project)

        gi.models.GithubBinding.objects.filter(project=project).delete()    
        token.delete()

    def getShortStatus(self, project):
        try:
            configuration = self.getConfiguration( project.slug )
            return configuration.get("status")
        except:
            return "Not configured"

    # def getExtraStoryActions(self, project, story):
    #     """ Should return a list of tupples with a label, url, silk icon, that represent actions that a user can manually
    #         invoke for this extra on a story. Example: ('Syncronize','/blah/blah/syncronize','') """
    # 
    #     return [("Report Bug",
    #               reverse("github_report_bug",kwargs={'project_slug':project.slug, 'story_id':story.id}), 
    #              'bug')]


    def pullProject( self, project ):
        if not self._isConfigured(project):
            return
        # now handling most issues->scrumdo updates via the webhook callback
        # But (goshdarnit) there isn't a webhook for issue updates, only opens and closes        
        token = gi.models.GithubCredentials.objects.get(project=project)
        if token.failure_count > 1000:
            return  # Skipping out on long-erroring projects.
        for binding in gi.models.GithubBinding.objects.filter(project=project):
            self._pull(project, binding, token, create_if_missing=binding.download_issues)




    def storyImported(self, project, story):
        api = slumber.API("https://api.github.com",append_slash=False)        
        token = gi.models.GithubCredentials.objects.get(project=project)
        mapping = self._getExternalLink(story)
        if not mapping:
            logger.warn("on storyImported, no external link found")        

        gi.utils.add_github_tags(story)
        story.save()

        for binding in gi.models.GithubBinding.objects.filter(project=project):
            issue = api.repos(binding.github_slug).issues(mapping.external_id).get(access_token=token.oauth_token)
            logger.info("Retrieved issue %s" % issue)
            update_issue(issue, project, binding.github_slug, False, binding)


    def _pull(self, project, binding, token, create_if_missing=False):
        api = slumber.API("https://api.github.com",append_slash=False)        

        had_results = True
        issues = []
        page = 1

        try:
            rate = api.rate_limit.get(access_token=token.oauth_token)
        except:
            gh_log(project, "Could not connect to GitHub account.", increment_count=True)
            return

        while had_results:
            try:
                r = api.repos(binding.github_slug).issues.get(page=page, per_page=100, access_token=token.oauth_token)
                had_results = len(r) > 0
                issues = issues + r
                page += 1
            except urllib2.HTTPError as e:
                gh_log(project, "Could not download issues %s" % e, increment_count=True)
                had_results = False
            except HttpClientError as e:
                gh_log(project, "Could not download issues %s" % e, increment_count=True)                
                had_results = False
            except:
                had_results = False
        # logger.debug("Pull found %d issues" % len(issues))
        count = 0
        for issue in issues:
            try:
                if 'pull_request' not in issue:
                    update_issue(issue, project, binding.github_slug, create_if_missing, binding)
                count += 1
            except:
                logger.warn("Could not update issue")                
                traceback.print_exc(file=sys.stdout)    
        gh_log(project, "Syncronized %d stories" % count, increment_count=False)



    def initialSync( self, project):
        logging.debug("Performing initial GitHub issues syncronization.")
        for binding in gi.models.GithubBinding.objects.filter(project=project):
            self._initialSync(project, binding)
        
    def _initialSync(self, project, binding):
        if not self._isConfigured(project):
            return
        
        token = gi.models.GithubCredentials.objects.get(project=project)
        try:
            for story in project.stories.all():
                self.storyCreated( project, story )
        except:
            logging.debug("Failed to upload stories.")
            traceback.print_exc(file=sys.stdout)

        logging.debug("GitHubIssues::intialSync download starting up.")        

        # The configuration view sets a download flag to true/false depending on user input.
        if not binding.download_issues:
            logging.debug("Not set to download stories, aborting.")
            return

        self._pull(project, binding, token, create_if_missing=True)
        

    def storyUpdated( self, project, story , **kwargs):
        "Called when a story is updated in a project that this extra is associated with."
        
        logging.debug("GitHub::storyUpdated")

        if not self._isConfigured(project):
            return

        link = self._getExternalLink( story )

        if link == None:
            logging.debug("Story not associated with external story, aborting.")
            return

        logger.debug(link.external_extra)
        for binding in gi.models.GithubBinding.objects.filter(github_slug=link.external_extra, project=project):
            try:
                logger.debug("Updating issue")
                token = gi.models.GithubCredentials.objects.get(project=project)
                api = slumber.API("https://api.github.com",append_slash=False)   
                target_labels = self._getTargetLabels(story, api, binding, token)

                if binding.delete_issues:
                    state = "closed" if kanban_util.isStoryComplete(story) else "open"
                else:
                    state = "open"
                summary = strip_tags(story.summary)
                detail = strip_tags(story.detail)
                result = api.repos(binding.github_slug).issues(link.external_id).post({'labels':target_labels, 'state':state,'title':summary,'body':detail}, access_token=token.oauth_token)

                logger.debug("Updated issue")
            except HttpClientError as e:
                gh_log(project, "Could not update issue %s" % e, increment_count=True)            
            except:
                traceback.print_exc(file=sys.stdout)    
                logger.warn("Could not update issue")


    def _getTargetLabels(self, story, api, binding, token):
        """We can only send labels that already exist in GitHub or the call fails, this method
           figures out what labels are appropriate. """
        try:
            labels = api.repos(binding.github_slug).labels.get(per_page=100, access_token=token.oauth_token)
            labels = [l['name'] for l in labels]        
            target_labels = []
            for tag in story.story_tags_array():
                if tag in labels:
                    target_labels.append(tag)
            return target_labels
        except HttpClientError as e:
            gh_log(story.project, "Could not retrieve labels for issue %s" % e, increment_count=True)            
        except:
            gh_log(story.project, "Could not retrieve labels (error #1023)", increment_count=True)            

        return []
        

    def storyStatusChange( self, project, story, **kwargs):
        self.storyUpdated(project, story, **kwargs)  # updated does status too

    def _isConfigured(self, project):
        try:
            gi.models.GithubCredentials.objects.get(project=project)
        except gi.models.GithubCredentials.DoesNotExist:
            return False
        return True

    def _getExternalLink( self, story ):
        """ Searches for the ExternalStoryMapping that is associated with this extra and returns it.
            returns None if it's not found. """
        for link in story.external_links.all():
            if link.extra_slug == self.getSlug():
                return link
        return None



