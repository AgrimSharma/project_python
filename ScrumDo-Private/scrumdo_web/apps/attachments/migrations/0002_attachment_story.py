# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0001_initial'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='story',
            field=models.ForeignKey(related_name='attachments', to='projects.Story', null=True),
            preserve_default=True,
        ),
    ]
