from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from apps.projects.access import read_access_or_403
from models import Attachment, NoteAttachment

@login_required
def attachment_redirect(request, attachment_id):
    attachment = get_object_or_404(Attachment, id=attachment_id)
    story = attachment.story
    project = story.project
    read_access_or_403(project, request.user)
    return HttpResponseRedirect(attachment.attachment_file.url)

@login_required
def note_attachment_redirect(request, attachment_id):
    attachment = get_object_or_404(NoteAttachment, id=attachment_id)
    note = attachment.note
    project = note.project
    read_access_or_403(project, request.user)
    return HttpResponseRedirect(attachment.attachment_file.url)

