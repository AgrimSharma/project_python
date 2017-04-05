import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from reports.mis_revised import generate_report, generate_by_thread

#generate_report(81044, 67081, 92082, 69087)
#generate_by_thread(81044, 67081, 92082, 69087)
generate_by_thread()
