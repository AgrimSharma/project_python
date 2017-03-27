from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


import datetime
import os
import logging

logger = logging.getLogger(__name__)

def _(v):
    return v

class Project(models.Model):
    POINT_CHOICES_FIBO = ( ('?', '?'), ('0', '0'), ('0.5','0.5'), ('1', '1'),  ('2', '2'),  ('3', '3'),  ('5', '5'), ('8', '8'), ('13', '13'), ('20', '20'), ('40', '40'), ('100', '100'), ('Inf', 'Infinite') )
    POINT_CHOICES_MINIMAL = ( ('?', '?'), ('0', '0'),  ('1', '1'),  ('2', '2'),  ('3', '3'),  ('4', '4'), ('5', '5') )
    POINT_CHOICES_MAX = ( ('?', '?'), ('0', '0'), ('0.5','0.5'), ('1', '1'),  ('2', '2'),  ('3', '3'),   ('4', '4'), ('5', '5'),  ('6', '6'),  ('7', '7'), ('8', '8'),  ('9', '9'),  ('10', '10'), ('15', '15'), ('25', '25'), ('50', '50'), ('100', '100'), ('Inf', 'Infinite') )
    POINT_CHOICES_SIZES = ( ('?', '?'), ('1', 'XS'), ('5', 'S'), ('10','M'), ('15', 'L'),  ('25', 'XL')  )
    POINT_CHOICES_FIBO_BIG = ( ('?', '?'), ('0', '0'), ('1', '1'),  ('2', '2'),  ('3', '3'),  ('5', '5'), ('8', '8'), ('13', '13'), ('21', '21'), ('34', '34'), ('55', '55'), ('89','89'), ('144','144'), ('Inf', 'Infinite') )
    POINT_RANGES = [POINT_CHOICES_FIBO, POINT_CHOICES_MINIMAL, POINT_CHOICES_MAX, POINT_CHOICES_SIZES, POINT_CHOICES_FIBO_BIG]

    VELOCITY_TYPE_AVERAGE = 0
    VELOCITY_TYPE_AVERAGE_5 = 1
    VELOCITY_TYPE_MEDIAN = 2
    VELOCITY_TYPE_AVERAGE_3 = 3

    PROJECT_TYPE_SCRUM = 0
    PROJECT_TYPE_KANBAN = 1
    PROJECT_TYPE_PORTFOLIO = 2

    RENDER_MODE_RESIZE = 0
    RENDER_MODE_FIXED = 1

    # PROJECT_TYPE_CHOICES = ((PROJECT_TYPE_SCRUM, "Scrum"), (PROJECT_TYPE_KANBAN, "Scrumban"), (PROJECT_TYPE_PORTFOLIO, "Portfolio Planning"))
    PROJECT_TYPE_CHOICES = ((PROJECT_TYPE_SCRUM, "Scrum"), (PROJECT_TYPE_KANBAN, "Scrumban"))

    project_type = models.SmallIntegerField(default=PROJECT_TYPE_SCRUM, choices=PROJECT_TYPE_CHOICES )

    slug = models.SlugField(_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=80 )
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="classic_projects_created")
    created = models.DateTimeField(_('created'), default=datetime.datetime.now)
    description = models.TextField(_('description'), blank=True, null=True, default="")

    personal = models.BooleanField(default=False)

    active = models.BooleanField( default=True )

    # private means only members can see the project
    private = models.BooleanField(_('private'), default=True)
    current_iterations = None
    default_iteration = None
    use_assignee = models.BooleanField( default=True )
    use_tasks = models.BooleanField( default=True )
    use_extra_1 = models.BooleanField( default=False )
    use_extra_2 = models.BooleanField( default=False )
    use_extra_3 = models.BooleanField( default=False )
    extra_1_label = models.CharField(  max_length=25, blank=True, null=True)
    extra_2_label = models.CharField(  max_length=25, blank=True, null=True)
    extra_3_label = models.CharField(  max_length=25, blank=True, null=True)

    status_names = models.CharField( max_length=100, default=     "Todo                          Doing                         Reviewing                     Done      ")
    task_status_names = models.CharField( max_length=100, default="Todo                          Doing                                                       Done      ")

    velocity_type = models.PositiveIntegerField( default=1 )
    point_scale_type = models.PositiveIntegerField( default=0 )
    velocity = models.PositiveIntegerField(null=True, blank=True)
    velocity_iteration_span = models.PositiveIntegerField( null=True, blank=True)
    iterations_left = models.PositiveIntegerField(null=True, blank=True)
    organization = models.ForeignKey("organizations.Organization",related_name="classic_projects", null=True, blank=True)
    category = models.CharField( max_length=25, blank=True, null=True, default="")
    categories = models.CharField(max_length=1024, blank=True, null=True)
    token = models.CharField(max_length=7, default="")
    burnup_reset = models.IntegerField(default=0)
    burnup_reset_date = models.DateField(null=True, default=None, blank=True)
    has_iterations_hidden = models.BooleanField(default=False)
    abandoned = models.BooleanField(default=False) # has this project languished for far to long with no activity?
    live_updates = models.BooleanField(default=False)

    story_minutes = models.IntegerField(default=0)

    render_mode = models.IntegerField(default=RENDER_MODE_RESIZE)

    def getNextId(self):
        stories = Story.objects.filter(project=self)
        if stories.count() == 0:
            return 1
        return stories.order_by('-local_id')[0].local_id + 1

    def statuses(self):
        for start in range(0, len(self.status_names), 10):
            yield self.status_names[start:start+10].strip()

    class Meta:
        app_label = "classic"
        ordering = ['-active', 'name']
        db_table = 'projects_project'




