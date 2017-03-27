from .common import *

from django.utils.html import strip_tags
from django.db.models import Count
from django.conf import settings

from apps.projects.models import *
import apps.projects.signals as signals
from apps.projects.managers import create_blocker, remove_blocker, blocker_report_data, \
story_by_blocker_reason, blocker_report_list_data, blocker_freq_data

from apps.realtime import util as realtime_util

import apps.organizations.tz as tz

import datetime

class StoryBlockerHandler(BaseHandler):
    fields = ("id",
              "card",
              "reason",
              "resolution",
              "blocked_date",
              "unblocked_date",
              "blocker",
              "unblocker",
              "resolved",
              "age",
              "external",
              "card_iteration")
    model = StoryBlocker
    allowed_methods = ('POST','GET','PUT',)
    
    @staticmethod
    def card_iteration(blocker):
        return blocker.card.iteration.name
    
    @staticmethod
    def blocked_date(blocker):
        return tz.formatDateTime(blocker.blocked_date, blocker.project.organization)

    @staticmethod
    def unblocked_date(blocker):
        return tz.formatDateTime(blocker.unblocked_date, blocker.project.organization)


    @staticmethod
    def age(blocker):
        return blocker.age
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, story_id, action = None):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        story = Story.objects.get(id=story_id)
        data = request.data
        
        if story.project != project:
            raise ValidationError("Organization and project don't match")
        
        blocker = create_blocker(story, data, request.user)
        story.block()
        
        realtime_util.send_story_patch(project, story, {'blocked':True})
        diffs = {'blocked': ('', data["reason"])}
        signals.story_updated.send(sender=request, story=story, diffs=diffs, user=request.user)
        return blocker
    
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, story_id, blocker_id = None):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        story = Story.objects.get(id=story_id)
        data = request.data
        
        if story.project != project:
            raise ValidationError("Organization and project don't match")
            
        if blocker_id == None:
            raise ValidationError("Blocker id missing")
            
        blocker = StoryBlocker.objects.get(id=blocker_id)
        blocker = remove_blocker(blocker, data["resolution"], request.user)
        
        diffs = {'unblocked': ('', data["resolution"])}
        signals.story_updated.send(sender=request, story=story, diffs=diffs, user=request.user)
        
        storyBlocker = StoryBlocker.objects.filter(card=story, resolved=0)
        if storyBlocker.count() == 0:
            story.unblock()
            realtime_util.send_story_patch(project, story, {'blocked':False})
        
        return blocker
    
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, story_id = None, action = 'blocker', iteration_id = None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        
        if iteration_id is not None:
            return StoryBlocker.objects.filter(project=project, card__iteration_id=iteration_id, resolved=False)
        
        if story_id is not None:
            #get blockers for a story or reasons for project
            story = Story.objects.get(id=story_id)
            if story.project != project:
                raise ValidationError("Organization and project don't match")

            if action == 'blocker':
                results = StoryBlocker.objects.filter(card=story).order_by("-id").select_related("project__organization")
            else:
                results = StoryBlocker.objects.filter(project=project).values("reason").distinct()
            
            return results
        elif action == "cards":
            #get cards for blocker's reason
            return story_by_blocker_reason(project,
                                            request.GET.get("reason", None),
                                            request.GET.get("assignee", None),
                                            request.GET.get("tag", None),
                                            request.GET.get("label", None),
                                            request.GET.get("epic", None),
                                            request.GET.get("startdate", None),
                                            request.GET.get("enddate", None),
                                            request.GET.get("iteration", "ALL"),
                                            )
        elif action == "reportlistdata":
            #get blockers report data for list
            return blocker_report_list_data(project,
                                            request.GET.get("assignee", None),
                                            request.GET.get("tag", None),
                                            request.GET.get("label", None),
                                            request.GET.get("epic", None),
                                            request.GET.get("startdate", None),
                                            request.GET.get("enddate", None),
                                            request.GET.get("iteration", "ALL"),
                                            )
        elif action == "reportfreq":
            #get blockers report data for list
            return blocker_freq_data(project,
                                            request.GET.get("assignee", None),
                                            request.GET.get("tag", None),
                                            request.GET.get("label", None),
                                            request.GET.get("epic", None),
                                            request.GET.get("startdate", None),
                                            request.GET.get("enddate", None),
                                            request.GET.get("iteration", "ALL"),
                                            )
        else:
            #get blockers report data
            return blocker_report_data(project,
                                      request.GET.get("assignee", None),
                                      request.GET.get("tag", None),
                                      request.GET.get("label", None),
                                      request.GET.get("epic", None),
                                      request.GET.get("startdate", None),
                                      request.GET.get("enddate", None),
                                      request.GET.get("iteration", "ALL"),
                                      )