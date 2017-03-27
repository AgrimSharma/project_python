from django_redis import get_redis_connection
from tasks import send_messages, MAX_SINGLE_MESSAGE_SIZE
from apps.projects.models import Project

import calendar, datetime
import json
import hashlib

# Story syncronization messages:

# Story Created
# DATA:ADD:STORY
# {id:##, iteration:##}

# Story deleted - or story moved out of project
# DATA:DEL:STORY
# {id:##}

# Story moved iteration
# DATA:MOVED:STORY
# {id:##, iteration:##}  (the new iteration id)

# Story modified, client should reload
# DATA:SYNC:STORY
# {id:##}

# Story modified, client should update
# DATA:PATCH:STORY
# {id:##, properties:{summary:"XXX", cell_id:##, ...} }

# Task modified, client should reload
# DATA:SYNC:TASK
# {modelId:##}

# Epic Created
# DATA:ADD:EPIC
# {id:##, project:##}

# Epic Deleted
# DATA:DEL:EPIC
# {id:##, project:##}



def channelName(project):
    # 48adj$ = just some random salt
    key = '48adj$%s%d%s' % (project.slug, project.id, project.token)
    return hashlib.sha224(key).hexdigest()


def _formatDateTime(date):
    # "2015-03-21T14:07:11.777"
    return date.strftime("%Y-%m-%dT%H:%M:%S")

def send_story_modified(project, story):
    send_project_message(project, format_message('DATA:SYNC:STORY', {'id': story.id, 'modified': story.modified}))


def send_story_created(project, story):
    send_project_message(project, format_message('DATA:ADD:STORY', {'id': story.id,
                                                                    'project': story.project.slug,
                                                                    'iteration': story.iteration_id,
                                                                    'modified': story.modified}))


def send_story_delete(project, story_id):
    send_project_message(project, format_message('DATA:DEL:STORY', {'id': story_id, 'project_slug': project.slug}))


def send_release_stat_patch(release, stat):
    message = {
        'id': release.id,
        'properties': {
            'cards_total': stat.cards_total,
            'cards_completed': stat.cards_completed,
            'cards_in_progress': stat.cards_in_progress,
            'points_total': stat.points_total,
            'points_completed': stat.points_completed,
            'points_in_progres': stat.points_in_progress
        }
    }
    for project in Project.objects.filter(parents__id=release.project_id, active=True):
        send_project_message(project, format_message('DATA:PATCH:RELEASESTAT', message), 0)


def send_epic_patch(project, epic, properties):
    """ Tries to send a DATA:PATCH:EPIC message
    :param project:
    :param epic:
    :param properties:  Dict of properties/values to send updated
    :return:
    """

    # if len(json.dumps(properties, default=_default_json)) > MAX_SINGLE_MESSAGE_SIZE:
    #     # Too big for a patch message.
    #     return send_story_modified(project, story)

    message = {
        'id': epic.id,
        'properties': properties,
        # 'modified': epic.modified,
        # 'project': story.project.slug
    }
    send_project_message(project, format_message('DATA:PATCH:EPIC', message), 0)

def send_epic_created(project, epic):
    send_project_message(project, format_message('DATA:ADD:EPIC', {'id': epic.id,
                                                                    'project': project.slug}))

def send_epic_delete(project, epic_id):
    send_project_message(project, format_message('DATA:DEL:EPIC', {'id': epic_id,
                                                                    'project': project.slug}))

def send_sentiment_added(project, team, sentiment, old_id):
    send_project_message(project, format_message('DATA:ADD:SENTIMENT', {'id': sentiment.id,
                                                                    'iteration_id': sentiment.iteration.id,
                                                                    'team': team.slug,
                                                                    'properties': {'number': sentiment.number, 'reason': sentiment.reason},
                                                                    'old_id': old_id,
                                                                    'project': project.slug}))

def send_story_patch(project, story, properties):
    """ Tries to send a DATA:PATCH:STORY message, but will resort back to a
        DATA:SYNC:STORY if the data in properties is too big.
    :param project:
    :param story:
    :param properties:  Dict of properties/values to send updated
    :return:
    """
    if 'epic_id' in properties:
        if properties['epic_id']:
            properties['epic'] = {
                'id': properties['epic_id'],
                'local_id': story.epic.local_id
            }
        else:
            properties['epic'] = None

    if 'release_id' in properties:
        miletone = story.release
        if miletone is not None:
            properties['release'] = {
                'id': miletone.id,
                'number': miletone.local_id,
                'summary': miletone.summary
            }
        else:
            properties['release'] = None

    properties['iteration_id'] = story.iteration_id  # Always need this in case we have to load the story on the client

    if len(json.dumps(properties, default=_default_json)) > MAX_SINGLE_MESSAGE_SIZE:
        # Too big for a patch message.
        return send_story_modified(project, story)

    message = {
        'id': story.id,
        'properties': properties,
        'modified': story.modified,
        'project': story.project.slug
    }
    send_project_message(project, format_message('DATA:PATCH:STORY', message), 0)


def send_story_moved(project, story):
    message = {
        'id': story.id,
        'iteration': story.iteration_id,
        'project': story.project_id,
        'modified': story.modified
    }
    send_project_message(project, format_message('DATA:MOVED:STORY', message))


def format_message(message_type, payload):
    return {"client": "scrumdo",
            "type": message_type,
            "payload": payload}


def _default_json(obj):
    """Default JSON serializer."""
    if isinstance(obj, datetime.datetime):
        return _formatDateTime(obj)
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    return str(obj)

def send_project_message(project, message, wait=3):
    channel = channelName(project)
    redis = get_redis_connection()
    key = "messages-%s" % channel
    redis.rpush(key, json.dumps(message, default=_default_json))
    send_messages.apply_async((channel,), countdown=wait)


def lock_realtime_project(project):
    """Prevent realtime messages from being sent to a project for 1 minute, or until unlock_realtime_project
       is called, whichever happens first."""
    redis = get_redis_connection()
    key = "realtime-lock-%s" % channelName(project)
    redis.setex(key, 60, True)


def unlock_realtime_project(project, delay=1):
    redis = get_redis_connection()
    key = "realtime-lock-%s" % channelName(project)
    redis.setex(key, delay, True)
    # Instead of deleting the key, we set a one-second timeout.  That way,
    # the current request has time to exit.  It's probably not neccessary.
    
def send_task_modified(story, task):
    send_project_message(story.project, format_message('DATA:SYNC:TASK', {'modelId': task.id}))