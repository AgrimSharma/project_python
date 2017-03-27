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


from StringIO import StringIO

from apps.projects.models import Iteration
from apps.kanban.models import CellMovement, BoardCell
import apps.kanban.managers as kanban_manager
from apps.kanban.stats.lead import calculateIncrementLeadTime
from xlrd import open_workbook
from apps.projects.models import Story, IterationSentiment, Portfolio
from django.core.files import File
from django.http import HttpResponse
from xml.dom.minidom import Document, parse
from apps.projects.calculation import onDemandCalculateVelocity, calculateEpicStats
from apps.projects.templatetags import projects_tags
from apps.projects.models import Label, ProgramIncrement, Risk, TeamIterationWIPLimit, StoryBlocker, Risk
from apps.organizations.models import Organization
from apps.organizations import tz
from django.db.models import Sum, Q, Count

from django.template import defaultfilters

import apps.html2text as html2text

import cStringIO
import traceback
import logging
import codecs
import xlwt
import sys
import csv
import re
import datetime


logger = logging.getLogger(__name__)
ezxf = xlwt.easyxf


def htmlify(input, project):
    if input is None:
        return None
    res = projects_tags.urlify2(projects_tags.markdown_save(defaultfilters.force_escape(input)))
    if project is not None:
        return projects_tags.link_stories_v2(res, project)
    return res

def exportIteration(iteration, organization_slug=None, format='xls', file_name=None ):
    """ Exports an iteration, format should be xls, xml or csv. """
    logger.info("Exporting iteration %s %d" % (iteration.project.slug, iteration.id) )
    if format.lower() == "xls":
        xlsf = File(StringIO())
        w = _exportExcel( iteration, organization_slug, file_name )
        w.save(xlsf); xlsf.size = xlsf.tell()
    elif format.lower() == "xml":
        doc = _exportXML( iteration, organization_slug, file_name )
        xlsf = File(StringIO(doc.toprettyxml(indent="  ")))
        xlsf.seek(0,2); xlsf.size = xlsf.tell()
    else:
        xlsf = _exportCSV( iteration, organization_slug, file_name )
        xlsf.seek(0,2); xlsf.size = xlsf.tell()


    return xlsf


def importIteration(iteration, file , user):
    """ Imports data to an iteration.  Both updating and creating stories is supported.
        file can be either Excel, XML, or CSV """
    m = re.search('\.(\S+)', file.name)

    if m.group(1).lower() == "xml" :
        return _importXMLIteration(iteration, file, user)
    elif m.group(1).lower() == "xls" :
        return _importExcelIteration(iteration, file, user)
    elif m.group(1).lower() == "xlsx" :
        logger.info("Tried to import xlsx file :(")
#        user.message_set.create(message="Please save your file as an .xls Excel file before importing.")
        return False
    else:
        # Assume CSV, hope for the best.
        return _importCSVIteration(iteration, file, user)

def exportTeamPlanning(iteration, team_project, organization_slug=None, file_name=None ):
    def dateToTimezone(date):
        if organization_slug == None:
            return date
        else:
            org = Organization.objects.get(slug=organization_slug)
            local_time = tz.formatDateTime(date, org, "%Y-%m-%d %I:%M %p")
            return local_time

    def assignedOn(story):
        try:
            return dateToTimezone(feature.assigned_to.filter(project=team_project)[0].assigned)
        except:
            return None

    def story_start_date(story):
        try:
            firstMovement = CellMovement.objects.filter(story_id = story.id, \
                        cell_to__time_type__in = [BoardCell.SETUP_TIME, BoardCell.WORK_TIME]).order_by("created").values_list("created", flat=True)[0]
            return dateToTimezone(firstMovement)
        except:
            return None

    def story_end_date(story):
        try:
            lastMovement = CellMovement.objects.filter(story_id = story.id).order_by("-created")[0]
            if lastMovement.cell_to.time_type == BoardCell.DONE_TIME:
                return dateToTimezone(lastMovement.created)
            else:
                return None
        except:
            return None

    if not file_name:
        file_name = "planning"

    project = iteration.project
    program_incement = ProgramIncrement.objects.get(iteration__project=iteration.project, iteration_id=iteration.id)
    schedules = program_incement.schedule.all().order_by("start_date")
    features = iteration.stories.filter(project_assignments=team_project).prefetch_related('assigned_to')
    child_iterations = []

    #get schedule iteartions for team project
    for schedule in schedules:
        try:
             child_iterations.append({"name": schedule.default_name, "itr": schedule.iterations.filter(project=team_project)[0]})
        except:
            pass

    w = xlwt.Workbook(encoding='utf8', style_compression=2)
    ws = w.add_sheet("%s Planning" % (team_project.name,))
    headers = _getHeaders(project, organization_slug, project_export_mode=False, export_iteration=False, teamplanning_export_mode=True)
    iter_format = ezxf('align: wrap on, vert top')
    wrap_xf = ezxf('align: wrap on, vert top')
    heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
    numeric_xf = ezxf('align: wrap on, vert top, horiz center')
    date_xf = ezxf(num_format_str='yyyy-mm-dd')

    row = 0
    # headers for features
    feature_headers = [(100, "Comitted Features", lambda story: "%s-%s" % (project.prefix, story.local_id), numeric_xf ),\
                        (350, "Summary", lambda story: html2text.html2text(story.summary)[0:2048], wrap_xf),\
                        (160, "Comitted Date",lambda story: assignedOn(story), date_xf),\
                        (160, "Start Date",lambda story: story_start_date(story), date_xf),\
                        (160, "End date",lambda story: story_end_date(story), date_xf)]
    
    # headers for Increment
    increment_header = [(160, "Increments",lambda story: story.iteration.name, wrap_xf)]

    all_headers = feature_headers + increment_header + headers

    for idx,header in enumerate( all_headers ):
        ws.write(row,idx,header[1],heading_xf)
        ws.col(idx).width = 37*header[0]
    
    for feature in features:
        row+=1

        for hidx, header in enumerate(feature_headers):
            f = header[2]
            ws.write(row, hidx, f(feature), header[3] )

        for child_iteration in child_iterations:
            stories = team_project.stories.filter(release=feature, iteration_id=child_iteration['itr'].id) \
                        .select_related("epic", "creator", "project", "cell", "release") \
                        .prefetch_related("story_tags__tag", "assignee", "extra_attributes", "labels", "time_entries", "risks", "blocked_instances").order_by("rank")
            #if len(stories) > 0 :
            ws.write(row, len(feature_headers), child_iteration['name'], increment_header[0][3] )
            
            for idx, story in enumerate(stories):
                row+=1
                for hidx, header in enumerate(headers):
                    f = header[2]
                    ws.write(row, hidx+len(feature_headers+increment_header), f(story), header[3] )
            row+=1
    
    return w

