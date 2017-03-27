from .common import *
from apps.attachments.models import Attachment, Tmpattachment, NoteAttachment
import apps.projects.signals as signals

class AttachmentHandler(BaseHandler):
    fields = ("id", "filename", "created", "modified", "url", "story_id", "attachment_url", "thumb_url", "attachment_type", "attachment_name", "creator", "cover_image")
    model = Attachment


    @staticmethod
    def url(attachment):
        # check if attachment is local of from remote services
        if attachment.attachment_type == "local":
            return attachment.attachment_file.url

    def read(self, request, organization_slug, project_slug, story_id, attachment_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        if int(story_id) != -1:
            story = project.stories.get(id=story_id)
            if attachment_id is None:
                attachments = Attachment.objects.filter(story=story)
                return attachments
            return Attachment.objects.filter(story=story, id=attachment_id)
        else:
            attachments = Tmpattachment.objects.filter(sessionkey=request.session.session_key, creator=request.user, project=project)
            return attachments

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, story_id, attachment_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        if int(story_id) == -1 and int(attachment_id) == -1:
            self._cleanTempAttachments(request, project)
            return "OK"
        if int(story_id) == -1:
            Tmpattachment.objects.filter(sessionkey=request.session.session_key,creator = request.user, id=attachment_id).delete()
            return "OK"
        story = project.stories.get(id=story_id)
        attachment = Attachment.objects.filter(story=story, id=attachment_id)
        attachment.delete()
        return "OK"
    
    def _cleanTempAttachments(self, request, project):
        Tmpattachment.objects.filter(sessionkey=request.session.session_key,creator = request.user, project=project).delete()
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, story_id):
        data = request.data
        file_url = data["attachmentUrl"]
        file_name = data["fileName"]
        thumb_url = data["thumbUrl"]
        
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        
        if int(story_id) != -1:
            story = project.stories.get(id=story_id)
            attchment = Attachment(creator = request.user)
            attchment.story = story
        else:
            attchment = Tmpattachment(creator = request.user)
            attchment.sessionkey = request.session.session_key
            attchment.project = project
        
        attchment.attachment_file = ""
        attchment.attachment_url = file_url
        attchment.attachment_name = file_name
        attchment.thumb_url = thumb_url
        attchment.attachment_type = 'dropbox'
        attchment.save()
        
        if int(story_id) != -1:
            signals.attachment_added.send(sender=request, story=story, user=request.user, \
                                          fileData={'file_name':file_name, 'file_url':file_url, 'thumb_url':thumb_url})
        
        return "OK"


class NoteAttachmentHandler(BaseHandler):
    fields = ("id", "filename", "created", "modified", "url", "note_id", "attachment_url", "thumb_url", "attachment_type", "attachment_name", "creator")
    model = NoteAttachment

    @staticmethod
    def url(attachment):
        # check if attachment is local of from remote services
        if attachment.attachment_type == "local":
            return attachment.attachment_file.url

    def read(self, request, organization_slug, project_slug, note_id, attachment_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        if int(note_id) != -1:
            note = project.notes.get(id=note_id)
            if attachment_id is None:
                attachments = NoteAttachment.objects.filter(note=note)
                return attachments
            return NoteAttachment.objects.filter(note=note, id=attachment_id)
        else:
            attachments = Tmpattachment.objects.filter(sessionkey=request.session.session_key, creator=request.user, project=project)
            return attachments

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, note_id, attachment_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        if int(note_id) == -1 and int(attachment_id) == -1:
            self._cleanTempAttachments(request, project)
            return "OK"
        if int(note_id) == -1:
            Tmpattachment.objects.filter(sessionkey=request.session.session_key,creator = request.user, id=attachment_id).delete()
            return "OK"
        note = project.notes.get(id=note_id)
        attachment = NoteAttachment.objects.filter(note=note, id=attachment_id)
        attachment.delete()
        return "OK"
    
    def _cleanTempAttachments(self, request, project):
        Tmpattachment.objects.filter(sessionkey=request.session.session_key,creator = request.user, project=project).delete()
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, note_id):
        data = request.data
        file_url = data["attachmentUrl"]
        file_name = data["fileName"]
        thumb_url = data["thumbUrl"]
        
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        
        if int(note_id) != -1:
            note = project.notes.get(id=note_id)
            attchment = NoteAttachment(creator = request.user)
            attchment.note = note
        else:
            attchment = Tmpattachment(creator = request.user)
            attchment.sessionkey = request.session.session_key
            attchment.project = project
        
        attchment.attachment_file = ""
        attchment.attachment_url = file_url
        attchment.attachment_name = file_name
        attchment.thumb_url = thumb_url
        attchment.attachment_type = 'dropbox'
        attchment.save()

        if int(note_id) != -1:
            signals.note_attachment_added.send(sender=request, note=note, user=request.user, \
                                          fileData={'file_name':file_name, 'file_url':file_url, 'thumb_url':thumb_url})
        return "OK"

class AttachmentCoverHandler(BaseHandler):
    
    allowed_methods = ('PUT', )

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, story_id, attachment_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        
        data = request.data
        action = data["action"]
         
        attachment = Attachment.objects.get(id=attachment_id, story_id = story_id)
        old_covers = Attachment.objects.filter(story_id = story_id, cover_image=True)
        for cover in old_covers:
            cover.cover_image = False
            cover.save()

        if action == "toggle":
            attachment.cover_image = True
            attachment.save()

        return attachment
         

