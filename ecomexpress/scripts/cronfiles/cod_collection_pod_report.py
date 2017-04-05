import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from django.core.mail import send_mail
from reports.cod_collection_pod_report import CodCollectionPodReport
from reports.report_api import  generate_zip
from reports.ecomm_mail import ecomm_send_attach_mail, ecomm_send_mail

def main():
    yester_day = datetime.date.today() - datetime.timedelta(days=1)

    date_from = yester_day.strftime('%Y-%m-%d')
    date_to = yester_day.strftime('%Y-%m-%d')
    xml_report = CodCollectionPodReport(date_from, date_to)
    xml_file_name = xml_report.create_xml_report()
    xml_to_email = ("jinesh@prtouch.com",  "murarikp@ecomexpress.in")
    xml_file_link = "http://billing.ecomexpress.in/static/uploads/reports/"+xml_file_name
    ecomm_send_mail('COD Collection POD XML Report', xml_file_link, xml_to_email)

    if yester_day.weekday() == 5: # dont send report on sunday
        sys.exit(0)
    elif yester_day.weekday() == 6: # on monday send report for both saturday and sunday
        date_from = yester_day - datetime.timedelta(days=1)
        date_from = date_from.strftime('%Y-%m-%d')
        date_to = yester_day.strftime('%Y-%m-%d')
    else:
        date_from = yester_day.strftime('%Y-%m-%d')
        date_to = yester_day.strftime('%Y-%m-%d')

    report = CodCollectionPodReport(date_from, date_to)
    file_name = report.generate_report()

    to_email = ("jinesh@prtouch.com", "nareshb@ecomexpress.in", 
                      "jignesh@prtouch.com", "karishmar@ecomexpress.in", "murarikp@ecomexpress.in","samar@prtouch.com",'arun@prtouch.com')
    ecomm_send_attach_mail('COD Collection POD Report', file_name, to_email)
    
main()
