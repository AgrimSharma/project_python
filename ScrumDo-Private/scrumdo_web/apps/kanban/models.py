from django.db import models
from django.contrib.auth.models import User
from apps.projects.models import Iteration

from model_utils import Choices

import logging

logger = logging.getLogger(__name__)


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
    min_related_value = models.IntegerField(default=0)
                                                                                      
    project = models.ForeignKey("projects.Project", related_name="policies", null=True)
    class Meta:
        db_table = "v2_kanban_policy"


class Workflow(models.Model):
    """ A workflow is a series of steps a story can go through.  Those steps may or may not be 
        displayed linearly on a board. 

        Workflow is the logical progression, BoardGroups are the visual representation.
        Graphs/reports/etc are made on Workflows

        In the UI, we call these report profile now.

        """
    WORK_FLOW_TYPES = Choices((0, 'user', 'User Defined'), (1, 'generated', 'System Generated'))
    project = models.ForeignKey("projects.Project", related_name="workflows")
    name = models.CharField(max_length=128, blank=False)
    default = models.BooleanField(default=False)
    flow_type = models.SmallIntegerField(choices=WORK_FLOW_TYPES, default=WORK_FLOW_TYPES.user)
    class Meta:
        db_table = "v2_kanban_workflow"



class WorkflowStep(models.Model):
    """ A single step in a workflow """
    # In the UI, we call these report profile steps now.
    order = models.IntegerField(default=0)
    workflow = models.ForeignKey(Workflow, related_name="steps")
    name = models.CharField(max_length=128)    
    # policies = models.ManyToManyField(Policy, related_name="steps")    
    report_color = models.IntegerField(default=0x448cca, null=True)

    mapped_status = models.SmallIntegerField(default=-1)
    # mapped status is for scrum projects that were converted to scrumban.
    # we remember the status of the cells that were created.  This way, we
    # can still generate the stacked charts for these projects.
    # Over time, we should push users towards the real CFD, once we do that
    # we can retire this.
    class Meta:
        db_table = "v2_kanban_workflowstep"
        ordering = ["order"]



def board_image_attachment_upload(instance, filename):
    return 'boardimages/%s/%s' % (instance.project.slug, filename)

class BoardImage(models.Model):
    sx = models.IntegerField()
    sy = models.IntegerField()
    ex = models.IntegerField()
    ey = models.IntegerField()
    project = models.ForeignKey("projects.Project", related_name="images")
    image_file = models.ImageField(upload_to=board_image_attachment_upload, height_field="image_height", width_field="image_width")
    image_height = models.IntegerField(default=0)
    image_width = models.IntegerField(default=0)

    class Meta:
        db_table = "v2_kanban_boardimage"



class BoardGraphic(models.Model):
    GRAPHIC_TYPE_LABEL = 0
    GRAPHIC_TYPE_ARROW = 1
    GRAPHIC_TYPE_RECTANGLE = 2
    GRAPHIC_TYPE_CIRCLE = 3

    graphic_type = models.IntegerField(default=GRAPHIC_TYPE_LABEL)
    label = models.CharField(max_length=128)

    project = models.ForeignKey("projects.Project", related_name="graphics")

    # Position...
    sx = models.IntegerField()
    sy = models.IntegerField()
    ex = models.IntegerField()
    ey = models.IntegerField()

    foreground = models.IntegerField(default=0xaaaaaa)
    background = models.IntegerField(default=0xaaaaaa)
    policy = models.ForeignKey(Policy, null=True, default=None)

    class Meta:
        db_table = "v2_kanban_boardgraphic"


