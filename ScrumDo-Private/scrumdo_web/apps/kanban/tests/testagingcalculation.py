import apps.kanban.managers as kanban_managers
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from mock import patch

from apps.projects.models import Story, Iteration
from apps.kanban.models import BoardCell

import math
import datetime

class JobsTest(TestCase):
    fixtures = ["sample_organization.json"]

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''
        self.patcher = None
        self.startDate = datetime.datetime.now()
        self.addCleanup(self.clearDatePatch)

    def clearDatePatch(self):
        if self.patcher is not None:
            self.patcher.stop()

    def setHoursInFuture(self, hours):
        self.clearDatePatch()

        class fakedatetime(datetime.datetime):
            @classmethod
            def now(cls):
                return self.startDate + datetime.timedelta(hours=hours)

        self.patcher = patch('datetime.datetime', fakedatetime)
        self.patcher.start()

    def testAgeCalc(self):
        story = Story.objects.get(id=1)
        project = story.project
        cell1 = project.boardCells.filter(time_type=BoardCell.WORK_TIME)[0]
        cell2 = project.boardCells.filter(time_type=BoardCell.WORK_TIME)[1]
        doneCell = project.boardCells.filter(time_type=BoardCell.DONE_TIME)[0]
        backlog = project.iterations.get(iteration_type=Iteration.ITERATION_BACKLOG)
        user = User.objects.all()[0]
        work = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK)[0]

        self.assertEqual(story.accumulated_hours, 0)
        self.assertEqual(story.last_moved, None)

        story.iteration = work
        kanban_managers.moveStoryOntoCell(story, cell2, user)

        self.assertIsNotNone(story.last_moved)

        # Let's make sure our setHoursInFuture mock works:
        d1 = datetime.datetime.now()
        self.setHoursInFuture(1)
        d2 = datetime.datetime.now()
        hours = (d2 - d1).total_seconds()/3600
        self.assertAlmostEqual(hours, 1, 0)

        # Great, so now we can test aging calculations, we should be an hour old here
        self.assertAlmostEqual(story.age_hours(), 1, 0)

        for h in (12, 24, 48, 128, 1000):
            self.setHoursInFuture(h)
            self.assertAlmostEqual(story.age_hours(), h, 0)

        # Sat in cell2 for one day and moved to cell1, then sit around for another day and make sure we're at 48 hours
        self.setHoursInFuture(24)
        kanban_managers.moveStoryOntoCell(story, cell1, user)
        self.assertAlmostEqual(story.age_hours(), 24, 0)
        self.setHoursInFuture(48)
        self.assertAlmostEqual(story.age_hours(), 48, 0)

        # Now, a day later, move the card into the backlog
        self.setHoursInFuture(72)
        story.iteration = backlog
        kanban_managers.moveStoryOntoCell(story, None, user)
        self.assertAlmostEqual(story.age_hours(), 72, 0)

        # Now, wait another day
        self.setHoursInFuture(96)
        # And at this point, we should have 72 hours logged, because the day spent in
        # the backlog doesn't count.
        self.assertAlmostEqual(story.age_hours(), 72, 0)

        # move the card back into cell1 in a work iteration, age shouldn't change
        story.iteration = work
        kanban_managers.moveStoryOntoCell(story, cell1, user)
        self.assertAlmostEqual(story.age_hours(), 72, 0)

        # But if we wait a day in that cell, we should get 96 hours (120 hours - 24 hours in backlog)
        self.setHoursInFuture(120)
        self.assertAlmostEqual(story.age_hours(), 96, 0)

        # Now, let's move it into a done cell, age shouldn't change
        kanban_managers.moveStoryOntoCell(story, doneCell, user)
        self.assertAlmostEqual(story.age_hours(), 96, 0)

        # Done time doesn't count, so waiting here doesn't matter
        self.setHoursInFuture(144)
        self.assertAlmostEqual(story.age_hours(), 96, 0)

        # Move back into a work cell, time still doesn't change
        kanban_managers.moveStoryOntoCell(story, cell1, user)
        self.assertAlmostEqual(story.age_hours(), 96, 0)

        # Wait a day, we add 24 hours
        self.setHoursInFuture(168)
        self.assertAlmostEqual(story.age_hours(), 120, 0)

        # Wait a day, we add 24 hours
        self.setHoursInFuture(192)
        self.assertAlmostEqual(story.age_hours(), 144, 0)

        # Move cells, no change
        kanban_managers.moveStoryOntoCell(story, cell1, user)
        self.assertAlmostEqual(story.age_hours(), 144, 0)

        # Move to done, no change
        kanban_managers.moveStoryOntoCell(story, doneCell, user)
        self.assertAlmostEqual(story.age_hours(), 144, 0)

        # Wait a day, no change
        self.setHoursInFuture(216)
        self.assertAlmostEqual(story.age_hours(), 144, 0)







