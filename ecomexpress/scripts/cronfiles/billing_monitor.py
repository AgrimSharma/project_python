import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')


from billing.provisional_billing import process_provisional_billqueue
from billing.generate_bill import process_billqueue

#process_provisional_billqueue()
process_billqueue()
