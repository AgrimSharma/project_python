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
from datetime import date, time, datetime

from django_markup.markup import formatter

from apps.projects.models import Story, Project
from apps.projects.access import has_write_access, has_admin_access, has_read_access
from apps.projects.util import reduce_burndown_data
from apps.projects.limits import personal_email_limit, org_email_limit, org_custom_status
from apps.favorites.models import Favorite
from django.template.defaultfilters import stringfilter
from django.template import NodeList

from apps.html2text import html2text as _html2text

import apps.organizations.tz as tz
from django.conf import settings

from .kanban_terms import KANBAN_TERMS, PORTFOLIO_TERMS
import sys, traceback
import urllib
import math
import random

import re
register = template.Library()

urlfinder = re.compile('((?:https|http)://[^\s<>]+)')
import logging

logger = logging.getLogger(__name__)





TIPS = [
    "Set a WIP limit of 999 on a cell to display the number of cards without seeing the limit",
    "Set a WIP limit of 999 on a cell to display the number of points without seeing the limit",
    "Set a WIP limit of 999 on a header to display the number of cards in several related cells",
    "Shift-Click cards to multi-select",
    "Drag a card up or down in an iteration to set it's rank.",
    "Use Planning poker to size stories with remote co-workers.",
    "Use tags to keep track of story <b>themes</b>",
    "Use epics or tags to group stories into features.",
    "Select your point scale in the workspace settings.",
    "Change your velocity calculation method in the workspace settings.",
    "Add custom fields in the workspace settings.",
    "ScrumDo can connect to your GitHub Issues",
    "What third party integrations would you like to see in ScrumDo?",
    "Set up email notifications via the gear menu in the upper right",
    "Create a release to track progress across workspaces.",
    "Set up your full name in the account settings page.",
    "@mentions - If you put an @username in a story or comment, that person will receive an email to let them know.",
    "If you could change just one thing about ScrumDo, what would it be?",
    "Visit help.scrumdo.com for all kinds of great info",
    "Do personal kanaban with a personal workspace that only YOU can see",
    "User Stories - A unit of work that describes something useful to your customer.",
    "Story Points - A relative measure of effort between cards.",
    "Scrum Role: Product Owner - Guides the team on what features should be built.",
    "Scrum Role: Scrum Master - Removes obstacles and guides the team in Scrum principles.",
    "Scrum Role: Team Members - The rest of the team doing the actual work of implementing the user stories.",
    "Definition of Done - An explicit statement of what 'done' means for a given piece of work.",
    "Backlog - A list of work that is not yet scheduled to start.",
    "Burndown Charts - A way of tracking how quickly the team is completing work."
    ]
TIPS_LENGTH = len(TIPS) - 1
@register.simple_tag
def scrumdo_tip():
    return TIPS[random.randint(0, TIPS_LENGTH)]

@register.simple_tag
def silk(name):
    mappings = { 
        "cog":"icon-cog",
        "cogs":"icon-cogs",
        "chart_organisation" : "icon-sitemap",
        "chart_organisation_add" : "icon-sitemap",
        "chart_org_delete" : "icon-trash",
        "drive_add" : "icon-tasks icon-green",
        "drive_delete" : "icon-tasks icon-red",
        "drive_edit" : "icon-tasks",
        "drive_go" : "icon-share",
        "flag_red" : "icon-flag",
        "comment_add" : "icon-comment",
        "script_add" : "icon-file icon-green",
        "script_delete" : "icon-trash",
        "script_go" : "icon-share",
        "script_edit" : "icon-edit",
        "script_code" : "icon-check",
        "group" : "icon-group",
        "tag_blue" : "icon-tag icon-blue",
        "attach": "icon-paper-clip",
        "calendar_delete" : "icon-calendar icon-red",
        "calendar_add" : "icon-calendar icon-blue"
    }
    if name in mappings:
        name = mappings[name]
    if name[0:4] == "icon":
        return """<i class='%s icon-glyph'></i>""" % (name)
    else:
        return """<img class="silk_icon" src="%spinax/images/silk/icons/%s.png" />""" % (settings.SSL_STATIC_URL, name)


@register.filter("html2text")
def html2text(html):
    return _html2text(html)