class Iteration(models.Model):
    ITERATION_BACKLOG = 0
    ITERATION_WORK = 1
    ITERATION_ARCHIVE = 2
    name = models.CharField("name", max_length=100)
    detail = models.TextField('detail', blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    project = models.ForeignKey("classic.Project", related_name="classic_iterations")
    default_iteration = models.BooleanField( default=False )
    locked = models.BooleanField(default=False)

    iteration_type = models.SmallIntegerField(default=ITERATION_WORK)

    include_in_velocity = models.BooleanField('include_in_velocity', default=True)
    hidden = models.BooleanField(default=False)

    class Meta:
        app_label = "classic"
        db_table = 'projects_iteration'

class Story(models.Model):
    # Why are these 4 statuses duplicated from the module level?
    STATUS_TODO = 1
    STATUS_DOING = 4
    STATUS_REVIEWING = 7
    STATUS_DONE = 10
    rank = models.IntegerField()
    summary = models.TextField()
    local_id = models.IntegerField()
    detail = models.TextField(blank=True)
    creator = models.ForeignKey(User, related_name="classic_created_stories", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    assignee = models.ManyToManyField(User, blank=True, verbose_name=_('assignees'), db_table='projects_story_assignee_m2m', related_name="classic_assigned_stories")
    points = models.CharField('points', max_length=3, default="?", blank=True)
    iteration = models.ForeignKey("classic.Iteration", related_name="classic_stories")
    project = models.ForeignKey("classic.Project", related_name="classic_stories")
    status = models.IntegerField(default=1)
    category = models.CharField(max_length=25, blank=True, null=True)
    extra_1 = models.TextField(blank=True, null=True)
    extra_2 = models.TextField(blank=True, null=True)
    extra_3 = models.TextField(blank=True, null=True)
    epic = models.ForeignKey("classic.Epic", null=True, blank=True, related_name="classic_stories")

    # These next 5 fields are added in to cache some values so we can
    # reduce the number of queries when displaying long lists of stories.
    # They are updated through signals and can be reset with self.resetCounts()
    task_counts = models.CommaSeparatedIntegerField(max_length=44, default="0,0,0,0,0,0,0,0,0,0")
    comment_count = models.IntegerField(default=0)
    has_external_links = models.BooleanField(default=False)
    has_attachment = models.BooleanField(default=False)
    has_commits = models.BooleanField(default=False)
    tags_cache = models.CharField(max_length=512, blank=True, null=True, default=None)
    epic_label = models.CharField(max_length=32, blank=True, null=True, default=None)
    assignees_cache = models.CharField(max_length=512, blank=True, null=True, default=None)

    estimated_minutes = models.IntegerField(default=0)
    task_minutes = models.IntegerField(default=0)

    cell = models.ForeignKey("classic.BoardCell", on_delete=models.SET_NULL, null=True, default=None, related_name="classic_stories", blank=True)

    tags_to_delete = []
    tags_to_add = []

    tasks_to_export = []

    class Meta:
        app_label = "classic"
        db_table = 'projects_story'


class NewsItem(models.Model):
    created = models.DateTimeField(_('created'), default=datetime.datetime.now)
    user = models.ForeignKey(User,related_name="classic_newsItems", null=True, blank=True)
    project = models.ForeignKey("classic.Project", related_name="classic_newsItems", null=True, blank=True)
    text = models.TextField()
    icon = models.CharField(max_length=24)
    feed_url = models.CharField(max_length=75, null=True, blank=True)
    related_story = models.ForeignKey("classic.Story", related_name="classic_story", null=True, blank=True, db_index=True)

    class Meta:
        app_label = "classic"
        db_table = "activities_newsitem"


class ClassicAttachmentManager(models.Manager):
    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id,
                           object_id=obj.id)


def classic_attachment_attachment_upload(self, filename):
    """Stores the attachment in a "per module/appname/primary key" folder"""
    attachmentdir = "attachments"
    return '%s/%s/%s/%s' % (
                   attachmentdir,
                   '%s_%s' % (self.content_object._meta.app_label,
                   self.content_object._meta.object_name.lower()),
                   self.content_object.pk,
                   filename)


class Attachment(models.Model):

    objects = ClassicAttachmentManager()

    content_type = models.ForeignKey(ContentType, related_name="classic_attachment",)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    creator = models.ForeignKey(User, related_name="classic_created_attachments", verbose_name=_('creator'))
    attachment_file = models.FileField('attachment', upload_to=classic_attachment_attachment_upload)
    created = models.DateTimeField('created', auto_now_add=True)
    modified = models.DateTimeField('modified', auto_now=True)

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]

    class Meta:
        app_label = "classic"
        db_table = "attachments_attachment"


