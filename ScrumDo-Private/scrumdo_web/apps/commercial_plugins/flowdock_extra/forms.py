from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import logging
import re
import apps.flowdock

logger = logging.getLogger(__name__)

class SetupForm(forms.Form):
    key = forms.CharField(label=_(u"Flowdock Key"), help_text = _('Find this inside Flowdock by clicking "settings" and look for the section that says "API token for this flow"'))

    def __init__(self, *args, **kwargs):
        super(SetupForm, self).__init__(*args, **kwargs)
        self.fields["key"].widget.attrs={'size':'50'}

    def clean(self):             
        try:
            flowdock.post(self.cleaned_data['key'],"ScrumDo","scrumdo@scrumdo.com","ScrumDo <-> Flowdock Setup","ScrumDo has successfully been configured to post to Flowdock.","ScrumDo",None,"http://www.scrumdo.com/")
        except:
            raise forms.ValidationError("Could not connect.  Check your API key.")

        
        return self.cleaned_data

