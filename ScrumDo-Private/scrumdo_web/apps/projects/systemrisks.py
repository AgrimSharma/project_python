from django.db.models import Count, Sum, Q
from django.core.cache import cache
from django.utils.html import strip_tags

from apps.projects.models import Iteration, Project, Story, TeamIterationWIPLimit
from apps.kanban.models import BoardCell, Policy

import datetime

import logging

logger = logging.getLogger(__name__)

CACHE_SECONDS = 43200 # one day long

def cacheKey(project, iteration, type):
    key = "systemrisks_%s_%d_%d" % (type, project.id, iteration.id)
    return key

def systemRisks(project, iteration):
    iteration_risks = iterationRisks(project, iteration)
    increment_risks = incrementWipRisks(project, iteration)
    cell_header_risks = cellHeaderRisks(project, iteration)
    story_aging_risks = agingRisks(project, iteration)
    due_date_risks = dueDateRisks(project, iteration)

    risks = iteration_risks + increment_risks + cell_header_risks + story_aging_risks + due_date_risks

    return risks

def updateProjectRisks(project):
    for iteration in project.iterations.all():
        key = cacheKey(project, iteration, "cellheaderwip")
        cache.delete(key)
        cellHeaderRisks(project, iteration)


def cellHeaderRisks(project, iteration):
    cache_key = cacheKey(project, iteration, "cellheaderwip")
    cached_value = cache.get(cache_key)
    if not cached_value:
        boardCells = project.boardCells.all()
        boardHeaders = project.headers.all()
        stories = iteration.stories.all()
        risks = []
        #return if not a working Iteration
        if iteration.iteration_type != Iteration.ITERATION_WORK:
            return risks
        for cell in boardCells:
            if cell.wipLimit !=0 or cell.minWipLimit != 0 or cell.pointLimit != 0 or cell.minPointLimit != 0:
                cell_stories = stories.filter(cell_id = cell.id)
                total_cell_stories = cell_stories.count() 
                cell_points = cell_stories.aggregate(points=Sum('points'))
                if cell_points["points"] is None:
                    cell_points["points"] = 0

                related_to = {"title": cell.full_label, "id": cell.id, "type": "cell"}

                if cell.wipLimit > 0 and total_cell_stories > cell.wipLimit:
                    risks.append({"description": "%d is over WIP Limit of %d Cards in <i>%s</i> for cell <i>%s</i>" % (total_cell_stories,\
                                        cell.wipLimit, iteration.name, cell.full_label), "type": "wip", "related_to": related_to})
                
                if cell.minWipLimit > 0 and total_cell_stories < cell.minWipLimit:
                    risks.append({"description": "%d is below WIP Limit of %d Cards in <i>%s</i> for cell <i>%s</i>" % (total_cell_stories,\
                                        cell.minWipLimit, iteration.name, cell.full_label), "type": "wip", "related_to": related_to})
                
                if cell.pointLimit > 0 and cell_points["points"] > cell.pointLimit and cell_points["points"] is not None:
                    risks.append({"description": "%d is over WIP Limit of %d Points in <i>%s</i> for cell <i>%s</i>" % (cell_points["points"],\
                                        cell.pointLimit, iteration.name, cell.full_label), "type": "wip", "related_to": related_to})
                
                if cell.minPointLimit > 0 and cell_points["points"] < cell.minPointLimit and cell_points["points"] is not None:
                    risks.append({"description": "%d is below WIP Limit of %d Points in <i>%s</i> for cell <i>%s</i>" % (cell_points["points"],\
                                        cell.minPointLimit, iteration.name, cell.full_label), "type": "wip", "related_to": related_to})

        for header in boardHeaders:
            if header.policy is not None:
                policy_type = header.policy.policy_type
                related_value = header.policy.related_value
                min_related_value = header.policy.min_related_value
                if related_value !=0 or min_related_value !=0: 
                    header_cell = header.policy.cells.all()
                    header_stories = stories.filter(cell__in = header_cell)
                    total_header_stories = header_stories.count() 
                    header_points = header_stories.aggregate(points=Sum('points'))
                    if header_points["points"] is None:
                        header_points["points"] = 0
                    related_to = {"title": header.label, "id": header.id, "type": "header"}
                    
                    if policy_type == Policy.POLICY_TYPE_STORY_WIP:
                        if min_related_value>0 and total_header_stories < min_related_value:
                            risks.append({"description": "%d is below WIP Limit of %d Cards in <i>%s</i> for header <i>%s</i>" % (total_header_stories,\
                                            min_related_value, iteration.name, header.label), "type": "wip", "related_to": related_to})
                        
                        if related_value>0 and total_header_stories > related_value:
                            risks.append({"description": "%d is over WIP Limit of %d Cards in <i>%s</i> for header <i>%s</i>" % (total_header_stories,\
                                        related_value, iteration.name, header.label), "type": "wip", "related_to": related_to})

                    if policy_type == Policy.POLICY_TYPE_POINTS_WIP:
                        if min_related_value>0 and header_points["points"] < min_related_value:
                            risks.append({"description": "%d is below WIP Limit of %d Cards in <i>%s</i> for header <i>%s</i>" % (header_points["points"],\
                                            min_related_value, iteration.name, header.label), "type": "wip", "related_to": related_to})
                        
                        if related_value>0 and header_points["points"] > related_value:
                            risks.append({"description": "%d is over WIP Limit of %d Cards in <i>%s</i> for header <i>%s</i>" % (header_points["points"],\
                                        related_value, iteration.name, header.label), "type": "wip", "related_to": related_to})
        
        cache.delete(cache_key)
        cache.set(cache_key, risks, CACHE_SECONDS)
        return risks
    else:
        return cached_value

