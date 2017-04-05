import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from customer.models import Product
from service_centre.models import Shipment, ShipmentExtension
from billing.special_billing import (jasper_jammu, jasper_rts, 
    jasper_rts_frt_update, vector_ecomm_rts, actolingerie_update, dealskart_update, 
    tv18_updates_stage1, tv18_updates_stage2)


today = datetime.date.today()
yester_day = today - datetime.timedelta(days=1)

to_date = today.strftime('%Y-%m-%d')
from_date = yester_day.strftime('%Y-%m-%d')

#jasper_jammu(from_date, from_date)
#jasper_rts(from_date, from_date)
#jasper_rts_frt_update(from_date, from_date)
#vector_ecomm_rts('2014-07-01', '2014-07-28')
actolingerie_update(from_date, from_date)
dealskart_update(from_date, from_date)
tv18_updates_stage1(from_date, from_date)
tv18_updates_stage2(from_date, from_date)


def update_product_type(from_date, to_date):
    cod = Product.objects.get(product_name='cod')
    ppd = Product.objects.get(product_name='ppd')
    ebscod = Product.objects.get(product_name='ebscod')
    ebsppd = Product.objects.get(product_name='ebsppd')
    rev = Product.objects.get(product_name='rev')

    codships = Shipment.objects.filter(shipment_date__range=(from_date, to_date), product_type='cod', billing=None)
    cod_count = ShipmentExtension.objects.filter(shipment__in=codships).update(product=cod)

    ppdships = Shipment.objects.filter(shipment_date__range=(from_date, to_date), product_type='ppd', billing=None)
    ppd_count = ShipmentExtension.objects.filter(shipment__in=ppdships).update(product=ppd)

    ebsppdships = Shipment.objects.filter(shipment_date__range=(from_date, to_date), airwaybill_number__startswith=3, billing=None)
    ebsppd_count = ShipmentExtension.objects.filter(shipment__in=ebsppdships).update(product=ebsppd)

    ebscodships = Shipment.objects.filter(shipment_date__range=(from_date, to_date), airwaybill_number__startswith=4, billing=None)
    ebscod_count = ShipmentExtension.objects.filter(shipment__in=ebscodships).update(product=ebscod)

    revships = Shipment.objects.filter(shipment_date__range=(from_date, to_date), airwaybill_number__startswith=5, billing=None)
    rev_count = ShipmentExtension.objects.filter(shipment__in=revships).update(product=rev)

update_product_type(from_date, from_date)
