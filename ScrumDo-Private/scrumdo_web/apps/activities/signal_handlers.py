from django.template.loader import render_to_string
from django.dispatch import receiver
from django.core.urlresolvers import reverse
import sys, traceback


from apps.activities.models import *
import apps.projects.signals as signals
import apps.projects.diffs as pdiffs
from django.utils import timezone
from apps.projects.models import StoryComment, Project, Note
from django.core.cache import cache
from apps.projects.managers import get_newsitem_cache_key, clearNewsItemsCache

import logging

logger = logging.getLogger(__name__)

def _createStoryNewsItem(icon, template, **kwargs):
    try:
        story = kwargs["story"]
        project = story.project
        if project.personal:
            return
        if project.project_type == Project.PROJECT_TYPE_SCRUM:
            return

        if project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        user = kwargs["user"]
        diffs = kwargs.get("diffs", None)
        logger.debug(diffs)
        diffs = pdiffs.translate_diffs(diffs, story.project)

        if icon not in ["script_add", "script_delete"] and len(diffs) == 0:
            return


        item = NewsItem(user=user, project=story.iteration.project, icon=icon, related_story=story)

        item.text = render_to_string("activities/%s" % template, {'user': user, 'story': story, 'diffs': diffs})
        logger.debug(item.text)
        item._story = story #used to update story 'modified' field
        item.save()

        # clear today newsitems cache 
        org  = project.organization
        clearNewsItemsCache(org, project.slug)
    except Exception, e:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout)    


def _createAttachmentNewsItem(icon, template, **kwargs):
    try:
        story = kwargs["story"]
        fileData = kwargs["fileData"]
        project = story.project
        if project.personal:
            return
        if project.project_type == Project.PROJECT_TYPE_SCRUM:
            return

        if project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        user = kwargs["user"]
        item = NewsItem(user=user, project=story.iteration.project, icon=icon, related_story=story)
        item.text = render_to_string("activities/%s" % template, {'user': user, 'story': story, 'fileData': fileData})
        item.save()

        # clear today newsitems cache 
        org  = project.organization
        clearNewsItemsCache(org, project.slug)
    except:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout)    


def _createEpicNewsItem(icon, template, **kwargs):
    try:
        epic = kwargs["epic"]
        user = kwargs["user"]
        diffs = kwargs.get("diffs", None)

        if epic.project.personal:
            return
        
        if epic.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        diffs = pdiffs.translate_epic_diffs(diffs, epic.project)

        item = NewsItem(user=user, project=epic.project, icon=icon)
        item.text = render_to_string("activities/%s" % template, {'user': user, 'epic': epic, 'diffs': diffs})
        item.save()

        # clear today newsitems cache 
        project = epic.project
        org  = project.organization
        clearNewsItemsCache(org, project.slug)
    except:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout)   
        
            
def _createIterationNewsItem(icon, template, **kwargs):
    try:
        iteration = kwargs["iteration"]

        if iteration.project.personal:
            return

        if iteration.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        user = kwargs["user"]
        item = NewsItem(user=user, project=iteration.project, icon=icon)
        item.text = render_to_string("activities/%s" % template, {'user': user, 'iteration': iteration})
        item.save()

        # clear today newsitems cache 
        project = iteration.project
        org  = project.organization
        clearNewsItemsCache(org, project.slug)
    except:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout)


def _createTaskNewsItem(icon, template, **kwargs):
    try:

        task = kwargs["task"]

        if task.story.project.personal:
            return

        if task.story.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        user = kwargs["user"]
        diffs = kwargs.get("diffs", None)
        item = NewsItem(user=user, project=task.story.iteration.project, icon=icon, related_story=task.story)
        logger.debug(template)
        item.text = render_to_string("activities/%s" % template, {'user': user, 'task': task, 'diffs': diffs})
        item.save()

        # clear today newsitems cache 
        project = task.story.project
        org  = project.organization
        clearNewsItemsCache(org, project.slug)
    except:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout)    

def _createNoteNewsItem(icon, template, **kwargs):
    try:
        note = kwargs["note"]
        project = note.project
        iteration = note.iteration
        if project.personal:
            return
        if project.project_type == Project.PROJECT_TYPE_SCRUM:
            return

        if project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return

        user = kwargs["user"]
        diffs = kwargs.get("diffs", None)
        diffs = pdiffs.translate_note_diffs(diffs, project)

        if icon not in ["script_add", "script_delete"] and len(diffs) == 0:
            return 
        
        url = '{}#/iteration/{}/notes/{}'.format(reverse('project_app', kwargs={'project_slug':project.slug}), iteration.id, note.id)
        item = NewsItem(user=note.creator, project=project, icon="comment_add")
        item.text = render_to_string("activities/%s" % template, {'project':project, 'item':note, 'url':url})
        item.save()

        # clear today newsitems cache 
        org  = project.organization
        clearNewsItemsCache(org, project.slug)
    except:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout) 

@receiver(signals.project_created, dispatch_uid="newsfeed_signal_hookup")
def onProjectCreated(**kwargs):
    project = kwargs["project"]
    if project.personal:
        return

    if project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
        return

    user = kwargs["user"]
    item = NewsItem(user=user, project=project, icon='server_add')
    item.text = render_to_string("activities/project_created.txt", {'user': user, 'project': project})
    item.save()

    # clear today newsitems cache 
    org  = project.organization
    clearNewsItemsCache(org, project.slug)

