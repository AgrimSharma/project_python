# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailNotificationQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('event_type', models.CharField(max_length=32)),
            ],
            options={
                'db_table': 'v2_email_notifications_emailnotificationqueue',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailOptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('digest', models.PositiveSmallIntegerField(default=0, help_text=b'Daily digest of activity in projects', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects')])),
                ('iteration_summary', models.PositiveSmallIntegerField(default=0, help_text=b'End of iteration report', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects')])),
                ('iteration_scope', models.PositiveSmallIntegerField(default=0, help_text=b'Story added to current iteration', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects')])),
                ('story_assigned', models.PositiveSmallIntegerField(default=0, help_text=b'A Story is (re)assigned', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('story_status', models.PositiveSmallIntegerField(default=0, help_text=b"A Story's status changes", choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('story_edited', models.PositiveSmallIntegerField(default=0, help_text=b'A Story is edited', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('story_created', models.PositiveSmallIntegerField(default=0, help_text=b'A Story is created', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('story_deleted', models.PositiveSmallIntegerField(default=0, help_text=b'A Story is deleted', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('story_comment', models.PositiveSmallIntegerField(default=0, help_text=b'A Story is commented on', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('epic_created', models.PositiveSmallIntegerField(default=0, help_text=b'An Epic is created', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects')])),
                ('epic_edited', models.PositiveSmallIntegerField(default=0, help_text=b'An Epic is edited', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects')])),
                ('epic_deleted', models.PositiveSmallIntegerField(default=0, help_text=b'An Epic is deleted', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects')])),
                ('task_created', models.PositiveSmallIntegerField(default=0, help_text=b'A Task is created', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('task_edited', models.PositiveSmallIntegerField(default=0, help_text=b'A Task is edited', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('task_deleted', models.PositiveSmallIntegerField(default=0, help_text=b'A Task is deleted', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('task_status', models.PositiveSmallIntegerField(default=0, help_text=b"A Task's status changes", choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects'), (3, b'Assigned To You')])),
                ('mention', models.PositiveSmallIntegerField(default=2, help_text=b'You are explicitly mentioned by username', choices=[(0, b'Never'), (2, b'Always')])),
                ('scrumlog', models.PositiveSmallIntegerField(default=0, help_text=b'A scrum log is posted', choices=[(0, b'Never'), (1, b'Watched Projects'), (2, b'All Projects')])),
                ('marketing', models.BooleanField(default=True, help_text=b'News and updates about ScrumDo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryMentions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'v2_email_notifications_storymentions',
            },
            bases=(models.Model,),
        ),
    ]