def exportProject(project, organization_slug=None, file_name=None ):
    if not file_name:
        file_name = "project"

    stories = project.stories\
        .exclude(iteration__iteration_type=Iteration.ITERATION_TRASH) \
        .select_related("epic", "creator", "project", "cell", "release") \
        .prefetch_related("story_tags__tag", "assignee", "labels") \
        .order_by("iteration_id", "rank")


    w = xlwt.Workbook(encoding='utf8', style_compression=2)
    ws = w.add_sheet("All Stories")
    headers = _getHeaders(project, organization_slug, project_export_mode=True, export_iteration=True)
    iter_format = ezxf('align: wrap on, vert top')
    wrap_xf = ezxf('align: wrap on, vert top')
    heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
    date_xf = xlwt.XFStyle()
    date_xf.num_format_str = 'MM/dd/YYYY'

    # Write out a header row.
    for idx,header in enumerate(headers):
        ws.write(0,idx,header[1],heading_xf)
        ws.col(idx).width = 37*header[0]
    # Write out the first sheet of all the stories
    idx = -1
    for story in stories:
        idx += 1

        logger.info(idx)
        for hidx, header in enumerate(headers):
            f = header[2]
            ws.write(1+idx, hidx, f(story), header[3] )
    headers = _getHeaders(project, organization_slug, project_export_mode=True)

    # Create the iteration sheet (it gets filled in below the tags sheet)
    iteration_ws = w.add_sheet("Iterations Summary")
    program_iteration_headers = [("Iteration",150),("Start",100),("End",100), ("# All Features", 100), ("Feature identifiers", 260), 
                                    ("Feature WIP Limit",100), ("# Features Committed",100), ("Committed Feature identifiers",260),
                                    ("# Features Started",100), ("Started Feature identifiers",260), ("Features Done",100), 
                                    ("Done Features Identifiers",260) , ("# Outside Dependecies", 100), ("Dependency identifiers", 260),
                                    ("# Blockers", 100), ("Unique Features Blocked", 260), ("# Risks", 100), ("Risks", 260)]
    if project.children.count():
        team_iteration_headers = [("# Stories Started", 100), 
                                    ("Story Identifiers", 260), ('# Stories carried', 100), ('Carried Story identifiers', 260), 
                                    ("# Stories Completed", 100), ("Completed Story identifiers", 260), ("Avg Stories done to date", 100),
                                    ("# Stories Discarded", 100), ("Discarded Story identifiers", 260), ("Child Project Sentiment avg at start", 100), 
                                    ("Child project Sentiment avg at end", 100), ("Average Sentiment", 100), ("Cumulative throughput", 100), 
                                    ("Iteration flow effeciency", 100), ("Avg Iteartion Lead Time", 100), ("Median Iteration Lead time", 100)]
    else:
        team_iteration_headers = [("Average Sentiment", 100), ("Cumulative throughput", 100), ("Iteration flow effeciency", 100), 
                                    ("Avg Iteartion Lead Time", 100), ("Median Iteration Lead time", 100)]

    for idx,header in enumerate( program_iteration_headers + team_iteration_headers ):
        iteration_ws.write(0,idx,header[0],heading_xf)
        iteration_ws.col(idx).width = 37*header[1]


    # Porfolio break down sheet
    if project.portfolio_level is not None or project.project_type == 2:
        _add_portfolio_break_down_sheet(w, project, organization_slug)

    # Create Iteration Features Story Detail Sheet
    _add_iteration_features_story_sheet(w, project, organization_slug)

    epic_ws = w.add_sheet("Collections")
    # for idx,header in enumerate( [("Iteration",150),("Start",100),("End",100),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60),("Starting Points", 60), ("Max Points",60) ] ):
    #     epic_ws.write(0,idx,header[0],heading_xf)
    #     epic_ws.col(idx).width = 37*header[1]

    # Collect tags
    tags = {}
    for story in stories:
        for tag in story.story_tags.all():
            tagname = tag.name
            if tagname in tags:
                tags[tagname].append( story )
            else:
                tags[tagname] = [story]

    # Write out the tags sheet.
    if len( tags ) > 0:
        ws = w.add_sheet( "Tags" )
        for idx,header in enumerate( [("Tag",150),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60)] ):
            ws.write(0,idx,header[0],heading_xf)
            ws.col(idx).width = 37*header[1]
        for idx,tag in enumerate( tags ):
            stories = tags[tag]
            completed_stories = [story for story in stories if story.status==Story.STATUS_DONE ]
            ws.write(idx+1,0,tag)
            ws.write(idx+1,1, len(stories) )
            ws.write(idx+1,2, len(completed_stories) )
            ws.write(idx+1,3, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
            ws.write(idx+1,4, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )
    try:
        epicRow = 0
        epic_ws.col(0).width = 80*37
        epic_ws.col(1).width = 300*37
        epic_ws.col(2).width = 300*37
        epic_ws.col(3).width = 40*37
        for epic in project.epics.filter(archived=False, parent=None).order_by("order"):
            epicRow = _writeEpicLine(epicRow, 0, epic, epic_ws, wrap_xf)
        

    except:
        logger.warn("Could not export epics")
        
    # Write out the blockers sheet.
    blockers = project.blocked_reasons.all().order_by("blocked_date")
    if(len(blockers) > 0):
        blockers_ws = w.add_sheet( "Blockers" )
        for idx,header in enumerate( [("Reason",300),("Resolution",300),("Blocked By",100),("Blocked On",100),("Unblocked By",100),
                ("Unblocked On",100),("#Story",80),("Resolved",80),("External",80),("Duration", 80)] ):
            blockers_ws.write(0,idx,header[0],heading_xf)
            blockers_ws.col(idx).width = 37*header[1]
        blockerRow = 1
        for blocker in blockers:
            blockerRow = _write_blockers_line(blockerRow, 0, blocker, blockers_ws, wrap_xf,date_xf)
    # Write out the Risks sheet.
    risks = Risk.objects.filter(Q(projects=project) | Q(iterations__project=project) | Q(cards__project=project)).order_by("-probability")
    if(len(risks) > 0):
        risks_ws = w.add_sheet( "Risks" )
        for idx,header in enumerate( [("Risk",300),("Severity",300),("Probability",100),("Artifacts",300)] ):
            risks_ws.write(0,idx,header[0],heading_xf)
            risks_ws.col(idx).width = 37*header[1]
        risksRow = 1
        for risk in risks:
            risksRow = _write_risks_line(risksRow, 0, risk, risks_ws, wrap_xf,date_xf)
    # Write data to the iteration sheet, plus create one sheet per iteration.
    for itIdx, iteration in enumerate(project.iterations.exclude(iteration_type=Iteration.ITERATION_TRASH).order_by("start_date")):
        prefix = iteration.project.prefix
        iteration_stories = iteration.stories.all().order_by("rank")
        completed_stories = iteration_stories.filter(cell__time_type=3)
        commited_stories = iteration_stories.filter(project_assignments__isnull=False).distinct() 
        started_stories = iteration_stories.filter(cell__time_type=2)
        dependent_stories = Story.objects.filter(dependent_stories__iteration = iteration).exclude(project = iteration.project).distinct()
        blockers = StoryBlocker.objects.values('card__local_id').filter(card__iteration_id = iteration.id).distinct()
        risks = Risk.objects.filter(Q(iterations=iteration) | Q(cards__iteration=iteration) | Q(cards__project__in = iteration.project.children.all()) |\
                Q(iterations__program_increment_schedule__increment__iteration=iteration) ).distinct()
        
        flow_efficiency = kanban_manager.get_iteration_flow_efficiency(iteration)
        cumulative_throughput = kanban_manager.get_iteration_cumulative_throughput(iteration)
        # lead_time = calculateIncrementLeadTime(iteration.project, iteration.id)

        try:
            wip_limit = TeamIterationWIPLimit.objects.get(team=project, iteration_id=iteration.id)
        except TeamIterationWIPLimit.DoesNotExist:
            wip_limit = None

        try:
            sentiments = IterationSentiment.objects.filter(iteration=iteration)
            avg_sentiments = len(sentiments)/ (project.children.all().count()+1)
        except:
            avg_sentiments = 0
        
        if project.children.count():
            team_stories = Story.objects.filter(iteration__program_increment_schedule__increment__iteration=iteration).order_by("rank").distinct()
            team_stories_started = team_stories.filter(cell__time_type__in=[1, 2, 3])
            team_stories_completed = team_stories.filter(cell__time_type=3)
            child_iterations = Iteration.objects.filter(program_increment_schedule__increment__iteration=iteration).order_by("start_date")
            child_iterations_completed = child_iterations.filter(end_date__lt = datetime.date.today())
            discarded_stories = kanban_manager.discardedStories(child_iterations)
            try:
                child_sentimentds_start = IterationSentiment.objects.filter(project__in = project.children.all(), iteration=child_iterations[0])
                child_sentimentds_end = IterationSentiment.objects.filter(project__in = project.children.all(), iteration=child_iterations[len(child_iterations)-1])
                child_avg_sentimentds_start = len(child_sentimentds_start)/project.children.all().count()
                child_avg_sentimentds_end = len(child_sentimentds_end)/project.children.all().count()
            except:
                child_avg_sentimentds_start = 0
                child_avg_sentimentds_end = 0

            if iteration.start_date is not None and iteration.end_date is not None:
                previous_iterations = iteration.project.iterations.filter( start_date__lt = iteration.start_date)
                days_gone = (max(iteration.end_date, datetime.date.today()) - iteration.start_date)
                
                stories_wip = CellMovement.objects.filter(related_iteration__program_increment_schedule__increment__iteration=iteration,\
                                            cell_to__time_type__in = [1, 2]).extra({'date_created': "date(created)"})\
                                            .values('story_id').distinct().aggregate(count = Count('created'))
                stories_avg_wip = stories_wip['count']/days_gone.days 

                previous_iterations_stories = CellMovement.objects.filter(related_iteration__program_increment_schedule__increment__iteration__in=previous_iterations).values('story__local_id').distinct()
                current_iteration_stories = CellMovement.objects.filter(related_iteration__program_increment_schedule__increment__iteration=iteration ,\
                                            story__iteration__program_increment_schedule__increment__iteration=iteration).values('story__local_id').distinct()
                stories_carried =  [s for s in previous_iterations_stories if s in current_iteration_stories]

                avg_stories_completed = len(team_stories_completed)/len(child_iterations_completed) if len(child_iterations_completed) is not 0 else 0
            else:
                avg_stories_completed = 0
                stories_avg_wip = 0
                stories_carried = []
        
        iteration_ws.write(itIdx+1, 0, iteration.name )
        iteration_ws.write(itIdx+1, 1, iteration.start_date , date_xf)
        iteration_ws.write(itIdx+1, 2, iteration.end_date , date_xf)
        iteration_ws.write(itIdx+1, 3, len(iteration_stories) )
        iteration_ws.write(itIdx+1, 4,  ", ".join(["%s-%d" % (prefix, story.local_id) for story in iteration_stories]), wrap_xf)
        iteration_ws.write(itIdx+1, 5, wip_limit.featureLimit if wip_limit is not None else 0)
        iteration_ws.write(itIdx+1, 6, len(commited_stories) )
        iteration_ws.write(itIdx+1, 7,  ", ".join(["%s-%d" % (prefix, story.local_id) for story in commited_stories]), wrap_xf)
        
        iteration_ws.write(itIdx+1, 8, len(started_stories) )
        iteration_ws.write(itIdx+1, 9, ", ".join(["%s-%d" % (prefix, story.local_id) for story in started_stories]), wrap_xf )
        iteration_ws.write(itIdx+1, 10, len(completed_stories) )
        iteration_ws.write(itIdx+1, 11, ", ".join(["%s-%d" % (prefix, story.local_id) for story in completed_stories]), wrap_xf )
        iteration_ws.write(itIdx+1, 12, len(dependent_stories) )
        iteration_ws.write(itIdx+1, 13, ", ".join(["%s-%d" % (story.project.prefix, story.local_id) for story in dependent_stories]), wrap_xf )
        iteration_ws.write(itIdx+1, 14, len(blockers) )
        iteration_ws.write(itIdx+1, 15, ", ".join(["%s-%d" % (prefix, b['card__local_id']) for b in blockers]), wrap_xf )
        iteration_ws.write(itIdx+1, 16, len(risks) )
        iteration_ws.write(itIdx+1, 17, ", ".join([ risk.description for risk in risks]), wrap_xf )
        
        # team level data 
        if project.children.count():
            iteration_ws.write(itIdx+1, 18, len(team_stories_started) )
            iteration_ws.write(itIdx+1, 19, ", ".join(["%s-%d" % (story.project.prefix, story.local_id) for story in team_stories_started]), wrap_xf )
            iteration_ws.write(itIdx+1, 20, len(stories_carried) )
            iteration_ws.write(itIdx+1, 21, ", ".join(["%s-%d" % (prefix, story['story__local_id']) for story in stories_carried]), wrap_xf )
            iteration_ws.write(itIdx+1, 22, len(team_stories_completed) )
            iteration_ws.write(itIdx+1, 23, ", ".join(["%s-%d" % (story.project.prefix, story.local_id) for story in team_stories_completed]), wrap_xf )
            iteration_ws.write(itIdx+1, 24, avg_stories_completed )
            iteration_ws.write(itIdx+1, 25, len(discarded_stories) )
            iteration_ws.write(itIdx+1, 26, ", ".join(["%s-%d" % (story.project.prefix, story.local_id) for story in discarded_stories]), wrap_xf )
            iteration_ws.write(itIdx+1, 27, child_avg_sentimentds_start )
            iteration_ws.write(itIdx+1, 28, child_avg_sentimentds_end )
            iteration_ws.write(itIdx+1, 29, avg_sentiments )
            iteration_ws.write(itIdx+1, 30, cumulative_throughput )
            iteration_ws.write(itIdx+1, 31, "%.2f" % flow_efficiency )
            # iteration_ws.write(itIdx+1, 32, lead_time["mean"] )
            # iteration_ws.write(itIdx+1, 33, lead_time["median"] )
            
        else:
            iteration_ws.write(itIdx+1, 18, avg_sentiments )
            iteration_ws.write(itIdx+1, 19, cumulative_throughput )
            iteration_ws.write(itIdx+1, 20, "%.2f" % flow_efficiency )
            # iteration_ws.write(itIdx+1, 21, lead_time["mean"] )
            # iteration_ws.write(itIdx+1, 22, lead_time["median"] )

        if not iteration.hidden:
            ws = w.add_sheet( cleanWorksheetName(iteration.name) )

            for idx,header in enumerate(headers):
                ws.write(0,idx,header[1],heading_xf)
                ws.col(idx).width = 37*header[0]
            row = 1 
            for idx, story in enumerate(iteration_stories):
                for hidx, header in enumerate(headers):
                    f = header[2]
                    ws.write(row, hidx, f(story), header[3] )
                row += 1
                count = 1
                for task in story.tasks.all().order_by("status","order"):
                    ws.write(row, 1, "Task #%d" % count)                    
                    ws.write(row, 2, task.summary)
                    ws.write(row, 4, task.estimated_minutes)
                    ws.write(row, 5, task.status_text())
                    if task.assignee:
                        ws.write(row, 6, task.assignee.username )
                    ws.write(row,8,task.tags_cache)
                    count += 1
                    row += 1
    # w.save(response)
    return w
    
def _write_blockers_line(row, indent, blocker, blockers_ws, wrap_xf, date_xf):
    indent_xf = ezxf('align: wrap on, vert top, indent %d' % indent)
    resolved = "yes" if blocker.resolved == True else "no"
    external = "yes" if blocker.external == True else "no"
    blocked_by = blocker.blocker.username if blocker.blocker is not None else ""
    unblocked_by = blocker.unblocker.username if blocker.unblocker is not None else ""
    
    blockers_ws.write(row,0,blocker.reason,indent_xf)
    blockers_ws.write(row,1,blocker.resolution,wrap_xf)
    blockers_ws.write(row,2,blocked_by,wrap_xf)
    blockers_ws.write(row,3,blocker.blocked_date,date_xf)
    blockers_ws.write(row,4,unblocked_by,wrap_xf)
    blockers_ws.write(row,5,blocker.unblocked_date,date_xf)
    blockers_ws.write(row,6,"%s-%d" % (blocker.card.project.prefix, blocker.card.local_id),wrap_xf)
    blockers_ws.write(row,7,resolved,wrap_xf)
    blockers_ws.write(row,8,external,wrap_xf)
    blockers_ws.write(row,9,"%d days" % blocker.age,wrap_xf)
    row += 1
    return row
    
def _write_risks_line(row, indent, risk, risks_ws, wrap_xf, date_xf):
    indent_xf = ezxf('align: wrap on, vert top, indent %d' % indent)
    risks_ws.write(row, 0, risk.description,indent_xf)
    risks_ws.write(row, 1, _get_risk_severity(risk), indent_xf)
    risks_ws.write(row, 2, risk.probability)
    risks_ws.write(row, 3, _get_risk_artifacts(risk), indent_xf)
    row += 1
    return row

def _get_risk_severity(risk):
    risk_types = [ getattr(risk.portfolio,"risk_type_%d" % index) for index in range(1, 8) if getattr(risk.portfolio, "risk_type_%d" % index) != '']
    risk_severity = [ getattr(risk,"severity_%d" % index) for index in range(1, 8) if getattr(risk, "severity_%d" % index) != 0]
    r = [];
    severity_lable = ["", "Low", "Medium", "High", "", "Urgent"]
    for idx, type in enumerate(risk_types):
        try:
            r.append("%s: %s" % (type, severity_lable[risk_severity[idx]]))
        except:
            pass

    return ", ".join(r)

def _get_risk_artifacts(risk):
    cards = []
    iterations = []
    projects = []
    for card in risk.cards.all().select_related('project'):
        cards.append("%s-%s %s" % (card.project.prefix, card.local_id, html2text.html2text(card.summary)[0:2048]))
    
    for iteration in risk.iterations.all().select_related('project'):
        iterations.append("%s/%s" % (iteration.project.name, iteration.name))
    
    for project in risk.projects.all():
        projects.append("%s" % project.name)
    
    artifacts = cards+iterations+projects

    return ", ".join(artifacts)

def _writeEpicLine(row, indent, epic, epic_ws, wrap_xf):
    indent_xf = ezxf('align: wrap on, vert top, indent %d' % indent)
    epic_ws.write(row,0,"#E%d" % epic.local_id,indent_xf)
    epic_ws.write(row,1,epic.summary,wrap_xf)
    epic_ws.write(row,2,epic.detail,wrap_xf)
    epic_ws.write(row,3,epic.points,wrap_xf)
    row += 1
    indent_formats = {}  # key = indent amount, value = ezxf value
    for story in epic.stories.all().order_by("rank"):
        if (indent+1) not in indent_formats:
            indent_formats[indent+1] = ezxf('align: wrap on, vert top, indent %d' % (indent+1))

        indent_xf = indent_formats[indent+1]  #ezxf('align: wrap on, vert top, indent %d' % (indent+1) )

        epic_ws.write(row,0,"%s-%d" % (story.project.prefix, story.local_id), indent_xf)
        epic_ws.write(row,1,html2text.html2text(story.summary),wrap_xf)
        epic_ws.write(row,2,html2text.html2text(story.detail),wrap_xf)
        epic_ws.write(row,3,story.points,wrap_xf)
        row += 1
    
    for child in epic.children.all():
        row = _writeEpicLine(row, indent+1, child, epic_ws,wrap_xf)        
        
    return row

def _add_portfolio_break_down_sheet(w, project, organization_slug):
    ws = w.add_sheet( "Portfolio Work Break Down" );
    heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
    wrap_xf = ezxf('align: wrap on, vert top')
    numeric_xf = ezxf('align: wrap on, vert top, horiz right')
    date_xf = ezxf(num_format_str='yyyy-mm-dd')

    if project.portfolio_level is not None:
        portfolio = project.portfolio_level.portfolio
    else:
        portfolio = Portfolio.objects.get(root = project)
    levels = portfolio.levels.all()
    root = portfolio.root
    epics = root.stories.all().order_by("rank").prefetch_related("project", "project__portfolio_level")
    
    row = 0
    headers = [("Portfolio Epics", 150), ("Capabilities", 150), ("Features", 100), ("Stories", 150)]

    ws.write(row, 0, root.work_item_name, heading_xf)
    ws.col(0).width = 37*150

    for idx, level in enumerate(levels):
        ws.write(row, idx+1, level.projects.all()[0].work_item_name, heading_xf)
        ws.col(idx+1).width = 37*150
    
    row +=2
    for epic in epics:
        col = 0
        ws.write(row, col, "%s-%d %s" % (epic.project.prefix, epic.local_id, html2text.html2text(epic.summary)) ,wrap_xf)
        row = _add_level_stories(ws, epic, row, levels)
        row +=1
        

def _add_level_stories(ws, epic, row, levels): 
    wrap_xf = ezxf('align: wrap on, vert top')
    numeric_xf = ezxf('align: wrap on, vert top, horiz right')
    stories = Story.objects.filter(release = epic, project__portfolio_level__in = levels).\
                            order_by("rank").prefetch_related("project", "project__portfolio_level")
    try:
        c = epic.project.portfolio_level.level_number
    except:
        c = 0
        ws.write(row, c+1, len(stories) ,numeric_xf)
    
    for story in stories:
        col = story.project.portfolio_level.level_number
        row +=1
        ws.write(row, col, "%s-%d %s" % (story.project.prefix, story.local_id, html2text.html2text(story.summary)) ,wrap_xf)
        children = Story.objects.filter(release = story).order_by("rank")
        if len(levels) > col+1:
            ws.write(row, col+1, len(children) ,numeric_xf)
        if len(children):
            row = _add_level_stories(ws, story, row, levels)
            row +=1
    return row
    

def _add_iteration_features_story_sheet(w, project, organization_slug):
    ws = w.add_sheet( "Iteration-Feature-Story Detail" );
    heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
    wrap_xf = ezxf('align: wrap on, vert top')
    numeric_xf = ezxf('align: wrap on, vert top, horiz right')
    date_xf = ezxf(num_format_str='yyyy-mm-dd')

    def dateToTimezone(date):
        if organization_slug == None:
            return date
        else:
            org = Organization.objects.get(slug=organization_slug)
            local_time = tz.formatDateTime(date, org, "%Y-%m-%d %I:%M %p")
            return local_time

    def story_start_date(story):
        try:
            firstMovement = CellMovement.objects.filter(story_id = story.id, \
                        cell_to__time_type__in = [BoardCell.SETUP_TIME, BoardCell.WORK_TIME]).order_by("created").values_list("created", flat=True)[0]
            return dateToTimezone(firstMovement)
        except:
            return None

    def story_end_date(story):
        try:
            lastMovement = CellMovement.objects.filter(story_id = story.id).order_by("-created")[0]
            if lastMovement.cell_to.time_type == BoardCell.DONE_TIME:
                return dateToTimezone(lastMovement.created)
            else:
                return None
        except:
            return None
    
    def assignedOn(story):
        try:
            all_assignees = story.assigned_to.all()
            return ", ".join(["%s - %s" % (s.project.name, dateToTimezone(s.assigned)) for s in all_assignees])
        except:
            return None

    headers = _getHeaders(project, organization_slug, project_export_mode=False, export_iteration=False, teamplanning_export_mode=True)
    
    # headers for Iteration
    iteration_header = [(160, "Iteration",lambda iteration: iteration.name, wrap_xf),
                        (160, "Start Date",lambda iteration: iteration.start_date, date_xf),\
                        (160, "End date",lambda iteration: iteration.end_date, date_xf)]

    # headers for features
    feature_headers = [(100, "Features", lambda story: "%s-%s" % (project.prefix, story.local_id), numeric_xf ),\
                        (350, "Summary", lambda story: html2text.html2text(story.summary)[0:2048], wrap_xf),\
                        (160, "Comitted Date",lambda story: assignedOn(story), wrap_xf),\
                        (160, "Start Date",lambda story: story_start_date(story), date_xf),\
                        (160, "End date",lambda story: story_end_date(story), date_xf)]

    all_headers = iteration_header + feature_headers + headers
    
    row = 0
    for idx,header in enumerate( all_headers ):
        ws.write(row,idx,header[1],heading_xf)
        ws.col(idx).width = 37*header[0]
    row += 1
    iterations = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK, hidden=0)
    for iteration in iterations:
                
        for idx, header in enumerate(iteration_header):
            f = header[2]
            ws.write(row, idx, f(iteration), header[3] )
        row += 1

        for feature in iteration.stories.all():
            for idx, header in enumerate(feature_headers):
                f = header[2]
                ws.write(row, len(iteration_header)+idx, f(feature), header[3] )

            stories = Story.objects.filter(release=feature) \
                    .select_related("epic", "creator", "project", "cell", "release") \
                    .prefetch_related("story_tags__tag", "assignee", "extra_attributes", "labels", "time_entries", "risks", "blocked_instances").order_by("rank")
            
            for idx, story in enumerate(stories):
                row+=1
                for hidx, header in enumerate(headers):
                    f = header[2]
                    ws.write(row, hidx+len(feature_headers+iteration_header), f(story), header[3] )
            row+=1            


