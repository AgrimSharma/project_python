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
from hub.models import *
from datetime import datetime, time, date, timedelta
from django.db.models import Q
import settings
import csv

def generate_overage_report(date_uploading_from=None, date_uploading_to=None, cur_sc_id=None):
    report = ReportGenerator('overage_report.xlsx')
#    file_name = "/overage_report.csv"
#    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
#    csv_out = open(path_to_save,"wb")
#    mywriter = csv.writer(csv_out)
    today = datetime.today()
    col_heads = ('AWB',
        'Inscan Date', 
        'Current SC',
        'Destination', 
        'Scanned Bag Number',
         'Original Bag Number')
#    mywriter.writerow(col_heads)
    report.write_header(col_heads)
    q = Q()
    if date_uploading_from:
       date_uploading_from=date_uploading_from
    if date_uploading_to:
       date_uploading_to=date_uploading_to
    else:
       date_uploading_to=today
    q = Q(added_on__gte=date_uploading_from, added_on__lte=date_uploading_to)
    print date_uploading_to,date_uploading_from
    #if date_uploading_from and date_uploading_to:
    #   q = Q(added_on__gte=date_uploading_from, added_on__lte=date_uploading_to)
    if cur_sc_id:
       q = Q(current_sc = cur_sc_id)
#   mywriter.writerow([q])
    print q
#    if destination_id == 0:
#        bag_ship = Bag_shipment_table.objects.filter(added_on = date_uploading)
#    else:
#        bag_ship = Bag_shipment_table.objects.filter(added_on = date_uploading,current_sc=destination_id)
    bag_ship = Bag_shipment_table.objects.filter(q)
    print bag_ship
    for b_sh in bag_ship:
     if b_sh.scanned_bag_number and b_sh.original_bag_number:   
        if b_sh.scanned_bag_number.lower() != b_sh.original_bag_number.lower():
        	ship = Shipment.objects.get(airwaybill_number = b_sh.airwaybill_number)
                print "insert to row"
                row =(ship.airwaybill_number,b_sh.added_on,b_sh.current_sc,ship.original_dest.center_shortcode,b_sh.scanned_bag_number,b_sh.original_bag_number)
#                mywriter.writerow(row)
                report.write_row(row)
    file_name = report.manual_sheet_close()
    return file_name



def generate_shortage_report_old(date_uploading_from=None, date_uploading_to = None, cur_sc_id=None):
    q = Q()
    name=datetime.now().strftime('%d%m%Y%H%M%S%s')
    report=ReportGenerator('shortage_Report_{0}.xlsx'.format(name))
    #report = ReportGenerator('shortage_report.xlsx')
    col_heads = ('AWB',
        'Inscan Date',
        'Origin',
        'Destination',
        'Bag Number',)
    report.write_header(col_heads)
    if date_uploading_from and date_uploading_to:
       q = Q(added_on__gte=date_uploading_from, added_on__lte=date_uploading_to)
    if int(cur_sc_id):
       q = Q(current_sc = cur_sc_id)
    #    bag_ship = Bag_shipment_table.objects.filter(added_on = date_uploading)
    #else:
    #    bag_ship = Bag_shipment_table.objects.filter(added_on = date_uploading,current_sc=destination_id)
    bag_ship = Bag_shipment_table.objects.filter(q)
    awb_dic ={}
    data=[]
    for b_sh in bag_ship:
        bags = Bags.objects.filter(bag_number =b_sh.scanned_bag_number)
        for bag in bags:
            ships = bag.shipments.all()
            for ship in ships:
		print "found ships"
                li = Bag_shipment_table.objects.filter(airwaybill_number = ship.airwaybill_number)
                if not li:
                    print "fount"
                    if ship.airwaybill_number in awb_dic:
                        print "already added"
                    else:
                        awb_dic[ship.airwaybill_number]=ship.airwaybill_number
                        print "insert to row"
                        row =(ship.airwaybill_number,b_sh.added_on,b_sh.current_sc,ship.original_dest.center_shortcode,b_sh.scanned_bag_number)
                        data.append(row)
                        #report.write_row(row)
    file_name=report.write_body(data)
    #file_name = report.manual_sheet_close()
    return file_name

def generate_shortage_report_tmp(date_uploading_from=None, date_uploading_to = None, cur_sc_id=None):
   q=Q()
   if date_uploading_from and date_uploading_to:
         q = Q(added_on__gte=date_uploading_from, added_on__lte=date_uploading_to)
   if int(cur_sc_id):
        q = Q(current_sc = cur_sc_id)

   name=datetime.now().strftime('%d%m%Y%H%M%S%s')
   report=ReportGenerator('shortage_report_{0}.xlsx'.format(name))
   col_heads = ('AWB','Inscan Date','Current SC','Destination','Scanned Bag Number','Original Bag Number')
   report.write_header(col_heads)
   data = []
   tmp =0
   count = 0
   bag_ship = Bag_shipment_table.objects.filter(q).values('added_on','current_sc','original_bag_number','scanned_bag_number','airwaybill_number')
   print bag_ship.count()
   name=datetime.now().strftime('%d%m%Y%H%M%S%s')
   print name
   for b in bag_ship:
       if isinstance( b['original_bag_number'], int ):
           original_bag = b['original_bag_number']
       else :
          if b['original_bag_number'] is not  None:
             original_bag = b['original_bag_number'][3:]
          else:
             original_bag = ""
       if isinstance( b['scanned_bag_number'], int ):
          scanned_bag_number = scanned_bag_number
       else:
          if b['scanned_bag_number'] is not  None :
             scanned_bag_number = b['scanned_bag_number'][3:]
          else:
            scanned_bag_number = "" 
       if   original_bag <> scanned_bag_number:
            ship=Shipment.objects.get(airwaybill_number = b['airwaybill_number'])
            sc= ServiceCenter.objects.get(id=b['current_sc'])
            if b['original_bag_number'] is not  None and b['scanned_bag_number'] is not  None :
                u = (b['airwaybill_number'],b['added_on'],sc.center_shortcode,ship.original_dest.center_shortcode,b['scanned_bag_number'],b['original_bag_number'])
                data.append(u) 
       if tmp == 1000:
          tmp = 0
          count = count + 1
          print "tmp is 100",count * 1000
       else:
          tmp = tmp + 1    
   file_name=report.write_body(data)
   print datetime.now().strftime('%d%m%Y%H%M%S%s')
   print file_name    
   return file_name


