from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import django.core.validators as validators
from apps.attachments.models import Attachment
from apps.account.templatetags import account_tags

from model_utils import FieldTracker

from storytag import StoryTag
from storytagging import StoryTagging

import datetime

# from iteration import Iteration
# from epic import Epic
from extrauserinfo import ExtraUserInfo
from task import Task

import logging

logger = logging.getLogger(__name__)


class Story(models.Model):
    # Why are these 4 statuses duplicated from the module level?
    STATUS_TODO = 1
    STATUS_DOING = 4
    STATUS_REVIEWING = 7
    STATUS_DONE = 10
    business_value = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    rank = models.IntegerField(default=500000)
    epic_rank = models.IntegerField(default=500000)  # Rank of this card inside epic views
    release_rank = models.IntegerField(default=500000)  # Rank of this card inside release views
    summary = models.TextField()
    local_id = models.IntegerField()
    detail = models.TextField(blank=True)
    creator = models.ForeignKey(User, related_name="created_stories", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now_add=True)
    assignee = models.ManyToManyField(User,
                                      blank=True,
                                      verbose_name=_('assignees'),
                                      db_table='v2_projects_story_assignee_m2m',
                                      related_name="assigned_stories")

    dependency = models.ManyToManyField('projects.Story',
                                          blank=True,
                                          verbose_name=_('dependencies'),
                                          db_table='v2_projects_story_dependencies_m2m',
                                          related_name="dependent_stories")

    points = models.CharField('points', max_length=7, default="?", blank=True)
    iteration = models.ForeignKey("projects.Iteration", related_name="stories")
    project = models.ForeignKey("projects.Project", related_name="stories")
    status = models.IntegerField(default=1, validators=[validators.MinValueValidator(1), validators.MaxValueValidator(10)])
    card_type = models.IntegerField(default=1, validators=[validators.MinValueValidator(1), validators.MaxValueValidator(10)])
    category = models.CharField(max_length=25, blank=True, null=True)
    extra_1 = models.TextField(blank=True, null=True)
    extra_2 = models.TextField(blank=True, null=True)
    extra_3 = models.TextField(blank=True, null=True)
    epic = models.ForeignKey("projects.Epic", null=True, blank=True, related_name="stories")

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

    cell = models.ForeignKey("kanban.BoardCell", on_delete=models.SET_NULL, null=True, default=None, related_name="stories", blank=True)

    due_date = models.DateTimeField(null=True, blank=True)

    release = models.ForeignKey('projects.Story',
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL,
                                  default=None)

    blocked = models.BooleanField(default=False)
    time_criticality = models.CharField('time_criticality', max_length=7, default="?", blank=True)
    risk_reduction = models.CharField('risk_reduction', max_length=7, default="?", blank=True)

    # Other projects that are going to contribute work against this card.
    # For instance, if this story is a feature, it might point to team projects.
    #project_assignments = models.ManyToManyField('projects.project', related_name='assigned_stories')

    project_assignments = models.ManyToManyField('projects.project', related_name='assigned_stories', through='ProjectAssignments')


    tags_to_delete = []
    tags_to_add = []

    tasks_to_export = []

    tracker = FieldTracker(fields=['tags_cache', 'cell_id'])

    last_moved = models.DateTimeField(null=True, default=None, blank=True)
    accumulated_hours = models.IntegerField(default=0)

    def age_hours(self):
        a = 0
        if self.last_moved is not None:
            a = round((datetime.datetime.now() - self.last_moved).total_seconds() / 60 / 60)
        return a + self.accumulated_hours

    def clean_fields(self, exclude=None):
        super(Story, self).clean_fields(exclude)
        self.status = min(10, max(1, self.status))

    def full_epic_label(self):
        if self.epic != None:
            return self.epic.full_name()
        return ""

    def resetCounts(self, autosave=True):
        self.resetTaskCount()
        self.resetCommentCount()
        self.resetExternalLinksCount()
        self.resetAttachmentCount()
        self.resetEpicLabel()
        if self.id is None:
            self.save()  # The assignee cache needs an ID
        self.resetAssigneeCache()
        if autosave:
            self.save()


    def resetEpicLabel(self):
        if self.epic:
            self.epic_label = self.epic.short_name()[-32:]
        else:
            self.epic_label = ""

    def resetAttachmentCount(self):
        try:
            self.has_attachment = (Attachment.objects.filter(story=self).count() > 0)
        except:
            logger.debug("Could not update attachment count")
            pass # no .attachments in open source edition

    def resetExternalLinksCount(self):
        self.has_external_links = (self.external_links.count() > 0)

    def resetCommentCount(self):
        self.comment_count = self.comments.count()

    @property
    def task_count(self):
        return sum( self.taskCountsArray() )

    @property
    def completed_task_count(self):
        return self.taskCountsArray()[9]


    def taskCountsArray(self):
        return [int(v) for v in self.task_counts.split(",")]

    def resetTaskCount(self):
        counts = [0] * 10
        for task in self.tasks.all():
            counts[task.status-1] += 1
        self.task_counts = ",".join([str(c) for c in counts])

    def story_tags_array(self):
        tags = self.tags.split(",")
        return [tag.strip() for tag in tags if len(tag.strip())>0]

    def story_tags_full(self):
        "Helper function to return queryset of taggings with the tag object preloaded"
        return self.story_tags.all().select_related("tag")

    def statusText(self):
        try:
            si = self.status * 10 - 10
            ei = self.status * 10
            return self.project.status_names[si:ei].strip()
        except:
            return "Unknown"

    def cardTypeText(self):
        try:
            si = self.card_type * 10 - 10
            ei = self.card_type * 10
            return self.project.card_types[si:ei].strip()
        except:
            return "Unknown"

    def getPointsLabel(self):
        result = filter( lambda v: v[0] == self.points, self.project.getPointScale())
        if len(result) > 0:
            return result[0][1]
        return self.points

    def points_value(self):
        # the float() method understands inf!
        if self.points.lower() == "inf" :
            return 0

        try:
            return float(self.points)
        except:
            return 0

    def businessValue(self):
        if self.business_value == None :
            return 0
        try:
            return float(self.business_value)
        except:
            return 0

    def getBusinessValueLablel(self):
        if self.businessValue() == None:
            return self.businessValue()

        #if project business value mode is set to dollar value return the business_value
        bv = int(self.businessValue()) if (self.businessValue()) % 1 == 0 else self.businessValue()
        if self.project.business_value_mode == 0:
            return bv
        #find the value label from point scale
        result = filter( lambda v: v[0] == str(bv), self.project.getPointScale())
        if len(result) > 0:
            return result[0][1]
        return bv

    def resetTagsCache(self):
        r = ""
        for tag in self.story_tags.all():
            if len(r) > 0:
                r = r + ", "
            r = r + tag.name
        self.tags_cache = r

    def time_criticality_value(self):
        # the float() method understands inf!
        if self.time_criticality.lower() == "inf" :
            return 0

        try:
            return float(self.time_criticality)
        except:
            return 0

    def risk_reduction_value(self):
        # the float() method understands inf!
        if self.risk_reduction.lower() == "inf" :
            return 0

        try:
            return float(self.risk_reduction)
        except:
            return 0

    def wsjfValue(self):
        timeCriticality = self.time_criticality_value()
        riskReduction = self.risk_reduction_value()
        businessValue = self.businessValue() if self.businessValue() is not None else 0
        points = self.points_value()

        if self.points.lower() == "inf":
            return 0
        if points == 0:
            return 'Inf'
        try:
            return round((timeCriticality + riskReduction + businessValue) / points, 2)
        except:
            return 0

    def getTimeCriticalityLabel(self):
        result = filter( lambda v: v[0] == self.time_criticality, self.project.getPointScale())
        if len(result) > 0:
            return result[0][1]
        return self.time_criticality

    def getRiskReductionLabel(self):
        result = filter( lambda v: v[0] == self.risk_reduction, self.project.getPointScale())
        if len(result) > 0:
            return result[0][1]
        return self.risk_reduction

    @property
    def tags(self):
        if self.tags_cache is None:
            self.resetTagsCache()
        return self.tags_cache


    @tags.setter
    def tags(self, value):
        if self.tags_cache == value:
            return
        self.tags_cache = value
        self.update_tags = True


    @property
    def assignees(self):
        return self.assignee.all()

    @assignees.setter
    def assignees(self, value):
        # self.assignee.clear()
        if value:
            if self.id is None:
                self.save()  # Need to have an ID to set assignees

            old_assignees = list(self.assignee.all())

            for input_name in value.split(","):
                input_name = input_name.strip()
                # Then, try to look up by username
                try:
                    user_obj = User.objects.get(username=input_name)
                    if self.project.hasReadAccess(user_obj):
                        try:
                            self.assignee.add(user_obj)
                        except IntegrityError:
                            pass  # occasionally we got an error here because the person was already assigned.
                        old_assignees = [a for a in old_assignees if a.username != user_obj.username]
                        continue
                except User.DoesNotExist:
                    logger.warn("Could not find user %s" % input_name)

                # First, try to find the user's full name
                eui = ExtraUserInfo.objects.filter(full_name=input_name).select_related('user')
                for e in eui:
                    user = e.user
                    if self.project.hasReadAccess(user):
                        try:
                            self.assignee.add(user)
                        except IntegrityError:
                            pass  # occasionally we got an error here because the person was already assigned.
                        # This username is seen, so remove it from old_assignees
                        old_assignees = [a for a in old_assignees if a.username != user.username]


            # old_assignees now contains users not seen in the new list, so remove them
            for assignee in old_assignees:
                self.assignee.remove( assignee )
            self.resetAssigneeCache()
        else:
            # No assignees set, so clear 'em out
            self.assignee.clear()

    def resetAssigneeCache(self):
        r = ""
        for assignee in self.assignee.all():
            if len(r) > 0:
                r += ", "
            r += account_tags.realname(assignee)
        self.assignees_cache = r

    @property
    def storyTasks(self):
        t = ""
        tasks_list = self.tasks.all()
        for single_task in tasks_list:
            if len(t) > 0:
                t += "\n"
            t += single_task.export_value()
        return t

    @storyTasks.setter
    def storyTasks(self, value):
        input_tasks = value.split('\n')
        story_saved = False
        # Find tasks to be added
        for input_task in input_tasks:
            found = False
            task_values = input_task.split('\t')
            # status
            assignee = None
            summary = task_values[0]
            status = 1

            if len(task_values) >= 2 :
                s = self.project.reverseTaskStatus(task_values[len(task_values)-1])
                status = s if s > 0 else 1

            if len(task_values) >= 3:
                try:
                    assignee = User.objects.get(username=task_values[1])
                    if not self.project.hasReadAccess(assignee):
                        assignee = None
                except:
                    assignee = None

            for saved_task in self.tasks.all():
                if summary.strip() == saved_task.summary.strip():
                    saved_task.assignee = assignee
                    saved_task.status = status
                    saved_task.save()
                    found = True
            if not found and summary.strip() != "":
                if not story_saved:
                    self.save()
                    story_saved = True
                new_task = Task(story=self,summary=summary,status=status,assignee=assignee)
                new_task.save()  # saving the Task


        # find tasks to be deleted
        for saved_task in self.tasks.all():
            found = False
            for input_task in input_tasks:
                task_values = input_task.split('\t')
                summary = task_values[0]
                if saved_task.summary == summary:
                    found = True
            if not found:
                saved_task.delete()

    def save(self, *args, **kwargs):
        super(Story, self).save(*args, **kwargs)
        if hasattr(self, 'update_tags') and self.update_tags:
            self.saveTags()

    def saveTags(self):
        current_tags = {tag.name.lower() for tag in self.story_tags.all()}
        if self.tags_cache is None:
            self.tags_cache = ''
        target_tags = {tag.strip()[:32].lower() for tag in self.tags_cache.split(",") if len(tag.strip()) > 0}

        # A hash of lower case:user capitalized tags
        cap_tags = {tag.strip()[:32].lower():tag.strip()[:32] for tag in self.tags_cache.split(",") if len(tag.strip()) > 0}

        tags_to_remove = current_tags.difference(target_tags)
        if len(tags_to_remove) > 0:
            logger.info("Removing [%s]" % tags_to_remove)
        tags_to_add = target_tags.difference(current_tags)
        project = self.project

        for lower_tag_name in tags_to_add:
            tag_name = cap_tags[lower_tag_name]
            existing = list(project.tags.filter(name__iexact=tag_name))
            if len(existing) > 0:  # in the past, we generated duplicate storytags, oops.
                tag = existing[0]
            else:
                tag = StoryTag(name=tag_name, project=project)
                tag.save()
            StoryTagging(tag=tag, story=self).save()

        for tag_name in tags_to_remove:
            StoryTagging.objects.filter(tag__name__iexact=tag_name, story=self).delete()
        self.update_tags = False



    def __unicode__(self):
        try:
            return "[%s/%s-%d] %s" % (self.project.name, self.project.prefix, self.local_id, self.summary)
        except:
            return "[???/#%d] %s" % (self.local_id, self.summary)


    @models.permalink
    def get_absolute_url(self):
        return 'story_permalink', [str(self.id)]

    @property
    def available_status(self):
        return self.project.status_choices()

    @property
    def attachments(self):
        attachment_resource = []
        attachments = Attachment.objects.filter(story=self)
        for attachment in attachments:
            attachment_resource.append([attachment.filename, attachment.attachment_file.url])
        return attachment_resource

    @property
    def dependencies(self):
        return self.dependency.all()

    @dependencies.setter
    def dependencies(self, value):
        if value:
            if self.id is None:
                self.save()  # Need to have an ID to set assignees

            old_dependencies = list(self.dependencies.all())

            for input_id in value.split(","):
                input_id = input_name.strip()

                try:
                    story_obj = Story.objects.get(id=input_id)
                    try:
                        self.dependencies.add(story_obj)
                    except IntegrityError:
                        pass  # occasionally we got an error here because the person was already assigned.
                    old_dependencies = [a for a in old_dependencies if a.id != story_obj.id]
                    continue
                except Story.DoesNotExist:
                    logger.warn("Could not find story %s" % input_id)


            # old_assignees now contains users not seen in the new list, so remove them
            for dependencies in old_dependencies:
                self.dependencies.remove( dependencies )
        else:
            # No assignees set, so clear 'em out
            self.dependencies.clear()

    def block(self):
        self.blocked = 1
        self.save()

    def unblock(self):
        self.blocked = 0
        self.save()

    def resetAgeHours(self):
        self.accumulated_hours = 0
        self.last_moved = None
        self.save()

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_story"
        unique_together = (("local_id", "project"),)

class ProjectAssignments(models.Model):
    story = models.ForeignKey('projects.Story', related_name="assigned_to")
    project = models.ForeignKey('projects.Project')
    assigned = models.DateTimeField(_('assigned'), auto_now_add=True)

    def __unicode__(self):
        try:
            return "story %s assigned to %s on %s" % (self.story.id, self.project.id, self.assigned)
        except:
            return "assigned on %s" % self.assigned

    
    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_story_project_assignments"