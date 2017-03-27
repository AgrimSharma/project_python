import apps.classic.models as cmodels
import apps.projects.models as pmodels
import apps.activities.models as amodels
import apps.organizations.models as omodels
import apps.attachments.models as atmodels
import apps.kanban.models as kmodels
import apps.email_notifications.models as emodels
from django.core.files.base import ContentFile
import apps.kanban.managers as kmanagers
from apps.projects.templatetags import projects_tags

from django.template import defaultfilters

from django.db import models
import logging
import random
import re
import string
import traceback
import sys
import json


logger = logging.getLogger(__name__)


# Var naming scheme:
#    sproject = source project / classic project
#    dproject = destination project / new project

def _htmlify(input, project):
    if input is None:
        return None
    res = projects_tags.urlify2(projects_tags.markdown_save(defaultfilters.force_escape(input)))
    if project is not None:
        return projects_tags.link_stories(res, project)
    return res

def _copyPrimitiveFields(source, dest):
    _copyFields(source, dest, _primitiveFields(source))


def _copyFields(source, dest, fields):
    """Copies named fields from a source to a destination object"""
    for fieldname in fields:
        value = getattr(source, fieldname)
        if hasattr(dest, fieldname):
            setattr(dest, fieldname, value)


def _primitiveFields(obj):
    """Returns the primitive field names of a model object.
       Very useful in combination with _copyFields!"""
    result = []
    for field in obj._meta.local_fields:
        if field.__class__ in [models.SmallIntegerField,
                               models.CharField,
                               models.DateField,
                               models.DateTimeField,
                               models.TextField,
                               models.BooleanField,
                               models.PositiveIntegerField,
                               models.PositiveSmallIntegerField,
                               models.IntegerField,
                               models.CommaSeparatedIntegerField]:
            # logger.debug("copying %s on %s" % (field, obj.__class__.__name__) )
            result.append(field.name)
        else:
            if field.__class__ not in [models.ForeignKey, models.AutoField, models.SlugField]:
                logger.debug("ignoring %s on %s" % (field, obj.__class__.__name__) )

    return result


def generateSlug(Model, name):
        slug = defaultfilters.slugify(name)[:45]
        c = 0
        while True:
            try:
                Model.objects.get(slug=slug)
                c += 1
                slug = "%s%d" % (defaultfilters.slugify( name )[:45], c)
            except Model.DoesNotExist:
                break  # finally found a slug that doesn't exist
        return slug


def convertClassicIteration(siteration, dproject):
    diteration = pmodels.Iteration(project=dproject)
    _copyFields(siteration, diteration, _primitiveFields(siteration))
    diteration.save()
    for spointslog in cmodels.PointsLog.objects.filter(object_id=siteration.id, content_type_id=36):
        # 36=iteration content type
        dpointslog = pmodels.PointsLog(iteration=diteration)
        _copyFields(spointslog, dpointslog, _primitiveFields(spointslog))
        dpointslog.save()

    return diteration


def convertClassicCommit(scommit, dstory):
    if pmodels.Commit.objects.filter(story=dstory, link=scommit.link).count() > 0:
        # A duplicate?
        return
    dcommit = pmodels.Commit(story=dstory)
    _copyFields(scommit, dcommit, _primitiveFields(scommit))
    dcommit.save()


def convertClassicTask(stask, dstory):
    dtask = pmodels.Task(story=dstory)
    _copyFields(stask, dtask, _primitiveFields(stask))
    dtask.assignee = stask.assignee
    dtask.save()


def convertClassicAttachment(sattachment, dstory):
    try:
        dattachment = atmodels.Attachment()
        _copyFields(sattachment, dattachment, _primitiveFields(sattachment))
        dattachment.story = dstory
        dattachment.creator = sattachment.creator
        f = ContentFile(sattachment.attachment_file.file.read())
        f.name = sattachment.filename
        dattachment.attachment_file = f
        dattachment.save()
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logger.warn("Could not copy attachment %s" % sattachment.attachment_file.name )


