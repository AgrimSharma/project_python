# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalStoryMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('external_id', models.CharField(max_length=40)),
                ('external_url', models.CharField(max_length=256, null=True, blank=True)),
                ('extra_slug', models.CharField(max_length=20)),
                ('external_extra', models.CharField(max_length=512, null=True, blank=True)),
            ],
            options={
                'db_table': 'v2_extras_externalstorymapping',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExternalTaskMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('external_id', models.CharField(max_length=40)),
                ('external_url', models.CharField(max_length=256, null=True, blank=True)),
                ('extra_slug', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'v2_extras_externaltaskmapping',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectExtraMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extra_slug', models.CharField(max_length=25, verbose_name=b'extra_slug')),
            ],
            options={
                'db_table': 'v2_extras_projectextramapping',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extra_slug', models.CharField(max_length=25, verbose_name=b'extra_slug')),
                ('external_id', models.CharField(max_length=40)),
                ('external_url', models.CharField(max_length=256, null=True, blank=True)),
                ('imported_on', models.DateTimeField(default=datetime.datetime.now)),
                ('modified', models.DateTimeField(default=datetime.datetime.now)),
                ('summary', models.TextField()),
                ('detail', models.TextField(blank=True)),
                ('points', models.CharField(default=b'?', max_length=3, verbose_name=b'points', blank=True)),
                ('status', models.IntegerField(default=1, max_length=2)),
                ('extra_1', models.TextField(null=True, blank=True)),
                ('extra_2', models.TextField(null=True, blank=True)),
                ('extra_3', models.TextField(null=True, blank=True)),
                ('external_extra', models.CharField(max_length=512, null=True, blank=True)),
                ('archived', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'v2_extras_storyqueue',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SyncronizationQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extra_slug', models.CharField(max_length=25)),
                ('action', models.IntegerField(max_length=2, choices=[(1, b'SYNC_REMOTE'), (2, b'STORY_UPDATED'), (3, b'STORY_DELETED'), (4, b'STORY_CREATED'), (5, b'INITIAL_SYNC'), (6, b'ACTION_STORY_STATUS_CHANGED'), (7, b'ACTION_TASK_UPDATED'), (8, b'ACTION_TASK_DELETED'), (9, b'ACTION_TASK_CREATED'), (10, b'ACTION_TASK_STATUS_CHANGED'), (11, b'ACTION_STORY_IMPORTED')])),
                ('queue_date', models.DateTimeField(default=datetime.datetime.now)),
                ('external_id', models.CharField(max_length=40, null=True)),
            ],
            options={
                'db_table': 'v2_extras_syncronizationqueue',
            },
            bases=(models.Model,),
        ),
    ]
