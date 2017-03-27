from .common import *
from apps.projects.models import FileJob, OfflineJob


class JobHandler(BaseHandler):
    model = FileJob
    fields = ("completed", "url", "result")

    @staticmethod
    def url(job):
        if not job.completed:
            return None
        return job.attachment_file.url

    def read(self, request, job_id):
        job = FileJob.objects.get(id=job_id)
        if job.owner is not None and job.owner != request.user:
            raise PermissionDenied("You don't have access to that file")
        return job


class OfflineJobHandler(BaseHandler):
    model = OfflineJob
    fields = ("completed",)

    def read(self, request, job_id):
        job = OfflineJob.objects.get(id=job_id)
        if job.owner != request.user:
            raise PermissionDenied("You don't have access to that file")
        return job