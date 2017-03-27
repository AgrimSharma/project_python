# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.


from apps.extras.models import *
from apps.projects.models import Project, StoryComment

from apps.projects import util as project_utils
from apps.projects import signals as signals
from apps.kanban.models import BoardCell
from apps.kanban import managers as kanban_managers
from apps.kanban import util as kanban_util


from django.utils.text import slugify


from django.db.models.signals import pre_delete
from django.conf import settings
from django.template.defaultfilters import strip_tags

import apps.github_integration as gi
import logging
import slumber
import requests
import mixpanel

import sys, traceback

logger = logging.getLogger(__name__)

EXTRA_SLUG = "github"

# class UTC(tzinfo):
#     def utcoffset(self, dt):
#         return timedelta(0)
# 
#     def tzname(self, dt):
#         return "UTC"
# 
#     def dst(self, dt):
#         return timedelta(0)
# 
# utc = UTC()


def get_repo_name(user_repo):
    return user_repo.split("/")[-1:][0]


def add_github_tags(story):
    for link in story.external_links.filter(extra_slug='github'):
        repo_name = get_repo_name(link.external_extra)
        tagname = slugify(repo_name)
        existing = story.story_tags_array()
        if tagname not in existing:
            story.tags += ", " + tagname


def importProject(request, user, organization, project_slug, upload_issues, download_issues, close_on_delete, commit_messages):
    """ Import project from github to an organization, set up teams, set up GitHub extra, and trigger the initial sync.
    :param user:
    :param organization:
    :param project_slug:
    :param upload_issues:
    :param download_issues:
    :param close_on_delete:
    :param commit_messages:
    :return:
    """
    gho = gi.models.GithubOrganization.objects.get(organization=organization)
    api = slumber.API("https://api.github.com", append_slash=False)
    # /repos/:owner/:repo
    github_project = api.repos(project_slug).get(access_token=gho.oauth_token)
    github_teams = api.repos(project_slug).teams.get(access_token=gho.oauth_token)

    # project: description full_name  has_issues  html_url  name
    # teams: has id param
    projectName = github_project['name']
    project = Project(project_type=Project.PROJECT_TYPE_KANBAN,
                      creator=user,
                      category=github_project['owner']['login'],
                      name=projectName,
                      organization=organization,
                      slug=project_utils.generateProjectSlug(projectName))
    project.save()
    kanban_managers.initKanbanProject(project)
    for github_team in github_teams:
        teamId = github_team['id']
        try:
            ghteam = gi.models.GithubTeam.objects.get(github_team_id=teamId, team__organization=organization)
            ghteam.team.projects.add(project)
        except gi.models.GithubTeam.DoesNotExist:
            pass  # This is fine, just means the team isn't set up to sync.


    # Finally, set up the github project level integration.
    credentials = gi.models.GithubCredentials(user=user, project=project, oauth_token=gho.oauth_token, github_username=gho.github_username)
    credentials.save()

    binding = gi.models.GithubBinding(project=project,
                                      github_slug=github_project['full_name'],
                                      upload_issues=upload_issues,
                                      download_issues=download_issues,
                                      delete_issues=close_on_delete,
                                      log_commit_messages=commit_messages,
                                      commit_status_updates=commit_messages)
    binding.save()

    ProjectExtraMapping.objects.get_or_create(project=project, extra_slug='github')

    signals.project_created.send(sender=request, project=project, user=user)
    mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
    mp.track(organization.slug, 'Import Github Project')
    setupCallbacks(gho.oauth_token, binding, project)
    return project


def project_auth_url(projectSlug):
    return "%s?client_id=%s&scope=repo,read:org,write:repo_hook,user,repo:status&redirect_uri=%s/github/auth_callback/%s" % \
           (settings.GITHUB_AUTH_URL, settings.GITHUB_CLIENT_ID, settings.SSL_BASE_URL, projectSlug)

