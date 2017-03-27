# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.


from django.db import models


from django.contrib.auth.models import User
from apps.projects.models import Project
import logging

logger = logging.getLogger(__name__)

# Used for User <-> Github mappings
class GithubUser(models.Model):
    user = models.OneToOneField(User, related_name="github_user")
    github_username = models.CharField(max_length=64, default="")
    oauth_token = models.CharField(max_length=64)


class GithubOrganization(models.Model):
    """Mapping of scrumdo<->github organizations when using the organization level extra
       to keep authentication info in sync."""
    organization = models.ForeignKey("organizations.Organization")
    github_username = models.CharField(max_length=64, default="")
    github_organization_name = models.CharField(max_length=128, default="")
    oauth_token = models.CharField(max_length=64)


class GithubTeam(models.Model):
    team = models.ForeignKey("organizations.Team")
    github_team_id = models.IntegerField()
    github_organization_name = models.CharField(max_length=128, default="")
    last_sync = models.DateTimeField(null=True)


# Used for Project <-> Gitub mappings
class GithubCredentials(models.Model):
    user = models.ForeignKey(User, related_name="github_credentials")
    project = models.ForeignKey(Project)
    oauth_token = models.CharField(max_length=64)
    failure_count = models.IntegerField(default=0)
    github_username = models.CharField(max_length=48)
    class Meta:
        db_table = "v2_github_integration_githubcredentials"


class GithubBinding(models.Model):
    project = models.ForeignKey(Project)
    github_slug = models.CharField(max_length=64, help_text="You must have GitHub admin privileges to connect to a repo.",verbose_name="GitHub Repo")
    upload_issues = models.BooleanField(default=False, help_text="Upload ScrumDo stories as GitHub issues. (Careful, this will upload all existing stories.)")
    download_issues = models.BooleanField(default=True, help_text="Download GitHub issues into the ScrumDo story queue.")
    delete_issues = models.BooleanField(default=False, help_text="Should ScrumDo close an associated GitHub issue when a story is deleted?")
    log_commit_messages = models.BooleanField(default=True, help_text="Do you want GitHub commit messages in your scrum log?")
    commit_status_updates = models.BooleanField(default=True, help_text="Allow users to update story status via commit messages.")
    class Meta:
        db_table = "v2_github_integration_githubbinding"


class GithubLog(models.Model):
    project = models.ForeignKey( Project )
    date = models.DateTimeField( auto_now=True )
    message = models.TextField()
    class Meta:
        db_table = "v2_github_integration_githublog"

    
