import datetime
import calendar
import Queue
import threading

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from customer.models import Customer
from reports.report_api import ReportGenerator
from reports.customer_emails import customer_emails_dict
from reports.ecomm_mail import ecomm_send_mail
from service_centre.models import Shipment, get_internal_shipment_status
from track_me.models import RTOInstructionUpdate
customer_code_queue = Queue.Queue()


def get_date_range():
    month = datetime.date.today().month
    year = datetime.date.today().year
    day = datetime.date.today().day
    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if prev_month == 12 else year
    if day <= 20:
        start_date = datetime.date(prev_year, prev_month, 1)
    else:
        start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, day)

    return (start_date, end_date)

def split_date(start_date, end_date):
    date_sum = start_date.toordinal() + end_date.toordinal()
    mid = date_sum // 2
    mid_date = datetime.datetime.fromordinal(mid).date()
    return (
        (start_date, mid_date),
        (mid_date + datetime.timedelta(days=1), end_date)
    )

def customer_report_inrange(code, date_range):
    start_date, end_date = date_range
    hour = datetime.datetime.now().strftime('%H')
    file_name = 'MIS_REPORT_{0}_{1}_{2}.xlsx'.format(str(code), str(end_date), str(hour))
    report = ReportGenerator(file_name, border=True)

    col_heads = (
        'Air Waybill No', 'Order No', 'Product Type', 'Weight', 'Vol Weight', # 4
        'COD Amount', 'Declared Value', 'Origin', 'Destination', 'Vendor', # 9
        'Shipper', 'Consignee', 'Consignee Address', 'Contact Number', # 13
        'P/U Date', 'Expected DOD', 'Status', 'Remarks', 'Reason',
        'Received by', 'Last Updated Date', 'New Air Waybill (RTS)',
        'Return Status', 'Ref_awb Updated', 'First outscan', 'Last Outscan')
    report.write_header(col_heads)

    report_matrix = []
    while start_date <= end_date:
        date_str = start_date.strftime('%Y-%m-%d')
        start_date += datetime.timedelta(days=1)
        raw_data = list(Shipment.objects.using('local_ecomm')\
            .filter(shipper__code=code, added_on__range=(date_str+' 00:00:00', date_str+' 23:59:59'))\
            .exclude(rts_status=1).exclude(reverse_pickup=True).exclude(reason_code__code__in=[111, 333])\
            .values_list('airwaybill_number',  #0
                    'order_number', #1
                    'product_type', #2
                    'actual_weight', #3
                    'volumetric_weight', #4
                    'collectable_value', #5
                    'declared_value', #6
                    'pickup__service_centre__center_name', #7
                    'original_dest__center_name', #8
                    'shipper__name', #9
                    'pickup__customer_code__name', #10
                    'consignee', #11
                    'consignee_address1', #12
                    'consignee_address2', #13
                    'consignee_address3', #14
                    'consignee_address4', #15
                    'mobile', #16
                    'added_on', #17
                    'status', #18
                    'reason_code__code', #19
                    'reason_code__code_description', #20
                    'updated_on', #21
                    'ref_airwaybill_number', #22
                    'rts_status', #23
                    'return_shipment', #24
                    'rto_status',#25
                    'expected_dod')) #26

        for row in raw_data:
            airwaybill_number = row[0]
            orderno = row[1]
            product_type = row[2]
            actual_weight = row[3]
            vol_weight = row[4]
            cod_amount = row[5]
            declared_value = row[6]
            origin = row[7]
            destination = row[8]
            vendor = row[9]
            shipper = row[10]
            consignee = row[11]
            consignee_address = ''
            consignee_address1 = row[12]
            consignee_address2 = row[13]
            consignee_address3 = row[14]
            consignee_address4 = row[15]
            contact_number = row[16]
            pu_date = row[17]
            status = row[18]
            mis_status = ''
            remarks = ''
            reason = ''
            reason_code = int(row[19]) if row[19] else 0
            reason_code_description = row[20]
            recieved_by = ''
            updated_date = row[21]
            ref_airwaybill_number = row[22]
            rts_status = row[23]
            return_status = ''
            return_shipment = row[24]
            rto_status = row[25]
            expected_dod = row[26]
            ref_updated_on = ''

            # get address
            try:
                consignee_address1 = consignee_address1 if consignee_address1 else ''
                consignee_address2 = consignee_address2 if consignee_address2 else ''
                consignee_address3 = consignee_address3 if consignee_address3 else ''
                consignee_address4 = consignee_address4 if consignee_address4 else ''
                consignee_address = str(consignee_address1) + str(consignee_address2) + str(consignee_address3) + str(consignee_address4)
            except UnicodeError:
                consignee_address = ''

            # get reason, remarks and recieved_by
            su_id, reason, remarks, recieved_by = Shipment.objects.using('local_ecomm').filter(airwaybill_number=airwaybill_number)\
                    .values_list('statusupdate__id', 'statusupdate__reason_code__code_description',
                            'statusupdate__remarks', 'statusupdate__recieved_by').latest('statusupdate__id')

            status = int(status)
            if status == 9:
                mis_status = 'Delivered / Closed'
            elif reason_code and reason_code in [206, 777]:
                mis_status = 'Returned'
            elif reason_code and reason_code == 310:
                mis_status = 'Returned to Vendor'
            elif reason_code and reason_code == [311, 302, 333]:
                mis_status = reason_code_description
            elif RTOInstructionUpdate.objects.filter(shipment__airwaybill_number=airwaybill_number).only('id').exists():
                mis_status = 'RTO Instruction Received'
            elif rts_status in [1, 2] or rto_status == 1 or return_shipment == 3:
                mis_status = 'Returned'
            elif status in [0, 1, 2, 3, 4, 5]:
                mis_status = 'Intransit'
            else:
                mis_status = get_internal_shipment_status(status)
            if not mis_status:
                mis_status = ''

            if mis_status.lower() in ['delivered', 'outscan','delivered / closed']:
                remarks, reason = '', ''
            elif mis_status.lower() == 'undelivered':
                recieved_by = ''
            # update ref airwaybill number details if it is present
            if ref_airwaybill_number and status != 9:
                try:
                    ref_updated_on = Shipment.objects.using('local_ecomm').get(airwaybill_number=ref_airwaybill_number).updated_on
                    if ref_updated_on:
                        ref_updated_on = ref_updated_on.date()
                    ref_status = Shipment.objects.using('local_ecomm').get(airwaybill_number=ref_airwaybill_number).status
                    if ref_status in [1, 2, 3, 4, 5]:
                        if int(airwaybill_number) == int(ref_airwaybill_number):
                            return_status = 'RTO In transit'
                        else:
                            return_status = 'Return In transit'
                    else:
                        return_status = get_internal_shipment_status(ref_status)
                except Shipment.DoesNotExist:
                    return_status = ''
            pu_date = pu_date.strftime('%Y-%m-%d') if pu_date else ''
            expected_dod = expected_dod.strftime('%Y-%m-%d') if expected_dod else ''
            updated_date = updated_date.strftime('%Y-%m-%d') if updated_date else ''
            ships=Shipment.objects.get(airwaybill_number=airwaybill_number)
            ot=ships.deliveryoutscan_set.filter().order_by('id')
            if ot:
                first_outscan=ot[0].added_on.strftime("%d-%m-%y %H:%M")
                last_outscan=ot[ot.count()-1].added_on.strftime("%d-%m-%y %H:%M")
            else:
                 first_outscan=""
                 last_outscan=""
            row_content = (airwaybill_number, orderno, product_type, actual_weight,
                vol_weight, cod_amount, declared_value, origin, destination,
                vendor, shipper, consignee, consignee_address, contact_number,
                pu_date, expected_dod, mis_status, remarks, reason, recieved_by, updated_date,
                ref_airwaybill_number, return_status, ref_updated_on,first_outscan,last_outscan)

            unicode_cleaned_content = [val.encode('ascii', 'ignore') if isinstance(val, unicode) else val for val in row_content]
            clean_row_content = [' ' if not val else str(val) for val in unicode_cleaned_content]
            # write content to excel file
            report.write_row(clean_row_content)
    path = report.manual_sheet_close()
    return file_name


