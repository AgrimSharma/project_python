from django.db.models import Count

from apps.projects.models import *
from apps.activities.models import *
from apps.kanban.models import *

from apps.subscription.models import Subscription

import apps.kanban.tasks as kanban_tasks
from apps.organizations.models import *
import apps.activities.utils as utils
import apps.projects.signals as signals



from apps.projects.managers import reorderStory
from apps.projects.task_utils import reorderTask
from apps.extras.manager import manager as extras_manager


import apps.kanban.managers as kanban_manager

from .common import *

import logging


logger = logging.getLogger(__name__)



class ProjectMemberHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = User
    fields = ('id', 'username','email','first_name','last_name')
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')    
    def read(self, request, organization_slug, project_slug ):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        
        return project.all_members()


class StepMovement(BaseHandler):
# Just defining this one to define sub fields of tags on other handlers
    allowed_methods = ()
    model = StepMovement
    fields = ("id","created", "story_id","step_to","step_from","date","user","iteration__id")
    @staticmethod
    def date(movement):
        return movement.created.strftime("%Y-%m-%d")

#
# class TagHandler(BaseHandler):
#     # Just defining this one to define sub fields of tags on other handlers
#     allowed_methods = ()
#     model = StoryTag
#     fields = ("id","name")


class ProjectStatsHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')    
    def read(self, request, organization_slug, project_slug ):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        return {
            'velocity': project.velocity,
            'lastStories': project.get_last_iteration_stories(),
            'lastVelocity': project.get_last_iteration_velocity()            
        }




# Special call to reorder tasks
class TaskOrderHandler(BaseHandler):
    allowed_methods = ('POST}')

    # organizations/(?P<organization_slug>[-\w]+)/projects/(?P<project_slug>[-\w]+)/stories/(?P<story_id>[0-9]+)/tasks/(?P<task_id>[0-9]+)/reorder{0,1}$
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')    
    def create(self, request, organization_slug, project_slug, story_id, task_id ):
        data = request.data
        before_id = request.REQUEST.get('before')
        after_id = request.REQUEST.get('after')

        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        
        story = Story.objects.get(id=story_id)
        if story.project != project:
            raise ValidationError("Project and story don't match")

        task = Task.objects.get(id=task_id)
        if task.story != story:
            raise ValidationError("Task and story don't match")
        
        modifiedOther, modified = reorderTask( before_id, after_id, task)

        return {'modifiedOther':modifiedOther, 'newOrder':task.order}


class BoardAttributesHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST', "DELETE")
    model = BoardAttributes
    fields = ("id", "project_id", "context", "key", "value")

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, attr_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        
        attr = BoardAttributes.objects.get(id=attr_id)
        if attr.project != project:
            raise ValidationError("Project doesn't match")

        attr.delete()       
        return "deleted"
            
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, attr_id=None):
        data = request.data

        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        
        try:
            attr = BoardAttributes.objects.get(project=project, context=data['context'], key=data['key'])
            attr.value = data['value']
            attr.save()
        except BoardAttributes.MultipleObjectsReturned:
            BoardAttributes.objects.filter(project=project, context=data['context'], key=data['key']).delete()
            attr = BoardAttributes( project=project, context=data['context'], key=data['key'], value=data['value'] )
            attr.save()
        except BoardAttributes.DoesNotExist:
            attr = BoardAttributes( project=project, context=data['context'], key=data['key'], value=data['value'] )
            attr.save()

        return attr

        
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, attr_id=None):
        return self.update( request, organization_slug, project_slug)
    
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')    
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        return project.extra_attributes.all()


class StoryAttributesHandler(BaseHandler):    
    allowed_methods = ('GET','PUT','POST', "DELETE")
    model = StoryAttributes
    fields = ("id","context","key","value")

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, story_id, attr_id, iteration_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        
        story = Story.objects.get(id=story_id)
        if story.project != project:
            raise ValidationError("Organization and project don't match")

        attr = StoryAttributes.objects.get(id=attr_id)
        if attr.story != story:
            raise ValidationError("Story doesn't match")

        attr.delete()       
        return "deleted"
            
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, story_id, iteration_id=None, attr_id=None):
        data = request.data

        org, project = checkOrgProject(request, organization_slug, project_slug)

        if not has_write_access(project, request.user):
            raise PermissionDenied("You don't have access to that Project")
        
        story = Story.objects.get(id=story_id)
        if story.project != project:
            raise ValidationError("Organization and project don't match")

        try:
            attr = StoryAttributes.objects.get(story=story, context=data['context'], key=data['key'])
            attr.value = data['value']
            attr.save()
        except StoryAttributes.DoesNotExist:
            attr = StoryAttributes( story=story, context=data['context'], key=data['key'], value=data['value'] )
            attr.save()

        return attr

        
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, story_id, iteration_id=None, attr_id=None):
        return self.update( request, organization_slug, project_slug, story_id, iteration_id=None ) # put, post do the same thing for these.
    
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')    
    def read(self, request, organization_slug, project_slug, story_id, iteration_id = None ):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        
        story = Story.objects.get(id=story_id)
        if story.project != project:
            raise ValidationError("Organization and project don't match")

        return story.extra_attributes.all()


