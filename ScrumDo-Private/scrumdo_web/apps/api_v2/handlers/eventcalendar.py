from common import *
from apps.projects.models.story import Story


class EventCalenderView(BaseHandler):
    allowed_methods = ('GET',)

    exclude = ('creator', 'source')
    model = Story

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug=None):
        base = Story.objects
        if organization_slug:
            org = base.filter(due_date__isnull=False)
            data = []
            for o in org:
                data.append({"summary": o.summary, "creator": o.creator})

            return data
        else:
            org = base.filter(due_date__isnull=False)
            data = []
            for o in org:
                data.append({"summary":o.summary,"creator": o.creator,'due_date':o.due_date.strftime('%Y-%m-%d')})
            return data
