#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError
import logging

from apps.kanban.models import CellMovementLog
from apps.kanban.util import resetWorkflowReportData

logger = logging.getLogger(__name__)

# Deletes the cached cell data report files for all users with a CellMovementLog record.
class Command(BaseCommand):
    def handle(self, *args, **options):
        for log in CellMovementLog.objects.all():
            resetWorkflowReportData(log.project, log.workflow)