@register.filter("last_activity_date")
def last_activity_date(project):
    news = project.newsItems.all().order_by("-created")
    if news.count() == 0:
        return ""
    return news[0].created


@register.filter("google_chart_url")
def google_chart_url(iteration_or_project):
    return _google_chart(iteration_or_project)

@register.filter("tiny_google_chart_url")
def tiny_google_chart_url(iteration_or_project):
    return _google_chart(iteration_or_project, project_size="140x50", iteration_size="140x50", label_axis="", bg_color="f6f6f6", axis_color="f6f6f6", title=True)

def _google_chart(iteration_or_project, project_size="550x120", iteration_size="550x80", label_axis="y", bg_color="ffffff", axis_color="444444", title=False):
    """Returns a URL for either a project or an iteration that corresponds to the burn up chart generated by google charts.
       The url will be to an image format. If no chart can be drawn, a 1x1 image is returned.  This should be used for quick
       summary charts, not detailed pretty ones.  We only use it in emails right now.  """
    try:
        total_points = []
        claimed_points = []
        max_val = 0
        claimed_dates = []
        claimed_values = []
        total_dates = []
        total_values = []

        # Chart Size...
        if hasattr(iteration_or_project,"slug"):
            size = project_size
            # Project charts are bigger than iteration charts.
        else:
            size = iteration_size

        # Gather up all the points_log entries.
        for log in iteration_or_project.points_log.all():
            total_points.append( [log.timestamp(), log.points_total] )
            claimed_points.append( [log.timestamp(), log.points_status10] )
            if log.points_total > max_val:
                max_val = log.points_total

        # If we don't have enough points to draw a chart, bail.
        if len(total_points) <= 1:
            # logger.warn("Not enough points to plot")
            return "https://chart.googleapis.com/chart?cht=lxy&chs=1x2"

        # Remove redundant data in chart data.
        total_points = reduce_burndown_data(total_points)
        claimed_points = reduce_burndown_data(claimed_points)

        # Some helper values.
        start_date = total_points[0][0]        
        end_date = total_points[-1][0]
        
        
        start_date_s = date.fromtimestamp( start_date/1000 ).strftime('%Y-%m-%d')
        
        try:
            end_date_s = iteration_or_project.end_date.strftime('%Y-%m-%d')
            end_date = int(datetime.combine(iteration_or_project.end_date, time()).strftime("%s")) * 1000
        except:                    
            end_date_s = date.fromtimestamp( end_date/1000 ).strftime('%Y-%m-%d')

        
        # logger.debug("END DATE" % end_date_s)            
        date_range = end_date - start_date

        # Create the entries for the total points series.
        for piece in total_points:
            total_dates.append( _googleChartValue(piece[0], start_date, end_date) )
            total_values.append( _googleChartValue( piece[1] ,0, max_val) )

        # Create the entries for the claimed points series.
        for piece in claimed_points:
            claimed_dates.append( _googleChartValue(piece[0], start_date, end_date) )
            claimed_values.append( _googleChartValue( piece[1] ,0, max_val) )

        if title:
            title_snippet = "chtt=%s&chts=000000,8&" %  urllib.quote(iteration_or_project.name)
        else:
            title_snippet = ""
        
        # Put it all together in google chart format.  (Docs: http://code.google.com/apis/chart/)
        data = "https://chart.googleapis.com/chart?%schf=bg,s,%s&chxr=0,0,%d&cht=lxy&chs=%s&chd=s:%s,%s,%s,%s&chxt=%s,x&chxs=0,%s,8,0,lt&chxl=1:|%s|%s&chco=9ED147,30B6EB&chm=B,eef5fb,1,0,0|B,99CBB0,0,0,0" % ( title_snippet, bg_color, max_val,size,"".join(claimed_dates), "".join(claimed_values), "".join(total_dates), "".join(total_values), label_axis, axis_color, start_date_s, end_date_s )
        #logger.debug(data)
        return data
    except:
        traceback.print_exc(file=sys.stdout)
        return "https://chart.googleapis.com/chart?cht=lxy&chs=1x1"


def _googleChartValue(val, min_val, max_val):
    """ Google charts can encode values in a 62 value range using alpha numeric characters.  This
        method does that for a given value, and a given range (min/max) of values """
    codes = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    if (max_val - min_val) == 0:
        return 'A'
    
    percent = (val-min_val) / float(max_val - min_val)
    new_val = int( 61 * percent )
    return codes[ new_val ]

