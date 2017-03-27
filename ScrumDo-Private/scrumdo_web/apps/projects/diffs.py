from django.utils.html import strip_tags
import apps.html2text as html2text

from apps.kanban.models import BoardCell
from apps.projects.models import Iteration, Story, Project


def translate_epic_diffs(diffs, project):
    epic_mappers = {        
        'summary':lambda val: "Summary: %s -> %s" % val,
        'detail':lambda val: "Detail: %s -> %s" % val,
        'points':lambda val: "Point Value: %s -> %s" % val,
        'status':lambda val: "Status: %s -> %s" % (val[0].name, val[1].name),
        'archived':lambda val: "Archived: %s -> %s" % val,
    }
    if diffs == None:
        return {}
    tdiffs = {}
    for k,v in diffs.iteritems():
        # logger.debug("Translate diffs %s %s" % (k,v) )
        if k in epic_mappers:
            newval = epic_mappers[k](v)
            if newval:
                tdiffs[k] = newval
        
    return tdiffs


def _translateRelease(val):
    try:
        new_id = val[1]
        old_id = val[0]
        try:
            newRelease = strip_tags(Story.objects.get(id=new_id).summary)
        except Story.DoesNotExist:
            newRelease = 'None'

        try:
            oldRelease = strip_tags(Story.objects.get(id=old_id).summary)
        except Story.DoesNotExist:
            oldRelease = 'None'

        return "Release: %s -> %s" % (oldRelease, newRelease)
    except:
        return None


def _translateIteration(val):
    try:
        new_id = val[1]
        old_id = val[0]        
        newIteration = Iteration.objects.get(id=new_id)
        oldIteration = Iteration.objects.get(id=old_id)

        oldLabel = "%s / %s" % (oldIteration.project.name, oldIteration.name)
        newLabel = "%s / %s" % (newIteration.project.name, newIteration.name)
        
        return "Iteration: %s -> %s" % (oldLabel, newLabel)
        
    except:
        return None


def _translateCell(val):    
    new_id = val[1]
    try:
        cell = BoardCell.objects.get(id=new_id)
        return "Moved card into %s" % cell.full_label
    except:
        return None

def _translateLable(val):
    try:
        prev_label_name,new_label_name = [],[]
        for key, value in val[0].iteritems():
            prev_label_name.append(value['name'])
        prev_message = ', '.join(map(str, prev_label_name)) if len(val[0])>0 else "None"

        for key, value in val[1].iteritems():
            new_label_name.append(value['name'])
        new_message = ', '.join(map(str, new_label_name)) if len(val[1])>0 else "None"
        return "Labels: %s -> %s" % (prev_message, new_message)
    except:
        return None
        
def _translateProject(val):
    try:
        new_id = val[1]
        old_id = val[0]        
        newProject = Project.objects.get(id=new_id)
        oldProject = Project.objects.get(id=old_id)
        return "Project: %s -> %s" % (oldProject.name, newProject.name)
    except:
        return None

def date_or_none(date):
    if date is None:
        return "None"
    return date.strftime('%Y-%m-%d')

def _translateEstimate(val):
    try:
        h,m = divmod(val[0], 60)
        h1,m1 = divmod(val[1], 60)
        return "Estimate Time: %d:%02d hr -> %d:%02d hr" % (h,m,h1,m1)
    except:
        return None

def translate_diffs(diffs, project):
    mappers = {        
        'summary': lambda val: "Previous Summary: %s" % html2text.html2text(val[0]),
        'detail': lambda val: "Detail: %s -> %s" % (html2text.html2text(val[0]), html2text.html2text(val[1])),
        'labels': _translateLable,
        'modified': lambda val: None,
        'assignee': lambda val: "Assigned To: %s -> %s" % val,
        'points': lambda val: "Point Value: %s -> %s" % val,
        'time_criticality': lambda val: "Time Criticality Value: %s -> %s" % val,
        'risk_reduction': lambda val: "Risk Reduction / Opportunity Enablement Value: %s -> %s" % val,
        'iteration': lambda val: "Iteration: %s -> %s" % (val[0].name, val[1].name),
        'project': lambda val: "Project: %s -> %s" % (val[0].name, val[1].name),
        'status': lambda val: "Status: %s -> %s" % (project.getStatusName(val[0]), project.getStatusName(val[1]) ),
        'category': lambda val: "Category: %s -> %s" % val,
        'epic': lambda val: "Epic: %s -> %s" % val,
        'extra_1': lambda val: "%s: %s -> %s" % (project.extra_1_label, html2text.html2text(val[0]), html2text.html2text(val[1])),
        'extra_2': lambda val: "%s: %s -> %s" % (project.extra_2_label, html2text.html2text(val[0]), html2text.html2text(val[1])),
        'extra_3': lambda val: "%s: %s -> %s" % (project.extra_3_label, html2text.html2text(val[0]), html2text.html2text(val[1])),
        'due_date': lambda val: "Due Date: %s -> %s" % (date_or_none(val[0]), date_or_none(val[1])),
        'board_cell': lambda val: "Moved Card 12121",
        'cell_id': _translateCell,
        'project_id': _translateProject,
        'iteration_id': _translateIteration,
        'release_id': _translateRelease,
        'assignees_cache': lambda val: "Changed assignees %s -> %s" % val,
        'estimated_minutes': _translateEstimate,
        'blocked': lambda val: "Blocked: %s" % val[1],
        'unblocked': lambda val: "Unblocked: %s" % val[1],
        'aging_reset': lambda val: "Reset card aging",
    }
    if diffs == None:
        return {}
    tdiffs = {}
    for k,v in diffs.iteritems():
        # logger.debug("Translate diffs %s %s" % (k,v) )
        if k in mappers:
            newval = mappers[k](v)
            if newval:
                tdiffs[k] = newval
        
    return tdiffs

def translate_note_diffs(diffs, project):
    note_mappers = {        
        'title':lambda val: "Title: %s -> %s" % val,
        'body':lambda val: "Detail: %s" % val[1],
    }
    if diffs == None:
        return {}
    tdiffs = {}
    for k,v in diffs.iteritems():
        # logger.debug("Translate diffs %s %s" % (k,v) )
        if k in note_mappers:
            newval = note_mappers[k](v)
            if newval:
                tdiffs[k] = newval
        
    return tdiffs