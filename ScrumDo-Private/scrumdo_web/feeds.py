from django.contrib.syndication.views import FeedDoesNotExist
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from apps.projects.models import Project
from apps.activities.models import NewsItem
from django.conf import settings
import apps.activities.feedgenerator as feedgenerator

import logging

logger = logging.getLogger(__name__)



class ProjectStories(Feed):
    title_template = 'feeds/project_title.html'
    description_template = 'feeds/project_description.html' 

    def __init__(self):
        self.feed_type = feedgenerator.DefaultFeed
           

    def get_object(self, request, project_id, project_key):
        project = get_object_or_404(Project, pk=project_id)
        if project.token == project_key:
            return project
        else:
            return None
    
      
    def item_pubdate(self, item):
        # Returning the time the action was created, lets RSS readers sort them properly.
        return item.created

    def title(self, obj):
        return "Scrumdo - %s" % obj.name

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return "%sprojects/project/%s/" % (settings.BASE_URL,obj.slug)

    def item_enclosure_url(self, item):
        try:
            return item.get_absolute_url()
        except:
            return ""

    def item_link(self, obj):
        return "%sprojects/story_permalink/%d/" % (settings.BASE_URL,obj.pk)


    def item_guid(self, obj):
        # We need to return unique GUIDs for each activity, or RSS readers will assume they're the same entry
        return "GUID-%d" % obj.id

    def description(self, obj):
        return "Recent work in all iterations of project."

    def items(self, obj):
        if not obj.active:
            return []
        activities = NewsItem.objects.filter(project = obj)
        return activities[:60]

    def item_title(self, item):
        try:
            return "%s %s" % (item.text[:15], item.related_story.local_id)
        except:
            return "%s" % (item.text[:15])

    def item_description(self, item):
        return item.text

