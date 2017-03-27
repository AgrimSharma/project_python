from .common import *
from apps.projects.models import Iteration, IterationSentiment, ProgramIncrementSchedule, ProgramIncrement, TeamIterationWIPLimit
import apps.projects.signals as signals
import apps.projects.managers as project_manager
import apps.organizations.tz as tz
from apps.kanban.models import BoardCell
import apps.kanban.managers as kanban_manager
from apps.realtime import util as realtime_util
from django.db.models import Avg
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

class CurrentIterationHandler(BaseHandler):
    allowed_methods = ('GET', )
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        today = tz.today(org)

        # Get all the date-bound iterations that are current
        current_iterations = project.iterations.filter(start_date__lte=today, end_date__gte=today)

        # ok, maybe we have a continuous iteration
        if current_iterations.count() == 0:
            current_iterations = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK,start_date=None, end_date=None)

        # ok, lets grab the last completed iteration
        if current_iterations.count() == 0:
            current_iterations = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK, end_date__lte=today).order_by('-end_date')[0:1]

        return current_iterations


class IterationHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    fields = ("id", "hidden", "url",
              "story_count", "include_in_velocity",
              "locked", "name", "default_iteration",
              "detail", "end_date", "start_date",
              "iteration_type", "project_slug", "vision", "done_count", "doing_count",
              "is_continuous",
              "wip_limits",
              "increment")
    write_fields = ("include_in_velocity", "locked", "name", "detail", "end_date", "start_date", "iteration_type", "hidden", "vision")
    model = Iteration

    @staticmethod
    def wip_limits(iteration):
        project = iteration.project
        try:
            limit = TeamIterationWIPLimit.objects.get(team=project, iteration_id=iteration.id)
            return limit
        except TeamIterationWIPLimit.DoesNotExist:
            return None

    @staticmethod
    def is_continuous(iteration):
        return iteration.project.continuous_flow_iteration_id == iteration.id

    @staticmethod
    def increment(iteration):
        if iteration.program_increment_schedule.all().count() is 0:
            return None
        else:
            return [
                {
                    "project_name": schedule.increment.iteration.project.name,
                    "project_slug": schedule.increment.iteration.project.slug,
                    "project_icon": schedule.increment.iteration.project.icon,
                    "project_color": schedule.increment.iteration.project.color,
                    "increment_id": schedule.increment.id,
                    "name": schedule.increment.iteration.name,
                    "id": schedule.increment.iteration.id,
                    "start_date": schedule.increment.iteration.start_date,
                    "end_date": schedule.increment.iteration.end_date
                }
                for schedule in iteration.program_increment_schedule.all().select_related("increment").order_by('start_date')
            ]

    @staticmethod
    def project_slug(iteration):
        return iteration.project.slug

    @staticmethod
    def story_count(iteration):
        return iteration.stories.all().count()

    @staticmethod
    def done_count(iteration):
        cell = BoardCell.DONE_TIME
        return iteration.stories.filter(cell__time_type=cell).count()

    @staticmethod
    def doing_count(iteration):
        cell = BoardCell.WORK_TIME
        return iteration.stories.filter(cell__time_type=cell).count()

    @staticmethod
    def url(iteration):
        return iteration.get_absolute_url()

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        iteration = Iteration(project=project)
        for field in IterationHandler.write_fields:
            if field in data:
                setattr(iteration, field, data[field])
        
        iteration.full_clean()
        iteration.save()
        
        self._handle_child_iteration_increment_data(request, project, iteration)
        signals.iteration_created.send(sender=request, iteration=iteration, user=request.user)

        return iteration

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, iteration_id):

        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        iteration = project.iterations.get(id=iteration_id)
        for field in IterationHandler.write_fields:
            if field in data:
                setattr(iteration, field, data[field])
        
        self._handle_child_iteration_increment_data(request, project, iteration)

        iteration.full_clean()
        iteration.save()

        return iteration

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id=None ):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        if iteration_id != None:
            return project.iterations.get(id=iteration_id)
        else:
            return project.iterations.select_related("project").all()

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, iteration_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        iteration = project.iterations.get(id=iteration_id)
        if iteration.iteration_type != Iteration.ITERATION_WORK:
            return False

        project_manager.delete_iteration(project, iteration, request)

        return "deleted"

    def _handle_child_iteration_increment_data(self, request, project, iteration):
        """
        will set the iteration increment to parent increment
        will select the schedule based on start data, if one exist already
        select that otherwise create new one with start date
        also create increment record if doesn't exist related to parent Iteration
        """
        data = request.data
        try:
            if data["increment"] is not None and data["start_date"]:
                existing_ids = {s.id for s in iteration.program_increment_schedule.all()}
                requested_ids = set()
                for iterationIncrement in data["increment"]:
                    increment, created = ProgramIncrement.objects.get_or_create(iteration_id=iterationIncrement["id"])
                    try:
                        schedule = ProgramIncrementSchedule.objects.get(increment=increment, start_date = data["start_date"])
                    except MultipleObjectsReturned:
                        schedule = ProgramIncrementSchedule.objects.filter(increment=increment, start_date = data["start_date"]).first()
                    except ObjectDoesNotExist:
                        schedule = ProgramIncrementSchedule(increment=increment,
                                                            start_date=data["start_date"],
                                                            default_name=data["name"])
                        schedule.save()

                    iteration.program_increment_schedule.add(schedule)
                    requested_ids.add(schedule.id)

                to_remove = existing_ids - requested_ids

                for schedule_id in to_remove:
                    schedule = ProgramIncrementSchedule.objects.get(id=schedule_id)
                    iteration.program_increment_schedule.remove(schedule)
            else:
                iteration.program_increment_schedule.clear()
        except KeyError:
            pass
            

