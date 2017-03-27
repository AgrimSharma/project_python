from .common import *

from apps.projects.models import Label
import apps.projects.tasks as projects_tasks


class LabelHandler(BaseHandler):
    allowed_methods = ('PUT', 'POST', 'GET', 'DELETE')
    fields = ("id", "name", "color")
    write_fields = ("name", "color")
    model = Label


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        policy = Label(project=project)
        self._update(policy, data)
        policy.save()
        return policy

    def _update(self, label, data):
        for field in LabelHandler.write_fields:
            if field in data:
                setattr(label, field, data[field])

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, label_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        if label_id is not None:
            return project.labels.get(id=label_id)
        else:
            return project.labels.all()


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, label_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        label = project.labels.get(id=label_id)
        story_ids = label.stories.values_list('id', flat=True).all()
        projects_tasks.queueUpdateStoryTagsLabel(story_ids)   
        label.delete()
        return "deleted"


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, label_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        label = project.labels.get(id=label_id)
        story_ids = label.stories.values_list('id', flat=True).all()
        projects_tasks.queueUpdateStoryTagsLabel(story_ids)
        self._update(label, data)
        label.save()
        return label