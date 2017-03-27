from .common import *

from apps.activities.models import NewsItem
from apps.projects.templatetags.projects_tags import silk
from apps.projects.managers import get_newsitem_cache_key
from apps.pinax.templatetags.shorttimesince_tag import shorttimesince
from apps.organizations import tz
from django_redis import get_redis_connection
from django.core.cache import cache

import datetime

class StoryNewsFeedHandler(BaseHandler):
    fields = ("created",
              "icon_html",
              "created_since",
              'local_time',
              "text",
              ("user", ('username', 'first_name', 'last_name')),
              "related_story_id","icon")
    allowed_methods = ('GET',)

    @staticmethod
    def icon_html(obj):
        return silk(obj.icon)

    @staticmethod
    def created_since(obj):
        return shorttimesince(obj.created)


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, story_id):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        story = project.stories.get(id=story_id)
        r = NewsItem.objects.filter(related_story=story).order_by("-created")
        for news in r:
            news.local_time = tz.formatDateTime(news.created, org, "%b %d, %Y %I:%M%p")
        return r


class NewsfeedHandler(BaseHandler):
    fields = ("created",
              "icon_html",
              "localTime",
              "text",
              ("user", ('id', 'username', 'first_name', 'last_name')),
              "related_story_id",
              "icon")
    allowed_methods = ('GET',)
    model = NewsItem


    # @staticmethod
    # def localTime(obj):
    #     return obj.created

    @staticmethod
    def icon_html(obj):
        return silk(obj.icon)


    @staticmethod
    def created_since(obj):
        return shorttimesince(obj.created)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        return paginate(project.newsItems.all(), request)