class BasecampCredentials( models.Model ):
    user = models.ForeignKey( User , related_name="classic_basecamp_credentials")
    project = models.ForeignKey( "classic.Project")
    oauth_token = models.CharField(max_length=512)
    failure_count = models.IntegerField(default=0)
    basecamp_account = models.IntegerField()
    basecamp_project = models.IntegerField()
    basecamp_project_name = models.CharField(max_length=256, default="")
    basecamp_todo_list = models.IntegerField(default=-1)
    download_todos = models.BooleanField(default=False, help_text="Should ScrumDo download Basecamp Todos as stories?")
    upload_stories = models.BooleanField(default=False, help_text="Should ScrumDo upload stories as Basecamp Todos?  This will upload ALL of your stories to Basecamp.")
    delete_todos = models.BooleanField(default=False, help_text="When a story is deleted, should the associated todo be deleted?")
    update_status = models.BooleanField(default=True, help_text="Should ScrumDo sync status between stories and todo items?")

    class Meta:
        app_label = "classic"
        db_table = "basecamp_next_basecampcredentials"


class BasecampEtags( models.Model ):
    project = models.ForeignKey( "classic.Project" )
    todo_list_id = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    etag = models.CharField(max_length=48)

    class Meta:
        app_label = "classic"
        db_table = "basecamp_next_basecampetags"


class StoryMentions(models.Model):
    story = models.ForeignKey("classic.Story")
    user = models.ForeignKey(User,related_name="classic_storyMention")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "classic"
        db_table = "email_notifications_storymentions"


class ExternalStoryMapping( models.Model ):
    story = models.ForeignKey("classic.Story", related_name="classic_external_links")
    external_id = models.CharField( max_length=40 )
    external_url = models.CharField( max_length=256, blank=True , null=True)
    extra_slug = models.CharField( max_length=20 )
    external_extra = models.CharField( max_length=512 , blank=True, null=True )

    class Meta:
        app_label = "classic"
        db_table = "extras_externalstorymapping"


