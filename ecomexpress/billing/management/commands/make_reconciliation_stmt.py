#import os
#import sys

#os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
#sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from django.core.management.base import BaseCommand, CommandError
from billing.reconciliation import generate_reconciliation_excel

class Command(BaseCommand):
    args = '<from_date to_date customer_id>'
    help = 'Generate reconciliation statement'

    def handle(self, *args, **options):
        try:
            date_from = args[0]
            date_to = args[1]
            cust_id = argv[2]
            file_name = generate_reconciliation_excel(date_from, date_to, cust_id)
            self.stdout.write('Reconciliation report successfully generated - "%s"' % file_name)
        except IndexError:
            raise CommandError("Please give arguments in the following order.. <date_from> <date_to> <customer_id>")
