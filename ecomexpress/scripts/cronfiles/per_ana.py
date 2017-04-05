import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from reports.performance_analysis import *
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
performance_analysis()
#print a
