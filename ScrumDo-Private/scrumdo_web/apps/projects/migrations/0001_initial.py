# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import apps.projects.models.project
import django.db.models.deletion
from django.conf import settings
import django.core.validators
import apps.projects.models.filejob


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_type', models.SmallIntegerField(default=0, choices=[(0, b'Scrum'), (1, b'Scrumban'), (2, b'Portfolio Planning')])),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('name', models.CharField(max_length=80, verbose_name='name')),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='created')),
                ('description', models.TextField(default=b'', null=True, verbose_name='description', blank=True)),
                ('personal', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('private', models.BooleanField(default=True, verbose_name='private')),
                ('use_assignee', models.BooleanField(default=True)),
                ('use_tasks', models.BooleanField(default=True)),
                ('use_extra_1', models.BooleanField(default=False)),
                ('use_extra_2', models.BooleanField(default=False)),
                ('use_extra_3', models.BooleanField(default=False)),
                ('extra_1_label', models.CharField(max_length=25, null=True, blank=True)),
                ('extra_2_label', models.CharField(max_length=25, null=True, blank=True)),
                ('extra_3_label', models.CharField(max_length=25, null=True, blank=True)),
                ('status_names', models.CharField(default=b'Todo                          Doing                         Reviewing                     Done      ', max_length=100)),
                ('task_status_names', models.CharField(default=b'Todo                          Doing                                                       Done      ', max_length=100)),
                ('card_types', models.CharField(default=b'User Story          Feature                                           Bug                           ', max_length=100)),
                ('velocity_type', models.PositiveIntegerField(default=1)),
                ('point_scale_type', models.PositiveIntegerField(default=0)),
                ('velocity', models.PositiveIntegerField(null=True, blank=True)),
                ('velocity_iteration_span', models.PositiveIntegerField(null=True, blank=True)),
                ('iterations_left', models.PositiveIntegerField(null=True, blank=True)),
                ('category', models.CharField(default=b'', max_length=25, null=True, blank=True)),
                ('categories', models.CharField(max_length=1024, null=True, blank=True)),
                ('token', models.CharField(default=apps.projects.models.project._default_token, max_length=7)),
                ('burnup_reset', models.IntegerField(default=0)),
                ('burnup_reset_date', models.DateField(default=None, null=True, blank=True)),
                ('has_iterations_hidden', models.BooleanField(default=False)),
                ('abandoned', models.BooleanField(default=False)),
                ('live_updates', models.BooleanField(default=False)),
                ('story_minutes', models.IntegerField(default=0)),
                ('render_mode', models.IntegerField(default=0)),
                ('creator', models.ForeignKey(related_name='projects_created', verbose_name='creator', to=settings.AUTH_USER_MODEL)),
                ('default_cell', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='kanban.BoardCell', null=True)),
                ('organization', models.ForeignKey(related_name='projects', blank=True, to='organizations.Organization', null=True)),
                ('release_project', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='projects.Project', null=True)),
            ],
            options={
                'ordering': ['-active', 'name'],
                'db_table': 'v2_projects_project',
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='Iteration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'name')),
                ('detail', models.TextField(verbose_name=b'detail', blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('default_iteration', models.BooleanField(default=False)),
                ('locked', models.BooleanField(default=False)),
                ('iteration_type', models.SmallIntegerField(default=1)),
                ('include_in_velocity', models.BooleanField(default=True, verbose_name=b'include_in_velocity')),
                ('hidden', models.BooleanField(default=False)),
                ('project', models.ForeignKey(related_name='iterations', to='projects.Project')),

            ],
            options={
                'db_table': 'v2_projects_iteration',
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='Epic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('local_id', models.IntegerField()),
                ('summary', models.TextField()),
                ('detail', models.TextField(blank=True)),
                ('points', models.CharField(default=b'?', help_text=b'Rough size of this epic (including size of sub-epics or stories).  Enter ? to specify no sizing.', max_length=4, verbose_name=b'points', blank=True)),
                ('order', models.IntegerField(default=5000, max_length=5)),
                ('archived', models.BooleanField(default=False, help_text=b"Archived epics are generally hidden and their points don't count towards the project.")),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Initial'), (1, b'Stories Written'), (2, b'Blocked'), (3, b'Completed')])),
                ('cards_total', models.IntegerField(default=0)),
                ('cards_completed', models.IntegerField(default=0)),
                ('cards_in_progress', models.IntegerField(default=0)),
                ('points_total', models.IntegerField(default=0)),
                ('points_completed', models.IntegerField(default=0)),
                ('points_in_progress', models.IntegerField(default=0)),
                ('parent', models.ForeignKey(related_name='children', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Parent Epic', to='projects.Epic', help_text=b'What epic does this one belong within?', null=True)),
                ('project', models.ForeignKey(related_name='epics', to='projects.Project')),

            ],
            options={
                'ordering': ['order'],
                'db_table': 'v2_projects_epic',
            },
            bases=(models.Model,),
        ),

            migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('business_value', models.PositiveIntegerField(default=0)),
                ('rank', models.IntegerField(default=500000)),
                ('epic_rank', models.IntegerField(default=500000)),
                ('release_rank', models.IntegerField(default=500000)),
                ('summary', models.TextField()),
                ('local_id', models.IntegerField()),
                ('detail', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('points', models.CharField(default=b'?', max_length=3, verbose_name=b'points', blank=True)),
                ('status', models.IntegerField(default=1, max_length=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('card_type', models.IntegerField(default=1, max_length=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('category', models.CharField(max_length=25, null=True, blank=True)),
                ('extra_1', models.TextField(null=True, blank=True)),
                ('extra_2', models.TextField(null=True, blank=True)),
                ('extra_3', models.TextField(null=True, blank=True)),
                ('task_counts', models.CommaSeparatedIntegerField(default=b'0,0,0,0,0,0,0,0,0,0', max_length=44)),
                ('comment_count', models.IntegerField(default=0)),
                ('has_external_links', models.BooleanField(default=False)),
                ('has_attachment', models.BooleanField(default=False)),
                ('has_commits', models.BooleanField(default=False)),
                ('tags_cache', models.CharField(default=None, max_length=512, null=True, blank=True)),
                ('epic_label', models.CharField(default=None, max_length=32, null=True, blank=True)),
                ('assignees_cache', models.CharField(default=None, max_length=512, null=True, blank=True)),
                ('estimated_minutes', models.IntegerField(default=0)),
                ('task_minutes', models.IntegerField(default=0)),
                ('due_date', models.DateTimeField(null=True, blank=True)),
                ('assignee', models.ManyToManyField(related_name='assigned_stories', to=settings.AUTH_USER_MODEL, db_table=b'v2_projects_story_assignee_m2m', blank=True, null=True, verbose_name='assignees')),
                ('cell', models.ForeignKey(related_name='stories', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='kanban.BoardCell', null=True)),
                ('creator', models.ForeignKey(related_name='created_stories', verbose_name='creator', to=settings.AUTH_USER_MODEL)),
                ('epic', models.ForeignKey(related_name='stories', blank=True, to='projects.Epic', null=True)),
                ('iteration', models.ForeignKey(related_name='stories', to='projects.Iteration')),
                ('project', models.ForeignKey(related_name='stories', to='projects.Project')),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='projects.Story', null=True)),
            ],
            options={
                'db_table': 'v2_projects_story',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BoardAttributes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('context', models.CharField(max_length=6)),
                ('key', models.CharField(max_length=4)),
                ('value', models.TextField()),
                ('project', models.ForeignKey(related_name='extra_attributes', to='projects.Project')),
            ],
            options={
                'db_table': 'v2_projects_boardattributes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(default=b'', max_length=24)),
                ('full_text', models.TextField()),
                ('link', models.CharField(max_length=200)),
                ('story', models.ForeignKey(related_name='commits', to='projects.Story')),
            ],
            options={
                'db_table': 'v2_projects_commit',
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='ExtraUserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=128, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FileJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment_file', models.FileField(upload_to=apps.projects.models.filejob.attachment_upload, null=True, verbose_name=b'attachment')),
                ('file_type', models.CharField(max_length=100)),
                ('request_date', models.DateField(auto_now=True)),
                ('completed', models.BooleanField(default=False)),
                ('organization', models.ForeignKey(related_name='generatedFiles', to='organizations.Organization')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name=b'name')),
                ('color', models.IntegerField()),
                ('mapped_category', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('mapped_card_type', models.IntegerField(default=None, null=True)),
                ('stories', models.ManyToManyField(related_name='labels', db_table=b'v2_projects_label_stories', to='projects.Story')),
                ('project', models.ForeignKey(related_name='labels', to='projects.Project')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'v2_projects_labels',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MilestoneAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('assigned_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Assigned'), (1, b'Scoped'), (2, b'Sized'), (3, b'Developing'), (4, b'Verification'), (5, b'Completed')])),
                ('cards_total', models.IntegerField(default=0)),
                ('cards_completed', models.IntegerField(default=0)),
                ('cards_in_progress', models.IntegerField(default=0)),
                ('points_total', models.IntegerField(default=0)),
                ('points_completed', models.IntegerField(default=0)),
                ('points_in_progress', models.IntegerField(default=0)),
                ('milestone', models.ForeignKey(to='projects.Story')),
                ('assigned_project', models.ForeignKey(to='projects.Project')),

            ],
            options={
                'db_table': 'v2_projects_milestone_assignment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OfflineJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_date', models.DateField(auto_now=True)),
                ('completed', models.BooleanField(default=False)),
                ('job_type', models.CharField(max_length=32)),
                ('result', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('organization', models.ForeignKey(related_name='offlineJobs', to='organizations.Organization')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'v2_projects_offline_job',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PointsLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('points_status1', models.IntegerField(default=0)),
                ('points_status2', models.IntegerField(default=0)),
                ('points_status3', models.IntegerField(default=0)),
                ('points_status4', models.IntegerField(default=0)),
                ('points_status5', models.IntegerField(default=0)),
                ('points_status6', models.IntegerField(default=0)),
                ('points_status7', models.IntegerField(default=0)),
                ('points_status8', models.IntegerField(default=0)),
                ('points_status9', models.IntegerField(default=0)),
                ('points_status10', models.IntegerField(default=0)),
                ('time_estimated', models.IntegerField(default=0)),
                ('time_estimated_completed', models.IntegerField(default=0)),
                ('points_total', models.IntegerField()),
                ('iteration', models.ForeignKey(related_name='points_log', to='projects.Iteration', null=True)),
                ('project', models.ForeignKey(related_name='points_log', to='projects.Project', null=True)),
            ],
            options={
                'ordering': ['date'],
                'db_table': 'v2_projects_pointslog',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PortfolioStoryMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('story', models.ForeignKey(related_name='portfolio_mappings', to='projects.Story')),
                ('target_project', models.ForeignKey(related_name='portfolio_mappings', to='projects.Project')),
                ('target_epic', models.ForeignKey(to='projects.Epic')),
            ],
            options={
                'db_table': 'v2_projects_portfoliostorymapping',
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='ProjectShare',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=False)),
                ('all_cards', models.BooleanField(default=False)),
                ('tag', models.CharField(default=b'public', max_length=b'64')),
                ('key', models.CharField(max_length=16)),
                ('iteration', models.ForeignKey(to='projects.Iteration')),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
            options={
                'db_table': 'v2_projects_project_share',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PullRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.IntegerField(default=0, choices=[(0, b'Open'), (1, b'Closed')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(default=b'', max_length=64)),
                ('full_text', models.TextField()),
                ('link', models.CharField(max_length=200)),
                ('stories', models.ManyToManyField(related_name='pull_requests', to='projects.Story')),

            ],
            options={
                'db_table': 'v2_projects_pull_request',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('start_date', models.DateField(help_text=b'Date that work on this release is planned to start.')),
                ('delivery_date', models.DateField(help_text=b'Date that this release is expected to be delivered/completed.')),
                ('shared', models.BooleanField(default=False, help_text=b'Should a public page about this release be created?')),
                ('key', models.CharField(max_length=32)),
                ('calculating', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=1)),
                ('epics', models.ManyToManyField(related_name='releases', to='projects.Epic')),
                ('organization', models.ForeignKey(related_name='releases', to='organizations.Organization')),
                ('projects', models.ManyToManyField(related_name='releases', to='projects.Project')),
                ('stories', models.ManyToManyField(related_name='releases', to='projects.Story')),

            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('points_status1', models.IntegerField(default=0)),
                ('points_status2', models.IntegerField(default=0)),
                ('points_status3', models.IntegerField(default=0)),
                ('points_status4', models.IntegerField(default=0)),
                ('points_status5', models.IntegerField(default=0)),
                ('points_status6', models.IntegerField(default=0)),
                ('points_status7', models.IntegerField(default=0)),
                ('points_status8', models.IntegerField(default=0)),
                ('points_status9', models.IntegerField(default=0)),
                ('points_status10', models.IntegerField(default=0)),
                ('stories_status1', models.IntegerField(default=0)),
                ('stories_status2', models.IntegerField(default=0)),
                ('stories_status3', models.IntegerField(default=0)),
                ('stories_status4', models.IntegerField(default=0)),
                ('stories_status5', models.IntegerField(default=0)),
                ('stories_status6', models.IntegerField(default=0)),
                ('stories_status7', models.IntegerField(default=0)),
                ('stories_status8', models.IntegerField(default=0)),
                ('stories_status9', models.IntegerField(default=0)),
                ('stories_status10', models.IntegerField(default=0)),
                ('points_total', models.IntegerField()),
                ('story_count', models.IntegerField()),
                ('total_time_spent', models.IntegerField()),
                ('time_estimated', models.IntegerField(default=0)),
                ('time_estimated_completed', models.IntegerField(default=0)),
                ('release', models.ForeignKey(related_name='points_log', to='projects.Release')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('cards_total', models.IntegerField(default=0)),
                ('cards_completed', models.IntegerField(default=0)),
                ('cards_in_progress', models.IntegerField(default=0)),
                ('points_total', models.IntegerField(default=0)),
                ('points_completed', models.IntegerField(default=0)),
                ('points_in_progress', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'v2_projects_releasestat',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SavedQuery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('query', models.CharField(max_length=255)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_count', models.IntegerField()),
                ('project_count', models.IntegerField()),
                ('story_count', models.IntegerField()),
                ('date', models.DateField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='StoryAttributes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('context', models.CharField(max_length=6)),
                ('key', models.CharField(max_length=4)),
                ('value', models.CharField(max_length=10)),
                ('story', models.ForeignKey(related_name='extra_attributes', to='projects.Story')),
            ],
            options={
                'db_table': 'v2_projects_storyattributes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_submitted', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('story', models.ForeignKey(related_name='comments', to='projects.Story')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-date_submitted'],
                'db_table': 'v2_projects_story_comment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name=b'name')),
                ('project', models.ForeignKey(related_name='tags', to='projects.Project')),
            ],
            options={
                'db_table': 'v2_projects_storytag',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryTagging',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('story', models.ForeignKey(related_name='story_tags', to='projects.Story')),
                ('tag', models.ForeignKey(related_name='stories', to='projects.StoryTag')),
            ],
            options={
                'db_table': 'v2_projects_storytagging',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('summary', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('tags_cache', models.CharField(default=None, max_length=512, null=True, blank=True)),
                ('estimated_minutes', models.IntegerField(default=0)),
                ('status', models.IntegerField(default=1, max_length=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('modified', models.DateTimeField(auto_now=True, verbose_name=b'modified')),
                ('assignee', models.ForeignKey(related_name='assigned_tasks', verbose_name=b'assignee', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('story', models.ForeignKey(related_name='tasks', to='projects.Story')),
            ],
            options={
                'db_table': 'v2_projects_task',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskTagging',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.ForeignKey(related_name='tasks', to='projects.StoryTag')),
                ('task', models.ForeignKey(related_name='task_tags', to='projects.Task')),
            ],
            options={
                'db_table': 'v2_projects_tasktagging',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimeAllocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('minutes_allocated', models.IntegerField(default=0)),
                ('iteration', models.ForeignKey(to='projects.Iteration', null=True)),
                ('project', models.ForeignKey(to='projects.Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'v2_projects_timeallocation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimeEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('minutes_spent', models.PositiveIntegerField()),
                ('notes', models.TextField()),
                ('date', models.DateField()),
                ('iteration', models.ForeignKey(to='projects.Iteration', null=True)),
                ('organization', models.ForeignKey(to='organizations.Organization')),
                ('project', models.ForeignKey(to='projects.Project', null=True)),
                ('story', models.ForeignKey(related_name='time_entries', on_delete=django.db.models.deletion.SET_NULL, to='projects.Story', null=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='projects.Task', null=True)),
                ('user', models.ForeignKey(related_name='time_entries', verbose_name=b'user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'v2_projects_timeentry',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='releasestat',
            name='release',
            field=models.ForeignKey(related_name='stats', to='projects.Story'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='epic',
            name='release',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='projects.Story', null=True),
            preserve_default=True,
        ),
    ]
