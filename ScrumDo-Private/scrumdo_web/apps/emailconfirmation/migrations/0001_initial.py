# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('verified', models.BooleanField(default=False)),
                ('primary', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'e-mail address',
                'verbose_name_plural': 'e-mail addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailConfirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sent', models.DateTimeField()),
                ('confirmation_key', models.CharField(max_length=40)),
                ('email_address', models.ForeignKey(to='emailconfirmation.EmailAddress')),
            ],
            options={
                'verbose_name': 'e-mail confirmation',
                'verbose_name_plural': 'e-mail confirmations',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='emailaddress',
            unique_together=set([('user', 'email')]),
        ),
    ]
