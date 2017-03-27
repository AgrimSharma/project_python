from django.core.management.base import BaseCommand
from apps.activities.models import NewsItem
from rollbardecorator import logexception


class Command(BaseCommand):
    help = 'Purge old Activities'

    @logexception
    def handle(self, *app_labels, **options):
        self.purge(*app_labels, **options)

    def purge(self, *app_labels, **options):
        print 'Purging Activities'
        NewsItem.purgeOld(365*2)
