from django.template.defaultfilters import last
from ..util import getCellMovements, getReportKey
from ..models import BoardCell
from apps.projects.models import Iteration, TimeEntry
from apps.projects.util import reduce_burndown_data
import logging
import math

import time

logger = logging.getLogger(__name__)


def isSameTimePeriod(lastDate, thisDate):
    if lastDate is None:
        return False
    h1 = math.floor(thisDate.hour/4)  # do 4 time slices per day
    h2 = math.floor(lastDate.hour/4)
    return h1 == h2 and lastDate.year == thisDate.year and lastDate.month == thisDate.month and lastDate.day == thisDate.day


def _record(result, date, todo, done):
    # logger.info(date)
    # t = 0
    # d = 0
    # for s in todo:
    #     logger.info("#%d %d %d" % (s.local_id, s.points_value(), t) )
    #     t += s.points_value()
    # for s in done:
    #     logger.info("#%d %d %d" % (s.local_id, -1 * s.points_value(), d) )
    #     d += s.points_value()
    # logger.info("%d - %d = %d" % (t,d,t-d))
    todo = sum(s.points_value() for s in todo)
    done = sum(s.points_value() for s in done)
    result.append({'date': date, 'todo': todo, 'done':done})


def _removeFrom(removeFrom, story):
    if story in removeFrom:
        removeFrom.remove(story)

def _removeAndAdd(removeFrom, addTo, story):
    _removeFrom(removeFrom, story)
    if not story in addTo:
        addTo.append(story)


def _updateStories(doingStories, doneStories, story, cell, iteration):

    if iteration.iteration_type == Iteration.ITERATION_ARCHIVE:
        _removeAndAdd(doingStories, doneStories, story)
    elif iteration.iteration_type == Iteration.ITERATION_BACKLOG:
        if story in doneStories:   # If we move a story back to the backlog, it's not doing nor done
            doneStories.remove(story)
        if story in doingStories:
            doingStories.remove(story)
    elif cell is None:
        # here, we're in a work iteration but don't have a cell
        # this can happen when a story is in a cell, moved out of the cell, and
        # later the cell is deleted from the board and the CellMovement record
        # gets it's cell reference nulled out we're going to assume it was supposed
        # to be in-progress
        _removeAndAdd(doneStories, doingStories, story)
    elif cell.time_type == BoardCell.DONE_TIME:
        _removeAndAdd(doingStories, doneStories, story)
    else:
        _removeAndAdd(doneStories, doingStories, story)



def calculateBurn(project, iteration_id, assignee, tag, category, epic):
    iteration = project.iterations.get(id=iteration_id)
    movements = getCellMovements(project, assignee, tag, category, epic)
    result = []
    doneStories = []
    doingStories = []
    lastDate = None
    for movement in movements:
        story = movement.story
        cell = movement.cell_to
        # iteration = movement.iteration

        if movement.related_iteration_id != iteration.id:
            continue

        if lastDate is None:
            lastDate = movement.created

        if not isSameTimePeriod(lastDate, movement.created):
            _record(result, lastDate, doingStories, doneStories)
            lastDate = movement.created

        _updateStories(doingStories, doneStories, story, cell, movement.related_iteration)

    _record(result, lastDate, doingStories, doneStories)

    return result


def calculateLegacyProjectBurn(project):
    total_points = []
    claimed_points = []
    if project.burnup_reset_date is None:
        points_log = project.points_log.all()
    else:
        points_log = project.points_log.filter(date__gte=project.burnup_reset_date)

    for log in points_log:
        total_points.append([log.timestamp(), max(0,log.points_total - project.burnup_reset)])
        claimed_points.append([log.timestamp(), max(0,log.points_status10 - project.burnup_reset)])

    total_stats = {"label": "Total Points", "data": reduce_burndown_data(total_points)}
    claimed_stats = {"label": "Claimed Points", "data": reduce_burndown_data(claimed_points)}
    return [total_stats, claimed_stats]


