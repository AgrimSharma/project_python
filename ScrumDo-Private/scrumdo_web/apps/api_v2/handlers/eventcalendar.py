from common import *
from apps.projects.models.story import Story


class EventCalenderView(BaseHandler):
    allowed_methods = ('GET',)

    exclude = ('creator', 'source')
    # don't user model field if used in another handler
    #model = Story

    # @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, project=None):
        base = Story.objects
        if project:
            org = base.filter(due_date__isnull=False,project=project)
            data = []
            for o in org:
                data.append(
                    {
                        "summary": o.summary,
                        "creator": o.creator,
                        "due_date":o.due_date.strftime('%Y-%m-%d'),
                        "created": o.created.strftime('%Y-%m-%d')
                    }
                )

            return data
        else:
            org = base.filter(due_date__isnull=False)
            data = []
            for o in org:
                data.append(
                    {
                        "summary": o.summary,
                        "creator": o.creator,
                        "due_date": o.due_date.strftime('%Y-%m-%d'),
                        "created": o.created.strftime('%Y-%m-%d')
                    }
                )

            return data
