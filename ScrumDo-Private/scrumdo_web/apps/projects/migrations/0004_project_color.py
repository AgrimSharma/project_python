# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-28 10:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20160113_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='color',
            field=models.IntegerField(default=16152142),
        ),
    ]