def org_auth_url(organizationSlug):
    return ("{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=repo,read:org,write:repo_hook,user,repo:status" + \
           "&redirect_uri={SSL_BASE_URL}/github/org_auth_callback/{organizationSlug}").\
               format(GITHUB_AUTH_URL=settings.GITHUB_AUTH_URL,
                      GITHUB_CLIENT_ID=settings.GITHUB_CLIENT_ID,
                      SSL_BASE_URL=settings.SSL_BASE_URL,
                      organizationSlug=organizationSlug)


def gh_log(project, message, increment_count=False):
    try:
        log = gi.models.GithubLog(project=project, message=message)
        log.save()
        if increment_count:
            cred = gi.models.GithubCredentials.objects.get(project=project)
            cred.failure_count += 1
            cred.save()
    except:
        logger.warn("Could not log message")


def _createComment(story, text):
    StoryComment(story=story, comment=text).save()


def _moveStoryToNotDone(story):
    if story.iteration.iteration_type != Iteration.ITERATION_WORK:
        # If we're not in a work iteration, there's really not a lot we can do about it.  Let's
        # just make a comment on the story.
        # _createComment(story, 'This card was set as opened in GitHub')
        return
    _createComment(story, 'This card was set as opened in GitHub so it has been moved into the default cell.')
    kanban_managers.moveStoryOntoDefaultCell(story, story.project, None, True)


def _moveStoryToDone(story):
    if story.iteration.iteration_type != Iteration.ITERATION_WORK:
        # If we're not in a work iteration, there's really not a lot we can do about it.  Let's
        # just make a comment on the story.
        # _createComment(story, 'This card was set as closed in GitHub')
        return
    cells = story.project.boardCells.filter(time_type=BoardCell.DONE_TIME)
    if cells.count() > 0:
        _createComment(story, 'This card was set as closed in GitHub so it has been moved into a done cell.')
        kanban_managers.moveStoryOntoCell(story, cells[0], None)
    else:
        _createComment(story, 'This card was set as closed in GitHub but no Done cells were found to move it to.')


def _updateStoryFromGithubStatus(story, github_state):
    storyIsComplete = kanban_util.isStoryComplete(story)
    if github_state == 'open' and storyIsComplete:
        _moveStoryToNotDone(story)
    if github_state == 'closed' and not storyIsComplete:
        _moveStoryToDone(story)


def update_issue(issue, project, repo_name, create_if_missing=False, binding=None):
    # first, try to update a story queue   
    try:
        qs = StoryQueue.objects.get(external_id=issue['number'],
                                    project=project,
                                    external_url=issue['html_url'],
                                    extra_slug=EXTRA_SLUG,
                                    external_extra=repo_name)

        if project.project_type == Project.PROJECT_TYPE_SCRUM:
            target_status = 1 if issue['state'] == 'open' else 10
        else:
            target_status = qs.status

        if (qs.summary != issue['title']) or (qs.detail != issue['body']) or (qs.status != target_status):
            qs.summary = issue['title']
            qs.external_url = issue['html_url']
            qs.detail = issue['body'] or ''
            qs.status = target_status
            qs.save()
            gh_log(project, "Updated story queue for %s" % str(issue['number']))


        return
    except StoryQueue.DoesNotExist:
        pass  # no existing story queue to update, no worries.

    # next, try to update a story proper
    try:
        mapping = ExternalStoryMapping.objects.get(external_extra=repo_name,
                                                   external_id=issue['number'],
                                                   extra_slug=EXTRA_SLUG,
                                                   external_url=issue['html_url'],
                                                   story__project=project)
        story = mapping.story        

        # updated_at = dateutil.parser.parse(issue['updated_at'])
        # if story.modified < updated_at:
        #     logger.debug("Updating story %s %s" % (updated_at, story.modified))

        target_status = story.status

        requires_save = False
        if (strip_tags(story.summary) != issue['title']) or (strip_tags(story.detail) != issue['body']):
            story.summary = issue['title']
            story.detail = issue['body'] or ''
            requires_save = True            
            gh_log(project, "Updated story %d for %s" % (story.local_id, str(issue['number']) ) )

        currentTags = story.story_tags_array()

        for label in issue["labels"]:
            tag = label["name"]            
            if not tag in currentTags:
                currentTags.append(tag)
                requires_save = True

        targetTags = ", ".join(currentTags)
        if story.tags != targetTags:
            story.tags = targetTags
            requires_save = True

        if requires_save:
            story.save()

        if binding.delete_issues:
            _updateStoryFromGithubStatus(story, issue['state'])

        return
    except ExternalStoryMapping.DoesNotExist:
        pass  # No existing story to update, again no worry

    if create_if_missing:
        qs = StoryQueue(external_id=issue['number'],
                        project=project,
                        extra_slug=EXTRA_SLUG,
                        summary=issue['title'],
                        detail=issue['body'] or '')
        qs.status = 1 if issue['state'] == 'open' else 10
        qs.external_url = issue['html_url']
        qs.external_extra = repo_name
        qs.save()
        gh_log(project, "Created story queue for %s" % str(issue['number']) )


