import datetime
import xlrd
from django.conf import settings
from django.core.mail import send_mail

from billing.models import Billing


def update_billing_for_excel(*args, **kwargs):
    print 'updating billing..'
    bill_id = kwargs.get('bill_id')
    balance = kwargs.get('balance')
    payment = kwargs.get('payment')
    adjustments = kwargs.get('adjustments')
    adjust_cr= kwargs.get('adjust_cr')
    year = kwargs.get('year')
    month = kwargs.get('month')

    balance = 0 if not balance else balance
    payment = 0 if not payment else payment
    adjustments = 0 if not adjustments else adjustments
    adjust_cr = 0 if not adjust_cr else adjust_cr

    Billing.objects.filter(id=bill_id).update(balance=balance,
            received=payment, adjustment=adjustments, adjustment_cr=adjust_cr)
    return bill_id

def read_excel_file():
    try:
        with open(settings.BILL_FILE, 'r') as f:
            data = f.read()
    except IOError:
        return []
    book = xlrd.open_workbook(file_contents=data)
    work_sheet = book.sheet_by_index(0)

    # row values in excel file is assumed to be in the following order
    #    -Customer code 0
    #    -Customer Name 1
    #    -Opening Balance 2
    #    -Payment Received 3
    #    -Balance 4
    #    -Adjustments(Dr) 5
    #    -Adjustments(Cr) 6
    #    -Bill Date 7

    sheet_data = []
    for x in xrange(1, work_sheet.nrows):
        row_data = []
        for y in xrange(work_sheet.ncols):
            cell_value = work_sheet.cell_value(x, y)
            # if the data type is date then we have to convert it
            # to date format
            if y == 7 and cell_value:
                date_time = datetime.datetime(*xlrd.xldate_as_tuple(cell_value, book.datemode))
                cell_value = datetime.datetime.strftime(date_time, '%Y-%m-%d')
            row_data.append(cell_value)
        sheet_data.append(row_data)

    return sheet_data[:-1]

def read_excel_n_update_billing(year, month):
    sheet_data = read_excel_file() # keep each row data from excel sheet
    bill_ccode_dict = dict(Billing.objects.filter(billing_date__year=year, billing_date__month=month).values_list('customer__code', 'id'))
    for row in sheet_data:
        bill_id = bill_ccode_dict.get(str(int(row[0])))
        if not bill_id:
            print '---'
            continue
        else:
            print 'updating bill ', bill_id
        update_billing_for_excel(bill_id=bill_id, balance=row[2], payment=row[3],
                adjustments=row[5], adjust_cr=row[6], year=year, month=month)
    return True
