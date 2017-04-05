from collections import defaultdict
from itertools import count
from service_centre.models import Shipment, get_internal_shipment_status, StatusUpdate
from ecomm_admin.models import ChangeLogs
from reports.report_api import ReportGenerator
from pickup.models import PickupSchedulerRegistration
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
#import csv
import datetime

def pickup_report(date_from, date_to, cust_id=None, origin_id=None):
    report = ReportGenerator('pickup_report_{0}.xlsx'.format(date_from))
    col_heads = (
        'SPUR No.',
        'Pickup Location', #1
        'Customer Name', #2
        'Sub Customer Name', #3
        'Pickup Type', #4
        'Registered Date', #5
        'No. of Shipments', #6
        'Status', #8
        'Reason Code'
    ) #8

    data = []
    q = Q()

    if date_from and date_to:
        t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
        date_to = t.strftime("%Y-%m-%d")
        q = q & Q(added_on__gte=date_from, added_on__lte=date_to)
    else:
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        date_from = yesterday.strftime('%Y-%m-%d')
        date_to = datetime.datetime.today().strftime('%Y-%m-%d')
        q = q & Q(added_on__gte=date_from, added_on__lte=date_to)

    if cust_id:
        q = q & Q(subcustomer_code__customer_id=cust_id)
    if origin_id: 
        q = q & Q(service_centre_id=origin_id)
    pickup_list = PickupSchedulerRegistration.objects.using('local_ecomm').filter(q)

    for pickup in pickup_list:
    	spur = pickup.id
    	origin = pickup.service_centre #0
    	customer = pickup.subcustomer_code.customer #1
    	subcustomer = pickup.subcustomer_code #2
    	pickup_type = "Regular" if pickup.pickup_scheduler.pickupscheduleweekdays_set.filter() else "Call Pickup"
    	reg_date = pickup.added_on  #5
        shipments = pickup.pickup.pieces if pickup.pickup else 0
    	status = "Completed" if pickup.status else "Pending" #7
        rc = pickup.reason_code
        data.append([spur,origin,customer,subcustomer,pickup_type,reg_date,shipments,status, rc])

    report.write_header(col_heads)
    path = report.write_body(data)
    return path
