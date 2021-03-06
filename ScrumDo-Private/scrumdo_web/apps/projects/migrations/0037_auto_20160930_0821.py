# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-30 08:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0036_teamiterationwiplimit'),
    ]

    operations = [
        migrations.CreateModel(
            name='Risk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(max_length=512)),
                ('probability', models.PositiveSmallIntegerField(default=0)),
                ('severity_1', models.PositiveSmallIntegerField(default=0)),
                ('severity_2', models.PositiveSmallIntegerField(default=0)),
                ('severity_3', models.PositiveSmallIntegerField(default=0)),
                ('severity_4', models.PositiveSmallIntegerField(default=0)),
                ('severity_5', models.PositiveSmallIntegerField(default=0)),
                ('severity_6', models.PositiveSmallIntegerField(default=0)),
                ('severity_7', models.PositiveSmallIntegerField(default=0)),
                ('cards', models.ManyToManyField(related_name='risks', to='projects.Story')),
                ('iterations', models.ManyToManyField(related_name='iterations', to='projects.Iteration')),
            ],
        ),
        migrations.AddField(
            model_name='portfolio',
            name='risk_type_1',
            field=models.CharField(default=b'Business', max_length=32),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='risk_type_2',
            field=models.CharField(default=b'Financial', max_length=32),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='risk_type_3',
            field=models.CharField(default=b'Technical', max_length=32),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='risk_type_4',
            field=models.CharField(default=b'', max_length=32),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='risk_type_5',
            field=models.CharField(default=b'', max_length=32),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='risk_type_6',
            field=models.CharField(default=b'', max_length=32),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='risk_type_7',
            field=models.CharField(default=b'', max_length=32),
        ),
        migrations.AddField(
            model_name='risk',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Portfolio'),
        ),
        migrations.AddField(
            model_name='risk',
            name='projects',
            field=models.ManyToManyField(related_name='projects', to='projects.Project'),
        ),
    ]
