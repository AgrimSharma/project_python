from django.conf import settings
from django.core.urlresolvers import reverse

from apps.scrumdocelery import app

from apps.projects.models import Story, StoryComment
from apps.flowdock.models import FlowdockMapping, FlowdockUser
from apps.flowdock.util import format_story_summary, format_flowdock_message, format_flowdock_html

import slumber
import requests
import json

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def post(token, source, from_address, subject, content, from_name, project, link):
    api = slumber.API("https://api.flowdock.com/v1/messages/", append_slash=False)
    data = {
        "source": source,
        "from_address": from_address,
        "subject": subject,
        "content": content,
        "from_name": from_name,
        "project": project,
        "link": link
        }
    logger.debug("Data: %s" % data)
    api.team_inbox(token).post(data)


@app.task(name='apps.flowdock.tasks.send_flowdock_message')
def send_flowdock_message(mappingId, messageText, title, action, story_id, author, color="green"):
    story = Story.objects.get(id=story_id)
    mapping = FlowdockMapping.objects.get(id=mappingId)
    user = FlowdockUser.objects.get(project=mapping.project)
    options = {
            "flow": mapping.channel_id,
            "flow_token": mapping.api_token,
            "event": "activity",
            "author": author,
            "title": title,
            "body": messageText,
            "external_thread_id": "STORY:%s" % story.id,
            "thread": {
                "title": u"%s-%s %s" % (story.project.prefix, story.local_id, story.summary),
                "fields": [
                    {'label': 'Project', 'value': story.project.name},
                    {'label': 'Iteration', 'value': story.iteration.name}
                ],
                # "body": story.detail,
                "external_url": "{base_url}{permalink}".format(base_url=settings.BASE_URL, permalink=story.get_absolute_url()),
                "status": {
                    "color": color,
                    "value": action
                }
            }
        }


    url = "https://api.flowdock.com/messages"
    r = requests.post(url, data=json.dumps(options), headers={"Content-Type": "application/json"})
    logger.info(r)
    # if not r["ok"]:
    #     mapping.errors += 1
    #     mapping.save()



@app.task(name='apps.flowdock.tasks.on_comment_posted')
def on_comment_posted(comment_id):
    comment = StoryComment.objects.get(id=comment_id)
    story = comment.story
    project = story.project
    url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())
    for mapping in FlowdockMapping.objects.filter(project=project, comment_created=True):

        send_flowdock_message(mapping.id,
                              format_flowdock_message(comment.comment),
                              "commented on",
                              "comment",
                              story.id,
                              {
                                  'name': comment.user.username,
                                  'avatar': u"{base}{url}".format(base=settings.BASE_URL,url=reverse('avatar_redirect', kwargs={'size': 48, 'username': comment.user.username}))
                              },
                              "purple")


@app.task(name='apps.flowdock.tasks.on_card_moved')
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

    for mapping in FlowdockMapping.objects.filter(project=project, card_moved=True):

        if cell_from is None:
            message = u"moved into {cell_to}".format(
                               story_number=story.local_id,
                               cell_to=cell_to)
        elif cell_to is None:
            message = u"moved out of {cell_from}".format(
                               story_number=story.local_id,
                               cell_from=cell_from)
        else:
            message = u"moved from {cell_from} to {cell_to}".format(
                               story_number=story.local_id,
                               cell_from=cell_from,
                               cell_to=cell_to)

        send_flowdock_message(mapping.id, '', message, "moved", story.id, user, "blue")
        # send_flowdock_message(mapping.id, message, "modified", story_id)
        # send_flowdock_message(mapping.id, message)



