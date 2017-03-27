from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from apps.attachments.models import Attachment, Tmpattachment, NoteAttachment

import logging

logger = logging.getLogger(__name__)


class AttachmentFormAjax(forms.ModelForm):
    attachment_file = forms.FileField(label=_('Upload attachment'))

    class Meta:
        model = Attachment
        fields = ('attachment_file',)

    def save(self, request, story, *args, **kwargs):
        self.instance.creator = request.user
        self.instance.content_type = ContentType.objects.get_for_model(story)
        self.instance.story = story
        attachment = super(AttachmentFormAjax, self).save(*args, **kwargs)
        return attachment
    
class TempAttachmentFormAjax(forms.ModelForm):
    attachment_file = forms.FileField(label=_('Upload attachment'))

    class Meta:
        model = Tmpattachment
        fields = ('attachment_file',)

    def save(self, request, project, *args, **kwargs):
        self.instance.creator = request.user
        self.instance.project = project
        self.instance.sessionkey = request.session.session_key
        attachment = super(TempAttachmentFormAjax, self).save(*args, **kwargs)
        return attachment

class NoteAttachmentFormAjax(forms.ModelForm):
    attachment_file = forms.FileField(label=_('Upload attachment'))

    class Meta:
        model = NoteAttachment
        fields = ('attachment_file',)

    def save(self, request, note, *args, **kwargs):
        self.instance.creator = request.user
        self.instance.note = note
        attachment = super(NoteAttachmentFormAjax, self).save(*args, **kwargs)
        return attachment
