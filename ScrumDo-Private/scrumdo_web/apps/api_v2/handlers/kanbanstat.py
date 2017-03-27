from common import *
import apps.kanban.stats as kstats
import apps.kanban.managers as kanban_manager
from apps.kanban.models import RebuildMovementJob

import datetime

class KanbanStatHandler(BaseHandler):
    allowed_methods = ('GET',)

    def _defaultStartStep(self, workflow):
        steps = workflow.steps.all()
        return steps[0].id

    def _defaultEndStep(self, workflow):
        steps = workflow.steps.all().reverse()
        return steps[0].id


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, stat_type, workflow_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        
        if RebuildMovementJob.objects.filter(project=project).count() > 0:
            # If we have a really old, stale job, let's get rid of it.
            old = datetime.date.today() - datetime.timedelta(days=2)
            RebuildMovementJob.objects.filter(project=project, created__lt=old).delete()
            return {"data": [], "locked": True}
        
        if stat_type == "burn":
            return kstats.calculateBurn(project,
                                        request.GET.get("iteration"),
                                        request.GET.get("assignee", None),
                                        request.GET.get("tag", None),
                                        request.GET.get("category", None),
                                        request.GET.get("epic", None)
                                        )

        if workflow_id == '-1':
            workflow = kanban_manager.getDefaultWorkflow(project)
        else:
            workflow = project.workflows.get(id=workflow_id)

        if stat_type == "movements":
            return kstats.calculateMovements(project,
                                             workflow,
                                             request.GET.get("storyId")
                                             )

        if stat_type == "cfd":
            return kstats.calculateCFD(project,
                                       workflow,
                                       request.GET.get("cfd_show_backlog") == 'true',
                                       request.GET.get("assignee", None),
                                       request.GET.get("tag", None),
                                       request.GET.get("label", None),
                                       request.GET.get("epic", None),
                                       request.GET.get("detail", "false") == "true",
                                       request.GET.get("yaxis", 1),
                                       request.GET.get("iteration", "ALL"),
                                       request.GET.get("startdate", None),
                                       request.GET.get("enddate", None),
                                       )
        if stat_type == "lead":
            # lead-start-step=-1&undefined=&lead-end-step=-2&interval=1&_=1382969750772
            return kstats.calculateLeadTime(project,
                                            workflow,
                                            int(request.GET.get("lead_start_step", self._defaultStartStep(workflow))),
                                            int(request.GET.get("lead_end_step", self._defaultEndStep(workflow))),
                                            int(request.GET.get("interval", -1)),
                                            request.GET.get("assignee", None),
                                            request.GET.get("tag", None),
                                            request.GET.get("label", None),
                                            request.GET.get("epic", None),
                                            request.GET.get("detail", "off") == "true",
                                            request.GET.get("startdate", None),
                                            request.GET.get("enddate", None),
                                            True,
                                            request.GET.get('cached', 'false') == 'true'
                                            )


        if stat_type == 'aging':
            return kstats.calculateAging(project,
                                         workflow,
                                         int(request.GET.get("agingType")),
                                         request.GET.get("agingData"),
                                         [int(s) if s else -1 for s in request.GET.get("agingSteps","").split(",")],
                                         set(request.GET.get("agingTags").split(",")),
                                         request.GET.get("assignee", None),
                                         request.GET.get("label", None),
                                         request.GET.get("epic", None),
                                         request.GET.get("tag", None),
                                         request.GET.get("startdate", None),
                                         request.GET.get("enddate", None),
                                         )

        if stat_type == 'backlogcfd':
            return kstats.calculateBacklogCFD(project,
                                            request.GET.get("startdate", None),
                                            request.GET.get("enddate", None),
                                            request.GET.get('cached', 'false') == 'true'
                                            )
