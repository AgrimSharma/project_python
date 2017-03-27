import rollbar
import sys
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


def catchlogexception(func):
    """
    :param func: Catches any exceptions, reports them to rollbar
    """
    def inner(*args, **kwargs):
        try:
            logger.info("Running task %s" % func.__name__)
            result = func(*args, **kwargs)
            logger.info("Task %s success" % func.__name__)
            return result
        except:
            logger.info("Exception in task %s" % func.__name__)
            rollbar.init(settings.ROLLBAR['access_token'], environment=settings.ROLLBAR['environment'])
            rollbar.report_exc_info(sys.exc_info(), None, {'task': func.__name__}, {'level': 'error'})
    return inner


def logdeprecated(func):
    """
    :param func: Logs to rollbar if the given function is called.  We'll use this to find views that are safe to remove.
    """
    def inner(*args, **kwargs):
        try:
            rollbar.init(settings.ROLLBAR['access_token'], environment=settings.ROLLBAR['environment'])
            rollbar.report_message("Deprececated method called: %s" % func.func_name, level='info', request=args[0])
        except:
            logger.warning("Failed to report deprecated function call")
        return func(*args, **kwargs)
    return inner



def logexception(func):
    """
    :param func: Catches any exceptions, reports them to rollbar, and then re-raises them.
    """
    def inner(*args, **kwargs):
        try:
            logger.info("Running task %s" % func.__name__)
            result = func(*args, **kwargs)
            logger.info("Task %s success" % func.__name__)
            return result
        except:
            logger.info("Exception in task %s" % func.__name__)
            rollbar.init(settings.ROLLBAR['access_token'], environment=settings.ROLLBAR['environment'])
            rollbar.report_exc_info(sys.exc_info(), None, {'task': func.__name__}, {'level': 'error'})
            raise
    return inner