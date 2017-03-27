#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError
import logging
import os

from haystack import connections

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        backend = connections.all()[0].get_backend()
        connection = backend.conn

        for i in range(1,15):
            index_name = "logstash-2016.07.%02d" % i
            logger.info("Attempting to delete index %s" % index_name)
            connection.indices.delete(index=index_name)
