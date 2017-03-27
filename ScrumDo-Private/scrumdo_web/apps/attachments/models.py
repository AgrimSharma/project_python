from datetime import datetime
import os
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

import random
import logging

logger = logging.getLogger(__name__)


class AttachmentManager(models.Manager):
    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id,
                           object_id=obj.id)


def attachment_attachment_upload(instance, filename):
    """Stores the attachment in a "per module/appname/primary key" folder"""
    attachmentdir = "attachments_v2"
    return 'projects/story/%s/%s' % (
                   attachmentdir,
                   '%s_%s' % (instance.story.pk, filename))

def attachment_temp_attachment_upload(instance, filename):
    """Stores the attachment in a "per module/appname/primary key" folder"""
    rndnum = random.randint(1000, 9999)
    attachmentdir = "attachments_v2"
    return 'projects/story/%s/%s' % (
                   attachmentdir,
                   '%s_%s' % (rndnum, filename))

def attachment_note_attachment_upload(instance, filename):
    """Stores the attachment in a "per module/appname/primary key" folder"""
    attachmentdir = "attachments_v2"
    return 'projects/note/%s/%s' % (
                   attachmentdir,
                   '%s_%s' % (instance.note.pk, filename))


class Attachment(models.Model):

    objects = AttachmentManager()
    
    ATTACHMENT_TYPES = (
        ('local', 'My Computer'),
        ('dropbox', 'Dropbox'),
    )

    # content_type = models.ForeignKey(ContentType)
    # object_id = models.PositiveIntegerField()
    story = models.ForeignKey("projects.Story", related_name="attachments", null=True)
    # content_object = generic.GenericForeignKey('content_type', 'object_id')
    creator = models.ForeignKey(User, related_name="created_attachments", verbose_name=_('creator'))
    attachment_file = models.FileField(_('attachment'), upload_to=attachment_attachment_upload, max_length=512)
    attachment_url = models.CharField(max_length=512)
    thumb_url = models.CharField(max_length=512)
    attachment_type = models.CharField(max_length=15,
                                       choices=ATTACHMENT_TYPES,
                                       default='local')
    attachment_name = models.CharField(max_length=256)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    cover_image = models.BooleanField(default=False)

    def canPreview(self):
        try:
            thumbnailAvailable = [".jpg", "jpeg", ".gif", ".png"]
            extension = str(self.filename)[-4:].lower()        
            return extension in thumbnailAvailable
        except:
            logger.debug(self.filename)
            return False
        

    class Meta:
        ordering = ['-created']
        permissions = (
            ('delete_foreign_attachments', 'Can delete foreign attachments'),
        )
        db_table = "v2_attachments_attachment"


    def __unicode__(self):
        return '%s attached %s' % (self.creator.username, self.attachment_file.name)

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]
    
class Tmpattachment(models.Model):
    
    ATTACHMENT_TYPES = (
        ('local', 'My Computer'),
        ('dropbox', 'Dropbox'),
    )
    creator = models.ForeignKey(User, related_name="created_tmpattachments", verbose_name=_('tmpcreator'))
    project = models.ForeignKey("projects.Project", related_name="attachments")
    attachment_file = models.FileField(_('attachment'), upload_to=attachment_temp_attachment_upload, max_length=512)
    attachment_url = models.CharField(max_length=512)
    thumb_url = models.CharField(max_length=512)
    attachment_type = models.CharField(max_length=15,
                                       choices=ATTACHMENT_TYPES,
                                       default='local')
    attachment_name = models.CharField(max_length=256)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    sessionkey = models.CharField(max_length=512)

    class Meta:
        ordering = ['-created']
        permissions = (
            ('delete_foreign_attachments', 'Can delete foreign attachments'),
        )
        db_table = "v2_attachments_tmpattachment"


    def __unicode__(self):
        return '%s attached %s' % (self.creator.username, self.attachment_file.name)

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]


class NoteAttachment(models.Model):
    objects = AttachmentManager()
    
    ATTACHMENT_TYPES = (
        ('local', 'My Computer'),
        ('dropbox', 'Dropbox'),
    )

    note = models.ForeignKey("projects.Note", related_name="attachments", null=True)
    creator = models.ForeignKey(User, related_name="created_note_attachments", verbose_name=_('creator'))
    attachment_file = models.FileField(_('attachment'), upload_to=attachment_note_attachment_upload, max_length=512)
    attachment_url = models.CharField(max_length=512)
    thumb_url = models.CharField(max_length=512)
    attachment_type = models.CharField(max_length=15,
                                       choices=ATTACHMENT_TYPES,
                                       default='local')
    attachment_name = models.CharField(max_length=256)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    def canPreview(self):
        try:
            thumbnailAvailable = [".jpg", "jpeg", ".gif", ".png"]
            extension = str(self.filename)[-4:].lower()        
            return extension in thumbnailAvailable
        except:
            logger.debug(self.filename)
            return False
        

    class Meta:
        ordering = ['-created']
        permissions = (
            ('delete_foreign_attachments', 'Can delete foreign attachments'),
        )
        db_table = "v2_attachments_note_attachment"

    def __unicode__(self):
        return '%s attached %s' % (self.creator.username, self.attachment_file.name)

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]