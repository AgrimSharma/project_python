'''
Created on Dec 7, 2012

@author: Sirius
'''
from django import template
from track_me.models import *
from django.db.models.loading import get_model
from django.contrib.auth.models import User, Group


register = template.Library()
import datetime
@register.filter
def get_api_status(a):
     if a in [3,5,7,2,4,6,0,1,13]:
        if a in [3,5]: return "003"
        if a in [7]: return "006"
        if a in [2]: return "002"
        if a in [4,6]: return "005"
        if a in [0,1]: return "001"
        if a in [13]: return "004"
     else: 
        return ''
