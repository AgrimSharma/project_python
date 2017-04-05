# Create your views here.

import os
import sys

PROJECT_ROOT_DIR = '/home/web/ecomm.prtouch.com/ecomexpress/'
os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

import datetime
import fileinput
import sys
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from django.core.servers.basehttp import FileWrapper

from service_centre.models import *
from privateviews.decorators import login_not_required
# from api.utils import api_auth

today = datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d")

@login_not_required
@csrf_exempt
def get_pincodes_txt(request):
    q = Q()
    date_range = (datetime.date.today() - datetime.timedelta(days=700))
    '''
    if request.POST:
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")
        if request.POST.get("date"): 
            if not validate_date(request.POST.get("date")): 
                return HttpResponse("%s"%"invalid date field")
            q = q & Q(added_on__gte = request.POST.get("date"))
        if request.POST.get("state"): 
            q = q & Q(service_center__city__state__state_shortcode = request.POST.get("state"))
        capi =  api_auth(request)
    '''
    entry_string= ''
    complete=[]
    location = Pincode.objects.filter(status=1).values("pincode", "service_center__city__city_name", "service_center__city__city_shortcode", "service_center__center_shortcode",  "service_center__city__state__state_name", "service_center__city__state__state_shortcode", "date_of_discontinuance", "pin_route__pinroute_name")
    x = 0
    for l in location:
        srecords = {'pincode':l['pincode'],"city":l['service_center__city__city_name'],"state":l['service_center__city__state__state_name'],"city_code":l['service_center__city__city_shortcode'],"dccode":l['service_center__center_shortcode'],"state_code":l['service_center__city__state__state_shortcode'],"date_of_discontinuance":l['date_of_discontinuance'],"route":l['pin_route__pinroute_name']}
	x+=1
	# <Entry>IN,380051|AMD,AMDD,X01</Entry>
	entry = ['IN', l['pincode'], '|',l['service_center__city__city_shortcode'],l['service_center__center_shortcode'],l['service_center__city__state__state_shortcode']]
	complete.append(entry)
    if not complete == []:
	for i in complete:
            string = '\t'*4+'<Entry>'
	    string+=(','.join(str(j) for j in i[:2]))
	    string+='|'
	    # string+=str(i[4])
	    string+=(','.join(str(j) for j in i[3:]))
	    if complete.index(i) == len(complete) - 1:
	        string+=('</Entry>')
	    else:
		string+=('</Entry>\n')
	    entry_string+=string
    else:
        entry_string+="Currently no entries in the database"
   
    file_name = today+".Default.XXXIN.RouteFile.txt"
    # date format: 2014-08-13T01:00:00Z
    time_string = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
    # return HttpResponse(entry_string)
    file_path = PROJECT_ROOT_DIR + 'static/uploads/outfile.txt'
    template_path = os.path.dirname(os.path.abspath(__file__)) 
    
    with open(file_path, 'w') as outfile:
	# "Ensure file RF.txt is in the same folder as views.py".
	try:
	    for line in fileinput.input(template_path+'/RF.txt'):
            	# outfile.write(line.replace('TiMe HeRe', time_string))
            	line = line.replace('TiMe HeRe', time_string)
            	line = line.replace('Entries HeRe', entry_string)
            	outfile.write(line)
    	except:
	    HttpResponse("Template not found, or error writing to template.")

    filed = FileWrapper(file(file_path))

#    return HttpResponse('outfile.txt', content_type="text")
    response =  HttpResponse(filed, content_type="application/text")
    response['Content-Disposition'] = 'attachment; filename="'+file_name+'"'
    return response

def amazon_manifest(request):
    from utils2 import map_shipment
    filed = map_shipment()
    return HttpResponse(filed)
    response =  HttpResponse(filed, content_type="application/text")
    response['Content-Disposition'] = 'attachment; filename="'+file_name+'"'
    return response