class ExternalTaskMapping( models.Model ):
    """ When a task is related to external, third party sites, this gives a way of associating a reference to that other site."""
    task = models.ForeignKey("classic.Task", related_name="classic_external_links")
    external_id = models.CharField( max_length=40 )
    external_url = models.CharField( max_length=256, blank=True , null=True)
    extra_slug = models.CharField( max_length=20 )

    class Meta:
        app_label = "classic"
        db_table = "extras_externaltaskmapping"


class ExtraConfiguration( models.Model ):
    extra_slug = models.CharField( "extra_slug" , max_length=25)
    project_slug = models.CharField( "project_slug" , max_length=55)
    configuration_pickle = models.TextField( blank=True )

    class Meta:
        app_label = "classic"
        db_table = "extras_extraconfiguration"


class ProjectExtraMapping( models.Model ):
    project = models.ForeignKey("classic.Project", related_name="classic_extras")
    extra_slug = models.CharField( "extra_slug" , max_length=25)
    configuration = models.TextField( )

    class Meta:
        app_label = "classic"
        db_table = "extras_projectextramapping"


class StoryQueue( models.Model ):
    project = models.ForeignKey("classic.Project", related_name="classic_story_queue")
    extra_slug = models.CharField( "extra_slug" , max_length=25)

    external_id = models.CharField( max_length=40)
    external_url = models.CharField( max_length=256, blank=True , null=True)
    imported_on = models.DateTimeField( default=datetime.datetime.now)
    modified = models.DateTimeField( default=datetime.datetime.now)

    summary = models.TextField( )
    detail = models.TextField( blank=True )
    points = models.CharField('points', max_length=3, default="?" ,blank=True)
    status = models.IntegerField(default=1 )
    extra_1 = models.TextField( blank=True , null=True)
    extra_2 = models.TextField( blank=True , null=True)
    extra_3 = models.TextField( blank=True , null=True)
    external_extra = models.CharField( max_length=512 , blank=True, null=True )
    archived = models.BooleanField( default=False )

    class Meta:
        app_label = "classic"
        db_table = "extras_storyqueue"


class SyncronizationQueue( models.Model ):
    ACTION_SYNC_REMOTE = 1
    ACTION_STORY_UPDATED = 2
    ACTION_STORY_DELETED = 3
    ACTION_STORY_CREATED = 4
    ACTION_INITIAL_SYNC = 5
    ACTION_STORY_STATUS_CHANGED = 6
    ACTION_TASK_UPDATED = 7
    ACTION_TASK_DELETED = 8
    ACTION_TASK_CREATED = 9
    ACTION_TASK_STATUS_CHANGED = 10
    ACTION_STORY_IMPORTED = 11
    ACTION_NEWS_POSTED = 12

    ACTION_CHOICES = (
        (1, "SYNC_REMOTE"),
        (2, "STORY_UPDATED"),
        (3, "STORY_DELETED"),
        (4, "STORY_CREATED"),
        (5, "INITIAL_SYNC"),
        (6, "ACTION_STORY_STATUS_CHANGED"),
        (7, "ACTION_TASK_UPDATED"),
        (8, "ACTION_TASK_DELETED"),
        (9, "ACTION_TASK_CREATED"),
        (10, "ACTION_TASK_STATUS_CHANGED"),
        (11, "ACTION_STORY_IMPORTED")   )

    project = models.ForeignKey("classic.Project")
    story = models.ForeignKey("classic.Story", null=True, related_name="classic_sync_queue")
    task = models.ForeignKey("classic.Task", null=True, related_name="classic_sync_queue")
    extra_slug = models.CharField(  max_length=25)
    action = models.IntegerField(choices=ACTION_CHOICES )
    queue_date = models.DateTimeField( default=datetime.datetime.now)
    external_id = models.CharField( max_length=40 , null=True)

    class Meta:
        app_label = "classic"
        db_table = "extras_syncronizationqueue"


