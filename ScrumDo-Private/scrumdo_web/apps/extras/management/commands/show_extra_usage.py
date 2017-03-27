#!/usr/bin/env python

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



# This script figures out how many people are actually using various extras.


import sys
from datetime import date, timedelta
from apps.projects.limits import org_extra_limit
from apps.projects.models import Project, Iteration, Story, PointsLog
from apps.extras.models import ProjectExtraMapping, SyncronizationQueue
from apps.extras.manager import manager
from apps.extras.util import processQueueItem
from apps.projects.limits import personal_email_limit, org_email_limit, org_custom_status
from django.conf import settings

import logging
import sys, traceback
import getopt
import urllib2

from django.core.management.base import BaseCommand, CommandError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        for extra in settings.SCRUMDO_EXTRAS:
            self.calculateUsage(extra)

    def calculateUsage(self, extraClassname):
        extra = get_class(extraClassname)()
        slug = extra.getSlug()        
        active = 0
        subscribed = 0
        activeConfiguredAndSubscribed = 0
        configured = 0
        orgs = {}
        orgCount = 0

        usesConfig = ["github"]
        
        today = date.today()  
        thirtyDaysAgo = today + timedelta(days=-30)

        for mapping in ProjectExtraMapping.objects.filter(extra_slug=slug).select_related("project"):
            project = mapping.project
            if project.organization == None:
                continue
            organization = project.organization

            a = False
            s = False
            c = False
            if project.newsItems.filter(created__gt=thirtyDaysAgo).count() > 0:
                active += 1
                a = True

            if org_email_limit.increaseAllowed(organization=project.organization) and organization.subscription.active and organization.subscription.token != "":
                subscribed += 1
                s = True
            
            config = extra.getConfiguration(project.slug)            
            if (config != None) and (config != {}):
                configured += 1
                c = True

            if slug in usesConfig:
                if a and s and c:
                    activeConfiguredAndSubscribed += 1
                    orgSlug = project.organization.slug
                    if not orgSlug in orgs:
                        orgs[orgSlug] = True
                        orgCount += 1
            elif a and s:
                orgSlug = project.organization.slug
                if not orgSlug in orgs:
                    orgs[orgSlug] = True
                    orgCount += 1                
                activeConfiguredAndSubscribed += 1 # not all extra use the configuration

        print "%20s %3d %3d %3d %3d %3d" % (slug, active, configured, subscribed, activeConfiguredAndSubscribed, orgCount)





def get_class( kls ):
    return getattr(__import__( kls , {}, {}, ['Plugin']), 'Plugin')
