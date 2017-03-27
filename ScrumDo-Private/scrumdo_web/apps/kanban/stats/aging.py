from apps.kanban.util import getLatestTagReportData
from ..util import getMovements, dateTimestamp, getLatestCellReportData, UnicodeReader

from apps.kanban.models import WorkflowStep

from collections import defaultdict

import math
import logging
import sys
import traceback
import os
import datetime

logger = logging.getLogger(__name__)

REPORT_COLORS = [0x3898DB, 0x34CC73, 0xBF392B, 0x9A59B5, 0xE57E24, 0x23BC9C, 0xF5764E, 0x1F1581,
                 0x448cca, 0x0D7D5B, 0xA60D05, 0x818B16, 0x8dc73e, 0xFFC54A, 0xff7f0e]

def _rowMatches(rowStepId, rowTag, agingSteps, agingTags, agingData):
    if agingData == 'step':
        return int(rowStepId) in agingSteps
    elif agingData == 'tag':
        return rowTag in agingTags

    return False


def _passes_filters(row, assignee, label, epic, tag):
    (_, _, _, _, _, rowAssignees, rowTags, rowLabels, rowEpic_id, _, _, _) = row
    if label and label not in rowLabels.split(","):
        return False
    if epic and epic != rowEpic_id:
        return False
    if assignee and assignee not in rowAssignees.split(","):
        return False
    if tag and tag not in rowTags.split(","):
        return False
    return True



def generateAgingFromCSV(filename, project, workflow, agingType, agingData, agingSteps, agingTags,
                         filterAssignee, filterLabel, filterEpic, filterTag, startdate, enddate):
    relativeAgeByStep = defaultdict(lambda: 0)

    # A two dimensional defaultdict
    # ageBreakdownEntries[story_id][step] = length the story spent in that step
    ageBreakdownEntries = defaultdict(lambda: defaultdict(lambda: 0))

    histogramAges = defaultdict(lambda: 0)

    todayTimestamp = dateTimestamp(datetime.datetime.now())

    with open(filename, 'rb') as csvfile:
        reader = UnicodeReader(csvfile, delimiter='|', quotechar='\'')
        for row in reader:
            (story_id, iteration_id, step_id, enterTime, exitTime, assignees, tags,
             labels, epic_id, points, story_number, estimated_minutes) = row

            if step_id == '-1':
                continue

            # Make sure this row is for the requested steps or tags
            if not _rowMatches(step_id, step_id, agingSteps, agingTags, agingData):
                continue

            if not _passes_filters(row, filterAssignee, filterLabel, filterEpic, filterTag):
                continue

            enterTime = int(enterTime)
            if exitTime == '' or exitTime is None:
                exitTime = todayTimestamp
            else:
                exitTime = int(exitTime)

            length = int(exitTime) - int(enterTime)
            days = int(round(length/(60*60*24)))  # Simple 24 hour days is fine for this.
            # logger.info((story_id, days, length))
            if agingType == 1:  # Age Histogram
                histogramAges[story_id] += length
            elif agingType == 2:  # Age Breakdown
                ageBreakdownEntries[story_id][step_id] += length
            elif agingType == 3:  # Relative age
                relativeAgeByStep[step_id] += length

    if agingType == 1:
        # At this point, we have a map of story_id to total time that story spent
        # So we can collate that to a frequency to build the histogram from.
        hisogramData = defaultdict(lambda: 0)
        for story_id, length in histogramAges.iteritems():
            days = int(round(length/(60*60*24)))  # Simple 24 hour days is fine for this.
            hisogramData[days] += 1
        return hisogramData

    if agingType == 2:
        r = []
        collated = defaultdict(list)
        for v in ageBreakdownEntries.values():
            for step_id, length in v.iteritems():
                days = int(round(length/(60*60*24)))
                collated[step_id].append(days)
        for key, data in collated.iteritems():
            if agingData == 'step':
                name = WorkflowStep.objects.get(id=key).name
            else:
                name = key
            data = sorted(data)
            r.append({
                'name': name,
                'median': data[int(math.floor(len(data)/2))],
                'mean': int(round(sum(data) / len(data))),
                'min': min(data),
                'max': max(data)
            })
        return r

    if agingType == 3:
        rv = []
        i = 0
        for step_id, length in relativeAgeByStep.iteritems():
            if agingData == 'step':
                step = WorkflowStep.objects.get(id=step_id)
                name = step.name
                color = step.report_color
            else:
                name = step_id
                color = REPORT_COLORS[i % len(REPORT_COLORS)]
                i += 1
            days = int(round(length/(60*60*24)))  # Simple 24 hour days is fine for this.
            rv.append({'label': name, 'days': days, 'color': color})
        return rv


    return {'error': 'Invalid Aging Type'}



def calculateAging(project, workflow, agingType, agingData, agingSteps, agingTags,
                   assignee, label, epic, tag, startdate, enddate):
    if agingData == 'step':
        filename = getLatestCellReportData(project, workflow)
    else:
        filename = getLatestTagReportData(project)
    try:
        r = generateAgingFromCSV(filename,
                                 project,
                                 workflow,
                                 agingType,
                                 agingData,
                                 agingSteps,
                                 agingTags,
                                 assignee,
                                 label,
                                 epic,
                                 tag,
                                 startdate,
                                 enddate)
        return r
    except:
        logger.error("\n".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
        return {'error': True}
    finally:
        os.unlink(filename)

