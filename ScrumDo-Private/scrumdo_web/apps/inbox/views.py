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


from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from apps.organizations.models import Organization
from apps.subscription.decorators import expired_subscription_check

# import logging
#
# logger = logging.getLogger(__name__)


@login_required
@expired_subscription_check
def inbox(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasReadAccess(request.user):
        raise PermissionDenied()

    return render_to_response("inbox/inbox.html", {
        "organization": organization,
        "user": request.user
    }, context_instance=RequestContext(request))
