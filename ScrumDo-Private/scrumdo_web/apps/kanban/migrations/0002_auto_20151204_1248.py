# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='project',
            field=models.ForeignKey(related_name='workflows', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagmovementlog',
            name='project',
            field=models.OneToOneField(to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagmovement',
            name='related_iteration',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='projects.Iteration', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagmovement',
            name='story',
            field=models.ForeignKey(to='projects.Story'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stepmovement',
            name='related_iteration',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='projects.Iteration', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stepmovement',
            name='step_from',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='kanban.WorkflowStep', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stepmovement',
            name='step_to',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='kanban.WorkflowStep', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stepmovement',
            name='story',
            field=models.ForeignKey(to='projects.Story'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stepmovement',
            name='user',
            field=models.ForeignKey(related_name='+', default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stepmovement',
            name='workflow',
            field=models.ForeignKey(to='kanban.Workflow'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rebuildmovementjob',
            name='initiator',
            field=models.ForeignKey(related_name='+', default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rebuildmovementjob',
            name='project',
            field=models.ForeignKey(related_name='+', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='policyage',
            name='policy',
            field=models.ForeignKey(to='kanban.Policy'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='policyage',
            name='story',
            field=models.ForeignKey(to='projects.Story'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='policy',
            name='project',
            field=models.ForeignKey(related_name='policies', to='projects.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kanbanstat',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kanbanizejob',
            name='destination',
            field=models.ForeignKey(related_name='+', to='projects.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kanbanizejob',
            name='initiator',
            field=models.ForeignKey(related_name='+', default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kanbanizejob',
            name='source',
            field=models.ForeignKey(related_name='+', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfdcachedvalue',
            name='cache',
            field=models.ForeignKey(related_name='values', to='kanban.CFDCache'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfdcachedvalue',
            name='step',
            field=models.ForeignKey(to='kanban.WorkflowStep', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfdcachedstory',
            name='story',
            field=models.ForeignKey(related_name='stories', to='projects.Story'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfdcachedstory',
            name='value',
            field=models.ForeignKey(to='kanban.CFDCachedValue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfdcache',
            name='iteration',
            field=models.ForeignKey(to='projects.Iteration', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfdcache',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfdcache',
            name='workflow',
            field=models.ForeignKey(to='kanban.Workflow'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cellmovementlog',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cellmovementlog',
            name='workflow',
            field=models.ForeignKey(to='kanban.Workflow'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cellmovementlog',
            unique_together=set([('project', 'workflow')]),
        ),
        migrations.AddField(
            model_name='cellmovement',
            name='cell_to',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='kanban.BoardCell', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cellmovement',
            name='related_iteration',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='projects.Iteration', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cellmovement',
            name='story',
            field=models.ForeignKey(to='projects.Story'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cellmovement',
            name='user',
            field=models.ForeignKey(related_name='+', default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardimage',
            name='project',
            field=models.ForeignKey(related_name='images', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardheader',
            name='policy',
            field=models.ForeignKey(default=None, to='kanban.Policy', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardheader',
            name='project',
            field=models.ForeignKey(related_name='headers', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardgraphic',
            name='policy',
            field=models.ForeignKey(default=None, to='kanban.Policy', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardgraphic',
            name='project',
            field=models.ForeignKey(related_name='graphics', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardcell',
            name='policies',
            field=models.ManyToManyField(related_name='cells', db_table=b'v2_kanban_boardcell_policies', to='kanban.Policy'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardcell',
            name='project',
            field=models.ForeignKey(related_name='boardCells', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardcell',
            name='steps',
            field=models.ManyToManyField(related_name='cells', null=True, db_table=b'v2_kanban_boardcell_steps', to='kanban.WorkflowStep'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardcell',
            name='wip_policy',
            field=models.ForeignKey(default=None, to='kanban.Policy', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backloghistorystories',
            name='snapshot',
            field=models.ForeignKey(related_name='stories', to='kanban.BacklogHistorySnapshot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backloghistorystories',
            name='story',
            field=models.ForeignKey(to='projects.Story'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backloghistorysnapshot',
            name='backlog',
            field=models.ForeignKey(to='projects.Iteration'),
            preserve_default=True,
        ),
    ]
