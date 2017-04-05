import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

#from reports.mis_report_jasper import generate_report
from reports.mis_revised import generate_report

generate_report(92006)