@app.task(name='apps.flowdock.tasks.on_card_modified')
def on_card_modified(story_id, diffs, user):
    story = Story.objects.get(id=story_id)
    project = story.project
    url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())

    mappers = {
        'summary': lambda val: u"<li><b>Summary</b> %s</li>" % format_flowdock_html(val[1], True),
        'detail': lambda val: u"<li><b>Detail</b> %s</li>" % format_flowdock_html(val[1], True),
        'points': lambda val: u"<li><b>Points</b> %s</li>" % val[1],
        'time_criticality': lambda val: u"<li><b>Time Criticality</b> %s</li>" % val[1],
        'risk_reduction': lambda val: u"<li><b>Risk Reduction / Opportunity Enablement</b> %s</li>" % val[1],
        'epic': lambda val: u"<li><b>Epic*: %s</li>" % format_flowdock_html(val[1], True),
        'extra_1': lambda val: u"<li><b>%s</b> %s</li>" % (project.extra_1_label, format_flowdock_html(val[1]), True),
        'extra_2': lambda val: u"<li><b>%s</b> %s</li>" % (project.extra_2_label, format_flowdock_html(val[1]), True),
        'extra_3': lambda val: u"<li><b>%s</b> %s</li>" % (project.extra_3_label, format_flowdock_html(val[1]), True),
        'business_value': lambda val: u"<li><b>Business Value</b> %s</li>" % val[1],
        'estimated_minutes': lambda val: u"<li><b>Estimated Time:</b> %d:%02d hr</li>" % divmod(val[1], 60),
        "iteration_id": lambda val: u"<li><b>Iteration</b> %s</li>" % story.iteration.name,
        'assignees_cache': lambda val: u"<li><b>Assignee</b> %s</li>" % val[1],
        'tags_cache': lambda val: u"<li><b>Tags</b> %s</li>" % val[1],
        'blocked': lambda val: u"<li><b>Blocked</b> %s" % val[1],
        'unblocked': lambda val: u"<li><b>Unblocked</b> %s" % val[1],
        'aging_reset': lambda val: u"Reset card aging",
    }


    fields = []
    for k, v in diffs.iteritems():
        if k in mappers:
            fields.append(mappers[k](v))

    if len(fields) == 0:
        return

    fields = "".join(fields)
    fields = "<ul>" + fields + "</ul>"

    if "summary" in diffs:
        # No need to double-post the summary.
        message = u"<{url}|Card {prefix}-{story_number} Modified>\n{fields}".format(
                       url=url,
                       prefix=project.prefix,
                       story_number=story.local_id,
                       story_summary=format_story_summary(story.summary, True),
                       fields=fields)
    else:
        # Give the summary as context
        message = u"<{url}|Card {prefix}-{story_number} Modified> - {story_summary}\n{fields}".format(
                       url=url,
                       prefix=project.prefix,
                       story_number=story.local_id,
                       story_summary=format_story_summary(story.summary, True),
                       fields=fields)


    for mapping in FlowdockMapping.objects.filter(project=project, card_modified=True):
        send_flowdock_message(mapping.id, fields, "edited card", 'modified', story_id, user, "green")
        # send_flowdock_message(mapping.id, message)



@app.task(name='apps.flowdock.tasks.on_card_created')
def on_card_created(story_id, author):
    story = Story.objects.get(id=story_id)
    project = story.project
    message = "created card"
    for mapping in FlowdockMapping.objects.filter(project=project, card_created=True):
        send_flowdock_message(mapping.id, '', message, 'created', story_id, author, color="green")


@app.task(name='apps.flowdock.tasks.on_attachment_added')
def on_attachment_added(story_id, fileData, author):
    story = Story.objects.get(id=story_id)
    project = story.project
    
    url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())
    attachmentUrl = "<a target='_blank' href='{uri}'>{filename}</a>".format(uri=fileData['file_url'], filename=fileData['file_name'])
    message = u"<{url}|Card {prefix}-{story_number} Modified> - Attachment Added\n{attachment_url}".format(
                   url=url,
                   prefix=project.prefix,
                   story_number=story.local_id,
                   attachment_url=attachmentUrl)
    for mapping in FlowdockMapping.objects.filter(project=project):
        send_flowdock_message(mapping.id, '', message, 'modified', story_id, author, color="green")