def _getHeaders(project, organization_slug=None, project_export_mode=False, export_iteration=False , teamplanning_export_mode=False):
    """Returns an array of tupples with info on columns.
        (target width, title, function to get the data from a story, excel output format, function to assign the value to a story)
    """
    # There's some excel-specific data mixed in here that doesn't entirely fit, but I'm leaving it for now.
    wrap_xf = ezxf('align: wrap on, vert top')
    numeric_xf = ezxf('align: wrap on, vert top, horiz right')
    date_xf = ezxf(num_format_str='yyyy-mm-dd')

    # Some methods to define how imported field values are set in a story.
    # This is one place we can do any logic to clean up the data.
    def intOrString( value ):
        try:
            if int(value) == float(value):
                return int(float(value))
        except:
            pass
        return value
    def setNull(story,value):
        pass
    def setId(story,value):
        pass
    def setSummary(story,value):
        story.summary = htmlify(unicode(value), project)
    def setDetail(story,value):
        story.detail = htmlify(unicode(value), project)
    def setMinutes(story, value):
        try:
            story.estimated_minutes = int(value)
        except:
            pass


    def setPoints(story,value):
        try:
            story.points="%g" % value
        except (ValueError, TypeError):
            if value == "":
                story.points = "?"
            else:
                story.points = str(value)
                
    def setTimeCriticality(story, value):
        try:
            story.time_criticality="%g" % value
        except (ValueError, TypeError):
            if value == "":
                story.time_criticality = "?"
            else:
                story.time_criticality = str(value)               
                
    def setRiskReduction(story, value):
        try:
            story.risk_reduction="%g" % value
        except (ValueError, TypeError):
            if value == "":
                story.risk_reduction = "?"
            else:
                story.risk_reduction = str(value)
    
    def formatPoints(points):
        if points.isdigit():
            return int(points) 
        else:
            try:
                float(points)
                return float(points)
            except:
                return points
    
    def dateToTimezone(date):
        if organization_slug == None:
            return date
        else:
            org = Organization.objects.get(slug=organization_slug)
            local_time = tz.formatDateTime(date, org, "%Y-%m-%d %I:%M %p")
            return local_time
            
    def dueDateToTimezone(date):
        if organization_slug == None or date is None:
            return date
        else:
            org = Organization.objects.get(slug=organization_slug)
            local_time = tz.formatDateTime(date, org, "%Y-%m-%d %I:%M %p")
            return local_time
            
    def setDueDate(story, value):
        if value == "":
            story.due_date = None
        else:
            try:
                story.due_date = tz.toFormat(value)
            except:
                story.due_date = None
        
    
    def setStatus(story,value):
        try:
            story.status = story.project.reverseStatus(value)
            if story.status == -1:
                story.status = 1
        except:
            story.status = 1
            
    def setAssignee(story,value):
        story.assignees = value

    def setRank(story,value):
        try:
            story.rank = int(value)
        except:
            story.rank = story.iteration.stories.count()
    def setExtra1(story,value):
        story.extra_1 = htmlify(unicode(value), project)
    def setExtra2(story,value):
        story.extra_2 = htmlify(unicode(value), project)
    def setExtra3(story,value):
        story.extra_3 = htmlify(unicode(value), project)
    def setTags( story, value ):
        story.tags = unicode(value)
    def setEpics( story, value ):
        epic_id = unicode(value)
        m = re.search("[0-9]+$", epic_id)
        if m is None:
            return
        epic_number = int(m.group(0))
        story.epic = story.project.epics.get(local_id=epic_number)

    def setBusinessValue(story, value):
        story.business_value = value if value != '' else 0
    def setLabels(story, value):
        story.save()
        story.labels.clear()
        for name in value.split(","):
            try:
                label = project.labels.get(name=name.strip())
                story.labels.add(label)
            except Label.DoesNotExist:
                pass

    def setCellName(story, value):
        try:
            cell = story.project.boardCells.filter(full_label=value)[0]
            story.cell = cell
        except:
            pass

    def getCellName(story):
        if story.cell:
            return story.cell.full_label
        return ''

    def setTasks(story,value):
        story.storyTasks = unicode(value)

    def story_tasks_count(story):
        return story.tasks.all().count()

    def storyPrefix(story):
        return "%s-%s" % (story.project.prefix, story.local_id)

    def story_cumulative_hours(story):
        try:
            minutes = story.time_entries.aggregate(total = Sum('minutes_spent'))['total']
            return minutes_to_hour(minutes)
        except:
            return 0
    
    def minutes_to_hour(minutes):
        return '{:02d}:{:02d}'.format(*divmod(minutes, 60))

    def hours_to_days(hours):
        return '{:02d} days {:02d} hours'.format(*divmod(int(hours), 24))
    
    def story_start_date(story):
        try:
            firstMovement = CellMovement.objects.filter(story_id = story.id, \
                        cell_to__time_type__in = [BoardCell.SETUP_TIME, BoardCell.WORK_TIME]).order_by("created").values_list("created", flat=True)[0]
            return dateToTimezone(firstMovement)
        except:
            return None

    def story_end_date(story):
        try:
            lastMovement = CellMovement.objects.filter(story_id = story.id).order_by("-created")[0]
            if lastMovement.cell_to.time_type == BoardCell.DONE_TIME:
                return dateToTimezone(lastMovement.created)
            else:
                return None
        except:
            return None

    def story_risks(story):
        return unicode(",".join(str(risk.description) for risk in story.risks.all()))

    def story_blockers(story):
        return unicode(",".join(str(blocker.reason) for blocker in story.blocked_instances.all()))

    def story_aging(story):
        try:
            aging_info = tuple(kanban_manager.get_aging_info(story))
            info = unicode(",".join("%s: %s" % (d[0].full_label, hours_to_days(d[1])) for i,d in enumerate(aging_info)))
            return info
        except:
            return None
    def iteration_history(story):
        try:
            movement = CellMovement.objects.filter(Q(story=story), ~Q(related_iteration_id=story.iteration.id)).order_by("-created")\
                        .select_related("related_iteration")[0]
            return "%s/%s" % (movement.related_iteration.project.name,movement.related_iteration.name)
        except:
            return None


    if teamplanning_export_mode:
        headers = [ (100,"User Story", lambda story: storyPrefix(story) ,numeric_xf, setId), 
               (350,"Summary", lambda story: html2text.html2text(story.summary)[0:2048],wrap_xf, setSummary),
               (160, "Start Date", lambda story: story_start_date(story), date_xf), 
               (160, "End date", lambda story: story_end_date(story), date_xf),
               (160, "Iteration history", lambda story: iteration_history(story), wrap_xf), 
               (50,"Points", lambda story: formatPoints(story.points), numeric_xf, setPoints),
               (65,"Estimated Minutes", lambda story: story.estimated_minutes , numeric_xf, setMinutes),
               (65,"Business Value", lambda story: story.business_value , numeric_xf, setBusinessValue),
               (75,"Time Criticality", lambda story: story.time_criticality , numeric_xf, setTimeCriticality),
               (75,"Risk Reduction / Opportunity Enablement", lambda story: story.risk_reduction , numeric_xf, setRiskReduction),
               (70,"Cell", getCellName, wrap_xf, setCellName),
               (50,"Rank", lambda story: story.rank,numeric_xf ,  setRank),
               (80,"Tags", lambda story: story.tags,wrap_xf,  setTags),
               (120,"Collections", lambda story: story.full_epic_label(),wrap_xf,  setEpics),
               (80,"Labels", lambda story: ",".join([label.name for label in story.labels.all()]), wrap_xf, setLabels),
               (50, "Number of tasks", lambda story: story_tasks_count(story), numeric_xf),
               (350,"Tasks", lambda story: story.storyTasks, wrap_xf, setTasks) ,
               (50, "Cumulative hours", lambda story: story_cumulative_hours(story), numeric_xf, None) ,
               (350, "Aging", lambda story: story_aging(story), wrap_xf),
               (350, "Risks", lambda story: story_risks(story), wrap_xf),
               (350, "Blockers", lambda story: story_blockers(story), wrap_xf),
               (110,"Due Date", lambda story: dueDateToTimezone(story.due_date), date_xf, setDueDate) ,
               (100,"Created", lambda story: dateToTimezone(story.created), date_xf, setNull) ]

    elif project_export_mode:
        headers = [ (50,"Story ID", lambda story: storyPrefix(story) ,numeric_xf, setId),
               (350,"Summary", lambda story: html2text.html2text(story.summary)[0:2048],wrap_xf, setSummary),
               (300,"Detail", lambda story: html2text.html2text(story.detail)[0:2048] ,wrap_xf, setDetail),
               (50,"Points", lambda story: formatPoints(story.points), numeric_xf, setPoints),
               (65,"Estimated Minutes", lambda story: story.estimated_minutes , numeric_xf, setMinutes),
               (65,"Business Value", lambda story: story.business_value , numeric_xf, setBusinessValue),
               (75,"Time Criticality", lambda story: story.time_criticality , numeric_xf, setTimeCriticality),
               (75,"Risk Reduction / Opportunity Enablement", lambda story: story.risk_reduction , numeric_xf, setRiskReduction),
               (70,"Cell", getCellName, wrap_xf, setCellName),
               (50,"Rank", lambda story: story.rank,numeric_xf ,  setRank),
               (80,"Tags", lambda story: story.tags,wrap_xf,  setTags),
               (120,"Collections", lambda story: story.full_epic_label(),wrap_xf,  setEpics),
               (80,"Labels", lambda story: ",".join([label.name for label in story.labels.all()]), wrap_xf, setLabels),
               (350,"Tasks", lambda story: story.storyTasks, wrap_xf, setTasks) ,
               (110,"Due Date", lambda story: dueDateToTimezone(story.due_date), date_xf, setDueDate) ,
               (100,"Created", lambda story: dateToTimezone(story.created), date_xf, setNull) ,
               (100,"Modified", lambda story: dateToTimezone(story.modified), date_xf, setNull) ]

    else: # Iteration mode
        headers = [ (50,"Story ID", lambda story: storyPrefix(story) ,numeric_xf, setId),
               (350,"Summary", lambda story: html2text.html2text(story.summary)[0:2048],wrap_xf, setSummary),
               (300,"Detail", lambda story: html2text.html2text(story.detail)[0:2048] ,wrap_xf, setDetail),
               (50,"Points", lambda story: formatPoints(story.points), numeric_xf, setPoints),
               (65,"Estimated Minutes", lambda story: story.estimated_minutes , numeric_xf, setMinutes),
               (65,"Business Value", lambda story: story.business_value , numeric_xf, setBusinessValue),
               (75,"Time Criticality", lambda story: story.time_criticality , numeric_xf, setTimeCriticality),
               (75,"Risk Reduction / Opportunity Enablement", lambda story: story.risk_reduction , numeric_xf, setRiskReduction),
               (70,"Cell", getCellName, wrap_xf, setCellName),
               (50,"Rank", lambda story: story.rank,numeric_xf ,  setRank),
               (80,"Tags", lambda story: story.tags,wrap_xf,  setTags),
               (80,"Collections", lambda story: story.epic_label,wrap_xf,  setEpics),
               (80,"Labels", lambda story: ",".join([label.name for label in story.labels.all()]), wrap_xf, setLabels),
               (350,"Tasks", lambda story: story.storyTasks, wrap_xf, setTasks),
               (110,"Due Date", lambda story: dueDateToTimezone(story.due_date), date_xf, setDueDate) ,
               (100,"Created", lambda story: dateToTimezone(story.created), date_xf, setNull) ,
               (100,"Modified", lambda story: dateToTimezone(story.modified), date_xf, setNull)               
                ]




    # And some optional columns that depend on project settings:
    if export_iteration:
        headers.insert(0, (70,"Iteration", lambda story:  story.iteration.name ,wrap_xf, setNull))

    headers.insert(6, (70,"Assignee", lambda story:  story.assignees_cache ,wrap_xf, setAssignee))

    if project.use_extra_1:
        headers.append((200,project.extra_1_label, lambda story: html2text.html2text(story.extra_1),wrap_xf,  setExtra1))

    if project.use_extra_2:
        headers.append( (200,project.extra_2_label, lambda story: html2text.html2text(story.extra_2),wrap_xf,  setExtra2) )

    if project.use_extra_3:
        headers.append( (200,project.extra_3_label, lambda story: html2text.html2text(story.extra_3),wrap_xf,  setExtra3) )

    return headers


