import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
import settings

import smtplib, os
import datetime
from pickup.models import *

#def pickup_weekday():
#pass

a = datetime.datetime.today().weekday()
pickup_weekday = PickupScheduleWeekdays.objects.filter(weekday=a+1, status = 0)

for a in pickup_weekday:
    if datetime.datetime.now() < a.pickupscheduler.schedule_uptil:
       #  if not PickupSchedulerRegistration.objects.filter(subcustomer_code = a.pickupscheduler.subcustomer_code, service_centre = a.pickupscheduler.service_centre, status=0):
              PickupSchedulerRegistration.objects.create(pickup_scheduler = a.pickupscheduler, subcustomer_code = a.pickupscheduler.subcustomer_code, pieces = a.pickupscheduler.pieces, pickup_date = datetime.datetime.now().date(), pickup_time = a.pickupscheduler.pickup_time, service_centre = a.pickupscheduler.service_centre)
