from django.db.models.signals import post_save
from django.contrib.auth.models import User

import logging

from .boardattributes import BoardAttributes
from .commit import Commit
from .epic import Epic
from .extrauserinfo import ExtraUserInfo
from .filejob import FileJob
from .offlinejob import OfflineJob
from .iteration import Iteration, IterationSentiment
from .pointslog import PointsLog
from .project import Project
from .release import Release
from .releaselog import ReleaseLog
from .savedquery import SavedQuery
from .sitestats import SiteStats
from .story import Story
from .storyattributes import StoryAttributes
from .storytag import StoryTag
from .storytagging import StoryTagging
from .task import Task
from .tasktagging import TaskTagging
from .timeallocation import TimeAllocation
from .timeentry import TimeEntry
from .labels import Label
from .projectshare import ProjectShare
from .comment import StoryComment, NoteComment
from .releasestat import ReleaseStat
from .milestoneassignment import MilestoneAssignment
from .pullrequest import PullRequest
from .storyblocker import StoryBlocker
from .note import Note
from .pointscale import PointScale
from .portfolio import Portfolio, PortfolioLevel
from .programincrement import ProgramIncrement, ProgramIncrementSchedule
from .wiplimit import TeamIterationWIPLimit
from .risks import Risk

STATUS_TODO = 1
STATUS_DOING = 4
STATUS_REVIEWING = 7
STATUS_DONE = 10

logger = logging.getLogger(__name__)


def set_full_name(sender, instance, signal, *args, **kwargs):
    try:
        fn = ExtraUserInfo.objects.filter(user=instance)
        name = "%s %s" % (instance.first_name, instance.last_name)
        name = name.strip()
        changed = False
        if len(fn) > 0:
            fn = fn[0]
            if fn.full_name != name:
                fn.full_name = name
                changed = True
                fn.save()
        elif name != "":
            fn = ExtraUserInfo(user=instance,full_name = name )
            changed = True
            fn.save()
    except:
        logger.error("Could not set user's name")

    if changed:
        try:
            for story in Story.objects.filter(assignee=instance):
                story.resetAssigneeCache()
                story.save()
        except:
            pass


post_save.connect(set_full_name, dispatch_uid="projects_models_signal", sender=User)





