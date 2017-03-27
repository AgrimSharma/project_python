# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from apps.subscription.models import Subscription
from apps.projects.models import Story, Project, Note
from apps.projects.access import write_access_or_403
from forms import AttachmentFormAjax, TempAttachmentFormAjax, NoteAttachmentFormAjax

from django.conf import settings
import apps.projects.signals as signals

import logging

logger = logging.getLogger(__name__)

@require_POST
@login_required
@csrf_exempt
def add_attachment_ajax(request, project_slug, story_id):
    if int(story_id) == -1:
        isSuccess, result = add_attachment_ajax_temp(request, project_slug)
        return HttpResponse(result)
    
    story = Story.objects.get(id=story_id)
    if story is None:
        return HttpResponse("Could not find story")

    project = story.project
    if project.slug != project_slug:
        raise PermissionDenied()
    write_access_or_403(project, request.user)
    
    sub = Subscription.getSubscriptionForObject(story)
    fil = request.FILES.get('attachment_file',None)

    if fil == None:
        logger.debug("Did not find a file to upload")
        return HttpResponse("Could not upload")
    
    if sub and sub.canUpload(fil.size/(1024*1024)):
        logger.debug("Uploading file...")
        logger.debug(request.FILES)
        form = AttachmentFormAjax(request.POST, request.FILES)
        logger.debug(12345)
        attachment = form.save(request, story)
        logger.debug(attachment.id)
        file_url = u"{base}/attachment/{id}".format(base=settings.BASE_URL, id=attachment.id)
        thumb_url = file_url if attachment.canPreview() else None
        signals.attachment_added.send(sender=request, story=story, user=request.user, fileData={'file_name':attachment.filename, 'file_url':file_url, 'thumb_url':thumb_url})
        
        return HttpResponse('Uploaded')
    else:
        logger.debug("No Storage")
        return HttpResponse('You do not have available storage space to upload.')
    
def add_attachment_ajax_temp(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    write_access_or_403(project, request.user)
    sub = Subscription.getSubscriptionForObject(project)
    fil = request.FILES.get('attachment_file',None)
    
    if fil == None:
        logger.debug("Did not find a file to upload")
        return (False, "Could not upload")
    if sub and sub.canUpload(fil.size/(1024*1024)):
        logger.debug("Uploading temp file...")
        form = TempAttachmentFormAjax(request.POST, request.FILES)
        attachment = form.save(request, project)
        return (True, "Uploaded")
    else:
        logger.debug("No Storage")
        return (False, "You do not have available storage space to upload.")

@require_POST
@login_required
@csrf_exempt
def add_note_attachment_ajax(request, project_slug, note_id): 
    if int(note_id) == -1:
        isSuccess, result = add_attachment_ajax_temp(request, project_slug)
        return HttpResponse(result)
    
    note = Note.objects.get(id=note_id)
    if note is None:
        return HttpResponse("Could not find note")

    project = note.project
    if project.slug != project_slug:
        raise PermissionDenied()
    write_access_or_403(project, request.user)
    
    sub = Subscription.getSubscriptionForObject(project)
    fil = request.FILES.get('attachment_file',None)

    if fil == None:
        logger.debug("Did not find a file to upload")
        return HttpResponse("Could not upload")
    
    if sub and sub.canUpload(fil.size/(1024*1024)):
        logger.debug("Uploading file...")
        form = NoteAttachmentFormAjax(request.POST, request.FILES)
        attachment = form.save(request, note)
        
        file_url = u"{base}/attachment/note/{id}".format(base=settings.BASE_URL, id=attachment.id)
        thumb_url = file_url if attachment.canPreview() else None
        signals.note_attachment_added.send(sender=request, note=note, user=request.user, 
            fileData={'file_name':attachment.filename, 'file_url':file_url, 'thumb_url':thumb_url})
        return HttpResponse('Uploaded')
    else:
        logger.debug("No Storage")
        return HttpResponse('You do not have available storage space to upload.')