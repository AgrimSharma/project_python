# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from apps.projects.models import Project
from apps.organizations.models import Organization
from apps.projects.limits import *

import logging

logger = logging.getLogger(__name__)

def initializeHandlers():
    # Personal account limits:
    personal_project_limit.addHandler( PersonalProjectLimit(10) )
    personal_user_limit.addHandler( PersonalUserLimit(10) )
    personal_storage_limit.addHandler( AlwaysNo() )
    personal_extra_limit.addHandler( AlwaysNo() )
    personal_email_limit.addHandler( AlwaysNo() )
    personal_ssl_access.addHandler( SSLLimit() )

    # Organizational account limits:
    org_project_limit.addHandler( OrganizationalProjectLimit() )
    org_user_limit.addHandler( OrganizationalUserLimit() )
    org_storage_limit.addHandler( OrganizationalStorageLimit() )
    org_extra_limit.addHandler( OrganizationalExtraLimit() )
    org_email_limit.addHandler( OrganizationalEmailLimit() ) 
    org_planning_poker.addHandler( OrganizationalPokerLimit() )

    org_kanban.addHandler( OrganizationKanban() )
    org_live_updates.addHandler( OrganizationLiveUpdates() )

    org_custom_status.addHandler( OrganizationalCustomStatus() )
    
    on_demand_velocity.addHandler( VelocityCalculationHandler() )
    
    org_time_tracking.addHandler( OrganizationTimeTracking() )
    # Uncomment the following lines to debug resource full scenarios.
    # personal_user_limit.addHandler( AlwaysNo() )
    # personal_project_limit.addHandler( AlwaysNo() )
    # personal_organization_limit.addHandler( AlwaysNo() )
    # org_user_limit.addHandler( AlwaysNo() )
    # org_project_limit.addHandler( AlwaysNo() )
    # org_organization_limit.addHandler( AlwaysNo() )

class BaseLimit( object ):
    def increaseAllowed( self, **kwargs ):
        max_allowed = self.maxAllowed(**kwargs)
        current = self.currentUsage( **kwargs )
        logger.debug("Testing limit %d > %d ?" % (max_allowed, current) )
        return max_allowed > current
    def stats(self, **kwargs):
        max_allowed = self.maxAllowed(**kwargs)
        current = self.currentUsage( **kwargs )
        return (max_allowed, current, max_allowed < current)

class SSLLimit(BaseLimit):
    def canHandle(self, **kwargs ):
        return True
    def increaseAllowed( self, **kwargs ):
        user = kwargs.get("user", None)
        orgs = Organization.getOrganizationsForUser(user)
        for org in orgs:
            if org.subscription.planPremiumExtras():
                # Piggy back on premium extras for now
                return True
        return False
        
class VelocityCalculationHandler(BaseLimit):
    def canHandle(self, **kwargs ):
        return True
    def increaseAllowed( self, **kwargs ):
        project = kwargs.get("project", None)
        if project.organization == None:
            return False
            
        return project.organization.subscription.planInstantCalculation()

class OrganizationalExtraLimit(BaseLimit):
    def canHandle(self, **kwargs ):
        return True
    def increaseAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        allowed = organization.subscription.planPremiumExtras()
        if not allowed:
            allowed = organization.subscription_overrides.filter(feature="premium_integrations",available=True).count() > 0
        return allowed



class OrganizationalPokerLimit(BaseLimit):
    def canHandle(self, **kwargs ):
        return True
    def increaseAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        allowed = organization.subscription.planPoker()
        if not allowed:
            allowed = organization.subscription_overrides.filter(feature="planning_poker",available=True).count() > 0
        return allowed        

class OrganizationalCustomStatus(BaseLimit):
    def canHandle(self, **kwargs ):
        return True
    def increaseAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        allowed = organization.subscription.planCustomStatus()
        if not allowed:
            allowed = organization.subscription_overrides.filter(feature="custom_status",available=True).count() > 0
        return allowed            

class OrganizationTimeTracking(BaseLimit):
    def canHandle(self, **kwargs ):
        return True
    def increaseAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        allowed = organization.subscription.planTimeTracking()
        if not allowed:
            allowed = organization.subscription_overrides.filter(feature="time_tracking",available=True).count() > 0
        return allowed         

class OrganizationKanban(BaseLimit):
    def canHandle(self, **kwargs ):
        return True
    def increaseAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        allowed = organization.subscription.planKanban()
        if not allowed:
            allowed = organization.subscription_overrides.filter(feature="kanban",available=True).count() > 0
        return allowed    