def removeCallbacks(token, binding, project):
    api = slumber.API("https://api.github.com", append_slash=False)
    try:
        hooks = api.repos(binding.github_slug).hooks.get(access_token=token)
        for hook in hooks:
            try:
                if "scrumdo.com" in hook['config']['url'] and project.slug in hook['config']['url']:
                    api.repos(binding.github_slug).hooks(hook['id']).delete(access_token=token)
            except:
                logger.warn("Could not remove github webhook.")
                traceback.print_exc(file=sys.stdout)
    except:
        logger.warn("Error in finding hooks")
        traceback.print_exc(file=sys.stdout)



def setupCallbacks(token, binding, project, force_remove=False):
    removeCallbacks(token, binding, project)
    if force_remove:
        return

    logger.debug("Setting up callbacks...")
    base = settings.BASE_URL

    # api = slumber.API("https://api.github.com", append_slash=False)
    url = "https://api.github.com/repos/{repo}/hooks".format(repo=binding.github_slug)

    callback_url = "%s/github/webhook/%s" % (base, project.slug)

    try:
        active = (binding.log_commit_messages or binding.commit_status_updates)
        payload = {
          "name": "web",
          "active": active,
          "events": ["pull_request", "pull_request_review_comment", "issue_comment"],
          "config": {
              "url": "{callback_url}/pull_request".format(callback_url=callback_url),
              "content_type": "json"
          }
        }
        result = requests.post(url, data=json.dumps(payload), params={'access_token': token})

        active = (binding.log_commit_messages or binding.commit_status_updates)
        payload = {
          "name": "web",
          "active": active,
          "events": ["push"],
          "config": {
              "url": "{callback_url}/push".format(callback_url=callback_url),
              "content_type": "json"
          }
        }
        result = requests.post(url, data=json.dumps(payload), params={'access_token': token})


        active = (binding.download_issues or binding.upload_issues)
        payload = {
          "name": "web",
          "active": active,
          "events": ["issues"],
          "config": {
              "url": "{callback_url}/issues".format(callback_url=callback_url),
              "content_type": "json"
          }
        }
        result = requests.post(url, data=json.dumps(payload), params={'access_token': token})


        active = (binding.download_issues or binding.upload_issues)
        payload = {
          "name": "web",
          "active": active,
          "events": ["issue_comment"],
          "config": {
              "url": "{callback_url}/issue_comment".format(callback_url=callback_url),
              "content_type": "json"
          }
        }
        result = requests.post(url, data=json.dumps(payload), params={'access_token': token})


        gh_log(project, "Configuring GitHub webhooks")
    except slumber.exceptions.HttpClientError as e:
        gh_log(project, "Error: Could not configure GitHub webhooks")





def project_deleted(sender, instance, **kwargs):
    """Delete any github webhooks if the project is deleted."""
    project = instance
    try:
        ghc = gi.models.GithubCredentials.objects.get(project=project)
        for binding in gi.models.GithubBinding.objects.filter(project=project):
            removeCallbacks(ghc.oauth_token, binding, project)
    except gi.models.GithubOrganization.DoesNotExist:
        pass  # no worries, it wasn't set up.
    except:
        logger.warn("Could not remove github webhooks on project deletion.")

pre_delete.connect(project_deleted, sender=Project, dispatch_uid="github_integration")