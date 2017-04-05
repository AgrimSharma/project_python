import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from reports.generic_update import *

today = datetime.datetime.today()
yesterday = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
history_day_update(yesterday)
