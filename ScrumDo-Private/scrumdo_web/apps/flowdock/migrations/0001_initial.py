# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlowdockMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flow_slug', models.CharField(max_length=128)),
                ('org_slug', models.CharField(max_length=128)),
                ('source_id', models.IntegerField(default=0)),
                ('channel_name', models.CharField(max_length=128)),
                ('channel_id', models.CharField(max_length=128)),
                ('errors', models.IntegerField(default=0)),
                ('api_token', models.CharField(max_length=128)),
                ('card_moved', models.BooleanField(default=True)),
                ('card_created', models.BooleanField(default=True)),
                ('card_modified', models.BooleanField(default=True)),
                ('comment_created', models.BooleanField(default=True)),
                ('task_moved', models.BooleanField(default=True)),
                ('task_created', models.BooleanField(default=True)),
                ('task_modified', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FlowdockUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flowdock_username', models.CharField(default=b'', max_length=64)),
                ('oauth_token', models.CharField(max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
