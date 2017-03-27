# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GithubBinding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github_slug', models.CharField(help_text=b'You must have GitHub admin privileges to connect to a repo.', max_length=64, verbose_name=b'GitHub Repo')),
                ('upload_issues', models.BooleanField(default=False, help_text=b'Upload ScrumDo stories as GitHub issues. (Careful, this will upload all existing stories.)')),
                ('download_issues', models.BooleanField(default=True, help_text=b'Download GitHub issues into the ScrumDo story queue.')),
                ('delete_issues', models.BooleanField(default=False, help_text=b'Should ScrumDo close an associated GitHub issue when a story is deleted?')),
                ('log_commit_messages', models.BooleanField(default=True, help_text=b'Do you want GitHub commit messages in your scrum log?')),
                ('commit_status_updates', models.BooleanField(default=True, help_text=b'Allow users to update story status via commit messages.')),
            ],
            options={
                'db_table': 'v2_github_integration_githubbinding',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GithubCredentials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oauth_token', models.CharField(max_length=64)),
                ('failure_count', models.IntegerField(default=0)),
                ('github_username', models.CharField(max_length=48)),
            ],
            options={
                'db_table': 'v2_github_integration_githubcredentials',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GithubLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
            ],
            options={
                'db_table': 'v2_github_integration_githublog',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GithubOrganization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github_username', models.CharField(default=b'', max_length=64)),
                ('github_organization_name', models.CharField(default=b'', max_length=128)),
                ('oauth_token', models.CharField(max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GithubTeam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github_team_id', models.IntegerField()),
                ('github_organization_name', models.CharField(default=b'', max_length=128)),
                ('last_sync', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GithubUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github_username', models.CharField(default=b'', max_length=64)),
                ('oauth_token', models.CharField(max_length=64)),
                ('user', models.OneToOneField(related_name='github_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