@register.filter("urlify2")
def urlify2(value):
    if value.find("<img") >= 0:
        return value
    if value.find("<a") >= 0:
        return value
    return urlfinder.sub(r'<a target="_blank" href="\1">\1</a>', value)
    

@register.filter("name_or_username")
def name_or_username(user):
    if not user:
        return ''
    if user.first_name and user.last_name:
        return "%s %s" % (user.first_name, user.last_name)
    return user.username

@register.filter("probable_email")
def probable_email(user):
    """ Returns what is probably the user's email address.  Use this to get the address of a user who never
        actually verified it. """
    try:
        if len(user.email) > 0:
            return user.email
        addrs = user.emailaddress_set.all()
        for email in addrs:
            if email.verified:
                return email.email

        # no verified, no primary emails...
        if len(addrs) > 0:
            return addrs[0].email
    except:
        logger.warn("Could not get probable email.")
        return ""

    return ""

@register.filter
def gt(a, b):
    return a > b




@stringfilter
def link_stories(value, project):
    """ Creates links to stories in a body of text.
        Example: 'Story #4' would open up the edit window for story with local_id #4 """
    def replaceLink( value ):
        try:
            local_id = value.group(1)
            story = Story.objects.get( project=project, local_id=int(local_id) )
            return "<a class='storyLink' onclick=\"scrumdoEditStory(%d, -1, '%s'); return false;\" >%s</a>" % (story.id, project.slug, value.group(0))
        except:
            return value.group(0)

    return re.sub(r'[sS]tory #([0-9]+)', replaceLink , value)

link_stories.is_safe=True
register.filter('link_stories', link_stories)


def _linkStories(input, project):
    """
        Links stories in the format "Story #5" or "Card #5" to a permalink for that story.
        Story #4
        will become...
        <a href='/projects/story_permalink/390482'>Story #4</a>
        It will try to not re-create stupid nested links by excluding anything with </a> after it.
    """
    def replaceLink(value):
        try:
            if value.group(3) is not None:
                # Most likely aleady wrapped.
                return value.group(0)
            local_id = value.group(2)
            story = project.stories.get(local_id=int(local_id) )
            return "<a href=\"%s/projects/story_permalink/%d\">%s</a>" % (settings.SSL_BASE_URL, story.id, value.group(0))
        except:
            return value.group(0)

    try:
        if input is None or input == '':
            return ''
        return re.sub(r'(?i)(story|card) #([0-9]+)(</a>)?', replaceLink, input)
    except:
        return input

@stringfilter
def link_stories_v2(input, project):
    """
        Links stories in the format "Story XX-5" or "Card XX-5" to a permalink for that story.
        Story XX-4
        will become...
        <a href='/projects/story_permalink/390482'>Story XX-4</a>
        It will try to not re-create stupid nested links by excluding anything with </a> after it.
        XX = Project Prefix
    """
    P = (project,)
    def replaceLinkVer2(value):
        try:
            if value.group(4) is not None:
                # Most likely aleady wrapped.
                return value.group(0)
            local_id = value.group(3)
            prefix = value.group(2)
            # not able to access project variable here, got working with this
            project = P[0]
            if prefix == project.prefix:
                story = project.stories.get(local_id=int(local_id))
            else:
                try:
                    project = Project.objects.get(prefix=prefix.upper(), organization = project.organization)
                    story = project.stories.get(local_id=int(local_id))
                except:
                    return value.group(0)
            return "<a href=\"%s/projects/story_permalink/%d\">%s</a>" % (settings.SSL_BASE_URL, story.id, value.group(0))
        except:
            return value.group(0)
    
    try:
        if input is None or input == '':
            return ''
        v = re.sub(r'(?i)(story|card) ([A-Z,0-9]{2})-([0-9]+)(</a>)?', replaceLinkVer2, input)
        return _linkStories(v, project)
    except:
        return input


link_stories_v2.is_safe=True
register.filter('link_stories_v2', link_stories_v2)


@register.inclusion_tag("projects/sub_iteration_list.html", takes_context=True)
def sub_iteration_list(context, project):
    iterations = project.iterations.all().order_by("-default_iteration", "-end_date")
    if 'iteration' in context:
        current = context['iteration']
    else:
        current = None

    return {"project_slug":project.slug, "iterations":iterations, "current_iteration":current, "request":context['request']}

