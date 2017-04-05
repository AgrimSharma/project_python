import os
import sys 
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')




from collections import defaultdict
from itertools import count
from service_centre.models import *
from ecomm_admin.models import ChangeLogs
from reports.report_api import ReportGenerator
from django.conf import settings
from django.db.models import *
from billing.models import *
import datetime


def generate_runcode_report():
    now = datetime.datetime.now()
    report = ReportGenerator('run_code_report_rev1_{0}.xlsx'.format(now.strftime('%Y-%m-%d')))
    year = now.year
    month = now.month
    day = int(now.day)-1
    col_heads = ('Run code',
        'Origin',
        'Destination',
        'No Of Bags',
        'No Of shpts',
        'Added On',
        )
    report.write_header(col_heads)
#    rs = RunCode.objects.using('local_ecomm').filter(added_on__year =2014,added_on__month=2,added_on__day=22)   
#    rs=RunCode.objects.filter(added_on__range=('2014-05-20 00:00:00','2014-05-21 00:00:00'))
  #  org_dest = rs.values_list('id', 'origin','origin__center_name','added_on')
    #org_dest = rs.values_list('id', 'origin', 'destination','origin__center_name','destination__center_name','added_on')
    #for org_des in org_dest:
 #   for runcode in rs:
        #bags=Connection.objects.using('local_ecomm').filter(runcode=runcode[0], origin__id=runcode[1], destination__id=runcode[2]).values_list('bags__bag_number',
    con = Connection.objects.using('local_ecomm').filter(added_on__year =2014,added_on__month=2,added_on__day=22)
    bags=con.values_list('bags__bag_number',
        flat=True)
    shipment_count = Bags.objects.using('local_ecomm').filter(bag_number__in=bags, bag_status__gte=2).exclude(bag_status=11).aggregate(Count('ship_data'))
    bag_count = len(bags)
    print bag_count
      #  if bag_count > 0:
    runcode = a.runcode_set.get()
    if shipment_count['ship_data__count']:
          row=(runcode.id,runcode.origin,con.destination,len(bags),shipment_count['ship_data__count'],con.added_on)
          print row
          report.write_row(row)
    file_name = report.manual_sheet_close()
    print file_name



generate_runcode_report()
