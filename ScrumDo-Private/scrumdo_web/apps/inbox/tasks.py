from apps.scrumdocelery import app
from apps.projects.models import Project, Story, Task, Iteration, Epic, StoryComment, Note, NoteComment

import managers
import datetime

import json
import decimal

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%b %d %Y %H:%M:%S")
    raise TypeError

@app.task
def on_comment_posted(comment_id):
    comment = StoryComment.objects.get(id=comment_id)
    story = comment.story
    project = story.project
    body = managers.create_body('comment_posted', project.organization, project, story,
                                {'text': comment.comment}, comment.user_id)
    managers.create_story_item(story.id, u"New Comment", json.dumps(body))


@app.task
def purge_old_inbox_items_job():
    managers.purge_old()


@app.task
def on_epic_created(epic_id, user_id):
    epic = Epic.objects.get(id=epic_id)
    project = epic.project
    body = managers.create_body('epic_created', project.organization, project, None, None, user_id)
    managers.create_epic_item(epic, u"Created: %s" % epic.summary, json.dumps(body))


@app.task
def on_epic_updated(epic_id, user_id, diffs):
    epic = Epic.objects.get(id=epic_id)
    project = epic.project
    body = managers.create_body('epic_edited', project.organization, project, None,
                                managers.translate_story_diffs(diffs, project, epic), user_id)
    managers.create_epic_item(epic, u"Epic edited", json.dumps(body))


@app.task
def on_project_created(project_slug, user_id):
    project = Project.objects.get(slug=project_slug)
    body = managers.create_body('project_created', project.organization, project, None, None, user_id)
    managers.create_project_item(project_slug, u"%s created" % project.name, json.dumps(body))


@app.task
def on_story_updated(story_id, user_id, diffs):
    story = Story.objects.get(id=story_id)
    project = story.project
    diffs = managers.translate_story_diffs(diffs, project, story)
    if len(diffs) == 0:
        return

    if managers.is_move_event(diffs):
        # A special case, if we only change the cell, we want to call that a cell moved event, not card edited.
        body = managers.create_body('card_moved', project.organization, project, story, diffs, user_id)
        if 'cell_name' in diffs:
            managers.create_story_item(story_id, u"Card moved to %s" % diffs['cell_name'][1], json.dumps(body))
        else:
            managers.create_story_item(story_id, u"Card moved", json.dumps(body))
    else:
        body = managers.create_body('card_edited', project.organization, project, story, diffs, user_id)
        managers.create_story_item(story_id, u"Card edited", json.dumps(body, default=decimal_default))


@app.task
def on_story_deleted(story_id, user_id):
    pass
    # story = Story.objects.get(id=story_id)
    # project = story.project
    # body = managers.create_body('card_deleted', project.organization, project, story, diffs, user_id)
    # managers.create_story_item(story_id, u"Card edited", json.dumps(body))


@app.task
def on_story_created(story_id, user_id):
    story = Story.objects.get(id=story_id)
    project = story.project
    body = managers.create_body('card_created', project.organization, project, story, None, user_id)
    managers.create_story_item(story_id, u"Card created", json.dumps(body))


@app.task
def on_story_moved(story_id, user_id, diffs):
    story = Story.objects.get(id=story_id)
    project = story.project
    body = managers.create_body('card_moved', project.organization, project, story, diffs, user_id)
    managers.create_story_item(story_id, u"Card Moved", json.dumps(body))


@app.task
def on_task_created(task_id, user_id):
    task = Task.objects.get(id=task_id)
    story = task.story
    project = story.project
    body = managers.create_body('task_created', project.organization, project, story,
                                managers.create_task_summary(project, task), user_id)
    managers.create_story_item(story.id, u"Task Created", json.dumps(body))


@app.task
def on_task_status_changed(task_id, user_id):
    task = Task.objects.get(id=task_id)
    story = task.story
    project = story.project
    body = managers.create_body('task_status', project.organization, project, story,
                                managers.create_task_summary(project, task),
                                user_id)

    managers.create_story_item(story.id, u"Task Status Changed", json.dumps(body))


@app.task
def on_task_updated(task_id, user_id):
    task = Task.objects.get(id=task_id)
    story = task.story
    project = story.project
    body = managers.create_body('task_updated', project.organization, project, story,
                                managers.create_task_summary(project, task),
                                user_id)

    managers.create_story_item(story.id, u"Task Modified", json.dumps(body))


@app.task
def on_iteration_created(iteration_id, user_id):
    iteration = Iteration.objects.get(id=iteration_id)
    project = iteration.project
    body = managers.create_body('iteration_created', project.organization, project, None,
                                {'iteration_name': iteration.name,
                                 'iteration_id': iteration.id,
                                 'start_date': iteration.start_date.strftime("%Y-%m-%d") if iteration.start_date is not None else None,
                                 'end_date': iteration.end_date.strftime("%Y-%m-%d") if iteration.end_date is not None else None
                                 },
                                user_id)

    managers.create_project_item(project.slug, u"Iteration Created", json.dumps(body))


@app.task
def on_iteration_updated(iteration_id, user_id, hidden):
    iteration = Iteration.objects.get(id=iteration_id)
    project = iteration.project
    body = managers.create_body('iteration_updated', project.organization, project, None,
                                {'iteration_name': iteration.name,
                                 'iteration_id': iteration.id,
                                 'start_date': iteration.start_date.strftime("%Y-%m-%d") if iteration.start_date is not None else None,
                                 'end_date': iteration.end_date.strftime("%Y-%m-%d") if iteration.end_date is not None else None
                                },
                                user_id)

    managers.create_project_item(project.slug, u"Iteration Updated", json.dumps(body))


@app.task
def on_attachment_added(story_id, user_id, fileData):
    story = Story.objects.get(id=story_id)
    project = story.project
    body = managers.create_body('attachment_added', project.organization, project, story, fileData, user_id)
    managers.create_story_item(story_id, u"Attachment Added", json.dumps(body))


@app.task
def on_note_created(note_id, isUpdated = False):
    note = Note.objects.get(id=note_id)
    project = note.project
    body = managers.create_body('note_created', project.organization, project, None,
                                {'text': note.title, 'note_id': note.id}, note.creator.id)
    if isUpdated == False:
        managers.create_note_item(note, u"Note Created", json.dumps(body))
    else:
        managers.create_note_item(note, u"Note Updated", json.dumps(body))

@app.task
def on_note_deleted(note_id):
    note = Note.objects.get(id=note_id)
    project = note.project
    body = managers.create_body('note_deleted', project.organization, project, None,
                                {'text': note.title, 'note_id': note.id}, note.creator.id)
    managers.create_note_item(note, u"Note Deleted", json.dumps(body))

@app.task
def on_note_comment_posted(comment_id):
    comment = NoteComment.objects.get(id=comment_id)
    note = comment.note
    project = note.project
    body = managers.create_body('comment_posted', project.organization, project, None,
                                {'text': comment.comment}, comment.user_id)
    managers.create_note_item(note, u"New Comment", json.dumps(body))

@app.task
def on_note_attachment_added(note, user_id, fileData):
    project = note.project
    body = managers.create_body('attachment_added', project.organization, project, None, fileData, user_id)
    managers.create_note_item(note, u"Attachment Added", json.dumps(body))
