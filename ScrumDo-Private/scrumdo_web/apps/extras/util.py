import sys
from datetime import date, timedelta

from apps.projects.models import Project, Iteration, Story, PointsLog
from apps.extras.models import SyncronizationQueue
from apps.extras.manager import manager
from apps.activities.models import NewsItem

import logging
import sys, traceback
import getopt
import urllib2

from django.core.management.base import BaseCommand, CommandError


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def processQueueItem(queueItem, rethrow_exceptions=False):
    try:
        project = queueItem.project
        if not project.active:
            return

        logger.info("== Synchronizing %s / %s / %d" % (project.slug, queueItem.extra_slug, queueItem.action) )
        story = queueItem.story
        task = queueItem.task
        action = queueItem.action
        extra_slug = queueItem.extra_slug        
        external_id = queueItem.external_id

        extra = manager.getExtra(extra_slug)
        
        if not project.active:
            logger.info("Skipping %s because it's inactive" % (project.slug) )
            return            
        
        if not project.organization:
            logger.info("Skipping %s because it's not in an org" % (project.slug) )
            return
        
        if extra.isPremium() and not project.organization.subscription.planPremiumExtras():
            logger.info("Skipping %s/%s due to subscription stats" % (project.slug, extra_slug))
            return

        if action == SyncronizationQueue.ACTION_SYNC_REMOTE:
            extra.pullProject(project)
        elif action == SyncronizationQueue.ACTION_STORY_UPDATED:
            extra.storyUpdated(project,story)
        elif action == SyncronizationQueue.ACTION_STORY_DELETED:
            extra.storyDeleted(project,external_id)
        elif action == SyncronizationQueue.ACTION_STORY_CREATED:
            extra.storyCreated(project,story)
        elif action == SyncronizationQueue.ACTION_STORY_STATUS_CHANGED:
            extra.storyStatusChange(project, story)
        elif action == SyncronizationQueue.ACTION_INITIAL_SYNC:
            extra.initialSync( project )
        elif action == SyncronizationQueue.ACTION_TASK_UPDATED:
            extra.taskUpdated(project, task)
        elif action == SyncronizationQueue.ACTION_TASK_DELETED:
            extra.taskDeleted(project, external_id)
        elif action == SyncronizationQueue.ACTION_TASK_CREATED:
            extra.taskCreated(project, task)
        elif action == SyncronizationQueue.ACTION_TASK_STATUS_CHANGED:
            extra.taskStatusChange(project, task)
        elif action == SyncronizationQueue.ACTION_STORY_IMPORTED:
            extra.storyImported(project, story)
        elif action == SyncronizationQueue.ACTION_NEWS_POSTED:
            news = NewsItem.objects.get(id=external_id)
            extra.newsItemPosted(project,news)

        logger.info("Success.")
    except NewsItem.DoesNotExist:
        pass
    except RuntimeError:
        logger.error("RuntimeError occured while processing a syncronization queue item.")
        traceback.print_exc(file=sys.stdout)
        if rethrow_exceptions:
            raise
    except urllib2.HTTPError as e:
        logger.error("HTTP Error %d occured while processing a syncronization queue item." % e.code)
        logger.error(e.headers)
        logger.error(e.read())
        traceback.print_exc(file=sys.stdout)
        if rethrow_exceptions:
            raise
    except:
        logger.error("Error occured while processing a syncronization queue item.")
        traceback.print_exc(file=sys.stdout)
        if rethrow_exceptions:
            raise
        