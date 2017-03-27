
from django.db.models import Count

from .common import *

from apps.projects.models import Epic, Iteration, Story
from apps.projects.calculation import calculateEpicStats
import apps.projects.tasks as projects_tasks
from apps.projects import signals
import apps.activities.utils as utils
from apps.realtime import util as realtime_util


class EpicHandler(BaseHandler):
    fields = ("stats", "archived", "parent_id", "story_count", "detail", "summary", "points", "order", "id", "number", "short_name", "detail_html", 'release')
    write_fields = ( "archived", "detail", "parent_id", "points", "summary", "order" )
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Epic

    @staticmethod
    def release(epic):
        if epic.release_id is None:
            return None
        return {
            'id': epic.release.id,
            'number': epic.release.local_id,
            'summary': epic.release.summary
        }

    @staticmethod
    def stats(epic):
        return {
            'cards_total': epic.cards_total,
            'cards_completed': epic.cards_completed,
            'cards_in_progress': epic.cards_in_progress,
            'points_total': epic.points_total,
            'points_completed': epic.points_completed,
            'points_in_progress': epic.points_in_progress
        }

    @staticmethod
    def detail_html(epic):
        return htmlify(epic.detail, epic.project)

    @staticmethod
    def story_count(epic):
        if hasattr(epic,"stories__count"):
            return epic.stories__count   # the bulk read annotates the records with this.
        else:
            return epic.stories.count()

    @staticmethod
    def parent_id(epic):
        return epic.parent_id

    @staticmethod
    def number(epic):
        return epic.local_id

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, epic_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        epic = Epic.objects.get(id=epic_id)

        release = epic.release

        if release:
            self._reindexStories(epic)

        if epic.project != project:
            raise ValidationError("Organization and project don't match")

        for story in epic.stories.all():
            story.epic = None
            story.resetCounts()

        for child in epic.children.all():
            child.parent = None
            child.save()

        signals.epic_deleted.send(sender=request, epic=epic, user=request.user)
        parent = epic.parent
        epic.delete()

        if parent is not None:
            calculateEpicStats(parent)

        if release:
            projects_tasks.queueMacroStatsCalc(None, release.id)
        realtime_util.send_epic_delete(project, epic_id)
        return "deleted"

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if not has_write_access(project, request.user):
            raise PermissionDenied("You don't have access to that Project")

        epic = Epic(project=project)
        epic.local_id = project.getNextEpicId()

        lastEpic = project.epics.all().order_by("-order")[:1]


        for field in EpicHandler.write_fields:
            if field in data:
                setattr(epic, field, data[field])

        if "release" in data:
            if data["release"] is not None:
                epic.release_id = data["release"].get("id", None)
                projects_tasks.queueMacroStatsCalc(None, epic.release_id)


        if len(lastEpic) == 0:
            epic.order = 10
        else:
            epic.order = lastEpic[0].order + 10

        epic.save()
        realtime_util.send_epic_created(project, epic)
        signals.epic_created.send(sender=request, epic=epic, user=request.user)
        return epic

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, epic_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        epic = Epic.objects.get(id=epic_id)

        old_epic = epic.__dict__.copy()

        previousParent = epic.parent
        if epic.project != project:
            raise ValidationError("Organization and project don't match")

        for field in EpicHandler.write_fields:
            if field in data:
                setattr(epic, field, data[field])

        if "release" in data:
            if epic.release_id is not None:
                projects_tasks.queueMacroStatsCalc(None, epic.release_id)

            if data["release"] is None:
                epic.release_id = None
            else:
                epic.release_id = data["release"].get("id", None)
                projects_tasks.queueMacroStatsCalc(None, epic.release_id)
            self._reindexStories(epic)

        epic.save()

        epic = Epic.objects.get(id=epic_id)

        if previousParent != epic.parent:
            if previousParent is not None:
                calculateEpicStats(previousParent)
            if epic.parent is not None:
                calculateEpicStats(epic.parent)

        diffs = utils.model_differences(old_epic, epic.__dict__, ["modified", "_state"], dicts=True)

        props = {k: v[1] for k, v in diffs.iteritems()}

        realtime_util.send_epic_patch(project, epic, props)
        signals.epic_updated.send(sender=request, epic=epic, user=request.user, diffs=diffs)
        return epic

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, epic_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if epic_id != None:
            return project.epics.annotate(Count('stories')).get(id=epic_id)
        else:
            return project.epics.all().select_related("project", 'parent', 'release').annotate(Count('stories'))

    def _reindexStories(self, epic):
        for story in epic.stories.all():
            projects_tasks.queueUpdateSolr(story.id)

class EpicStatsHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, epic_id = None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        result = []
        if epic_id is None:
             cards = project.stories.all().values('epic', 'iteration').annotate(totalcards = Count('iteration')).order_by()
             result.extend(list(cards))
             return [{'totalcards':c['totalcards'], 'epic':c['epic'] if c['epic'] is not None else -1 , 'iteration':c['iteration']} for c in cards]
        else:
            # for non epic stories
            if int(epic_id) == -1:
                noEpicCards = project.stories.filter(epic=None).values('epic', 'iteration').annotate(totalcards = Count('iteration')).order_by()
                return [{'totalcards':c['totalcards'], 'epic':c['epic'] if c['epic'] is not None else -1 , 'iteration':c['iteration']} for c in noEpicCards]
            else:
                epicCards = project.stories.filter(epic_id=epic_id).values('epic', 'iteration').annotate(totalcards = Count('iteration')).order_by()
                return [{'totalcards':c['totalcards'], 'epic':c['epic'] if c['epic'] is not None else -1 , 'iteration':c['iteration']} for c in epicCards]