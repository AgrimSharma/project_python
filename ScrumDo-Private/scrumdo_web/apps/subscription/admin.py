# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.contrib import admin
from apps.projects.models import Project, Iteration, SiteStats, Story, StoryTag
from django.contrib.auth.models import User
from django import forms
from apps.organizations.models import Organization
from django.contrib.admin.actions import delete_selected

from apps.subscription.models import *

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')
    search_fields = ('name', 'slug')
    actions = [delete_selected]

class StoryAdmin(admin.ModelAdmin):
    list_display = ('summary', 'project', 'modified')


def getSubChoices():
    return ( (r.id, "%s %d - %s - %s" % ("(old)" if not r.active else "", r.id, r.name, r.feature_level) )  for r in SubscriptionPlan.objects.all().order_by("-active","id") )


class SubscriptionInlineForm(forms.ModelForm):
    class Meta:
        model = Subscription
        widgets = {}
        exclude = ()
        def __init__(self):
            self.widgets['plan_id'] = forms.Select(choices=getSubChoices())


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    form = SubscriptionInlineForm


class SubscriptionFeatureOverrideInlineForm(forms.ModelForm):    
    class Meta:
            model = SubscriptionFeatureOverride
            exclude = ()
            widgets = {
                'feature': forms.Select(choices=(
                        ("","---------"),
                        ("custom_status","custom_status"),
                        ("emails","emails"),
                        ("epic_tool","epic_tool"),
                        ("kanban","kanban"),
                        ("live_updates","live_updates"),
                        ("planning_poker", "planning_poker"),
                        ("premium_integrations","premium_integrations"),
                        ("time_tracking","time_tracking")
                    ))
            }
class SubscriptionFeatureOverrideInline(admin.TabularInline):
    model = SubscriptionFeatureOverride
    form = SubscriptionFeatureOverrideInlineForm

class OrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.fields['creator'].queryset = User.objects.filter(teams__organization=self.instance).distinct().order_by("username")
            
class OrganizationAdmin(admin.ModelAdmin):
    inlines = [SubscriptionInline, SubscriptionFeatureOverrideInline ]
    list_display = ('name', 'slug', 'subscription','source','created')
    list_filter = ('subscription__plan_id',)
    search_fields = ('name', 'slug')    
    form = OrganizationForm
       
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ('organization__slug', 'organization__name', 'level')
    list_display = ('organization', 'level', 'active')
   
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'price', 'active','show_in_grid','spreedly_id','feature_level','users','projects','storage')
    ordering = ["active","show_in_grid","order"]

class CancelAdmin(admin.ModelAdmin):
    list_display = ('organization', 'reason', 'user', 'date')


class SubscriptionCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'expiration', 'trial_days')


admin.site.register(SubCode, SubscriptionCodeAdmin)
admin.site.register(Cancelation, CancelAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(SubscriptionPlan,SubscriptionPlanAdmin)
admin.site.register( Subscription , SubscriptionAdmin)
