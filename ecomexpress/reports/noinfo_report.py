#import os
#import sys

#os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
#sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
from xlsxwriter.workbook import Workbook

from django.conf import settings
from django.db.models import Sum, Q, get_model

from service_centre.models import Shipment, ShipmentStatusMaster, get_internal_shipment_status
from reports.report_api import ReportGenerator


def generate_noinfo_report(cust_id, date_from, date_to, csc=0, sc=0):

    col_heads = ("Air waybill Number", "Origin Service Centre", "Pickup Date", "Current Service Centre",
                 "Destination Service Centre", "Shipper", "Consignee", "Reason Code", "Updated On Date",
                 "Updated On Time", "Status", "Collectable Value", "Declared Value")
    file_name = 'noinfo_report_' + date_to + '.xlsx'
    report = ReportGenerator(file_name)
    report.write_header(col_heads)
    q = Q()

    if int(cust_id):
        q = q & Q(shipper_id = int(cust_id))
    if (date_from and date_to):
        t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
        date_to = t.strftime("%Y-%m-%d")
        q = q & Q(added_on__range=(date_from,datetime.datetime.now().date()))
    if int(sc):
        q = q & Q(service_centre_id=int(sc))
    q = q & Q(rts_status =0, rto_status=0)
    res_code = ShipmentStatusMaster.objects.using('local_ecomm').filter(id__in=[1,4,5,6,14,34,46,52,53])
    shipments = Shipment.objects.using('local_ecomm').filter(q).exclude(reason_code__in=res_code).exclude(shipper__code=32012).exclude(status_type=5)
    count = shipments.only('id').count()
    print q
    shipment_info={}
    download_list = []

    for a in shipments:
        count -= 1
        if not shipment_info.get(a):
            upd_time = a.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            status_upd =  a.statusupdate_set.all().order_by("-date")
            rto_status = 0
            rem_status = 0
            rts_status = 0
            rts_stat_val = 0
            shipment=a
            rto_status = shipment_history.objects.using('local_ecomm').filter(shipment=shipment, reason_code_id = 34)
            rem_status = shipment_history.objects.using('local_ecomm').filter(shipment=shipment, remarks = "Return to Origin")
            history1 = shipment_history.objects.using('local_ecomm').filter(shipment=shipment).exclude(status__in=[11,12,16])
            if not history1.exists():
                continue
            history = history1.latest('updated_on')
            if history.reason_code_id in [1,6,46]:
                continue
               #if history.current_sc_id <> int(csc):
                  #print 'continue...'
                  #continue
            rtss = history1.order_by('id')
            if (rtss[0].reason_code_id==5):
                rts_status = 1
            if (shipment.reason_code_id==5 or \
                     shipment.return_shipment==3 or \
                     rts_status or \
                     shipment.return_shipment==2 or
                     rto_status or rem_status):
                rts_stat_val = 1
            sc = a.service_centre
            if history.updated_on:
                upd_date = history.updated_on.strftime("%Y-%m-%d")
                last_date=datetime.datetime.today()-datetime.timedelta(days=2)
                last_date = last_date.strftime("%Y-%m-%d")
                if upd_date >= last_date or rts_stat_val == 1:
                    b=0
                else:
                    b = 1
            else:
                b = 1
            if b==1:
                if history:
                    hist = history
                    if not a.original_dest:
                        u = (a.airwaybill_number,
                             a.pickup.service_centre.center_name,
                             a.added_on,
                             hist.current_sc,
                             sc,
                             a.shipper.name,
                             a.consignee,
                             a.reason_code,
                             hist.updated_on.date(),
                             hist.updated_on.time(),
                             get_internal_shipment_status(a.status),
                             a.collectable_value,
                             a.declared_value)
                    else:
                        u = (a.airwaybill_number,
                             a.pickup.service_centre.center_name,
                             a.added_on,
                             hist.current_sc,
                             sc,
                             a.shipper.name,
                             a.consignee,
                             a.reason_code,
                             hist.updated_on.date(),
                             hist.updated_on.time(),
                             get_internal_shipment_status(a.status),
                             a.collectable_value,
                             a.declared_value)
                    download_list.append(u)
                    shipment_info[a]=hist
                else:
                    shipment_info[a]=None
    path = report.write_body(download_list)
    return file_name 