def generate_shortage_report(date_uploading_from=None, date_uploading_to = None, cur_sc_id=None):
   q=Q()
   if date_uploading_from:
      date_uploading_from = date_uploading_from + " 00:00:01"
   else :
      date_uploading_from = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   if date_uploading_to :
      date_uploading_to = date_uploading_to + " 23:59:59"
   else:
       date_uploading_to = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   q = q & Q(updated_on__range=(date_uploading_from,date_uploading_to))
   #if date_uploading_from and date_uploading_to:
   #      q = q & Q(updated_on__range=(date_uploading_from,date_uploading_to))
   if int(cur_sc_id):
        q = q & Q(bag_sc_id = cur_sc_id)
        #q = q & Q(destination_id = cur_sc_id)
  
   name=datetime.now().strftime('%d%m%Y%H%M%S%s')
   report=ReportGenerator('Shortage_Report_{0}.xlsx'.format(name))
   col_heads = ('AWB','Shipment Inscan Date','Current SC','Destination',' Bag Number','Bag Inscan')
   report.write_header(col_heads)
   data = []
   tmp =0
   count = 0 
   tmps  =  date_uploading_from.split('-')
   tmp = tmps[0]+"_"+tmps[1]
   history=get_model('delivery','BaggingHistory_%s'%(tmp))
   #hist=history.objects.filter(q).values('bag').distinct()
   hist=history.objects.filter(q,status__in=[7,9,10]).values('bag').distinct()
   bags=[]
   for h in hist:
       bags.append(h['bag'])
   #bags = set(bags)
   #bag_ship = Bags.objects.filter(q,bag_status=4)
   #bag_ship = Bag_shipment_table.objects.filter(q).values('added_on','current_sc','original_bag_number','scanned_bag_number','airwaybill_number')
   print hist.count(),len(bags)
   tmps  =  date_uploading_to.split('-')
   tmp = tmps[0]+"_"+tmps[1]
   history=get_model('delivery','BaggingHistory_%s'%(tmp))
   hist=history.objects.filter(q,status__in=[7,9,10]).values('bag').distinct()
   #hist=history.objects.filter(q,status__in=[9,10]).values('bag','updated_on').distinct()
   #print hist[0],hist.count()
   for h in hist:
      bags.append(h['bag'])
   bags=set(bags)
   #print len(bags)
   ships= []
   mycount =0
   for b in bags:
      bg=Bags.objects.filter(id=b)
      if bg :
        for s in bg[0].shipments.all():
           ships.append(s.airwaybill_number)
           u = (s.airwaybill_number,s.added_on.strftime("%d-%m-%Y %H:%M"),s.current_sc.center_shortcode,s.original_dest.center_shortcode,bg[0].bag_number,bg[0].added_on.strftime("%d-%m-%Y %H:%M"))
           data.append(u)
   iTmp= 0
   print len(ships)
   #for s in ships:
   #   u = (s.airwaybill_number,s.added_on.strftime("%d-%m-%Y %H:%M"),s.current_sc.center_shortcode,s.original_dest.center_shortcode,b.bag_number,b.added_on.strftime("%d-%m-%Y %H:%M"))
   #   data.append(u)
   file_name=report.write_body(data)
   ##print file_name
   return file_name
   ships = set(ships)
   #print "my count is",len(ships)
   return  "hi"
   for b in bags:
       bg = Bags.objects.get(id=b)
       for s in bg.ship_data.all():
         #print s
         ships.append(s.airwaybill_number)
         print s.airwaybill_number
         if mycount == 10:
           return "hi"
         else:
            mycount = mycount + 1
   print len(ships)
   ships = set(ships)
   print len(ships)
   return "hi"
   name=datetime.now().strftime('%d%m%Y%H%M%S%s')
   print name
   for b in bag_ship:
         ships=b.ship_data.filter(status=5)
         for s in ships:
            if not s.shipment_data.filter(added_on__gt = b.added_on):
                u = (s.airwaybill_number,s.added_on.strftime("%d-%m-%Y %H:%M"),s.current_sc.center_shortcode,s.original_dest.center_shortcode,b.bag_number,b.added_on.strftime("%d-%m-%Y %H:%M"))
                data.append(u)

   file_name=report.write_body(data)
   print datetime.now().strftime('%d%m%Y%H%M%S%s')
   print file_name
   return file_name
#shortage_report()i

#generate_shortage_report("2014-07-21","2014-07-22",0)