@register.inclusion_tag("projects/projects_list.html", takes_context=True)
def show_projects(context, organization):
    user = context['request'].user
    org_count = organization.projects.filter(active=True).count()
    if org_count > 28:
        # too many projects, only grab the favorite/watched ones
        favorite_projects = Favorite.objects.filter(project__active=True,user=user, project__organization=organization).select_related('project').order_by("-project__active","project__category","project__name")
        projects = [fav.project for fav in favorite_projects]        
        if( len(projects) == 0):
            # User has no favorites, so we'll give them all anyways.
            projects = organization.projects.filter(active=True).order_by("category","name")
    else:
        projects = organization.projects.filter(active=True).order_by("category","name")
    
    all_projects = len(projects) == org_count
    return {"STATIC_URL":context["STATIC_URL"],"organization":organization, "all_projects":all_projects, "projects":projects, "request":context['request']}


def _get_iteration_list(project,context,max_length=15):
    request = context['request']
    show_more = False
    full_list = project.iterations.filter(hidden=False).order_by("-default_iteration", "-end_date")
    
    if len(full_list) <= max_length or (request.GET.get("more","false")=="true"):
        iterations = full_list
        if project.iterations.filter(hidden=True).count() > 0:
            show_more = True
    else:
        show_more = True
        today = tz.today(project.organization)
        backlogs = []
        current = []
        past = []
        future = []
        for iteration in full_list:
            if iteration.default_iteration or iteration.start_date == None or iteration.end_date == None:
                backlogs.append(iteration)
            elif iteration.end_date < today:
                past.append(iteration)
            elif iteration.start_date > today:
                future.append(iteration)
            else:
                current.append(iteration)

        # logger.debug("%d %d %d %d" % (len(backlogs), len(current), len(past), len(future)))
        iterations = []
        iterations.extend(backlogs)            
        more = int( max(2, math.ceil( (max_length - len(iterations))/2)   ) )
        # logger.debug(more)
        iterations.extend(future[-more:])
        iterations.extend(current)        
        iterations.extend(past[:more])
    
    if 'page_type' in context:
        page_type = context['page_type']
    else:
        page_type = ''
    return {"STATIC_URL":context["STATIC_URL"],'iterations':iterations, 'show_more':show_more, 'project':project, 'request':context['request'], 'page_type':page_type}


@register.inclusion_tag("projects/tasks_array.html", takes_context=True)
def tasks_array(context, story):       
    if "project" in context:
        project = context["project"]
    else:
        project = story.project

    if story.task_count > 0:
        counts = story.taskCountsArray()
    else:
        counts = None


    return {'counts':counts, 'story':story, 'project':project}

    

@register.inclusion_tag("projects/popout_iteration_list.html", takes_context=True)
def show_sidebar_iterations(context, project):
    return _get_iteration_list(project,context,15)
    
@register.inclusion_tag("projects/iteration_list.html", takes_context=True)
def show_iterations(context, project):        
    return _get_iteration_list(project,context)

@register.inclusion_tag("projects/projects_tools_popup.html", takes_context=True)
def project_tools_popup(context,user):
    request = context['request']
    show_first_time = not "seen_project_tooltip" in request.COOKIES
    return {'show_first_time':show_first_time,'STATIC_URL':context['STATIC_URL']}
    
@register.inclusion_tag("projects/nothing.html", takes_context=True)
def set_organization(context):
    if 'organization' in context:
        return {}
    if 'project' in context:
        context['organization'] = context['project'].organization
    return {}


@register.inclusion_tag("projects/project_item.html", takes_context=True)
def show_project(context, project):
    return {'project': project, 'request': context['request']}

# @@@ should move these next two as they aren't particularly project-specific

@register.simple_tag
def clear_search_url(request):
    getvars = request.GET.copy()
    if 'search' in getvars:
        del getvars['search']
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path

@register.simple_tag
def persist_getvars(request):
    getvars = request.GET.copy()
    if len(getvars.keys()) > 0:
        return "?%s" % getvars.urlencode()
    return ''

