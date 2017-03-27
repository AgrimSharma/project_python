from ..models import StepMovement, WorkflowStep
from apps.projects.models import Story
from ..util import getMovements
import datetime
import math
import logging

logger = logging.getLogger(__name__)

def calculateMovements(project, workflow, storyId):
    story = Story.objects.get(id=storyId)
    movements = StepMovement.objects.filter(workflow=workflow, story_id=storyId ).order_by("created")
    return {"story":story,"movements":movements}

   