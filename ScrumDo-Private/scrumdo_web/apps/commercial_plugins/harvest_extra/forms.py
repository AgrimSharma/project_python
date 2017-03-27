# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django import forms
from django.utils.translation import ugettext_lazy as _
import re
import harvest as harvest
import urllib2

import logging

logger = logging.getLogger(__name__)

class HarvestConfig(forms.Form):
    username = forms.CharField(max_length=100, help_text = _("Your Harvest username, probably your email address."))
    password = forms.CharField(widget=forms.PasswordInput, help_text = _("Your Harvest password.") )
    url = forms.CharField(help_text = _("Your personal harvest URL.  Example: https://scrumdo.harvestapp.com"))
    def clean_url(self):
        logger.debug(self.cleaned_data["url"])
        m = re.search("^https(://[^/]+)$",self.cleaned_data["url"])
        if m == None:
            raise forms.ValidationError("The URL must be in the form: https://yoursite.harvestapp.com")
        return "https%s" % m.group(1)

    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            h = harvest.Harvest(cleaned_data.get("url"),cleaned_data.get("username"),cleaned_data.get("password") )
            for harvest_project in h.projects():
                pass
        except:
            raise forms.ValidationError("Could not log in with these credentials.")
            
        return cleaned_data
    