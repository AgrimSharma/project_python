from django.conf import settings
from apps.scrumdocelery import app
from apps.extras.util import processQueueItem
from apps.extras.models import SyncronizationQueue, ProjectExtraMapping

from django.db.models.signals import post_save
from django.dispatch import receiver
import traceback
import sys
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(name='apps.extras.tasks.processExtrasQueue')
def processExtrasQueue(dbid):
    """Processes a single extras queue item"""
    try:
        queue = SyncronizationQueue.objects.get(id=dbid)
        queue.delete()
        processQueueItem(queue, rethrow_exceptions=True)
    except SyncronizationQueue.DoesNotExist:
        pass # the cronjob already got it.
    except:
        e = sys.exc_info()[1]        
        stack = "\n".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        logger.error(stack)


@receiver(post_save, sender=SyncronizationQueue, dispatch_uid="extras_queue_tasks")
def setupQueue(sender, **kwargs):
    obj = kwargs['instance']
    processExtrasQueue.apply_async((obj.id,), countdown=5)


@app.task
def process_queue():
    """Processes any leftover queue items"""
    queue = SyncronizationQueue.objects.all()
    for queueItem in queue:
        # In case a second invocation of this script occurs while it's running, we don't want
        # to re-process any items...
        queueItem.delete()

    for queueItem in queue:
        processQueueItem(queueItem)


@app.task
def setup_pull_queue( **kwargs ):
    logger.info("Setting up queue to pull all projects next time.")
    project_slug = kwargs.get("project_slug",None)
    mappings = ProjectExtraMapping.objects.all()
    for mapping in mappings:
        if project_slug==None or project_slug==mapping.project.slug:
            qItem = SyncronizationQueue(project=mapping.project, extra_slug=mapping.extra_slug, action=SyncronizationQueue.ACTION_SYNC_REMOTE)
            qItem.save()
