# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('email_notifications', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='storymentions',
            name='story',
            field=models.ForeignKey(to='projects.Story'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='storymentions',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailoptions',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailnotificationqueue',
            name='epic',
            field=models.ForeignKey(to='projects.Epic', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailnotificationqueue',
            name='iteration',
            field=models.ForeignKey(to='projects.Iteration', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailnotificationqueue',
            name='originator',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailnotificationqueue',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailnotificationqueue',
            name='story',
            field=models.ForeignKey(to='projects.Story', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailnotificationqueue',
            name='task',
            field=models.ForeignKey(to='projects.Task', null=True),
            preserve_default=True,
        ),
    ]
