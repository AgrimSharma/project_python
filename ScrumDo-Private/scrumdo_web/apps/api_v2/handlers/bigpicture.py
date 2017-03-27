from common import *
from django.db.models import Max, Q
import datetime
from django.core.cache import cache

import apps.kanban.managers as kanban_manager
import apps.projects.managers as project_manager
import apps.projects.systemrisks as systemrisks
from apps.kanban.models import BoardCell
from apps.projects.models import Iteration, Story, ProgramIncrement, Project, Risk, Portfolio

class BigPictureStatsHandler(BaseHandler):

    allowed_methods = ('GET', )
    CACHE_SECONDS = 3600 # one hour

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id=None, increment_id=None, action='stats', story_id=None):
        """
        iteration_id : used for Portfolio root project's Iteration data
        increment_id : used for Parent Increment related data
        story_id : filter down to data related to parent Release
        """
        org, project = checkOrgProject(request, organization_slug, project_slug)
        cells = [BoardCell.WAIT_TIME, BoardCell.SETUP_TIME, BoardCell.WORK_TIME, BoardCell.DONE_TIME]
        release_id = request.GET.get("releaseId", None)
        if release_id is not None:
            rootRelease = Story.objects.get(id=release_id)
        else:
            rootRelease = None

        if action == "projectstats":
            data = {"cell_data": []}
            for cell in cells:
                stats = self._get_cell_stats(request, project, cell, iteration_id, increment_id, rootRelease)
                data["cell_data"].append(stats)
            
            return data

        if action == "stats":
            data = {"cell_data": []}    
            
            for cell in cells:
                stats = self._get_cell_stats(request, project, cell, iteration_id, increment_id, rootRelease)
                data["cell_data"].append(stats)
            
            return data

        if action == "levelstats":
            portfolio_level = int(request.GET.get("level_number", 0))
            
            data = {"cell_data": []}
            for cell in cells:
                stats = self._get_level_stats(cell, project, portfolio_level, increment_id, rootRelease)
                data["cell_data"].append(stats)
            
            return data
        
        if action == "cards":
            cell = request.GET.get("cellType", 0)
            return self._get_cell_cards(request, project, cell, iteration_id, increment_id, rootRelease)

        if action == "dependency":
            parent_dependent = self._get_cards_parent_dependency(project, increment_id, rootRelease) 
            sibling_dependent = self._get_cards_sibling_dependency(project, increment_id, rootRelease)

            return {"parent": parent_dependent, "sibling": sibling_dependent}

        if action == "systemrisks":
            root_increment = ProgramIncrement.objects.get(id=increment_id)
            project_increments = project_manager.get_child_increments(project.slug, 1, [root_increment])
            project_iteration = project.iterations.filter(program_increment_schedule__increment__in = project_increments)
            
            risks = []

            for iteration in project_iteration:
                r = systemrisks.systemRisks(project, iteration)
                risks = risks + r

            return risks

        if action == "risks":
            root_increment = ProgramIncrement.objects.get(id=increment_id)
            portfolio = Portfolio.objects.get(root=root_increment.iteration.project)

            project_increments = project_manager.get_child_increments(project.slug, 1, [root_increment])
            project_iteration = project.iterations.filter(program_increment_schedule__increment__in = project_increments)
            
            criteria = Q(iterations__in=project_iteration) | Q(cards__iteration__in=project_iteration)

            risks = Risk.objects.filter(portfolio=portfolio).filter(criteria).distinct().order_by("-probability")

            return risks

    def _get_cards_parent_dependency(self, project, increment_id, release = None):
        root_increment = ProgramIncrement.objects.get(id=increment_id)
        project_increments = project_manager.get_child_increments(project.slug, 1, [root_increment])
        parent_projects = project.parents.all()
        data = {}
        for p_project in parent_projects:
            if release is None:
                total_cards = project.stories.filter(iteration__program_increment_schedule__increment__in = project_increments, \
                                                    release__project=p_project).distinct().count()
            else:
                parent_releases = project_manager.get_child_releases(project.slug, 1, [release])
                total_cards = project.stories.filter(iteration__program_increment_schedule__increment__in = project_increments, \
                                                    release__in = parent_releases, release__project=p_project).distinct().count()

            data[p_project.id] = total_cards
        return data

    def _get_cards_sibling_dependency(self, project, increment_id, release = None):
        portfolio_level = project.portfolio_level
        sibling_projects = Project.objects.filter(portfolio_level=portfolio_level).exclude(slug=project.slug)
        root_increment = ProgramIncrement.objects.get(id=increment_id)
        project_increments = project_manager.get_child_increments(project.slug, 1, [root_increment])            

        data = {}

        for s_project in sibling_projects:
            if release is None:
                total = Story.objects.filter(project = s_project, dependent_stories__project = project,\
                                            iteration__program_increment_schedule__increment__in = project_increments).distinct().count()
            else:
                parent_releases = project_manager.get_child_releases(project.slug, 1, [release])
                total = Story.objects.filter(project = s_project, dependent_stories__project = project,\
                                            release__in = parent_releases,\
                                            iteration__program_increment_schedule__increment__in = project_increments).distinct().count()

            data[s_project.id] = total
            
        return data


    def _get_cell_cards(self, request, project, cell, iteration_id=None, increment_id=None, release=None):
        total_cards = project.stories.filter(cell__time_type=cell)
        if iteration_id is not None:
            cell_cards = total_cards.filter(iteration_id = iteration_id)
        else:
            root_increment = ProgramIncrement.objects.get(id=increment_id)
            project_increments = project_manager.get_child_increments(project.slug, 1, [root_increment])
            
            if release is None:
                cell_cards = total_cards.filter(iteration__program_increment_schedule__increment__in = project_increments).distinct()
            else:
                parent_releases = project_manager.get_child_releases(project.slug, 1, [release])
                cell_cards = total_cards.filter(iteration__program_increment_schedule__increment__in = project_increments, \
                                                release__in = parent_releases).distinct()
        
        return cell_cards

    def _get_cell_stats(self, request, project, cell, iteration_id=None, increment_id=None, release=None):
        cell_title = ["Waiting", "Committed", "In Progress", "Done"]
        total_cards = project.stories.filter()
        
        if iteration_id is not None:
            total_cards = total_cards.filter(iteration_id = iteration_id)
            total_aging = self._get_stories_cell_time(total_cards)

        elif increment_id is not None:
            root_increment = ProgramIncrement.objects.get(id=increment_id)
            project_increments = project_manager.get_child_increments(project.slug, 1, [root_increment])

            # filter down for release selected at root level
            if release is not None:
                parent_releases = project_manager.get_child_releases(project.slug, 1, [release])
                total_cards = total_cards.filter(iteration__program_increment_schedule__increment__in = project_increments, \
                                                release__in = parent_releases).distinct()
                total_aging = self._get_stories_cell_time(total_cards)

            else:
                total_cards = total_cards.filter(iteration__program_increment_schedule__increment__in = project_increments).distinct()
                total_aging = self._get_stories_cell_time(total_cards)
        
        else:
            total_aging = self._get_stories_cell_time(total_cards)
        
        cell_cards = total_cards.filter(cell__time_type=cell)
        try:
            avg_aging = total_aging[cell]/len(cell_cards)
        except ZeroDivisionError:
            avg_aging = 0
        
        return {"cell": cell_title[cell],\
                "cell_type": cell,\
                "total_cards": len(cell_cards),\
                "avg_time": avg_aging,\
                "total_time": total_aging[cell]}


    def _get_level_stats(self, cell, root, portfolio_level, increment_id=None, release=None):
        cell_title = ["waiting", "Committed", "inprogress", "done"]

        root_increment = ProgramIncrement.objects.get(id=increment_id)
        project_increments = project_manager.get_level_increments(portfolio_level, 1, [root_increment])
        level_projects = Project.objects.filter(portfolio_level__level_number=portfolio_level, portfolio_level__portfolio__root=root)

        aging = 0
        # filter down for release selected at root level
        if release is not None:
            parent_releases = project_manager.get_level_releases(portfolio_level, 1, [release])
            total_cards = Story.objects.filter(release__in = parent_releases, \
                                               iteration__program_increment_schedule__increment__in = project_increments).distinct()
        else:
            total_cards = Story.objects.filter(iteration__program_increment_schedule__increment__in = project_increments).distinct()

        total_aging = self._get_stories_cell_time(total_cards)
        cell_cards = total_cards.filter(cell__time_type=cell)
        
        return {"cell": cell_title[cell],\
                "cell_type": cell,\
                "total_cards": len(cell_cards),\
                "total_time": total_aging[cell]}


    def _get_stories_cell_time(self, stories):
        cells = {BoardCell.WAIT_TIME: 0, BoardCell.SETUP_TIME: 0, BoardCell.WORK_TIME: 0, BoardCell.DONE_TIME: 0}

        for story in stories:
            cache_key = "card-aging-info-%d" % (story.id, )
            cached_value = cache.get(cache_key)

            if not cached_value:
                aging = tuple(kanban_manager.get_aging_info(story))
                cache.set(cache_key, aging, self.CACHE_SECONDS)
            else:
                aging = cached_value

            for i,d in enumerate(aging):
                cells[d[0].time_type] += d[1] 

        return cells