# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('favorites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='epic',
            field=models.ForeignKey(blank=True, to='projects.Epic', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='favorite',
            name='iteration',
            field=models.ForeignKey(blank=True, to='projects.Iteration', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='favorite',
            name='project',
            field=models.ForeignKey(blank=True, to='projects.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='favorite',
            name='story',
            field=models.ForeignKey(blank=True, to='projects.Story', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