def _exportExcel( iteration, organization_slug, file_name=None ):
    """ Exports the stories in an iteration as an excel sheet. """
    if not file_name:
        file_name = "iteration"
    #response = HttpResponse( mimetype="Application/vnd.ms-excel")
    #response['Content-Disposition'] = 'attachment; filename=%s.xls'%file_name
    stories = iteration.stories.all().order_by("rank")
    w = xlwt.Workbook()
    ws = w.add_sheet('Iteration Export')
    headers = _getHeaders(iteration.project, organization_slug)
    heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')

    # Write out a header row.
    for idx,header in enumerate(headers):
        # logger.debug(header[1])
        ws.write(0,idx,header[1],heading_xf)
        ws.col(idx).width = 37*header[0]

    # Write out all the data.
    for idx, story in enumerate(stories):

        for hidx, header in enumerate(headers):
            f = header[2]
            # logger.debug(f(story))            
            ws.write(1+idx,hidx, f(story), header[3] )


    return w



def _exportXML( iteration, file_name=None  ):
    """ Exports the stories in an iteration as XML """
    if not file_name:
        file_name = "iteration"
    stories = iteration.stories.all().order_by("rank")
    doc = Document()
    iteration_node = doc.createElement("iteration")
    doc.appendChild(iteration_node)

    headers = _getHeaders(iteration.project)

    for idx, story in enumerate(stories):
        row = []
        story_node = doc.createElement("story")
        iteration_node.appendChild( story_node )
        for hidx, header in enumerate(headers):
            f = header[2]
            story_node.setAttribute(_toXMLNodeName(header[1]), unicode(f(story)).replace("\n"," ").replace("\r",""))
            # TODO (Future Enhancement): There's a bug in the minidom implementation that doesn't convert newlines to their entities inside attributes,
            #      and there's no good work-around I can find without monkey patching minidom itself.
            #      We should generally recommend people stick to excel or CSV files.


    return doc


    #response = HttpResponse(, mimetype="text/xml")
    #response['Content-Disposition'] = 'attachment; filename=%s.xml'%file_name
    #return response

