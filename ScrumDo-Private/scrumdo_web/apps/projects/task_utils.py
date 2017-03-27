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
#
#
# from django.shortcuts import render_to_response, get_object_or_404
# from django.template import RequestContext
# from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotAllowed
# from django.core.urlresolvers import reverse
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.contrib.contenttypes.models import ContentType
# from django.utils.translation import ugettext_lazy as _
#
#
# from django.conf import settings
#
# import re
#
#
from apps.projects.models import Task, Story
# from apps.projects.forms import TaskForm
# from apps.projects.access import *
# import projects.signals as signals
#
# import logging
#
# logger = logging.getLogger(__name__)
#
# @login_required
# def tasks_for_story(request, story_id):
#     story = get_object_or_404( Story, id=story_id )
#     project = story.project
#     read_access_or_403( project, request.user )
#     form = TaskForm(project)
#     return render_to_response("stories/tasks_section.html", {
#       "story": story,
#       "project": project,
#       "task_form": form
#     }, context_instance=RequestContext(request))
#
# # View called via ajax on the iteration or iteration planning pages.  Meant to add one new task
# @login_required
# def create_task( request ):
#     if request.method != "POST":
#         return HttpResponseNotAllowed('Only POST allowed')
#     story_id = request.POST.get("story_id")
#     story = get_object_or_404( Story, id=story_id )
#     assignee = None
#     assignee_id = request.POST.get("assignee")
#     if assignee_id != "-1":
#         assignee = User.objects.get(id=assignee_id)
#
#     write_access_or_403( story.project, request.user )
#     task_text = request.POST.get("summary")
#     logger.debug("Adding task to story %d %s" % (story.id, task_text) )
#
#     if story.tasks.count() > 0:
#         order = story.tasks.order_by("-order")[0].order + 1
#     else:
#         order = 0
#     tags = request.POST.get("tags")
#     task = Task(story=story, summary=task_text, assignee=assignee, order=order, tags=tags)
#     task.save()
#     signals.task_created.send( sender=request, task=task, user=request.user )
#     return HttpResponse("OK")
#
# @login_required
# def set_task_status( request, task_id ):
#     if request.method != "POST":
#         return HttpResponseNotAllowed('Only POST allowed')
#     status = request.POST.get("status", None)
#     if not status:
#         return HttpResponse("FAIL")
#     task = get_object_or_404(Task, id=task_id)
#     write_access_or_403( task.story.project, request.user )
#     task.complete = (status == "done")
#     task.save()
#     signals.task_status_changed.send( sender=request, task=task, user=request.user )
#     return HttpResponse("OK")
#
# @login_required
# def delete_task( request, task_id ):
#     if request.method != "POST":
#         return HttpResponseNotAllowed('Only POST allowed')
#     task = get_object_or_404(Task, id=task_id)
#     write_access_or_403( task.story.project, request.user )
#     story = task.story
#     signals.task_deleted.send( sender=request, task=task, user=request.user )
#     task.sync_queue.clear()
#     task.delete()
#
#     return HttpResponse("OK")
#
# @login_required
# def edit_task(request, task_id):
#     task = get_object_or_404(Task, id=task_id)
#     write_access_or_403( task.story.project, request.user )
#
#     if request.method == "POST":
#         form = TaskForm( task.story.project , request.POST, instance=task)
#         signals.task_updated.send( sender=request, task=task, user=request.user )
#         if form.is_valid():
#             form.save()
#             return HttpResponse("OK")
#         return  HttpResponse("FAIL")
#     else:
#         form = TaskForm( task.story.project , instance=task)
#         return render_to_response("tasks/edit.html", {
#           "task": task,
#           "form": form
#         }, context_instance=RequestContext(request))
#
#
def reorderTask(before_id, after_id, task):
    task_rank_before = 0
    task_rank_after = 999999 # max value of the DB field
    modified = []

    # If there is a story that should be before this one, grab it's rank
    try:
        task_before = Task.objects.get( id=before_id )
        task_rank_before = task_before.__dict__["order"]
    except:
        pass

    # If  there is a story that should be after this one, grab it's rank.
    try:
        task_after = Task.objects.get( id=after_id )
        task_rank_after = task_after.__dict__["order"]
    except:
        pass

    # If the story is between them, don't do anything! "do no harm"
    current_rank = task.order
    if current_rank > task_rank_before and current_rank < task_rank_after:
        return False, modified

    diff = abs(task_rank_after - task_rank_before)
    # logger.debug("Before %d , after %d, diff %d" % (story_rank_after, story_rank_before, diff) )
    try:
        if diff > 1:
            # It fits between them
            # logger.debug(round(diff/2) )
            task.order = round(diff/2) + task_rank_before
            task.save()
            modified.append([task.id, task.order])
            return False, modified
    except:
        pass # do an emergency re-order below if things are falling out of bounds.

    # It doesn't fit!  reorder everything!
    tasks = task.story.tasks.all().order_by("order")

    rank = 100

    for other_task in tasks:
        if other_task == task:
            continue
        if other_task.order == task_rank_after:
            # We should always have a story_rank_after if we get here.
            task.order = rank
            modified.append([task.id, task.order])
            rank += 100
        other_task.order = rank
        modified.append([other_task.id, other_task.order])
        other_task.save()
        rank += 100

    task.save()
    return True, modified
#
# @login_required
# def reorder_task(request, group_slug, task_id):
#     task = get_object_or_404( Task, id=task_id )
#     project = get_object_or_404( Project, slug=group_slug )
#     write_access_or_403(project,request.user)
#     if request.method == 'POST':
#         old_task = task.__dict__.copy()
#
#
#         before_id = request.POST.get("before")
#         after_id = request.POST.get("after")
#
#
#         reorderTask(before_id, after_id, task)
#         return HttpResponse("OK")
#     return  HttpResponse("Fail")
#
