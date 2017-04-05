import requests
import json
import cgi
import ho.pisa as pisa
import cStringIO as StringIO
from copy import deepcopy
import dateutil.parser
from decimal import Decimal
from xlsxwriter.workbook import Workbook
from collections import OrderedDict

from django.db.models import *
from django.shortcuts import render_to_response
from django.template.loader import render_to_string, get_template
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.template import Context
from django.db.models import datetime, Sum
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.utils import simplejson
from jsonview.decorators import json_view
from service_centre.models import *
from airwaybill.models import *
from delivery.models import (
    DashboardVisiblity, update_bag_history, get_expected_dod,
    cashtally_deliveryoutscan_details, cashtally_shipment_details
)
from datetime import date, timedelta as td
#now = datetime.datetime.now()
#monthdir = now.strftime("%Y_%m")
#before = now - datetime.timedelta(days=3)

@csrf_exempt
def fetch_awb(request):

    now = datetime.datetime.now()
    monthdir = now.strftime("%Y_%m")
    before = now - datetime.timedelta(days=3)
    query_type = int(request.GET.get('query_type'))
    day = int(request.GET.get('day'))
    date = request.GET.get('date')
    sc = request.GET.get('sc')
    counter_date = now.strftime('%Y-%m-%d 04:00:00')
    last_month = nextmonth = now - datetime.timedelta(days=10)
    
    service_centre = ServiceCenter.objects.all()
    selected_sc = ''
    ships = ''
    tenday = now - datetime.timedelta(days=9)
    #d1 = now.date()
    #d2 = tenday.date()
    #return HttpResponse(sc)
    #tenday = now - datetime.timedelta(days=8)
    #sc = request.user.employeemaster.service_centre
    d2 = tenday.date()
    q = Q(reason_code__isnull=True) | ~Q(reason_code__code__in=[777, 999, 888, 333, 310, 200, 208, 302, 311])
    q = q & ~Q(shipper_id = 2)
    if sc:
        if sc != "all":
            q = q & Q(current_sc__center_shortcode = sc)
    elif sc != "all":
        sc = request.user.employeemaster.service_centre
        q = q & Q(current_sc = sc)
    q = q & ~Q(status = 9)
    if query_type == 0:
        q = q & Q(status = 0) 
    if query_type == 1:
        q = q & Q(status__in = [1,2])
    if query_type == 2:
        q = q & Q(status = 8) 
    if query_type == 3:
        q = q & Q(status__in = [3,5]) 
    if query_type == 4:
        q = q & Q(reason_code_id__in = [38,40]) & ~Q(status__in = [3,5])
    if query_type == 5:
        q = q & Q(status = 7) 
    if query_type == 6:
        q = q & Q(reason_code_id = 24)
    if query_type == 7:
        q = q & Q(status__in = [4,6]) 
    if query_type == 8:
        q = q & Q(rts_status = 1) 
   #if query_type == 9:
   #    q = q & Q(status = 0) 

    if request.POST.get("rts"):
        if request.POST.get("rts") == "1":
            q = q & Q(rts_status  = 1)
        else:
            q = q & ~Q(rts_status  = 1)
    else:
       q = q & ~Q(rts_status  = 1)

    if date:
        if request.POST.get("date_type"):
            if request.POST.get("date_type") == "1":
                q = q & Q(added_on__gte = date,added_on__lte = date + " 23:59:59")
            else:
                q = q & Q(updated_on__gte = date,updated_on__lte = date + " 23:59:59")
        else:
            q = q & Q(updated_on__gte = date,updated_on__lte = date + " 23:59:59")
        #return HttpResponse(q)

    #return HttpResponse(q)

    if day == 10: 
        if request.POST.get("date_type"):
            if request.POST.get("date_type") == "1":
                q_null_date = Q(added_on__isnull = True) | Q(added_on__lte = d2)
            else:
                q_null_date = Q(updated_on__isnull = True) | Q(updated_on__lte = d2)
        else:
            q_null_date = Q(updated_on__isnull = True) | Q(updated_on__lte = d2)

        q = q & q_null_date
    #q_less_tenday_null = Q(updated_on__lt = d2) | Q(updated_on__isnull = True)
    #q_less_tenday = q & q_less_tenday_null


    ships = Shipment.objects.filter(q).values_list('airwaybill_number', 'current_sc__center_shortcode', 'updated_on').order_by("updated_on")
    #return HttpResponse("%s, %s" % (ships.query, query_type))
