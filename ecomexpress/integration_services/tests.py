"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')


#from django.test import TestCase
import unittest
from service_centre.models import Shipment
from integration_services.utils import nearest_dc, get_shipment_address
from location.models import ServiceCenter


class DCFinderTest(unittest.TestCase):

    def test_get_dc(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        shipments = Shipment.objects.filter(shipment_date='2014-01-10')[21:50]
        total_ships = shipments.count()
        success_count = 0
        for ship in shipments:
            ship_address = get_shipment_address(ship.airwaybill_number)
	    if ship_address:
	        from time import sleep
		sleep(1.7)
		dc = nearest_dc(ship_address)
                print '*' * 30
                print ship.airwaybill_number, '\t', ship.original_dest_id, '\t', dc
		if dc:
                    sc = ServiceCenter.objects.get(id=dc)
                    print ship.original_dest, '\t', sc
                    print ship.original_dest.city.state, '\t', sc.city.state
                if dc == ship.original_dest_id:
                    success_count += 1
        self.assertEqual(total_ships, success_count) 


if __name__ == '__main__':
    unittest.main()

#suite = unittest.TestLoader().loadTestsFromTestCase(SimpleTest)
#unittest.TextTestRunner(verbosity=2).run(suite)
