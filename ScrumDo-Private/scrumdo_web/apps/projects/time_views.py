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

from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

import apps.organizations.tz as tz
from apps.organizations.models import Organization
from apps.projects.models import Project, Iteration, Story, Epic, Task, TimeEntry
from apps.account.templatetags.account_tags import realname
from templatetags.time_entry_tags import minutes_to_hours


import xlwt
import logging
import datetime

ezxf = xlwt.easyxf


logger = logging.getLogger(__name__)


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(n)


@login_required
def export_time(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasReadAccess(request.user):
        raise PermissionDenied()
    if not organization.subscription.planTimeTracking():
        raise PermissionDenied("Time tracking not enabled.")

    file_name = "time"

    bow, eow = _get_time_range(request, organization)

    response = HttpResponse(content_type="Application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s.xls'%file_name
    w = xlwt.Workbook(encoding='utf8')

    # detail_ws = w.add_sheet( "Timesheet" )
    project_sheet = w.add_sheet( "By Project" )
    entries_ws = w.add_sheet( "Raw Entries" )

    row = 0
    entries_ws.write(row, 0, "Minutes")
    entries_ws.write(row, 1, "Person")
    entries_ws.write(row, 2, "Date")
    entries_ws.write(row, 3, "Notes")
    entries_ws.write(row, 4, "Project")
    entries_ws.write(row, 5, "Iteration")
    entries_ws.write(row, 6, "Story Number")
    entries_ws.write(row, 7, "Story Summary")
    entries_ws.write(row, 8, "Story Points")
    entries_ws.write(row, 9, "Story Status")
    entries_ws.write(row, 10, "Story Category")
    entries_ws.write(row, 11, "Task")
    entries_ws.write(row, 12, "Epic")
    entries_ws.write(row, 13, "Story Detail")
    entries_ws.write(row, 14, "Extra 1")
    entries_ws.write(row, 15, "Extra 2")
    entries_ws.write(row, 16, "Extra 3")

    # detail_ws.col(0).width  = 37*300
    entries_ws.col(3).width = 37*550
    entries_ws.col(4).width = 37*250
    entries_ws.col(7).width = 37*550
    entries_ws.col(11).width = 37*250
    entries_ws.col(13).width = 55*250
    entries_ws.col(14).width = 55*250
    entries_ws.col(15).width = 55*250
    entries_ws.col(16).width = 55*250

    wrap_format = ezxf('align: wrap on, vert top')
    date_xf = xlwt.XFStyle()
    date_xf.num_format_str = 'MM/dd/YYYY'
    
    if organization.hasStaffAccess(request.user):
        entries = TimeEntry.objects.filter(organization=organization, date__gte=bow, date__lte=eow).order_by("date")
    else:
        entries = TimeEntry.objects.filter(user=request.user, organization=organization, date__gte=bow, date__lte=eow).order_by("date")
        
    projects = {}
    for entry in entries:
        row+=1
        if entry.project.slug in projects:
            projects[entry.project.slug] += [entry]
        else:
            projects[entry.project.slug] = [entry]
        entries_ws.write(row, 1, realname(entry.user).encode("utf8"))
        entries_ws.write(row, 2, entry.date, date_xf)
        entries_ws.write(row, 3, entry.notes, wrap_format)
        entries_ws.write(row, 4, entry.project.name, wrap_format)


        if entry.iteration:
            entries_ws.write(row,5,entry.iteration.name,wrap_format)
        story = entry.story
        if story:
            entries_ws.write(row,6, "%s-%d" % (entry.project.prefix, story.local_id))
            entries_ws.write(row, 7, strip_tags(story.summary), wrap_format)
            entries_ws.write(row, 13, strip_tags(story.detail), wrap_format)

            entries_ws.write(row,8,int(story.points) if story.points.isdigit() else story.points,wrap_format)
            entries_ws.write(row,9,story.statusText(),wrap_format)
            entries_ws.write(row,10,story.category,wrap_format)
            if story.epic: entries_ws.write(row,12,story.epic.short_name())
            entries_ws.write(row,14,story.extra_1,wrap_format)
            entries_ws.write(row,15,story.extra_2,wrap_format)
            entries_ws.write(row,16,story.extra_3,wrap_format)

        if entry.task:
            entries_ws.write(row,11,entry.task.summary,wrap_format)

        entries_ws.write(row,0,entry.minutes_spent)

    c = 2
    for single_date in daterange(bow,eow):
        project_sheet.write(0,c,single_date,date_xf)
        c+=1

    row = 1
    for project_slug in projects.iterkeys():
        project_sheet.write(row,0,projects[project_slug][0].project.name)
        row += 1
        total = 0
        people = {}
        full_names = {}
        for entry in projects[project_slug]:
            un = entry.user.username
            total += entry.minutes_spent
            if un in people:
                people[un] += [entry]
            else:
                full_names[un] = realname(entry.user)
                people[un] = [entry]
        for person in people.iterkeys():
            minutes = reduce(lambda t,e: t+e.minutes_spent, people[person],0)
            project_sheet.write(row,1,full_names[person])

            c=2
            for single_date in daterange(bow,eow):
                project_sheet.write(row,c,minutes_to_hours(reduce(lambda t,e: t + (e.minutes_spent if e.date== single_date else 0), people[person],0)))
                c+=1
            project_sheet.write(row,c,minutes_to_hours(minutes))
            row += 1
        project_sheet.write(row,c,minutes_to_hours(total))
        row += 2



    w.save(response)
    return response

def _get_time_range(request, organization):
    if request.GET.get("eow"):
        eow =  datetime.datetime.strptime(request.GET.get("eow"),"%m/%d/%Y").date()
    else:
        eow = tz.today(organization)
        eow += datetime.timedelta(days=-eow.weekday() + organization.end_of_week)

    if request.GET.get("bow"):
        bow =  datetime.datetime.strptime(request.GET.get("bow"),"%m/%d/%Y").date()
    else:
        bow = eow + datetime.timedelta(days=-6)
    logger.debug("%s-%s" % (bow,eow))
    return (bow, eow)
