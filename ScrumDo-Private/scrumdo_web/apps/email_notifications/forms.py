# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from apps.email_notifications.models import *


import logging

logger = logging.getLogger(__name__)

         
         
SUBSCRIPTION_CATEGORIES = { # key = sort order & field name
    '00mention' : 'Mentions',
    '01digest':'Digest',
    
    '02iteration_summary':'Iteration',
    '03iteration_scope':'Iteration',
    '04scrumlog':'Iteration',
    '54story_assigned':'Stories',
    '53story_status':'Stories',
    '52story_edited':'Stories',
    '51story_created':'Stories',
    '55story_deleted':'Stories',
    '56story_comment':'Stories',    
    # Disabling mentions for now, they don't work right.
    # '57story_mention':'Stories',
    '21epic_created':'Epics',
    '22epic_edited':'Epics',
    '23epic_deleted':'Epics',
    '77task_created':'Tasks',
    '78task_edited':'Tasks',
    '79task_deleted':'Tasks',
    '70task_status':'Tasks'
    }            
            
            
class EmailSubscriptionForm(forms.ModelForm):

        
    def __init__(self,  *args, **kwargs):
        # initial = kwargs.get("instance")
        super(EmailSubscriptionForm, self).__init__(*args, **kwargs)
        self.option_list = []        
        for field in sorted(SUBSCRIPTION_CATEGORIES.keys()):
            self.fields[field[2:]].category = SUBSCRIPTION_CATEGORIES[field]
            self.fields[field[2:]].initial = self.instance.__dict__[field[2:]]
            self.option_list.append( (field[2:], self.fields[field[2:]]) )

    class Meta:
        model = EmailOptions
        fields = [k[2:] for k in SUBSCRIPTION_CATEGORIES.keys()] + ["marketing",]

