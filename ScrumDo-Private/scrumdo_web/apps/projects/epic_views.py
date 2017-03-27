# # ScrumDo - Agile/Scrum story management web application
# # Copyright (C) 2010 - 2016 ScrumDo LLC
# #
# # This software is free software; you can redistribute it and/or
# # modify it under the terms of the GNU Lesser General Public
# # License as published by the Free Software Foundation; either
# # version 2.1 of the License, or (at your option) any later version.
# #
# # This software is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# # Lesser General Public License for more details.
# #
# # You should have received a copy (See file COPYING) of the GNU Lesser General Public
# # License along with this library;  if not, write to the Free Software
# # Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# from django.shortcuts import render_to_response, get_object_or_404
# from django.template import RequestContext
# from django.core.urlresolvers import reverse
# from django.template import defaultfilters
# from django.http import HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# import projects.signals as signals
#
# from models import *
# from apps.projects.access import *
# from apps.projects.templatetags import projects_tags
# from apps.account.templatetags.account_tags import hover_username
# from util import organizationOrNone
# import activities.utils as utils
# from forms import *
#
# from apps.attachments.models import Attachment
#
# import json
# import logging
#
# from apps.projects.calculation import onDemandCalculateVelocity
#
# from django.conf import settings
#
#
# logger = logging.getLogger(__name__)
#
#
# def htmlify(input):
#     if input is None:
#         return None
#     return projects_tags.urlify2(projects_tags.markdown_save(defaultfilters.force_escape(input)))
#
#
# @login_required
# def epics(request, group_slug):
#     url = "%s/epics"  % reverse("planning_tool", kwargs={'group_slug':group_slug})
#     return HttpResponseRedirect(url)
#     # project = get_object_or_404( Project, slug=group_slug )
#     # archived = request.GET.get("show_archived","false") == "true"
#     # read_access_or_403(project, request.user )
#     # organization = organizationOrNone(project)
#
#     # return render_to_response("projects/epics.html",
#     #                           {
#     #                             "project":project,
#     #                             "organization":organization
#     #                           },
#     #                           context_instance=RequestContext(request))
#
# @login_required
# def epics_report(request, group_slug):
#     project = get_object_or_404(Project, slug=group_slug)
#     read_access_or_403(project, request.user)
#     try:
#         expanded_ids = [int(epic_id) for epic_id in request.COOKIES.get('DISPLAY_EPICS','').split("-")]
#     except ValueError: expanded_ids = []
#     return render_to_response('projects/epics_report.html',{
#         "expanded_epics": project.epics.filter(id__in=expanded_ids), 'expanded': expanded_ids,
#         "root_epics": project.epics.filter(parent=None), "project": project
#     }, context_instance=RequestContext(request))
#
#
# @login_required
# def epic_permalink(request, group_slug, epic_id):
#     project = get_object_or_404( Project, slug=group_slug )
#     read_access_or_403(project, request.user )
#     epic = get_object_or_404(Epic, id=epic_id)
#     return HttpResponseRedirect( "%s#epic_id=%d" %(reverse("epics", kwargs={'group_slug':project.slug}), epic.id) )
#
# # @login_required
# # def bulk_edit(request, group_slug):
# #     project = get_object_or_404( Project, slug=group_slug )
# #     write_access_or_403(project, request.user )
# #     changes = json.loads(request.POST.get("changes"))
# #     for change in changes:
# #         epic_id = change["epic"]
# #         epic = Epic.objects.get(id=epic_id)
# #         if epic.project_id != project.id:
# #             raise PermissionDenied()
# #         if "order" in change:
# #             epic.order = change["order"]
# #         if "parent_id" in change:
# #             if change["parent_id"] == None:
# #                 parent = None
# #             else:
# #                 parent = Epic.objects.get(id=change["parent_id"])
# #                 if parent.project_id != project.id:
# #                     raise PermissionDenied()
# #             epic.parent = parent
# #         epic.save()
# #
# #     return HttpResponse("OK")
#
# @login_required
# def stories_in_epics_json(request, group_slug):
#     project = get_object_or_404( Project, slug=group_slug )
#     # organization = organizationOrNone(project)
#     read_access_or_403(project, request.user )
#     story_id = request.GET.get("story_id",None)
#
#     if story_id is None:
#         stories = project.stories.filter(epic__id=request.GET.get("epic_id"))
#     else:
#         stories = [project.stories.get(id=story_id)]
#     stories_data = []
#     fields = ['id',"local_id","points","status","summary","detail","tags","category","rank","assignees_cache"]
#     for story in stories:
#         s = {}
#         for field in fields:
#             s[field] = getattr(story,field)
#         if story.assignee:
#             s["assignee"] = ""
#             for assignee in story.assignees:
#                 s["assignee"] += "%s " % hover_username(assignee)
#         i = story.iteration
#         s["points_label"] = story.getPointsLabel()
#         s["iteration"] = {'id':i.id, 'name':i.name, 'url':reverse('iteration', kwargs={'group_slug':project.slug,'iteration_id':i.id})}
#         if story.epic:
#             s["epic_id"] = story.epic.id
#         s["edit_url"] = reverse("story_form",kwargs={'group_slug':project.slug, 'story_id':story.id})
#         s["summaryHtml"] = htmlify(story.summary)
#         s["detailHtml"] = htmlify(story.detail)
#
#         tags = []
#         for tag in story.story_tags_array():
#             tags.append({'name':tag,'url':reverse('tag_detail',kwargs={'group_slug':project.slug,'tag_name':tag})})
#         s["tags"] = tags
#
#         stories_data.append(s)
#
#     return HttpResponse(json.dumps(stories_data), mimetype="application/json")
#
#
#
#
#
# @login_required
# def epics_json(request, group_slug):
#     project = get_object_or_404( Project, slug=group_slug )
#     read_access_or_403(project, request.user )
#     epic_id = request.GET.get("epic_id",None)
#     if(epic_id is None):
#         epics = project.epics.all()
#         if request.GET.get("archived") == "false":
#             epics = epics.filter(archived=False)
#         epics = epics.order_by("order")
#     else:
#         try:
#             epics = [ project.epics.get(id=epic_id) ]
#         except:
#             return HttpResponse("[]")
#
#     epics_data = []
#     fields = ['id',"local_id","summary","detail","points", "order"]
#     for epic in epics:
#         e = {}
#         epics_data.append(e)
#         for field in fields:
#             e[field] = getattr(epic,field)
#         e["parent_id"] = epic.parent.id if epic.parent else -1
#         e["archived"] = bool(epic.archived)
#         e["detailHtml"] = htmlify( epic.detail )
#
#     return HttpResponse(json.dumps(epics_data), mimetype="application/json")
#
#
# @login_required
# def reorder_epic( request, group_slug, epic_id):
#     epic = get_object_or_404( Epic, id=epic_id )
#     project = get_object_or_404( Project, slug=group_slug )
#     if epic.project != project:
#         raise PermissionDenied()
#     write_access_or_403(project,request.user)
#     if request.method == 'POST':
#         rank = 0
#         target_iteration = request.POST["iteration"]
#
#         try:
#             iteration = get_object_or_404( Iteration, id=target_iteration )
#         except:
#             iteration = story.iteration
#
#         if request.POST.get("action","") == "reorder" :
#             reorderEpic(epic, request.POST.get("before"), request.POST.get("after"), iteration)
#
#         epic.iteration = iteration
#         epic.save()
#
#         return HttpResponse("OK")
#     return HttpResponse("Fail")
#
#
# def _deleteEpic(epic ):
#     logger.debug("Deleing epic " + epic.summary)
#
#     for story in epic.stories.all():
#         story.epic = epic.parent
#         story.save()
#
#     for child in epic.children.all():
#         child.parent = None
#         child.save()
#     epic.delete()
#
#
#
# @login_required
# def delete_epic(request,  epic_id):
#     epic = get_object_or_404(Epic, id=epic_id)
#     project = epic.project
#     write_access_or_403(project, request.user)
#     if request.method == 'POST': # If the form has been submitted...
#         _deleteEpic( epic )
#         signals.epic_deleted.send( sender=request, epic=epic, user=request.user )
#         return HttpResponse("OK")
#
#
# @login_required
# def edit_epic(request,  epic_id, template_name="projects/epic_edit.html", extra_context={}):
#     epic = get_object_or_404(Epic, id=epic_id)
#     project = epic.project
#     write_access_or_403(project, request.user)
#     attachments = Attachment.objects.attachments_for_object(epic)
#
#     if request.method == 'POST': # If the form has been submitted...
#         old_epic = epic.__dict__.copy()
#         form = EpicForm( project, request.POST, request.FILES, instance=epic)
#         if form.is_valid(): # All validation rules pass
#             epic = form.save()
#             diffs = utils.model_differences(old_epic, epic.__dict__, dicts=True)
#             signals.epic_updated.send( sender=request, epic=epic, diffs=diffs, user=request.user )
#             for file in request.FILES.getlist('file'):
#                 content_type = ContentType.objects.get_for_model(epic)
#                 try:
#                     attachment = Attachment(
#                                content_type = content_type,
#                                object_id = epic.id,
#                                creator = request.user,
#                                attachment_file = file
#                                )
#                     attachment.save()
#                 except Exception:
#                     pass
#             onDemandCalculateVelocity(project)
#             return HttpResponse("OK")
#     else:
#         form = EpicForm( project,  instance=epic)
#
#     return render_to_response(template_name, {
#         "form":form,
#         "epic":epic,
#         "organization": project.organization,
#         "project":project,
#         "attachments": attachments,
#       }, context_instance=RequestContext(request))
#
# @login_required
# def create_epic_form(request, group_slug):
#     project = get_object_or_404(Project, slug=group_slug)
#     write_access_or_403(project,request.user)
#     form = EpicForm( project )
#     is_attachments = False
#     if "attachments" in settings.INSTALLED_APPS:
#         is_attachments = True
#     print is_attachments
#     return render_to_response("projects/epic_create.html", {
#         "form":form,
#         "project":project,
#         "is_attachments": is_attachments,
#       }, context_instance=RequestContext(request))
#
#
# @login_required
# def ajax_add_epic(request, group_slug):
#     project = get_object_or_404(Project, slug=group_slug)
#     write_access_or_403(project,request.user)
#     if request.method == 'POST': # If the form has been submitted...
#         form = EpicForm( project, request.POST, request.FILES)
#         if form.is_valid(): # All validation rules pass
#             epic = form.save()
#             signals.epic_created.send( sender=request, epic=epic, user=request.user )
#             onDemandCalculateVelocity(project)
#             return HttpResponse(epic.id)
#     return HttpResponse("")
#
#
# @login_required
# def epic(request, epic_id):
#     "Returns a snippet of html suitable for use in replacing an epic block on the backlog pages."
#     epic = get_object_or_404(Epic, id=epic_id)
#     project = epic.project
#     read_access_or_403(project,request.user)
#     organization = organizationOrNone( project )
#     return render_to_response("projects/epic.html", {
#     "epic": epic,
#     "organization":organization,
#     "project":project
#     }, context_instance=RequestContext(request))
