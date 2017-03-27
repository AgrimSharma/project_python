import logging
import datetime

from models import *
from apps.projects.models import Project
from apps.organizations.models import Organization, Team
from utils import update_issue, gh_log
import sys,traceback
import rollbar

from apps.scrumdocelery import app

import slumber

import logging

logger = logging.getLogger(__name__)


@app.task
def syncronize_teams(organization_slug):
    organization = Organization.objects.get(slug=organization_slug)
    gho = GithubOrganization.objects.get(organization=organization)
    for team in GithubTeam.objects.filter(team__organization=organization):
        _syncronize_github_team(organization, team, gho)
        team.last_sync = datetime.datetime.now()
        team.save()

def _get_unique_username(username):
    testusername = username
    try:
        User.objects.get(username__iexact=testusername)
        c = 1
        while True:
            testusername ="%s.%d" % (username, c)
            User.objects.get(username__iexact=testusername)
            c+=1
    except User.DoesNotExist:
        return testusername


def _syncronize_github_team(organization, team, gho):
    api = slumber.API("https://api.github.com", append_slash=False)
    github_members = api.teams(team.github_team_id).members.get(access_token=gho.oauth_token)
    scrumdo_team = team.team
    # Add missing members...
    for github_member in github_members:
        username = github_member['login']
        scrumdo_username = username
        usertype = github_member['type']
        if usertype != 'User':
            continue
        try:
            existing = GithubUser.objects.get(github_username=username)
            if not scrumdo_team.members.filter(id=existing.user_id).exists():
                scrumdo_team.members.add(existing.user)  # Only add the user if they're not already in there

        except GithubUser.DoesNotExist:  # User does not exist, create a new one and add it
            scrumdo_username = _get_unique_username(username)
            new_user = User.objects.create_user(scrumdo_username)
            ghuser = GithubUser(user=new_user, github_username=username, oauth_token="+")
            ghuser.save()
            scrumdo_team.members.add(new_user)
    # Remove extra/removed members...
    memberlist = [member['login'] for member in github_members]
    for member in scrumdo_team.members.all():
        try:
            ghuser = GithubUser.objects.get(user=member)
            if ghuser.github_username not in memberlist:
                scrumdo_team.members.remove(ghuser.user)
        except GithubUser.DoesNotExist:
            pass # a manually added user?





@app.task
def handle_issues_webhook(project_slug, payload):
    # We're getting a race condition occasionally if GitHub make's it's callback while we're still processing
    # a new-story request.  Adding a delay in here should help to fix that.  We commit early here so we don't have
    # a stale view of the data.  A better solution might be to come up with a memcache based locking system, but
    # this should be good enough.
    try:
        # raise Exception("test")
        project = Project.objects.get(slug=project_slug)
        logger.info("Processing github webook.")

        repo_url = payload['repository']['url']
        project_slug = repo_url[29:]  # https://api.github.com/repos/marc-hughes/Sandbox
        if 'issue' not in payload:
            # Happens when we first set up the webhook as a ping-test.
            return
        issue = payload['issue']
        for binding in GithubBinding.objects.filter(github_slug=project_slug, project=project):
            if (payload['action'] == 'unlabeled') or (payload['action'] == 'labeled') or (payload['action'] == 'opened') or (payload['action'] == 'closed') or (payload['action']=='reopened'):
                logger.debug("Received callback from GitHub to update issue %d" % issue['number'] )
                gh_log(project, "Received callback from GitHub to update issue %d" % issue['number'] )
                update_issue(issue, project, binding.github_slug, True, binding)
            else:
                gh_log(project, "Didn't know what to do with github callback %s" % payload )
                logger.warn("Didn't know what to do with github callback %s" % payload)
    except:
        traceback.print_exc(file=sys.stdout)
        logger.error(payload)
        rollbar.report_exc_info(sys.exc_info(), None, {'task': 'handle_issues_webhook'}, {'level': 'error'})
