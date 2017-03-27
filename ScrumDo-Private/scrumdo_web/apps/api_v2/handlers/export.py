from .common import *
from apps.projects.tasks import exportProject, exportIteration, exportTeamPlanning
from apps.projects.models import FileJob


class ProjectExportHandler(BaseHandler):
    allowed_methods = ('POST',)
    fields = ('job_id', )

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, iteration_id=None, team_slug=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, check_write_access = False)

        if iteration_id is None:
            job = FileJob(organization=org, file_type="project_export", owner=request.user, completed=False)
            job.save()
            exportProject.apply_async((project.id, organization_slug, job.id, request.data.get("filename", "export.xls")), countdown=5)
        elif team_slug is not None:
            org, team_project = checkOrgProject(request, organization_slug, team_slug, check_write_access = False)
            job = FileJob(organization=org, file_type="teamplanning_export", owner=request.user, completed=False)
            job.save()
            project.iterations.get(id=iteration_id)   # Error out if it doesn't exist in this project
            exportTeamPlanning.apply_async((iteration_id, team_project.id, organization_slug, job.id, request.data.get("filename", "export.xls")), countdown=5)
        else:
            job = FileJob(organization=org, file_type="iteration_export", owner=request.user, completed=False)
            job.save()
            project.iterations.get(id=iteration_id)   # Error out if it doesn't exist in this project
            exportIteration.apply_async((iteration_id, organization_slug, job.id, "xls", request.data.get("filename", "export.xls")), countdown=3)

        return {'job_id': job.id}

