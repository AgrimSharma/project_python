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
from reports.views import get_strike_rate_from_shipments

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



def strike_rate_analysis():
    cs = Customer.objects.filter(activation_status = True)
    print cs
    file_name = "/strike_analysis_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()

    sheet.write(3, 0, "Customer")
    sheet.write(3, 1, "Month")
    sheet.write(3, 2, "Count")
    sheet.write(3, 3, "Total")
    sheet.write(3, 4, "On Time")
    sheet.write(3, 5, "%Age")
    sheet.write(3, 6, "Day 1")
    sheet.write(3, 7, "%Age")
    sheet.write(3, 8, "Day 2")
    sheet.write(3, 9, "%Age")
    sheet.write(3, 10, "Day 3")
    sheet.write(3, 11, "%Age")
    sheet.write(3, 12, "Day>3")
    sheet.write(3, 13, "%Age")
 
    row = 4

    for customer in cs:

        #ym = request.POST.get('month',None)
        year_month = now.strftime("%Y-%m") 
        month = year_month.split("-")
 	date_from = now.strftime("%Y-%m")+"-01"
 	date_to = now.strftime("%Y-%m-%d")

        q = Q()

        q = q & Q(shipper = int(customer.id))   

        q = q & Q(added_on__year=month[0], added_on__month=month[1])
            
        p = 1
        c = 1
        ppd_shipment = Shipment.objects.filter(q, product_type="ppd").exclude(return_shipment=3).exclude(rts_status=1)
        ppd_shipment_count = ppd_shipment.count()
        if ppd_shipment_count == 0:
            p = 0
            ppd_shipment_count = 1
            
        strike_day_ppd_count = defaultdict(int) 

        strike_day_ppd_count = get_strike_rate_from_shipments(ppd_shipment, strike_day_ppd_count)

        on_time_ppd_perc= round(((float(strike_day_ppd_count[0])/float(ppd_shipment_count))*100.0),2)
        day1_ppd_perc = round(((float(strike_day_ppd_count[1])/float(ppd_shipment_count))*100.0),2)
        day2_ppd_perc = round(((float(strike_day_ppd_count[2])/float(ppd_shipment_count))*100.0),2)
        day3_ppd_perc = round(((float(strike_day_ppd_count[3])/float(ppd_shipment_count))*100.0),2)
        day4_ppd_perc = round(((float(strike_day_ppd_count[4])/float(ppd_shipment_count))*100.0),2)
            
        cod_shipment = Shipment.objects.filter(q, product_type="cod").exclude(return_shipment=3).exclude(rts_status=1)
        cod_shipment_count = cod_shipment.count()
        if cod_shipment_count == 0:
            c = 0
            cod_shipment_count = 1
                
        #delivered_cod = StatusUpdate.objects.filter(shipment__in=cod_shipment, status=2)
        #delivered_cods = DeliveryOutscan.objects.filter(shipments__in=cod_shipment)

        strike_day_cod_count = defaultdict(int) 

        strike_day_cod_count = get_strike_rate_from_shipments(cod_shipment, strike_day_cod_count)

        on_time_cod_perc= round(((float(strike_day_cod_count[0])/float(cod_shipment_count))*100.0),2)
        day1_cod_perc = round(((float(strike_day_cod_count[1])/float(cod_shipment_count))*100.0),2)
        day2_cod_perc = round(((float(strike_day_cod_count[2])/float(cod_shipment_count))*100.0),2)
        day3_cod_perc = round(((float(strike_day_cod_count[3])/float(cod_shipment_count))*100.0),2)
        day4_cod_perc = round(((float(strike_day_cod_count[4])/float(cod_shipment_count))*100.0),2)

        if p == 0:
            ppd_shipment_count = 0
        if c == 0:
            cod_shipment_count = 0    
        if not (year_month):
            year_month = str(date_from)+' To '+str(date_to)
            
        total=ppd_shipment_count+cod_shipment_count    

        sheet.write(0, 2, "Strike Rate Analysis - Customer Wise")
    
         
        print customer.name 

        sheet.write(row, 0, customer.name)
        sheet.write(row+1, 0, customer.name)

        sheet.write(row, 1, year_month)
        sheet.write(row+1, 1, year_month)
        
        sheet.write(row, 2, "Prepaid")
        sheet.write(row+1, 2, "COD")
        
        sheet.write(row, 3, str(ppd_shipment_count))
        sheet.write(row+1, 3, str(cod_shipment_count))
        
        sheet.write(row, 4, str(strike_day_ppd_count[0]))
        sheet.write(row+1, 4, str(strike_day_cod_count[0]))
        sheet.write(row, 5, str(on_time_ppd_perc)+'%')
        sheet.write(row+1, 5, str(on_time_cod_perc)+'%')
        
        sheet.write(row, 6, str(strike_day_ppd_count[1]))
        sheet.write(row+1, 6, str(strike_day_cod_count[1]))
        sheet.write(row, 7, str(day1_ppd_perc)+'%')
        sheet.write(row+1, 7, str(day1_cod_perc)+'%')
        
        sheet.write(row, 8, str(strike_day_ppd_count[2]))
        sheet.write(row+1, 8, str(strike_day_cod_count[2]))
        sheet.write(row, 9, str(day2_ppd_perc)+'%')
        sheet.write(row+1, 9, str(day2_cod_perc)+'%')
        
        sheet.write(row, 10, str(strike_day_ppd_count[3]))
        sheet.write(row+1, 10, str(strike_day_cod_count[3]))
        sheet.write(row, 11, str(day3_ppd_perc)+'%')
        sheet.write(row+1, 11, str(day3_cod_perc)+'%')
        
        sheet.write(row, 12, str(strike_day_ppd_count[4]))
        sheet.write(row+1, 12, str(strike_day_cod_count[4]))
        sheet.write(row, 13, str(day4_ppd_perc)+'%')
        sheet.write(row+1, 13, str(day4_cod_perc)+'%')

        row += 3

    workbook.close()
    return file_name 


def strike_rate_analysis_report():
    #today = datetime.datetime.now().date()
    #yesterday = now - datetime.timedelta(days=1)
    file_name = strike_rate_analysis() 
    print file_name
    '''send_mail('Ageing SOP Report',
              "Dear Team,\n Ageing SOP report has been generated. Please find the link below.\n http://cs.ecomexpress.in/static/uploads{0}\n\n".format(file_name),
              'support@ecomexpress.in', ['samar@prtouch.com','jignesh@prtouch.com'])
#           'support@ecomexpress.in',['samar@prtouch.com'])
    '''
    return True

    

if __name__ == '__main__':
    strike_rate_analysis_report()
