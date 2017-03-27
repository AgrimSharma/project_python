from .common import *

from django.db.models import Count

from apps.kanban.models import BoardCell, WorkflowStep, CellMovement
import apps.kanban.tasks as kanban_tasks
import apps.kanban.managers as kanban_manager
from apps.projects.models import Story
import apps.projects.tasks as projects_tasks


class IterationCellCounts(BaseHandler):
    allowed_methods = ('GET', )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        return Story.objects.filter(project=project, iteration=iteration_id).values('cell_id').annotate(Count("id"))


class BoardCellHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', "DELETE")
    fields = ("id",
              "project_id",
              "steps",
              "cell_type",
              "order",
              "label",
              "full_label",
              "x",
              "y",
              "width",
              "height",
              "headerColor",
              "backgroundColor",
              "wip_policy_id",
              "wipLimit",
              "pointLimit",
              "layout",
              "policy_text",
              "policy_html",
              "time_type",
              "leadTime",
              "minWipLimit",
              "minPointLimit",
              )

    write_fields = ("cell_type",
                    "order",
                    "label",
                    "x",
                    "y",
                    "width",
                    "height",
                    "headerColor",
                    "backgroundColor",
                    "wip",
                    "wip_policy_id",
                    "wipLimit",
                    "pointLimit",
                    "layout",
                    "policy_text",
                    "time_type",
                    "leadTime",
                    "minWipLimit",
                    "minPointLimit",
                    )

    model = BoardCell



    @staticmethod
    def policy_html(cell):
        try:
            if cell.policy_text != "":
                return htmlify(cell.policy_text, cell.project)
        finally:
            return ""

    @staticmethod
    def steps(cell):
        return [s.id for s in cell.steps.all()]

    @staticmethod
    def cell_type(cell):
        return cell.cellType

    def setSteps(self, cell, steps):
        result = []
        for stepId in steps:
            step = WorkflowStep.objects.get(id=stepId)
            if step.workflow.project_id != cell.project_id:
                raise ValidationError("Step %d not part of this project." % stepId)
            result.append(step)
        if cell.id is None:
            cell.save()

        before = set(cell.steps.all())
        after = set(result)

        added = after.difference(before)
        removed = before.difference(after)

        kanban_manager.handleStepsRemovedFromCell(removed, cell)
        kanban_manager.handleStepsAddedToCell(added, cell)

        cell.steps = result

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        cell = BoardCell( project=project )
        self._update(cell, data)
        kanban_manager.setFullCellName(project, cell)
        cell.save()

        if "steps" in data:
            self.setSteps(cell, data["steps"])

        kanban_tasks.scheduleRebuildStepMovements(project, request.user)
        return cell

    def _update(self, cell, data):
        for field in BoardCellHandler.write_fields:
            if field in data:
                setattr(cell, field, data[field])

        if "steps" in data:
            self.setSteps(cell, data["steps"])

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, cell_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        cell = project.boardCells.get(id=cell_id)

        tcid = request.GET.get("target_cell_id", None)
        targetCell = None
        if tcid is not None:
            targetCell = project.boardCells.get(id=tcid)
            updated = CellMovement.objects.filter(cell_to=cell).update(cell_to=targetCell)
            logger.info("Updated %d movements" % updated)

        for story in cell.stories.all():
            story.cell = targetCell
            story.save()

        cell.delete()
        kanban_tasks.scheduleRebuildStepMovements(project, request.user)
        projects_tasks.rebuildCellHeaderRisks.apply_async((project, ), countdown=10)
        return "deleted"

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, cell_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        cell = project.boardCells.get(id=cell_id)
        self._update(cell, data)
        kanban_manager.setFullCellName(project, cell)
        cell.save()

        kanban_tasks.scheduleRebuildStepMovements(project, request.user)
        projects_tasks.rebuildCellHeaderRisks.apply_async((project, ), countdown=10)
        return cell



    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, cell_id=None ):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        if cell_id is None:
            return project.boardCells.prefetch_related("steps").all()
        else:
            return project.boardCells.get(id=cell_id)







