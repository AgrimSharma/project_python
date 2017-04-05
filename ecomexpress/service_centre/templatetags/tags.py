'''
Created on Dec 7, 2012

@author: Sirius
'''
from django import template
from track_me.models import *
from django.db.models.loading import get_model
from django.contrib.auth.models import User, Group
import unicodedata
from service_centre.models import *

register = template.Library()
import datetime
from utils import chunks

@register.simple_tag
def active(request, pattern):
    if request.path.startswith(pattern):
        return 'active2'
    return ''

@register.filter
def is_in(var, obj):
    return var in obj

@register.filter    
def subtract(value, arg):
    return value - arg

@register.filter
def ship_serial(awb,oid):
    os = OutscanShipments.objects.get(outscan=oid, awb=awb)
    return os.serial


@register.simple_tag   
def tomorrow():
    now = datetime.datetime.now()
    nextmonth = now + datetime.timedelta(days=1)
    nextmonth = nextmonth.strftime("%Y-%m-%d")
    return nextmonth

@register.simple_tag   
def month():
    
    now = datetime.datetime.now()
    nextmonth = now + datetime.timedelta(days=1)
    nextmonth = nextmonth.strftime("%Y-%m-%d")
    return nextmonth

@register.filter
def instruction(value, arg):
    b = 0
    return 'alert'
    altinstructiawb = InstructionAWB.objects.filter(batch_instruction__shipments__current_sc = arg, status = 0)
    for aawb in altinstructiawb:
            upd_time = aawb.batch_instruction.shipments.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            if shipment_history:
                history = shipment_history.objects.filter(shipment=aawb.batch_instruction.shipments)
                if history:
                    history_latest=history.latest('updated_on')
                    if (history_latest.current_sc == arg) and (history_latest.reason_code==None):
                        b = 1
                     #   inst[a.shipments]=InstructionAWB.objects.get(batch_instruction=a)
    if b == 1:
        return "alert"
    else:
        return ' '            
#        print b
    #if request.path.startswith(pattern):
     #   return 'active2'
    #return ''

@register.filter(name="multiply")  
def multiply(value, arg):
    return value * arg * 1.00

@register.filter
def user_group(request, user):
     group = Group.objects.get(name="Customer Service")
     a=0
     if request.user.groups.filter(name="Customer Service").exists():
            a=1
	    return a
     return ''



@register.filter
def statusupdate_received_by(request, a):
     su = a.statusupdate_set.filter(status=2)
     if su:
        return su[0].recieved_by
     else: 
        return ''

@register.filter
def statusupdate_delivery_time(request, a):
     su = a.statusupdate_set.filter(status=2)
     if su:
        return "%s %s" % (su[0].date,su[0].time)
     else: 
        return ''



@register.filter
def get_statusupdate_sys_delivery_time(airwaybill_number):
     shipment = Shipment.objects.filter(airwaybill_number = airwaybill_number)
     if not shipment :
        return ''
     delivery_status = ""
     shipment = shipment[0]
     if shipment.status == 0: delivery_status="Shipment Uploaded"
     if shipment.status == 1: delivery_status="Pickup Complete / Inscan"
     if shipment.status == 2: delivery_status="Inscan completion / Ready for Bagging"
     if shipment.status == 3: delivery_status="Bagging completed"
     if shipment.status == 4: delivery_status="Shipment at HUB"
     if shipment.status == 5: delivery_status="Bagging Completed at HUB"
     if shipment.status == 6: delivery_status="Shipment at Delivery Centre"
     if shipment.status == 7: delivery_status="Outscan"
     if shipment.status == 8: delivery_status="Undelivered"
     if shipment.status == 9: delivery_status="Delivered / Closed"
     return delivery_status 


@register.filter
def statusupdate_sys_delivery_time(request):
     a = request
     su = a.statusupdate_set.filter(status=2).order_by("-added_on")
     if su:
        return "%s " % (su[0].added_on)
     else: 
        return ''

@register.filter
def add_minimum_spaces(value, size):
     value_len = len(str(value))
     if size > value_len:
        for count in xrange(size):
            if count > value_len:
                value = str(value) + " " 
     return value

@register.filter
def get_unicode(value):
     return unicodedata.normalize('NFKD', value).encode('ascii','ignore')


@register.filter
def address_split_dc(var_to_be_split, split_size):
     split_value_array = chunks(var_to_be_split, split_size)
     split_value_txt = ""
     count = 1 
     for schars in split_value_array: 
        split_value_txt = split_value_txt + "                             " + schars  
        if count < len(split_value_txt):
            split_value_txt = split_value_txt + "\n"
        count = count + 1 
     return split_value_txt

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)


# http://vanderwijk.info/blog/adding-css-classes-formfields-in-django-templates/
@register.filter(name='addcss')
def addcss(field, css):
   return field.as_widget(attrs={"class":css})

@register.filter
def get_fetchawb_status(status):
    
    if status == 0:
        return 'In Queue'
    if status == 1:
        return 'In Process'
    if status == 2:
        return 'Completed'
 
