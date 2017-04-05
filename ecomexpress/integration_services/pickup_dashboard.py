import sys
import re
import pdb
import xlrd
import datetime
from collections import defaultdict
from xlsxwriter.workbook import Workbook
#from openpyxl.reader.excel import load_workbook

from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Sum, Q, Count
from django.db.models.loading import get_model
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, send_mail

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

def pickup_dashbaord(request):
    file_name = 'pickup_format.xlsx'
    col_heads = ('Air Waybill number','Order Number','Product','Shipper','Consignee','Consignee Address1','Consignee Address2','Consignee Address3','Destination City','Pincode','State','Mobile','Telephone','Item Description','Pieces','Collectable Value','Declared value','Actual Weight','Volumetric Weight','Length(cms)','Breadth(cms)','Height(cms)','sub customer id','Pickup name','Pickup Address','Pickup Phone','Pickup Pincode','Return name','Return Address','Return Phone','Return Pincode')
    report.write_row(col_heads)
    report.manual_sheet_close()
    return render_to_response("integration_services/pickup_dashboard.html",
                               context_instance=RequestContext(request))


