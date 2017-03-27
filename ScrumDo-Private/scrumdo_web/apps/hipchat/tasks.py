from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from apps.scrumdocelery import app

from apps.projects.models import Story, StoryComment
from apps.hipchat.models import HipChatMapping
# from apps.hipchat.util import format_story_summary, format_flowdock_message, format_flowdock_html

import slumber
import requests
import json
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(name='apps.hipchat.tasks.send_flowdock_message')
def send_hipchat_message(mappingId, messageText):
    mapping = HipChatMapping.objects.get(id=mappingId)

    url = "{base}/v2/room/{name}/notification?auth_token={token}".format(name=mapping.name, base=mapping.url, token=mapping.token)
    options = {
        'message': messageText,
        'message_format': 'html'
    }
    r = requests.post(url, data=json.dumps(options), headers={"Content-Type": "application/json"})
    logger.info(r)
    # if not r["ok"]:
    #     mapping.errors += 1
    #     mapping.save()



@app.task(name='apps.hipchat.tasks.on_comment_posted')
def on_comment_posted(comment_id):
    comment = StoryComment.objects.get(id=comment_id)
    story = comment.story
    project = story.project
    url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())
    for mapping in HipChatMapping.objects.filter(project=project, comment_created=True):
        send_hipchat_message(mapping.id, u"[{project_name}] New comment on <a href='{url}'>Card {prefix}-{story_number}</a> {summary}<br/>{comment}".format(
                                            story_number=story.local_id, 
                                            prefix=project.prefix,
                                            summary=strip_tags(story.summary), 
                                            comment=comment.comment, 
                                            url=url, 
                                            project_name=project.name))


@app.task(name='apps.hipchat.tasks.on_card_moved')
def on_card_moved(story_id, cell_ids, user):
    story = Story.objects.get(id=story_id)
    project = story.project
    url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())

    if cell_ids[0] is None:
        cell_from = None
    else:
        cell_from = project.boardCells.get(id=cell_ids[0]).full_label

    if cell_ids[1] is None:
        cell_to = None
    else:
        cell_to = project.boardCells.get(id=cell_ids[1]).full_label

    if cell_from == cell_to:
        return

    for mapping in HipChatMapping.objects.filter(project=project, card_moved=True):

        if cell_from is None:
            message = u"[{project_name}] <a href='{url}'>Card {prefix}-{story_number}</a> moved into {cell_to}".format(
                               prefix=project.prefix,
                               url=url,
                               story_number=story.local_id,
                               cell_to=cell_to,
                               project_name=project.name)
        elif cell_to is None:
            message = u"[{project_name}] <a href='{url}'>Card {prefix}-{story_number}</a> moved out of {cell_from}".format(
                               prefix=project.prefix,
                               url=url,
                               story_number=story.local_id,
                               cell_from=cell_from,
                               project_name=project.name)
        else:
            message = u"[{project_name}] <a href='{url}'>Card {prefix}-{story_number}</a> moved from {cell_from} to {cell_to}".format(
                               prefix=project.prefix,
                               url=url,
                               story_number=story.local_id,
                               cell_from=cell_from,
                               cell_to=cell_to,
                               project_name=project.name)

        send_hipchat_message(mapping.id, message)



@app.task(name='apps.hipchat.tasks.on_card_modified')
def on_card_modified(story_id, diffs, user):
    story = Story.objects.get(id=story_id)
    project = story.project
    url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())

    mappers = {
        'summary': lambda val: u"Summary: %s" % strip_tags(val[1]),
        'detail': lambda val: u"Detail: %s" % strip_tags(val[1]),
        'points': lambda val: u"Points: %s" % val[1],
        'time_criticality': lambda val: u"Time Criticality: %s" % val[1],
        'risk_reduction': lambda val: u"Risk Reduction / Opportunity Enablement: %s" % val[1],
        'epic': lambda val: u"Epic*: %s" % strip_tags(val[1]),
        'extra_1': lambda val: u"%s: %s" % (project.extra_1_label, strip_tags(val[1])),
        'extra_2': lambda val: u"%s: %s" % (project.extra_2_label, strip_tags(val[1])),
        'extra_3': lambda val: u"%s: %s" % (project.extra_3_label, strip_tags(val[1])),
        'business_value': lambda val: u"Business Value: %s" % val[1],
        'estimated_minutes': lambda val: u"Estimated Time: %d:%02d hr" % divmod(val[1], 60),
        "iteration_id": lambda val: u"Iteration: %s" % story.iteration.name,
        'assignees_cache': lambda val: u"Assignee: %s" % val[1],
        'tags_cache': lambda val: u"Tags: %s" % val[1],
        'blocked': lambda val: u"Blocked: %s" % val[1],
        'unblocked': lambda val: u"Unblocked: %s" % val[1],
        'aging_reset': lambda val: u"Reset card aging",
    }


    fields = []
    for k, v in diffs.iteritems():
        if k in mappers:
            fields.append(mappers[k](v))

    if len(fields) == 0:
        return

    fields = "<br/>".join(fields)

    if "summary" in diffs:
        # No need to double-post the summary.
        message = u"[{project_name}] <a href='{url}'>Card {prefix}-{story_number}</a> Modified<br/>{fields}".format(
                       url=url,
                       prefix=project.prefix,
                       story_number=story.local_id,
                       story_summary=strip_tags(story.summary),
                       fields=fields,
                       project_name=project.name)
    else:
        # Give the summary as context
        message = u"[{project_name}] <a href='{url}'>Card {prefix}-{story_number}</a> Modified - {story_summary}<br/>{fields}".format(
                       url=url,
                       prefix=project.prefix,
                       story_number=story.local_id,
                       story_summary=strip_tags(story.summary),
                       fields=fields,
                       project_name=project.name)


    for mapping in HipChatMapping.objects.filter(project=project, card_modified=True):
        send_hipchat_message(mapping.id, message)



@app.task(name='apps.hipchat.tasks.on_card_created')
def on_card_created(story_id, author):
    story = Story.objects.get(id=story_id)
    project = story.project
    for mapping in HipChatMapping.objects.filter(project=project, card_created=True):
        url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())
        message = u"[{project_name}] New card created: <a href='{url}'>Card {prefix}-{story_number}</a> {summary}".format(
                    url=url,
                    prefix=project.prefix,
                    story_number=story.local_id,
                    summary=strip_tags(story.summary), 
                    project_name=project.name )
        send_hipchat_message(mapping.id, message)


@app.task(name='apps.hipchat.tasks.on_attachment_added')
def on_attachment_added(story_id, fileData, author):
    story = Story.objects.get(id=story_id)
    project = story.project
    attachmentUrl = "<a target='_blank' href='{uri}'>{filename}</a>".format(
                    uri=fileData['file_url'], 
                    filename=fileData['file_name']
                    )
    
    for mapping in HipChatMapping.objects.filter(project=project):
        url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())
        message = u"[{project_name}] Card {prefix}-{story_number} - Attachment Added\n{attachment_url}".format(
                    url=url,
                    prefix=project.prefix,
                    story_number=story.local_id,
                    attachment_url=attachmentUrl,
                    project_name=project.name)
        send_hipchat_message(mapping.id, message)
