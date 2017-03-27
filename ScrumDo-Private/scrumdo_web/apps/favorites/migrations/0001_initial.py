# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('favorite_type', models.IntegerField(choices=[(0, b'Story'), (1, b'Project'), (2, b'Iteration'), (3, b'Epic')])),
            ],
            options={
                'db_table': 'v2_favorites_favorite',
            },
            bases=(models.Model,),
        ),
    ]
