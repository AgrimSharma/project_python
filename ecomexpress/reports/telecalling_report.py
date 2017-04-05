from collections import defaultdict
from itertools import count
from service_centre.models import Shipment, get_internal_shipment_status, StatusUpdate
from ecomm_admin.models import ChangeLogs
from reports.report_api import ReportGenerator
from track_me.models import TeleCallingReport
from django.conf import settings

def generate_tellecalling_report(date_from, date_to, cust_id=0, destination_id=0):
    report = ReportGenerator('tellecalling_report.xlsx')
    col_heads = (
        'AWB',
        'Pickup Date', #1
        'Destination', #2
        'Shipper', #3
        'Status', #4
        'Updated On', #5
        'Tellecalling Remark', #6
        'Updated Date', #7
        'Updated By'
    ) #8
    data = []
    comment_list = TeleCallingReport.objects.using('local_ecomm').filter(added_on__range=(date_from, date_to))
    for comment in  comment_list:
    	sh = comment.shipment
    	AWB = sh.airwaybill_number #0
    	Pickup_date = sh.added_on #1
    	destination = sh.original_dest #2
    	shipper = sh.shipper.name #3
    	Status = str(get_internal_shipment_status(sh.status))+' '+str(comment.added_on)  #4
    	updated_on = sh.updated_on  #5
    	tele_remark = comment.comments #6
    	Updated_Date = comment.added_on#7
    	emp = comment.updated_by
    	updated_by = str(emp.firstname)+' '+str(emp.lastname)

        data.append([AWB,Pickup_date,destination,shipper,Status,updated_on,tele_remark,Updated_Date,updated_by])

    report.write_header(col_heads)
    path = report.write_body(data)
    return path