def convertClassicStory(sstory, iterationMap, epicMap, dproject, sproject, categoryLabelMap):
    logger.debug("Converting story %d" % sstory.id)
    dstory = pmodels.Story(project=dproject)
    dstory.iteration_id = iterationMap[sstory.iteration_id]
    dstory.creator = sstory.creator

    dstory.skip_announcements = True
    dstory.skip_haystack = True

    if sstory.epic is not None:
        dstory.epic_id = epicMap[sstory.epic_id]
    _copyFields(sstory, dstory, _primitiveFields(sstory))

    dstory.summary = _htmlify(dstory.summary, dproject)
    dstory.detail = _htmlify(dstory.detail, dproject)
    dstory.extra_1 = _htmlify(dstory.extra_1, dproject)
    dstory.extra_2 = _htmlify(dstory.extra_2, dproject)
    dstory.extra_3 = _htmlify(dstory.extra_3, dproject)

    # The classic projects could have had duplicate numbers, this makes sure that doesn't matter:
    try:
        pmodels.Story.objects.get(project=dproject, local_id=dstory.local_id)
        dstory.local_id = max(dproject.getNextId(), sproject.getNextId())
        logger.info('Duplicate number, set to %d' % dstory.local_id)
    except pmodels.Story.DoesNotExist:
        pass

    dstory.save()


    dstory.created = sstory.created
    dstory.save()

    if sstory.category is not None and sstory.category != '' and sstory.category in categoryLabelMap:
        dstory.labels.add(categoryLabelMap[sstory.category])

    try:
        if sproject.project_type == sproject.PROJECT_TYPE_KANBAN:
            statuses = list(sproject.statuses())
            cardTypeName = statuses[sstory.status-1]
            dstory.labels.add(categoryLabelMap[cardTypeName])
        else:
            dstory.labels.add(categoryLabelMap["User Story"])
    except:
        pass


    for assignee in sstory.assignee.all():
        dstory.assignee.add(assignee)
    for scommit in sstory.classic_commits.all():
        convertClassicCommit(scommit, dstory)
    for stask in sstory.classic_tasks.all():
        convertClassicTask(stask, dstory)
    for sattachment in cmodels.Attachment.objects.filter(object_id=sstory.id, content_type=37):
        convertClassicAttachment(sattachment, dstory)
    for smention in cmodels.StoryMentions.objects.filter(story=sstory):
        dmention = emodels.StoryMentions(story=dstory, user=smention.user, created=smention.created)
        dmention.save()
    for scomment in cmodels.Comment.objects.filter(object_id=sstory.id):
        dcomment = pmodels.StoryComment(story=dstory, comment=scomment.comment, user=scomment.user)
        dcomment.date_submitted = scomment.date_submitted
        dcomment.skip_announcements = True
        dcomment.save()


    dstory.tags = ",".join( [tagging.tag.name for tagging in cmodels.StoryTagging.objects.filter(story=sstory)] )
    dstory.save()

    return dstory


def convertClassicEpic(sepic, dproject, epicMap, parent=None):
    depic = pmodels.Epic(project=dproject, parent=parent)
    _copyFields(sepic, depic, _primitiveFields(sepic))
    depic.skip_haystack = True
    depic.save()
    epicMap[sepic.id] = depic.id
    for child in sepic.classic_children.all():
        convertClassicEpic(child, dproject, epicMap, depic)


def convertClassicTags(dproject, sproject):
    tags = []
    for tag in sproject.classic_tags.all():
        tags.append(tag.name)
    tags = set(tags)  # remove dupes
    for tag in tags:
        dtag = pmodels.StoryTag(name=tag, project=dproject)
        dtag.save()


def convertTimeEntry(sentry, dproject, iterationMap, storyMap):
    dentry = pmodels.TimeEntry(project=dproject)
    _copyFields(sentry, dentry, _primitiveFields(sentry))
    dentry.organization = sentry.organization
    dentry.user = sentry.user

    if sentry.iteration is not None and sentry.iteration_id in iterationMap:
        dentry.iteration_id = iterationMap[sentry.iteration_id]
    if sentry.story is not None and sentry.story_id in storyMap:
        dentry.story_id = storyMap[sentry.story_id]
    dentry.save()


def convertNewsEntry(snews, dproject, storyMap):
    try:
        if snews.user is None:
            return  # going to ignore the auto-generated github ones now
        dnews = amodels.NewsItem(project=dproject, user=snews.user)
        _copyFields(snews, dnews, ["created", "icon", "feed_url"])
        if snews.related_story is not None:
            dnews.related_story_id = storyMap[snews.related_story_id]

        text = snews.text.replace("\n", "")
        m = re.search("(modified|created) story(.*)(<ul>.*)", text)
        if m is None:
            dnews.text = text
        else:
            dnews.text = "%s story %s" % (m.group(1), m.group(3))
        dnews.save()
    except:
        logger.info("Could not convert news item")


def nextColor(colors):
    c = colors.pop(0)
    colors.append(c)
    return c


