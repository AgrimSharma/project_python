from .common import *
from apps.kanban.models import BoardHeader, BoardCell
import apps.kanban.managers as kanban_manager
import apps.projects.tasks as projects_tasks


class BoardHeaderHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST',"DELETE")
    fields = ("id","sx","sy", "ex", "ey", "label", "background", "policy_id", "policy_text", "policy_html")
    write_fields = ("sx","sy", "ex", "ey", "label", "background", "policy_id", "policy_text")
    model = BoardHeader

    def _setFields(self, data, step):
        for field in BoardHeaderHandler.write_fields:
            if field in data:
                setattr(step, field, data[field])

    @staticmethod
    def policy_html(header):
        try:
            if header.policy_text != "":
                return htmlify(header.policy_text, header.project)
            return ""
        except:
            return ""

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        header = BoardHeader(project=project)
        self._setFields(data, header)
        header.save()

        return header

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, header_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        header = BoardHeader.objects.get(project=project, id=header_id)
        if header.policy:
            header.policy.delete()
        header.delete()
        
        self._update_project_cells_fullname(project)
        projects_tasks.rebuildCellHeaderRisks.apply_async((project, ), countdown=10)
        return "deleted"

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, header_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        header = BoardHeader.objects.get(project=project, id=header_id)
        self._setFields(data, header)
        header.save()

        self._update_project_cells_fullname(project)
        projects_tasks.rebuildCellHeaderRisks.apply_async((project, ), countdown=10)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, header_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if header_id is not None:
            return BoardHeader.objects.get(project=project, id=header_id)
        else:
            return BoardHeader.objects.filter(project=project)

    def _update_project_cells_fullname(self, project):
        cells = BoardCell.objects.filter(project = project)
        for cell in cells:
            kanban_manager.setFullCellName(project, cell)
            cell.save()
            