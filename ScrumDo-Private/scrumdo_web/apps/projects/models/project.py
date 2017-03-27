from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db.models.signals import post_save

from datetime import datetime
from pointslog import PointsLog
import random
import string
import json

from .pointscale import PointScale

import apps.organizations.tz as tz

from apps.organizations.models import Organization
from apps.account.templatetags import account_tags

# from projectmember import ProjectMember
from iteration import Iteration
# from story import Story


def _default_token():
    return "".join(random.sample(string.lowercase + string.digits, 7))


class Project(models.Model):
    POINT_CHOICES_FIBO = ( ('?', '?'), ('0', '0'), ('0.5','0.5'), ('1', '1'),  ('2', '2'),  ('3', '3'),  ('5', '5'), ('8', '8'), ('13', '13'), ('20', '20'), ('40', '40'), ('100', '100'), ('Inf', 'Infinite') )
    POINT_CHOICES_MINIMAL = ( ('?', '?'), ('0', '0'),  ('1', '1'),  ('2', '2'),  ('3', '3'),  ('4', '4'), ('5', '5') )
    POINT_CHOICES_MAX = ( ('?', '?'), ('0', '0'), ('0.25', '0.25'), ('0.5','0.5'), ('1', '1'),  ('2', '2'),  ('3', '3'),   ('4', '4'), ('5', '5'),  ('6', '6'),  ('7', '7'), ('8', '8'),  ('9', '9'),  ('10', '10'), ('15', '15'), ('25', '25'), ('50', '50'), ('100', '100'), ('Inf', 'Infinite') )
    POINT_CHOICES_SIZES = ( ('?', '?'), ('1', 'XS'), ('5', 'S'), ('10','M'), ('15', 'L'),  ('25', 'XL')  )
    POINT_CHOICES_FIBO_BIG = ( ('?', '?'), ('0', '0'), ('1', '1'),  ('2', '2'),  ('3', '3'),  ('5', '5'), ('8', '8'), ('13', '13'), ('21', '21'), ('34', '34'), ('55', '55'), ('89','89'), ('144','144'), ('Inf', 'Infinite') )
    POINT_CHOICES_EXPO = (('1', '1'), ('2', '2'), ('4', '4'), ('8', '8'), ('16', '16'), ('32', '32'), ('64', '64') )
    POINT_RANGES = [POINT_CHOICES_FIBO, POINT_CHOICES_MINIMAL, POINT_CHOICES_MAX, POINT_CHOICES_SIZES, POINT_CHOICES_FIBO_BIG, POINT_CHOICES_EXPO]

    VELOCITY_TYPE_AVERAGE = 0
    VELOCITY_TYPE_AVERAGE_5 = 1
    VELOCITY_TYPE_MEDIAN = 2
    VELOCITY_TYPE_AVERAGE_3 = 3

    PROJECT_TYPE_SCRUM = 0
    PROJECT_TYPE_KANBAN = 1
    PROJECT_TYPE_PORTFOLIO = 2
    PROJECT_TYPE_BACKLOG_ONLY = 3

    RENDER_MODE_RESIZE = 0
    RENDER_MODE_FIXED = 1
    
    BUSINESS_VALUE_AS_DOLLAR = 0
    BUSINESS_VALUE_AS_POINT = 1
    BUSINESS_VALUE_HIDDEN = 2
    
    TIME_TRACKING_TYPES_CHOICES = (('scrumdo', 'ScrumDo'),('harvest', 'Harvest'))

    # PROJECT_TYPE_CHOICES = ((PROJECT_TYPE_SCRUM, "Scrum"), (PROJECT_TYPE_KANBAN, "Scrumban"), (PROJECT_TYPE_PORTFOLIO, "Portfolio Planning"))
    PROJECT_TYPE_CHOICES = ((PROJECT_TYPE_SCRUM, "Scrum"), (PROJECT_TYPE_KANBAN, "Scrumban"), (PROJECT_TYPE_PORTFOLIO, "Portfolio Planning"))

    project_type = models.SmallIntegerField(default=PROJECT_TYPE_SCRUM, choices=PROJECT_TYPE_CHOICES )

    slug = models.SlugField(_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=80 )
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="projects_created")
    created = models.DateTimeField(_('created'), default=datetime.now)
    description = models.TextField(_('description'), blank=True, null=True, default="")

    # release_project = models.ForeignKey("projects.Project", blank=True, null=True, default=None, on_delete=models.SET_NULL)
    # parent = models.ForeignKey("projects.Project", default=None, null=True, related_name="children", blank=True)
    parents = models.ManyToManyField("projects.Project", default=None, related_name="children", blank=True)

    personal = models.BooleanField(default=False)

    portfolio_level = models.ForeignKey("projects.PortfolioLevel",
                                        on_delete=models.SET_NULL,
                                        related_name="projects",
                                        default=None, null=True, blank=True)

    color = models.IntegerField(default=0xf6764e)
    icon = models.CharField(default="fa-cube", max_length=48)

    active = models.BooleanField( default=True)
    # private means only members can see the project
    private = models.BooleanField(_('private'), default=True)
    current_iterations = None
    default_iteration = None

    # Card field availability / customization:
    use_extra_1 = models.BooleanField(default=False )
    use_extra_2 = models.BooleanField(default=False )
    use_extra_3 = models.BooleanField(default=False )
    extra_1_label = models.CharField(max_length=25, blank=True, null=True)
    extra_2_label = models.CharField(max_length=25, blank=True, null=True)
    extra_3_label = models.CharField(max_length=25, blank=True, null=True)
    use_time_crit = models.BooleanField(default=False)
    use_risk_reduction = models.BooleanField(default=False)
    use_points = models.BooleanField(default=True)
    use_time_estimate = models.BooleanField(default=True)
    use_due_date = models.BooleanField(default=True)
    business_value_mode = models.IntegerField(default=BUSINESS_VALUE_AS_DOLLAR)


    status_names = models.CharField(max_length=100, default="Todo                          Doing                         Reviewing                     Done      ")
    task_status_names = models.CharField( max_length=100, default = "Todo                          Doing                                                       Done      ")

    card_types = models.CharField(max_length=100, default="User Story          Feature                                           Bug                           ")

    velocity_type = models.PositiveIntegerField( default=1 )
    point_scale_type = models.PositiveIntegerField( default=0 )
    velocity = models.PositiveIntegerField(null=True, blank=True)
    velocity_iteration_span = models.PositiveIntegerField( null=True, blank=True)
    iterations_left = models.PositiveIntegerField(null=True, blank=True)
    organization = models.ForeignKey(Organization,related_name="projects", null=True, blank=True)
    category = models.CharField( max_length=25, blank=True, null=True, default="")
    categories = models.CharField(max_length=1024, blank=True, null=True)
    token = models.CharField(max_length=7, default=_default_token)
    burnup_reset = models.IntegerField(default=0)
    burnup_reset_date = models.DateField(null=True, default=None, blank=True)
    has_iterations_hidden = models.BooleanField(default=False)
    abandoned = models.BooleanField(default=False) # has this project languished for far to long with no activity?
    live_updates = models.BooleanField(default=False)

    shared = models.CharField( max_length=25, blank=True, null=True, default=None)

    story_minutes = models.IntegerField(default=0)

    render_mode = models.IntegerField(default=RENDER_MODE_RESIZE)

    default_cell = models.ForeignKey("kanban.BoardCell", blank=True, null=True, on_delete=models.SET_NULL, related_name="+")


    time_tracking_mode = models.CharField(max_length=50, choices=TIME_TRACKING_TYPES_CHOICES, default='scrumdo')

    work_item_name = models.CharField(max_length=32, default="Card")
    folder_item_name = models.CharField(max_length=32, default="Epic")
    
    aging_display = models.BooleanField( default=True )
    warning_threshold = models.PositiveIntegerField(null=True, blank=True)
    critical_threshold = models.PositiveIntegerField(null=True, blank=True)
    duedate_warning_threshold = models.PositiveIntegerField(null=True, blank=True, default=2)

    prefix = models.CharField(max_length=2, null=True, blank=True)

    vision = models.TextField('vision', blank=True)

    tab_sentiments = models.BooleanField(default=True)
    tab_board = models.BooleanField(default=True)
    tab_teamplanning = models.BooleanField(default=True)
    tab_dependencies = models.BooleanField(default=True)
    tab_chat = models.BooleanField(default=True)
    tab_planning = models.BooleanField(default=True)
    tab_risks = models.BooleanField(default=True)
    tab_milestones = models.BooleanField(default=False)
    tab_timeline = models.BooleanField(default=True)

    continuous_flow_iteration = models.ForeignKey("projects.Iteration", blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    # no of days after which Past Iterations will be auto archived
    auto_archive_iterations = models.PositiveIntegerField(null=True, blank=True, default=30)

    def storiesByIterationAndRank(self):
        return self.stories.exclude(iteration__iteration_type=Iteration.ITERATION_TRASH).order_by("iteration__end_date", "iteration__name", "rank")

    def getTaskStatusName(self, status_number):
        pos = (status_number - 1) * 10
        return self.task_status_names[pos:pos+10].strip()

    def getStatusName(self, status_number):
        pos = (status_number - 1) * 10
        return self.status_names[pos:pos+10].strip()

    def status_choices(self):
        n = 1
        for start in range(0, len(self.status_names), 10):
            name = self.status_names[start:start+10].strip()
            if len(name) > 0:
                yield (n, name)
            n += 1

    def task_status_choices(self):
        n = 1
        for start in range(0, len(self.task_status_names), 10):
            name = self.task_status_names[start:start+10].strip()
            if len(name) > 0:
                yield (n, name)
            n += 1

    def cardTypes(self):
        for start in range(0, len(self.card_types), 10):
            yield self.card_types[start:start+10].strip()

    def statuses(self):
        for start in range(0, len(self.status_names), 10):
            yield self.status_names[start:start+10].strip()

    def task_statuses(self):
        for start in range(0, len(self.task_status_names), 10):
            yield self.task_status_names[start:start+10].strip()


    def reverseTaskStatus(self, status_name):
        status_name = status_name.strip().lower()
        for status in self.task_status_choices():
            if status[1].strip().lower() == status_name:
                return status[0]
        return -1

    def reverseStatus(self, status_name):
        status_name = status_name.strip().lower()
        for status in self.status_choices():
            if status[1].strip().lower() == status_name:
                return status[0]
        return -1

    def active_story_queue_count(self):
        """ returns the number of active (not ignored) story queue items"""
        return self.story_queue.filter(archived=False).count()

    def getCategoryList( self ):
        if self.categories:
            return [c.strip() for c in self.categories.split(",")]
        else:
            return []

    def getPointScale( self ):
        if self.point_scale_type > 5:
            """ we have 5 predefined scales, project have (id+5) custom scale id """
            pid = self.point_scale_type-5
            try:
                point_scale = PointScale.objects.get(id=pid)
                return json.loads(point_scale.value)
            except:
                """ return a point scale if somehow something wrong happens """
                return self.POINT_RANGES[0]
        else:
            return self.POINT_RANGES[ self.point_scale_type ]

    def getNextEpicId( self ):
        if self.epics.count() == 0:
            return 1
        return self.epics.order_by('-local_id')[0].local_id + 1

    def getNextId( self ):
        if self.stories.count() == 0:
            return 1
        return self.stories.order_by('-local_id')[0].local_id + 1

    def all_member_choices(self):
        members = self.all_members()
        choices = []
        for member in members:
            choices.append([member.id, account_tags.realname(member)])
        choices = sorted(choices, key=lambda user: user[1].lower() )
        return choices

    def assignable_members(self):
        """
        :return: A list of members who could be assigned a card according to the Team's assignable property.
        """
        members = []

        for team in self.teams.filter(assignable=True):
            for member in team.members.all():
                if not member in members:
                    members.append(member)

        if self.organization:
            for team in self.organization.teams.filter(access_type="staff", assignable=True).prefetch_related("members"):
                for member in team.members.all():
                    if not member in members:
                        members.append(member)

        if self.personal:
            if not self.creator in members:
                members.append(self.creator)

        return sorted(members, key=lambda user: (u"%s%s" % (user.last_name, user.username)).lower())


    def all_members(self):
        members = []

        # Update: 2/4/15 - I'm ignoring the ancient per-project membership lists now.
        #                  everyone should be on team based members by now.
        # for membership in self.members.all():
        #     members.append( membership.user )

        for team in self.teams.all():
            for member in team.members.all():
                if not member in members:
                    members.append(member)

        if self.organization:
            for team in self.organization.teams.filter(access_type="staff").prefetch_related("members"):
                for member in team.members.all():
                    if not member in members:
                        members.append(member)


        return sorted(members, key=lambda member:member.username.lower())

    def get_member_by_username(self, username):
        members = self.all_members()
        for member in members:
            if member.username == username:
                return member
        return None

    def hasReadAccess( self, user ):
        return (self.personal and self.creator == user) or \
               (Organization.objects.filter(teams__members=user , teams__projects=self).count() > 0) or \
               (self.organization.teams.filter(members = user , access_type='staff').count() > 0) or \
               (self.has_project_in_cache_list(user))


    def get_default_iteration( self ):
        if self.default_iteration is None:
            iterations = Iteration.objects.filter( project=self, default_iteration=True)
            if len(iterations) == 0:
                self.default_iteration = self.iterations.all()[0]  # Shouldn't really happen, but just in case.
            else:
                self.default_iteration = iterations[0]
        return self.default_iteration

    def get_current_iterations(self, organization=None):
        # check if Project is set for Continuous Flow, if so return continue Iteration
        if self.continuous_flow_iteration is not None:
            return [self.continuous_flow_iteration]

        if self.current_iterations is None:
            if organization is None:
                today = tz.today(self.organization)
            else:
                today = tz.today(organization)

            # Get all the date-bound iterations that are current
            self.current_iterations = list(self.iterations.filter(start_date__lte=today, end_date__gte=today))
            # Plus any work iterations with no dates (mostly for continuous flow people)
            self.current_iterations += list(self.iterations.filter(iteration_type=Iteration.ITERATION_WORK,start_date=None, end_date=None))
        return self.current_iterations

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'group_slug': self.slug})

    def member_queryset(self):
        return self.member_users.all()

    def user_is_member(self, user):
        if self.members.filter(user=user).count() > 0:  # @@@ is there a better way?
            return True
        else:
            return False

    def get_num_stories(self):
        return self.stories.exclude(iteration__iteration_type = Iteration.ITERATION_TRASH).count()

    def get_num_iterations(self):
        return Iteration.objects.filter(project=self).exclude(iteration_type = Iteration.ITERATION_TRASH).count()

    def get_url_kwargs(self):
        return {'group_slug': self.slug}

    def unique_tags(self):
        all_tags = self.tags.all().order_by("name")
        tags = []
        for tag in all_tags:
            if len([t for t in tags if t.name == tag.name]) == 0:  #remove duplicates
                tags.append(tag)
        return tags

    def get_completed_count(self):
        return self.stories.filter(status=10).exclude(iteration__iteration_type = Iteration.ITERATION_TRASH).count()

    def get_in_progress_count(self):
        return self.stories.exclude(status=1).exclude(status=10).count()

    def get_iterations_all(self):
        return self.iterations.exclude(iteration_type = Iteration.ITERATION_TRASH)

    def show_more(self):
        return self.get_num_iterations() > 15

    def reasonable_default_iteration(self):
        """ Returns a reasonably default iteration """
        current = self.get_current_iterations()
        if len(current) > 0:
            return current[0]
        return self.get_default_iteration()

    def iteration_exists(self):
        today = tz.today(self.organization)
        iterations = self.iterations.filter( end_date__lt=today)
        if len(iterations) > 0:
            return True
        return False

    def get_last_iteration_stories(self):
        today = tz.today(self.organization)
        iterations = self.iterations.filter( end_date__lt=today)
        if len(iterations) > 0:
            iterations.order_by("end_date")
            return len(iterations.reverse()[0].stories.all())
        return None

    def get_last_iteration_velocity(self):
        today = tz.today(self.organization)
        iterations = self.iterations.filter( end_date__lt=today)
        if len(iterations) > 0:
            iterations.order_by("end_date")
            return iterations.reverse()[0].completed_points()
        return None

    def get_status_names(self):
        names=[]
        for status in self.status_choices():
            names = names + list(status)
        return names

    def update_has_iterations_hidden(self):
        """
        If there are ANY hidden iteration,the "More iterations..."
        link must appear in the top nav bar and in the quick links
        """
        self.has_iterations_hidden = False
        for iteration in self.iterations.all():
            if iteration.hidden:
                self.has_iterations_hidden = True
        self.save()

    def has_project_in_cache_list(self, user):
        projects_cache_key = "project_list_%s_%d_%d" % ("read", user.id, self.organization.id)
        cached_projects = cache.get(projects_cache_key)
        if not cached_projects:
            return False
        else:
            return self in cached_projects

    class Meta:
        ordering = ['-active', 'name']
        unique_together = (('organization', 'prefix'),)
        app_label = 'projects'
        db_table = "v2_projects_project"

def clear_project_cache(sender, instance=False, **kwargs):
    key = "point_scale_%d" % instance.id
    cache.delete(key)

post_save.connect(clear_project_cache, Project, dispatch_uid="apps.projects.models.Project")