class IterationSentimentsHandler(BaseHandler):
    allowed_methods = ('GET', 'POST',)

    fields = (  "id", 
                "reason", 
                "number",
                "date",
                ("iteration", ("name", "id")),
                ("creator", ("username", "first_name", "last_name"))
                )

    
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id, team_slug=None, sentiment_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        iteration = project.iterations.get(id=iteration_id)

        # return a single entry
        if sentiment_id is not None:
            return iteration.sentiments.get(id=sentiment_id)

        # return team specific sentiments
        if team_slug is not None:
            team_project = org.projects.get(slug=team_slug)
            return team_project.sentiments.filter(iteration = iteration)
        
        # return parent project sentiments
        return project.sentiments.filter(iteration = iteration)

        
    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, iteration_id, team_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        iteration = project.iterations.get(id=iteration_id)
        team_project = org.projects.get(slug=team_slug)
        data = request.data
        old_id = 0;
        try:
            sentiment = IterationSentiment.objects.get(iteration = iteration, project = team_project, creator = request.user)
            old_id = sentiment.id
            sentiment.delete()
        except MultipleObjectsReturned:
            sentiments = IterationSentiment.objects.filter(iteration = iteration, project = team_project, creator = request.user)
            for sentiment in sentiments:
                sentiment.delete()
        except ObjectDoesNotExist:
            pass

        sentiment = IterationSentiment(iteration = iteration, project = team_project, creator = request.user)
        sentiment.number = data["number"]
        sentiment.reason = data["reason"]

        sentiment.save()

        realtime_util.send_sentiment_added(project, team_project, sentiment, old_id)

        return {"sentiment": sentiment, "old_id": old_id};


class SentimentReportHandler(BaseHandler):
    allowed_methods = ('GET', )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)

        data = []
        for iteration in project.iterations.filter(iteration_type=Iteration.ITERATION_WORK, hidden=False):
            sentiments = iteration.sentiments.all().aggregate(total=Avg('number'))
            if sentiments['total'] is None:
                sentiments['total'] = 0
            data.append({'iteration': iteration.name, "total": sentiments['total']})

        return data
