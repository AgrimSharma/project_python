# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlackMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('channel_name', models.CharField(max_length=128)),
                ('channel_id', models.CharField(max_length=16)),
                ('errors', models.IntegerField(default=0)),
                ('card_moved', models.BooleanField(default=True)),
                ('card_created', models.BooleanField(default=True)),
                ('card_modified', models.BooleanField(default=True)),
                ('comment_created', models.BooleanField(default=True)),
                ('task_moved', models.BooleanField(default=True)),
                ('task_created', models.BooleanField(default=True)),
                ('task_modified', models.BooleanField(default=True)),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SlackUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slack_username', models.CharField(default=b'', max_length=64)),
                ('oauth_token', models.CharField(max_length=64)),
                ('project', models.ForeignKey(to='projects.Project')),
                ('user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
