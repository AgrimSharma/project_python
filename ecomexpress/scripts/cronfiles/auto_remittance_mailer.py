import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from django.conf import settings
import calendar
from reports.unremitted_shipments_report import generate_report_for_selected_customers
from reports.ecomm_mail import ecomm_send_mail
from reports.models import CustomerRemittance
from math import ceil

def week_no(now):
    first_day = now.replace(day=1)

    dom = now.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))

def prev_weekday(d, weekday):
    days_ahead = d.weekday() - weekday
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d - datetime.timedelta(days_ahead)

def remittance():
    now = datetime.datetime.now()
    weekday = now.weekday()
#    week_number = week_no(now)
#    week_number = (now.day - 1) // 7  + 1 
    cr = CustomerRemittance.objects.filter(current_day = weekday).values_list('customer_id', 'to_day')
    remit_dict = {}
    for a in cr:
 #          print a
           to_date = prev_weekday(now, a[1])
           to_date = to_date.date() 
#           week_number = (a[1].day - 1) // 7  + 1
           #to_date = calendar.Calendar(a[1]).monthdatescalendar(now.year, now.month)[week_number][0]
           remit_dict[a[0]] = to_date
    reports = generate_report_for_selected_customers(remit_dict)



    reports_list = [settings.ROOT_URL + 'static/uploads/reports/'+file_name for file_name in reports]
    reports_list_str = '\n'.join(reports_list)
#    to_email = ("samar@prtouch.com",)
    to_email = ("samar@prtouch.com","karishmar@ecomexpress.in", "nareshb@ecomexpress.in", "jignesh@prtouch.com", "jinesh@prtouch.com")
    ecomm_send_mail('Unremitted Shipments Report', reports_list_str, to_email)

if __name__ == '__main__':
    remittance()

# day_dict = {'mon':0, 'tue':1, 'wed':2, 'thu':3, 'fri':4, 'sat':5, 'sun':6}
#for a in cr.split('\n'):
#    val = a.split('q1')
#    cust_code = val[0]
#    val1 = val[1].split('q2')
#    cur = val1[0]
#    to = val1[1]
#    print cust_code, cur, to, day_dict[cur.lower()[:3]]
#    cust_id = Customer.objects.get(code = cust_code).id
#    CustomerRemittance.objects.create(customer_code = cust_code, customer_id = cust_id, current_day = day_dict[cur.lower()[:3]], to_day = day_dict[to.lower()[:3]])


