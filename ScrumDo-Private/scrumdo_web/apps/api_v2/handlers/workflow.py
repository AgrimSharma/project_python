from .common import *
from apps.kanban.models import WorkflowStep, Workflow, BoardCell
import apps.kanban.tasks as kanban_tasks


class WorkflowHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    fields = ("id", "project_id", "name", "steps", "default", "flow_type")
    model = Workflow

    @staticmethod
    def steps(obj):
        return obj.steps.all()

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        workflow = Workflow(project=project, name=data["name"])
        workflow.save()

        kanban_tasks.scheduleRebuildStepMovements(project, request.user)

        return workflow

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, workflow_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        workflow = project.workflows.get(id=workflow_id)
        workflow.name = request.data["name"]
        if "default" in request.data:
            workflow.default = request.data["default"]
        workflow.save()

        kanban_tasks.scheduleRebuildStepMovements(project, request.user)

        return workflow


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, workflow_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        workflow = project.workflows.get(id=workflow_id)
        workflow.delete()

        kanban_tasks.scheduleRebuildStepMovements(project, request.user)

        return "deleted"

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, workflow_id=None ):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if workflow_id is not None:
            return project.workflows.prefetch_related("steps").get(id=workflow_id)
        else:
            return project.workflows.prefetch_related("steps").all().order_by("-flow_type", "name")


class WorkflowStepHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST',"DELETE")
    fields = ("id", "workflow_id", "name", "order", "report_color", "mapped_status")
    write_fields = ("name", "on_hold", "status_code", "order", "report_color", "mapped_status")
    model = WorkflowStep

    def _setFields(self, data, step):
        for field in WorkflowStepHandler.write_fields:
            if field in data:
                setattr(step, field, data[field])


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, workflow_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        workflow = project.workflows.get(id=workflow_id)

        workflow_step = WorkflowStep(workflow=workflow)
        self._setFields(data, workflow_step)
        workflow_step.save()

        kanban_tasks.scheduleRebuildStepMovements(project, request.user)

        return workflow_step


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, workflow_id, workflow_step_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        workflow = project.workflows.get(id=workflow_id)

        workflow_step = workflow.steps.get(id=workflow_step_id)
        workflow_step.delete()

        kanban_tasks.scheduleRebuildStepMovements(project, request.user)
        return "deleted"


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, workflow_id, workflow_step_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        workflow = project.workflows.get(id=workflow_id)
        workflow_step = workflow.steps.get(id=workflow_step_id)
        self._setFields(data, workflow_step)

        if "cells" in data:
            cells = []
            for cellId in data["cells"]:
                cell = BoardCell.objects.get(id=cellId, project=project)  # query on project to prevent shenanigans.
                cells.append(cell)
            workflow_step.cells = cells

        workflow_step.save()

        kanban_tasks.scheduleRebuildStepMovements(project, request.user)
        return workflow_step



    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, workflow_id, workflow_step_id=None, cells=False):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if cells:
            step = project.workflows.get(id=workflow_id).steps.get(id=workflow_step_id)
            return [cell.id for cell in step.cells.all()]

        if workflow_step_id is not None:
            return project.workflows.get(id=workflow_id).steps.get(id=workflow_step_id).orderBy("order")
        else:
            return project.workflows.get(id=workflow_id).steps.all().orderBy("order")

