# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-21 08:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_project_shared'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='shared',
            field=models.CharField(blank=True, default=None, max_length=25, null=True),
        ),
    ]