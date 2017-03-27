# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HipChatMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('token', models.CharField(max_length=128)),
                ('url', models.CharField(max_length=256)),
                ('errors', models.IntegerField(default=0)),
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
    ]
