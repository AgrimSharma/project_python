from django import template
from apps.projects.models import *
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
import re
register = template.Library()
from apps.projects.util import smart_truncate


@register.filter
def show_entry_label(entry):
    
    rv = ""

    if entry.task:
        rv = "Story <a href='%s'>%s-%d</a> %s<br/>Task: %s<br/><small>" % (reverse("story_permalink",kwargs={'story_id':entry.story.id}), entry.story.project.prefix ,entry.story.local_id, smart_truncate(entry.story.summary), entry.task.summary)
    elif entry.story:
        rv = "Story <a href='%s'>$s-%d</a> %s<br/><small>" % (reverse("story_permalink",kwargs={'story_id':entry.story.id}), entry.story.project.prefix, entry.story.local_id,smart_truncate(entry.story.summary))

    rv += "<a href='%s'>%s</a>" % (reverse('project_detail',kwargs={'group_slug':entry.project.slug}),entry.project.name)
    if entry.iteration:
        rv += " / <a href='%s'>%s</a>" % ( reverse('iteration', kwargs={'group_slug':entry.project.slug, 'iteration_id':entry.iteration.id}), entry.iteration.name )
    if entry.task or entry.story:
        rv += "</small>"
    return mark_safe(rv)


@register.filter
def minutes_to_hours(minutes):
    minutes = int(minutes)
    return "%d:%02d" % (int(minutes/60), minutes%60)

@register.filter
def show_project(entry):
    project = entry.project
    if project:
        return project.name
    return ""
    
@register.filter
def show_iteration(entry):
    iteration = entry.iteration
    if iteration:
        return iteration.name
    return ""

@register.filter
def show_story(entry):
    story = entry.story
    if story:
        return "#%d %s" % (story.local_id, smart_truncate(story.summary) )
    return ""

@register.filter
def show_task(entry):
    task = entry.task
    if task:
        return smart_truncate(task.summary) 
    return ""

             