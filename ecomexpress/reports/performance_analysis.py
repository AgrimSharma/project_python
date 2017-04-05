import sys
import re
import pdb
import xlrd
from reports.report_api import ReportGenerator, CSVReportGenerator, generate_zip
import datetime
from collections import defaultdict
from xlsxwriter.workbook import Workbook
 
from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Sum, Q, Count
#from django.db.models.loading import get_mode
from django.contrib.auth.models import User

from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Sum, Q, Count
#from django.db.models.loading import get_model
import datetime
from service_centre.models import *
from service_centre.general_updates import update_shipment_pricing
from location.models import Pincode, ServiceCenter
from authentication.models import EmployeeMaster, Department
from airwaybill.models import AirwaybillCustomer, AirwaybillNumbers
from ecomm_admin.models import ShipmentStatusMaster, PickupStatusMaster
from reports.report_api import ReportGenerator, CSVReportGenerator, generate_zip
from reports.customer_emails import customer_emails_dict
from reports.ecomm_mail import ecomm_send_mail
from nimda.views import shipment_rts_creation
from customer.models import *
from billing.generate_bill_pdf import *
from billing.generate_bill_reports import *
from reports.ecomm_mail import ecomm_send_mail
from service_centre.models import *
from reports.models import Cluster,ClusterDCMapping,ClusterEmailMapping
from delivery.models import *
import csv


def performance_analysis():
    """
    input: your function will take 3 arguments: from_date, to_date, sc
    process: create an excel report for performance analysis
    output: file_name / file_link
    """
    file_name = 'Performance_Analysis.xlsx'
    report = ReportGenerator(file_name)
    rtype = 0
    q = Q()
    r = Q()
    s = Q()
    now = datetime.datetime.now()

    start_date = datetime.datetime(2015, 3, 1)
    end_date = datetime.datetime(2015, 3, 31)
    nowd = now.date()-datetime.timedelta(days=1)
    yest = now.date()-datetime.timedelta(days=2)
    q = q & Q(added_on__range = (yest,nowd))

   # c = "Customer" if rtype else "Location"
    col_head = ('Location', 'Total Shipments','Total Delivered Shipments','% Delivered Shipments',
                'Returned Shipments','%Returned Shipments','Shipments in Outscan','Total Undelivered Shipments',
                '%Undelivered Shipments','Shipments in Transit','RTO in Transit')
    #for col, val in enumerate(col_head):
     #   sheet.write(1,col,val,header)
    report.write_header(col_head)
    q = q & Q(rts_status__in = [0,2])
    filter_by = Customer.objects.all()
    """ if rtype else ServiceCenter.objects.filter(s)"""
    for a in filter_by:
        r = Q(shipper = a) if rtype else Q(service_centre = a)
	tot_ships = Shipment.objects.filter(q).filter(r).only('id').count()
	del_ships = Shipment.objects.filter(q, status = 9).filter(r).only('id').count()
	ret_ships = Shipment.objects.filter(q, rts_status=2).filter(r).only('id').count()
	ofd_ships = Shipment.objects.filter(q, status = 7).filter(r).only('id').count()
	undel_ships = Shipment.objects.filter(q, status = 8).exclude(rts_status=2).filter(r).only('id').count()
	transit_ships = Shipment.objects.filter(q, status__in = [0,1,2,3,4,5,6]).filter(r).exclude(rto_status=1).only('id').count()
	rto_transit_ships = Shipment.objects.filter(q, status__in=[0,1,2,3,4,5,6], rto_status=1).filter(r).only('id').count()
	del_perc = float(del_ships)/float(tot_ships)*100.0 if tot_ships else 0
	ret_perc = float(ret_ships)/float(tot_ships)*100.0 if tot_ships else 0
	undel_perc = float(undel_ships)/float(tot_ships)*100.0 if tot_ships else 0

	row = [a, tot_ships, del_ships, round(del_perc,2), ret_ships, round(ret_perc,2), ofd_ships, undel_ships, round(undel_perc,2), transit_ships, rto_transit_ships]
        report.write_row(row)
    report.manual_sheet_close()
    print file_name