def iterationRisks(project, iteration):
    cache_key = cacheKey(project, iteration, "iterationwip")
    cached_value = cache.get(cache_key)
    if not cached_value:
        risks = []
        #return if not a working Iteration
        if iteration.iteration_type != Iteration.ITERATION_WORK:
            return risks

        stories = iteration.stories.all()
        total_stories = stories.count()
        story_points = iteration.total_points()
        
        try:
            related_to = {"title": iteration.name, "id": iteration.id, "type": "iteration"}
            limit = TeamIterationWIPLimit.objects.get(team=project, iteration=iteration)
            if total_stories > limit.featureLimit and limit.featureLimit > 0:
                risks.append({"description": "%d is over WIP Limit of %d Cards for <i>%s</i>" % (total_stories,\
                                    limit.featureLimit, iteration.name), "type": "wip", "related_to": related_to})

            if story_points > limit.featurePointLimit and limit.featurePointLimit > 0:
                risks.append({"description": "%d is over WIP Limit of %d Points for <i>%s</i>" % (story_points,\
                                    limit.featurePointLimit, iteration.name), "type": "wip", "related_to": related_to})

        except TeamIterationWIPLimit.DoesNotExist:
            pass
        
        cache.delete(cache_key)
        cache.set(cache_key, risks, CACHE_SECONDS)
        return risks
    else:
        return cached_value

def incrementWipRisks(team, iteration):
    project = iteration.project
    cache_key = cacheKey(project, iteration, "incrementwip")
    cached_value = cache.get(cache_key)
    if not cached_value:
        risks = []
        #return if not a working Iteration
        if iteration.iteration_type != Iteration.ITERATION_WORK:
            return risks

        teams = project.children.all()
        for team in teams:
            try:
                related_to = {"title": iteration.name, "id": iteration.id, "type": "iteration"}
                limit = TeamIterationWIPLimit.objects.get(team=team, iteration=iteration)
                features = iteration.stories.filter(project_assignments=team)
                points = features.aggregate(points=Sum('points'))

                if features.count() > limit.featureLimit and limit.featureLimit > 0:
                    risks.append({"description": "%d is over WIP Limit of %d Features for Team <i>%s</i> in increment <i>%s</i>" % \
                                (features.count(), limit.featureLimit, team.name, iteration.name), "type": "wip", "related_to": related_to})

                if points["points"] > limit.featurePointLimit and limit.featurePointLimit > 0:
                    risks.append({"description": "%d is over WIP Limit of %d Feature Points for Team <i>%s</i> in increment <i>%s</i>" % \
                                (points["points"], limit.featurePointLimit, team.name, iteration.name), "type": "wip", "related_to": related_to})

            except TeamIterationWIPLimit.DoesNotExist:
                pass

        cache.delete(cache_key)
        cache.set(cache_key, risks, CACHE_SECONDS)
        return risks
    else:
        return cached_value

def agingRisks(project, iteration):
    cache_key = cacheKey(project, iteration, "aging")
    cached_value = cache.get(cache_key)
    if not cached_value:
        risks = []
        #return if not a working Iteration
        if iteration.iteration_type != Iteration.ITERATION_WORK:
            return risks
        critical_threshold = project.critical_threshold
        stories = iteration.stories.all()
        # filter out done stories
        for story in stories.exclude(cell__time_type=BoardCell.DONE_TIME):
            age_hours = story.age_hours()

            title = "%s-%d %s" % (project.prefix, story.local_id, strip_tags(story.summary))
            related_to = {"title": title, "id": story.id, "type": "card"}

            if critical_threshold is not None and age_hours > critical_threshold * 24:
                days = round(age_hours/(24*1.0))
                risks.append({"description": "%d is over Critical threshold of %d days in <i>%s</i> for Card <i>%s-%d</i> %s" % (days,\
                                        critical_threshold, iteration.name, project.prefix, story.local_id, strip_tags(story.summary)), \
                                        "type": "aging", "related_to": related_to})
        
        cache.delete(cache_key)
        cache.set(cache_key, risks, CACHE_SECONDS)
        return risks
    else:
        return cached_value

def dueDateRisks(project, iteration):
    cache_key = cacheKey(project, iteration, "duedate")
    cached_value = cache.get(cache_key)
    if not cached_value:
        risks = []
        #return if not a working Iteration
        if iteration.iteration_type != Iteration.ITERATION_WORK:
            return risks
        stories = iteration.stories.all()
        duedate_threshold = project.duedate_warning_threshold

        for story in stories.exclude(Q(cell__time_type=BoardCell.DONE_TIME) | Q(due_date__isnull=True)):
            
            title = "%s-%d %s" % (project.prefix, story.local_id, strip_tags(story.summary))
            related_to = {"title": title, "id": story.id, "type": "card"}
            due_date = story.due_date
            today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            diff = (due_date - today).days

            if diff < 0:
                description = "%s due date is passed in <i>%s</i> for Card <i>%s-%d</i> %s" % \
                            (story.due_date.strftime("%Y-%m-%d"), iteration.name, project.prefix, story.local_id, strip_tags(story.summary))
                risks.append({"description": description, "type": "duedate", "related_to": related_to})
            
            elif diff < duedate_threshold:
                description = "%s due date is over Warning threshold of %d days in <i>%s</i> for Card <i>%s-%d</i> %s" % \
                            (story.due_date.strftime("%Y-%m-%d"), duedate_threshold, iteration.name, project.prefix, story.local_id, strip_tags(story.summary))

                risks.append({"description": description, "type": "duedate", "related_to": related_to})
        
        cache.delete(cache_key)
        cache.set(cache_key, risks, CACHE_SECONDS)
        return risks
    else:
        return cached_value