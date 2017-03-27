from .models import StepMovement, CellMovement, BoardCell, CellMovementLog, TagMovementLog, TagMovement
from apps.projects.models import Epic, Iteration

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import S3ResponseError

from django.conf import settings
from django_redis import get_redis_connection

from collections import defaultdict, namedtuple
from contextlib import contextmanager

import logging
import tempfile
import hashlib
import csv
import codecs
import cStringIO
import datetime
import os
import ast

if settings.DEBUG:
    GEN_CACHE_TIMEOUT = 30
else:
    GEN_CACHE_TIMEOUT = 300

EPOCH = datetime.datetime.utcfromtimestamp(0)

logger = logging.getLogger(__name__)


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        dialect.lineterminator = "\n"
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def _encode(self, s):
        if hasattr(s, "encode"):
            return s.encode("utf-8")
        return s

    def writerow(self, row):
        self.writer.writerow([self._encode(s) for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def isStoryComplete(story):
    cell = story.cell
    if cell is None:
        return story.iteration.iteration_type == Iteration.ITERATION_ARCHIVE
    return cell.time_type == BoardCell.DONE_TIME


def resetTagReportData(project):
    TagMovementLog.objects.filter(project=project).delete()
    deleteTagReportData(project)


def deleteTagReportData(project):
    connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = connection.get_bucket(settings.AWS_REPORTING_BUCKET)
    key = Key(bucket)
    key.key = getGeneratedTagReportKey(project)
    key.delete()


def resetWorkflowReportData(project, workflow):
    CellMovementLog.objects.filter(project=project, workflow=workflow).delete()
    deleteWorkflowReportDataFile(project, workflow)


def deleteWorkflowReportDataFile(project, workflow):
    connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = connection.get_bucket(settings.AWS_REPORTING_BUCKET)
    key = Key(bucket)
    key.key = getGeneratedCellReportKey(project, workflow)
    key.delete()


def getReportKey(reportType, workflow, assignee, tag, category, epic):
    query = hashlib.sha224("%s%s%s%s" % (assignee, tag, category, epic)).hexdigest()
    # logger.debug("Report key query: %s" % query)
    return "%s/%d/%s" % (reportType, workflow.id, query)


def getCellMovements(project, assignee, tag, category, epic):
    result = CellMovement.objects.filter(story__project=project).order_by("created").select_related("story",
                                                                                                    "related_iteration",
                                                                                                    "cell_to")
    return applyStoryFilters(result, assignee, tag, category, epic)


def getMovements(workflow, assignee, tag, label, epic, afterDate=None):
    result = StepMovement.objects.filter(workflow=workflow).order_by("created")
    if afterDate is not None:
        # Sometimes, we have cached values and only need to update
        # the records after them.  In those cases, afterDate will
        # be set.
        result = result.filter(created__gte=afterDate)

    return applyStoryFilters(result, assignee, tag, label, epic)


def getParentEpics(epic):
    if epic is None:
        return []
    rv = [epic.id]
    while epic.parent:
        epic = epic.parent
        rv.append(epic.id)
    return rv


def getChildEpics(epic):
    if epic is None:
        return []
    result = [epic.id]
    for child in epic.children.all():
        result += getChildEpics(child)
    return result


def applyStoryFilters(query, assignee, tag, label, epic):
    # Be aware, the query might be for either CellMovement or StepMovement records, which
    # both contain a story field. 
    if assignee:
        assignee_ids = [int(x) for x in assignee.split(',')] #convert unicode into list of assignee id
        query = query.filter(story__assignee__id__in=assignee_ids).distinct()
    if tag:
        query = query.filter(story__story_tags__tag__name=tag)
    if label:
        query = query.filter(story__labels__id=label)
    if epic:
        # Generate a list of sub epics.
        epics = getChildEpics(Epic.objects.get(id=epic))
        query = query.filter(story__epic_id__in=epics)

    return query


def dateTimestamp(date):
    delta = date - EPOCH
    return int(delta.total_seconds())


def getGeneratedCellReportKey(project, workflow):
    return "reports/cell/{project.slug}/workflow-{workflow.id}".format(project=project, workflow=workflow)


def getGeneratedTagReportKey(project):
    return "reports/tag/{project.slug}-tag".format(project=project)


def uploadGeneratedTagReportData(project, filename):
    connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = connection.get_bucket(settings.AWS_REPORTING_BUCKET)
    key = Key(bucket)
    key.key = getGeneratedTagReportKey(project)
    key.set_contents_from_filename(filename)


def uploadGeneratedCellReportData(project, workflow, filename):
    connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = connection.get_bucket(settings.AWS_REPORTING_BUCKET)
    key = Key(bucket)
    key.key = getGeneratedCellReportKey(project, workflow)
    key.set_contents_from_filename(filename)


def downloadGeneratedTagReportData(project):
    connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = connection.get_bucket(settings.AWS_REPORTING_BUCKET)
    key = Key(bucket)
    key.key = getGeneratedTagReportKey(project)
    outputFile = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
    outputFile.close()
    filename = outputFile.name
    try:
        key.get_contents_to_filename(filename)
    except S3ResponseError:
        logger.info('No content to download.')
    return filename


def downloadGeneratedCellReportData(project, workflow):
    connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = connection.get_bucket(settings.AWS_REPORTING_BUCKET)
    key = Key(bucket)
    key.key = getGeneratedCellReportKey(project, workflow)
    outputFile = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
    outputFile.close()
    filename = outputFile.name
    try:
        key.get_contents_to_filename(filename)
    except S3ResponseError:
        logger.info('No content to download.')
    return filename


def getLatestTagReportData(project):
    filename = conditionalGenerateTagReportData(project)
    if filename:
        # We just generated some new data, yay!
        return filename
    return downloadGeneratedTagReportData(project)



def getLatestCellReportData(project, workflow):
    filename = conditionalGenerateCellReportData(project, workflow)
    if filename:
        # We just generated some new data, yay!
        return filename
    # No new data, lets grab the existing stuff instead...
    return downloadGeneratedCellReportData(project, workflow)


def conditionalGenerateCellReportData(project, workflow):
    """ If there are new CellMovement records, generates a report data file and uploads it to S3.
    :param project:
    :param workflow:
    :return: filename if we did generate something, None otherwise.
    """

    lastGeneration, created = CellMovementLog.objects.get_or_create(project=project, workflow=workflow)

    if created:
        # This fixes a bug where a datafile exists, but the CellMovementLog doesn't, it should only
        # really happen in development, but I'll clean it up here just to be sure.
        deleteWorkflowReportDataFile(project, workflow)


    try:
        lastMovement = CellMovement.objects.filter(story__project=project).order_by("-created")[0]
    except IndexError:
        # No movements at all, skip it
        return None

    if lastGeneration.last_cell_movement < lastMovement.id:
        # There have been movements since the last time we've done this.
        redis = get_redis_connection('default')
        cache_key = "cell-report-gen-{project.slug}-{workflow.id}".format(project=project, workflow=workflow)
        existingFilename = False
        if redis.get(cache_key):
            # STOP! Someone else is calculating this data right now.
            logger.info("Tried to generate cell report data, but someone else already was.")
            return None

        try:
            redis.setex(cache_key, GEN_CACHE_TIMEOUT, True)

            existingFilename = downloadGeneratedCellReportData(project, workflow)

            newFilename = generateCellReportData(project,
                                                 workflow,
                                                 fromCellMovementId=lastGeneration.last_cell_movement,
                                                 filename=existingFilename)

            lastGeneration.last_cell_movement = lastMovement.id
            lastGeneration.save()

            # So, at this point, we downloaded any existing data, updated it, and we're ready to upload it again.
            uploadGeneratedCellReportData(project, workflow, newFilename)
        finally:
            redis.delete(cache_key)
            if existingFilename:
                    os.unlink(existingFilename)

        return newFilename

    return None


def conditionalGenerateTagReportData(project):
    """ If there are new CellMovement records, generates a report data file and uploads it to S3.
    :param project:
    :return: filename if we did generate something, None otherwise.
    """

    # DEBUG
    # resetTagReportData(project)



    lastGeneration, created = TagMovementLog.objects.get_or_create(project=project)
    try:
        lastMovement = TagMovement.objects.filter(story__project=project).order_by("-created")[0]
    except IndexError:
        # No movements at all, skip it
        return None



    if created:
        # This fixes a bug where a datafile exists, but the CellMovementLog doesn't, it should only
        # really happen in development, but I'll clean it up here just to be sure.
        deleteTagReportData(project)

    if lastGeneration.last_tag_movement < lastMovement.id:
        # There have been movements since the last time we've done this.
        redis = get_redis_connection('default')
        cache_key = "tag-report-gen-{project.slug}".format(project=project)
        if redis.get(cache_key):
            # STOP! Someone else is calculating this data right now.
            logger.info("Tried to generate tag report data, but someone else already was.")
            return None

        try:
            redis.setex(cache_key, GEN_CACHE_TIMEOUT, True)

            existingFilename = downloadGeneratedTagReportData(project)

            newFilename = generateTagReportData(project,
                                                fromTagMovementId=lastGeneration.last_tag_movement,
                                                filename=existingFilename)
            lastGeneration.last_tag_movement = lastMovement.id
            lastGeneration.save()

            # So, at this point, we downloaded any existing data, updated it, and we're ready to upload it again.
            uploadGeneratedTagReportData(project, newFilename)
        finally:
            redis.delete(cache_key)
            os.unlink(existingFilename)
        return newFilename

    return None


def _preProcessTagData(inputFileName, csvwriter):
    """When we're updating an existing tag data file, there is a good chance that file will
       contain null exit time records in it.  Those represent records that were still open
       at the time of the last generation.  In those cases, this generation might
       close those records.  This pre-process finds them and sets up some state
       so our normal processing will work."""
    recordsByStoryTag = {}  # key: story_id:tag
    tagsByStory = defaultdict(set)  # key=story_id  value=set of tags
    with open(inputFileName, "rt") as inFile:
        reader = UnicodeReader(inFile, delimiter='|', quotechar='\'')
        for row in reader:
            (story_id, _, tag, _, exitTime, _, _, _, _, _, _) = row
            if exitTime == '':
                story_id = int(story_id)
                key = "{story_id}:{tag}".format(story_id=story_id, tag=tag)
                recordsByStoryTag[key] = row
                tagsByStory[story_id].add(tag)
            else:
                # Records that were closed out are good to go and we can just write them.
                csvwriter.writerow(row)
    return recordsByStoryTag, tagsByStory


def generateTagReportData(project, fromTagMovementId=0, filename=None):
    recordsByStoryTag = {}  # key: story_id:tag
    tagsByStory = defaultdict(set)  # key=story_id  value=set of tags

    outputFile = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
    csvwriter = UnicodeWriter(outputFile, delimiter='|', quotechar='\'', quoting=csv.QUOTE_MINIMAL)

    if filename:
        (recordsByStoryTag, tagsByStory) = _preProcessTagData(filename, csvwriter)

    for tagMovement in TagMovement.objects.filter(id__gt=fromTagMovementId,
                                                  story__project=project).select_related("story").order_by("created"):
        story = tagMovement.story

        try:
            epic = Epic.objects.get(id=tagMovement.epic_id)
            epic_ids = ",".join([str(epicid) for epicid in getParentEpics(epic)])
        except Epic.DoesNotExist:
            epic_ids = ""
        labelIDs = tagMovement.label_ids
        assignees = tagMovement.assignee_ids

        tags = set(tagMovement.tags_cache.split(","))
        addedTags = tags.difference(tagsByStory[story.id])
        removedTags = tagsByStory[story.id].difference(tags)
        for newTag in addedTags:
            if not newTag:
                continue
            storytag = "{story_id}:{tag}".format(story_id=story.id, tag=newTag)
            rec = [story.id, tagMovement.related_iteration_id,
                   newTag, dateTimestamp(tagMovement.created), None,
                   assignees, story.tags_cache,
                   labelIDs, epic_ids, story.points_value(), story.local_id]
            recordsByStoryTag[storytag] = rec
            tagsByStory[story.id].add(newTag)

        for removedtag in removedTags:
            storytag = "{story_id}:{tag}".format(story_id=story.id, tag=removedtag)
            existing = recordsByStoryTag[storytag]
            existing[4] = dateTimestamp(tagMovement.created)
            csvwriter.writerow(existing)
            del recordsByStoryTag[storytag]
            tagsByStory[story.id].remove(removedtag)

        # TODO - what if the filtering changed for a tag that wasn't added/removed

    # ok, now at the end we have some leftover records to output
    for k, v in recordsByStoryTag.iteritems():
        csvwriter.writerow(v)

    outputFile.close()
    logger.info("Generated tag report data")
    return outputFile.name


def _preProcessCellData(inputFileName, csvwriter):
    """When we're updating an existing cell data file, there is a good chance that file will
       contain null exit time records in it.  Those represent records that were still open
       at the time of the last generation.  In those cases, this generation might
       close those records.  This pre-process finds them and sets up some state
       so our normal processing will work."""
    recordsByStory = {}

    with open(inputFileName, "rt") as inFile:
        reader = UnicodeReader(inFile, delimiter='|', quotechar='\'')
        for row in reader:
            (story_id, _, step_id, _, exitTime, _, _, _, _, _, _, _) = row
            if exitTime == '':
                story_id = int(story_id)
                recordsByStory[story_id] = row
            else:
                # Records that were closed out are good to go and we can just write them.
                csvwriter.writerow(row)
    return recordsByStory


def generateCellReportData(project, workflow, fromCellMovementId=0, filename=None):
    cellToSteps = defaultdict(list)
    for step in workflow.steps.all():
        for cell in step.cells.all():
            cellToSteps[cell.id].append(step)

    recordsByStory = {}

    outputFile = tempfile.NamedTemporaryFile(mode='wt', delete=False)
    csvwriter = UnicodeWriter(outputFile, delimiter='|', quotechar='\'', quoting=csv.QUOTE_MINIMAL)

    if filename:
        recordsByStory = _preProcessCellData(filename, csvwriter)

    for cellMovement in CellMovement.objects.filter(id__gt=fromCellMovementId,
                                                    story__project=project)\
            .select_related("story", "cell_to").order_by("created"):

        story = cellMovement.story
        try:
            epic = Epic.objects.get(id=cellMovement.epic_id)
            epic_ids = ",".join([str(epicid) for epicid in getParentEpics(epic)])
        except Epic.DoesNotExist:
            epic_ids = ""
        labelIDs = cellMovement.label_ids
        assignees = cellMovement.assignee_ids

        steps = cellToSteps[cellMovement.cell_to_id]
        for step in steps:
            rec = [story.id, cellMovement.related_iteration_id,
                   step.id, dateTimestamp(cellMovement.created), None,
                   assignees, story.tags_cache,
                   labelIDs, epic_ids, story.points_value(), story.local_id, story.estimated_minutes]

            if story.id in recordsByStory:
                # ok, so here we are, with a cell movement for a given story AND we previously had
                # a record for that story.  This means that this cell movement represents a movement OUT
                # of that previous record and we should set the exit
                existing = recordsByStory[story.id]
                existing[4] = dateTimestamp(cellMovement.created)
                csvwriter.writerow(existing)
            recordsByStory[story.id] = rec
        if not steps:
            # We had a cell movement that didn't go into a step of this workflow..
            # therefore we exited this workflow.
            if story.id in recordsByStory:
                existing = recordsByStory[story.id]
                existing[4] = dateTimestamp(cellMovement.created)
                csvwriter.writerow(existing)
                del recordsByStory[story.id]
                if cellMovement.related_iteration_id and cellMovement.related_iteration.iteration_type == Iteration.ITERATION_ARCHIVE:
                    # HEY! it went into the archive, and we do care about knowing that.  We can handle it like
                    # a normal record and use a special placeholder step id (-1) to represent that.
                    # If it's later moved out of the archive and into a step, it still works out fine and the
                    # exit will get filled in
                    # Note, this is purposfully under "if story.id in recordsByStory:" because we only care
                    # about cards that hit this workflow, and then later moved to the archive.  Since we're ordering
                    # by CellMovement.created now, this should work out.
                    rec = [story.id, cellMovement.related_iteration_id,
                           -1, dateTimestamp(cellMovement.created), None,
                           assignees, story.tags_cache,
                           labelIDs, epic_ids, story.points_value(), story.local_id, story.estimated_minutes]
                    recordsByStory[story.id] = rec

    # ok, now at the end we have some leftover records to output
    for k,v in recordsByStory.iteritems():
        csvwriter.writerow(v)
    outputFile.close()
    logger.info("Generated cell report data")
    return outputFile.name


def json_default(obj):
    """Default JSON serializer to handle date/times "2015-03-31T12:21:04",."""
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    return str(obj)