# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.kanban.models import BoardCell


import re
import urllib2
import slumber
import traceback
import requests
import sys

from urlparse import parse_qs
from apps.projects.models import *
import apps.projects.signals as project_signals
from apps.projects.access import *
from apps.github_integration.forms import *

from apps.extras.models import *
from slumber.exceptions import *
from django.contrib import messages
from django.conf import settings

import rollbar

from tasks import handle_issues_webhook

from apps.github_integration.utils import gh_log

from apps.realtime import util as realtime_util
from apps.kanban import managers as kanban_manager

logger = logging.getLogger(__name__)

EXTRA_SLUG = "github"


def _handle_issue_comment_webhook(request, project, payload):
    pass


def get_referenced_stories(text, project):
    rv = set()

    if text is None or text == '':
        return rv

    for match in re.finditer("(card #|story #|%s)([0-9]+)" % settings.STORY_LINKING_PREFIX_TOKEN, text, re.IGNORECASE ):
        try:
            story = project.stories.get(local_id=match.group(2) )
            rv.add(story)
        except Story.DoesNotExist:
            pass
    # to accept card prefix command
    for match in re.finditer("(card |story )([A-Z,a-z,0-9]{2})-([0-9]+)", text, re.IGNORECASE ):
        try:
            story = project.stories.get(local_id=match.group(3) )
            rv.add(story)
        except Story.DoesNotExist:
            pass
    return rv


def _handle_pull_request_webhook(request, project, payload):
    """Handles a github webhook related to pull requests.  Can deal with pull_request pull_request_review_comment and issue_comment"""
    if 'pull_request' in payload:
        _handle_pull_payload(project, payload['pull_request'])
    if 'issue' in payload and 'pull_request' in payload['issue'] and payload['issue']['pull_request'] is not None:
        _handle_pull_comment(request, project, payload)


def _handle_pull_payload(project, pull_request):
    """Does the work of the pull request payload, after we get the proper pull_request payload retrieved."""
    stories = get_referenced_stories(pull_request['title'], project)
    stories = stories.union(get_referenced_stories(pull_request['body'], project))
    # Do we want to check comment and sub issues?  I think so...  But I don't want any of that to cause a failure.
    try:
        token = GithubCredentials.objects.get(project=project).oauth_token
        commits_url = pull_request['_links']['commits']['href']
        result = requests.get(commits_url, {'access_token':token}).json()
        for commitResult in result:
            commit = commitResult['commit']
            stories = stories.union(get_referenced_stories(commit['message'], project))

        comments_url = pull_request['_links']['comments']['href']
        result = requests.get(comments_url,{'access_token':token}).json()
        for comment in result:
            stories = stories.union(get_referenced_stories(comment['body'], project))
    except:
        pass

    if len(stories) == 0:
        # If no stories, we don't care about it.
        return

    pr_url = pull_request['html_url']
    try:
        pr = PullRequest.objects.get(link=pr_url)
    except PullRequest.MultipleObjectsReturned:
        # There could be a problem in the past where multiple requests
        pr = PullRequest.objects.filter(link=pr_url)[0]
        # TODO: How should we clean this up...??
    except PullRequest.DoesNotExist:
        pr = PullRequest(link=pr_url)

    # Update the pull request details
    pr.state = PullRequest.STATUS.closed if pull_request['state'] == 'closed' else PullRequest.STATUS.open
    name = "#{number} {title}".format(number=pull_request['number'], title=pull_request['title'][:64])
    pr.name = name[:64]
    pr.full_text = pull_request['title'] + pull_request['body']
    pr.save()

    # Now, we should have a PullRequest and a full list of stories that this card references.

    for story in stories:
        if not story.has_commits:
            story.has_commits = True
            story.skip_haystack = True
            story.save()
        pr.stories.add(story)


def _handle_pull_comment(request, project, payload):
    """Handles the issue_comment github webhook and extracts the pull_request if one exists."""
    try:
        token = GithubCredentials.objects.get(project=project).oauth_token
        pull_url = payload['issue']['pull_request']['url']
        result = requests.get(pull_url, {'access_token':token}).json()
        _handle_pull_payload(project, result)
    except:
        pass


def _getCommitUser(email_address):
    try:
        return User.objects.filter(email=email_address)[0]
    except:
        return None


def _updateFromCommit(commit, project):
    if not "message" in commit:
        return
    commit_msg = commit["message"]
    stories = get_referenced_stories(commit_msg, project)
    for story in stories:
        if not story.has_commits:
            story.has_commits = True
            story.save()
        commithash = commit["id"][:7]
        try:
            Commit.objects.get(story=story, name=commithash)
        except Commit.DoesNotExist:  # We want to avoid duplicate commit hashes on the same card.
            c = Commit(story=story,
                        name=commithash,
                        link=commit["url"],
                        full_text=commit_msg )
            c.save()
        gh_log(project, "Updated story %s-%d from commit message" % (project.prefix, story.local_id) )
            

    cells = list(BoardCell.objects.filter(project=project))
    status_filter = "|".join(["%s|%s" % (cell.full_label, cell.label) for cell in cells])

    for match in re.finditer("(card #|story #|%s)([0-9]+) (%s)" % (settings.STORY_LINKING_PREFIX_TOKEN, status_filter), commit_msg, re.IGNORECASE ):
        _move_story_to_cell(match.group(2), match.group(3), cells, commit, project)

    for match in re.finditer("(card |story )([A-Z,a-z,0-9]{2})-([0-9]+) (%s)" % (status_filter,), commit_msg, re.IGNORECASE ):
        _move_story_to_cell(match.group(3), match.group(4), cells, commit, project)


