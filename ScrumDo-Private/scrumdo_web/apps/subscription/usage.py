# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from apps.projects.models import Project
from apps.organizations.models import Organization

import logging

logger = logging.getLogger(__name__)

def calculateUserUsage(organization):
    users = []
    # for project in organization.projects.all():
    #     for member in project.members.all():
    #         if (not member.user.id in users) and (member.user != project.creator):
    #             # Not counting project creators due to some odd use-cases where a creator gives a project
    #             # to an organization, but is later removed from the organization.  That results in a phantom
    #             # user in the counts.
    #             
    #             # logger.debug(member.user)
    #             users.append(member.user.id)
    for team in organization.teams.all():
        for user in team.members.all():
            if not user.id in users:
                # logger.debug(user)
                users.append(user.id)
    return len(users)

def calculateStorageUsage(organization):
    from models import AttachmentExtra
    size = AttachmentExtra.objects.subscription_usage(organization.subscription)
    return (size / (1024*1024))

def calculateProjectUsage(organization):
    # exclude Portfolio Level Backlog projects from Organization Usage
    return organization.projects.filter(active=True).exclude(project_type = Project.PROJECT_TYPE_BACKLOG_ONLY).count()
