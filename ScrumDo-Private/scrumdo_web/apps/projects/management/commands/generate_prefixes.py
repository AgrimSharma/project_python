#!/usr/bin/env python
from apps.projects.models import Project, Iteration, Story, PointsLog
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
import string
import random
import re


import logging

logger = logging.getLogger(__name__)


def generateProjectPrefix(project, userDefined=None):
    c = 0
    prefix = _get_prefix(project, c)
    while True:
        try:
            Project.objects.get(prefix=prefix, organization=project.organization)
            c += 1
            prefix = _get_prefix(project, c)
        except Project.DoesNotExist:
            break
    return prefix.upper()


def _get_prefix(project, counter=0):
    prefix = ""
    if counter < 2:
        prefix = _get_prefix_char(project, counter)
        return prefix
    elif counter < 12:
        r = random.randint(1, 9)
        p = _get_prefix_char(project, 1)
        prefix = "%s%s" % (p[0], r)
        return prefix
    else:
        prefix = prefix_generator()
        return prefix


def _get_prefix_char(project, counter=0):
    name = re.sub('[^0-9a-zA-Z\s]+', '', project.name)
    names = name.split()
    prefix = ""
    if len(names) > 1:
        if len(names[1]) > 1:
            prefix = "%s%s" % (names[0][0], names[1][counter])
        else:
            prefix = "%s%s" % (names[0][0], names[1][0])
    elif len(names) == 1:
        if len(names[0]) > 1:
            prefix = "%s%s" % (names[0][0], names[0][1])
        else:
            prefix = "%s%s" % (names[0][0], names[0][0])
    else:
        prefix = prefix_generator()
    return prefix


def prefix_generator(size=2, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



class Command(BaseCommand):
    def handle(self, *args, **options):
        projects = Project.objects.filter(Q(prefix=None) | Q(prefix='')).order_by("-id")
        for project in projects:
            prefix = generateProjectPrefix(project)
            project.prefix = prefix
            logger.info(prefix)
            project.save()