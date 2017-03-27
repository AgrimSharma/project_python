# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=65)),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='created')),
                ('description', models.TextField(default=b'', null=True, verbose_name='description', blank=True)),
                ('source', models.CharField(default=b'', max_length=100, blank=True)),
                ('bill_to', models.TextField(default=b'', help_text=b'Bill To address to put on invoices.', null=True, blank=True)),
                ('timezone', models.CharField(default=b'US/Eastern', max_length=32)),
                ('end_of_week', models.PositiveSmallIntegerField(default=6, choices=[(0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday'), (6, b'Sunday')])),
                ('allow_personal', models.BooleanField(default=True, help_text=b'Allow users to create personal projects.')),
                ('active', models.BooleanField(default=True)),
                ('planning_mode', models.CharField(default=b'unset', max_length=10, choices=[(b'unset', b'unset'), (b'release', b'release'), (b'portfolio', b'portfolio')])),
                ('classic_mode', models.SmallIntegerField(default=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationVelocityLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='created')),
                ('velocity', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assignable', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=65)),
                ('access_type', models.CharField(default=b'read', max_length=25, choices=[(b'read', b'Read Only'), (b'write', b'Read / Write'), (b'admin', b'Administrator'), (b'staff', b'Staff Member')])),
                ('members', models.ManyToManyField(related_name='teams', verbose_name='members', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(related_name='teams', to='organizations.Organization')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamInvite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_address', models.CharField(max_length=60)),
                ('key', models.CharField(max_length=8)),
                ('team', models.ForeignKey(related_name='invites', to='organizations.Team')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
