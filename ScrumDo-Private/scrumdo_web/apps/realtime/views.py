# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.utils.html import escape

import apps.organizations.tz as tz

from apps.projects.templatetags.projects_tags import link_stories, urlify2, link_stories_v2
import json
from models import *

from apps.projects.access import *

from apps.account.templatetags.account_tags import realname

from util import send_project_message

logger = logging.getLogger(__name__)

@login_required
def chat(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user)

    message_txt = _parse_chat_message( request.POST.get("message") , project)
    if len(message_txt) > 0:
        message = ChatMessage( author=request.user, project=project, message=message_txt )
        message.save()
        send_project_message(project, _formatChat(message), 0)
    return HttpResponse("OK")

@login_required
def chat_history(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    read_access_or_403(project, request.user)
    count = int(request.GET.get("count", 25))
    page = int(request.GET.get("page", 1))
    chats = ChatMessage.objects.filter(project=project).order_by("-timestamp","-id")[(page-1)*count:page*count]
    rv = {'has_more':False, 'lines':[]}
    for chat in chats:
        rv['lines'].append(_formatChat(chat))
    rv['lines'].reverse()
    rv['has_more'] = len(rv['lines']) == count # Assume we have more if we're == count        
    return HttpResponse( json.dumps(rv) )

@login_required
def chat_upload(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user)
    fil = request.FILES.get('attachment_file',None)
    sub = project.organization.subscription
    if sub and sub.canUpload(fil.size/(1024*1024)):
        # attachment = form.save(request, None)
        message = ChatMessage(author=request.user, project=project, message=fil.name, message_type=ChatMessage.MESSAGE_TYPE_FILE)
        message.attachment_file = fil
        message.save()
        send_project_message(project, _formatChat(message), 0)
        return HttpResponse( '{"status":"ok"}' )
        
    return HttpResponse( '{"status":"failed"}' )
    

def _parse_chat_message(message_txt, project):
    message_txt = escape( message_txt ) # Strip out html and xss attacks
    message_txt = urlify2(message_txt) # Add in url links
    message_txt = link_stories_v2(message_txt,project) # Add in story links
    return message_txt
    
IMAGE_FORMATS = ('png','jpg','jpeg','gif')
FILE_ICONS = ( ('excel48',('xls','xlsx')),
               ('word48',('doc','docx')),
               ('page_white_vector48',('ai','xps','eps','fxg')),
               ('page_white_acrobat48',('pdf',)),
               ('page_white_actionscript48',('as',)),
               ('page_white_c48',('cpp','c')),
               ('page_white_code48',('xml','html')),
               ('page_white_cup48',('java','class')),
               ('page_white_flash48',('fla','swf')),
               ('page_white_h48',('h','hpp')),
               ('page_white_paint48',('psd','png','jpg','jpeg','gif','bmp','tif','tiff')),
               ('page_white_php48',('php',)),
               ('page_white_ruby48',('rb',)),
               ('page_white_text48',('txt',)),
               ('page_white_visualstudio48',('vss',)),
               ('page_white_zip48',('zip','rar','gz','tar')),
               ('powerpoint48',('ppt','pptx')),               
             )


def download_chat_attachment(request, message_id):
    message = ChatMessage.objects.get(id=message_id, message_type=ChatMessage.MESSAGE_TYPE_FILE)
    if not has_read_access(message.project, request.user):
        raise PermissionDenied()
    return HttpResponseRedirect(message.attachment_file.url)


    
def _formatChat(message):
    timestamp = tz.toOrganizationTime(message.timestamp, message.project.organization)
    author = {
        'username': message.author.username,
        'name': realname(message.author)
    }
    if message.message_type == ChatMessage.MESSAGE_TYPE_FILE:
        parts = message.message.rsplit(".", 1)
        preview = ""
        extension = ""
        if len(parts) > 1:
            extension = parts[1]

        attachment_url = reverse("download_chat_attachment", kwargs={"message_id": message.id} )

        if extension in IMAGE_FORMATS:
            # We can display it!
            preview = '<img src="%s" style="margin-left:48px; max-width: 300px; max-height: 300px;" />' % attachment_url
            
        icon_url = "%sfileicons/page_white48.gif" % settings.STATIC_URL
        for icon_type in FILE_ICONS:
            if extension in icon_type[1]:
                icon_url = "%sfileicons/%s.gif" % (settings.STATIC_URL,icon_type[0])
                

        txt = '<img style="margin:4px;vertical-align:middle" src="%s"><a target="_blank" href="%s">%s<br/>%s</a>' % \
              (icon_url, attachment_url, message.message,preview)

        payload = {
            "client": "scrumdo",
            "type": "chat:file",
            "payload": {
                "message": txt,
                "from": author,
                "date": timestamp.strftime("%B %d, %Y"),
                "time": timestamp.strftime("%I:%M")
            }
        }
        return payload
    else:
        txt = message.message.replace("\n", "<br/>")
        txt = txt.replace("%", "&#37;")

        payload = {
            "client": "scrumdo",
            "type": "chat:message",
            "payload": {
                "message": txt,
                "from": author,
                "project_slug": message.project.slug,
                "date": timestamp.strftime("%B %d, %Y"),
                "time": timestamp.strftime("%I:%M")
            }
        }
        return payload

