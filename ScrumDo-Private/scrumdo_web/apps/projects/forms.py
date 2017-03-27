# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from apps.projects.models import Project, Iteration, Story, Task, Epic, Release
from apps.organizations.models import Team
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import RadioFieldRenderer
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


from apps.projects.limits import userIncreasedAlowed
from time_utils import toInt
import logging
import datetime

logger = logging.getLogger(__name__)

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

# @@@ we should have auto slugs, even if suggested and overrideable



class SplitHoursMinsWidget(forms.widgets.MultiWidget):

    def __init__(self, *args, **kwargs):
        widgets = (
            forms.TextInput(),
            forms.TextInput()
        )
        super(SplitHoursMinsWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value:
            logger.debug([value//60,value%60])
            return [value//60, "%02d" % (value%60) ] 
        return ["0", "00"]

    def format_output(self, rendered_widgets):
        return (rendered_widgets[0] + ":" + rendered_widgets[1] + " (HH:MM)")

    def value_from_datadict(self, data, files, name):
        hours_mins = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)]
        try:
            return toInt(hours_mins[0])*60 + toInt(hours_mins[1])
        except ValueError:
            return None

class IterationForm(forms.ModelForm):
    def __init__(self,  *args, **kwargs):
        super(IterationForm, self).__init__(*args, **kwargs)
        self.fields['include_in_velocity'].label = "Include In Velocity Calculations"

    class Meta:
        model = Iteration
        fields = ('name', 'start_date', 'end_date', 'include_in_velocity')

    def clean(self):
        cleaned_data = self.cleaned_data
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if end_date and start_date and end_date < start_date:
            msg = u"End date should be greater than start date."
            self._errors["end_date"] = self.error_class([msg])
            del cleaned_data['end_date']
        return cleaned_data


class ReleaseForm(forms.ModelForm):
    def clean_delivery_date(self):
        sd = self.cleaned_data["start_date"]
        ed = self.cleaned_data["delivery_date"]
        # sd = datetime.datetime.strptime("%Y-%m-%d", sd_text)
        # ed = datetime.datetime.strptime("%Y-%m-%d", ed_text)
        if sd >= ed:
            raise forms.ValidationError("Delivery date must be after the start date.")
        return self.cleaned_data["delivery_date"]
        
    class Meta:
        model = Release
        fields = ("name","start_date","delivery_date")
        
        
class ProjectOptionsForm(forms.ModelForm):
    card_type_1 = forms.CharField(max_length=10, )
    card_type_2 = forms.CharField(max_length=10, required=False)
    card_type_3 = forms.CharField(max_length=10, required=False)
    card_type_4 = forms.CharField(max_length=10, required=False)
    card_type_5 = forms.CharField(max_length=10, required=False)
    card_type_6 = forms.CharField(max_length=10, required=False)
    card_type_7 = forms.CharField(max_length=10, required=False)
    card_type_8 = forms.CharField(max_length=10, required=False)
    card_type_9 = forms.CharField(max_length=10, required=False)
    card_type_10 = forms.CharField(max_length=10, required=False)

    task_status_1 = forms.CharField(max_length=10, )
    task_status_2 = forms.CharField(max_length=10, required=False)
    task_status_3 = forms.CharField(max_length=10, required=False)
    task_status_4 = forms.CharField(max_length=10, required=False)
    task_status_5 = forms.CharField(max_length=10, required=False)
    task_status_6 = forms.CharField(max_length=10, required=False)
    task_status_7 = forms.CharField(max_length=10, required=False)
    task_status_8 = forms.CharField(max_length=10, required=False)
    task_status_9 = forms.CharField(max_length=10, required=False)
    task_status_10 = forms.CharField(max_length=10)
    
    def __init__(self, *args, **kwargs):
        super(ProjectOptionsForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["style"] = 'width:595px;'
        self.fields["categories"].widget.attrs["style"] = 'width:595px;'
        self.fields["description"].widget.attrs["style"] = 'width:600px; height:75px;'
        cardTypes = list(self.instance.cardTypes())
        task_statuses = list(self.instance.task_statuses())
        for i in range(10):
            self.fields["card_type_%d" % (i+1)].initial = cardTypes[i]

        for i in range(10):
            self.fields["task_status_%d" % (i+1)].initial = task_statuses[i]

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(ProjectOptionsForm, self).save(commit=False)

        m.task_status_names = ""
        for i in range(10):
            m.task_status_names += "%-10s" % self.cleaned_data["task_status_%d" % (i+1) ]

        m.card_types = ""
        for i in range(10):
            m.card_types += "%-10s" % self.cleaned_data["card_type_%d" % (i+1) ]

        if commit:
            m.save()
        return m
        
    class Meta:
        model = Project
        fields = ('live_updates','category','categories','velocity_type','point_scale_type', 'use_extra_1', 'use_extra_2', 'use_extra_3', 'extra_1_label', 'extra_2_label', 'extra_3_label','name', 'description' )

class TaskForm( forms.ModelForm ):
    tags = forms.CharField( required=False )
    complete = forms.BooleanField()

    def __init__(self, project, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        members = project.all_member_choices()
        members.insert(0,("","Nobody"))
        self.fields["assignee"].choices = members
        self.fields["summary"].widget = forms.widgets.TextInput(attrs={'size':'50'})
        self.fields["tags"].initial = self.instance.tags
        self.fields["complete"].initial = self.instance.complete

    def save(self,  **kwargs):
        self.instance.tags = self.cleaned_data["tags"]
        self.instance.complete = self.cleaned_data["complete"]
        return super(TaskForm, self).save(**kwargs)

    class Meta:
        model = Task
        fields = ('summary','assignee','tags',)

class AddStoryForm( forms.ModelForm ):
    RANK_CHOICES = (
        ('0', 'Top'),
        ('1', 'Middle'),
        ('2', 'Bottom') )
    project = None
    tags = forms.CharField( required=False )
    general_rank = forms.CharField( required=False, widget=forms.RadioSelect(choices=RANK_CHOICES), initial=2)
    assignee = forms.CharField(required=False)
    iteration = forms.ModelChoiceField(queryset=None, empty_label=None)

    def __init__(self, project, *args, **kwargs):
        super(AddStoryForm, self).__init__(*args, **kwargs)
        self.fields["points"].choices = project.getPointScale()
        self.fields["points"].widget = forms.RadioSelect(choices=project.getPointScale())
        self.fields["summary"].widget = forms.widgets.Textarea(attrs={'rows':1, 'cols':50, 'maxlength':5000})
        self.fields["summary"].widget.size = 200
        members = project.all_member_choices()
        members.insert(0,("","---------"))
        self.fields["extra_1"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50, 'maxlength':5000})
        self.fields["extra_2"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50, 'maxlength':5000})
        self.fields["extra_3"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50, 'maxlength':5000})
        self.fields["detail"].widget.attrs['maxlength'] = 5000

        self.fields["estimated_minutes"].widget = SplitHoursMinsWidget()
        
        epics = [ (epic.id, ("#E%d %s" % (epic.local_id, epic.summary))[:150] ) for epic in project.epics.all().order_by("local_id") ]
        epics.insert(0,("","----------") )
        self.fields["epic"].choices=epics
        self.fields["epic"].required = False
        choices = []
        if project.categories:
            choices = [(c.strip(),c.strip()) for c in project.categories.split(",")]
        choices.insert(0,("","----------"))
        self.fields["category"] = forms.ChoiceField(choices=choices, required=False)
        self.fields["extra_1"].required = False
        self.fields["extra_2"].required = False
        self.fields["extra_3"].required = False
        self.fields["tags"].initial = self.instance.tags

        self.fields["status"].required = False
        self.fields["status"].widget = forms.widgets.RadioSelect(choices=project.status_choices(), renderer=StatusRadioRenderer)

        self.fields['iteration'].queryset = project.iterations.all()

    def save(self,  **kwargs):
        self.instance.tags = self.cleaned_data["tags"]
        return super(AddStoryForm, self).save(**kwargs)

    class Meta:
        model = Story
        fields = ('status', 'summary', 'detail', 'category', 'tags', 'points', 'iteration', 'extra_1','extra_2','extra_3','epic','estimated_minutes')


class EpicForm( forms.ModelForm ):
    def __init__(self, project,  *args, **kwargs):
        super(EpicForm, self).__init__(*args, **kwargs)
        self.project = project

        self.fields["summary"].widget = forms.TextInput()
        self.fields["summary"].widget.attrs['size'] = 60
        self.fields["summary"].widget.attrs['maxlength'] = 5000
        self.fields["detail"].widget.attrs['maxlength'] = 5000
        
        epics = [ (epic.id, ("#E%d %s" % (epic.local_id, epic.summary)[:150]) ) for epic in project.epics.all().order_by("local_id") ]
        epics.insert(0,("","----------") )
        self.fields["parent"].choices=epics
        self.fields["parent"].required = False        
        

    def clean_points(self):
        try:
            self.cleaned_data["points"] = int(self.cleaned_data["points"])
            if self.cleaned_data["points"] > 9999 :
                raise forms.ValidationError("Points must be less than 10,000")
        except:
            self.cleaned_data["points"] = "?"
        return self.cleaned_data["points"]

    def save(self,  **kwargs):
        self.instance.project = self.project
        if not self.instance.local_id:
            self.instance.local_id = self.project.getNextEpicId()
        archived = self.cleaned_data["archived"]
        # for epic in self.instance.children.exclude(archived=archived):
        #     epic.archived = archived
        #     epic.save()
            
        return super(EpicForm, self).save(**kwargs)

    class Meta:
        model = Epic
        fields = ('summary','detail','points','parent', 'archived')


class StatusRadioRenderer( RadioFieldRenderer ):
    def render( self ):
        """Outputs a series of <td></td> fields for this set of radio fields."""
        return( mark_safe( u''.join( [ u'<div class="status-pill status-bg-%s">%s %s</div>' % (w.choice_value, force_unicode(w.tag()),w.choice_label) for w in self ] )))


class StoryForm( forms.ModelForm ):
    RANK_CHOICES = (
        ('0', 'Top'),
        ('1', 'Middle'),
        ('2', 'Bottom') )
    project = None
    tags = forms.CharField( required=False )
    summary = forms.CharField(widget=forms.Textarea())
    comments = forms.CharField(widget=forms.Textarea(), required=False)
    assignee = forms.CharField()
    iteration = forms.ModelChoiceField(queryset=None)

    def __init__(self, project, *args, **kwargs):
        
        if "request" in kwargs:
            self.request = kwargs.pop("request")

        super(StoryForm, self).__init__(*args, **kwargs)

        
        

        self.fields["points"].choices = project.getPointScale()
        self.fields["points"].widget = forms.RadioSelect(choices=project.getPointScale())
        self.fields["summary"].widget = forms.widgets.Textarea(attrs={'rows':4, 'cols':50, 'maxlength':5000})
        self.fields["summary"].widget.size = 200
        members = project.all_member_choices()
        members.insert(0,("","---------"))
        
        epics = [ (epic.id, "#E%d %s" % (epic.local_id, epic.summary) ) for epic in project.epics.exclude(archived=True).order_by("local_id") ]
        epics.insert(0,("","----------") )
        self.fields["epic"].choices=epics
        self.fields["epic"].required = False
        
        self.fields["detail"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50, 'maxlength':5000})
        self.fields["extra_1"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50, 'maxlength':5000})
        self.fields["extra_2"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50, 'maxlength':5000})
        self.fields["extra_3"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50, 'maxlength':5000})
        self.fields["status"].widget = forms.widgets.RadioSelect(choices=project.status_choices(), renderer=StatusRadioRenderer)
        self.fields["estimated_minutes"].widget = SplitHoursMinsWidget()
        
        
        choices = []    
        if project.categories:
            choices = [(c.strip(),c.strip()) for c in project.categories.split(",")]
        choices.insert(0,("","----------"))
        self.fields["category"] = forms.ChoiceField(choices=choices, required=False)
        self.fields["assignee"].required = False
        self.fields["assignee"].initial = self.instance.assignees_cache
        self.fields["extra_1"].required = False
        self.fields["extra_2"].required = False        
        self.fields["extra_3"].required = False
        self.fields["tags"].initial = self.instance.tags

