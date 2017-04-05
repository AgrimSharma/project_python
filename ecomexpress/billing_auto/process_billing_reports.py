from customer.models import Customer
from billing.models import BillingReportQueue, CustomerBillingReport

from billing.generate_bill_pdf import generate_bill_pdf, generate_bill_summary_xls
from billing.generate_bill_reports import generate_awbpdf_report, generate_awbexcel_report

from billing.thread_bill_pdf import start_bill_thread_billpdf,\
        start_bill_thread_awbexcel, start_bill_thread_awbpdf, start_bill_thread


def process_queue(queue_id, *args, **kwargs):
    try:
        queue = BillingReportQueue.objects.get(id=queue_id)
    except BillingReportQueue.DoesNotExist:
        return None

    bills_list = queue.billqueue.bills.values_list('id', flat=True)

    if queue.summary:
        generate_bill_summary_xls(bills_list)

    if queue.msr:
        pass

    if queue.invoice_report:
        start_bill_thread_billpdf(bills_list, billqueue=queue) 
    if queue.ebs_invoice_report:
        pass
    if queue.awb_pdf_report:
        start_bill_thread_awbpdf(bills_list, billqueue=queue)
    if queue.awb_excel_report:
        start_bill_thread_awbexcel(bills_list, billqueue=queue) 

    return True


def process_report_queue():
    queue = BillingReportQueue.objects.filter(status=0) 
    for q in queue:
        BillingReportQueue.objects.filter(id=q.id).update(status=1)
        done = process_queue(q.id)
        if done:
            BillingReportQueue.objects.filter(id=q.id).update(status=2)
    return True