@register.tag(name="notlocked")
def isNotLocked(parser, token):
    tag_name, story = token.split_contents()
    nodelist = parser.parse(('endnotlocked',))
    parser.delete_first_token()
    return NotLockedNode(nodelist, story)

class NotLockedNode(template.Node):
    def __init__(self, nodelist, story):
        self.nodelist = nodelist
        self.story = story
    def render(self, context):
        if not context[self.story].iteration.locked:
            output = self.nodelist.render(context)
            return output
        else:
            return ""



@register.tag(name="scrumproject")
def scrumProject(parser, token):
    tag_name, project = token.split_contents()

    bits = token.split_contents()[1:]
    project = bits[0]
    nodelist_true = parser.parse(('else', 'endscrumproject'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endscrumproject',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()

    return ProjectTypeNode(nodelist_true, nodelist_false, project, Project.PROJECT_TYPE_SCRUM)

@register.tag(name="kanbanproject")
def kanbanProject(parser, token):
    tag_name, project = token.split_contents()

    bits = token.split_contents()[1:]
    project = bits[0]
    nodelist_true = parser.parse(('else', 'endkanbanproject'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endkanbanproject',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()

    return ProjectTypeNode(nodelist_true, nodelist_false, project, Project.PROJECT_TYPE_KANBAN)

@register.tag(name="portfolioproject")
def portfolioProject(parser, token):
    tag_name, project = token.split_contents()

    bits = token.split_contents()[1:]
    project = bits[0]
    nodelist_true = parser.parse(('else', 'endportfolioproject'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endportfolioproject',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()

    return ProjectTypeNode(nodelist_true, nodelist_false, project, Project.PROJECT_TYPE_PORTFOLIO)




@register.tag(name="kanbanize")
def kanbanize(parser, token):
    bits = token.split_contents()[1:]
    if len(bits) > 0:
        project = bits[0]
    else:
        project = None

    nodelist = parser.parse(('endkanbanize',))
    parser.delete_first_token()
    return KanbanizeNode(nodelist, project)


class KanbanizeNode(template.Node):
    def __init__(self, nodelist, project):
        self.nodelist = nodelist        
        self._project = project

    def project(self, context):
        if self._project != None:
            return self._project
        if "project" in context:
            return context["project"]
        return None

    def translate(self, text, terms):
        if text in terms:
            return terms[text]
        return text

    def renderTranslated(self, context, terms):
        result = []
        # logger.debug(self.nodelist)
        for node in self.nodelist:            
            # result.append( node.render(context) )
            # logger.debug(node.__dict__)
            if isinstance(node,template.TextNode): 
                result.append( self.translate(node.render(context), terms) )
            elif isinstance(node,template.VariableNode):
                result.append( node.render(context) )

        # logger.debug(self.nodelist)
        return "".join(result)

    def render(self, context):
        try:
            project = self.project(context)   
            if (project is None) or (project.project_type == Project.PROJECT_TYPE_SCRUM):
                # We're going to pass through the input unchanged.
                return self.nodelist.render(context)
            # Otherwise, we're going to Kanbanify the language.
            if project.project_type == Project.PROJECT_TYPE_KANBAN:
                return self.renderTranslated(context, KANBAN_TERMS)
            else:
                return self.renderTranslated(context, PORTFOLIO_TERMS)

        except:
            traceback.print_exc(file=sys.stdout)
            return "ERROR"




class ProjectTypeNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, project, targetType):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.project = project
        self.targetType = targetType
        # logger.debug("%s %d" % (project, targetType))
    def render(self, context):
        try:   
            if context[self.project].project_type == self.targetType:
                return self.nodelist_true.render(context)
            else:
                return self.nodelist_false.render(context)
        except:
            traceback.print_exc(file=sys.stdout)
            return "ERROR"



@register.tag(name="archived")
def isArchived(parser, token):
    tag_name, project = token.split_contents()
    nodelist = parser.parse(('endarchived',))
    parser.delete_first_token()
    return ArchivedNode(nodelist, project)

class ArchivedNode(template.Node):
    def __init__(self, nodelist, project):
        self.nodelist = nodelist
        self.project = project
    def render(self, context):
        try:
            if not context[self.project].active:
                output = self.nodelist.render(context)
                return output
            else:
                return ""
        except:
            return ""



@register.tag(name="locked")
def istLocked(parser, token):
    tag_name, story = token.split_contents()
    nodelist = parser.parse(('endlocked',))
    parser.delete_first_token()
    return LockedNode(nodelist, story)

class LockedNode(template.Node):
    def __init__(self, nodelist, story):
        self.nodelist = nodelist
        self.story = story
    def render(self, context):
        if context[self.story].iteration.locked:
            output = self.nodelist.render(context)
            return output
        else:
            return ""

@register.tag(name="isadmin")
def isadmin( parser, token):
    tag_name, project = token.split_contents()
    nodelist = parser.parse(('endisadmin',))
    parser.delete_first_token()
    return IsAdminNode(nodelist, project)

class IsAdminNode(template.Node):
    def __init__(self, nodelist, project):
        self.nodelist = nodelist
        self.project = project
    def render(self, context):
        if has_admin_access(context[self.project], context["request"].user):
            output = self.nodelist.render(context)
            return output
        else:
            return ""

@register.tag(name="canchat")
def can_chat(parser, token):
    tag_name, project = token.split_contents()
    nodelist = parser.parse(('endcanchat',))
    parser.delete_first_token()
    return CanEmailNode(nodelist, project)



@register.tag(name="canemail")
def can_email(parser, token):
    tag_name, project = token.split_contents()
    nodelist = parser.parse(('endcanemail',))
    parser.delete_first_token()
    return CanEmailNode(nodelist, project)

class CanEmailNode(template.Node):
    def __init__(self, nodelist, project):
        self.nodelist = nodelist
        self.project = project
    def render(self, context):
        access = True
        if not "project" in context:
            return ""
        
        project = context[self.project]
        if not project:
            return ""
            
        if project.organization:
            access = org_email_limit.increaseAllowed(organization=project.organization)
        else:
            access = personal_email_limit.increaseAllowed(project=project)

        if access:
            output = self.nodelist.render(context)
            return output
        else:
            return ""





@register.tag(name='cancustomstatus')
def can_custom_status(parser, token):
    bits = token.split_contents()[1:]
    project = bits[0]
    nodelist_true = parser.parse(('else', 'endcancustomstatus'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endcancustomstatus',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return CanCustomStatusNode(project, nodelist_true, nodelist_false)



class CanCustomStatusNode(template.Node):
    def __init__(self, project, nodelist_true, nodelist_false=None):
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.project = project

    def __repr__(self):
        return '<CanStatus node>'

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        nodes.extend(self.nodelist_true.get_nodes_by_type(nodetype))
        nodes.extend(self.nodelist_false.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        access = org_custom_status.increaseAllowed(organization=context[self.project].organization)
        if access:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)

    

@register.tag(name="canwrite")
def canwrite( parser, token):
    tag_name, project = token.split_contents()
    nodelist = parser.parse(('endcanwrite',))
    parser.delete_first_token()
    return CanWriteNode(nodelist, project)

class CanWriteNode(template.Node):
    def __init__(self, nodelist, project):
        self.nodelist = nodelist
        self.project = project
    def render(self, context):
        if has_write_access(context[self.project], context["request"].user):
            output = self.nodelist.render(context)
            return output
        else:
            return ""


@register.tag(name="canread")
def canread( parser, token):
    tag_name, project = token.split_contents()
    nodelist = parser.parse(('endcanread',))
    parser.delete_first_token()
    return CanReadNode(nodelist, project)

class CanReadNode(template.Node):
    def __init__(self, nodelist, project):
        self.nodelist = nodelist
        self.project = project
    def render(self, context):
        if has_read_access(context[self.project], context["request"].user):
            output = self.nodelist.render(context)
            return output
        else:
            return ""

@register.filter
def hash(h, key):
    return h[key]
    
@register.filter
def attr(h, key):
    return getattr(h,key)
    
@register.filter
def format_string(val, key):
    return key % val
    
@register.filter(is_safe=True)
def markdown_save(value, args=''):
    try:
        # logger.info("MARKDOWN %s" % value)
        result = formatter(value, "markdown")
        # markdown(value=value)
        # logger.info("RESULT %s" % result)
        return result        
    except:
        return value

@register.filter
def filter_results_by_modelname(search_results, model_name):
    results = []
    for result in search_results:
        if result != None and result.model_name == model_name:
            results.append(result)
    return results