#   #Soft Data Uploaded
#   if query_type == "1":
#       query_tenday = q_tenday & Q(status = 0)
#       #return HttpResponse(query_tenday)
#       ships = Shipment.objects.filter(query_tenday).values_list('airwaybill_number', 'current_sc__center_shortcode', 'updated_on')
#       #return HttpResponse(ships)
#   if query_type == "2":
#       query_total = q & Q(status = 0)
#       ships = Shipment.objects.filter(query_total).values_list('airwaybill_number', 'current_sc__center_shortcode', 'updated_on')
#   if query_type == "0":
#       query_beyond_tenday = q_less_tenday & Q(status = 0)
#       ships  = Shipment.objects.filter(query_beyond_tenday).values_list('airwaybill_number', 'current_sc__center_shortcode', 'updated_on')
    return render_to_response("delivery/monitoring_dashboard_sc.html",
                              {'ships': ships,
                               'q': q,
                              }, context_instance=RequestContext(request)) 

@csrf_exempt
def dashboard(request):
    
    now = datetime.datetime.now()
    monthdir = now.strftime("%Y_%m")
    before = now - datetime.timedelta(days=3)
    counter_date = now.strftime('%Y-%m-%d 04:00:00')
    last_month = nextmonth = now - datetime.timedelta(days=10)
    #sc = cluster_based_sc(request)
    sc = request.user.employeemaster.service_centre
    if request.POST.get("sc"):
        center = ServiceCenter.objects.filter(center_shortcode = request.POST.get("sc"))
        if center:
            sc = center[0]

    tenday = now - datetime.timedelta(days=9)
    d1 = now.date()
    d2 = tenday.date()
    #return HttpResponse("%s,%s" % (d1, d2))
    service_centre = ServiceCenter.objects.all()
    selected_sc = ''
    q = Q(reason_code__isnull=True) | ~Q(reason_code__code__in=[777, 999, 888, 333, 310, 200, 208, 302, 311])
    q = q & ~Q(shipper_id = 2)

    if not request.POST.get("all") and not request.POST.get("sc"):
        q = q & Q(current_sc = sc)
    if request.POST.get("sc"):
        selected_sc = request.POST.get("sc")
        if  request.POST.get("sc") != "all":
            q = q & Q(current_sc__center_shortcode = request.POST.get("sc") )

    qrts = ~Q(rts_status=1)
    if request.POST.get("rts"):
        #return HttpResponse("%s ----<br>" % (request.POST.get("rts")))
        if request.POST.get("rts") == "1":
            qrts = Q(rts_status=1)

    q = q & qrts
    q = q & ~Q(status = 9)

    q_tenday_date = Q(updated_on__gte = d2)
    q_less_tenday_null = Q(updated_on__lt = d2) | Q(updated_on__isnull = True)
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            q_tenday_date = Q(added_on__gte = d2) | Q(added_on__isnull = True)
            q_less_tenday_null = Q(added_on__lt = d2) | Q(added_on__isnull = True)

    q_tenday = q & q_tenday_date
    q_less_tenday = q & q_less_tenday_null

    #return HttpResponse("%s<br> %s<br> %s" % (q,q_tenday,q_less_tenday))

    #Soft Data Uploaded
    query_tenday = q_tenday & Q(status = 0)
    ships_softdata_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_softdata_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q & Q(status = 0)
    ships_softdata_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday & Q(status = 0)
    ships_softdata_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))
 
    #return HttpResponse("%s" % ships_softdata_total)
    #scan
    query_tenday = q_tenday & Q(status__in = [1,2])
    ships_scan_cc_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_scan_cc_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q & Q(status__in = [1,2])
    ships_scan_cc_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday & Q(status__in = [1,2])
    ships_scan_cc_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))
    

    #Failed
    query_tenday = q_tenday & Q(status = 8)
    ships_failed_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_failed_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q & Q(status = 8)
    ships_failed_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday & Q(status = 8)
    ships_failed_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))
    
    #Bagged
    query_tenday = q_tenday & Q(status__in = [3,5])
    ships_bagged_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_bagged_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q & Q(status__in = [3,5])
    ships_bagged_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday & Q(status__in = [3,5])
    ships_bagged_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))

    #Misrouted
    query_tenday = q_tenday & Q(reason_code_id__in = [38,40]) & ~Q(status__in = [3,5])
    ships_misrouted_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_misrouted_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q & Q(reason_code_id__in = [38,40])
    ships_misrouted_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday & Q(reason_code_id__in = [38,40])
    ships_misrouted_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))

    #Outscan
    query_tenday = q_tenday & Q(status = 7)
    ships_outscan_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_outscan_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q & Q(status = 7)
    ships_outscan_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday & Q(status = 7)
    ships_outscan_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))

    #Inscan
    query_tenday = q_tenday & Q(status = 6)
    ships_inscan_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_inscan_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q & Q(status = 6)
    ships_inscan_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday & Q(status = 6)
    ships_inscan_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))

    #Consignee Refused
    query_tenday = q_tenday & Q(reason_code_id = 24)
    ships_refused_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_refused_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q & Q(reason_code_id = 24)
    ships_refused_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday & Q(reason_code_id = 24)
    ships_refused_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))
    
    #Requeued
    query_tenday = q_tenday & Q(rts_status = 1)
    ships_requeued_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_requeued_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q & Q(rts_status = 1)
    ships_requeued_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday & Q(rts_status = 1)
    ships_requeued_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))
    #yet to scan
 
    #total
    query_tenday = q_tenday 
    ships_total_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( updated_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    if request.POST.get("date_type"):
        if request.POST.get("date_type") == "1":
            ships_total_tenday = Shipment.objects.filter(query_tenday).extra(select={'day': 'date( added_on )'}).values('day').annotate(count=Count('airwaybill_number'))
    query_total = q 
    ships_total_total  = Shipment.objects.filter(query_total).aggregate(count=Count('airwaybill_number'))
    query_beyond_tenday = q_less_tenday 
    ships_total_beyond_ten  = Shipment.objects.filter(query_beyond_tenday).aggregate(count=Count('airwaybill_number'))
 
    #return HttpResponse("%s" % ships_total_total.query)

    day_list = [10,9,8,7,6,5,4,3,2,1,0]
    date_list = []
    delta = d1-d2
    #date_list.append(d2)
    for i in range(delta.days+1):
        date_list.append(d2 + td(days=i))

    date_list = date_list[ : : 1]
    monitor_counts = ""
    state = ""
    return render_to_response("delivery/monitoring_dashboard.html",
                                   {'monitor_counts':monitor_counts,
                                    'ships_failed_tenday':ships_failed_tenday,
                                    'ships_failed_total':ships_failed_total,
                                    'ships_failed_beyond_ten':ships_failed_beyond_ten,

                                    'ships_bagged_tenday':ships_bagged_tenday,
                                    'ships_bagged_total':ships_bagged_total,
                                    'ships_bagged_beyond_ten':ships_bagged_beyond_ten,

                                    'ships_misrouted_tenday':ships_misrouted_tenday,
                                    'ships_misrouted_total':ships_misrouted_total,
                                    'ships_misrouted_beyond_ten':ships_misrouted_beyond_ten,

                                    'ships_outscan_tenday':ships_outscan_tenday,
                                    'ships_outscan_total':ships_outscan_total,
                                    'ships_outscan_beyond_ten':ships_outscan_beyond_ten,

                                    'ships_inscan_tenday':ships_inscan_tenday,
                                    'ships_inscan_total':ships_inscan_total,
                                    'ships_inscan_beyond_ten':ships_inscan_beyond_ten,

                                    'ships_refused_tenday':ships_refused_tenday,
                                    'ships_refused_total':ships_refused_total,
                                    'ships_refused_beyond_ten':ships_refused_beyond_ten,

                                    'ships_requeued_tenday':ships_requeued_tenday,
                                    'ships_requeued_total':ships_requeued_total,
                                    'ships_requeued_beyond_ten':ships_requeued_beyond_ten,

                                    'ships_softdata_tenday':ships_softdata_tenday,
                                    'ships_softdata_total':ships_softdata_total,
                                    'ships_softdata_beyond_ten':ships_softdata_beyond_ten,

                                    'ships_scan_cc_tenday':ships_scan_cc_tenday,
                                    'ships_scan_cc_total':ships_scan_cc_total,
                                    'ships_scan_cc_beyond_ten':ships_scan_cc_beyond_ten,

                                    'ships_total_tenday':ships_total_tenday,
                                    'ships_total_total':ships_total_total,
                                    'ships_total_beyond_ten':ships_total_beyond_ten,

                                    'day_list':day_list ,
                                    'date_list':date_list ,
                                    'state':state,
                                    'service_centre': service_centre,
                                    'q': q_tenday,
                                    'selected_sc': selected_sc },
                                    context_instance=RequestContext(request))
