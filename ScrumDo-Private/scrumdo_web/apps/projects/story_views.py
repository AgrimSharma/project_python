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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA
import urllib
import re

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages

from haystack.query import SearchQuerySet

from apps.projects.forms import *
from apps.projects.access import *
from apps.projects.managers import reorderStory

import apps.kanban.managers as kanban_managers
from . import tasks

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


STORIES_PER_PAGE = 300

logger = logging.getLogger(__name__)



@login_required
def epic_permalink(request, epic_id):
    """A permalink for a story.  No matter where it goes this should work"""
    epic = get_object_or_404(Epic, id=epic_id)
    read_access_or_403(epic.project, request.user)
    return HttpResponseRedirect(reverse('planning_tool', kwargs={'group_slug':epic.project.slug}))



@login_required
def story_permalink(request, story_id):
    """A permalink for a story.  No matter where it goes this should work"""
    story = get_object_or_404(Story, id=story_id)
    read_access_or_403(story.project, request.user)
    iteration = story.iteration

    if iteration.iteration_type == Iteration.ITERATION_WORK:
        # Usually, go to the board.
        # /iteration/:iterationid/story/:storyid
        return HttpResponseRedirect("%s#/iteration/%d/board/story/%d" % (
            reverse("project_app", kwargs={'project_slug': story.project.slug}),
            iteration.id,
            story.id))
    else:
        # Backlog / Archive goes to the story list.
        url = '{}#/iteration/{}/cards?story_{}'.format(
            reverse('project_app', kwargs={'project_slug':story.project.slug}), story.iteration.id, story.id)
        return HttpResponseRedirect(url)








def _calculate_rank(iteration, general_rank):
    """ calculates the rank a new story should have for a project based off of 3 general rankings.
    0=top, 1=middle, 2=bottom
    TODO (Improvement) - I'd like to re-think how ranking is done for both initial and adjustments of ranks.
    """
    try:
        stories = iteration.stories.all().order_by("rank")
        story_count = len(stories)
        if story_count == 0:
            return 500

        if(general_rank == 0):  # top
            return int(stories[0].rank / 2)

        if(general_rank == 1):  # middle
            if story_count < 2:
                return 500
            s1_rank = stories[int(story_count / 2) - 1].rank
            s2_rank = stories[int(story_count / 2)].rank
            return int((s1_rank + s2_rank) / 2)

        return stories[story_count - 1].rank + 500
    except:
        return 100




def _getStoriesWithTextSearch(iteration, text_search, order_by, tags_search,
                              category, only_assigned, user, backlog_mode, status, assignee):
    search_results = SearchQuerySet().filter(
        project_id=iteration.project.id).filter(
        iteration_id=iteration.id).filter(
            content=text_search).models(Story).order_by(order_by).load_all()
    if tags_search != "":
        search_results = search_results.filter(tags=tags_search)
    if category != "":
        search_results = search_results.filter(category=category)
    if only_assigned:
        search_results = search_results.filter(user_id=user.id)
    if status:
        search_results = search_results.filter(status=status)
    if assignee:
        if assignee == "unassigned":
            search_results = search_results.filter(assignee__id="")
        else:
            get_user = User.objects.get(pk=assignee)
            search_results = search_results.filter(assignee=get_user)
    stories = [result.object for result in search_results]
    return stories


