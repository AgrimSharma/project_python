from .common import *
from apps.projects.models import TimeEntry, Iteration, Story, Task
from apps.organizations import tz
from apps.organizations.models import Organization
from apps.projects.access import has_read_access, has_write_access
from django.utils.html import strip_tags

import datetime
import apps.html2text as html2text


class TimeEntryHandler(BaseHandler):
    fields = ("id",
              "user",
              "user_id",
              "project_id",
              "project_name",
              "project_slug",
              "iteration_name",
              "story_name",
              "task_name",
              "iteration_id",
              "story_id",
              "task_id",
              "minutes_spent",
              "notes",
              "story_tags",
              "story_labels",
              "filter_labels",
              "filter_tags",
              "story_points",
              "date")
    model = TimeEntry
    allowed_methods = ('GET', 'PUT', 'POST', "DELETE")

    @staticmethod
    def story_tags(entry):
        if entry.story is not None:
            return entry.story.story_tags_array()
        else:
            return None

    @staticmethod
    def filter_tags(entry):
        if entry.story is not None:
            return " ".join([ "%s" % (tag, ) for tag in entry.story.story_tags_array()])
        else:
            return None

    @staticmethod
    def story_labels(entry):
        if entry.story is not None:
            return [{"name": label.name, 'id': label.id, 'color': label.color} for label in entry.story.labels.all()]
        else:
            return None

    @staticmethod
    def filter_labels(entry):
        if entry.story is not None:
            return " ".join([ "%s_%d" % (label.name, label.id) for label in entry.story.labels.all()])
        else:
            return None

    @staticmethod
    def story_points(entry):
        if entry.story is not None:
            return {"label": entry.story.getPointsLabel(),
                    "value": entry.story.points_value()}
        else:
            return None

    @staticmethod
    def iteration_name(entry):
        if entry.iteration is not None:
            return entry.iteration.name
        else:
            return None

    @staticmethod
    def story_name(entry):
        if entry.story is not None:
            return "<span class='cards-number'>%s-%d</span> %s" % (entry.story.project.prefix,\
                                                                entry.story.local_id,\
                                                                html2text.html2text(strip_tags(entry.story.summary)) )
        else:
            return None

    @staticmethod
    def task_name(entry):
        if entry.task is not None:
            return entry.task.summary
        else:
            return None

    @staticmethod
    def project_name(entry):
        if entry.project is not None:
            return entry.project.name
        else:
            return None

    @staticmethod
    def project_slug(entry):
        if entry.project is not None:
            return entry.project.slug
        else:
            return None

    def updateEntry(self, entry, data, default_today):

        if "iteration_id" in data and data["iteration_id"] is not None:
            iteration = Iteration.objects.get(id=data['iteration_id'])
            if iteration.project == entry.project:
                entry.iteration = iteration

        if "story_id" in data and data["story_id"] is not None:
            story = Story.objects.get(id=data['story_id'])
            if entry.project == story.project:
                entry.story = story

        if "task_id" in data and data['task_id'] is not None:
            task = Task.objects.get(id=data['task_id'])
            if entry.story == task.story:
                entry.task = task

        if "notes" in data:
            entry.notes = data["notes"]

        if "date" in data:
            entry.date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
        else:
            if default_today:
                entry.date = tz.today(entry.organization)

        entry.minutes_spent = data["minutes_spent"]


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, entry_id,  project_slug=None):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that Organization")

        entry = TimeEntry.objects.get(id=entry_id)

        project = entry.project
        if not has_write_access(project, request.user):
            raise PermissionDenied("You don't have access to that Project")
        if project.organization != org:
            logger.debug("Organization did not match")
            raise ValidationError("Organization and project don't match")

        entry.delete()
        return "deleted"

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        entry = TimeEntry(project=project, organization=org, user=request.user)
        self.updateEntry(entry, data, True)
        entry.save()

        return entry

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, entry_id):
        data = request.data
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that Organization")

        entry = TimeEntry.objects.get(id=entry_id)

        project = entry.project
        if not has_read_access(project, request.user):
            raise PermissionDenied("You don't have access to that Project")
        if project.organization != org:
            raise ValidationError("Organization and project don't match")

        self.updateEntry(entry, data, False)
        entry.save()

        return entry

    def _read_story_time_entries(self, request, organization_slug, project_slug, story_id):
        # When viewing time entries for a story, we're going to let anyone who can
        # view the story see their own time, and any admins see all the time.
        org, project = checkOrgProject(request, organization_slug, project_slug)
        results = TimeEntry.objects.filter(project=project, story_id=story_id)
        if not has_admin_access(project, request.user):
            results = results.filter(user=request.user)
        results.select_related("project", "user", "story", "iteration")\
            .prefetch_related('story__tags','story__labels') \
            .order_by("-date", "-id")
        return results


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None, scope="all", story_id=None):

        if story_id is not None:
            return self._read_story_time_entries(request, organization_slug, project_slug, story_id)


        if project_slug is not None:
            org, project = checkOrgProject(request, organization_slug, project_slug, False)
            results = TimeEntry.objects.filter(project=project)
        else:
            org = Organization.objects.get(slug=organization_slug)
            results = TimeEntry.objects.filter(organization=org)

        if org.hasStaffAccess(request.user) and scope != 'user':
            # Staff users can either ask for ALL users or a specific user
            userId = request.GET.get("user", "")
            if userId != "":
                results = results.filter(user_id=userId)
        else:
            # Non-staff users can only ask for their personal entries
            # NOTE - this is also how we make sure non-staff users have access since they
            #        could have asked for any project.
            results = results.filter(user=request.user)

        if scope == 'user':
            results = results.select_related("project", "user", "story", "iteration").order_by("-date", "-id")
            return paginate(results, request)
        elif scope == "recent":
            today = datetime.date.today()
            mdiff = datetime.timedelta(days=-30)
            date_30days_ago = today + mdiff
            results = results.filter(date__gt=date_30days_ago)
        else:
            results = results.filter(date__gte=request.GET.get("start"), date__lte=request.GET.get("end"))
        
        if request.GET.get("iterationID", None) is not None:
            iteration_id = int(request.GET.get("iterationID", None))
            results = results.filter(iteration_id = iteration_id)
            

        results = results.select_related("project", "user", "story", "iteration")

        return results.order_by("-date")
