# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
        ('attachments', '0001_initial'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentExtra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_size', models.PositiveIntegerField()),
                ('related_id', models.PositiveIntegerField()),
                ('is_latest', models.BooleanField(default=True)),
                ('attachment', models.OneToOneField(related_name='extra', to='attachments.Attachment')),
                ('old_version', models.ForeignKey(related_name='attachment_old_version', to='attachments.Attachment', null=True)),
                ('related_iteration', models.ForeignKey(to='projects.Iteration', null=True)),
                ('related_organization', models.ForeignKey(to='organizations.Organization', null=True)),
                ('related_project', models.ForeignKey(to='projects.Project', null=True)),
            ],
            options={
                'db_table': 'v2_subscription_attachment_extra',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cancelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason', models.TextField()),
                ('date', models.DateField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='organizations.Organization', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SingleUseCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('campaign', models.CharField(max_length=32)),
                ('code', models.CharField(max_length=32)),
                ('expiration', models.DateField()),
                ('used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SpreedlyInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_transaction_fetched', models.IntegerField(default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=32)),
                ('expiration', models.DateField()),
                ('trial_days', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubCodeUsage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('code', models.ForeignKey(to='subscription.SubCode')),
                ('organization', models.ForeignKey(to='organizations.Organization')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_revenue', models.DecimalField(default=0, max_digits=8, decimal_places=2)),
                ('plan_id', models.IntegerField(default=1000)),
                ('level', models.IntegerField()),
                ('active', models.BooleanField(default=False)),
                ('token', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('is_billed', models.BooleanField(default=False)),
                ('is_trial', models.BooleanField(default=False)),
                ('had_trial', models.BooleanField(default=False)),
                ('expires', models.DateField(null=True, blank=True)),
                ('grace_until', models.DateField(null=True, blank=True)),
                ('organization', models.OneToOneField(related_name='subscription', to='organizations.Organization')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriptionFeatureOverride',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feature', models.CharField(max_length=16)),
                ('available', models.BooleanField(default=True)),
                ('organization', models.ForeignKey(related_name='subscription_overrides', to='organizations.Organization')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=16)),
                ('tagline', models.CharField(default=b'', max_length=50, blank=True)),
                ('active', models.BooleanField(default=False)),
                ('show_in_grid', models.BooleanField(default=False)),
                ('price', models.CharField(max_length=32)),
                ('price_val', models.DecimalField(default=0.0, max_digits=6, decimal_places=2)),
                ('users', models.IntegerField()),
                ('projects', models.IntegerField()),
                ('storage', models.IntegerField()),
                ('premium_integrations', models.BooleanField(default=False)),
                ('order', models.IntegerField()),
                ('spreedly_id', models.IntegerField()),
                ('feature_level', models.CharField(default=b'', max_length=24, blank=True)),
                ('featured_plan', models.BooleanField(default=False)),
                ('planning_poker', models.BooleanField(default=True)),
                ('epic_tool', models.BooleanField(default=True)),
                ('emails', models.BooleanField(default=True)),
                ('yearly', models.BooleanField(default=False)),
                ('custom_status', models.BooleanField(default=False)),
                ('time_tracking', models.BooleanField(default=False)),
                ('special_allowed', models.BooleanField(default=False)),
                ('kanban', models.BooleanField(default=False)),
                ('live_updates', models.BooleanField(default=False)),
                ('premium_plan', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriptionStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now=True)),
                ('trial_orgs', models.IntegerField()),
                ('recurring_orgs', models.IntegerField()),
                ('paid_orgs', models.IntegerField()),
                ('active_orgs', models.IntegerField()),
                ('expected_monthly_revenue', models.DecimalField(default=0, max_digits=8, decimal_places=2)),
                ('trial_monthly_revenue', models.DecimalField(default=0, max_digits=8, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='attachmentextra',
            name='subscription',
            field=models.ForeignKey(related_name='subscription_files', to='subscription.Subscription'),
            preserve_default=True,
        ),
    ]
