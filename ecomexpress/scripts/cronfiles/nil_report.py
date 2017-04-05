import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
from xlsxwriter.workbook import Workbook

from django.core.mail import send_mail
from django.conf import settings
from django.core.mail.message import EmailMessage
from service_centre.models import Shipment, Order_price
from django.db.models import Q

now = datetime.datetime.now()

report_date_str = datetime.datetime.strptime(now.strftime('%Y%m%d'),"%Y%m%d").date()
nextmonthdate = report_date_str + datetime.timedelta(days=1)
nextmonth_date = nextmonthdate.strftime('%Y-%m-%d')
report_date = report_date_str.strftime('%Y-%m-01')


def nil_value():
    shipments=Shipment.objects.filter(inscan_date__isnull = False, shipment_date__range=(report_date,nextmonthdate), status__gte=2, status_type=1).\
           filter(Q(order_price__isnull = True) | Q(order_price__freight_charge__lte = 0.0)).exclude(shipper__code=32012).\
           values('airwaybill_number',
                 'chargeable_weight', 'pickup__service_centre__city__zone__zone_shortcode',
                 'original_dest__city__zone__zone_shortcode', 'shipper__name', 'shipper__code',
                 'inscan_date','current_sc__center_name','rts_status')

    file_name = "/nil_value_report_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)

    header_format = workbook.add_format()
    header_format.set_bold()
    header_format.set_align('center')

    plain_format = workbook.add_format()
    plain_format.set_align('center')
    
    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, 12, 15) # set column width 
    sheet.write(0, 4, "NIL Value report", header_format)
    row_num = 3
    
    #write column headers
    col_heads = ('AWB',
            'Chargeable Weight',
            'Origin Zone',
            'Destination Zone',
            'Customer Name',
            'Customer Code',
            'Inscan date',
            'Current SC',
            'RTS Status'
    #        'Item Description',
            )

    for col, head in enumerate(col_heads):
        sheet.write(row_num, col, head, header_format)

    for row, value_dict in enumerate(shipments, start=row_num+1):
        sheet.write(row, 0, str(value_dict.get('airwaybill_number')), plain_format)
        sheet.write(row, 1, str(value_dict.get('chargeable_weight')), plain_format)
        sheet.write(row, 2, str(value_dict.get('pickup__service_centre__city__zone__zone_shortcode')), plain_format)
        sheet.write(row, 3, str(value_dict.get('original_dest__city__zone__zone_shortcode')), plain_format)
        sheet.write(row, 4, str(value_dict.get('shipper__name')), plain_format)
        sheet.write(row, 5, str(value_dict.get('shipper__code')), plain_format)
        sheet.write(row,6, str(value_dict.get('inscan_date')), plain_format)
        sheet.write(row, 7, str(value_dict.get('current_sc__center_name')), plain_format)
        sheet.write(row, 8, str(value_dict.get('rts_status')), plain_format)

    workbook.close()
    return "/home/web/ecomm.prtouch.com/ecomexpress/static/uploads%s"%(file_name)



gq = nil_value()
gq_split = gq.split('/ecomexpress')
gq_path = 'http://cs.ecomexpress.in'+gq_split[1]

subject = "Nil Value Shipments Report"
message = "Please find the link below of shipments with NIL value \n %s"%(gq_path)
from_email = "support@ecomexpress.in"
to_email = ("samar@prtouch.com","jignesh@prtouch.com", , "onkar@prtouch.com")
#m = text(message)
#m['Subject'] = 'Generic Query'
#smtpObj.sendmail(sender, reciever, m.as_string())
send_mail(subject,message,from_email,to_email)


