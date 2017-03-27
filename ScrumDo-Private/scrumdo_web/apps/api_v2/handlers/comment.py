from .common import *

from apps.pinax.templatetags.shorttimesince_tag import shorttimesince
from apps.projects.models import Story, StoryComment, NoteComment, Note
from django.contrib.auth.models import User
import apps.organizations.tz as tz


class StoryCommentHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST', 'DELETE')
    fields = ('id', 'html', 'date_submitted_since',
              'local_date_submitted',
              'date_submitted', 'comment', 'user_id',
              'user_name', 'user')
    model = StoryComment

    @staticmethod
    def local_date_submitted(comment):
        return tz.toOrganizationTime(comment.date_submitted, comment.story.project.organization)


    @staticmethod
    def date_submitted_since(obj):
        return shorttimesince(obj.date_submitted)

    @staticmethod
    def comment(comment):
        comment_text = defaultfilters.force_escape(comment.comment)
        comment_text = defaultfilters.linebreaks(comment_text)
        project = comment.story.project
        comment_text = linkStoriesVer2(comment_text, project)
        return projects_tags.urlify2(comment_text)

    @staticmethod
    def user_name(comment):
        if comment.user:
            return comment.user.username
        else:
            return "ScrumDo"

    def read(self, request, story_id):
        story = Story.objects.get(id=story_id)
        if has_read_access(story.project, request.user):
            return story.comments.all().order_by("date_submitted")
        else:
            return []

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, story_id):
        data = request.data

        story = Story.objects.get(id=story_id)

        if not has_read_access(story.project, request.user):
            raise PermissionDenied("You don't have access to that project.")


        user = request.user
        if 'author' in data:
            try:
                user = User.objects.get(username=data['author'])
            except User.DoesNotExist:
                pass


        comment = StoryComment(story=story,
                               user=user,
                               comment=data["comment"])
        comment.save()
        #update story comment count
        story.resetCommentCount()
        story.save()
        return comment
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, story_id, comment_id):
        data = request.data

        story = Story.objects.get(id=story_id)
        comment = StoryComment.objects.get(id=comment_id)
        user = request.user
        
        if comment.story != story:
            raise ValidationError("Story and comment don't match")

        if not has_read_access(story.project, request.user):
            raise PermissionDenied("You don't have access to that project.")
        
        if user.id != comment.user.id:
            raise PermissionDenied("You don't have permission to edit this comment.")
        
        comment.comment = data["comment"]
        comment.save()
        return comment

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, story_id, comment_id):

        story = Story.objects.get(id=story_id)
        comment = StoryComment.objects.get(id=comment_id)
        user = request.user

        if comment.story != story:
            raise ValidationError("Story and comment don't match")

        if not has_read_access(story.project, request.user):
            raise PermissionDenied("You don't have access to that project.")

        if user.id != comment.user.id:
            raise PermissionDenied("You don't have permission to edit this comment.")

        comment.delete()
        #update story comment count
        story.resetCommentCount()
        story.save()
        
        return "deleted"

class NoteCommentHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST', 'DELETE')
    fields = ('id', 'html', 'date_submitted_since',
              'local_date_submitted',
              'date_submitted', 'comment', 'user_id',
              'user_name', 'user')
    model = NoteComment

    @staticmethod
    def local_date_submitted(comment):
        return tz.toOrganizationTime(comment.date_submitted, comment.note.project.organization)


    @staticmethod
    def date_submitted_since(obj):
        return shorttimesince(obj.date_submitted)

    @staticmethod
    def comment(comment):
        comment_text = defaultfilters.force_escape(comment.comment)
        comment_text = defaultfilters.linebreaks(comment_text)
        project = comment.note.project
        comment_text = linkStoriesVer2(comment_text, project)
        return projects_tags.urlify2(comment_text)

    @staticmethod
    def user_name(comment):
        if comment.user:
            return comment.user.username
        else:
            return "ScrumDo"

    def read(self, request, note_id):
        note = Note.objects.get(id=note_id)
        if has_read_access(note.project, request.user):
            return note.comments.all().order_by("date_submitted")
        else:
            return []

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, note_id):
        data = request.data

        note = Note.objects.get(id=note_id)

        if not has_read_access(note.project, request.user):
            raise PermissionDenied("You don't have access to that project.")


        user = request.user
        if 'author' in data:
            try:
                user = User.objects.get(username=data['author'])
            except User.DoesNotExist:
                pass


        comment = NoteComment(note=note,
                               user=user,
                               comment=data["comment"])
        comment.save()
        return comment
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, note_id, comment_id):
        data = request.data

        note = Note.objects.get(id=note_id)
        comment = NoteComment.objects.get(id=comment_id)
        user = request.user
        
        if comment.note != note:
            raise ValidationError("Story and comment don't match")

        if not has_read_access(note.project, request.user):
            raise PermissionDenied("You don't have access to that project.")
        
        if user.id != comment.user.id:
            raise PermissionDenied("You don't have permission to edit this comment.")
            
        comment.comment = data["comment"]
        comment.save()
        return comment

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, note_id, comment_id):

        note = Note.objects.get(id=note_id)
        comment = NoteComment.objects.get(id=comment_id)
        user = request.user

        if comment.note != note:
            raise ValidationError("Story and comment don't match")

        if not has_read_access(note.project, request.user):
            raise PermissionDenied("You don't have access to that project.")

        if user.id != comment.user.id:
            raise PermissionDenied("You don't have permission to edit this comment.")

        comment.delete()
        
        return "deleted"

