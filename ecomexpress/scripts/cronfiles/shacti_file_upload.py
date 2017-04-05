import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from shacti_api.update_dc_shipments import upload_dc_shipments

upload_dc_shipments()
