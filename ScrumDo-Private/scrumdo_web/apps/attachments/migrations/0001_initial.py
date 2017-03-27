# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.attachments.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment_file', models.FileField(upload_to=apps.attachments.models.attachment_attachment_upload, max_length=512, verbose_name='attachment')),
                ('attachment_url', models.CharField(max_length=512)),
                ('thumb_url', models.CharField(max_length=512)),
                ('attachment_type', models.CharField(default=b'local', max_length=15, choices=[(b'local', b'My Computer'), (b'dropbox', b'Dropbox')])),
                ('attachment_name', models.CharField(max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('creator', models.ForeignKey(related_name='created_attachments', verbose_name='creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
                'db_table': 'v2_attachments_attachment',
                'permissions': (('delete_foreign_attachments', 'Can delete foreign attachments'),),
            },
            bases=(models.Model,),
        ),
    ]
