# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='created')),
                ('text', models.TextField()),
                ('icon', models.CharField(max_length=24)),
                ('feed_url', models.CharField(max_length=75, null=True, blank=True)),
            ],
            options={
                'ordering': ['-created'],
                'db_table': 'v2_activities_newsitem',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectEmailSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
