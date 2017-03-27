from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Max
from django.utils.html import escape

from email_reply_parser import EmailReplyParser
from apps.projects.calculation import calculateEpicStats
from apps.projects.models import Story, StoryComment, Project, Label, Epic
from apps.projects.access import has_write_access, has_read_access
from apps.projects.managers import reorderStory
import apps.projects.tasks as projects_tasks

import re
import apps.html2text as html2text


from django_redis import get_redis_connection

import logging

logger = logging.getLogger(__name__)

MIN_REPLY_LENGTH = 1
MAX_REPLY_LENGTH = 2048
ERROR_SEND_TIMEOUT = 300


def project_email_address(project):
    # key = "%s.%s" % (project.slug, project.token)
    return settings.PROJECT_EMAIL_ADDRESS % project.slug


def is_auto_responder(message):
    autoresponder_strings = ['X-Autoresponse:',
                             'X-Autorespond:',
                             'Subject: Auto Response',
                             'Out of office',
                             'Out of the office',
                             'autoreply']
    for test in autoresponder_strings:
        if test in message['raw_msg']:
            return True
    return False


def send_error_response(msg, opening, reason):
    redis = get_redis_connection('default')
    key = "failed-response-%s" % msg['from_email']

    # don't want to get in some sort of send loop, so only send one of these to each email address once every 5 minutes.
    if redis.get(key):
        return
    redis.setex(key, ERROR_SEND_TIMEOUT, 1)

    text_body = """
Hi There,

%s

    %s

You can reply to this email to contact our support team.

""" % (opening, reason)

    msg = EmailMultiAlternatives('[ScrumDo] Email command error',
                                             text_body,
                                             'support@scrumdo.com',
                                             [msg['from_email']])

    msg.send()


def get_user_with_permission(email, project):
    """Finds a user with a given email address that has at least write access
    to a given project.  Returns NONE if none are found."""
    for user in User.objects.filter(email=email):
        if has_read_access(project, user):
            return user
    return None

# def extract_field(text_body, field_name):
#     for line in

def _set_due(story, value):
    try:
        story.due_date = value
    except:
        pass

def _set_estimate(story, value):
    try:
        hour, min = value.split(":")
        story.estimated_minutes = int(hour)*60 + int(min)
    except:
        pass

def _set_epic(story, project, value):
    try:
        epic = project.epics.get(local_id=value)
        story.epic = epic
    except Epic.DoesNotExist:
        pass


def _set_labels(story, project, value):
    for label in value.split(","):
        label = label.strip()
        try:
            l = project.labels.get(name__iexact=label)
            story.labels.add(l)
        except Label.DoesNotExist:
            pass


def handle_incoming_project_email(message):
    """ Takes an inbound email and attempts to add a card to a project.
    :param message: A message dict in the mandrillapp inbound email format.
    :return: status(bool), reason(str)
    """
    if is_auto_responder(message):
        # Make sure it's not an out of office auto-reply
        return False, None

    subject = message['subject']

    if len(subject) < 3:
        return False, "Subject was too short."

    if "text" in message:
        body_text = EmailReplyParser.parse_reply(message['text'])
    elif "html" in message:
        plaintext = html2text.html2text(message['html'])
        body_text = EmailReplyParser.parse_reply(plaintext)
    else:
        body_text = ""

    to_address = message['to'][0][0]
    project_slug = to_address.split("@")[0]

    try:
        project = Project.objects.get(slug=project_slug)
    except Project.DoesNotExist:
        return False, "Not a valid project."

    from_user = get_user_with_permission(message['from_email'], project)

    if from_user is None:
        return False, "Could not find a user account with email address %s" % message['from_email']

    iteration = project.get_default_iteration()

    story = Story(summary=subject,
                  creator=from_user,
                  rank=500000,
                  local_id=project.getNextId(),
                  project=project,
                  iteration=iteration)

    story.save()
    valid_points = list(v[1] for v in project.getPointScale())
    for line in body_text.split("\n"):
        match = re.search("(assignee|due|tags|labels|points|epic|estimate): (.*)", line, re.IGNORECASE)
        if match:
            field = match.group(1).lower()
            value = match.group(2)
            body_text = body_text.replace(line, "")
            if field == 'assignee':
                story.assignees = value
            if field == 'tags':
                story.tags = value
            if field == 'labels':
                _set_labels(story, project, value)
            if field == 'due':
                _set_due(story, value)
            if field == 'epic':
                _set_epic(story, project, value)
            if field == 'estimate':
                _set_estimate(story, value)
            if field == 'points' and value in valid_points:
                story.points = value

    story.detail = escape(body_text.strip()).replace("\n", "<br/>")

    others = iteration.stories.all().order_by("rank")
    if others.count() > 0:
        modifiedOthers, modifiedList = reorderStory(story, -1, others[0].id, iteration)

    if story.epic:
        calculateEpicStats(story.epic)
        max_rank = story.epic.stories.all().aggregate(Max('epic_rank'))['epic_rank__max']
        if max_rank:
            story.epic_rank = max_rank + 5000

    story.tags += ", email-generated"
    story.save()
    projects_tasks.sendStoryAddedSignals.apply_async((story.id, from_user.id), countdown=3)
    return True, "All set"


def _handle_outlook_2013(text):
    try:
        # Outlook 2013's quoting doesn't get caught by EmailReplyParser, but it's easy to catch.
        ind = text.index('From: ScrumDo Robot')
        reply_text = text[0:ind]
    except ValueError:
        pass
    return text

def handle_incoming_story_email(message):
    """ Takes an inbound email and attempts to add a comment to a card.
    :param message: A message dict in the mandrillapp inbound email format.
    :return: status(bool), reason(str)
    """

    if is_auto_responder(message):
        # Make sure it's not an out of office auto-reply
        return False, None

    reply_text = EmailReplyParser.parse_reply(message['text'])
    reply_text = _handle_outlook_2013(reply_text)

    l = len(reply_text)
    to_address = message['to'][0][0]

    try:
        userpart = to_address.split("@")[0]
        story_id = userpart.split("-")[0]
        project_slug = "-".join(userpart.split("-")[1:])
    except:
        return False, "Could not find the card to add a comment to"

    try:
        story = Story.objects.get(id=story_id)
    except Story.DoesNotExist:
        return False, "Could not find the card to add a comment to"

    if story.project.slug != project_slug:
        return False, "Could not find the card to add a comment to"

    project = story.project

    from_user = get_user_with_permission(message['from_email'], project)

    if from_user is None:
        return False, "Could not find a user account with email address %s" % message['from_email']

    if l < MIN_REPLY_LENGTH:
        logger.info("Reply length %d not valid" % l)
        return False, "Reply too short, or reply text not found."

    if l > MAX_REPLY_LENGTH:
        logger.info("Reply length %d not valid" % l)
        return False, "Reply too long for a comment."

    # So at this point, we have a story, a user it's from, and content.  We can create the comment!
    # news items & email notificaitons are set up as post save hooks, so that's all automatic.
    comment = StoryComment(story=story,
                           user=from_user,
                           comment=reply_text)
    comment.save()

    return True, "All Set"

