import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
from service_centre.models import *
from billing.views import *

import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives


import datetime

now = datetime.datetime.now()
before = now - datetime.timedelta(days=1)
request = None

bags = Bags.objects.filter(added_on__gte = before, added_on__lt = now, bag_status__gte=1)
f = open("/tmp/bag_details-2014-02-13","w")  
f.write("Bag No\tHub\tDest\tRuncode\tFlight num\tFlight Departure\tDC Inscan\tno of Shipments\n")
for b in bags:
    con = b.connection_set.all().order_by("-added_on")
    if con:
        con = con[0]
        print con
    else:
        con = ""
    if con:
        runcode = con.runcode_set.all()
    else: runcode=[]
    if runcode: 
        runcode = runcode[0]
        runcode_id = runcode.id
    else: 
        runcode = ""
        runcode_id = ""
    f.write("%d\t%s\t%s\t%s\t"%  (b.id,b.hub, b.destination, runcode_id ))
    if runcode:
        for ac in runcode.airportconfirmation_set.all():
            f.write("%s " %  (ac.flight_num))    
    f.write("\t")
    if runcode:    
        for ac in runcode.airportconfirmation_set.all():
            f.write("%s " %  (ac.atd))
    f.write("\t%s\t%d" % (b.updated_on,b.ship_data.count()))
    f.write("\n")    


subject = "Bag Details"
email_msg = "Please find the link below for today`s Bag Report \n %s"%(msr_path)
to_email = ("jaideeps@ecomexpress.in",  "jignesh@prtouch.com", "onkar@prtouch.com", "jinesh@prtouch.com")
#to_email = ("samar@prtouch.com",)
from_email = "support@ecomexpress.in"
send_mail(subject,email_msg,from_email,to_email)
 
