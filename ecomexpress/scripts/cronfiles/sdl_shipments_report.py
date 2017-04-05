import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
from xlsxwriter.workbook import Workbook

from django.core.mail import send_mail
from django.conf import settings
from django.core.mail.message import EmailMessage
from service_centre.models import Shipment, Order_price,Customer
#import smtplib
#from email.mime.text import MIMEText as text

# Return the (from, to) date range
def get_dates_range():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(1)
    date_to = today.strftime('%Y-%m-%d 07:00:00')
    date_from = yesterday.strftime('%Y-%m-%d 07:00:00')
    return (date_from, date_to)
#    return ('2013-07-14 07:00:00', '2013-07-16 07:00:00')

# Get shipments data
def get_shipments():
    dates_range = get_dates_range()
    cust=Customer.objects.get(code=32012)
    ships=Shipment.objects.filter(inscan_date__range=dates_range, sdl=1).exclude(shipper=cust).\
            values('airwaybill_number',
                   'pickup__service_centre__center_name',
                   'original_dest__center_name',
                   'shipper__name',
                   'shipper__code',
                   'pincode',
                   'inscan_date',
                   'chargeable_weight',
                   'order_price__sdl_charge').exclude(rts_status=1)
    return ships

# Generate excel file from the given data
def generate_excel(data_list):
    file_name = "/sdl_shipments_report_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format()
    header_format.set_bold()
    header_format.set_align('center')

    plain_format = workbook.add_format()
    plain_format.set_align('center')

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, 12, 15) # set column width
    sheet.write(0, 4, "SDL Shipments Report", header_format)

    row_num = 3

    #write column headers
    col_heads = ('AWB',
            'Origin',
            'Destination',
            'Customer Name',
            'Customer Code',
            'Pincode',
            'Inscan date',
            'Chargeable Weight',
            'SDL Charge',
            )
    
    for col, head in enumerate(col_heads):
        sheet.write(row_num, col, head, header_format)

    # write data to excel sheet
    # data is in following format
    #[{'airwaybill_number': 700172405L,
      #'chargeable_weight': 0.0,
      #'codcharge__cod_charge': 30.0,
      #'inscan_date': datetime.datetime(2013, 5, 1, 8, 28, 34),
      #'order_price__freight_charge': 19.0,
      #'order_price__fuel_surcharge': 4.75,
      #'order_price__rto_charge': 0.0,
      #'order_price__sdl_charge': 0.0,
      #'order_price__to_pay_charge': 0.0,
      #'order_price__valuable_cargo_handling_charge': 0.0,
      #'original_dest__center_name': u'GHAZIABAD-GZB',
      #'pickup__service_centre__center_name': u'GURGAON - GGA'},..]
    for row, value_dict in enumerate(data_list, start=row_num+1):
        sheet.write(row, 0, str(value_dict.get('airwaybill_number')), plain_format)
        sheet.write(row, 1, str(value_dict.get('pickup__service_centre__center_name')), plain_format)
        sheet.write(row, 2, str(value_dict.get('original_dest__center_name')), plain_format)
        sheet.write(row, 3, str(value_dict.get('shipper__name')), plain_format)
        sheet.write(row, 4, str(value_dict.get('shipper__code')), plain_format)
        sheet.write(row, 5, str(value_dict.get('pincode')), plain_format)
        sheet.write(row, 6, str(value_dict.get('inscan_date')), plain_format)
        sheet.write(row, 7, str(value_dict.get('chargeable_weight')), plain_format)
        sheet.write(row, 8, str(value_dict.get('order_price__sdl_charge')), plain_format)

    workbook.close()
    return file_name

# Email the excel file as attachment
def mail_report(file_name):
 #   smtpObj = smtplib.SMTP('i.prtouch.com', 26)
    #email = EmailMessage()
    #email.subject = "Daily SDL Report"
    #email.body = "Dear Team,\nThis is daily SDL report\n\nWith Regards,\nPrtouch"
    #email.from_email = "Jignesh Vasani <jignesh@prtouch.com>"
    #email.to = [ "jinesh@prtouch.com", ]
    file_path = settings.FILE_UPLOAD_TEMP_DIR+file_name
    base_path = file_path.split('ecomexpress/')[1]
  #  sender = "support@prtouch.com"
  #  reciever = ["krishnanta@ecomexpress.in", "satyak@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in","samar@prtouch.com","jaideeps@ecomexpress.in", "jignesh@prtouch.com", "nareshb@ecomexpress.in"]
    download_path = 'http://billing.ecomexpress.in/'+base_path
    message = "Dear Team,\nPlease download SDL from the following link.\n %s \n\n" % (download_path)
   # m = text(message)
   # m['Subject'] = 'SDL Report'
    #email.attach_file(file_path) # Attach a file directly
    #email.send()
   # smtpObj.sendmail(sender, reciever, m.as_string())  
    subject = "Daily SDL Report"
    to = ("sunainas@ecomexpress.in","krishnanta@ecomexpress.in", "satyak@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in","jaideeps@ecomexpress.in", "jignesh@prtouch.com", "nareshb@ecomexpress.in","onkar@prtouch.com","veenav@ecomexpress.in","rsinha@ecomexpress.in", "shilpaa@ecomexpress.in")
  #  download_path = 'http://eepl.ecomexpress.in/'+base_path
#    to = ("samar@prtouch.com",)
  #  message = "Dear Team,\nThis is daily SDL report. Download it from the following link.\n %s \n\nWith Regards,\nPrtouch" % (download_path)
  #  to = ['samar@prtouch.com']
    send_mail(subject, message, 'support@ecomexpress.in', to)

def main():
    data_list = get_shipments()
    file_name = generate_excel(data_list)
    mail_report(file_name)

if __name__ == "__main__":
    main()
