#!/usr/bin/env python

from apps.activities.models import NewsItem
from apps.projects.models import Commit, Story
from apps.github_integration.models import *
from apps.github_integration.views import gh_log
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import re
import slumber
import logging
import string
logger = logging.getLogger(__name__)

string_types = (string.ascii_lowercase, string.ascii_uppercase, string.digits)

class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) == 0:
            logger.error("Please specify a project slug")
            return
        projectSlug = args[0]
        logger.info("Processing project %s" % projectSlug)
        credential = GithubCredentials.objects.get(project__slug=projectSlug)
        for binding in GithubBinding.objects.filter(project__slug=projectSlug):
            self.fixForCredentials(credential, binding, projectSlug)

    def fixForCredentials(self, credential, binding, projectSlug):
        logger.info(" Processing repo %s" % binding.github_slug)
        # marc-hughes/git-test-2
        #
        access_token = credential.oauth_token
        # /repos/:owner/:repo/commits
        api = slumber.API("https://api.github.com/repos/%s" % binding.github_slug,append_slash=False)
        branches = api.branches.get(access_token=access_token)
        commits = []
        project = Project.objects.get(slug=projectSlug)
        for branch in branches:
            sha = branch["commit"]["sha"]
            commits += api.commits().get(page=1, per_page=100, since="2014-10-13T01:01:00Z", access_token=access_token)
            commits += api.commits().get(page=2, per_page=100, since="2014-10-13T01:01:00Z", access_token=access_token)
            commits += api.commits().get(page=3, per_page=100, since="2014-10-13T01:01:00Z", access_token=access_token)

        logger.info("Found %d commits" % len(commits))
        for commit in commits:
            self.processCommit(project, binding.github_slug, commit)

    def processCommit(self, project, github_slug, commit):
        name = commit["sha"][0:7]
        try:
            Commit.objects.get(story__project=project, name=name)
            logger.info("Found commit %s" % name)
        except Commit.MultipleObjectsReturned:
            pass
        except Commit.DoesNotExist:
            logger.info("Commit %s not found, creating" % name)
            self.logCommit(project, commit)


    def logCommit(self, project, commit):
        commit_msg = commit["commit"]["message"]

        for match in re.finditer("(card #|story #|%s)([0-9]+)" % settings.STORY_LINKING_PREFIX_TOKEN, commit_msg, re.IGNORECASE ):
            try:
                story = project.stories.get(local_id=match.group(2) )
                story.has_commits = True
                story.save()
                c = Commit(story=story,
                            name=commit["sha"][:7],
                            link=commit["html_url"],
                            full_text=commit_msg )
                c.save()
                gh_log(project, "Updated story #%d from commit message" % (story.local_id, ) )
            except Story.DoesNotExist:
                logger.info("Story not found")
            except Story.MultipleObjectsReturned:
                pass
                
        for match in re.finditer("(card |story )([A-Z,a-z,0-9]{2})-([0-9]+)", commit_msg, re.IGNORECASE ):
            try:
                story = project.stories.get(local_id=match.group(3) )
                story.has_commits = True
                story.save()
                c = Commit(story=story,
                            name=commit["sha"][:7],
                            link=commit["html_url"],
                            full_text=commit_msg )
                c.save()
                gh_log(project, "Updated story %s-%d from commit message" % (project.prefix, story.local_id) )
            except Story.DoesNotExist:
                logger.info("Story not found")
            except Story.MultipleObjectsReturned:
                pass




