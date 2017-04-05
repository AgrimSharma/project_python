"""
UnitTests for product_master

prtouch
"""

from django.test import TestCase
from .models import ProductItemMaster
from customer.models import Customer
import datetime
from decimal import Decimal 

class pimTest(TestCase):
    def setUp(self):
        '''setup the test rig'''

        customer = Customer.objects.create(activation_by_id= 285L,
            activation_date= datetime.date(2013, 7, 29),
            activation_status= True,
            address_id= 144L,
            approved_id= 99L,
            authorized_id= 99L,
            bill_delivery_email= True,
            bill_delivery_hand= True,
            billing_schedule= 30L,
            code= u'92006',
            contact_person_id= 17L,
            contract_from= datetime.date(2013, 1, 31),
            contract_to= datetime.date(2016, 1, 30),
            created_by_id= None,
            created_on= datetime.datetime(2013, 1, 29, 13, 44, 56),
            credit_limit= 500000L,
            credit_period= 10L,
            day_of_billing= 1,
            decision_maker_id= 18L,
            demarrage_min_amt= None,
            demarrage_perkg_amt= None,
            email= u'www.jasperinfotech.com',
            # lat_cod_amt= None,
            fuel_surcharge_applicable= True,
            id= 6L,
            invoice_date= None,
            legality_id= 1L,
            name= u'JASPER INFOTECH PRIVATE LIMITED',
            next_bill_date= None,
            pan_number= u'0',
            referred_by= None,
            remittance_cycle= 7,
            return_to_origin= Decimal('0.00'),
            reverse_charges= None,
            saleslead_id= 99L,
            signed_id= 99L,
            tan_number= u'0',
            to_pay_charge= Decimal('0.00'),
            updated_by_id= None,
            updated_on= datetime.datetime(2013, 12, 13, 17, 47, 18),
            vchc_min= Decimal('0.00'),
            vchc_min_amnt_applied= 5000L,
            vchc_rate= Decimal('0.30'),
            website= 'www.jasperinfotech.com',
            zone_label_id= None)
        ProductItemMaster.objects.create(product_description="mobile phone",product_weight=15.4,product_height=2.66,product_breadth=10.1,product_length=5,squ_id="MP-1", customer=customer)
        ProductItemMaster.objects.create(product_description="tablet phone",product_weight=13.7,product_height=2.2,product_breadth=9.11,product_length=5.3,squ_id="MP-2", customer=customer)

    def test_basic_data_sanity(self):
        """
        Tests that correct objects are being created and returned.
        """
        object1 = ProductItemMaster.objects.get(id=1)
        object2 = ProductItemMaster.objects.get(id=2)
        self.assertEqual(object1.product_description, "mobile phone")
        self.assertEqual(object2.product_description, "tablet phone")
        self.assertEquals(object2.product_height, 2.66)
        self.assertEquals(object1.produc_breadth, 10.1)
        
    def test_pim_updates_properly(self):
        '''
        Tests that existing pim record updates properly.
        '''
        object1 = ProductItemMaster.objects.get(id=1)