from common import *
from django.db.models import Max, Q

import apps.kanban.managers as kanban_manager
from apps.kanban.models import Workflow, KanbanStat, BoardCell
from apps.activities.models import NewsItem
from apps.projects.models import Iteration, ProjectShare, StoryBlocker
from apps.favorites.models import Favorite

from .story import storyWithoutAssigneeHandler

def _storiesForShare(share):
    if share.all_cards:
        return share.iteration.stories.all()
    else:
        return share.iteration.stories.filter(story_tags__tag__name__iexact=share.tag)

def _checkFieldsPrivacy(share):
    stories = _storiesForShare(share)
    for story in stories:
        if not share.assignee:
            story.apiMapper = storyWithoutAssigneeHandler
            # story.assignee = []
            pass
        if not share.summary:
            story.summary = ""
        if not share.detail:
            story.detail = ""
        if not share.custom1 and story.extra_1:
            story.extra_1 = ""
        if not share.custom2 and story.extra_2:
            story.extra_2 = ""
        if not share.custom3 and story.extra_3:
            story.extra_3 = ""
        if not share.time_estimates:
            story.estimated_minutes = 0
        if not share.points:
            story.points = "?"
        if not share.epic:
            story.epic = None
            story.epic_label = ""
        if not share.business_value:
            story.business_value = 0
        if not share.comments:
            story.comment_count = 0
        if not share.tasks:
            story.task_counts = "0,0,0,0,0,0,0,0,0,0"
    return stories

def _checkPrivacyEnabled(share, story):
    flag = False
    if not share.assignee:
        flag = True
    if not share.summary:
        flag = True
    if not share.detail:
        flag = True
    if not share.custom1 and story.extra_1:
        flag = True
    if not share.custom2 and story.extra_2:
        flag = True
    if not share.custom3 and story.extra_3:
        flag = True
    if not share.time_estimates:
        flag = True
    if not share.points:
        flag = True
    if not share.epic:
        flag = True
    if not share.business_value:
        flag = True
    if not share.comments:
        flag = True
    if not share.tasks:
        flag = True
    return flag

def _filter_comments(story):
    return story.comments.all().exclude(comment__iregex=r'\[private\]')

def _filter_news_items(story):
    return NewsItem.objects.filter(related_story=story).exclude(text__iregex=r'\[private\]')
    
def _filter_blockers_items(story):
    return StoryBlocker.objects.filter(card=story).order_by("-id")

class SharedStoryHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(60, 60, 'anon_reads')
    def read(self, request, story_id, share_key, *args, **kwargs):
        share = ProjectShare.objects.get(key=share_key)
        story = _storiesForShare(share).get(id=story_id)
        comments = [] if not share.comments else _filter_comments(story)
        tasks = [] if not share.tasks else story.tasks.all()
        news = [] if _checkPrivacyEnabled(share, story) else _filter_news_items(story)
        aging = tuple(kanban_manager.get_aging_info(story))
        blockers = _filter_blockers_items(story)
        return {
            'news': news,
            'comments': comments,
            'attachments': story.attachments.all(),
            'tasks': tasks,
            'aging': aging,
            'blockers': blockers
        }


class SharedProjectHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(20, 60, 'anon_reads')
    def read(self, request, share_key, *args, **kwargs):
        share = ProjectShare.objects.get(key=share_key)
        stories = _checkFieldsPrivacy(share)
        return {
            'project': share.project,
            'boardCells': share.project.boardCells.all(),
            'boardHeaders': share.project.headers.all(),
            'workflows': share.project.workflows.all(),
            'stories': stories,
            'iterations': [share.iteration],
            'epics': share.project.epics.all()  # TODO - let's filter this down to the ones used.
        }
