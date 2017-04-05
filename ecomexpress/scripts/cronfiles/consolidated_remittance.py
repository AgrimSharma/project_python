import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from reports.random_reports import yearly_remittance_report

yearly_remittance_report(dates=('2013-11-01', '2013-12-31'))
yearly_remittance_report(dates=('2013-08-01', '2013-10-31'))
yearly_remittance_report(dates=('2013-05-01', '2013-07-31'))
yearly_remittance_report(dates=('2013-04-01', '2013-06-30'))
yearly_remittance_report(dates=('2013-01-01', '2013-03-31'))