def _toXMLNodeName( name ):
    return re.sub('[^a-zA-Z0-9_-]',"",name.replace(" ","_").lower())

def _exportCSV( iteration, file_name=None ):
    """ Exports the stories in an iteration as CSV """
    if not file_name:
        file_name = "iteration"
    #response =  HttpResponse( mimetype="text/csv")
    #response['Content-Disposition'] = 'attachment; filename=%s.csv'%file_name
    stories = iteration.stories.all().order_by("rank")

    xlsf = File(StringIO())
    writer = UnicodeWriter(xlsf)
    #csv.writer(response, delimiter=',' ,  quoting=csv.QUOTE_ALL, escapechar='\\')

    headers = _getHeaders(iteration.project)
    row = []
    for idx,header in enumerate(headers):
        row.append(header[1])

    writer.writerow( row )

    for idx, story in enumerate(stories):
        row = []
        for hidx, header in enumerate(headers):
            f = header[2]
            row.append( f(story) )
        writer.writerow( row )

    return xlsf

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([ unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)



def _importData( data, iteration , user):
    """ Imports data from a python object to an iteration.
        The idea here is that all the import mechanisms (CSV, XML, XLS) can translate
        their input to a python object hierarchy, and they all can pass that off to
        this method to do the actual import so we only have to write the sync-code
        once.

        data should be an array of python dict like objects, where the keys are
        the names from the getHeaders call, and the values are the user's input.
        """
    imported = 0
    failed = 0
    for row in data:
        if _importSingleRow(row, iteration, user):
            imported += 1
        else:
            failed += 1
    logger.info("Imported %d records, failed on %d" % (imported,failed))
#    if failed == 0:
#        user.message_set.create(message="Imported %d records." % imported )
#    else:
#        user.message_set.create(message="Imported %d records, failed on %d" % (imported,failed))
    onDemandCalculateVelocity(iteration.project)
    
    return (imported,failed)


def _getFieldFromImportData( data, field_name ):
    """ This method returns a value for a given field.  Generally, it's used for translating user data
        into values suitable for a story.  """
    # TODO (Future Enhancement) - Right now, we do only exact matches, we might want a more intelligent
    #        search scheme to accept a wider variety of import formats.
    #        For instance, case insensitive, ignore whitespace, whatever.

    rv = data.get(field_name)
    if( rv == None ):
        # If we didn't find one, lets try an alternative naming...
        rv = data.get( _toXMLNodeName(field_name) )

    return rv;


def _importSingleRow( row, iteration, user):
    try:
        local_id = _getFieldFromImportData(row, "Story ID")
        local_id_prefix = re.search("([A-Z,a-z,0-9]{2})-([0-9]+)", str(local_id))
        if local_id_prefix != None: 
            local_id = local_id_prefix.group(2)

        story = None
        if local_id != None:
            try:
                story = Story.objects.get( project=iteration.project, local_id=int(local_id) )
                logger.debug("Found story to update (%d)" % int(local_id) )
            except:
                # Story didn't exist already, so we'll be making a new one
                # This is a little dangerous if there was a story id set, since we'll now be ignoring
                # that and that might not be what the user intended.
                story = Story(project=iteration.project, iteration=iteration, local_id=iteration.project.getNextId() )
                story.creator = user
                logger.debug("Creating new story to import into.")


        # A user could move rows from one iteration export to another, so set it here. It'll probably be rare to actually happen.
        story.iteration = iteration

        headers = _getHeaders(iteration.project)
        for header in headers:
            value = _getFieldFromImportData(row, header[1])
            if value != None:
                try:
                    f = header[4]  # This should be a method capable of setting the property
                    f(story, value)
                    # logger.debug("Setting %s to %s" % (header[1],value) )
                except:
                    traceback.print_exc(file=sys.stdout)    
                    logger.info("Failed to set %s to %s, ignoring." % (header[1], unicode(value) ) )
        story.resetCounts()  # This auto saves...
        if story.epic is not None:
            calculateEpicStats(story.epic)
        # story.save()
        return True
    except Exception as e:
        logger.debug("Failed to import a record. %s" % e)
        return False



def _importExcelIteration(iteration, file, user):
    try:
        workbook = open_workbook(file_contents=file.read())
    except:
        workbook = open_workbook(file_contents=file.read(), encoding_override="cp1252")
    sheet = workbook.sheets()[0]
    count = 0
    headers = _getHeaders( iteration.project )
    import_data = []
    for row in range(1,sheet.nrows):
        rowData = {}
        count += 1
        for col in range(sheet.ncols):
            header = sheet.cell(0,col).value
            val = sheet.cell(row,col).value
            rowData[header] = val
        import_data.append( rowData )
    logger.info("Found %d rows in an excel sheet " % count)
    return _importData( import_data , iteration, user)



def _importXMLIteration(iteration, file, user):
    xml = parse( file )
    import_data = []
    count = 0
    for story_node in xml.getElementsByTagName("story"):
        attrs = story_node.attributes
        import_row = {}
        for attrName in attrs.keys():
            import_row[attrName] = attrs[attrName].nodeValue
        count += 1
        import_data.append(import_row)
    logger.info("Found %d rows in an XML file" % count)
    _importData( import_data, iteration, user )




def _importCSVIteration(iteration, file, user):
    import_file = csv.reader( file , delimiter=',' ,  quoting=csv.QUOTE_ALL, escapechar='\\' )
    try:
        headers = None
        import_data = []
        count = 0
        for row in import_file:
            try:
                if headers == None:
                    headers = row
                else:
                    import_row = {}
                    for idx,header in enumerate(headers):
                        import_row[header] = row[idx]
                        #logger.debug("Import field %s as %s"%(header, row[idx]) )
                    count += 1
                    import_data.append( import_row )
            except:
                logger.warn("Failed to import CSV row")
    except:
        logger.info("Failed to import CSV file")
    logger.info("Found %d rows in a CSV file" % count)
    _importData( import_data, iteration, user )

def cleanWorksheetName( name ):
    invalidchars = "[]*/\?:=;"
    tmp = name
    for char in invalidchars:
        tmp = tmp.replace(char,"")
    tmp = tmp[:31]
    
    return tmp



def exportEpicsSheet( project, file_name=None ):
    if not file_name:
        file_name = "project"
    response = HttpResponse(content_type="Application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s.xls'%file_name 
    stories = project.stories.all().order_by("iteration","rank")
    w = xlwt.Workbook(encoding='utf8')
    iter_format = ezxf('align: wrap on, vert top')
    wrap_xf = ezxf('align: wrap on, vert top')
    heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
    date_xf = xlwt.XFStyle()
    date_xf.num_format_str = 'MM/dd/YYYY'
    epic_ws = w.add_sheet("Collections")
    
    statuses = list(project.status_choices())

    epic_ws.write(0,0,"Collection #")
    epic_ws.write(0,1,"Summary")
    epic_ws.write(0,2,"Detail")
    epic_ws.write(0,3,"Collection Estimate")
    epic_ws.write(0,4,"Stories")
    epic_ws.write(0,5,"Stories Sized")

    i = 6
    for status in statuses:
        epic_ws.write( 0, i , status[1] )
        i += 1


    epicRow=1
    for epic in project.epics.filter(archived=False, parent=None).order_by("order"):
       (epicRow, story_count, story_sized, points_by_status ) = _writeEpicWorksheetLine(epicRow, 0, epic, epic_ws, wrap_xf, statuses)

    w.save(response)
    return response

def _writeEpicWorksheetLine(row, indent, epic, epic_ws, wrap_xf, statuses):
    indent_xf = ezxf('align: wrap on, vert top, indent %d' % indent)
    epic_ws.write(row,0,"#E%d" % epic.local_id,indent_xf)
    epic_ws.write(row,1,epic.summary,wrap_xf)
    epic_ws.write(row,2,epic.detail,wrap_xf)
    epic_ws.write(row,3,epic.points,wrap_xf)
    thisRow = row
    row += 1
    
    story_count = 0
    story_sized = 0
    points_by_status = [0] * 10
    
    for child in epic.children.all():
        (row, astory_count, astory_sized, apoints_by_status ) = _writeEpicWorksheetLine(row, indent+1, child, epic_ws,wrap_xf, statuses)        
        story_count += astory_count
        story_sized += astory_sized        
        for i in range(10):
            points_by_status[i] += apoints_by_status[i]
        # points_todo += apoints_todo
        # points_doing += apoints_doing
        # points_reviewing += apoints_reviewing
        # points_done += apoints_done
    
    for story in epic.stories.all().order_by("rank"):        
        # indent_xf = ezxf('align: wrap on, vert top, indent %d' % (indent+1) )
        story_count += 1
        if story.points != "?":
            story_sized += 1
            
        points_by_status[story.status-1] += story.points_value()
        # if story.status < 4:
        #     points_todo += story.points_value()
        # elif story.status < 7:
        #     points_doing += story.points_value()
        # elif story.status < 10:
        #     points_reviewing += story.points_value()
        # else:
        #     points_done += story.points_value()
    
    epic_ws.write( thisRow, 4, story_count)    
    epic_ws.write( thisRow, 5, story_sized)                
    
    i = 6
    for status in statuses:
        epic_ws.write( thisRow, i , points_by_status[ status[0] - 1] )
        i += 1
    
        
    # epic_ws.write( thisRow, 6, points_todo)
    # epic_ws.write( thisRow, 7, points_doing)
    # epic_ws.write( thisRow, 8, points_reviewing)
    # epic_ws.write( thisRow, 9, points_done)

    return (row, story_count, story_sized, points_by_status )
