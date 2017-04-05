import os
from collections import defaultdict
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from billing.models import Billing
from billing.thread_bill_pdf import start_bill_thread_billpdf,\
        start_bill_thread_awbexcel, start_bill_thread_awbpdf, start_bill_thread


class Command(BaseCommand):
    args = '<year> <month>'
    help = 'Generate pdf reports for all billings for the given year and month'

    def handle(self, *args, **options):
        if len(args) == 2:
            self.start_pdf_generation(int(args[0]), int(args[1]))
        elif len(args) == 0:
            bill_date = datetime.datetime.today()
            month = bill_date.month - 1
            year = bill_date.year
            if month == 0:
                month = 12
                year =- 1
            self.start_pdf_generation(year, month)
        else:
            raise CommandError("Usage: python manage.py generate_bill_pdfs <year> <month>")

    def start_pdf_generation(self, year, month):
        bills_list = Billing.objects.filter(billing_date__year=year, billing_date__month=month)\
                .exclude(customer__id=6).values_list('id', flat=True)
        bills_list = list(reversed([x for x in bills_list]))
        print bills_list
        start_bill_thread_billpdf(bills_list)
        start_bill_thread_awbexcel(bills_list)
        start_bill_thread_awbpdf(bills_list)
        print 'reports generation finished...'
