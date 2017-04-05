import os
import sys

# Setup environ
os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import *
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
import datetime

now = datetime.datetime.now()
before = now - datetime.timedelta(days=1)

def high_value_shipments():
    shipments=Shipment.objects.filter(status__in = [6,7,8],return_shipment=0).exclude(rts_status=2).exclude(rts_status=1).exclude(rto_status=1).exclude(reason_code_id=1)
    morethan200=[]
    morethan100=[]
    for a in shipments:
        try:
            if a.codcharge_set.get().cod_charge > 100 :
                if a.codcharge_set.get().cod_charge > 200 :
                    u=(a.airwaybill_number,a.shipper,a.added_on,a.original_dest,a.reason_code,a.current_sc,a.codcharge_set.get().cod_charge)
                    morethan200.append(u)
                v=(a.airwaybill_number,a.shipper,a.added_on,a.original_dest,a.reason_code,a.current_sc,a.codcharge_set.get().cod_charge) 
                morethan100.append(v)   
        except:        
            pass
    print "100",len(morethan100),"200",len(morethan200)    
    subject200 = "High Value Shipments > 200 "
    email_msg_200 = "Given below are high value shipments with COD charge > 200:\n"+"\n".join(['%s, %s, %s, %s, %s, %s, %s' % (a[0], a[1], a[2], a[3],a[4],a[5],a[6]) for a in morethan200])
    
    subject100="High Value Shipments > 100 "
    email_msg_100= "Given below are high value shipments with COD charge > 100:\n"+"\n".join(['%s, %s, %s, %s, %s, %s, %s' % (a[0], a[1], a[2], a[3],a[4],a[5],a[6]) for a in morethan100])
    
    
    from_email = "support@ecomexpress.in"
    #to_email =  "onkar@prtouch.com"
#    to_email=("jignesh@prtouch.com", "onkar@prtouch.com","sanjeevs@ecomexpress.in","krishnanta@ecomexpress.in","manjud@ecomexpress.in","satyak@ecomexpress.in","sravank@ecomexpress.in","anila@ecomexpress.in")
    send_mail(subject200,email_msg_200,from_email,[to_email])
    send_mail(subject100,email_msg_100,from_email,[to_email])

high_value_shipments()
