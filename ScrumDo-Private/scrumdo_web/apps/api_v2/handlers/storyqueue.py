from common import *
from apps.extras.models import StoryQueue, ExternalStoryMapping
from apps.projects.models import Story, Iteration
from apps.extras import signals
from apps.projects.managers import broadcastIterationCounts, reorderStory
from apps.kanban import managers as kanban_manager


class StoryQueueHandler(BaseHandler):
    model = StoryQueue
    allowed_methods = ('GET', 'PUT', 'POST',)
    fields = ('id',
              'extra_slug',
              'external_url',
              'imported_on',
              'modified',
              'summary',
              'detail',
              'points',
              'status',
              'extra_1',
              'extra_2',
              'extra_3',
              'external_extra',
              'archived'
              )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        result = StoryQueue.objects.filter(project=project)

        if request.GET.get('archived', None) != 'true':
            result = result.filter(archived=False)

        return paginate(result, request)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        action = data['action']

        if action == 'create':
            return self.createQueue(data, project)

        queue = project.story_queue.get(id=data['id'])

        if action == 'import':
            return self.importQueue(request, org, project, data, queue)

        if action == 'archive':
            return self.archiveQueue(queue)

        if action == 'unarchive':
            return self.unarchiveQueue(queue)

        raise Exception('Unprocessable action')

    def createQueue(self, data, project):
        write_fields = ('extra_slug',
                        'external_id',
                        'external_url',
                        'summary',
                        'detail',
                        'points',
                        'extra_1',
                        'extra_2',
                        'extra_3',
                        )
        queue = StoryQueue(project=project)
        for field in write_fields:
            if field in data:
                setattr(queue, field, data[field])
        queue.save()
        return queue

    def importQueue(self, request, org, project, data, queue):
        iteration = project.iterations.get(id=data['iteration'])
        new_story = Story(project=project, rank=0,
                          local_id=project.getNextId(),
                          summary=queue.summary,
                          detail=queue.detail,
                          extra_1=queue.extra_1,
                          extra_2=queue.extra_2,
                          extra_3=queue.extra_3,
                          status=queue.status,
                          points=queue.points,
                          iteration=iteration,
                          creator=request.user
                          )
        new_story.save()

        others = iteration.stories.all().order_by("rank")
        if others.count() > 0:
            reorderStory(new_story, -1, others[0].id, iteration)

        if iteration.iteration_type == Iteration.ITERATION_WORK:
            kanban_manager.moveStoryOntoDefaultCell(new_story, project, request.user)
        logger.debug("Added story %d" % new_story.id)
        mapping = ExternalStoryMapping(story=new_story,
                                       external_id=queue.external_id,
                                       external_url=queue.external_url,
                                       external_extra=queue.external_extra,
                                       extra_slug=queue.extra_slug)
        mapping.save()
        queue.delete()  # delete the story queue object since we just imported it.
        signals.story_imported.send(sender=request, story=new_story, story_queue=queue, user=request.user)
        broadcastIterationCounts(project)
        return queue

    def archiveQueue(self, queue):
        queue.archived = True
        queue.save()
        return queue

    def unarchiveQueue(self, queue):
        queue.archived = False
        queue.save()
        return queue