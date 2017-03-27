from apps.attachments.models import Attachment
from models import TimeAllocation, Project, Story, Iteration
from apps.organizations.models import Organization
from apps.kanban.models import BoardCell

from django.template import defaultfilters
from django.conf import settings
from django.core.files.base import ContentFile


import logging
import base64
import random
import string
import rollbar
import sys
import re

logger = logging.getLogger(__name__)


def extractInlineImagesForStory(story):
    try:
        story.summary, m1 = extractInlineImages(story.summary, story)
        story.detail, m2 = extractInlineImages(story.detail, story)
        story.extra_1, m3 = extractInlineImages(story.extra_1, story)
        story.extra_2, m4 = extractInlineImages(story.extra_2, story)
        story.extra_3, m5 = extractInlineImages(story.extra_3, story)
        return m1 or m2 or m3 or m4 or m5
    except:
        rollbar.init(settings.ROLLBAR['access_token'], environment=settings.ROLLBAR['environment'])
        rollbar.report_exc_info(sys.exc_info(), None, {'task': 'extractInlineImages'}, {'level': 'error'})
        return False


IMG_RE = re.compile(u"<img [^>]*src=['\"]data:image/([a-z]+);base64,([^\"]+)['\"]", flags=re.MULTILINE)

# <img style="width: 50%;" src="data:image/png;base64

def stripInlineImages(text):
    if text is None:
        return text
    match = IMG_RE.search(text)
    while match is not None:
        imgtype, data = match.group(1, 2)
        if len(data) > 512:
            repl = u"data:image/{imgtype};base64,{data}".format(imgtype=imgtype, data=data)
            text = text.replace(repl, '')
        match = IMG_RE.search(text)
    return text


def extractInlineImages(text, story):
    """Extracts any base64 encoded inline images in text, creates an attachment for it, and replaces it with a normal
       img href tag."""
    if text is None:
        return text, False
    modified = False
    match = IMG_RE.search(text)
    c = random.randint(0, 100000)
    while match is not None:
        imgtype, data = match.group(1, 2)
        if len(data) > 512:
            c += 1
            filename = u"inlineimage{rand}.{imgtype}".format(imgtype=imgtype, rand=c)
            file = ContentFile(base64.decodestring(data))
            attachment = Attachment(story=story, creator=story.creator)
            attachment.attachment_file.save(filename, file)
            attachment.save()

            newLink = u"{base}/attachment/{id}".format(base=settings.BASE_URL, id=attachment.id)
            logger.info(newLink)
            repl = u"data:image/{imgtype};base64,{data}".format(imgtype=imgtype, data=data)
            text = text.replace(repl, newLink)
            modified = True
        match = IMG_RE.search(text)

    return text, modified


def generateProjectSlug(project_name):
    slug = defaultfilters.slugify(project_name)[:45]
    c = 0
    while True:
        try:
            Project.objects.get(slug=slug)
            c += 1
            slug = "%s%d" % (defaultfilters.slugify(project_name)[:45], c)
        except Project.DoesNotExist:
            break  # finally found a slug that doesn't exist
    return slug


def getStoryStatus(story, project):
    """
    Status is going away.  But for now, we can calculate an equivalent status for a story
    using it's iteration or cell that it's inside of.

    This method will conditionally do that based on the project type.

    One potential discrepency:
      Stuff in the backlog that is not in TODO status will come out with different
      statuses on a kanban or scrum project.
    """
    if project.project_type == Project.PROJECT_TYPE_SCRUM:
        return story.status
    s = getStatus(story)
    return s


def getStatus(story):
    """
    Status is going away.  But for now, we can calculate an equivalent status for a story
    using it's iteration or cell that it's inside of.

    We also might have a mapped_status in a workflow step from an imported project.

    THIS METHOD IS INEFFICIENT, DO NOT USE IT IN VIEW CODE.
    """
    # First, if we're in archive or backlog, we know our status...
    iteration = story.iteration
    if iteration.iteration_type == Iteration.ITERATION_ARCHIVE:
        return Story.STATUS_DONE
    if iteration.iteration_type == Iteration.ITERATION_BACKLOG:
        return Story.STATUS_TODO

    cell = story.cell
    if cell is None:
        return Story.STATUS_TODO  # Default status?


    # If the cell the story is in has a default workflow, and it has a mapped_status,
    # then this workflow represents an imported one from a scrum project that had an
    # actual status associated with it.
    defaultSteps = cell.steps.filter(workflow__default=True).exclude(mapped_status=-1)
    for step in defaultSteps:
        return step.mapped_status

    # At this point, we have a story sitting in a cell in a current iteration.  We'll infer the
    # status from the cell's time type
    if cell.time_type == BoardCell.DONE_TIME:
        return Story.STATUS_DONE

    if cell.time_type == BoardCell.WORK_TIME:
        return Story.STATUS_DOING

    return Story.STATUS_TODO





