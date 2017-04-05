import sys
import datetime
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings

from billing.generate_bill import generate_bill_for_customer
from billing.generate_bill_pdf import generate_bill_summary_xls
from billing.update_billing import read_excel_n_update_billing
from customer.models import Customer
from billing.product_billing_update import update_productbilling_for_month, update_productbilling
from billing.jasper_billing import generate_bill_for_jasper


class Command(BaseCommand):
    args = '<year> <month>'
    help = 'Generate bill for the given year and month'

    def handle(self, *args, **options):
        if len(args) == 0:
            bill_date = datetime.datetime.today()
            year = bill_date.year
            month = bill_date.month - 1
            if month == 0:
                year = year -1
                month = 12
            self.generate_bills(bill_date.year, bill_date.month)
        elif len(args) == 2:
            year = args[0]
            month = args[1]
            self.generate_bills(year, month)
        elif len(args) == 3:
            year = args[0]
            month = args[1]
            to_date = args[2]
            self.generate_bills(year, month, to_date=to_date)
        else:
            raise CommandError("Invalid arguments.  Please pass arguments in the following order.. <year> <month>")

    def generate_bills(self, year, month, to_date=None):
        # get all customers for generating bill
        customer_codes = list(Customer.objects.exclude(code__in=[92006, 32012]).values_list('code', flat=True))

        # start the bill generation process, this list may contain None,
        # so better to take precuation while generating bill
        bill_ccode = [generate_bill_for_customer(code, year, month, to_date=to_date) for code in customer_codes]
        bill_ccode_tuple = [x for x in bill_ccode if x[0]]

        bill_code_dict = defaultdict(int)
        for bill_id, code in bill_ccode_tuple:
            bill_code_dict[code] = int(bill_id)

        bill_id_list = tuple([x[0] for x in bill_ccode_tuple])

        if len(bill_id_list) == 0:
            print 'No Billing For this Month!'
            sys.exit(0)

        update_productbilling_for_month(year, month)
        # following 2 lines are for jasper.
        #fwd_bill_id, rev_bill_id = generate_bill_for_jasper(year, month)
        #bill_id_list = list(bill_id_list) + [fwd_bill_id, rev_bill_id ]
       
        # update Bill file that naresh provides
        read_excel_n_update_billing(year, month)

        # Below line will generate bill summary file.
        bill_summary_file = generate_bill_summary_xls(bill_id_list)
        self.send_summary_mail(bill_summary_file)

    def send_summary_mail(self, bill_summary_file):
        sb_url = bill_summary_file.split('ecomexpress')[1]
        file_path = settings.ROOT_URL + sb_url
        msg = 'Hi,\nThe bill summary has been generated. You can download it from the following link {0}'.format(file_path)
        send_mail('Bill Summary file Generated', msg, 'jignesh@prtouch.com',
                  ('jignesh@prtouch.com', 'jinesh@prtouch.com', 'jaideeps@ecomexpress.in', 'nareshb@ecomexpress.in'))
        print 'mail has send...'
