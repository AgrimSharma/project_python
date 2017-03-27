# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectemailsubscription',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectemailsubscription',
            name='user',
            field=models.ForeignKey(related_name='email_subscriptions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='newsitem',
            name='project',
            field=models.ForeignKey(related_name='newsItems', blank=True, to='projects.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='newsitem',
            name='related_story',
            field=models.ForeignKey(blank=True, to='projects.Story', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='newsitem',
            name='user',
            field=models.ForeignKey(related_name='newsItems', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