#        picked_iteration = kwargs.get('picked_iteration')
#        self.fields['iteration'].initial = picked_iteration
        self.fields['iteration'].queryset = project.iterations.all()

    def save(self,  **kwargs):
        self.instance.tags = self.cleaned_data["tags"]
        self.instance.assignees = self.cleaned_data["assignee"]
        logger.debug("Status: %s" % self.cleaned_data["status"])

        story = super(StoryForm, self).save(**kwargs)

        return story

    class Meta:
        model = Story
        fields = ('summary', 'detail', 'tags', 'points', 'iteration', 'category', 'extra_1','extra_2','extra_3', 'status', 'epic', 'estimated_minutes')


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        team_options = kwargs.pop('team_options', None)
        project_options = kwargs.pop('project_options', None)
        personal = kwargs.pop("personal", False)
        workflow_options = kwargs.pop("workflow_options", None)
        super(ProjectForm, self).__init__(*args, **kwargs)
        
        if workflow_options is not None:
            self.fields['Workspace Flow'] = forms.ChoiceField(widget=forms.RadioSelect, required=True, choices=workflow_options, \
                                                    initial='continuous', help_text= _("Continuous type Workspace will have a single continuous Iteration."))

        if not personal:
            self.fields['Teams'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, choices=team_options)
            if project_options:
                self.fields['Workspace'] = forms.ChoiceField(widget=forms.Select, required=False, choices=project_options, \
                                                    help_text= _("(Optional) Select a workspace to clone board structure and settings."))

    class Meta:
        model = Project
        fields = ('name', )

    def clean_project_type(self):
        data = self.cleaned_data['project_type']
        return int(data)
    
    def save(self, force_insert=False, force_update=False, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        project.project_type = Project.PROJECT_TYPE_KANBAN  # self.cleaned_data["project_type"]
        return project



# @@@ is this the right approach, to have two forms where creation and update fields differ?

class ProjectUpdateForm(forms.ModelForm):
    def clean_name(self):
        if Project.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            if self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]

    class Meta:
        model = Project
        fields = ('name', 'description')