def _move_story_to_cell(local_id, cell_name, cells, commit, project):
    try:
        story = project.stories.get(local_id=local_id)
        candidate_cell_name = cell_name.lower().strip()
        candidates = [cell for cell in cells if cell.full_label.lower() == candidate_cell_name]
        if len(candidates) == 0:
            candidates = [cell for cell in cells if cell.label.lower() == candidate_cell_name]
        if len(candidates) > 0:
            target_cell = candidates[0]
            user = _getCommitUser(commit['author']['email'])
            kanban_manager.moveStoryOntoCell(story, target_cell, user)
            realtime_util.send_story_patch(project, story, {'cell_id': target_cell.id})
    except:
        pass

def _handle_push_webhook(request, project, payload):
    if not "commits" in payload:
        return

    logger.info("Received GitHub webook")    

    for commit in payload["commits"]:
        if commit["message"][:5] != "Merge":
            _updateFromCommit(commit, project)

    return HttpResponse("OK!")


@csrf_exempt
def github_webhook(request, project_slug, event_type):
    if request.method == "GET":
        return HttpResponse("Not Allowed")
    
    try:
        project = get_object_or_404( Project, slug=project_slug )
    except Project.DoesNotExist:
        return HttpResponseNotFound("Project Not Found")

    logger.debug("Received payload: %s " % request.body)
    payload = json.loads(request.body)
    
    try:
        if event_type in ["pull_request", "pull_request_review_comment"]:
            _handle_pull_request_webhook(request, project, payload)

        if event_type == "issues":
            handle_issues_webhook.apply_async(args=[project.slug, payload], countdown=5)
        
        if event_type == "issue_comment":
            _handle_issue_comment_webhook(request, project, payload)
        
        if event_type == "push":
            _handle_push_webhook(request, project, payload)
    except:
        logger.error(payload)
        traceback.print_exc(file=sys.stdout)
        rollbar.init(settings.ROLLBAR['access_token'], environment=settings.ROLLBAR['environment'])
        rollbar.report_exc_info(sys.exc_info(), None, {'task': 'github_webhook'}, {'level': 'error'})


    return HttpResponse("OK!")

 
