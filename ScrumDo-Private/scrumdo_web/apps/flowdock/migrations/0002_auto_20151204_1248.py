# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
        ('flowdock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='flowdockuser',
            name='project',
            field=models.ForeignKey(related_name='+', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flowdockuser',
            name='user',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flowdockmapping',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
            preserve_default=True,
        ),
    ]
