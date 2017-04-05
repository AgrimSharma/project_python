import datetime
from decimal import Decimal

from billing.models import Billing
from customer.models import CustomerReportNames

TW = Decimal(10) ** -2


def generate_invoicetrfreport(year, month):
    bill_objs = Billing.objects.filter(billing_date__year=year,billing_date__month=month)
    report_list = []
    for count, bill in enumerate(bill_objs, start=1):
        indate = bill.billing_date
        indate = indate + datetime.timedelta(days=1)
        try:
            cu_obj = CustomerReportNames.objects.get(customer=bill.customer)
            customer_name = cu_obj.invoice_name
        except CustomerReportNames.DoesNotExist:
            customer_name = bill.customer.name

        row = (
            count, 
            '', 
            bill.id, 
            indate, 
            int(round(Decimal(bill.total_payable_charge).quantize(TW))), 
            customer_name
        )
        report_list.append(list(row))
    return report_list
