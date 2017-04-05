import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from reports.generic_update import history_delivered_update

today = datetime.datetime.today()

to_day = today.strftime('%Y-%m-%d')
history_delivered_update(to_day)
