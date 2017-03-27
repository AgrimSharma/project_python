# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.realtime.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
                ('message_type', models.PositiveSmallIntegerField(default=0)),
                ('attachment_file', models.FileField(upload_to=apps.realtime.models.attachment_upload, null=True, verbose_name=b'attachment')),
                ('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
            options={
                'db_table': 'v2_realtime_chatmessage',
            },
            bases=(models.Model,),
        ),
    ]
