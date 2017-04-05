
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import *
from reports.views import *
import settings

import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
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
from track_me.models import *

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives


import datetime
from reports.noinfo_report import generate_noinfo_report
from reports.cod_collection_pod_report import CodCollectionPodReport
count = 1
import datetime
import xlwt
import json
from decimal import *
from collections import defaultdict
from xlsxwriter.workbook import Workbook
from reports.correction_report import generate_correction_report
#from scripts.cronfiles.outscan_del import *
from reports.telecalling_report import *




def bagging_report():
    download_list=[]
    now=datetime.datetime.now()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yday=yesterday.strftime('%Y-%m-%d')
    yday_start=yday+" 00:00:00"
    yday_end=yday+" 23:59:59"
    sc=ServiceCenter.objects.all()
    monthdir = yesterday.strftime("%Y_%m")
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
    for s in sc:
             hist=shipment_history.objects.using('local_ecomm').filter(updated_on__range=[yday_start,yday_end],current_sc=s)
             one_status=Shipment.objects.using('local_ecomm').filter(added_on__year=int(yesterday.year),added_on__month=int(yesterday.month),added_on__day=int(yesterday.day),pickup__service_centre=s).count()
             two_status=hist.filter(status=2).count()
             three_status=hist.filter(status=3).count()
             four_status=hist.filter(status=4).count()
             five_status=hist.filter(status=5).count()
             six_status=hist.filter(status=6).count()
             onefour_count=hist.filter(status=14).count()
             onefive_count=hist.filter(status=15).count()
             onesix_count=hist.filter(status=16).count()
             u=(s,one_status,two_status,three_status,four_status,five_status,six_status,int(onefour_count),int(onefive_count),int(onesix_count))
             download_list.append(u)
    hist=shipment_history.objects.using('local_ecomm').filter(updated_on__range=[yday_start,yday_end])
    two_status=hist.filter(status=2).count()
    three_status=hist.filter(status=3).count()
    four_status=hist.filter(status=4).count()
    five_status=hist.filter(status=5).count()
    six_status=hist.filter(status=6).count()
    onefour_count=hist.filter(status=14).count()
    onefive_count=hist.filter(status=15).count()
    onesix_count=hist.filter(status=16).count()         
    total_onestatus= one_status=Shipment.objects.using('local_ecomm').filter(added_on__year=int(yesterday.year),added_on__month=int(yesterday.month),added_on__day=int(yesterday.day)).count()
    u=("TOTAL",total_onestatus,two_status,three_status,four_status,five_status,six_status,int(onefour_count),int(onefive_count),int(onesix_count))
    download_list.append(u)
    sheet = book.add_sheet('Bagging Inscan Report')
    sheet.write(6, 1, "Service Center", style=header_style)
    sheet.write(6, 2, "Soft data up loaded count", style=header_style)
    sheet.write(6, 3, "inscan operation completion", style=header_style)
    sheet.write(6, 4, "added to bag(service centre)", style=header_style)
    sheet.write(6, 5, "debag shipment(hub)", style=header_style)
    sheet.write(6, 6, "added to bag(hub)", style=header_style)
    sheet.write(6, 7, "debag shipment(delivery centre)", style=header_style)
    sheet.write(6, 8, "connected to destination(airport confirm from sc)", style=header_style)
    sheet.write(6, 9, "connected to destination(airport confirm from hub)", style=header_style)
    sheet.write(6, 10, "comments", style=header_style)
    datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
    style = datetime_style
    for row, rowdata in enumerate(download_list, start=7):
         sheet.write(row, 0, style=style)
         for col, val in enumerate(rowdata, start=1):
                        sheet.write(row, col, str(val), style=style)

    file_name="/bagging_inscan_report_%s.xls"%(now.strftime("%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    book.save(path_to_save)
    dest="/home/web/ecomm.prtouch.com/ecomexpress/static/uploads%s"%(file_name)
    f=open(dest,"r")
    high_val_content = f.read()
    f.close()
    filename = dest.split('uploads/')
    attach = MIMEApplication(high_val_content, 'xls')
    attach.add_header('Content-Disposition', 'attachment', filename = filename[1])
    #to_email=("onkar@prtouch.com")
    to_email=("krishnanta@ecomexpress.in","satyak@ecomexpress.in",'sanjeevs@ecomexpress.in','manjud@ecomexpress.in','sravan@ecomexpress.in','jaideeps@ecomexpress.in',"onkar@prtouch.com","jaideeps@ecomexpress.in")
    s = smtplib.SMTP('i.prtouch.com', 26)
    for a in to_email:
        msg = MIMEMultipart()
        msg['Subject']= 'Bagging  Inscan Report'
        msg['From'] = "Reports <jignesh@prtouch.com>"
        plain_test_part = MIMEText("Dear Team, \nPlease find  attached Bagging Inscan Report. \n\nRegards\n\nSupport Team", 'plain')
        msg.attach(plain_test_part)
        msg.attach(attach)
        msg['To']=a
        s.sendmail(msg['From'] , msg['To'], msg.as_string())
    s.quit()

bagging_report()
 
