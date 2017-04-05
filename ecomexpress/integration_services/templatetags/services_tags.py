'''
Created on Dec 7, 2012

@author: Sirius
'''
from django import template
#from track_me.models import *
#from django.db.models.loading import get_model
#from django.contrib.auth.models import User, Group
#import unicodedata
#from service_centre.models import *

register = template.Library()
#import datetime
#from utils import chunks

@register.filter
def get_fetchawb_status(status):
    
    if status == 0:
        return 'In Queue'
    if status == 1:
        return 'In Process'
    if status == 2:
        return 'Completed'
        