class BoardCell(models.Model):
    """ A single location on a board where a story can be placed. """
    CELL_TYPE_STANDARD = 0
    CELL_TYPE_SPLIT = 1

    LAYOUT_NORMAL = 0
    LAYOUT_COMPACT = 1
    LAYOUT_LIST = 2
    LAYOUT_GRID = 3
    LAYOUT_COMPACT_GRID = 4
    LAYOUT_POKER = 5
    LAYOUT_FULL_WIDTH = 6
    LAYOUT_SEARCH = 7
    LAYOUT_TASKS = 8
    LAYOUT_TEAM = 9

    WAIT_TIME = 0
    SETUP_TIME = 1
    WORK_TIME = 2
    DONE_TIME = 3    
    
    
    # group = models.ForeignKey(BoardGroup, related_name="cells")
    # Note: There is a ForeignKey on projects.Story to BoardCell with a related_name of stories
    steps = models.ManyToManyField(WorkflowStep,
                                   db_table="v2_kanban_boardcell_steps",
                                   related_name="cells")
    project = models.ForeignKey("projects.Project", related_name="boardCells")  # duplicating this, so we can get all cells for a project in a single query
    cellType = models.SmallIntegerField(default=CELL_TYPE_STANDARD)
    # order = models.SmallIntegerField(default=0)
    label = models.CharField(max_length=100, null=True)

    full_label = models.CharField(max_length=100, null=True)

    layout = models.PositiveSmallIntegerField(default=LAYOUT_NORMAL)
    
    headerColor = models.IntegerField(default=0xaaaaaa)
    backgroundColor = models.IntegerField(default=0xfafafa)

    wip_policy = models.ForeignKey(Policy, null=True, default=None)

    wipLimit = models.IntegerField(default=-1)
    pointLimit = models.IntegerField(default=-1)
    
    minWipLimit = models.IntegerField(default=0)
    minPointLimit = models.IntegerField(default=0)

    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    width = models.IntegerField(default=200)
    height = models.IntegerField(default=200)

    policy_text = models.TextField(blank=True, default="")

    time_type = models.PositiveSmallIntegerField(default=WORK_TIME)

    leadTime = models.BooleanField(default=True)

    policies = models.ManyToManyField(Policy,
                                      related_name="cells",
                                      db_table="v2_kanban_boardcell_policies")


    def __unicode__(self):
        if self.id:
            return "%d %s " % (self.id, self.label)
        else:
            return "? %s " % self.label

    class Meta:
        db_table = "v2_kanban_boardcell"


class CellMovementLog(models.Model):
    """We're going to save cell movements in S3 as flat files so that
       we can do faster reporting without hitting the database.  These records remember
       the last place that we saved to S3 for a given project."""
    project = models.ForeignKey("projects.Project")
    workflow = models.ForeignKey(Workflow)
    last_cell_movement = models.IntegerField(null=True, default=0)

    class Meta:
        db_table = "v2_cell_movement_log"
        unique_together = (("project", "workflow"),)


class TagMovementLog(models.Model):
    """We're going to save cell movements in S3 as flat files so that
       we can do faster reporting without hitting the database.  These records remember
       the last place that we saved to S3 for a given project."""
    project = models.OneToOneField("projects.Project")
    last_tag_movement = models.IntegerField(null=True, default=0)

    class Meta:
        db_table = "v2_tag_movement_log"


class TagMovement(models.Model):
    story = models.ForeignKey("projects.story")
    tags_cache = models.CharField(max_length=512)
    created = models.DateTimeField(auto_now_add=True)


    # These next five fields cache some values as of the tag movement record's creation
    # These are used in the filtering of reports.
    related_iteration = models.ForeignKey(Iteration, null=True, on_delete=models.SET_NULL, related_name='+')
    epic_id = models.IntegerField(default=0)
    label_ids = models.CharField(max_length=72, default='')
    assignee_ids = models.CharField(max_length=72, default='')
    points_value = models.DecimalField(max_digits=8, decimal_places=1, default="0.0")
    class Meta:
        db_table = "v2_kanban_tagmovement"


class CellMovement(models.Model):
    user = models.ForeignKey(User, related_name='+', default=None, null=True)
    story = models.ForeignKey("projects.story")
    cell_to = models.ForeignKey(BoardCell, null=True, on_delete=models.SET_NULL, related_name='+')    
    created = models.DateTimeField(auto_now_add=True)    
    related_iteration = models.ForeignKey(Iteration, null=True, on_delete=models.SET_NULL, related_name='+')

    # These next four fields cache some values as of the cell movement record's creation
    # These are used in the filtering of reports.
    epic_id = models.IntegerField(default=0)
    label_ids = models.CharField(max_length=72, default='')
    tags = models.CharField(max_length=256, default='')
    assignee_ids = models.CharField(max_length=72, default='')
    points_value = models.DecimalField(max_digits=8, decimal_places=1)

    class Meta:
        db_table = "v2_kanban_cellmovement"


class StepMovement(models.Model):
    """ Records when a story goes from one step in a workflow to another.  
        Please note, 
            1. Either side of that could be null if the boardCell isn't associated with a step
            2. A single move on a board, could produce multiple StepMovement records if cells are associated with more than one step
            3. The to/from should always be within the same workflow.
    """
    user = models.ForeignKey(User, related_name='+', default=None, null=True)
    story = models.ForeignKey("projects.story")
    step_from = models.ForeignKey(WorkflowStep, null=True, on_delete=models.SET_NULL, related_name='+')
    step_to = models.ForeignKey(WorkflowStep,   null=True, on_delete=models.SET_NULL, related_name='+')
    workflow = models.ForeignKey(Workflow)
    created = models.DateTimeField(auto_now_add=True)
    related_iteration = models.ForeignKey(Iteration, null=True, on_delete=models.SET_NULL, related_name='+')


    class Meta:
        db_table = "v2_kanban_stepmovement"


class BacklogHistorySnapshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    backlog = models.ForeignKey("projects.iteration")

    class Meta:
        db_table = "v2_kanban_backloghistorysnapshot"



class BacklogHistoryStories(models.Model):
    snapshot = models.ForeignKey(BacklogHistorySnapshot, related_name="stories")
    story = models.ForeignKey("projects.story")

    class Meta:
        db_table = "v2_kanban_backloghistorystories"



class PolicyAge(models.Model):
    # to be able to calculate the age of stories in a policy efficiently, we need to keep
    # this table around.  You get one record with an entered date when a story enters a policy.
    # When it exits that policy, you get an exited value filled in.  If a story re-enters,
    # a new record is created.  You can find the age of a story in a policy by getting
    # the record with that story/policy and a null exited.
    # Records with an exited filled in are for historical & charting purposes
    # TODO: We might need things like this for workflows/steps as well someday.
    story = models.ForeignKey("projects.story")
    policy = models.ForeignKey(Policy)
    entered = models.DateTimeField(auto_now_add=True)
    exited = models.DateTimeField(default=None, null=True)

    class Meta:
        db_table = "v2_kanban_policyage"



class StepStat(models.Model):
    """ A daily tally of some stats for a step. """
    created = models.DateField(auto_now_add=True)
    stories = models.IntegerField()
    points = models.IntegerField()

    class Meta:
        db_table = "v2_kanban_stepstat"


class PolicyNotification(models.Model):
    """ A notification to be sent out whenver a policy is violated. """


class RebuildMovementJob(models.Model):
    initiator = models.ForeignKey(User, related_name='+', default=None, null=True)
    project = models.ForeignKey("projects.project",related_name='+')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "v2_kanban_rebuildmovementjob"


class KanbanizeJob(models.Model):
    initiator = models.ForeignKey(User, related_name='+', default=None, null=True)
    source = models.ForeignKey("projects.project",related_name='+')
    destination = models.ForeignKey("projects.project", null=True,related_name='+')
    complete = models.BooleanField(default=False)
    config = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "v2_kanban_kanbanizejob"



class BoardHeader(models.Model):
    project = models.ForeignKey("projects.project", related_name='headers')
    sx = models.IntegerField()
    sy = models.IntegerField()
    ex = models.IntegerField()    
    ey = models.IntegerField()
    background = models.IntegerField(default=0x444444)
    label = models.CharField(max_length=128)
    policy = models.ForeignKey(Policy, null=True, default=None)    
    policy_text = models.TextField(blank=True, default="")

    class Meta:
        db_table = "v2_kanban_boardheader"


class KanbanStat(models.Model):
    project = models.ForeignKey("projects.project")    
    daily_lead_time = models.IntegerField()  # in minutes
    daily_flow_efficiency = models.IntegerField()
    system_lead_time = models.IntegerField()  # in minutes
    system_flow_efficiency = models.IntegerField()
    cards_claimed = models.IntegerField(default=0)
    points_claimed = models.IntegerField(default=0)
    created = models.DateField(auto_now_add=True)

    # 85th percentile lead time, over the past 90 days,
    lead_time_85 = models.IntegerField(default=0)
    # 65th percentile lead time, over the past 90 days,
    lead_time_65 = models.IntegerField(default=0)

    def _formatTime(self, time):
        if time == -1:
            return "n/a"
        if time > 60*24:
            days = round(time/60/24)
            return "%d Days" % days
        hours = round(time/60)
        return "%d Hours" % hours
    def _formatEff(self, val):
        if val == -1:
            return "n/a"
        return "%d%%" % val
    def daily_lead_time_string(self):
        return self._formatTime(self.daily_lead_time)
    def system_lead_time_string(self):
        return self._formatTime(self.system_lead_time)
    def daily_flow_efficiency_string(self):
        return self._formatEff(self.daily_flow_efficiency)
    def system_flow_efficiency_string(self):
        return self._formatEff(self.system_flow_efficiency)

    class Meta:
        db_table = "v2_kanban_kanbanstat"


