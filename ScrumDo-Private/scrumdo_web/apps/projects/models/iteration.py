from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse

import apps.organizations.tz as tz

from pointslog import PointsLog
from story import Story


class Iteration(models.Model):
    ITERATION_BACKLOG = 0
    ITERATION_WORK = 1
    ITERATION_ARCHIVE = 2
    ITERATION_TRASH = 3
    name = models.CharField("name", max_length=100)
    detail = models.TextField('detail', blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    project = models.ForeignKey("projects.Project", related_name="iterations")
    default_iteration = models.BooleanField( default=False )
    # points_log = generic.GenericRelation(PointsLog)
    locked = models.BooleanField(default=False)

    iteration_type = models.SmallIntegerField(default=ITERATION_WORK)

    include_in_velocity = models.BooleanField('include_in_velocity', default=True)
    hidden = models.BooleanField(default=False)

    program_increment_schedule = models.ManyToManyField('projects.ProgramIncrementSchedule',
                                                   blank=True,
                                                   default=None,
                                                   related_name="iterations")
    vision = models.TextField('vision', blank=True)

    def isCurrent(self):
        key = "iter_current%s%s%d" % (self.start_date, self.end_date, self.id)
        cached = cache.get(key)
        if cached:
            return cached
        if self.start_date is None or self.end_date is None:
            return False
        today = tz.today(self.project.organization)
        cached = self.start_date <= today and self.end_date >= today
        cache.set(key, cached, 1800)
        return cached

    def is_continuous(self):
        return self.project.continuous_flow_iteration_id == self.id

    def total_points(self):
        return sum(map(lambda story: story.points_value(), self.stories.exclude(iteration__iteration_type=Iteration.ITERATION_TRASH)))

    def total_business_value(self):
        return sum(map(lambda story: story.businessValue(), self.stories.exclude(iteration__iteration_type=Iteration.ITERATION_TRASH)))

    def completed_points(self) :
        if self.iteration_type == Iteration.ITERATION_ARCHIVE:
            return self.total_points()
        if self.iteration_type in (Iteration.ITERATION_BACKLOG, Iteration.ITERATION_TRASH):
            return 0
        return sum(map(lambda story: story.points_value(), self.stories.filter(cell__time_type=3)))

    def in_progress_points(self) :
        if self.iteration_type != Iteration.ITERATION_WORK:
            return 0
        return sum(map(lambda story: story.points_value(), self.stories.filter(cell__time_type=2)))

    def max_points(self):
        logs = self.points_log.all()
        if len(logs) == 0:
            return None
        return reduce(lambda x,y: max(x,y.points_total), logs, 0 )

    def starting_points(self):
        for p in self.points_log.all():
            if p.date == self.start_date:
                return p.points_total
        return None

    def daysLeft(self):
        try:
            today = tz.today(self.project.organization) #date.today()
            if self.start_date <= today and self.end_date >= today:
                return (self.end_date - today).days
        except:
            pass
        return None

    def stats(self):
        points = 0
        stories = 0
        for story in self.stories.exclude(iteration__iteration_type=Iteration.ITERATION_TRASH):
            stories += 1
            points += story.points
        return stories, points

    def get_absolute_url(self):
        return reverse('iteration', kwargs={'group_slug': self.project.slug, 'iteration_id': self.id})

    class Meta:
        ordering = ["-default_iteration","end_date"]

    def __unicode__(self):
        return "%s / %s" % (self.project.name, self.name)

    def delete(self):
        super(Iteration, self).delete()

    def hide(self):
        self.hidden = True
        self.save()

    def unhide(self):
        self.hidden = False
        self.save()

    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_iteration"


class IterationSentiment(models.Model):
    
    iteration = models.ForeignKey("projects.Iteration", related_name="sentiments")
    project = models.ForeignKey("projects.Project", related_name="sentiments")
    creator = models.ForeignKey(User, related_name="iteration_sentiments")
    reason = models.TextField()
    number = models.PositiveSmallIntegerField()
    date = models.DateTimeField(auto_now_add=True) 

    def __unicode__(self):
        return "%s" % ( self.reason)
    
    class Meta:
        app_label = 'projects'
        db_table = "v2_projects_iteration_sentiment"