@receiver(signals.story_moved, dispatch_uid="newsfeed_signal_hookup")
def onStoryMoved(**kwargs):
    _createStoryNewsItem("script_go", "move_story.txt", **kwargs)


@receiver(signals.story_created, dispatch_uid="newsfeed_signal_hookup")
def onStoryCreated(**kwargs):
    _createStoryNewsItem("script_add", "new_story.txt", **kwargs)


@receiver(signals.story_updated, dispatch_uid="newsfeed_signal_hookup")
def onStoryUpdated(**kwargs):
    _createStoryNewsItem("script_edit", "edited_story.txt", **kwargs)


@receiver(signals.attachment_added, dispatch_uid="newsfeed_signal_hookup")
def onAttachmentAdded(**kwargs):
    _createAttachmentNewsItem("script_edit", "attachment_added.txt", **kwargs)


@receiver(signals.story_deleted, dispatch_uid="newsfeed_signal_hookup")
def onStoryDeleted(**kwargs):
    _createStoryNewsItem("script_delete", "delete_story.txt", **kwargs)


@receiver(signals.epic_created, dispatch_uid="newsfeed_signal_hookup")
def onEpicCreated(**kwargs):
    _createEpicNewsItem('chart_organisation_add', 'new_epic.txt', **kwargs)


@receiver(signals.epic_deleted, dispatch_uid="newsfeed_signal_hookup")
def onEpicDeleted(**kwargs):
    _createEpicNewsItem('chart_org_delete', 'delete_epic.txt', **kwargs)


@receiver(signals.epic_updated, dispatch_uid="newsfeed_signal_hookup")
def onEpicChanged(**kwargs):
    _createEpicNewsItem('chart_organisation', 'edited_epic.txt', **kwargs)


@receiver(signals.task_created, dispatch_uid="newsfeed_signal_hookup")
def onTaskCreated(**kwargs):
    _createTaskNewsItem('drive_add', 'new_task.txt', **kwargs)


@receiver(signals.task_status_changed, dispatch_uid="newsfeed_signal_hookup")
def onTaskStatusChange(**kwargs):
    _createTaskNewsItem('drive_go', 'status_change_task.txt', **kwargs)    


@receiver(signals.task_updated, dispatch_uid="newsfeed_signal_hookup")
def onTaskUpdated(**kwargs):
    _createTaskNewsItem('drive_edit', 'edited_task.txt', **kwargs)    


@receiver(signals.task_deleted, dispatch_uid="newsfeed_signal_hookup")
def onTaskDeleted(**kwargs):
    _createTaskNewsItem('drive_delete', 'delete_task.txt', **kwargs)    


@receiver(signals.iteration_created, dispatch_uid="newsfeed_signal_hookup")
def onIterationCreated(**kwargs):
    _createIterationNewsItem("calendar_add", "new_iteration.html", **kwargs)


@receiver(signals.iteration_updated, dispatch_uid="newsfeed_signal_hookup")
def onIterationUpdated(_, iteration, user, hidden, **kwargs):
    iteration.project.update_has_iterations_hidden()


@receiver(signals.iteration_deleted, dispatch_uid="newsfeed_signal_hookup")
def onIterationDeleted(**kwargs):
    _createIterationNewsItem("calendar_delete", "delete_iteration.html", **kwargs)

@receiver(signals.note_created, dispatch_uid="newsfeed_signal_hookup")
def onNoteCreated(**kwargs):
    _createNoteNewsItem("script_add", "project_note_created.txt", **kwargs)

@receiver(signals.note_updated, dispatch_uid="newsfeed_signal_hookup")
def onNoteUpdated(**kwargs):
    _createNoteNewsItem("script_edit", "project_note_updated.txt", **kwargs)

@receiver(signals.note_deleted, dispatch_uid="newsfeed_signal_hookup")
def onNoteUpdated(**kwargs):
    _createNoteNewsItem("script_delete", "project_note_deleted.txt", **kwargs)


@receiver(models.signals.post_save, sender=StoryComment, dispatch_uid="activities-comment-post")
def onCommentPosted(**kwargs):
    t_comment = kwargs['instance']
    if hasattr(t_comment, "skip_announcements"):
        return
    try:
        story = t_comment.story
        if story.project.personal:
            return

        if story.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return
            
        item = NewsItem(user=t_comment.user, project=story.iteration.project, icon="comment_add", related_story=story)
        item.text = render_to_string("activities/comment_on_story.txt", {'story': story, 'item':t_comment})
        item.save()
        
        # clear today newsitems cache 
        project = story.project
        org  = project.organization
        clearNewsItemsCache(org, project.slug)
    except:
        logger.error("Could not create news item for a comment")
        traceback.print_exc(file=sys.stdout)
@receiver(models.signals.post_save, sender=NewsItem, dispatch_uid="update_story_modified_field")
def update_story_modified(sender, instance, created, **kwargs):
    """Updates 'story:modified' field when story creates a NewsItem entry"""
    story = getattr(instance, '_story', None)

    if created and story:
        story.modified = timezone.now()
        story.save()
