from .common import *
from apps.projects.models import *
from apps.projects.access import *
from apps.projects.task_utils import reorderTask
import apps.projects.signals as signals

class TaskHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    write_fields = ("complete", "summary", "tags", "estimated_minutes")
    fields = ("id",
              "complete",
              "summary",
              ("assignee", ("username", "first_name", "last_name", "id")),
              "tags",
              "order",
              "status",
              "project_slug",
              "story_id",
              "reorderResults",
              "estimated_minutes",
              "new_project_tags")

    model = Task

    @staticmethod
    def reorderResults(task):
        try:
            return task.reorderResults
        except:
            return None

    @staticmethod
    def project_slug(task):
        return task.story.project.slug

    @staticmethod
    def tags(task):
        if task.tags_cache is not None:
            return task.tags_cache
        else:
            return ""
    
    #return all new project tags, will be added to project scope
    @staticmethod
    def new_project_tags(task):
        return task.new_project_tags
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, story_id, task_id, iteration_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        task = Task.objects.get(id=task_id)
        if task.story.project != project:
            logger.debug("Project did not match %d %d" % (task.story.project.id, project.id) )
            raise ValidationError("Organization and project don't match")

        signals.task_deleted.send(sender=request, task=task, user=request.user)
        task.sync_queue.clear()
        task.delete()
        return "deleted"

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, story_id, iteration_id=None):
        data = request.data

        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        story = project.stories.get(id=story_id)

        task = Task(story=story)
        for field in TaskHandler.write_fields:
            if field in data:
                setattr(task, field, data[field])

        if "status" in data:
            try:
                newStatus = int(data['status'])
                if 1 <= newStatus <= 10:
                    task.status = newStatus
            except:
                logger.debug("Bad task status passed in")

        if "assignee" in data and data["assignee"] is not None:
            try:
                if "username" in data["assignee"]:
                    username = data["assignee"]["username"]
                else:
                    username = data["assignee"]

                user = User.objects.get(username=username)
                if has_read_access(project,user):
                    task.assignee = user
            except User.DoesNotExist:
                pass

        task.save()
        signals.task_created.send( sender=request, task=task, user=request.user )
        return task

    def _reorderTask(self, task, data, project):
        # PLEASE REMEMBER - both this and the story order handler can reorder stories, so modify both if you modify one.
        modified = []
        before_id = data["task_before_id"]
        after_id = data["task_after_id"]
        modifiedOtherTasks, modified = reorderTask(before_id, after_id, task)
        return {'modifiedOther':modifiedOtherTasks, 'newOrder':task.order, 'storiesModified':modified}


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, story_id, task_id, iteration_id=None):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, check_write_access=True)

        task = Task.objects.get(id=task_id)
        if task.story.project != project:
            raise ValidationError("Organization and project don't match")

        status_changed = False
        if task.status != data['status']:
            status_changed = True

        for field in TaskHandler.write_fields:
            if field in data:
                setattr(task, field, data[field])

        if "assignee" in data:
            if data["assignee"] is None:
                task.assignee = None
            else:
                try:
                    if "username" in data["assignee"]:
                        username = data["assignee"]["username"]
                    else:
                        username = data["assignee"]
                    user = User.objects.get(username=username)
                    if has_read_access(project,user):
                        task.assignee = user
                except User.DoesNotExist:
                    task.user = None

        if "status" in data:
            try:
                newStatus = int( data['status'] )
                if 1 <= newStatus <= 10:
                    task.status = newStatus
            except:
                logger.debug("Bad task status passed in")

        # There's a special task_id_before/task_id_after pair that can be set to affect reordering
        # of the story.  We do this last so the _reorderStory algorithm can make inferences from
        # the current story data.
        if ("task_before_id" in data) and ("task_after_id" in data):
            task.reorderResults = self._reorderTask(task, data, project)

        task.save()

        if status_changed:
            signals.task_status_changed.send(sender=request, task=task, user=request.user)
        else:
            signals.task_updated.send(sender=request, task=task, user=request.user)
        
        
        return task

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, story_id, iteration_id=None, task_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        story = project.stories.get(id=story_id)

        if task_id is None:
            return story.tasks.all().order_by("status","order")
        else:
            return story.tasks.get(id=task_id)
