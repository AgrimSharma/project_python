import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from django.db.models import Q
from service_centre.models import Shipment, Order_price, CODCharge

today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)


def update_ebs_prices(start_date, end_date):
    Order_price.objects.filter(
        Q(shipment__shipment_date__range=(start_date, end_date)), 
        Q(freight_charge__gt=1) | Q(valuable_cargo_handling_charge__gt=0), 
        Q(shipment__airwaybill_number__startswith=3) |
        Q(shipment__airwaybill_number__startswith=4)
    ).update(
        freight_charge=1, 
        fuel_surcharge=0, 
        valuable_cargo_handling_charge=0, 
        to_pay_charge=0, 
        rto_charge=0, 
        sdd_charge=0, 
        sdl_charge=0, 
        reverse_charge=0, 
        tab_charge=0
    )
    CODCharge.objects.filter(
        Q(shipment__shipment_date__range=(start_date, end_date)),
        Q(cod_charge__gt=0),
        Q(shipment__airwaybill_number__startswith=3) |
        Q(shipment__airwaybill_number__startswith=4)
    ).update(cod_charge=0)

start_date = yesterday.strftime('%Y-%m-01')
end_date = today.strftime('%Y-%m-%d')
update_ebs_prices(start_date, end_date)
