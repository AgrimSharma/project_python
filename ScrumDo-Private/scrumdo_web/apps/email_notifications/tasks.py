from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse

from apps.scrumdocelery import app

from mailer import send_mail
from mailer.engine import send_all
from mailer.models import Message

from apps.email_notifications.models import StoryMentions, EmailOptions, ChatMentions, NoteMentions

from .dailydigest import DailyDigest
from .iteration_report import IterationReport
from .email_notifications import EmailNotifications

import traceback
import sys
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task
def retry_deferred():
    Message.objects.retry_deferred()


@app.task
def send_queued_mail():
    send_all()


@app.task
def send_notifications():
    notifications = EmailNotifications()
    notifications.send()


@app.task
def send_iteration_reports():
    reports = IterationReport()
    reports.send()


@app.task
def send_daily_digest():
    digest = DailyDigest()
    digest.send()


@app.task
def sendMentionEmail(dbid):
    try:
        mention = StoryMentions.objects.get(id=dbid)
        story = mention.story
        user = mention.user
        creator = mention.creator
        mention.delete()

        options = _getUserOptions(user)
        if options.mention == 0:
            return # notifications off.        

        comments = story.comments.order_by("-date_submitted")
        if len(comments) > 0:
            last_comment = comments[0]
        else:
            last_comment = ""

        body = render_to_string("email_notifications/emails/email_mentions.html" , 
                                {'story':story, 
                                 'mentioned_by':creator,
                                 'last_comment':last_comment,
                                 'static_url': settings.STATIC_URL,
                                 'base_url':settings.BASE_URL} )
        text_body = strip_tags(body)

        subject = "[ScrumDo] You were mentioned."

        replyTo = settings.STORY_EMAIL_ADDRESS % (story.id, story.project.slug)

        msg = EmailMultiAlternatives(subject,
                                     text_body,
                                     settings.AUTOMATED_EMAIL,
                                     [user.email],
                                     headers={'Reply-To': replyTo,
                                              'format': 'flowed'})

        msg.attach_alternative(body, "text/html")
        msg.send()

    except StoryMentions.DoesNotExist:
        pass  # the cronjob already got it.
    except:
        e = sys.exc_info()[1]       
        stack = "\n".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        send_mail('sendMentionEmail Error', stack, settings.DEFAULT_FROM_EMAIL, ["marc.hughes@gmail.com"], fail_silently=False)

@app.task
def sendChatMentionEmail(dbid):
    try:
        mention = ChatMentions.objects.get(id=dbid)
        project = mention.project
        user = mention.user
        creator = mention.creator
        message = mention.message
        mention.delete()
        
        chat_url = reverse('project_app', kwargs={'project_slug': project.slug}) + "#/chat"

        options = _getUserOptions(user)
        if options.mention == 0:
            return # notifications off.        
        
        body = render_to_string("email_notifications/emails/email_chat_mentions.html" , 
                                {'project':project,
                                 'mentioned_by':creator, 
                                 'message':message,
                                 'chat_url':chat_url,
                                 'static_url': settings.STATIC_URL,
                                 'base_url':settings.BASE_URL} )
        
        text_body = strip_tags(body)

        subject = "[ScrumDo] You were mentioned."

        replyTo = "noreply@scrumdo.com"

        msg = EmailMultiAlternatives(subject,
                                     text_body,
                                     settings.AUTOMATED_EMAIL,
                                     [user.email],
                                     headers={'Reply-To': replyTo,
                                              'format': 'flowed'})

        msg.attach_alternative(body, "text/html")
        msg.send()
        
    except ChatMentions.DoesNotExist:
        pass  # the cronjob already got it.
    except:
        e = sys.exc_info()[1]        
        stack = "\n".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        send_mail('sendChatMentionEmail Error', stack, settings.DEFAULT_FROM_EMAIL, ["marc.hughes@gmail.com"], fail_silently=False)

@app.task
def sendNoteMentionEmail(dbid):
    try:
        mention = NoteMentions.objects.get(id=dbid)
        note = mention.note
        user = mention.user
        creator = mention.creator
        mention.delete()

        if note.iteration is not None:
            iteration = "#/iteration/%d/notes/%d" % (note.iteration.id, note.id)
            url = reverse('project_app', kwargs={'project_slug': note.project.slug}) + iteration
        else:
            url = reverse('project_app', kwargs={'project_slug': note.project.slug}) + "#/"

        options = _getUserOptions(user)
        if options.mention == 0:
            return # notifications off.        
        
        body = render_to_string("email_notifications/emails/email_note_mention.html" , 
                                {'project':note.project,
                                 'mentioned_by':creator, 
                                 'note':note,
                                 'url':url,
                                 'static_url': settings.STATIC_URL,
                                 'base_url':settings.BASE_URL} )
        
        text_body = strip_tags(body)
        subject = "[ScrumDo] You were mentioned."
        replyTo = "noreply@scrumdo.com"

        msg = EmailMultiAlternatives(subject,
                                     text_body,
                                     settings.AUTOMATED_EMAIL,
                                     [user.email],
                                     headers={'Reply-To': replyTo,
                                              'format': 'flowed'})

        msg.attach_alternative(body, "text/html")
        msg.send()
        
    except ChatMentions.DoesNotExist:
        pass  # the cronjob already got it.
    except:
        e = sys.exc_info()[1]        
        stack = "\n".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        send_mail('sendChatMentionEmail Error', stack, settings.DEFAULT_FROM_EMAIL, ["marc.hughes@gmail.com"], fail_silently=False)


def _getUserOptions(user):
    """Returns the EmailOptions object for a user, automatically creating it if it 
       doesn't exist and caching results"""
    recs = EmailOptions.objects.filter(user=user)
    if len(recs) > 0:
        rec = recs[0]
    else:
        rec = EmailOptions(user=user)
        rec.save()
    return rec