def get_completed_stories(project, iteration):
    """
    For a given project/iteration, returns all the completed stories.
    (status=Done for scrum, cell time_type=done for kanban)
    """
    if project.project_type == Project.PROJECT_TYPE_SCRUM:
        return iteration.stories.filter(status=Story.STATUS_DONE)
    return iteration.stories.filter(cell__time_type=BoardCell.DONE_TIME)


def reduce_burndown_data( data ):
    """Takes a list of datapoints for a burnup chart and if there are more than 30, removes any redundant points.
       Redundant is when a point's two neighbors are equal to itself so it would just be a marker on a straight line.
       (I guess points along a straight sloped line could be considered redundant, but we don't remove those)
       The middle 15 is considered redundant here: [5,6,10,10,15,15,15,20]
       The middle 4 threes are considered redundant here: [1,2,3,3,3,3,3,3,5]
    """
    if len(data) < 30:
        return data

    subset = data[1:-1] # Subset of data that never includes first/last
    remove = []
    for idx,item in enumerate( subset ):
                # idx = index before this item in data
                # idx+1 = this item in data
                # idx+2 = next item in data
        last_val = data[ idx ][1]
        next_val = data[ idx+2 ][1]

        if item[1]==last_val and item[1]==next_val:
            # don't need this item!
            remove.append(idx+1)
            # logger.debug("Can remove %d" % (idx+1))

    remove.reverse()
    for remove_index in remove:
        del data[remove_index:(remove_index+1)]
    return data


def organizationOrNone(project):
    try:
        organization = project.organization
    except Organization.DoesNotExist:
        organization = None
    return organization
    
    
def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix
        

def getAllocationsForIteration(project, iteration):
    allocations = []    
    members = project.all_members()
    members = sorted(members, key=lambda member:member.username.lower())
    for member in members:
      try:
          allocation = TimeAllocation.objects.get(iteration=iteration, user=member)
      except TimeAllocation.DoesNotExist:
          try:
              allocation = TimeAllocation.objects.get(project=project, user=member, iteration=None)
          except TimeAllocation.DoesNotExist:
              allocation = TimeAllocation(iteration=iteration, user=member)
      allocations.append(allocation) 
    return allocations
    
    
def returnUniqueList(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def generateDeletedPrefix():
    return ''.join(random.choice(string.printable) for _ in range(2))

def generateDeletedProjectPrefix(project):
    prefix = generateDeletedPrefix()
    while True:
        try:
            Project.objects.get(prefix=prefix, organization=project.organization)
            prefix = generateDeletedPrefix()
        except Project.DoesNotExist:
            break
    return prefix


def generateProjectPrefix(project, random=None):
    if random is not None:
        c = 15
    else:
        c = 0
    prefix = _get_prefix(project, c)
    while True:
        try:
            Project.objects.get(prefix=prefix, organization = project.organization)
            c += 1
            prefix = _get_prefix(project, c)
        except Project.DoesNotExist:
            break
    return prefix.upper()

def _get_prefix(project, counter=0):
    prefix = ""
    if counter < 2:
        prefix = _get_prefix_char(project, counter)
        return prefix
    elif counter < 12:
        r = random.randint(1, 9)
        p = _get_prefix_char(project, 1)
        prefix = "%s%s" % (p[0], r)
        return prefix
    else:
        prefix = prefix_generator()
        return prefix

def _get_prefix_char(project, counter=0):
    name = re.sub('[^0-9a-zA-Z\s]+', '', project.name)
    names = name.split()
    prefix = ""
    if len(names) > 1:
        if len(names[1]) > 1:
            prefix  = "%s%s" % (names[0][0], names[1][counter])
        else:
            prefix  = "%s%s" % (names[0][0], names[1][0])
    elif len(names) == 1:
        if len(names[0]) > 1:
            prefix = "%s%s" % (names[0][0], names[0][1])
        else:
            prefix = "%s%s" % (names[0][0], names[0][0])
    else:
        prefix = prefix_generator()
    return prefix

def prefix_generator(size=2, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def duplicatePrefix(project, organization):
    return Project.objects.filter(prefix=project.prefix, organization = organization).exclude(id=project.id).count()