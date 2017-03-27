from .common import *
import apps.kanban.managers as kanban_manager


class KanbanBoardHandler(BaseHandler):
    allowed_methods = ('POST','GET')

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, action):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        if action == "copy":
            other = Project.objects.get(slug=data["other_project"])
            if (other.organization == project.organization) or (other.organization.slug == "scrumdo-system"):
                # scrumdo-system is a special organization made just for templates.
                return kanban_manager.copyProject(other, project)
        elif action == "reset":
            return kanban_manager.reset(project)
        elif action == "wizard":
            return kanban_manager.wizard(project, data)
        return None

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, action, template_type=1):
        checkOrgProject(request, organization_slug, project_slug, False)
        if action == "templates":
            return Project.objects.filter(organization__slug="scrumdo-system", project_type=template_type)
        return None

