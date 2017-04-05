import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from reports.random_reports import pickup_dashbaord
pickup_dashbaord()
#active_customer_details()
# cluster_dcmapping, cluster_emailmapping
# from billing.jasper_update_new import *
# from reports.daywise_charge_misc import get_daywise_charge_report
# from reports.cluster_reports import *
# from reports.models import *
# from_date = '2014-2-01'
# to_date = '2014-2-02'

#pwp(12, 04, 2015)

# cluster = Cluster.objects.all()
#for cl in cluster:
#    fn = inbound_exception_notin_EEPL_gt_24(cl)
#    print fn
#fn = cluster_emailmapping('/tmp/cluster_emailmapping.xlsx')
#print fn
#fn = get_daywise_charge_report(-9,4)
#print fn
#ships = Shipment.objects.filter(shipper_id=6, shipment_date__range=(from_date, to_date))

#for s in ships:
#   s.set_chargeable_weight
#bagging()
#print a

#if __name__ == "__main__":
    #print update_dc_lat_lng()
    #print process_slashes(None)
#    address1 = "Ghansh@#$yam enc$@lave,Link% Road,Ka*ndivali(E),Mumbai"
# raw_input("Please enter address 1> ")
    #address2 = "ecomm express,old gurgaon road, kapashera, new delhi"
# raw_input("Please enter address 2> ")
    #print feed_addresses(address1, address2)
#    print nearest_dc(address1)
