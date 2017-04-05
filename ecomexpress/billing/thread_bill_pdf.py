import os
import sys

import Queue
import threading
import time

from billing.models import CustomerBillingReport, Billing, BillingQueue
from billing.generate_bill_pdf import generate_bill_pdf
from billing.generate_bill_reports import generate_awbpdf_report, generate_awbexcel_report
from billing.jasper_update_new import generate_report

queuebillpdf = Queue.Queue()
queueawbexcel = Queue.Queue()
queueawbpdf = Queue.Queue()
root_url = 'http://billing.prtouch.com/'

class BillingThreadBillPdf(threading.Thread):
    """Threaded billing pdf generation"""
    def __init__(self, billqueue):
        threading.Thread.__init__(self)
        self.billqueue = billqueue

    def run(self):
        while queuebillpdf.qsize() > 0:
            #grabs host from queue
            bill_id = queuebillpdf.get()
            billing = Billing.objects.get(id=bill_id)

            # generate reports for given bill_id
            bill_pdf = generate_bill_pdf(bill_id) # this function will generate report for the given bill id
            billh_pdf = generate_bill_pdf(bill_id, False)

            bill_url = root_url + bill_pdf.split('ecomexpress')[1]
            billh_url = root_url + billh_pdf.split('ecomexpress')[1]
            CustomerBillingReport.objects.filter(
                billqueue=self.billqueue, customer=billing.customer, billing=billing
            ).update(
                invoice_report=bill_url, headless_invoice_report=billh_url)

            #signals to queue job is done
            queuebillpdf.task_done()


class BillingThreadAwbExcel(threading.Thread):
    """Threaded billing pdf generation"""
    def __init__(self, billqueue):
        threading.Thread.__init__(self)
        self.billqueue = billqueue

    def run(self):
        while queueawbexcel.qsize() > 0:
            #grabs host from queue
            bill_id = queueawbexcel.get()
            billing = Billing.objects.get(id=bill_id)

            # generate reports for given bill_id
            if billing.customer.id == 6:
                awb_excel = generate_report(billing.billing_date_from.strftime('%Y-%m-%d'), billing.billing_date.strftime('%Y-%m-%d'))
            else:
                awb_excel = generate_awbexcel_report(bill_id) # creating excel for individual bill id

            awbexcel_url = root_url + awb_excel.split('ecomexpress')[1]

            CustomerBillingReport.objects.filter(
                billqueue=self.billqueue, customer=billing.customer, billing=billing
            ).update(awb_excel_report=awbexcel_url)
                
            #send email to ecom team
            if queueawbexcel.empty():
                exit(0)

class BillingThreadAwbPdf(threading.Thread):
    """Threaded billing pdf generation"""
    def __init__(self, billqueue):
        threading.Thread.__init__(self)
        self.billqueue = billqueue

    def run(self):
        while queueawbpdf.qsize() > 0:
            #grabs host from queue
            bill_id = queueawbpdf.get()
            billing = Billing.objects.get(id=bill_id)

            if billing.customer.id == 6:
                queueawbpdf.task_done()
                return True

            # generate reports for given bill_id
            awb_pdf = generate_awbpdf_report(bill_id) # creating pdf for individual bill id
            awbpdf_url = root_url + awb_pdf.split('ecomexpress')[1]

            billing = Billing.objects.get(id=bill_id)
            CustomerBillingReport.objects.filter(
                billqueue=self.billqueue, customer=billing.customer, billing=billing
            ).update(awb_pdf_report=awbpdf_url)

            #signals to queue job is done
            queueawbpdf.task_done()


def start_bill_thread(bill_ids, billqueue=None):
    #populate queue with data
    for bill_id in bill_ids:
        queuebillpdf.put(bill_id)
        queueawbexcel.put(bill_id)
        queueawbpdf.put(bill_id)

    #spawn a pool of threads, and pass them queue instance
    for i in range(3):
        t = BillingThreadBillPdf(billqueue=billqueue)
        t1 = BillingThreadAwbExcel(billqueue=billqueue)
        t2 = BillingThreadAwbPdf(billqueue=billqueue)
        t.setDaemon(True)
        t1.setDaemon(True)
        t2.setDaemon(True)
        t.start()
        t1.start()
        t2.start()

    queuebillpdf.join()
    queueawbexcel.join()
    queueawbpdf.join()

def start_bill_thread_billpdf(bill_ids, billqueue=None):
    #populate queue with data
    for bill_id in bill_ids:
        queuebillpdf.put(bill_id)

    #spawn a pool of threads, and pass them queue instance
    threads = []
    for i in range(3):
        t = BillingThreadBillPdf(billqueue=billqueue)
        threads.append(t)
        t.setDaemon(True)
        t.start()

    #queuebillpdf.join()
    for t in threads:
        t.join()

def start_bill_thread_awbexcel(bill_ids, billqueue=None):
    #populate queue with data
    for bill_id in bill_ids:
        queueawbexcel.put(bill_id)

    #spawn a pool of threads, and pass them queue instance
    threads = []
    for i in range(3):
        t = BillingThreadAwbExcel(billqueue=billqueue)
        threads.append(t)
        t.setDaemon(True)
        t.start()

    #queueawbexcel.join()
    for t in threads:
        t.join()

def start_bill_thread_awbpdf(bill_ids, billqueue=None):
    #populate queue with data
    for bill_id in bill_ids:
        queueawbpdf.put(bill_id)

    #spawn a pool of threads, and pass them queue instance
    threads = []
    for i in range(3):
        t = BillingThreadAwbPdf(billqueue=billqueue)
        threads.append(t)
        t.setDaemon(True)
        t.start()

    #queueawbpdf.join()
    for t in threads:
        t.join()
