# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-25 10:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_auto_20160516_0334'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='use_assignee',
        ),
        migrations.RemoveField(
            model_name='project',
            name='use_tasks',
        ),
        migrations.AddField(
            model_name='project',
            name='use_due_date',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='project',
            name='use_points',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='project',
            name='use_risk_reduction',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='use_time_crit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='use_time_estimate',
            field=models.BooleanField(default=True),
        ),
    ]