def _getStoriesNoTextSearch(iteration, order_by, tags_search, category,
                            only_assigned, user, paged, page, backlog_mode, status, assignee):
    tags_list = re.split('[, ]+', tags_search)

    stories = iteration.stories

    if order_by != "numeric_points":
        stories = stories.order_by(order_by)
    else:
        # Tried a few things here... CAST(points as SIGNED) in the order_by clause would have been preferred, but I couldn't get that through
        # the ORM.  Secondary, I tried craeting a custom column assigned to that, but it caused the query to fail.  The 0+string is a bit
        # of a mysql specific hack to convert a string to a number.
        stories = stories.extra(
            select={
                'numeric_points': '0+points'}).order_by(order_by)

    if tags_search:
        stories = stories.filter(
            story_tags__tag__name__in=tags_list).distinct().order_by(order_by)
    if only_assigned:
        stories = stories.filter(assignee=user)
    if category:
        stories = stories.filter(category=category)
    if status:
        stories = stories.filter(status=status)
    if assignee:
        if assignee == "unassigned":
            stories = stories.filter(assignee=None)
        else:
            get_user = User.objects.get(pk=assignee)
            stories = stories.filter(assignee=get_user)

    if backlog_mode:
        stories = stories.filter(epic=None)

    stories = stories.select_related(
        'project',
        'project__organization',
        'project__organization__subscription',
        'iteration',
    )

    if paged:
        paginator = Paginator(stories, STORIES_PER_PAGE)
        page_obj = paginator.page(page)
        has_next = page_obj.has_next()
        stories = page_obj.object_list
    else:
        has_next = False

    return (has_next, stories)




def _handleAddStoryInternal(form, project, request):
    story = form.save(commit=False)
    story.local_id = project.getNextId()
    story.project = project
    story.creator = request.user
    iteration_id = request.POST.get("iteration", None)
    epic_id = request.POST.get("epic", None)
    cell_id = request.POST.get("cellId", None)
    logger.debug("cell id: %s" % cell_id)

    if iteration_id is not None:
        iteration = get_object_or_404(Iteration, id=iteration_id)
        if iteration.project != project:
            raise PermissionDenied()  # Shenanigans!
        story.iteration = iteration
    else:
        story.iteration = project.get_default_iteration()

    if epic_id is not None and epic_id != "":
        epic = Epic.objects.get(id=epic_id)
        if epic.project != project:
            raise PermissionDenied()  # Shenanigans!
        story.epic = epic

    if request.POST.get("category_name") != "":
        category_name = request.POST.get("category_name", "")
        category_name = category_name.replace(",", "").strip()
        category_name = category_name[:50]
        if not category_name in project.getCategoryList():
            project.categories = "%s, %s" % (project.categories, category_name)
            if len(project.categories) <= 1024:
                project.save()
            else:
                messages.success(request, "Too many categories")
        story.category = category_name

    # story.rank = _calculate_rank( story.iteration, relativePosition )

    # story.skip_haystack = True
    story.rank = 0
    story.save()
    story.assignees = request.POST.get("assignee", None)
    story.resetCounts()

    relativePosition = int(request.POST.get("relativePosition", "0"))
    (modifiedOrder, othersModified) = setRelativeRank(
        story, iteration, relativePosition)
    story.save()

    if cell_id is not None and cell_id != "":
        cell = project.boardCells.get(id=cell_id)
        kanban_managers.moveStoryOntoCell(story, cell, request.user)
        # story.cell = cell

    if settings.USE_QUEUE:
        tasks.sendStoryAddedSignals.apply_async((story.id, request.user.id), countdown=3)
    else:
        tasks.sendStoryAddedSignals(story.id, request.user.id)

    return (story, modifiedOrder, othersModified)


def handleAddStory(request, project, *args, **kwargs):
    """ Handles the add story form.
        Various views have an add story form on them.  This method handles that,
        and returns a new StoryForm object the view can use. """
    if request.method == "POST" and request.POST.get("action") == "addStory":
        form = AddStoryForm(
            project,
            request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            (story,
             modifiedOrder,
             othersModified) = _handleAddStoryInternal(form,
                                                       project,
                                                       request)
        else:
            return form

    picked_iteration = kwargs.get('picked_iteration')
    return AddStoryForm(project, initial={'iteration': picked_iteration})


@login_required
def planning_tool(request, group_slug):
    url = reverse("planning_tool", kwargs={'group_slug': group_slug})
    return HttpResponseRedirect(url)


def story_list(request, organization_slug):
    organization = Organization.objects.get(slug=organization_slug)
    stories = Story.objects.filter(project__organization=organization)
    return render_to_response("projects/story_list.html", {
        "stories": stories,
        "organization": organization
    }, context_instance=RequestContext(request))
