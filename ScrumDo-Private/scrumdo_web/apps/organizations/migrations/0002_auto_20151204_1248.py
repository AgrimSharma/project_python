# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='projects',
            field=models.ManyToManyField(related_name='teams', db_table=b'v2_organizations_team_projects', verbose_name='projects', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organizationvelocitylog',
            name='organization',
            field=models.ForeignKey(related_name='velocity_log', to='organizations.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organization',
            name='creator',
            field=models.ForeignKey(related_name='organizations_created', verbose_name='creator', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