class Favorite(models.Model):
    TYPE_CHOICES = ( (0,"Story"),(1,"Project"),(2,"Iteration"),(3,"Epic") )
    user = models.ForeignKey(User, verbose_name=_('user'), related_name="classic_favorite")
    favorite_type = models.IntegerField( choices=TYPE_CHOICES )

    # I really didn't want to use generic fields nor have 4 types of favorites, there's
    # going to be a ton of these and I'll need to index by all of them.
    story     = models.ForeignKey("classic.Story", null=True, blank=True)
    epic      = models.ForeignKey("classic.Epic", null=True, blank=True)
    iteration = models.ForeignKey("classic.Iteration", null=True, blank=True)
    project   = models.ForeignKey("classic.Project", null=True, blank=True)

    class Meta:
        app_label = "classic"
        db_table = "favorites_favorite"



class Policy(models.Model):
    """ A policy represents a rule on a workflow step.
        For instance, it could be a WIP Limit. """
    POLICY_TYPE_STORY_WIP = 0   # The maximum number of stories allowed
    POLICY_TYPE_POINTS_WIP = 1  # The maximum number of points allowed
    POLICY_TYPE_MAX_AGE = 2     # The maximum age of a story in hours
    policy_type = models.SmallIntegerField(default=POLICY_TYPE_STORY_WIP)
    user_defined = models.BooleanField(default=False)
    name = models.CharField(max_length=128)
    related_value = models.IntegerField()  # for age records, max minutes the card can be.
                                           # otherwise # of cards or points.
    project = models.ForeignKey("classic.Project", related_name="classic_policies", null=True)

    class Meta:
        app_label = "classic"
        db_table = "kanban_policy"


class Workflow(models.Model):
    """ A workflow is a series of steps a story can go through.  Those steps may or may not be
        displayed linearly on a board.

        Workflow is the logical progression, BoardGroups are the visual representation.
        Graphs/reports/etc are made on Workflows

        In the UI, we call these report profile now.

        """
    project = models.ForeignKey("classic.Project", related_name="classic_workflows")
    name = models.CharField(max_length=128, blank=False)

    class Meta:
        app_label = "classic"
        db_table = "kanban_workflow"


class WorkflowStep(models.Model):
    order = models.IntegerField(default=0)
    workflow = models.ForeignKey("classic.Workflow", related_name="classic_steps")
    name = models.CharField(max_length=128)
    report_color = models.IntegerField(default=0x448cca, null=True)

    class Meta:
        app_label = "classic"
        db_table = "kanban_workflowstep"

def board_image_attachment_upload(instance, filename):
    return 'boardimages/%s/%s' % (instance.project.slug, filename)

class BoardImage(models.Model):
    sx = models.IntegerField()
    sy = models.IntegerField()
    ex = models.IntegerField()
    ey = models.IntegerField()
    project = models.ForeignKey("classic.Project", related_name="classic_images")
    image_file = models.ImageField(upload_to=board_image_attachment_upload, height_field="image_height", width_field="image_width")
    image_height = models.IntegerField(default=0)
    image_width = models.IntegerField(default=0)

    class Meta:
        app_label = "classic"
        db_table = "kanban_boardimage"


class BoardGraphic(models.Model):
    GRAPHIC_TYPE_LABEL = 0
    GRAPHIC_TYPE_ARROW = 1
    GRAPHIC_TYPE_RECTANGLE = 2
    GRAPHIC_TYPE_CIRCLE = 3

    graphic_type = models.IntegerField(default=GRAPHIC_TYPE_LABEL)
    label = models.CharField(max_length=128)

    project = models.ForeignKey("classic.Project", related_name="classic_graphics")

    # Position...
    sx = models.IntegerField()
    sy = models.IntegerField()
    ex = models.IntegerField()
    ey = models.IntegerField()

    foreground = models.IntegerField(default=0xaaaaaa)
    background = models.IntegerField(default=0xaaaaaa)
    policy = models.ForeignKey("classic.Policy", null=True, default=None)

    class Meta:
        app_label = "classic"
        db_table = "kanban_boardgraphic"


