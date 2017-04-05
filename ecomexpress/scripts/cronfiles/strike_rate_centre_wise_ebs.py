import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
from xlsxwriter.workbook import Workbook
from django.conf import settings
from django.db.models import Count, Sum
from django.core.mail import send_mail
from service_centre.models import Shipment, DeliveryOutscan
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
import sys, traceback
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from customer.models import Customer
from location.models import ServiceCenter
from django.views.decorators.csrf import csrf_exempt
from service_centre.models import Shipment,StatusUpdate
from django.db.models import get_model
from django.core.management import call_command
from django.db.models import Q
from django.conf import settings
from service_centre.models import *
import datetime
import xlwt
import json
from decimal import *
from collections import defaultdict
from xlsxwriter.workbook import Workbook
from reports.views import get_strike_rate_from_shipments, get_strike_rate_from_shipments_del

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")
nextmonth = now + datetime.timedelta(days=1)
nextmonth = nextmonth.strftime("%Y_%m")
         
          
book = xlwt.Workbook(encoding='utf8') 
default_style = xlwt.Style.default_style
datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
header_style = xlwt.XFStyle()
status_style = xlwt.XFStyle()
category_style = xlwt.XFStyle()
font = xlwt.Font() 
font.bold = True
             
pattern = xlwt.Pattern() 
pattern.pattern = xlwt.Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = 5
           
pattern1 = xlwt.Pattern()
pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
pattern1.pattern_fore_colour = 0x0A

borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
header_style.pattern = pattern
status_style.pattern = pattern1
header_style.font = font
category_style.font = font
header_style.borders=borders
default_style.borders=borders



PROJECT_ROOT = '/home/web/ecomm.prtouch.com/ecomexpress'
root_url = 'http://ecomm.prtouch.com/'

now = datetime.datetime.now()

