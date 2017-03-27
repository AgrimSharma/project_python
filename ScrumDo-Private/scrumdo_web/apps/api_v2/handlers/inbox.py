from .common import *

from apps.inbox.models import InboxGroup, InboxEntry

import json


class InboxEntryHandler(BaseHandler):
    allowed_methods = ()  # just used to define the serialization
    model = InboxEntry
    fields = ('created', 'status', 'subject', 'body')
    @staticmethod
    def body(item):
        return json.loads(item.body)


class InboxGroupHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = InboxGroup
    fields = ("id", 'date', 'story', 'entries', 'epic')

    @staticmethod
    def paginate(queryset, request, customHandler=None):
        """We're going to paginate this a bit different to better support deleting entries and getting the
           next set of results without missing any based on counts.
           Instead of specifying a page to get, you specify the last record you already received.
        """
        lastRecord = int(request.GET.get("lastRecord", '0'))
        perPage = int(request.GET.get("perPage", "200"))

        totalCount = queryset.count()
        if lastRecord > 0:
            queryset = queryset.filter(id__lt=lastRecord)

        try:
            p = Paginator(queryset, perPage)
            return {'current_page': 1, 'max_page': p.num_pages, 'count': totalCount, 'items': p.page(1).object_list}
        except EmptyPage:
            return []


    @staticmethod
    def entries(group):
        return group.entries.all()

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, groupId):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        InboxGroup.objects.filter(user=request.user, project=project, id=groupId).delete()
        return "ok"


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, groupId=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        page = int(request.GET.get("page", 0))
        results = InboxGroup.objects.filter(user=request.user, project=project).order_by("-date", "-id").\
                    select_related("story",
                                   "epic",
                                   "story__epic",
                                   "story__creator",
                                   "story__project",
                                   "story__cell",
                                   "story__release").\
                    prefetch_related("story__story_tags__tag",
                                     "story__assignee",
                                     "story__project__labels",
                                     "story__extra_attributes",
                                     "entries")
        return InboxGroupHandler.paginate(results, request)

