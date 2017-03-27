from .common import *

from apps.projects.models import MilestoneAssignment
from apps.projects.managers import enableReleasesMode, enablePortfolioMode

class OrganizationHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    write_fields = ('description', 'end_of_week', 'timezone', 'name')
    fields = ["description",
              "created",
              "end_of_week",
              "id",
              "timezone",
              "slug",
              "name",
              "mobile_allowed",
              "planning_mode",
              "subscription"]

    exclude = ('creator', 'source')
    model = Organization

    @staticmethod
    def mobile_allowed(organization):
        # TODO - right now, tying mobile allowed to premium integration, might want to separate that out.
        return organization.subscription.planPremiumExtras()

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug):
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasStaffAccess(request.user):
            raise PermissionDenied('You can not update this organization.')

        data = request.data
        for field in OrganizationHandler.write_fields:
            if field in data:
                setattr(organization, field, data[field])

        if 'planning_mode' in data and organization.planning_mode != data['planning_mode']:
            if data['planning_mode'] == Organization.PLANNING_MODES.release:
                organization.planning_mode = Organization.PLANNING_MODES.release
                enableReleasesMode(organization, request.user)
            elif data['planning_mode'] == Organization.PLANNING_MODES.portfolio:
                organization.planning_mode = Organization.PLANNING_MODES.portfolio
                enablePortfolioMode(organization, request.user)

        organization.save()
        return organization

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug=None):
        base = Organization.objects
        if organization_slug:
            org = base.get(slug=organization_slug)
            if not org.hasReadAccess(request.user):
                raise PermissionDenied("You don't have access to that Organization")
            return org
        else:
            return base.filter(teams__members=request.user).distinct()
