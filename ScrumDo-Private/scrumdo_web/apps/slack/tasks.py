from django.conf import settings

from apps.scrumdocelery import app
from apps.projects.models import Story, StoryComment
from apps.projects.templatetags.projects_tags import name_or_username
from apps.slack.models import SlackMapping, SlackUser
from apps.slack.util import format_story_summary, format_slack_message, format_slack_html

import requests

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(name='apps.slack.tasks.send_slack_message')
def send_slack_message(mappingId, messageText):
    mapping = SlackMapping.objects.get(id=mappingId)
    user = SlackUser.objects.get(project=mapping.project)
    options = {
        'channel': mapping.channel_id,
        'text': messageText,
        'username': 'ScrumDo',
        'link_names': False,
        'icon_url': 'http://scrumdo-cdn.s3.amazonaws.com/manual_uploads/logos/48.png'
    }
    r = requests.post("https://slack.com/api/chat.postMessage?token=%s" % user.oauth_token, data=options).json()
    if not r["ok"]:
        mapping.errors += 1
        mapping.save()



@app.task(name='apps.slack.tasks.on_comment_posted')
def on_comment_posted(comment_id):
    comment = StoryComment.objects.get(id=comment_id)
    story = comment.story
    project = story.project
    url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())
    for mapping in SlackMapping.objects.filter(project=project, comment_created=True):
        send_slack_message(mapping.id,
                           u"New comment on <{url}|Card {prefix}-{story_number}> - _{story_summary}_\n*{user}* - {comment}".format(
                               url=url,
                               prefix=project.prefix,
                               story_number=story.local_id,
                               story_summary=format_story_summary(story.summary, True),
                               user=name_or_username(comment.user),
                               comment=format_slack_message(comment.comment)
                           ))

@app.task(name='apps.slack.tasks.on_card_moved')
def on_card_moved(story_id, cell_ids):
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

    for mapping in SlackMapping.objects.filter(project=project, card_moved=True):

        if cell_from is None:
            message = u"<{url}|Card {prefix}-{story_number}> moved into *{cell_to}* _{story_summary}_".format(
                               url=url,
                               prefix=project.prefix,
                               story_number=story.local_id,
                               story_summary=format_story_summary(story.summary, True),
                               cell_to=cell_to)
        elif cell_to is None:
            message = u"<{url}|Card {prefix}-{story_number}> moved out of *{cell_from}* _{story_summary}_".format(
                               url=url,
                               prefix=project.prefix,
                               story_number=story.local_id,
                               story_summary=format_story_summary(story.summary, True),
                               cell_from=cell_from)
        else:
            message = u"<{url}|Card {prefix}-{story_number}> moved from *{cell_from}* to *{cell_to}* _{story_summary}_".format(
                               url=url,
                               prefix=project.prefix,
                               story_number=story.local_id,
                               story_summary=format_story_summary(story.summary, True),
                               cell_from=cell_from,
                               cell_to=cell_to)

        send_slack_message(mapping.id, message)



@app.task(name='apps.slack.tasks.on_card_modified')
def on_card_modified(story_id, diffs):
    story = Story.objects.get(id=story_id)
    project = story.project
    url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())

    mappers = {
        'summary': lambda val: u"*Summary:* %s" % format_slack_html(val[1], True),
        'detail': lambda val: u"*Detail:* %s" % format_slack_html(val[1], True),
        'points': lambda val: u"*Points:* %s" % val[1],
        'time_criticality': lambda val: u"*Time Criticality:* %s" % val[1],
        'risk_reduction': lambda val: u"*Risk Reduction / Opportunity Enablement:* %s" % val[1],
        'epic': lambda val: u"*Collection*: %s" % format_slack_html(val[1]),
        'extra_1': lambda val: u"*%s:* %s" % (project.extra_1_label, format_slack_html(val[1]), True),
        'extra_2': lambda val: u"*%s:* %s" % (project.extra_2_label, format_slack_html(val[1]), True),
        'extra_3': lambda val: u"*%s:* %s" % (project.extra_3_label, format_slack_html(val[1]), True),
        'business_value': lambda val: u"*Business Value:* %s" % val[1],
        'estimated_minutes': lambda val: u"*Estimated Time:* %d:%02d hr" % divmod(val[1], 60),
        "iteration_id": lambda val: u"*Iteration:* %s" % story.iteration.name,
        'assignees_cache': lambda val: u"*Assignee:* %s" % val[1],
        'tags_cache': lambda val: u"*Tags:* %s" % val[1],
        'blocked': lambda val: u"*Blocked:* %s" % val[1],
        'unblocked': lambda val: u"*Unblocked:* %s" % val[1],
        'aging_reset': lambda val: u"Reset card aging",
    }


    fields = []
    for k, v in diffs.iteritems():
        if k in mappers:
            fields.append(mappers[k](v))

    if len(fields) == 0:
        return

    fields = "\n".join(fields)

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

    for mapping in SlackMapping.objects.filter(project=project, card_modified=True):
        send_slack_message(mapping.id, message)



@app.task(name='apps.slack.tasks.on_card_created')
def on_card_created(story_id):
    story = Story.objects.get(id=story_id)
    project = story.project
    for mapping in SlackMapping.objects.filter(project=project, card_created=True):
        url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())
        message = u"<{url}|Card {prefix}-{story_number} Created> - _{story_summary}_".format(
                       url=url,
                       prefix=project.prefix,
                       story_number=story.local_id,
                       story_summary=format_story_summary(story.summary, True))
        send_slack_message(mapping.id, message)
        
@app.task(name='apps.slack.tasks.on_attachment_added')
def on_attachment_added(story_id, fileData):
    story = Story.objects.get(id=story_id)
    project = story.project
    for mapping in SlackMapping.objects.filter(project=project, card_modified=True):
        url = "{host}{uri}".format(host=settings.SSL_BASE_URL, uri=story.get_absolute_url())
        attachmentUrl = u"<{uri}|{filename}>".format(uri=fileData['file_url'],
                                                     filename=fileData['file_name'])
        message = u"<{url}|Card {prefix}-{story_number} Modified> - Attachment Added\n{attachment_url}".format(
                       url=url,
                       prefix=project.prefix,
                       story_number=story.local_id,
                       attachment_url=attachmentUrl)
        send_slack_message(mapping.id, message)

#
#
# def setupQueue(sender, **kwargs):
#     obj = kwargs['instance']
#     processExtrasQueue.apply_async((obj.id,), countdown=5)
#
# if __name__ == "apps.extras.tasks" and settings.USE_QUEUE:
#     post_save.connect(setupQueue, sender=SyncronizationQueue, dispatch_uid="queue_tasks")
