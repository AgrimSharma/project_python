#!/usr/bin/env python

from apps.projects.models import Epic, Project, Iteration, Story, PointsLog, SiteStats
from apps.activities.models import NewsItem
from apps.extras.models import *
from apps.organizations.models import *
from apps.realtime.models import ChatMessage
from mailer.models import Message
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from apps.emailconfirmation.models import EmailAddress


import logging
import string
import random
logger = logging.getLogger(__name__)

string_types = (string.ascii_lowercase, string.ascii_uppercase, string.digits)

def anon_char(char):
    for char_class in string_types:
        if char in char_class:
            return random.choice(char_class)
    return char
    

def anon(inp):
    if inp == None:
        return None
    s = list(inp)
    for i in range(len(s)):
        s[i] = anon_char(s[i])
    return "".join(s)


def anonymize_objects(object_type, fields):
    count = object_type.objects.all().count()
    i = 0
    print "Anonymizing %s" % object_type
    for obj in object_type.objects.all():
        for field in fields:
            setattr(obj,field, anon(getattr(obj,field)))            
        obj.skip_haystack = True
        obj.save()
        i+=1
        if (i % 1000) == 0:
            print "%s %d / %d" % (object_type,i,count)
    print "%s completed!" % object_type

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.DEBUG:
            logger.error("Can only run this on sites in debug mode (for safety!)")
            return

        confirm = raw_input("We're about to devestate this DB making it completely non-production worthy and destroy user data.  Type yes to continue.\n > ")
        if confirm != "yes":
            return

        threads = []
        
        models = (  
                    # (Organization,["name","description","source"]),
                    # (Project, ["name","description","extra_1_label","extra_2_label","extra_3_label","categories","token"]),
                    # (Iteration, ["name","detail"]),                    
                    # (Story, ["summary","detail","category","extra_2","extra_1","extra_3"]  ),
                    (Epic, ["summary","detail"]),
                    (NewsItem,["text"]  ),
                    (User,["email","first_name","last_name"]),
                    (EmailAddress,["email"]),                    
                    (TeamInvite,["email_address"]),
                    # (ChatMessage,["message"]),
                    # (ScrumLog,["message"]),
                 )
        
        for m in models:
            anonymize_objects(m[0],m[1])            
            

        
        # anonymize_objects(Project, ["name","description","extra_1_label","extra_2_label","extra_3_label","categories","token"] )
        #        anonymize_objects(Iteration, ["name","detail"] )
        #        anonymize_objects(Story, ["summary","detail","category","extra_2","extra_1","extra_3"] )
        #        anonymize_objects(Epic, ["summary","detail"] )

          