class BoardCell(models.Model):
    """ A single location on a board where a story can be placed. """
    CELL_TYPE_STANDARD = 0
    CELL_TYPE_SPLIT = 1

    LAYOUT_NORMAL = 0
    LAYOUT_COMPACT = 1
    LAYOUT_LIST = 2
    LAYOUT_GRID = 3
    LAYOUT_COMPACT_GRID = 4

    WAIT_TIME = 0
    SETUP_TIME = 1
    WORK_TIME = 2
    DONE_TIME = 3

    steps = models.ManyToManyField(WorkflowStep,
                                   db_table="kanban_boardcell_steps",
                                   related_name="classic_cells")

    project = models.ForeignKey("classic.Project", related_name="classic_boardCells")  # duplicating this, so we can get all cells for a project in a single query
    cellType = models.SmallIntegerField(default=CELL_TYPE_STANDARD)

    label = models.CharField(max_length=100, null=True)

    layout = models.PositiveSmallIntegerField(default=LAYOUT_NORMAL)

    headerColor = models.IntegerField(default=0xaaaaaa)
    backgroundColor = models.IntegerField(default=0xfafafa)

    wip_policy = models.ForeignKey("classic.Policy", null=True, default=None)

    wipLimit = models.IntegerField(default=-1)
    pointLimit = models.IntegerField(default=-1)

    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    width  = models.IntegerField(default=200)
    height = models.IntegerField(default=200)

    policy_text = models.TextField(blank=True, default="")

    time_type = models.PositiveSmallIntegerField(default=2)

    leadTime = models.BooleanField(default=True)

    policies = models.ManyToManyField(Policy,
                                      db_table="kanban_boardcell_policies",
                                      related_name="classic_cells")

    class Meta:
        app_label = "classic"
        db_table = "kanban_boardcell"


class CellMovement(models.Model):
    user = models.ForeignKey(User, related_name='+', default=None, null=True)
    story = models.ForeignKey("classic.story")
    cell_to = models.ForeignKey("classic.BoardCell", null=True, on_delete=models.SET_NULL, related_name='+')
    created = models.DateTimeField(auto_now_add=True)
    related_iteration = models.ForeignKey("classic.Iteration", null=True, on_delete=models.SET_NULL, related_name='+')

    class Meta:
        app_label = "classic"
        db_table = "kanban_cellmovement"


class StepMovement(models.Model):
    """ Records when a story goes from one step in a workflow to another.
        Please note,
            1. Either side of that could be null if the boardCell isn't associated with a step
            2. A single move on a board, could produce multiple StepMovement records if cells are associated with more than one step
            3. The to/from should always be within the same workflow.
    """
    user = models.ForeignKey(User, related_name='+', default=None, null=True)
    story = models.ForeignKey("classic.story")
    step_from = models.ForeignKey("classic.WorkflowStep", null=True, on_delete=models.SET_NULL, related_name='+')
    step_to = models.ForeignKey("classic.WorkflowStep",   null=True, on_delete=models.SET_NULL, related_name='+')
    workflow = models.ForeignKey("classic.Workflow")
    created = models.DateTimeField(auto_now_add=True)
    related_iteration = models.ForeignKey("classic.Iteration", null=True, on_delete=models.SET_NULL, related_name='+')

    class Meta:
        app_label = "classic"
        db_table = "kanban_stepmovement"


class BacklogHistorySnapshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    backlog = models.ForeignKey("classic.iteration")

    class Meta:
        app_label = "classic"
        db_table = "kanban_backloghistorysnapshot"


class BacklogHistoryStories(models.Model):
    snapshot = models.ForeignKey("classic.BacklogHistorySnapshot", related_name="classic_stories")
    story = models.ForeignKey("classic.story")

    class Meta:
        app_label = "classic"
        db_table = "kanban_backloghistorystories"


class PolicyAge(models.Model):
    story = models.ForeignKey("classic.story")
    policy = models.ForeignKey("classic.Policy")
    entered = models.DateTimeField(auto_now_add=True)
    exited = models.DateTimeField(default=None, null=True)

    class Meta:
        app_label = "classic"
        db_table = "kanban_policyage"


class StepStat(models.Model):
    """ A daily tally of some stats for a step. """
    created = models.DateField(auto_now_add=True)
    stories = models.IntegerField()
    points = models.IntegerField()

    class Meta:
        app_label = "classic"
        db_table = "kanban_stepstat"


