from .common import *

from django.utils.html import strip_tags
from django.db.models import Count
from django.conf import settings

from apps.projects.models import Note, NoteComment
import apps.projects.signals as signals
from apps.realtime import util as realtime_util
import apps.activities.utils as utils
from apps.attachments.models import NoteAttachment, Tmpattachment

import apps.organizations.tz as tz
import datetime

class NoteHandler(BaseHandler):
    fields = ("id",
              "title",
              "body",
              "created_date",
              "modified_date",
              ("creator", ("first_name", "last_name", "username")),
              "project_id",
              "iteration_id",
              "iteration_name",
              "comments_count",
              "attachments_count",
              "active")
    model = Note
    allowed_methods = ('POST','GET','PUT','DELETE',)

    @staticmethod
    def attachments_count(note):
        return note.attachments.all().count()

    @staticmethod
    def comments_count(note):
        return note.comments.all().count()

    @staticmethod
    def created_date(note):
        return tz.formatDateTime(note.created, note.project.organization)

    @staticmethod
    def modified_date(note):
        return tz.formatDateTime(note.modified, note.project.organization)

    @staticmethod
    def iteration_name(note):
        try:
            return note.iteration.name
        except:
            pass

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id = None, note_id = None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)

        if note_id is None:
            if iteration_id is None:
                return project.notes.filter(active=True).order_by("-created")
            else:
                iteration = project.iterations.get(id=iteration_id)
                return iteration.notes.filter(active=True).order_by("-created")
        else:
            return project.notes.get(id=note_id)
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, iteration_id, note_id = None):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        data = request.data
        note = Note(project = project, creator=request.user)
        note.title = data['title']
        note.body = data['body']

        if iteration_id is not None:
            note.iteration_id = iteration_id
        else:
            if int(data['iteration_id']) == 0:
                note.iteration_id = None
            else:
                note.iteration_id = data['iteration_id']

        note.save()
        self._checkForTempAttachments(note, project, request)
        self._checkForComment(note, data, request)
        signals.note_created.send(sender=request, note=note, user=request.user)
        return note;

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, iteration_id, note_id = None):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        data = request.data

        note = project.notes.get(id=note_id)
        if note.project != project:
            raise ValidationError("project don't match!")

        old_note_copy = note.__dict__.copy()

        note.title = data['title']
        note.body = data['body']

        if iteration_id is not None:
            note.iteration_id = iteration_id
        else:
            if int(data['iteration_id']) != -1:
                note.iteration_id = data['iteration_id']
            if int(data['iteration_id']) == 0:
                note.iteration_id = None

        note.save()
        note_copy = note.__dict__.copy()

        diffs = utils.model_differences(old_note_copy, note_copy, ["modified"], dicts=True)
        signals.note_updated.send(sender=request, note=note, user=request.user, diffs=diffs)
        return note;
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, iteration_id, note_id = None):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        note = project.notes.get(id=note_id)

        if note.project != project:
            raise ValidationError("project don't match!")
        
        if note_id is not None:
            note.active = False
            note.save()
            signals.note_deleted.send(sender=request, note=note, user=request.user)
            return "deleted"
        else:
            raise ValidationError("missing note!")

    def _checkForTempAttachments(self, note, project, request):
        tmpAttachments = Tmpattachment.objects.filter(sessionkey=request.session.session_key,
                                                      creator=request.user, project=project)
        for tmpAttachment in tmpAttachments:
            attchment = NoteAttachment(creator = request.user)
            attchment.note = note
            attchment.attachment_file = tmpAttachment.attachment_file
            attchment.attachment_url = tmpAttachment.attachment_url
            attchment.attachment_name = tmpAttachment.attachment_name
            attchment.thumb_url = tmpAttachment.thumb_url
            attchment.attachment_type = tmpAttachment.attachment_type
            attchment.save()
            tmpAttachment.delete()

    def _checkForComment(self, note, data, request):
        if "newComment" in data and len(data['newComment']) > 1:
            comment = NoteComment(note=note,
                                   user=request.user,
                                   comment=data["newComment"])
            comment.save()
