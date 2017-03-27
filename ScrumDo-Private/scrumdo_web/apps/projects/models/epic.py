from django.db import models


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
    parent = models.ForeignKey('self', related_name="children", on_delete=models.SET_NULL, null=True, verbose_name="Parent Epic", help_text="What epic does this one belong within?", )
    detail = models.TextField(blank=True)
    points = models.CharField('points',
                              max_length=4,
                              default="?",
                              blank=True,
                              help_text="Rough size of this epic (including size of sub-epics or stories).  Enter ? to specify no sizing.")
    project = models.ForeignKey("projects.Project", related_name="epics")
    order = models.IntegerField(default=5000)
    archived = models.BooleanField(default=False,
                                   help_text="Archived epics are generally hidden and their points don't count towards the project.")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_INITIAL)

    cards_total = models.IntegerField(default=0)
    cards_completed = models.IntegerField(default=0)
    cards_in_progress = models.IntegerField(default=0)

    points_total = models.IntegerField(default=0)
    points_completed = models.IntegerField(default=0)
    points_in_progress = models.IntegerField(default=0)

    release = models.ForeignKey('projects.Story',
                                related_name='+',
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                default=None)



    def save(self, *args, **kwargs):
        p = self.parent
        while p:
            if p == self:
                # Prevent epic loops.
                self.parent = None
                break
            p = p.parent

        super(Epic, self).save(*args, **kwargs)

    def stories_by_rank(self):
        return self.stories.all().order_by("rank")

    def child_ids(self, rv=None):
        """Returns a list of the child ID's and sub-child ID's for this epic"""
        if rv is None:
            rv = []
        for child in self.children.all():
            rv.append(child.id)
            child.child_ids(rv)
        return rv


    def short_name(self):
        if self.parent:
            return "%s #E%d" % (self.parent.short_name(), self.local_id)
        return "#E%d" % self.local_id

    def full_name(self):
        if self.parent_id:
            return "%s / #E%d %s" % (self.parent.short_name(), self.local_id, self.summary)
        return "#E%d %s" % (self.local_id,self.summary)

    def normalized_points_value(self):
        """Returns the point value of this epic, minus the point value of the stories within it, minimum of 0"""
        pv = self.points_value()
        for story in self.stories.all():
            pv -= story.points_value()
        for epic in self.children.all():
            pv -= epic.normalized_points_value()
        return max(pv, 0)

    def points_value(self):
        if self.points.lower() == "inf":
            return 0
        try:
            return float(self.points)
        except:
            return 0

    def getPointsLabel(self):
        result = filter(lambda v: v[0] == self.points, self.project.getPointScale())
        if len(result) > 0:
            return result[0][1]
        return self.points

    def __unicode__(self):
        if self.local_id is None:
            local_id = -1
        else:
            local_id = self.local_id
        return u"Epic %d %s" % (local_id, self.summary)

    @models.permalink
    def get_absolute_url(self):
        return 'epics', [self.project.slug]

    class Meta:
        ordering = ['order']
        app_label = 'projects'
        db_table = "v2_projects_epic"