def strike_rate_analysis():
    scs = ServiceCenter.objects.filter().order_by("center_shortcode")
    file_name = "/strike_analysis_by_centre_ebs_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()
 
    header = workbook.add_format()
    header.set_bg_color('green')
    header.set_bold()
    header.set_border()
    plain_format = workbook.add_format()

    sheet.write(3, 0, "Centre", header)
    sheet.write(3, 1, "Month", header)
    sheet.write(3, 2, "Count", header)
    sheet.write(3, 3, "Total", header)
    sheet.write(3, 4, "On Time Delivery Attempt", header)
    sheet.write(3, 5, "%Age", header)
    sheet.write(3, 6, "Day 1 Delivery Attempt", header)
    sheet.write(3, 7, "%Age", header)
    sheet.write(3, 8, "Day 2 Delivery Attempt", header)
    sheet.write(3, 9, "%Age", header)
    sheet.write(3, 10, "Day 3 Delivery Attempt", header)
    sheet.write(3, 11, "%Age", header)
    sheet.write(3, 12, "Day>3 Delivery Attempt", header)
    sheet.write(3, 13, "%Age", header)
    sheet.write(3, 14, "On Time Delivered", header)
    sheet.write(3, 15, "%Age", header)
    sheet.write(3, 16, "Day 1 Delivered", header)
    sheet.write(3, 17, "%Age", header)
    sheet.write(3, 18, "Day 2 Delivered", header)
    sheet.write(3, 19, "%Age", header)
    sheet.write(3, 20, "Day 3 Delivered", header)
    sheet.write(3, 21, "%Age", header)
    sheet.write(3, 22, "Day>3 Delivered", header)
    sheet.write(3, 23, "%Age", header)

 
    row = 4

    for sc in scs:

        q = Q()
        year_month = 0
        q = q & Q(original_dest=int(sc.id))
        q = q & Q(Q(airwaybill_number__startswith = 3) | Q(airwaybill_number__startswith = 4))
        yest = now.date()-datetime.timedelta(days=2)
        q = q & Q(added_on__month=now.month, added_on__lt = yest)  
        e = 1
        ebs_shipment = Shipment.objects.filter(q).exclude(rts_status=1)
        ebs_shipment_count = ebs_shipment.count()
        if ebs_shipment_count == 0:
            e = 0
            ebs_shipment_count = 1
            
        strike_day_ebs_count = defaultdict(int) 
        strike_day_ebs_count = get_strike_rate_from_shipments(ebs_shipment, strike_day_ebs_count)
        strike_day_ebs_count_del = defaultdict(int)
        strike_day_ebs_count_del = get_strike_rate_from_shipments_del(ebs_shipment, strike_day_ebs_count_del)        
        on_time_ebs_perc= round(((float(strike_day_ebs_count[0])/float(ebs_shipment_count))*100.0),2)
        day1_ebs_perc = round(((float(strike_day_ebs_count[1])/float(ebs_shipment_count))*100.0),2)
        day2_ebs_perc = round(((float(strike_day_ebs_count[2])/float(ebs_shipment_count))*100.0),2)
        day3_ebs_perc = round(((float(strike_day_ebs_count[3])/float(ebs_shipment_count))*100.0),2)
        day4_ebs_perc = round(((float(strike_day_ebs_count[4])/float(ebs_shipment_count))*100.0),2)
  

        on_time_ebs_perc_del= round(((float(strike_day_ebs_count_del[0])/float(ebs_shipment_count))*100.0),2)
        day1_ebs_perc_del = round(((float(strike_day_ebs_count_del[1])/float(ebs_shipment_count))*100.0),2)
        day2_ebs_perc_del = round(((float(strike_day_ebs_count_del[2])/float(ebs_shipment_count))*100.0),2)
        day3_ebs_perc_del = round(((float(strike_day_ebs_count_del[3])/float(ebs_shipment_count))*100.0),2)
        day4_ebs_perc_del = round(((float(strike_day_ebs_count_del[4])/float(ebs_shipment_count))*100.0),2)
          
        if e == 0:
            ebs_shipment_count = 0
        if not (year_month):
               year_month = ""
            
        total=ebs_shipment_count

        sheet.write(0, 2, "Strike Rate Analysis - Centre (EBS)")
    
         

        sheet.write(row, 0, sc.center_shortcode, plain_format)

        sheet.write(row, 1, year_month, plain_format)
        
        sheet.write(row, 2, "EBS", plain_format)
        
        sheet.write(row, 3, str(ebs_shipment_count), plain_format)
        
        sheet.write(row, 4, str(strike_day_ebs_count[0]), plain_format)
        sheet.write(row, 5, str(on_time_ebs_perc)+'%', plain_format)
        
        sheet.write(row, 6, str(strike_day_ebs_count[1]), plain_format)
        sheet.write(row, 7, str(day1_ebs_perc)+'%', plain_format)
        
        sheet.write(row, 8, str(strike_day_ebs_count[2]), plain_format)
        sheet.write(row, 9, str(day2_ebs_perc)+'%', plain_format)
        
        sheet.write(row, 10, str(strike_day_ebs_count[3]), plain_format)
        sheet.write(row, 11, str(day3_ebs_perc)+'%', plain_format)
        
        sheet.write(row, 12, str(strike_day_ebs_count[4]), plain_format)
        sheet.write(row, 13, str(day4_ebs_perc)+'%', plain_format)


        sheet.write(row, 14, str(strike_day_ebs_count_del[0]), plain_format)
        sheet.write(row, 15, str(on_time_ebs_perc_del)+'%', plain_format)

        sheet.write(row, 16, str(strike_day_ebs_count_del[1]), plain_format)
        sheet.write(row, 17, str(day1_ebs_perc_del)+'%', plain_format)

        sheet.write(row, 18, str(strike_day_ebs_count_del[2]), plain_format)
        sheet.write(row, 19, str(day2_ebs_perc_del)+'%', plain_format)

        sheet.write(row, 20, str(strike_day_ebs_count_del[3]), plain_format)
        sheet.write(row, 21, str(day3_ebs_perc_del)+'%', plain_format)

        sheet.write(row, 22, str(strike_day_ebs_count_del[4]), plain_format)
        sheet.write(row, 23, str(day4_ebs_perc_del)+'%', plain_format)

 
        row += 2

    workbook.close()
    return file_name 


def strike_rate_analysis_report():
    #today = datetime.datetime.now().date()
    #yesterday = now - datetime.timedelta(days=1)
    file_name = strike_rate_analysis() 
    print file_name
    send_mail('Centre Strike Rate Analysis',
              "Dear Team,\n Centre Strike Rate Analysis by Centre report has been generated. Please find the link below.\n http://cs.ecomexpress.in/static/uploads{0}\n\n".format(file_name),
   #           'support@ecomexpress.in', ['onkar@prtouch.com','sunainas@ecomexpress.in','sravank@ecomexpress.in','jignesh@prtouch.com'])
           'support@ecomexpress.in',['samar@prtouch.com'])
    return True

    

if __name__ == '__main__':
    strike_rate_analysis_report()