class FindStoryForm(forms.Form):
    text = forms.CharField(label="Search For")

class IterationImportForm(forms.Form):
    import_file  = forms.FileField(required=False)

class IterationImportFormWithUnlock(forms.Form):
    import_file  = forms.FileField(required=False)
    unlock_iteration = forms.BooleanField( required=False, help_text = _("Unlocking the iteration allows users with the appropriate access to edit stories in this iteration.") )

class UnlockForm(forms.Form):
    unlock_iteration = forms.BooleanField( required=False, help_text = _("Unlocking the iteration allows users with the appropriate access to edit stories in this iteration.") )

class ExportForm(forms.Form):
    format = forms.ChoiceField(choices=(("xls","Excel"),("csv","Comma Seperated Value (CSV)"),("xml","XML") ) )
    lock_iteration = forms.BooleanField( required=False, help_text = _("Locking the iteration prevents anyone from editing any stories in it until the iteration is unlocked.") )
    file_name = forms.CharField( required=False, help_text = _("Name of the file when saved to disk.") )

class ExportProjectForm(forms.Form):
    #format = forms.ChoiceField(initial="sheet", choices=(("sheet","Export each iteration as a seperate sheet."),("combined","Export one combined sheet.") ) , widget=forms.RadioSelect() )
    file_name = forms.CharField( required=False, help_text = _("Name of the file when saved to disk.") )