class BoardHeader(models.Model):
    project = models.ForeignKey("classic.project", related_name='classic_headers')
    sx = models.IntegerField()
    sy = models.IntegerField()
    ex = models.IntegerField()
    ey = models.IntegerField()
    background = models.IntegerField(default=0x444444)
    label = models.CharField(max_length=128)
    policy = models.ForeignKey("classic.Policy", null=True, default=None)
    policy_text = models.TextField(blank=True, default="")

    class Meta:
        app_label = "classic"
        db_table = "kanban_boardheader"


class KanbanStat(models.Model):
    project = models.ForeignKey("classic.project")
    daily_lead_time = models.IntegerField() # in hours
    daily_flow_efficiency = models.IntegerField()
    system_lead_time = models.IntegerField() # in hours
    system_flow_efficiency = models.IntegerField()
    created = models.DateField(auto_now_add=True)

    class Meta:
        app_label = "classic"
        db_table = "kanban_kanbanstat"



class BoardAttributes(models.Model):
    project = models.ForeignKey("classic.Project", related_name="classic_extra_attributes")
    context = models.CharField(max_length=6)
    key = models.CharField(max_length=4)
    value = models.TextField()

    class Meta:
        app_label = "classic"
        db_table = 'projects_boardattributes'



class Commit(models.Model):
    story = models.ForeignKey("classic.Story", related_name="classic_commits")
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=24, default="")
    full_text = models.TextField()
    link = models.CharField(max_length=200)

    class Meta:
        app_label = "classic"
        db_table = 'projects_commit'


class Epic(models.Model):
    """Represents an epic in your backlog."""
    STATUS_INITIAL = 0
    STATUS_WRITTEN = 1
    STATUS_BLOCKED = 2
    STATUS_COMPLETED = 3
    STATUS_CHOICES = (
        (STATUS_INITIAL, 'Initial'),
        (STATUS_WRITTEN, 'Stories Written'),
        (STATUS_BLOCKED, 'Blocked'),
        (STATUS_COMPLETED, 'Completed'),
    )
    local_id = models.IntegerField()
    summary = models.TextField()
    parent = models.ForeignKey('self',
                               related_name="classic_children",
                               on_delete=models.SET_NULL,
                               null=True,
                               verbose_name="Parent Epic",
                               help_text="What epic does this one belong within?", )

    detail = models.TextField(blank=True)
    points = models.CharField('points',
                              max_length=4,
                              default="?",
                              blank=True,
                              help_text="Rough size of this epic (including size of sub-epics or stories).  Enter ? to specify no sizing."
    )
    project = models.ForeignKey("classic.Project", related_name="classic_epics")
    order = models.IntegerField(default=5000)
    archived = models.BooleanField(default=False,
                                   help_text="Archived epics are generally hidden and their points don't count towards the project."
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_INITIAL)


    class Meta:
        app_label = "classic"
        ordering = ['order']
        db_table = 'projects_epic'



class PointsLog(models.Model):
    date = models.DateField()
    points_status1 = models.IntegerField(default=0)
    points_status2 = models.IntegerField(default=0)
    points_status3 = models.IntegerField(default=0)
    points_status4 = models.IntegerField(default=0)
    points_status5 = models.IntegerField(default=0)
    points_status6 = models.IntegerField(default=0)
    points_status7 = models.IntegerField(default=0)
    points_status8 = models.IntegerField(default=0)
    points_status9 = models.IntegerField(default=0)
    points_status10 = models.IntegerField(default=0)

    time_estimated = models.IntegerField(default=0)  # total of time of stories estimated.
    time_estimated_completed = models.IntegerField(default=0)  # total of estimates from compelted stories

    points_total = models.IntegerField()
    content_type = models.ForeignKey(ContentType, related_name='+')
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        app_label = "classic"
        ordering = ["date"]
        db_table = 'projects_pointslog'



class StoryAttributes( models.Model ):
    story = models.ForeignKey( "classic.Story", related_name="classic_extra_attributes")
    context = models.CharField(max_length=6)
    key = models.CharField(max_length=4)
    value = models.CharField(max_length=10)

    class Meta:
        app_label = "classic"
        db_table = 'projects_storyattributes'


