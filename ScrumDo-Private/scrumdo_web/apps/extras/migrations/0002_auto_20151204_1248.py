# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0001_initial'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncronizationqueue',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='syncronizationqueue',
            name='story',
            field=models.ForeignKey(related_name='sync_queue', to='projects.Story', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='syncronizationqueue',
            name='task',
            field=models.ForeignKey(related_name='sync_queue', to='projects.Task', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='storyqueue',
            name='project',
            field=models.ForeignKey(related_name='story_queue', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectextramapping',
            name='project',
            field=models.ForeignKey(related_name='extras', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='externaltaskmapping',
            name='task',
            field=models.ForeignKey(related_name='external_links', to='projects.Task'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='externalstorymapping',
            name='story',
            field=models.ForeignKey(related_name='external_links', to='projects.Story'),
            preserve_default=True,
        ),
    ]