class GroupedNewsfeedHandler(BaseHandler):
    """ Returns newsitems, but groups them.
            1. By day
            2. By story/iteration/project
    """
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, start_day=0, end_day=0, project_slug=None, iteration_id=None):
        # If start_day = 0 and end_day = 0 we send TODAY
        # If start_day = 0 and end_day = 1 we send TODAY and yesterday
        # If start_day = 1 and end_day = 3 we send yesterday, and the 2 days before that
        #
        # Return results looks something like this:
        # [   { day:'date', data: [   { project_name: 'lkdfjsdklj',
        #                               project_slug: 'dfdsdsfsd',
        #                               entries: [
        #
        #                             {
        #                                 type: 'story',
        #                                 story: {...},
        #                                 news: [
        #                                     {user_id:324, text:"YAYA", created:"date string", icon_html:"<i class='icon'></i>"},
        #                                     {user_id:325, text:"YAYA", created:"date string", icon_html:"<i class='icon'></i>"},
        #                                     {user_id:326, text:"YAYA", created:"date string", icon_html:"<i class='icon'></i>"},
        #                                 ]
        #                             },
        #                             {
        #                                 type: 'story',
        #                                 story_id: 320947,
        #                                 news: [
        #                                     {user_id:324, text:"YAYA", created:"date string", icon_html:"<i class='icon'></i>"},
        #                                     {user_id:325, text:"YAYA", created:"date string", icon_html:"<i class='icon'></i>"},
        #                                     {user_id:326, text:"YAYA", created:"date string", icon_html:"<i class='icon'></i>"},
        #                                 ]
        #                             },
        #                             {
        #                                 type: 'project',
        #                                 project_id: 320947,
        #                                 news: [
        #                                     {user_id:324, text:"YAYA", created:"date string", icon_html:"<i class='icon'></i>"},
        #                                     {user_id:325, text:"YAYA", created:"date string", icon_html:"<i class='icon'></i>"},
        #                                     {user_id:326, text:"YAYA", created:"date string", icon_html:"<i class='icon'></i>"},
        #                                 ]
        #                             }
        #                           ]]}
        # ]
        # also...
        #  type: 'iteration', 'organization'
        #
        org = Organization.objects.get(slug=organization_slug)

        if not org.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that Organization")

        today = tz.today(org)
        endDate = today + datetime.timedelta(days=-int(start_day)+1)
        startDate = today + datetime.timedelta(days=-int(end_day) )

        CACHE_SECONDS = 43200 # one day long
        cache_key =  get_newsitem_cache_key(org, request.user, project_slug, iteration_id, start_day, end_day)
        cached_value = cache.get(cache_key)

        if cached_value:
            return cached_value

        if org.hasStaffAccess(request.user):
            if project_slug is None:
                projects = set(org.projects.filter(active=True))
            else:
                projects = set(org.projects.filter(slug=project_slug))
            
            newsItems = NewsItem.objects.filter(project__in=projects,
                                            created__gte=startDate,
                                            created__lte=endDate
                                           ).order_by("-created")
            # iteration specific
            if iteration_id is not None:
                newsItems = newsItems.filter(related_story__iteration_id=iteration_id)
        else:
            if project_slug is None:
                # get all user projects public only
                projects = get_users_projects_public_only(org, request.user)
            else:
                projects = set(org.projects.filter(slug=project_slug))

            newsItems = NewsItem.objects.filter(project__in=projects,
                                                created__gte=startDate,
                                                created__lte=endDate,
                                               ).order_by("-created")
            # iteration specific
            if iteration_id is not None:
                newsItems = newsItems.filter(related_story__iteration_id=iteration_id)

        newsItems = newsItems.select_related("related_story",
                                             "related_story__cell",
                                             "related_story__creator",
                                             "related_story__epic",
                                             "user",
                                             "project").prefetch_related("related_story__labels")
        # logger.info(newsItems.count())
        result = []
        days = {}
        entries = {}  # by entry key
        projects = {}  # by project slug
        for news in newsItems:
            day = tz.formatDateTime(news.created, org, "%b %d, %Y")
            news.localTime = tz.formatDateTime(news.created, org, "%I:%M%p").lstrip('0')
            if news.related_story_id is not None:
                entryKey = "%s-story-%d" % (day, news.related_story_id)
            elif news.project_id is not None:
                entryKey = "%s-project-%d" % (day, news.project_id)
            else:
                entryKey = "%s-general" % day

            projectKey = "%s-%s" % (day, news.project.slug)

            if not (day in days):
                days[day] = {'day': day, 'data':[]}
                result.append(days[day])

            if not (projectKey in projects):
                # project key is a day/project combined key
                p = {
                    'project_name': news.project.name,
                    'project_slug': news.project.slug,
                    'project_prefix': news.project.prefix,
                    'entries': []
                }
                projects[projectKey] = p
                days[day]['data'].append(p)

            if not (entryKey in entries):
                entries[entryKey] = self._createEntry(news, news.project)
                # days[day]['data'].append(entries[entryKey])
                projects[projectKey]['entries'].append(entries[entryKey])

            if len(entries[entryKey]['news']) < 7:
                entries[entryKey]['news'].append(self._get_news_dict(news))
            elif len(entries[entryKey]['news']) == 7:
                entries[entryKey]['truncated'] = True

            # redis = get_redis_connection('default')
            # redis.setex(_projectCalcKey(project.id), 300, True)
        
        cache.set(cache_key, result, CACHE_SECONDS)
        return result

    def _createEntry(self, news, project):
        if news.related_story_id is not None:
            news.related_story.project = project  # Cache it so the story api renderer doesn't query it.
            return {'type': 'story',
                    'story': self._get_story_dict(news.related_story),
                    'news': []}
        else:
            return {'type': 'project',
                    'project': self._get_project_dict(news.project),
                    'news': []}

    def _get_news_dict(self, news):
        r = {}
        for key in ["created", "icon", "localTime", "text"]:
            r[key] = news.__dict__[key]
        r["icon_html"] = silk(news.icon)
        r["user"] = self._get_user_dict(news.user)
        return r  

    def _get_user_dict(self, user):
        if user is None:
            return None
        r = {}
        for key in ["first_name", "id", "last_name", "username"]:
            r[key] = user.__dict__[key]
        return r

    def _get_label_dict(self, label):
        r = {}
        for key in ["id", "color", "name"]:
            r[key] =label.__dict__[key]
        return r
    
    def _get_project_dict(self, project):
        r = {}
        for key in ["name", "prefix", "slug"]:
            r["project_"+key] = project.__dict__[key]
        return r

    def _get_story_dict(self, story):
        r = {}
        r["cell"] = {}

        for key in ["id", "epic_label", "summary", "task_counts", "comment_count"]:
            r[key] = story.__dict__[key]

        r["labels"] = [ self._get_label_dict(label) for label in story.labels.all()]
        r["number"] = story.local_id
        r["points_value"] = story.points_value()
        r["points"] = story.getPointsLabel()

        r["assignee"] = [ self._get_user_dict(assignee) for assignee in story.assignee.all()]
        r["tags_list"] = story.story_tags_array()
        if story.cell is not None:
            r["cell"]["full_label"] = story.cell.full_label
            r["cell"]["color"] = story.cell.headerColor
        else:
            r["cell"] = None
        return r
