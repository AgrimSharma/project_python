# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget

from apps.github_integration.models import *

from apps.projects.limits import org_user_limit


class ReportBugForm( forms.Form ):
    title = forms.CharField(max_length=200)
    body = forms.CharField(max_length=2048, widget=forms.Textarea)


class GithubBindingForm(forms.ModelForm):
    def clean(self):
        cleaned_data = self.cleaned_data
        gh_slug = cleaned_data.get("github_slug")
        try:
            GithubBinding.objects.get(project=self.project, github_slug=gh_slug)
            raise forms.ValidationError("This repository is already assigned to this project.")
        except GithubBinding.DoesNotExist:
            pass # Good, none exist
        return cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(GithubBindingForm, self).save(commit=False)
        m.project = self.project
        if commit:
            m.save()
        return m

    def __init__(self, project, github_projects, *args, **kwargs):
        super(GithubBindingForm, self).__init__(*args, **kwargs)
        self.project = project
        self.fields["github_slug"].widget = forms.Select(choices=github_projects)
        
    class Meta:
        model = GithubBinding
        fields = ('github_slug', 'upload_issues', 'download_issues', 'delete_issues', 'log_commit_messages', 'commit_status_updates')


class KanbanGithubBindingForm(forms.ModelForm):
    def clean(self):
        cleaned_data = self.cleaned_data
        gh_slug = cleaned_data.get("github_slug")
        try:
            GithubBinding.objects.get(project=self.project, github_slug=gh_slug)
            raise forms.ValidationError("This repository is already assigned to this project.")
        except GithubBinding.DoesNotExist:
            pass # Good, none exist
        return cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(KanbanGithubBindingForm, self).save(commit=False)
        m.project = self.project
        if commit:
            m.save()
        return m

    def __init__(self, project, github_projects, *args, **kwargs):
        super(KanbanGithubBindingForm, self).__init__(*args, **kwargs)
        self.project = project
        self.fields["github_slug"].widget = forms.Select(choices=github_projects)
        
    class Meta:
        model = GithubBinding
        fields = ('github_slug', 'upload_issues', 'download_issues', 'delete_issues', 'log_commit_messages')
       