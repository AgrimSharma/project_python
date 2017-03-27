from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from jira import Jira

import logging
import re


logger = logging.getLogger(__name__)

class FilterForm( forms.Form ):
    
    def __init__(self, choices, projects, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["project"] = forms.ChoiceField(label="Jira Project to add bugs to", choices=projects , required=False)        
        self.fields["importStories"] = forms.BooleanField(label="Add Jira bugs to import queue", initial=True, required=False, help_text="Should ScrumDo retrieve a list of bugs from Jira and add them to the import queue so you can turn them into stories?")
        self.fields["jiraFilter"] = forms.ChoiceField(label="Jira Filter to get bugs from", choices=choices , required=False, help_text="ScrumDo uses this filter to find a list of bugs to add to the import queue.  You always have the option of importing individual bugs or not.<br/><br/>You can create a new filter in Jira and refresh this page.")
    def clean(self):
        if len(self.cleaned_data["jiraFilter"]) == 0:
            raise forms.ValidationError("Please select a Jira filter to use.  You can go create one, come back, and referesh this page if you need to.")
        return self.cleaned_data

        

class StatusForm( forms.Form ):
    def __init__(self, statuses, *args, **kwargs):
        statusChoices = [(status.id, status.name) for status in statuses]
        statusChoices.insert(0, ('-1',"None") )
        super(StatusForm, self).__init__(*args, **kwargs)
        self.fields["todoStatus"] = forms.ChoiceField(label="Todo Status", choices=statusChoices , required=False, help_text="The Jira Status that maps to ScrumDo TODO")
        self.fields["doingStatus"] = forms.ChoiceField(label="Doing Status", choices=statusChoices , required=False, help_text="The Jira Status that maps to ScrumDo Doing")
        self.fields["reviewingStatus"] = forms.ChoiceField(label="Reviewing Status", choices=statusChoices , required=False, help_text="The Jira Status that maps to ScrumDo Reviewing")
        self.fields["doneStatus"] = forms.ChoiceField(label="Done Status", choices=statusChoices , required=False, help_text="The Jira Status that maps to ScrumDo Done")

class CredentialsForm(forms.Form):
    url = forms.URLField(label=_(u"Jira URL"), help_text = _("The base URL to your Jira server.  Examples:  http://jira.example.com or http://jira.example.com:8080"))
    username = forms.CharField(label=_(u"Username"), help_text = _('The Jira username ScrumDo should use'))
    password = forms.CharField(label=_(u"Password"), help_text = _('The Jira password ScrumDo should use'), widget=forms.PasswordInput )
    
    def __init__(self, *args, **kwargs):
        super(CredentialsForm, self).__init__(*args, **kwargs)
        self.fields["url"].widget.attrs={'size':'50'}
        self.fields["username"].widget.attrs={'size':'50'}
        self.fields["password"].widget.attrs={'size':'50'}        

    def clean(self):
        url = self.cleaned_data.get("url","")
        username = self.cleaned_data.get("username","")
        password = self.cleaned_data.get("password","")
        
        if len(url) == 0 or len(username) == 0 or len(password) == 0:
            raise forms.ValidationError("Could not load list of projects.  Check your login credentials.")
        
        m = re.search('^(http[s]*://[^/]+)', url)
        if m is not None:
            # Remove any extra bits at the end of the url
            url = m.group(1)
            
        if url[-1] == "/":
            # Remove trailing slash
            url = url[:-1]
        
        self.cleaned_data["url"] = url
        
        try:
            # Make sure the connection works
            test_connection = Jira(url,username,password)
            all_projects = test_connection.getProjects()            
        except:
            raise forms.ValidationError("Could not load list of projects.  Check your login credentials.")

        if len(all_projects) == 0:
            raise forms.ValidationError("Could not load any projects.  Check your login credentials.")

        return self.cleaned_data

