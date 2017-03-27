# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django import forms
from django.conf import settings
from apps.organizations.models import Organization
from apps.projects.models import Project

class OrganizationPlusProjectForm(forms.Form):   
    organization_name = forms.CharField(max_length=65, help_text="The name of your company or team of people.")
    project_name = forms.CharField(required=False,max_length=65, help_text="The name of the project to work on.  You can add additional projects later.")    
    project_members = forms.CharField(required=False,widget=forms.Textarea, help_text="Enter email addresses of members to invite.  One per line.")
    sub_code = forms.CharField(required=False, help_text="Subscription offer code")

    def __init__(self, *args, **kwargs):
        super(OrganizationPlusProjectForm, self).__init__(*args, **kwargs)
        # self.fields['project_type'] = forms.ChoiceField(required=True,widget=forms.RadioSelect,help_text="Which type of project should we create?", choices=Project.PROJECT_TYPE_CHOICES,initial=0)


    def save(self, commit=False):
        org = Organization()
        org.name = self.cleaned_data['organization_name']
        if commit:
            org.save()
        return org
        
