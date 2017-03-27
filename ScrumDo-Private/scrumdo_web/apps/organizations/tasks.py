import logging
from apps.scrumdocelery import app
from StringIO import StringIO
from django.core.files import File
from apps.projects.models import Story, Project, FileJob
from apps.projects.calculation import delayedCalculateProject, onDemandCalculateVelocity
from apps.projects.access import write_access_or_403
from apps.organizations.models import Organization
import apps.projects.import_export as import_export
import apps.organizations.import_export as import_export
from rollbardecorator import logexception

logger = logging.getLogger(__name__)

import datetime

@app.task
def exportOrganization(job_id, organization_id, project_ids=None, start_date=None, end_date=None):
    organization = Organization.objects.get(id=organization_id)

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except:
        start_date = None
        end_date = None

    xlsf = File(StringIO())
    job = FileJob.objects.get(id = job_id)
    import_export.export_organization(organization, project_ids, start_date, end_date).save(xlsf)
    xlsf.size = xlsf.tell()
    job.attachment_file.save("organization.xls", xlsf)
    job.completed = True
    job.save()