class SavedReport(models.Model):
    DATE_FORMAT_TYPES = Choices((0, 'fixed', 'Fixed Dates'),
                                (2, 'relative', 'Relative Dates'))

    name = models.CharField(max_length=60)
    project = models.ForeignKey("projects.Project")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    workflow = models.ForeignKey(Workflow)

    date_format = models.SmallIntegerField(choices=DATE_FORMAT_TYPES, default=DATE_FORMAT_TYPES.fixed)

    # Have to add these when we start caching aging report:
    # agingData=step
    # agingSteps=142937,142938,142939,142940,142942,142944,142945
    # agingTags=\
    # agingType=1
    startdate = models.DateField(null=True, default=None)
    enddate = models.DateField(null=True, default=None)

    # General report options
    report_type = models.CharField(max_length=10)  # cfd or lead for now, will expand later.
    burn_type = models.IntegerField(default=0)  # 0-3 for burn types
    y_axis = models.SmallIntegerField(default=1)
    lead_start_step = models.ForeignKey(WorkflowStep, null=True, related_name="+")
    lead_end_step = models.ForeignKey(WorkflowStep, null=True, related_name="+")
    cfd_show_backlog = models.BooleanField(default=False)
    interval = models.SmallIntegerField(default=-1)

    iteration = models.ForeignKey("projects.Iteration", default=None, null=True, on_delete=models.SET_NULL, related_name="+")

    # Filter options:
    assignee = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL, related_name="+")
    #add patch to add multiple assignees to report
    #TODO: remove single assignee after all data assignees already merged
    assignees = models.ManyToManyField(User, blank=True, related_name="assignees") 
    epic = models.ForeignKey("projects.Epic", null=True, default=None, on_delete=models.SET_NULL, related_name="+")
    label = models.ForeignKey("projects.Label", null=True, default=None, on_delete=models.SET_NULL, related_name="+")
    tag = models.CharField(max_length=255, null=True, default=None)

    aging_type = models.SmallIntegerField(default=0, choices=((0,'Step'),(1,'Tag')))
    aging_by = models.SmallIntegerField(default=0)
    aging_steps = models.CommaSeparatedIntegerField(max_length=255, null=True, default=None)
    aging_tags = models.CharField(max_length=255, default=None, null=True)

    # these next few entries will be used to help determine which saved reports to automatically run

    # The last time we automatically generated this report.
    last_generated = models.DateTimeField(null=True)

    # The last time this saved report was manually viewed via the reports interface
    last_manual_view = models.DateField(null=True)

    # The last time this saved report was viewed via an automatic means
    last_auto_view = models.DateField(null=True)

    # How many times has this saved report been viewed
    views = models.IntegerField(default=0)

    created = models.DateField(auto_now_add=True)

    # Was this saved report auto-generated by the system?
    generated = models.BooleanField(default=False)

    def cache_key(self, date, iteration_id=None):
        """Returns the redis cache key for this saved report/date.  You should
           pass in the organization's date and not the server date."""
        if iteration_id is None:
            return "report_%d_%s" % (self.id, date.strftime('%Y%m%d'))
        else:
            return "report_%d_%s_%s" % (self.id, date.strftime('%Y%m%d'), str(iteration_id) )




# def cached_report_filename(instance, filename):
#     """Stores the file in a "per module/appname/primary key" folder"""
#     attachmentdir = "attachments_v2"
#     return 'cached_report/'
#
#
# class CFDCache(models.Model):
#     project = models.ForeignKey("projects.project")
#     last_updated = models.DateTimeField(auto_now=True)
#     processing = models.BooleanField(default=True)
#     filters = models.CharField(default="", max_length=256)
#     workflow = models.ForeignKey(Workflow)
#     iteration = models.ForeignKey("projects.Iteration", null=True)
#
#     class Meta:
#         db_table = "v2_kanban_cfd_cache"
#
#
# class CFDCachedValue(models.Model):
#     datetime = models.DateTimeField()
#     point_value = models.IntegerField()
#     card_count = models.IntegerField()
#     # The value has to be either a step, the backlog, or the archive ...
#     step = models.ForeignKey(WorkflowStep, null=True)
#     archive = models.BooleanField(default=False)
#     backlog = models.BooleanField(default=False)
#     cache = models.ForeignKey(CFDCache, related_name="values")
#
#     class Meta:
#         db_table = "v2_kanban_cfd_cached_value"
#
# class CFDCachedStory(models.Model):
#     story = models.ForeignKey("projects.Story", related_name='stories')
#     value = models.ForeignKey(CFDCachedValue)
#
#     class Meta:
#         db_table = "v2_kanban_cfd_cached_story"