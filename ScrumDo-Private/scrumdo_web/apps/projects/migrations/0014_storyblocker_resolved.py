# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-04 22:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_auto_20160504_0816'),
    ]

    operations = [
        migrations.AddField(
            model_name='storyblocker',
            name='resolved',
            field=models.BooleanField(default=False),
        ),
    ]
