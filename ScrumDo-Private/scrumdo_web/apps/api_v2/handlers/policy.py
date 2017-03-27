from .common import *

from apps.kanban.models import BoardCell, Policy
import apps.kanban.managers as kanban_manager


class PolicyHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', "DELETE")
    fields = ("id", "policy_type", "name", "project_id", "related_value", "user_defined", "cells", "min_related_value")
    write_fields = ("policy_type", "name", "related_value", "user_defined", "min_related_value")
    model = Policy

    @staticmethod
    def cells(policy):
        return [cell.id for cell in policy.cells.all()]

    def setCells(self, policy, cells):
        result = []
        for cellId in cells:
            cell = BoardCell.objects.get(id=cellId)
            if cell.project_id != policy.project_id:
                raise ValidationError("Cell %d not part of this project." % cellId)
            result.append(cell)

        policy.cells = result

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        policy = Policy(project=project)
        self._update(policy, data)
        policy.save()
        return policy

    def _update(self, policy, data):
        for field in PolicyHandler.write_fields:
            if field in data:
                setattr(policy, field, data[field])
        if not policy.id:
            policy.save()
        if "cells" in data:
            self.setCells(policy, data["cells"])


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, policy_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if policy_id is not None:
            return project.policies.get(id=policy_id)
        else:
            return project.policies.all()

    def _values(self, query):
        rv = []
        for policy in query:
            rv.append({'id':policy.id, 'current_value':kanban_manager.calculatePolicy(policy)})
        return rv


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, policy_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        policy = project.policies.get(id=policy_id)

        # TODO - there may be more cleanup to do here.
        policy.delete()

        return "deleted"


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, policy_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        policy = project.policies.get(id=policy_id)
        self._update(policy, data)
        policy.save()
        return policy