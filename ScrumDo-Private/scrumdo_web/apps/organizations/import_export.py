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



import StringIO
import csv
import re

from xml.dom.minidom import Document, parse
from django.http import HttpResponse

import apps.projects.xlwt as xlwt
ezxf = xlwt.easyxf

from apps.projects.import_export import _getHeaders
from apps.projects.models import Story

import logging
import re

logger = logging.getLogger(__name__)
heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')

def cleanWorksheetName( name ):
    invalidchars = "[]*/\?:=;"
    tmp = name
    for char in invalidchars:
        tmp = tmp.replace(char,"")
    tmp = tmp[:31]
    return tmp

def export_organization( organization, project_ids=None, start_date=None, end_date=None):
    w = xlwt.Workbook(encoding='utf8')
    projects_ws = w.add_sheet( "Workspaces" )
    iterations_ws = w.add_sheet( "Iterations" )

    # category_ws = w.add_sheet( "Categories" )
    # ic_ws = w.add_sheet( "Iterations x Categories" )

    tags_ws = w.add_sheet( "Tags" )
    it_ws = w.add_sheet( "Iterations x Tags" )

    date_xf = xlwt.XFStyle()
    date_xf.num_format_str = 'MM/dd/YYYY'

    _write_headers( projects_ws, [("Workspace",250),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60) ] )
    _write_headers( tags_ws, [("Workspace",250),("Tag",100),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60) ] )
    _write_headers( iterations_ws, [("Workspace",250),("Iteration",100),("Start",80),("End",80),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60),("Starting Points", 60), ("Max Points",60) ] )
    _write_headers( it_ws, [("Workspace",250),("Iteration",100),("Tag",110),("Start",80),("End",80),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60)] )
    # _write_headers( category_ws, [("Workspace",250),("Category",100),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60)] )
    # _write_headers( ic_ws, [("Workspace",250),("Iteration",100),("Category",110),("Start",80),("End",80),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60) ] )


    project_row = 1
    tags_row = 1
    categories_row = 1
    iteration_categories_row = 1
    iterations_row = 1
    iteration_tags_row = 1
    for project in organization.projects.filter(active=True, personal=False):
        if project_ids:
            if project.id not in project_ids:
                continue
        
        story_headers = _getHeaders(project, export_iteration=True)
        project_ws = w.add_sheet(cleanWorksheetName(project.name))

        for idx, header in enumerate(story_headers):
            project_ws.write(0,idx,header[1],heading_xf)
            project_ws.col(idx).width = 37*header[0]

        stories = project.stories.all()
        if start_date:
            stories = stories.filter(iteration__start_date__gte=start_date)
        if end_date:
            stories = stories.filter(iteration__start_date__lte=end_date)
            
        stories = stories.order_by("iteration","rank")

        for idx, story in enumerate(stories):
            for hidx, header in enumerate(story_headers):
                f = header[2]
                project_ws.write(1+idx,hidx, f(story), header[3] )

        
        completed_stories = [story for story in stories if story.status==Story.STATUS_DONE ]
        projects_ws.write(project_row,0, project.name )
        projects_ws.write(project_row,1, len(stories) )
        projects_ws.write(project_row,2, len(completed_stories) )
        projects_ws.write(project_row,3, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
        projects_ws.write(project_row,4, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )

        it_ws.write(iteration_tags_row,0, project.name )
        it_ws.write(iteration_tags_row,5, len(stories) )
        it_ws.write(iteration_tags_row,6, len(completed_stories) )
        it_ws.write(iteration_tags_row,7, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
        it_ws.write(iteration_tags_row,8, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )

        # ic_ws.write(iteration_categories_row,0, project.name )
        # ic_ws.write(iteration_categories_row,5, len(stories) )
        # ic_ws.write(iteration_categories_row,6, len(completed_stories) )
        # ic_ws.write(iteration_categories_row,7, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
        # ic_ws.write(iteration_categories_row,8, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )

        iterations_ws.write(iterations_row,0, project.name )
        iterations_ws.write(iterations_row,4, len(stories) )
        iterations_ws.write(iterations_row,5, len(completed_stories) )
        iterations_ws.write(iterations_row,6, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
        iterations_ws.write(iterations_row,7, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )
        

        tags_ws.write(tags_row,0, project.name )
        tags_ws.write(tags_row,2, len(stories) )
        tags_ws.write(tags_row,3, len(completed_stories) )
        tags_ws.write(tags_row,4, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
        tags_ws.write(tags_row,5, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )

        # category_ws.write(categories_row,0, project.name )
        # category_ws.write(categories_row,2, len(stories) )
        # category_ws.write(categories_row,3, len(completed_stories) )
        # category_ws.write(categories_row,4, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
        # category_ws.write(categories_row,5, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )

        project_row += 1
        tags_row += 1
        categories_row += 1
        iteration_categories_row += 1
        iterations_row += 1
        iteration_tags_row += 1

        tags = {}
        categories = {}


        # Summarize the stories in each tag/category
        for story in stories:
            if story.category in categories:
                categories[story.category].append(story)
            else:
                categories[story.category] = [story]

            for tag in story.story_tags.all():
                tagname = tag.name
                if tagname in tags:
                    tags[tagname].append( story )
                else:
                    tags[tagname] = [story]

        # Write out the tag sheet
        for tag in tags :
            stories = tags[tag]
            completed_stories = [story for story in stories if story.status==Story.STATUS_DONE ]
            tags_ws.write(tags_row,1,tag)
            tags_ws.write(tags_row,2, len(stories) )
            tags_ws.write(tags_row,3, len(completed_stories) )
            tags_ws.write(tags_row,4, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
            tags_ws.write(tags_row,5, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )
            tags_row += 1

        # Write out the category sheet
        # for category in categories:
        #     stories = categories[category]
        #     completed_stories = [story for story in stories if story.status==Story.STATUS_DONE ]
        #     category_ws.write(categories_row,1,category)
        #     category_ws.write(categories_row,2, len(stories) )
        #     category_ws.write(categories_row,3, len(completed_stories) )
        #     category_ws.write(categories_row,4, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
        #     category_ws.write(categories_row,5, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )
        #     categories_row += 1

        iterations = project.iterations.all()

        if start_date:
            iterations = iterations.filter(start_date__gte=start_date)

        if end_date:
            iterations = iterations.filter(start_date__lte=end_date)

            
        for iteration in iterations:
            itags = {}
            icategories = {}
            stories = iteration.stories.all().order_by("rank")

            # Summarize the stories in categories / tags
            for story in stories:
                if story.category in icategories:
                    icategories[story.category].append(story)
                else:
                    icategories[story.category] = [story]
                for tag in story.story_tags.all():
                    tagname = tag.name
                    if tagname in itags:
                        itags[tagname].append( story )
                    else:
                        itags[tagname] = [story]
            completed_stories = [story for story in stories if story.status==Story.STATUS_DONE ]
            iterations_ws.write(iterations_row,1, iteration.name)
            iterations_ws.write(iterations_row,2, iteration.start_date , date_xf)
            iterations_ws.write(iterations_row,3, iteration.end_date , date_xf)
            iterations_ws.write(iterations_row,4, len(stories) )
            iterations_ws.write(iterations_row,5, len(completed_stories) )
            iterations_ws.write(iterations_row,6, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
            iterations_ws.write(iterations_row,7, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )
            iterations_ws.write(iterations_row,8, iteration.starting_points()  )
            iterations_ws.write(iterations_row,9, iteration.max_points() )

            # ic_ws.write(iteration_categories_row,1, iteration.name)
            # ic_ws.write(iteration_categories_row,3, iteration.start_date , date_xf)
            # ic_ws.write(iteration_categories_row,4, iteration.end_date , date_xf)
            # ic_ws.write(iteration_categories_row,5, len(stories) )
            # ic_ws.write(iteration_categories_row,6, len(completed_stories) )
            # ic_ws.write(iteration_categories_row,7, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
            # ic_ws.write(iteration_categories_row,8, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )

            it_ws.write(iteration_tags_row,1, iteration.name)
            it_ws.write(iteration_tags_row,3, iteration.start_date , date_xf)
            it_ws.write(iteration_tags_row,4, iteration.end_date , date_xf)
            it_ws.write(iteration_tags_row,5, len(stories) )
            it_ws.write(iteration_tags_row,6, len(completed_stories) )
            it_ws.write(iteration_tags_row,7, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
            it_ws.write(iteration_tags_row,8, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )
            
            iterations_row += 1
            iteration_tags_row += 1
            iteration_categories_row += 1
            # for category in icategories:
            #     stories = icategories[category]
            #     completed_stories = [story for story in stories if story.status==Story.STATUS_DONE ]
            #     ic_ws.write(iteration_categories_row,2,category)
            #     ic_ws.write(iteration_categories_row,5, len(stories) )
            #     ic_ws.write(iteration_categories_row,6, len(completed_stories) )
            #     ic_ws.write(iteration_categories_row,7, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
            #     ic_ws.write(iteration_categories_row,8, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )
            #     iteration_categories_row += 1

            for tag in itags :
                stories = itags[tag]
                completed_stories = [story for story in stories if story.status==Story.STATUS_DONE ]
                it_ws.write(iteration_tags_row,2,tag)
                it_ws.write(iteration_tags_row,5, len(stories) )
                it_ws.write(iteration_tags_row,6, len(completed_stories) )
                it_ws.write(iteration_tags_row,7, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
                it_ws.write(iteration_tags_row,8, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )
                iteration_tags_row += 1





    return w

def _write_headers(ws, headers):

    for idx,header in enumerate( headers ):
        ws.write(0,idx,header[0],heading_xf)
        ws.col(idx).width = 37*header[1]
