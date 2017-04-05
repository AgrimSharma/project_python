import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from service_centre.models import DeliveryOutscan, outscan_update_for_cash_tally


today = datetime.datetime.now()
yester_day = today - datetime.timedelta(days=1)
start_time = yester_day.strftime('%Y-%m-%d 00:00:00')
end_time = yester_day.strftime('%Y-%m-%d 23:59:59')

outscans = DeliveryOutscan.objects.filter(added_on__range=(start_time, end_time)).values_list('id', flat=True)

for del_id in outscans:
    outscan_update_for_cash_tally(del_id)
