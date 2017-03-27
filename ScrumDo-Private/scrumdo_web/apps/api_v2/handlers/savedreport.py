from .common import *

from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User

import apps.kanban.stats as kstats

from apps.kanban.models import SavedReport, WorkflowStep, RebuildMovementJob
from apps.projects.access import read_access_or_403
from apps.organizations import tz
from apps.projects.managers import blocker_report_data, blocker_report_list_data, blocker_freq_data

import datetime


def _translateDate(date_format, created, date):
    if isinstance(date, basestring):
        parts = [int(s) for s in date.split("-")]
        if len(parts) != 3:
            return None
        date = datetime.date(parts[0], parts[1], parts[2])

    if date_format == SavedReport.DATE_FORMAT_TYPES.fixed:
        return date

    if date is None:
        return date

    # We need a relative date...
    diff = created - date
    # TODO - do we need the organization date here?

    return datetime.date.today() - diff


class SavedReportHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')
    write_fields = ("report_type",
                    "y_axis",
                    "cfd_show_backlog",
                    "tag",
                    "name",
                    "date_format",
                    "interval",
                    "startdate",
                    "enddate",
                    "iteration_id")
    fields = ("id",
              "name",
              "workflow_id",
              "project_id",
              ("creator", ("username", "first_name", "last_name", "id")),
              "report_type",
              "y_axis",
              "lead_start_step_id",
              "lead_end_step_id",
              "cfd_show_backlog",
              "assignee_id",
              "epic_id",
              "label_id",
              "tag",
              "iteration_id",
              "last_generated",
              "views",
              "date_format",
              "interval",
              "startdate",
              "enddate",
              "iteration_id",
              "burn_type",
              "aging_by",
              "aging_tags",
              "aging_steps",
              "aging_type",
              "generated",
              "assignees",
              )

    model = SavedReport

    @staticmethod
    def epic_id(obj):
        return obj.epic_id
        
    @staticmethod
    def assignee_id(obj):
        return obj.assignee_id

    @staticmethod
    def label_id(obj):
        return obj.label_id
        
    @staticmethod
    def startdate(obj):
        return _translateDate(obj.date_format, obj.created, obj.startdate)

    @staticmethod
    def enddate(obj):
        return _translateDate(obj.date_format, obj.created, obj.enddate)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, report_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        savedReport = SavedReport.objects.get(id=report_id)

        if request.user == savedReport.creator or org.hasStaffAccess(request.user):
            savedReport.delete()
            return "deleted"

        raise PermissionDenied('You can not delete this saved report.')

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug)

        report = SavedReport(project=project, creator=request.user)

        for field in SavedReportHandler.write_fields:
            if field in data:
                setattr(report, field, data[field])

        project_relations = (
            ('workflow', project.workflows),
            ('lead_start_step', WorkflowStep.objects.filter(workflow__project=project)),
            ('lead_end_step', WorkflowStep.objects.filter(workflow__project=project)),
            ('epic', project.epics),
            ('label', project.labels)
        )

        report.aging_by = 0 if data.get("agingData") == "step" else 1
        report.aging_steps = data.get("agingSteps")


        report.aging_tags = data.get('agingTags', '')
        report.aging_type = data.get('agingType', "1")

        if report.report_type != 'lead':
            report.iteration_id = data.get('iteration', None)

        report.burn_type = data.get('burn_type', 0)

        for relation in project_relations:
            relation_id = data.get(relation[0], None)

            # See if the value was passed in
            if relation_id is None:
                continue

            # If it was, try to get it from our project.
            try:
                obj = relation[1].get(id=relation_id)
            except ObjectDoesNotExist:
                continue

            # Finaly, set it
            setattr(report, relation[0], obj)

        assignee_ids = data.get("assignee", None)
        filtered_assignees = []
        
        if len(assignee_ids) > 0:
            ids = [int(x) for x in assignee_ids.split(',')] 
            for user in User.objects.filter(id__in=ids):
                read_access_or_403(project, user)
                filtered_assignees.append(user)
        report.save()
      
        for user in filtered_assignees:
          report.assignees.add(user) #Were going to add assignees here     
        return report

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, report_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if report_id is not None:
            return SavedReport.objects.get(id=report_id, project=project)
        else:
            return SavedReport.objects.filter(project=project)


