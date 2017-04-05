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
import datetime

now = datetime.datetime.now()
#before = now - datetime.timedelta(days=21)

report_date_str = datetime.datetime.strptime(now.strftime('%Y%m%d'),"%Y%m%d").date()
nextmonthdate = report_date_str + datetime.timedelta(days=1)
nextmonth_date = nextmonthdate.strftime('%Y-%m-%d')
report_date = report_date_str.strftime('%Y-%m-01')
#report_date='2013-10-01'
#report_date="2014-05-01"
#nextmonth_date="2014-05-31"
def high_weight():
    shipments=Shipment.objects.filter(chargeable_weight__gt=20, shipment_date__range=(report_date,nextmonth_date)).\
           values('pickup__service_centre__city__city_shortcode','airwaybill_number',
                 'shipper__code', 'shipper__name', 'actual_weight','volumetric_weight', 
                 'length', 'breadth', 'height', 
                 'chargeable_weight', 
                 'original_dest__city__city_shortcode', 
                 'shipment_date','current_sc__center_name','item_description')
    file_name = "/high_weight_report_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
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
    sheet.write(0, 4, "High Weight Report", header_format)
    row_num = 3

    #write column headers
    col_heads = ('Origin',
            'Airwaybill Number',
            'Customer Code',
            'Customer Name',
            'Actual Weight',
            'Volumetric Weight',
            'Length',
            'Breadth', 
            'Height',
            'Chargeable Weight',
            'Destination',
            'Inscan date',
            'Current SC',
            'Item Description',
            )

    for col, head in enumerate(col_heads):
        sheet.write(row_num, col, head, header_format)

    for row, value_dict in enumerate(shipments, start=row_num+1):
        sheet.write(row, 0, str(value_dict.get('pickup__service_centre__city__city_shortcode')), plain_format)
        sheet.write(row, 1, str(value_dict.get('airwaybill_number')), plain_format)
        sheet.write(row, 2, str(value_dict.get('shipper__code')), plain_format)
        sheet.write(row, 3, str(value_dict.get('shipper__name')), plain_format)
        sheet.write(row, 4, str(value_dict.get('actual_weight')), plain_format)
        sheet.write(row, 5, str(value_dict.get('volumetric_weight')), plain_format)
        sheet.write(row, 6, str(value_dict.get('length')), plain_format)
        sheet.write(row, 7, str(value_dict.get('breadth')), plain_format)
        sheet.write(row, 8, str(value_dict.get('height')), plain_format)
        sheet.write(row, 9, str(value_dict.get('chargeable_weight')), plain_format)
        sheet.write(row, 10, str(value_dict.get('original_dest__city__city_shortcode')), plain_format)
        sheet.write(row,11, str(value_dict.get('shipment_date')), plain_format)
        sheet.write(row, 12, str(value_dict.get('current_sc__center_name')), plain_format)
        try:
           sheet.write(row, 13, str(value_dict.get('item_description')), plain_format)
        except:
           pass


    workbook.close()
    return "/home/web/ecomm.prtouch.com/ecomexpress/static/uploads%s"%(file_name)



gq = high_weight()
gq_split = gq.split('/ecomexpress')
gq_path = 'http://billing.ecomexpress.in'+gq_split[1]

subject = "High Weight Shipments Report"
message = "Please find the link below of shipments weighing more than 20KG \n %s"%(gq_path)
from_email = "support@ecomexpress.in"
to_email = ("rajivj@ecomexpress.in",'birjus@ecomexpress.in',"praveen.joshi@ecomexpress.in",  "rameshw@ecomexpress.in",   "prashanta@ecomexpress.in",   "lokeshr@ecomexpress.in",   "Sbabaria@ecomexpress.in",   "sunainas@ecomexpress.in",  "shalinia@ecomexpress.in", "veenav@ecomexpress.in",  "Rakeshp@ecomexpress.in",   "rakeshl@ecomexpress.in","anilku@ecomexpress.in","sravank@ecomexpress.in", "jaideeps@ecomexpress.in", "nareshb@ecomexpress.in", "prashanta@ecomexpress.in", "jignesh@prtouch.com", "onkar@prtouch.com")
send_mail(subject,message,from_email,to_email)
