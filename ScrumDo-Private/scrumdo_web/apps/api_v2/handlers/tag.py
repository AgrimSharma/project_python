from .common import *

from apps.projects.models import StoryTag, StoryTagging, TaskTagging
from apps.projects.util import returnUniqueList
import apps.projects.tasks as projects_tasks


class TagHandler(BaseHandler):
    allowed_methods = ('PUT', 'POST', 'GET', 'DELETE')
    fields = ("id", "name")
    write_fields = ("name")
    model = StoryTag

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        tag = StoryTag(project=project)
        tag.name = data["name"]
        tag.save()
        return tag

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, tag_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        if tag_id is not None:
            return project.tags.get(id=tag_id)
        else:
            return project.tags.all()


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, tag_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        tag = project.tags.get(id=tag_id)
        story_ids = tag.stories.values_list('story_id', flat=True).all()
        task_ids = list(tag.tasks.values_list('task_id', flat=True).all())
        projects_tasks.queueUpdateStoryTagsLabel(story_ids)
        projects_tasks.queueUpdateTaskTags(task_ids)   
        tag.delete()
        return "deleted"


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, tag_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        tag = project.tags.get(id=tag_id)
        #check if we have duplicate tag and fetch all stories
        #link those stories with new tag
        existing_tags = project.tags.filter(name=data["name"]).exclude(id=tag_id)
        old_story_ids, old_tasks_ids = self._update_stories_tasks_tags(existing_tags, tag)

        tag.name = data["name"]
        tag.save()
        story_ids = list(tag.stories.values_list('story_id', flat=True).all())
        task_ids = list(tag.tasks.values_list('task_id', flat=True).all())

        projects_tasks.queueUpdateStoryTagsLabel(returnUniqueList(story_ids+old_story_ids))
        projects_tasks.queueUpdateTaskTags(returnUniqueList(task_ids+old_tasks_ids))
        
        return {"tag": tag, "dups": existing_tags}
        
    def _update_stories_tasks_tags(self, existing_tags, new_tag):
        to_update_story_ids = []
        to_update_task_ids = []
        for existing_tag in existing_tags:
            stories_to_update = existing_tag.stories.values_list('story_id', flat=True).all()
            tasks_to_update = existing_tag.tasks.values_list('task_id', flat=True).all()
            
            for story_id in stories_to_update:
                to_update_story_ids.append(story_id)
                try:
                    #story already has that tag, no need to add new one
                    StoryTagging.objects.get(tag=new_tag, story_id=story_id)
                except StoryTagging.DoesNotExist:
                    StoryTagging(tag=new_tag, story_id=story_id).save()
            
            for task_id in tasks_to_update:
                to_update_task_ids.append(task_id)
                try:
                    #task already has that tag, no need to add new one
                    TaskTagging.objects.get(tag=new_tag, task_id=task_id)
                except TaskTagging.DoesNotExist:
                    TaskTagging(tag=new_tag, task_id=task_id).save()
                    
            existing_tag.delete()
        return (to_update_story_ids, to_update_task_ids)