import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

#from reports.sunday_delivery import generate_sunday_report
from reports.daily_delivery import generate_sunday_report
from reports.ecomm_mail import ecomm_send_mail
from reports.run_code import *
#from reports.run_code_rev import *
def main():
    today = datetime.date.today()

    file_name = generate_sunday_report()
    file_name = "http://billing.ecomexpress.in/static/uploads/reports/"+str(file_name)
    print file_name
    to_email = ("krishnanta@ecomexpress.in", "satyak@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in", "jitendrad@ecomexpress.in", "jaideeps@ecomexpress.in", "jinesh@prtouch.com", "nareshb@ecomexpress.in","onkar@prtouch.com", "arun@prtouch.com", "sravan@ecomexpress.in")
#    to_email = ("arun@prtouch.com","jinesh@prtouch.com","onkar@prtouch.com")
#    ecomm_send_mail('DC Daily Delivery Report', file_name, to_email)

main()
