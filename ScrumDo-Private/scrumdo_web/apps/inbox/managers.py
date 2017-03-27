from django.contrib.auth.models import User

from apps.kanban.models import BoardCell
from apps.projects.models import Project, Story, Epic, Iteration
from apps.organizations.models import Organization
from apps.organizations import tz

import htmldiff

from .models import InboxEntry, InboxGroup

import json
import datetime


def translate_story_diffs(diffs, project, story):
    for f in ("epic_rank", "epic_label", "comment_count"):
        # Ignore these diffs..'
        if f in diffs:
            del diffs[f]

    if "iteration_id" in diffs:
        diffs["iteration"] = [None, None]
        for i in xrange(2):
            try:
                iteration = Iteration.objects.get(id=diffs["iteration_id"][i])
                diffs["iteration"][i] = iteration.name
            except Epic.DoesNotExist:
                pass
        del diffs["iteration_id"]

    if "epic_id" in diffs:
        diffs["epic"] = [None, None]
        for i in xrange(2):
            try:
                e = Epic.objects.get(id=diffs["epic_id"][i])
                diffs["epic"][i] = "%s %s" % (e.short_name(), e.summary)
            except Epic.DoesNotExist:
                pass

        del diffs["epic_id"]

    # We want the cell name, not the cell id.
    if "cell_id" in diffs:
        try:
            cell_from = project.boardCells.get(id=diffs['cell_id'][0]).full_label \
                if (diffs['cell_id'][0] is not None) else ''
            cell_to = project.boardCells.get(id=diffs['cell_id'][1]).full_label \
                if (diffs['cell_id'][1] is not None) else ''
            diffs['cell_name'] = [cell_from, cell_to]
        except BoardCell.DoesNotExist:
            pass;

    # For text fields, we don't want a before/after, we want to see a nice visual diff
    for f in ("summary", "detail", "extra_1", "extra_2", "extra_3", "tags_cache"):
        if f in diffs:
            try:
                rendered = htmldiff.render_html_diff(diffs[f][0], diffs[f][1])
                diffs[f][0] = None
                diffs[f][1] = rendered
            except:
                pass

    return diffs


def create_task_summary(project, task):
    return {
        'status': task.status,
        'assignee': task.assignee,
        'status_name': project.getTaskStatusName(task.status),
        'summary': task.summary
    }


def get_group(date, user, organization=None, project=None, story=None, epic=None, note=None):
    """ Gets an appropriate InboxGroup for the given criteria, creates one if it doesn't exist."""
    groups = []
    # InboxGroup.objects.filter(user=user, date=date)
    if story:
        groups = InboxGroup.objects.filter(user=user, date=date, story=story)
    elif epic:
        groups = InboxGroup.objects.filter(user=user, date=date, epic=epic)
    elif note:
        groups = InboxGroup.objects.filter(user=user, date=date, note=note)
    # elif project:
    #     groups = groups.filter(project=project, story__isnull=True, epic__isnull=True)
    # else:
    #     groups = groups.filter(organization=organization, project__isnull=True, story__isnull=True, epic__isnull=True)

    try:
        group = groups[0]
    except IndexError:
        group = InboxGroup(date=date, user=user, organization=organization, project=project, story=story, epic=epic, note=note)
        group.save()
    return group


def create_body(event_type, organization, project, story, message, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None

    return {
        'user': {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'id': user.id
        } if user else None,

        'event_type': event_type,

        'message': message
    }


def mark_archived(entry, auto_save=True):
    entry.status = InboxEntry.INBOX_STATUSES.archived
    if auto_save:
        entry.save()


def mark_read(entry, auto_save=True):
    if entry.status == InboxEntry.INBOX_STATUSES.unread:
        entry.status = InboxEntry.INBOX_STATUSES.read
        if auto_save:
            entry.save()


def mark_unread(entry, auto_save=True):
    entry.status = InboxEntry.INBOX_STATUSES.unread
    if auto_save:
        entry.save()


def inbox_for_user(user, project=None, organization=None):
    entries = InboxEntry.objects.filter(user=user).order_by("status", "-created")
    if project:
        entries = entries.filter(project=project)
    if organization:
        entries = entries.filter(organization=organization)
    return entries


def purge_old(days=14):
    cut_off = datetime.date.today() - datetime.timedelta(days=days)
    InboxEntry.objects.filter(created__lt=cut_off).delete()
    InboxGroup.objects.filter(date__lt=cut_off).delete()


def create_inbox_item(user, organization, project, story, subject, body, epic=None, note=None):
    date = tz.today(organization)
    group = get_group(date, user, organization, project, story, epic, note)
    item = InboxEntry(subject=subject, body=body, group=group)
    item.save()
    return item


def create_story_item(story_id, subject, body):
    story = Story.objects.get(id=story_id)
    project = story.project
    users = project.all_members()
    for user in users:
        create_inbox_item(user, project.organization, project, story, subject, body)


def create_epic_item(epic, subject, body):
    project = epic.project
    users = project.all_members()
    for user in users:
        create_inbox_item(user, project.organization, project, None, subject, body, epic);


def create_project_item(project_slug, subject, body):
    project = Project.objects.get(slug=project_slug)
    users = project.all_members()
    for user in users:
        create_inbox_item(user, project.organization, project, None, subject, body)


def create_organization_item(organization_id, subject, body):
    org = Organization.objects.get(id=organization_id)
    users = org.members()
    for user in users:
        create_inbox_item(user, org, None, None, subject, body)


def create_organization_staff_item(organization_id, subject, body):
    org = Organization.objects.get(id=organization_id)
    users = org.staff_members()
    for user in users:
        create_inbox_item(user, org, None, None, subject, body)


def create_iteration_end_item(iteration):
    project = iteration.project
    org = project.organization
    body = create_body('iteration_end', org, project, None,
                       {'iteration_id': iteration.id,
                        'iteration_name': iteration.name}, None)
    create_project_item(project.slug, u"Iteration Ended: %s" % iteration.name, json.dumps(body) )


def is_move_event(diffs):
    """Returns true if the only difference is the card moving cells/rank"""
    keys = set(diffs.keys())
    return len(keys.difference(set(('cell_id', 'cell_name', 'rank')))) == 0

def create_note_item(note, subject, body):
    project = note.project
    users = project.all_members()
    for user in users:
        create_inbox_item(user, project.organization, project, None, subject, body, None, note)
