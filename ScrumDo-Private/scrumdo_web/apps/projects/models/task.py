from django.db import models
from django.contrib.auth.models import User
import django.core.validators as validators
from storytag import StoryTag
from tasktagging import TaskTagging
import re

# from story import Story


class Task(models.Model):
    story = models.ForeignKey("projects.Story", related_name="tasks")
    summary = models.TextField(blank=True)
    assignee = models.ForeignKey(User, related_name="assigned_tasks", verbose_name='assignee', null=True, blank=True)
    order = models.PositiveIntegerField( default=0 )
    tags_cache = models.CharField(max_length=512, blank=True, null=True, default=None)

    estimated_minutes = models.IntegerField(default=0)

    status = models.IntegerField(default=1, validators=[validators.MinValueValidator(1), validators.MaxValueValidator(10)])

    modified = models.DateTimeField('modified', auto_now=True)

    tags_to_delete = []
    tags_to_add = []
    new_project_tags = []

    def status_text(self):
        si = self.status * 10 - 10
        ei = self.status * 10
        return self.story.project.task_status_names[si:ei].strip()

    def task_tags_array(self):
        tags = self.tags.split(",")
        return [tag.strip() for tag in tags if len(tag.strip())>0]

    def task_tags_full(self):
        "Helper function to return queryset of taggings with the tag object preloaded"
        return self.task_tags.all().select_related("tag")

    def resetTagsCache(self):
        r = ""
        for tag in self.task_tags.all():
            if len(r) > 0:
                r = r + ", "
            r = r + tag.name
        self.tags_cache = r

    # For backwards compatibility when I added the status field:
    @property
    def complete(self):
        return self.status == 10

    @complete.setter
    def complete(self, value):
        if value:
            self.status = 10
        else:
            self.status = 1


    @property
    def tags(self):
        if self.tags_cache is None:
            self.resetTagsCache()
        return self.tags_cache

    @tags.setter
    def tags(self, value):
        #print "TAGS SET " + value
        self.tags_cache = value
        input_tags = [t.strip() for t in value.split(',')]
        self.tags_to_delete = []
        self.tags_to_add = []
        self.new_project_tags = []
        # First, find all the tags we need to add.
        for input_tag in input_tags:
            found = False
            for saved_tag in self.task_tags.all():
                if saved_tag.name == input_tag:
                    found = True
            if not found and input_tag != "":
                self.tags_to_add.append( input_tag )
            # Next, find the tags we have to delete
        for saved_tag in self.task_tags.all():
            found = False
            for input_tag in input_tags:
                if saved_tag.name == input_tag:
                    found = True
            if not found :
                self.tags_to_delete.append( saved_tag )

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        self.saveTags()
        
    def saveTags(self):
        project = self.story.project
        for tag_name in self.tags_to_add:
            existing = list(project.tags.filter(name__iexact=tag_name))
            if len(existing) > 0:
                tag = existing[0]
            else:
                tag = StoryTag(name=tag_name, project=project)
                tag.save()
                self.new_project_tags.append(tag_name)
            TaskTagging(tag=tag, task=self).save()

        for tag_name in self.tags_to_delete:
            tag_name.delete()
                    
    def __unicode__(self):
        return "[%s/%s-%d] Task: %s" % (self.story.project.name, self.story.project.prefix ,self.story.local_id, self.summary)
    class Meta:
        ordering = [ 'order' ]

    @models.permalink
    def get_absolute_url(self):
        return 'story_task_permalink', [str(self.story.id), str(self.id)]

    def export_value(self):
        status = self.status_text()
        if self.summary == "":
            return ""
        if self.assignee == None:
            return self.summary + "\t" + status
        else:
            return self.summary + "\t" + self.assignee.username + "\t" + status

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_task"