def calculateLegacyIterationBurn(project, iteration):
    try:
        if iteration.start_date:
            start_date_timestamp = int((time.mktime(iteration.start_date.timetuple()) - time.timezone)*1000)
        if iteration.end_date:
            end_date_timestamp = int((time.mktime(iteration.end_date.timetuple()) - time.timezone)*1000)
    except Exception as e:
        return None

    has_startdate_data = False
    has_enddate_data = False
    highest_total_points = 0
    last_total_points = 0

    points = [[], [], [], [], [], [], [], [], [], [], [], [], []]

    for log in iteration.points_log.all():

        if iteration.start_date:
            if log.timestamp() > start_date_timestamp and not has_startdate_data and start_date_timestamp != 0:
                # If the first day isn't filled out, give it 0's
                for i in range(13):
                    points[i].append( [start_date_timestamp, 0])

        has_startdate_data = True
        last_total_points = log.points_total
        if iteration.end_date:
            if log.timestamp() == end_date_timestamp :
                has_enddate_data = True
        if highest_total_points < log.points_total:
            highest_total_points = log.points_total

        points[0].append([log.timestamp(), log.points_total])
        points[1].append([log.timestamp(), log.points_status1])
        points[2].append([log.timestamp(), log.points_status2])
        points[3].append([log.timestamp(), log.points_status3])
        points[4].append([log.timestamp(), log.points_status4])
        points[5].append([log.timestamp(), log.points_status5])
        points[6].append([log.timestamp(), log.points_status6])
        points[7].append([log.timestamp(), log.points_status7])
        points[8].append([log.timestamp(), log.points_status8])
        points[9].append([log.timestamp(), log.points_status9])
        points[10].append([log.timestamp(), log.points_status10])
        points[11].append([log.timestamp(), log.time_estimated])
        points[12].append([log.timestamp(), log.time_estimated_completed])

    entries = TimeEntry.objects.filter(iteration=iteration).order_by("date")
    entries_series = []
    last_day = None
    last_count = 0
    for entry in entries:
        if entry.timestamp() != last_day:
            if last_day:
                entries_series.append([last_day, last_count]);
            last_day = entry.timestamp()
            # last_count = 0 don't reset so we get cumulative counts for the charts...
        last_count += entry.minutes_spent
    if last_day:
        entries_series.append([last_day, last_count]);

    entries_series = [[e[0], int(e[1]/60)] for e in entries_series]

    if not has_enddate_data and iteration.end_date:
        points[0].append( [end_date_timestamp, last_total_points])

    # Filter out stuff too early
    if iteration.start_date:
        for i in range(13):
            points[i] = filter(lambda x:x[0]>=start_date_timestamp, points[i])
            entries_series = filter(lambda x:x[0]>=start_date_timestamp, entries_series)

    # Filter out stuff too late
    if iteration.end_date:
        for i in range(13):
            points[i] = filter(lambda x:x[0]<=end_date_timestamp, points[i])
            entries_series = filter(lambda x:x[0]<=end_date_timestamp, entries_series)

    labels = project.statuses()
    labels = ["Total Points"] + list(labels) + ["Estimated Hours", "Completed"]

    # Convert minutes to hours
    points[11] = [[d[0], d[1]/60] for d in points[11]]
    points[12] = [[d[0], d[1]/60] for d in points[12]]

    data = [0] * 14
    for i in range(13):
        data[i] = {"label":labels[i], "data":reduce_burndown_data(points[i])}

    data[11]["hourseries"] = True
    data[12]["hourseries"] = True

    for i in range(1,11):
        data[i]["stack"] = True
        data[i]["statusType"] = i - 1

    # yaxis = 2 = the hourly axis
    data[11]["yaxis"] = 2;
    data[12]["yaxis"] = 2;
    data[13] = {"hourseries":True,"yaxis":2, "label":"Hours Spent", "data":entries_series, "lines":{ "show": True, "fill": False, "opacity":0.5 }, "points":{"radius":2}}
    # data[14] = {"hourseries":True,"yaxis":2, "label":"Hours Left", "data":allocated_series, "lines":{ "show": True, "fill": False, "opacity":0.5 }, "points":{"radius":2}}

    return data