class OrganizationLiveUpdates(BaseLimit):
    def canHandle(self, **kwargs ):
        return True
    def increaseAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        allowed = organization.subscription.planLiveUpdates()
        if not allowed:
            allowed = organization.subscription_overrides.filter(feature="live_updates",available=True).count() > 0
        return allowed  


class OrganizationalEmailLimit(BaseLimit):
    def canHandle(self, **kwargs ):
        return True
    def increaseAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        allowed = organization.subscription.planEmail()
        if not allowed:
            allowed = organization.subscription_overrides.filter(feature="emails",available=True).count() > 0
        return allowed           

class OrganizationalUserLimit( BaseLimit ):
    def maxAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        return organization.subscription.planUsers()     # Just delegating to the subscription for all of these...
    def currentUsage( self, **kwargs ):
        organization = kwargs.get("organization", None)
        return organization.subscription.usersUsed()
    def canHandle(self, **kwargs ):
        organization = kwargs.get("organization",None)
        return (organization != None) and (organization.subscription != None)
    def increaseAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        userToAdd = kwargs.get("userToAdd",None)
        if userToAdd in self._teamMembers( organization ):
            # user is already a part of this organization
            return True
        return self.maxAllowed(**kwargs) > self.currentUsage(  **kwargs )
    def _teamMembers( self, organization ):
        users = []
        for project in organization.projects.all():
            if not project.active:
                continue
            # for member in project.members.all():
            #     if not member.user in users:
            #         users.append(member.user) # Members individually assigned to a project

        for team in organization.teams.all():
            for user in team.members.all():
                if not user in users:
                    users.append(user)  # members in a team
        return users

class OrganizationalProjectLimit( BaseLimit ):
    def maxAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        return organization.subscription.planProjects()
    def currentUsage( self, **kwargs ):
        organization = kwargs.get("organization", None)
        return organization.subscription.projectsUsed()
    def canHandle(self, **kwargs ):
        organization = kwargs.get("organization",None)
        return (organization != None) and (organization.subscription != None)


class OrganizationalStorageLimit( BaseLimit ):
    def maxAllowed( self, **kwargs ):
        organization = kwargs.get("organization", None)
        return organization.subscription.planStorage() * 1024
    def currentUsage( self, **kwargs ):
        organization = kwargs.get("organization", None)
        return organization.subscription.storageUsed()
    def canHandle(self, **kwargs ):
        organization = kwargs.get("organization",None)
        return (organization != None) and (organization.subscription != None)

class PersonalUserLimit( BaseLimit ):
    "Defines a limit for adding users to a project that is not part of an organization."

    def __init__(self, limit):
        self.limit = limit

    def maxAllowed( self, **kwargs ):
        return self.limit

    def increaseAllowed( self, **kwargs ):
        user = kwargs.get("user",None)
        userToAdd = kwargs.get("userToAdd",None)
        members = self._generateMemberList( user )
        if userToAdd in members:
                # User is already a member of one of the other projects, so it's ok to add
                # them to this one no matter what the count.
            logger.debug("User already in another project, allowing add to this one.")
            return True
        return self.maxAllowed(**kwargs) > self.currentUsage( memberList=members, **kwargs )


    def currentUsage( self, **kwargs ):
        user = kwargs.get("user",None)
        userToAdd = kwargs.get("userToAdd",None)
        members = kwargs.get("memberList", self._generateMemberList(user) )
        logger.debug("Current usage: %d" % len(members))

        return len( members )

    def _generateMemberList(self, owner ):
        members = []
        # for project in Project.objects.filter( creator=owner, active=True, organization=None ) :
        #     for membership in project.members.all():
        #         user = membership.user
        #         if not user in members:
        #             members.append(user)
        return members

    def canHandle(self, **kwargs ):
        organization = kwargs.get("organization",None)
        return organization == None

class PersonalProjectLimit(BaseLimit):
    "The limit for personal projects"
    def __init__(self, limit):
        self.limit = limit

    def maxAllowed( self, **kwargs ):
        return self.limit

    def currentUsage( self, **kwargs ):
        user = kwargs.get("user",None)
        return Project.objects.filter( creator=user, active=True, organization=None ).count()

    def canHandle(self, **kwargs ):
        organization = kwargs.get("organization",None)
        return organization == None




class AlwaysNo(BaseLimit):
    def canHandle( self, **kwargs ):
        return True
    def maxAllowed( self, **kwargs):
        return 0
    def currentUsage( self, **kwargs):
        return 0
