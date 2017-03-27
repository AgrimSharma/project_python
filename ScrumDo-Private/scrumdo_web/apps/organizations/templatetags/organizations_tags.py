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


from django import template
from apps.projects.forms import ProjectForm
from django.template import NodeList
from apps.projects.models import Story
from apps.projects.access import has_write_access, has_admin_access, has_read_access
from apps.organizations.tz import formatDateTime, toOrganizationTime
from django.template.defaultfilters import stringfilter
import re
register = template.Library()


@register.filter
def org_datetime(datetime='', organization=''):
    try:
        return formatDateTime(datetime, organization)
    except:
        return datetime.strftime("%b %d, %Y %I:%M %p")


@register.filter
def org_shortdatetime(datetime, organization):
    try:
        datetime = toOrganizationTime(datetime,organization)
    except:
        pass
    return datetime.strftime("%m/%d/%Y %I:%M %p")

@register.tag(name="isorgstaff")
def isorgstaff( parser, token):
    tag_name, organization = token.split_contents()
    nodelist_true = parser.parse(('else','endisorgstaff',))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endisorgstaff',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()

    # parser.delete_first_token()
    return IsAdminNode(nodelist_true, nodelist_false, organization)

class IsAdminNode(template.Node):
    def __init__(self, nodelist_true,nodelist_false, organization):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.organization = organization
    def render(self, context):
        if self.organization in context and context[self.organization] is not None and context[self.organization].hasStaffAccess(context["request"].user):
            output = self.nodelist_true.render(context)
            return output
        else:
            output = self.nodelist_false.render(context)
            return output

@register.tag(name="teammember")
def teammember( parser, token):
    tag_name, team = token.split_contents()
    nodelist = parser.parse(('endteammember',))
    parser.delete_first_token()
    return IsAdminNode(nodelist, team)

class IsTeamMemberNode(template.Node):
    def __init__(self, nodelist, team):
        self.nodelist = nodelist
        self.team = team
    def render(self, context):
        if context[self.team].hasMember( context["request"].user ):
            output = self.nodelist.render(context)
            return output
        else:
            return ""
            