def convertScrumToKanban(sproject, dproject):
    try:
        boardConfig = json.loads(cmodels.BoardAttributes.objects.get(project=sproject, context='board', key='cfg').value)
    except cmodels.BoardAttributes.MultipleObjectsReturned:
        boardConfig = json.loads(cmodels.BoardAttributes.objects.filter(project=sproject, context='board', key='cfg')[0].value)
    except cmodels.BoardAttributes.DoesNotExist:
        # This is the default board the view code uses if no config is set:
        boardConfig = {'columns': [1,1,1,1,1,1,1,1,1,1], 'splitNames': ["Doing","Done"], 'rows':[{'type':1},{'type':3},{'type':3},{'type':3},{'type':3}] }

    kmanagers.autoConvertScrumProject(dproject, boardConfig)
    dproject.project_type = pmodels.Project.PROJECT_TYPE_KANBAN
    dproject.save()


def convertClassicWorkflows(sproject, dproject, cellMap):
    for sworkflow in sproject.classic_workflows.all():
        dworkflow = kmodels.Workflow(project=dproject)
        _copyPrimitiveFields(sworkflow, dworkflow)
        dworkflow.save()
        for sstep in sworkflow.classic_steps.all():
            dstep = kmodels.WorkflowStep(workflow=dworkflow)
            _copyPrimitiveFields(sstep, dstep)
            dstep.save()
            for scell in sstep.classic_cells.all():
                dstep.cells.add(cellMap[scell.id])


def convertClassicCells(sproject, dproject, storyMap):
    cellMap = {}
    for scell in sproject.classic_boardCells.all():
        dcell = kmodels.BoardCell(project=dproject)
        _copyPrimitiveFields(scell, dcell)
        kmanagers.setFullCellName(dproject, dcell)
        dcell.save()
        cellMap[scell.id] = dcell
        for sstory in scell.classic_stories.all():
            if sstory.id in storyMap:
                dstory = dproject.stories.get(id=storyMap[sstory.id])
                dstory.cell = dcell
                dstory.save()
            else:
                logger.warn("Could not find story %d to put into cell." % sstory.id)
    return cellMap


def convertClassicHeaders(sproject, dproject):
    headerMap = {}
    # todo: policy
    for sheader in sproject.classic_headers.all():
        dheader = kmodels.BoardHeader(project=dproject)
        _copyPrimitiveFields(sheader, dheader)
        dheader.save()
        headerMap[sheader.id] = dheader.id
    return headerMap


def convertClassicPolicies(sproject, dproject, cellMap, headerMap):
    for spolicy in sproject.classic_policies.all():
        dpolicy = kmodels.Policy(project=dproject)
        _copyPrimitiveFields(spolicy, dpolicy)
        dpolicy.save()
        for scell in spolicy.classic_cells.all():
            dpolicy.cells.add(cellMap[scell.id])
        for sheader in cmodels.BoardHeader.objects.filter(policy=spolicy):
            dheader = kmodels.BoardHeader.objects.get(id=headerMap[sheader.id])
            dheader.policy = dpolicy
            dheader.save()


def convertClassicCellMovements(sproject, dproject, cellMap, storyMap, iterationMap):
    for smovement in cmodels.CellMovement.objects.filter(cell_to__project=sproject):
        if smovement.story_id in storyMap:
            dmovement = kmodels.CellMovement()
            dmovement.cell_to = cellMap[smovement.cell_to_id]
            dmovement.user = smovement.user
            dmovement.story_id = storyMap[smovement.story_id]
            dmovement.related_iteration_id = iterationMap[smovement.related_iteration_id]

            story = pmodels.Story.objects.get(id=dmovement.story_id)

            kmanagers.setCellMovementStoryProperties(dmovement, story)
            dmovement.save()
            dmovement.created = smovement.created


            if story.epic_id:
                dmovement.epic_id = story.epic_id
            dmovement.label_ids = ",".join([str(label.id) for label in story.labels.all()])
            dmovement.assignee_ids = ",".join([str(assignee.id) for assignee in story.assignee.all()])
            if story.tags_cache is None:
                dmovement.tags = ''
            else:
                dmovement.tags = story.tags_cache[:256]
            dmovement.points_value = story.points_value()

            dmovement.save()