class StoryTag(models.Model):
    project = models.ForeignKey("classic.Project", related_name="classic_tags")
    name = models.CharField('name', max_length=32)

    class Meta:
        app_label = "classic"
        db_table = 'projects_storytag'


class StoryTagging(models.Model):
    tag = models.ForeignKey("classic.StoryTag", related_name="classic_stories")
    story = models.ForeignKey("classic.Story", related_name="classic_story_tags")

    @property
    def name(self):
        return self.tag.name

    class Meta:
        app_label = "classic"
        db_table = 'projects_storytagging'



class Task(models.Model):
    story = models.ForeignKey("classic.Story", related_name="classic_tasks")
    summary = models.TextField(blank=True)
    assignee = models.ForeignKey(User, related_name="classic_assigned_tasks", verbose_name='assignee', null=True, blank=True)
    order = models.PositiveIntegerField( default=0 )
    tags_cache = models.CharField(max_length=512, blank=True, null=True, default=None)

    estimated_minutes = models.IntegerField(default=0)

    status = models.IntegerField(default=1)

    tags_to_delete = []
    tags_to_add = []

    class Meta:
        app_label = "classic"
        db_table = 'projects_task'


class TaskTagging(models.Model):
    tag = models.ForeignKey("classic.StoryTag", related_name="classic_tasks")
    task = models.ForeignKey("classic.Task", related_name="classic_task_tags")

    class Meta:
        app_label = "classic"
        db_table = 'projects_tasktagging'


class TimeEntry(models.Model):
    user = models.ForeignKey(User, related_name="classic_time_entries", verbose_name='user')
    organization = models.ForeignKey("organizations.Organization", related_name="classic_timeEntries")
    project = models.ForeignKey("classic.Project", null=True)
    iteration = models.ForeignKey("classic.Iteration", null=True)
    story = models.ForeignKey("classic.Story", null=True)
    task = models.ForeignKey("classic.Task", null=True)
    minutes_spent = models.PositiveIntegerField()
    notes = models.TextField()
    date = models.DateField()

    class Meta:
        app_label = "classic"
        db_table = "projects_timeentry"


class GithubCredentials(models.Model):
    user = models.ForeignKey(User, related_name="classic_github_credentials")
    project = models.ForeignKey("classic.Project")
    oauth_token = models.CharField(max_length=64)
    failure_count = models.IntegerField(default=0)
    github_username = models.CharField(max_length=48)

    class Meta:
        app_label = "classic"
        db_table = "github_integration_githubcredentials"



class GithubBinding(models.Model):
    project = models.ForeignKey("classic.Project")
    github_slug = models.CharField(max_length=64, help_text="You must have GitHub admin privileges to connect to a repo.",verbose_name="GitHub Repo")
    upload_issues = models.BooleanField(default=False, help_text="Upload ScrumDo stories as GitHub issues. (Careful, this will upload all existing stories.)")
    download_issues = models.BooleanField(default=True, help_text="Download GitHub issues into the ScrumDo story queue.")
    delete_issues = models.BooleanField(default=False, help_text="Should ScrumDo close an associated GitHub issue when a story is deleted?")
    log_commit_messages = models.BooleanField(default=True, help_text="Do you want GitHub commit messages in your scrum log?")
    commit_status_updates = models.BooleanField(default=True, help_text="Allow users to update story status via commit messages.")

    class Meta:
        app_label = "classic"
        db_table = "github_integration_githubbinding"


class GithubLog(models.Model):
    project = models.ForeignKey("classic.Project")
    date = models.DateTimeField(auto_now=True)
    message = models.TextField()

    class Meta:
        app_label = "classic"
        db_table = "github_integration_githublog"


class Comment(models.Model):
    object_id = models.IntegerField()
    user = models.ForeignKey(User)
    date_submitted = models.DateTimeField()
    comment = models.TextField()

    class Meta:
        app_label = "classic"
        db_table = "threadedcomments_threadedcomment"


class TeamProject(models.Model):
    team = models.ForeignKey("organizations.Team")
    project = models.ForeignKey(Project, related_name='classic_teams')

    class Meta:
        app_label = "classic"
        db_table = "organizations_team_projects"