# Special call to reorder stories.
class StoryOrderHandler(BaseHandler):
    allowed_methods = ('POST',)
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')    
    def create(self, request, organization_slug, project_slug, story_id, iteration_id=None):
        # PLEASE REMEMBER - both this and the normal story handler can reorder stories, so modify both if you modify one.
        data = request.data
        before_id = request.REQUEST.get('before')
        after_id = request.REQUEST.get('after')
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if not has_write_access(project, request.user):
            raise PermissionDenied("You don't have access to that Project")
        
        story = Story.objects.get(id=story_id)
        old_story = story.__dict__.copy()

        if story.project != project:
            raise ValidationError("Project and story don't match")

        modifiedOtherStories = reorderStory( story, before_id, after_id, story.iteration )
        diffs = utils.model_differences(old_story, story.__dict__, dicts=True)
        signals.story_updated.send( sender=request, story=story, diffs=diffs, user=request.user )
        story.save()
        return {'modifiedOther':modifiedOtherStories, 'newRank':story.rank}




class CommitHandler(BaseHandler):
    # This one is just to define the output in the story handler.
    model = Commit
    fields = ('created','name','full_text','link')




class ReleaseHandler(BaseHandler):
    fields = ("id", "name", "start_date", "delivery_date", "calculating", "order")
    write_fields = ( "name", "start_date", "delivery_date", "calculating", "order")
    allowed_methods = ('PUT',) # TODO - Being lazy for now and only implementing update - do everything else
    model = Release      
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, release_id):
        data = request.data
        org = Organization.objects.get(slug=organization_slug)
        if not has_staff_access(org, request.user):
            PermissionDenied("You don't have access to update that Organization")

        release = org.releases.get(id=release_id)

        for field in ReleaseHandler.write_fields:
            if field in data:
                setattr(release, field, data[field])
        release.save()
        return release
   



class BoardGraphicHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST',"DELETE")
    fields = ("id","project_id","graphic_type","label","sx","sy","ex","ey","foreground","background","policy_id")
    write_fields = ("graphic_type","label","sx","sy","ex","ey","foreground","background","policy_id")
    model = BoardGraphic

    def _setFields(self, data, step):
        for field in BoardGraphicHandler.write_fields:
            if field in data:                
                setattr(step, field, data[field])

        
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        graphic = BoardGraphic( project=project )
        self._setFields(data, graphic)
        graphic.save()

        return graphic


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, graphic_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        graphic = project.graphics.get(id=graphic_id)
        graphic.delete()

        return "deleted"
        
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, graphic_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        
        graphic = project.graphics.get(id=graphic_id)        
        self._setFields(data, graphic)
        graphic.save()
        return graphic
    
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')    
    def read(self, request, organization_slug, project_slug, graphic_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if graphic_id != None:
            return project.graphics.get(id=graphic_id)
        else:
            return project.graphics.all()



    # project = models.ForeignKey("projects.project",related_name='+')
    # sx = models.IntegerField()
    # sy = models.IntegerField()
    # ex = models.IntegerField()
    # ey = models.IntegerField()
    # foreground = models.IntegerField(default=0xaaaaaa)
    # background = models.IntegerField(default=0x444444)
    # policy = models.ForeignKey(Policy, null=True, default=None)    



class BoardImageHandler(BaseHandler):
    allowed_methods = ('GET','PUT',"DELETE")
    fields = ("id","sx","sy","ex","ey","url")
    write_fields = ("sx","sy","ex","ey")
    model = BoardImage

    @staticmethod
    def url(image):
        return reverse("board_image", kwargs={"project_slug":image.project.slug, "image_id":image.id} )
        # /uploader/get-board-image/test-kanban-project1/6/
        # return image.image_file.url

    def _setFields(self, data, step):
        for field in BoardImageHandler.write_fields:
            if field in data:                
                setattr(step, field, data[field])


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, image_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        image = project.images.get(id=image_id)
        image.delete()

        return "deleted"
        
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, image_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        
        image = project.images.get(id=image_id)        
        self._setFields(data, image)
        image.save()
        return image

        
    
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')    
    def read(self, request, organization_slug, project_slug, image_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if image_id != None:
            return project.images.get(id=image_id)
        else:
            return project.images.all()





class SavedQueryHandler(BaseHandler):
    model = SavedQuery
    allowed_methods = ('GET','PUT','POST',"DELETE")
    fields = ("id", "name", "query")
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request):
        data = request.data
        q = SavedQuery(creator=request.user, name=data["name"], query=data["query"])
        q.save()
        return q

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')    
    def read(self, request):
        return SavedQuery.objects.filter(creator=request.user).order_by("name")

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, query_id):
        data = request.data
        q = SavedQuery.objects.get(id=query_id, creator=request.user)
        q.delete()        
        return "deleted"
        
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, query_id):
        data = request.data
        q = SavedQuery.objects.get(id=query_id, creator=request.user)
        q.name = data["name"]
        q.query = data["query"]
        q.save()
        return q






