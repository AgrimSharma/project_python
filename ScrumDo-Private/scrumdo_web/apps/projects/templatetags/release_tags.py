from django.template import loader
from django.template import NodeList
from django.conf import settings
from django.db import models
from django import template
import sys, traceback
import urllib
import json

register = template.Library()

@register.filter
def contains_project(release, project):
    return release.projects.filter(id=project.id).count() > 0

@register.filter
def contains_epic(release, epic):
    return release.epics.filter(id=epic.id).count() > 0