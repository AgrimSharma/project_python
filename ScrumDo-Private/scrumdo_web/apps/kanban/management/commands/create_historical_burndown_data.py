#!/usr/bin/env python

from apps.projects.models import Project, Story, Iteration, PointsLog
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

import logging
import datetime

from apps.kanban.models import BoardCell, CellMovement


logger = logging.getLogger(__name__)

# 1. Looks at all kanban projects.
# 2. Generates project-level burndown data from step history.
# 3. Looks at all iterations with dates.
# 4. Generates iteration burndown data from step history.
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--project', '-p', dest='project_slug',  help='Help for the long options'),
            make_option('--all', action='store_true', dest='all', default=False, help='Rebuild all projects'),
        )
    args = "project"
    def handle(self, *args, **options):
        allProjects = options["all"]
        if allProjects:
            projects = Project.objects.filter(abandoned=False, active=True, project_type__in=[Project.PROJECT_TYPE_KANBAN, Project.PROJECT_TYPE_PORTFOLIO])
        else:
            slug = options["project_slug"]
            try:
                projects = [Project.objects.get(slug=slug)]
            except Project.DoesNotExist:
                print "Could not find project."
                return

        for project in projects:
            self.rebuildProject(project)

    def getReportingProfile(self,project):
        defaultFlows = project.workflows.filter(default=True)
        if len(defaultFlows) == 0:
            defaultFlows = project.workflows.all()
        biggest = None
        biggestSize = 0
        for flow in defaultFlows:
            flowSize = flow.steps.count()
            if flowSize > biggestSize:
                biggest = flow
                biggestSize = flowSize
        return biggest  # Return the workflow with the most steps


    def getStatus(self, cell, iteration):
        if iteration is not None:
            if iteration.iteration_type == Iteration.ITERATION_ARCHIVE:
                return Story.STATUS_DONE
            if iteration.iteration_type == Iteration.ITERATION_BACKLOG:
                return Story.STATUS_TODO
        else:
            logger.info("null iteration")

        if cell is None:
            return Story.STATUS_TODO   # shouldn't happen ???

        for step in cell.steps.exclude(mapped_status=-1):
            return step.mapped_status

        if cell.time_type == BoardCell.DONE_TIME:
            return Story.STATUS_DONE
        if cell.time_type == BoardCell.WORK_TIME:
            return Story.STATUS_DOING
        return Story.STATUS_TODO

    def recordIteration(self, iterationStatuses, status, iteration, amount):
        if iteration is None:
            return
        if iteration.iteration_type != Iteration.ITERATION_WORK:
            return
        if not iteration.id in iterationStatuses:
            iterationStatuses[iteration.id] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        iterationStatuses[iteration.id][status] += amount

    def createLog(self, target, currentDay, statuses):
        try:
            if hasattr(target, "project_id"):
                target.points_log.get(date=currentDay, iteration=target)
            else:
                target.points_log.get(date=currentDay, project=target)
        except PointsLog.MultipleObjectsReturned:
            pass
        except PointsLog.DoesNotExist:
            # Only creating entries that are missing.
            logger.info("Created entry for %s %s %s %d" % (target, currentDay, statuses, int(sum(statuses)) ))
            log = PointsLog(date=currentDay)
            if hasattr(target, "project_id"):
                target.iteration = target
            else:
                target.project = target
            log.points_status1 = statuses[0]
            log.points_status2 = statuses[1]
            log.points_status3 = statuses[2]
            log.points_status4 = statuses[3]
            log.points_status5 = statuses[4]
            log.points_status6 = statuses[5]
            log.points_status7 = statuses[6]
            log.points_status8 = statuses[7]
            log.points_status9 = statuses[8]
            log.points_status10 = statuses[9]
            log.points_total = sum(statuses)
            log.save()


    def logData(self, project, currentDay, statuses, iterationStatuses):
        self.createLog(project, currentDay, statuses)
        for k, v in iterationStatuses.iteritems():
            try:
                iteration = project.iterations.get(id=k)
                if iteration.start_date is not None and currentDay < iteration.start_date:
                    continue  # Before this iteration
                if iteration.end_date is not None and currentDay > iteration.end_date:
                    continue  # After this iteration
                self.createLog(iteration, currentDay, v)  # Within the dates, or the dates weren't there (CF?)
            except Iteration.DoesNotExist:
                logger.warn("Warning: Iteration not found, skipping.")


    def rebuildProject(self, project):
        workflow = self.getReportingProfile(project)
        movements = CellMovement.objects.filter(story__project=project).order_by("created")
        if len(movements) == 0:
            logger.info(u"No movements found %s" % project.slug)
            return
        statuses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        iterationStatuses = {}
        currentDay = movements[0].created.date()
        storyStatuses = {}
        for movement in movements:
            previousStatus = None
            if movement.story_id in storyStatuses:
                previousStatus = storyStatuses[movement.story_id]

            if movement.cell_to is not None or movement.related_iteration is not None:
                status = self.getStatus(movement.cell_to, movement.related_iteration) - 1
                statuses[status] += movement.story.points_value()
                self.recordIteration(iterationStatuses, status, movement.related_iteration, movement.story.points_value())
                storyStatuses[movement.story_id] = {'status':status, 'iteration':movement.related_iteration}

            if previousStatus is not None:
                status = previousStatus['status']
                iteration = previousStatus['iteration']
                statuses[status] -= movement.story.points_value()
                self.recordIteration(iterationStatuses, status, iteration, -1 * movement.story.points_value())

            if movement.created.date() != currentDay:
                self.logData(project, currentDay, statuses, iterationStatuses)
                currentDay = movement.created.date()

        # for iteration in project.iterations.filter(iteration_type=Iteration.ITERATION_WORK):



