from .. import managers 
from django import template
from apps.projects.models import Story
from apps.kanban.models import BoardCell
register = template.Library()

@register.filter("current_card_count")
def current_card_count(project):
    return Story.objects.filter(project=project, iteration__iteration_type=1).count()

@register.filter("archived_card_count")
def archived_card_count(project):
    return managers.getArchiveIteration(project).stories.count()

@register.filter("kanban_points_in_progress")
def kanban_points_in_progress(iteration):
    points = 0
    for story in iteration.stories.filter(points__gt=0).select_related("cell"):
        if (story.cell is not None) and ( (story.cell.time_type == BoardCell.SETUP_TIME) or (story.cell.time_type == BoardCell.WORK_TIME) ):
            points += story.points_value();
    return points

@register.filter("kanban_points_completed")
def kanban_points_completed(iteration):
    points = 0
    for story in iteration.stories.filter(points__gt=0).select_related("cell"):
        if (story.cell is not None) and story.cell.time_type == BoardCell.DONE_TIME:
            points += story.points_value();
    return points