def convertClassicBacklogHistories(sproject, storyMap, iterationMap):
    for shistory in cmodels.BacklogHistorySnapshot.objects.filter(backlog__project=sproject):
        dhistory = kmodels.BacklogHistorySnapshot()
        dhistory.backlog_id = iterationMap[shistory.backlog_id]
        dhistory.save()
        dhistory.created = shistory.created
        dhistory.save()
        for sstory in shistory.classic_stories.all():
            if sstory.story_id in storyMap:
                dstory = kmodels.BacklogHistoryStories()
                dstory.snapshot = dhistory
                dstory.story_id = storyMap[sstory.story_id]
                dstory.save()


def convertKanbanTables(sproject, dproject, storyMap, iterationMap):
    headerMap = convertClassicHeaders(sproject, dproject)
    cellMap = convertClassicCells(sproject, dproject, storyMap)
    convertClassicWorkflows(sproject, dproject, cellMap)
    convertClassicPolicies(sproject, dproject, cellMap, headerMap)
    convertClassicCellMovements(sproject, dproject, cellMap, storyMap, iterationMap)
    convertClassicBacklogHistories(sproject, storyMap, iterationMap)

    for sstat in cmodels.KanbanStat.objects.filter(project=sproject):
        dstat = kmodels.KanbanStat(project=dproject)
        _copyPrimitiveFields(sstat, dstat)
        dstat.save()


def convertClassicProject(projectId, mode):
    labelColors = [0x3898DB, 0x34CC73, 0xBF392B, 0x9A59B5, 0xE57E24, 0x23BC9C, 0xF5764E, 0x1F1581,
                   0x448cca, 0x0D7D5B, 0xA60D05, 0x818B16, 0x8dc73e, 0xFFC54A, 0xff7f0e]
    sproject = cmodels.Project.objects.get(id=projectId)
    dproject = pmodels.Project(organization=sproject.organization)
    _copyFields(sproject, dproject, _primitiveFields(sproject))
    dproject.slug = generateSlug(pmodels.Project, sproject.name)
    dproject.creator = sproject.creator
    dproject.token = "".join(random.sample(string.lowercase + string.digits, 7))
    dproject.save()


    iterationMap = {}
    storyMap = {}
    epicMap = {}
    categoryLabelMap = {}

    convertClassicTags(dproject, sproject)

    if sproject.categories is not None:
        for category in sproject.categories.split(","):
            category = category.strip()
            if len(category) > 0:
                label = pmodels.Label(name=category, color=nextColor(labelColors), project=dproject)
                label.save()
                categoryLabelMap[category] = label


    if sproject.project_type == sproject.PROJECT_TYPE_KANBAN:
        for name in sproject.statuses():
            if name != '':
                label = pmodels.Label(name=name, color=nextColor(labelColors), project=dproject)
                label.save()
                categoryLabelMap[name] = label
    else:
        defaultLabels = ["User Story", "Feature", "Bug"]
        for labelName in defaultLabels:
            label = pmodels.Label(name=labelName, color=nextColor(labelColors), project=dproject)
            label.save()
            categoryLabelMap[labelName] = label

    for spointslog in cmodels.PointsLog.objects.filter(object_id=sproject.id, content_type_id=35):
        dpointslog = pmodels.PointsLog(project=dproject)
        _copyFields(spointslog, dpointslog, _primitiveFields(spointslog))
        dpointslog.save()

    for siteration in sproject.classic_iterations.all():
        diteration = convertClassicIteration(siteration, dproject)
        iterationMap[siteration.id] = diteration.id

    for sepic in sproject.classic_epics.filter(parent=None):
        convertClassicEpic(sepic, dproject, epicMap)

    for sstory in sproject.classic_stories.all():
        dstory = convertClassicStory(sstory, iterationMap, epicMap, dproject, sproject, categoryLabelMap)
        storyMap[sstory.id] = dstory.id

    for sentry in cmodels.TimeEntry.objects.filter(project=sproject):
        convertTimeEntry(sentry, dproject, iterationMap, storyMap)

    for snews in cmodels.NewsItem.objects.filter(project=sproject):
        convertNewsEntry(snews, dproject, storyMap)

    if sproject.project_type == pmodels.Project.PROJECT_TYPE_SCRUM:
        convertScrumToKanban(sproject, dproject)
    elif sproject.project_type == pmodels.Project.PROJECT_TYPE_KANBAN:
        convertKanbanTables(sproject, dproject, storyMap, iterationMap)

    for steam in cmodels.TeamProject.objects.filter(project=sproject):
        dproject.teams.add(steam.team)

    for story in dproject.stories.all():
        story.resetCounts()

    if mode == 'perm':
        sproject.active = False
        sproject.save()

    kmanagers.checkCellMovements(dproject.stories.all())

    return dproject