@login_required
def github_log(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    admin_access_or_403(project, request.user )
    log = GithubLog.objects.filter(project=project).order_by("-date")

    paginator = Paginator(log, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        log = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        log = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        log = paginator.page(paginator.num_pages)

    return render_to_response("github_integration/log.html", { "project":project, "log":log }, context_instance=RequestContext(request))


def _handleClientError(request, error, project):
    try:
        cred = GithubCredentials.objects.get(project=project)
        cred.failure_count += 1
        cred.save()
        log = GithubLog(project=project, message="Client error while attempting to access GitHub.  %s" % error)
        log.save()
    except:
        logger.warn("Could not log error")
    auth_url = "%s?client_id=%s&scope=repo,read:org,write:repo_hook,user,repo:status&redirect_uri=%s/github/auth_callback/%s" % (settings.GITHUB_AUTH_URL, settings.GITHUB_CLIENT_ID, settings.SSL_BASE_URL, project.slug)
    return render_to_response("github_integration/api_failure.html", {"project":project, "auth_url":auth_url, "error":error }, context_instance=RequestContext(request))



def _redeemOauthCode(code):
    url = "%s?client_id=%s&client_secret=%s&code=%s" % (settings.GITHUB_TOKEN_URL,
                                                        settings.GITHUB_CLIENT_ID,
                                                        settings.GITHUB_SECRET, code)
    req = urllib2.Request(url)
    req.get_method = lambda: 'POST'
    result = urllib2.urlopen(req).read()
    return parse_qs(result)

@login_required
def org_auth_callback(request, organization_slug):
    organization = Organization.objects.get(slug=organization_slug)
    if not organization.hasStaffAccess(request.user):
        raise PermissionDenied('Only staff members can set this up')
    try:
        code = _redeemOauthCode(request.GET.get("code"))
        access_token = code['access_token'][0]
        api = slumber.API("https://api.github.com", append_slash=False)
        user_info = api.user.get(access_token=access_token)
        gho, created = GithubOrganization.objects.get_or_create(organization=organization)
        gho.github_username = user_info['login']
        gho.oauth_token = access_token
        gho.save()
    except:
        return HttpResponseRedirect("%s#/github" % reverse('organization_extras', kwargs={'organization_slug': organization_slug}))

    return HttpResponseRedirect("%s#/github" % reverse('organization_extras', kwargs={'organization_slug': organization_slug}))




@login_required
def auth_callback(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    admin_access_or_403(project, request.user )
    
    try:
        code = request.GET.get("code")
        o = _redeemOauthCode(code)
        access_token = o['access_token'][0]
        api = slumber.API("https://api.github.com", append_slash=False)
        user_info = api.user.get(access_token=access_token)

        if "name" in user_info:
            github_name = user_info['name']
        else:
            github_name = user_info['login']
            
        github_username = user_info['login']
        
        # let's cheat and grab the person's full name if github knows it and we don't!
        if request.user.first_name == '' and request.user.last_name == '':
            try:
                names = github_name.split(" ")
                if len(names) == 2:
                    request.user.first_name = names[0]
                    request.user.last_name = names[1]
                    request.user.save()
            except:
                logger.debug("Could not snag users' name")
        
        try:
            c = GithubCredentials.objects.get(project=project)
            c.oauth_token = access_token
            c.github_username = github_username
            c.save()
        except GithubCredentials.DoesNotExist:
            c = GithubCredentials(project=project, user=request.user, oauth_token=access_token, failure_count=0, github_username=github_username)
            c.save()
        ProjectExtraMapping.objects.get_or_create(project=project, extra_slug='github')


    except:
        traceback.print_exc(file=sys.stdout)
        #request.user.message_set.create(message='Something went wrong with the authentication.')
        messages.add_message(request, messages.INFO, 'Something went wrong with the authentication.')
        
    return HttpResponseRedirect( "%s#/settings/extras/github" % reverse('project_app', kwargs={'project_slug':project_slug}) )


def onStoryDeleted(sender, **kwargs):    
    try:
        story = kwargs["story"]
        project = story.project
        link = ExternalStoryMapping.objects.get(story=story, extra_slug="github")
        if link is None:
            # logging.debug("Story not associated with external story, aborting.")
            return
        
        for binding in GithubBinding.objects.filter(github_slug=link.external_extra, project=project):
            token = GithubCredentials.objects.get(project=project)

            if not binding.delete_issues:
                continue  # Not configured to delete stories.
    
            api = slumber.API("https://api.github.com",append_slash=False)           
            api.repos(binding.github_slug).issues(link.external_id).comments.post({'body':'Story deleted from ScrumDo'}, access_token=token.oauth_token)
            api.repos(binding.github_slug).issues(link.external_id).post({'state':'closed'}, access_token=token.oauth_token)
    except HttpClientError as e:
        gh_log(project, "Could not update deleted story %s" % e, increment_count=True)
    except:
        logger.warn("Could not close github issue for deleted story")


project_signals.story_deleted.connect(onStoryDeleted, dispatch_uid="github_extra_signal_hookup")

def github_login_callback(request):
    try:
        
        code = request.GET.get("code")
        url = "%s?client_id=%s&client_secret=%s&code=%s" % (settings.GITHUB_TOKEN_URL, settings.GITHUB_CLIENT_ID, settings.GITHUB_SECRET, code)
        req = urllib2.Request(url)
        req.get_method = lambda: 'POST'
        result = urllib2.urlopen(req).read()
        logger.debug(result)
        o = parse_qs(result)
        access_token = o['access_token'][0]    
        user = authenticate(access_token=access_token)
        login(request, user)
        logger.debug(request.session)
        if 'success_url' in request.session:
            result = HttpResponseRedirect(request.session['success_url'])
            del request.session['success_url'] 
            return result
        return HttpResponseRedirect("/")
    except:
        return render_to_response("github_integration/auth_failure.html", context_instance=RequestContext(request))

    
def github_login(request):
    auth_url = "%s?client_id=%s&scope=repo,read:org,write:repo_hook,user,repo:status&redirect_uri=%s/github/login_callback" % (settings.GITHUB_AUTH_URL, settings.GITHUB_CLIENT_ID, settings.SSL_BASE_URL)
    return HttpResponseRedirect(auth_url)



@login_required
def github_login_associate_callback(request):
    try:

        code = request.GET.get("code")
        url = "%s?client_id=%s&client_secret=%s&code=%s" % (settings.GITHUB_TOKEN_URL, settings.GITHUB_CLIENT_ID, settings.GITHUB_SECRET, code)
        req = urllib2.Request(url)
        req.get_method = lambda: 'POST'
        result = urllib2.urlopen(req).read()
        logger.debug(result)
        o = parse_qs(result)
        access_token = o['access_token'][0]

        api = slumber.API("https://api.github.com", append_slash=False)
        user_info = api.user.get(access_token=access_token)
        github_username = user_info['login']

        try:
            GithubUser.objects.get(user=request.user)
            return render_to_response("github_integration/auth_dupe.html", context_instance=RequestContext(request))
        except GithubUser.DoesNotExist:
            try:
                GithubUser.objects.get(github_username=github_username)
                return render_to_response("github_integration/auth_dupe.html", context_instance=RequestContext(request))
            except GithubUser.DoesNotExist:
                user = GithubUser(user=request.user, oauth_token=access_token, github_username=github_username)
                user.save()


        return HttpResponseRedirect("/account/#/github")
    except:
        return render_to_response("github_integration/auth_failure.html", context_instance=RequestContext(request))