def generate_report_for_customer(code, name):
    cdict = customer_emails_dict.get(int(code))
    if cdict:
        customer_emails_list = cdict.get('to') + cdict.get('cc')
    else:
        customer_emails_list = []
        return True
    ecomm_team = ['jinesh@prtouch.com', 'sravank@ecomexpress.in',' sandeepc@ecomexpress.in']
    all_mails = customer_emails_list + ecomm_team

    date_range = get_date_range()
    start_date, end_date = date_range
    first_half, second_half = split_date(start_date, end_date)

    # get reports in two parts
    first_file = customer_report_inrange(code, first_half)
    first_file_link = settings.ROOT_URL + 'static/uploads/reports/' + first_file
    print first_file_link 

    second_file = customer_report_inrange(code, second_half)
    second_file_link = settings.ROOT_URL + 'static/uploads/reports/' + second_file
    print second_file_link 
    file_link = first_file_link + '\n' + second_file_link
    print file_link
    ecomm_send_mail('MIS Report  '+ name, file_link, all_mails)
    print 'mail send'
    return True

def generate_report(*args, **kwargs):
    # Get all customers
    if args:
        customers_list = Customer.objects.using('local_ecomm').filter(
            code__in=args, activation_status=True).values_list('code', 'name')
    else:
        customers_list = Customer.objects.using('local_ecomm').filter(
            activation_status=True).exclude(id=6).values_list('code', 'name')
    customers = list(reversed(customers_list))
    for code, name in customers:
        generate_report_for_customer(code, name)

class ThreadMis(threading.Thread):
    """Threaded billing pdf generation"""
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while customer_code_queue.qsize() > 0:
            #grabs host from queue
            code, name = customer_code_queue.get()

            # generate reports for given bill_id
            generate_report_for_customer(code, name)

            #signals to queue job is done
            customer_code_queue.task_done()

            #send email to ecom team
            if customer_code_queue.empty():
                exit(0)

def generate_by_thread(*args, **kwargs):
    if args:
        customers_list = Customer.objects.using('local_ecomm').filter(code__in=args, activation_status=True).values_list('code', 'name')
    else:
        customers_list = Customer.objects.using('local_ecomm').filter(activation_status=True).exclude(id__in=[6, 4]).values_list('code', 'name')
    customers = list(reversed(customers_list))
    #populate queue with data
    for code in customers:
        customer_code_queue.put(code)

    #spawn a pool of threads, and pass them queue instance
    threads = []
    for i in range(3):
        t = ThreadMis()
        threads.append(t)
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()
