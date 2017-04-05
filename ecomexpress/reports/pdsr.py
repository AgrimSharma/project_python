"""
Calculating charges for the Weekly Performance Report.
"""
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')
# sys.path.append('/home/prtouch/workspace/ecomexpress/')

from django.db.models import Count, Sum

from service_centre.models import Shipment
from datetime import datetime, timedelta

today = datetime.today()
start_date = today - timedelta(days=30)

"""
  others = reverse_sdl_sdd_vchc_topay_rto_sum
  total = others + freight_sum + fuel_sum + cod_sum
  wt_ship = chargeable_weight_sum / ship_count
  yl_ship = total / ship_count
  yl_kl = total/cw if cw else total
  cod_rowd = [day_data.get('ship_count'), day_data.get('total_cw'), dfreight_sum,
                    dfuel_sum, day_cod_sum, others, total, wt_ship, yl_ship, yl_kl]
"""

def calculate_charges(date_range=None):
    """
    Calculate charges
    """
    if date_range==None:
        date_range=start_date
    
    shipments_in_range = Shipment.objects.filter(added_on__gte=start_date)
    
    ship_count = shipments_in_range.aggregate(Count('id'))
    total_cw = shipments_in_range.aggregate(Sum('chargeable_weight'))
    freight_sum =  shipments_in_range.aggregate(Sum('order_price__freight_charge')).values()[0]
    sdl_sum =  shipments_in_range.aggregate(Sum('order_price__sdl_charge')).values()[0] #added to others
    fuel_sum =  shipments_in_range.aggregate(Sum('order_price__fuel_surcharge')).values()[0]
    rto_sum =  shipments_in_range.aggregate(Sum('order_price__rto_charge')).values()[0] #added to others
    sdd_sum =  shipments_in_range.aggregate(Sum('order_price__sdd_charge')).values()[0] #added to others
    reverse_sum =  shipments_in_range.aggregate(Sum('order_price__reverse_charge')).values()[0]  #added to others
    vchc_sum =  shipments_in_range.aggregate(Sum('order_price__valuable_cargo_handling_charge')).values()[0] #added to others
    to_pay_sum =  shipments_in_range.aggregate(Sum('order_price__to_pay_charge')).values()[0] #added to others

    # Calculate other charges
    others = reverse_sum + sdl_sum + sdd_sum + vchc_sum + to_pay_sum + rto_sum

    # Calculate cod positive and negative
    cod_positive_sum = shipments_in_range.exclude(rts_status=1).aggregate(Sum('codcharge__cod_charge')).values()[0] # exclude rts_status = 1
    cod_negative_sum = shipments_in_range.filter(rts_status=1). aggregate(Sum('codcharge__cod_charge')).values()[0] # only rts_stauts = 1

    # Calculate cod_sum
    cod_sum = cod_positive_sum - cod_negative_sum 

    return others+freight_sum +fuel_sum+cod_sum

if __name__ == "__main__":
    print calculate_charges()
