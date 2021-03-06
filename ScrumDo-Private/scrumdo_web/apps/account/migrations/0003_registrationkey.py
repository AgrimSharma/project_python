# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-01-17 08:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20160112_0843'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('key', models.CharField(blank=True, max_length=32, null=True)),
                ('is_used', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
