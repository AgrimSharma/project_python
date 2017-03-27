from django import forms


class NamedModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class ExportForm(forms.Form):
    iteration = NamedModelChoiceField(queryset=None, empty_label=None)
    field = forms.ChoiceField()
    RADIO_CHOICES = (
        ('cucumber', "Cucumber '.feature'"),
        ('txt', ".txt"),
    )
    type = forms.ChoiceField(widget=forms.RadioSelect(), choices=RADIO_CHOICES, initial={'txt': '.txt'})

    def __init__(self, project, fields, *args, **kwargs):
        super(ExportForm, self).__init__(*args, **kwargs)
        self.fields["field"].choices = fields
        self.fields['iteration'].queryset = project.iterations.all().order_by("end_date")