class RunSavedReportHandler(BaseHandler):
    allowed_methods = ('GET',)
    def read(self, request, organization_slug, project_slug, report_id,iteration_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        report = SavedReport.objects.get(id=report_id, project=project)
        iteration = None
        iteration_forced = iteration_id is not None

        if iteration_id is None:
            # We're going to let people override what iteration they are running a saved report for
            iteration = report.iteration
            iteration_id = iteration.id if iteration is not None else 'ALL'
        else:
            iteration_id = int(iteration_id)
            iteration = project.iterations.get(id=iteration_id)

        epic = report.epic
        epic_id = epic.id if epic is not None else None

        label = report.label
        label_id = label.id if label is not None else None

        assignee = report.assignee
        assignee_id = assignee.id if assignee is not None else None

        enddate_d = _translateDate(report.date_format, report.created, report.enddate)
        enddate = enddate_d.strftime('%Y-%m-%d') if enddate_d is not None else None

        startdate_d = _translateDate(report.date_format, report.created, report.startdate)
        startdate = startdate_d.strftime('%Y-%m-%d') if startdate_d is not None else None

        
            
        if iteration_forced and iteration.end_date is not None and iteration.start_date is not None and \
                (iteration.start_date > enddate_d or iteration.end_date < startdate_d):
            logger.debug("Forcing saved report dates to iteration start/end")
            # We forced the iteration, but the dates don't fall within that iteration.
            startdate = iteration.start_date.strftime('%Y-%m-%d')
            enddate = iteration.end_date.strftime('%Y-%m-%d')

        cached = kstats.get_cached_saved_report(report, org, iteration_id)
        if request.GET.get("refresh", None) != 'true':
            if cached and (report.report_type != 'blocklist' and report.report_type != 'blockfreq'):
                report.views += 1
                report.save()
                return cached
                
        if (RebuildMovementJob.objects.filter(project=project).count() > 0 and (report.report_type == 'cfd' or report.report_type == 'lead' or \
            report.report_type == 'aging')):
            return {
                    'report_type': report.report_type,
                    'name': report.name,
                    'updated_at': tz.formatDateTime(datetime.datetime.now(), org),
                    'report_id': report.id,
                    'data': [],
                    'locked': True
                    }

        if report.report_type == 'cfd':
            data = kstats.calculateCFD(project,
                                   report.workflow,
                                   report.cfd_show_backlog,
                                   assignee_id,
                                   report.tag,
                                   label_id,
                                   epic_id,
                                   False,
                                   report.y_axis,
                                   iteration_id,
                                   startdate,
                                   enddate
                                   )
        elif report.report_type == 'lead':
            data = kstats.calculateLeadTime(project,
                                            report.workflow,
                                            report.lead_start_step_id,
                                            report.lead_end_step_id,
                                            report.interval,
                                            assignee_id,
                                            report.tag,
                                            label_id,
                                            epic_id,
                                            False,
                                            startdate,
                                            enddate,
                                            )
        elif report.report_type == 'aging':
            data = kstats.calculateAging(project,
                                         report.workflow,
                                         report.aging_type,
                                         "step" if report.aging_by == 0 else "tag",
                                         [int(s) if s else -1 for s in report.aging_steps.split(",")],
                                         report.tag,
                                         assignee_id,
                                         label_id,
                                         epic_id,
                                         report.aging_tags,
                                         startdate,
                                         enddate,
                                         )
        elif report.report_type == 'burn':

            if iteration_id == 'ALL' or iteration_id is None:
                data = kstats.calculateLegacyProjectBurn(project)

            else:
                data = kstats.calculateLegacyIterationBurn(project, iteration)
                # data = kstats.calculateBurn(project,
                #                         iteration_id,
                #                         assignee_id,
                #                         '',  # This is odd, you can't filter by these for burndown charts, why are they in the call?
                #                         '',
                #                         ''
                #                         )
                
        elif report.report_type == 'block':
            data = blocker_report_data(project,
                                      assignee_id,
                                      report.tag,
                                      label_id,
                                      epic_id,
                                      startdate,
                                      enddate,
                                      iteration_id,
                                      )

        elif report.report_type == "blockfreq":
            data = blocker_freq_data(project,
                                    assignee_id,
                                    report.tag,
                                    label_id,
                                    epic_id,
                                    startdate,
                                    enddate,
                                    iteration_id,
                                    )

        elif report.report_type == 'blocklist':
            data = blocker_report_list_data(project,
                                      assignee_id,
                                      report.tag,
                                      label_id,
                                      epic_id,
                                      startdate,
                                      enddate,
                                      iteration_id,
                                      )

        report.last_generated = datetime.datetime.now()
        report.views += 1
        report.save()


        report_data = {
            'report_type': report.report_type,
            'name': report.name,
            'updated_at': tz.formatDateTime(datetime.datetime.now(), org),
            'report_id': report.id,
            'data': data
        }

        kstats.cache_saved_report(report, report_data, org, iteration_id)

        return report_data
