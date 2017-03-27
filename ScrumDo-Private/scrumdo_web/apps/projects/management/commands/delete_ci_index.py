#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError
import logging
import os

from haystack import connections

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        index_name = "devqa" + os.environ.get('CIRCLE_BUILD_NUM', '0');
        logger.info("Attempting to delete index %s" % index_name)

        backend = connections.all()[0].get_backend()
        connection = backend.conn
        connection.indices.delete(index=index_name)
