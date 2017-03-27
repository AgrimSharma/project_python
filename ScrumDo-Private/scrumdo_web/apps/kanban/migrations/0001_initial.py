# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.kanban.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BacklogHistorySnapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'v2_kanban_backloghistorysnapshot',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BacklogHistoryStories',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'v2_kanban_backloghistorystories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BoardCell',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cellType', models.SmallIntegerField(default=0)),
                ('label', models.CharField(max_length=100, null=True)),
                ('full_label', models.CharField(max_length=100, null=True)),
                ('layout', models.PositiveSmallIntegerField(default=0)),
                ('headerColor', models.IntegerField(default=11184810)),
                ('backgroundColor', models.IntegerField(default=16448250)),
                ('wipLimit', models.IntegerField(default=-1)),
                ('pointLimit', models.IntegerField(default=-1)),
                ('x', models.IntegerField(default=0)),
                ('y', models.IntegerField(default=0)),
                ('width', models.IntegerField(default=200)),
                ('height', models.IntegerField(default=200)),
                ('policy_text', models.TextField(default=b'', blank=True)),
                ('time_type', models.PositiveSmallIntegerField(default=2)),
                ('leadTime', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'v2_kanban_boardcell',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BoardGraphic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('graphic_type', models.IntegerField(default=0)),
                ('label', models.CharField(max_length=128)),
                ('sx', models.IntegerField()),
                ('sy', models.IntegerField()),
                ('ex', models.IntegerField()),
                ('ey', models.IntegerField()),
                ('foreground', models.IntegerField(default=11184810)),
                ('background', models.IntegerField(default=11184810)),
            ],
            options={
                'db_table': 'v2_kanban_boardgraphic',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BoardHeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sx', models.IntegerField()),
                ('sy', models.IntegerField()),
                ('ex', models.IntegerField()),
                ('ey', models.IntegerField()),
                ('background', models.IntegerField(default=4473924)),
                ('label', models.CharField(max_length=128)),
                ('policy_text', models.TextField(default=b'', blank=True)),
            ],
            options={
                'db_table': 'v2_kanban_boardheader',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BoardImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sx', models.IntegerField()),
                ('sy', models.IntegerField()),
                ('ex', models.IntegerField()),
                ('ey', models.IntegerField()),
                ('image_file', models.ImageField(height_field=b'image_height', width_field=b'image_width', upload_to=apps.kanban.models.board_image_attachment_upload)),
                ('image_height', models.IntegerField(default=0)),
                ('image_width', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'v2_kanban_boardimage',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CellMovement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('epic_id', models.IntegerField(default=0)),
                ('label_ids', models.CharField(default=b'', max_length=72)),
                ('tags', models.CharField(default=b'', max_length=256)),
                ('assignee_ids', models.CharField(default=b'', max_length=72)),
                ('points_value', models.DecimalField(max_digits=6, decimal_places=1)),
            ],
            options={
                'db_table': 'v2_kanban_cellmovement',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CellMovementLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_cell_movement', models.IntegerField(default=0, null=True)),
            ],
            options={
                'db_table': 'v2_cell_movement_log',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CFDCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('processing', models.BooleanField(default=True)),
                ('filters', models.CharField(default=b'', max_length=256)),
            ],
            options={
                'db_table': 'v2_kanban_cfd_cache',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CFDCachedStory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'v2_kanban_cfd_cached_story',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CFDCachedValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField()),
                ('point_value', models.IntegerField()),
                ('card_count', models.IntegerField()),
                ('archive', models.BooleanField(default=False)),
                ('backlog', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'v2_kanban_cfd_cached_value',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KanbanizeJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('complete', models.BooleanField(default=False)),
                ('config', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'v2_kanban_kanbanizejob',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KanbanStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('daily_lead_time', models.IntegerField()),
                ('daily_flow_efficiency', models.IntegerField()),
                ('system_lead_time', models.IntegerField()),
                ('system_flow_efficiency', models.IntegerField()),
                ('cards_claimed', models.IntegerField(default=0)),
                ('points_claimed', models.IntegerField(default=0)),
                ('created', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'v2_kanban_kanbanstat',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('policy_type', models.SmallIntegerField(default=0)),
                ('user_defined', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=128)),
                ('related_value', models.IntegerField()),
            ],
            options={
                'db_table': 'v2_kanban_policy',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PolicyAge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entered', models.DateTimeField(auto_now_add=True)),
                ('exited', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'db_table': 'v2_kanban_policyage',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PolicyNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RebuildMovementJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'v2_kanban_rebuildmovementjob',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StepMovement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'v2_kanban_stepmovement',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StepStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateField(auto_now_add=True)),
                ('stories', models.IntegerField()),
                ('points', models.IntegerField()),
            ],
            options={
                'db_table': 'v2_kanban_stepstat',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagMovement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags_cache', models.CharField(max_length=512)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('epic_id', models.IntegerField(default=0)),
                ('label_ids', models.CharField(default=b'', max_length=72)),
                ('assignee_ids', models.CharField(default=b'', max_length=72)),
                ('points_value', models.DecimalField(default=b'0.0', max_digits=6, decimal_places=1)),
            ],
            options={
                'db_table': 'v2_kanban_tagmovement',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagMovementLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_tag_movement', models.IntegerField(default=0, null=True)),
            ],
            options={
                'db_table': 'v2_tag_movement_log',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('default', models.BooleanField(default=False)),
                ('flow_type', models.SmallIntegerField(default=0, choices=[(0, b'User Defined'), (1, b'System Generated')])),
            ],
            options={
                'db_table': 'v2_kanban_workflow',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WorkflowStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=128)),
                ('report_color', models.IntegerField(default=4492490, null=True)),
                ('mapped_status', models.SmallIntegerField(default=-1)),
                ('workflow', models.ForeignKey(related_name='steps', to='kanban.Workflow')),
            ],
            options={
                'ordering': ['order'],
                'db_table': 'v2_kanban_workflowstep',
            },
            bases=(models.Model,),
        ),
    ]
