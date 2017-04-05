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

from mongoadmin.models import view_shipment_correction


class MongoAdminCorrectionTableTest(unittest.TestCase):

    def test_view_shipment_correction(self):
        result = view_shipment_correction('2015-04-28', '2015-04-28')
        self.assertEqual(result.count(), 40)


if __name__ == '__main__':
    unittest.main()
