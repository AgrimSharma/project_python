# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Billing'
        db.create_table('billing_billing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('demarrage_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_applied_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_subtract_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('billing_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('billing_date_from', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('generation_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('payment_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('service_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('education_secondary_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cess_higher_secondary_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('bill_generation_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('total_charge_pretax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_payable_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('balance', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('received', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('adjustment', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('adjustment_cr', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment_count', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_chargeable_weight', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['Billing'])

        # Adding M2M table for field shipments on 'Billing'
        db.create_table('billing_billing_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('billing', models.ForeignKey(orm['billing.billing'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('billing_billing_shipments', ['billing_id', 'shipment_id'])

        # Adding M2M table for field demarrage_shipments on 'Billing'
        db.create_table('billing_billing_demarrage_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('billing', models.ForeignKey(orm['billing.billing'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('billing_billing_demarrage_shipments', ['billing_id', 'shipment_id'])

        # Adding model 'ProductBilling'
        db.create_table('billing_productbilling', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Product'])),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['billing.Billing'])),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_applied_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_subtract_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('service_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('education_secondary_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cess_higher_secondary_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('bill_generation_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('total_charge_pretax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_payable_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment_count', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_chargeable_weight', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['ProductBilling'])

        # Adding model 'BillingSubCustomer'
        db.create_table('billing_billingsubcustomer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('demarrage_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_applied_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_subtract_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('billing_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('billing_date_from', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('generation_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('payment_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['billing.Billing'], null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment_count', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_chargeable_weight', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingSubCustomer'])

        # Adding M2M table for field shipments on 'BillingSubCustomer'
        db.create_table('billing_billingsubcustomer_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('billingsubcustomer', models.ForeignKey(orm['billing.billingsubcustomer'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('billing_billingsubcustomer_shipments', ['billingsubcustomer_id', 'shipment_id'])

        # Adding M2M table for field demarrage_shipments on 'BillingSubCustomer'
        db.create_table('billing_billingsubcustomer_demarrage_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('billingsubcustomer', models.ForeignKey(orm['billing.billingsubcustomer'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('billing_billingsubcustomer_demarrage_shipments', ['billingsubcustomer_id', 'shipment_id'])

        # Adding model 'BillingCutOff'
        db.create_table('billing_billingcutoff', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cutoff_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('billing', ['BillingCutOff'])

        # Adding model 'BillDocument'
        db.create_table('billing_billdocument', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('excel_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('billing', ['BillDocument'])

        # Adding model 'RateMatrix'
        db.create_table('billing_ratematrix', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slab', self.gf('django.db.models.fields.IntegerField')()),
            ('counter', self.gf('django.db.models.fields.IntegerField')()),
            ('rate', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal('billing', ['RateMatrix'])

        # Adding model 'ShipmentBillingQueue'
        db.create_table('billing_shipmentbillingqueue', (
            ('airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True, db_index=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('shipment_date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('shipment_type', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('product_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Product'])),
        ))
        db.send_create_signal('billing', ['ShipmentBillingQueue'])

        # Adding model 'ShipmentCharges'
        db.create_table('billing_shipmentcharges', (
            ('airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True, db_index=True)),
            ('ref_airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('origin_city', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipcharges_origin_city', null=True, to=orm['location.City'])),
            ('destination_city', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipcharges_destination_city', null=True, to=orm['location.City'])),
            ('origin_zone', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipcharges_origin_zone', null=True, to=orm['location.Zone'])),
            ('destination_zone', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipcharges_destination_zone', null=True, to=orm['location.Zone'])),
            ('length', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('bredth', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('actual_weight', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('chargeable_weight', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('sdl_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('vchc_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('topay_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('net_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('service_tax', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('education_sec_tax', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('cess_higher_secondary_tax', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('grand_total', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('billing', ['ShipmentCharges'])

        # Adding M2M table for field slabs on 'ShipmentCharges'
        db.create_table('billing_shipmentcharges_slabs', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shipmentcharges', models.ForeignKey(orm['billing.shipmentcharges'], null=False)),
            ('ratematrix', models.ForeignKey(orm['billing.ratematrix'], null=False))
        ))
        db.create_unique('billing_shipmentcharges_slabs', ['shipmentcharges_id', 'ratematrix_id'])

        # Adding model 'BillingHistory_2013_06'
        db.create_table('billing_billinghistory_2013_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0613', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_06'])

        # Adding model 'BillingHistory_2013_07'
        db.create_table('billing_billinghistory_2013_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0713', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_07'])

        # Adding model 'BillingHistory_2013_08'
        db.create_table('billing_billinghistory_2013_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0813', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_08'])

        # Adding model 'BillingHistory_2013_09'
        db.create_table('billing_billinghistory_2013_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0913', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_09'])

        # Adding model 'BillingHistory_2013_10'
        db.create_table('billing_billinghistory_2013_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1013', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_10'])

        # Adding model 'BillingHistory_2013_11'
        db.create_table('billing_billinghistory_2013_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1113', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_11'])

        # Adding model 'BillingHistory_2013_12'
        db.create_table('billing_billinghistory_2013_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1213', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_12'])

        # Adding model 'BillingHistory_2013_02'
        db.create_table('billing_billinghistory_2013_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0213', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_02'])

        # Adding model 'BillingHistory_2013_03'
        db.create_table('billing_billinghistory_2013_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0313', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_03'])

        # Adding model 'BillingHistory_2013_04'
        db.create_table('billing_billinghistory_2013_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0413', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_04'])

        # Adding model 'BillingHistory_2013_05'
        db.create_table('billing_billinghistory_2013_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0513', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2013_05'])

        # Adding model 'BillingHistory_2014_01'
        db.create_table('billing_billinghistory_2014_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0114', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_01'])

        # Adding model 'BillingHistory_2014_02'
        db.create_table('billing_billinghistory_2014_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0214', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_02'])

        # Adding model 'BillingHistory_2014_03'
        db.create_table('billing_billinghistory_2014_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0314', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_03'])

        # Adding model 'BillingHistory_2014_04'
        db.create_table('billing_billinghistory_2014_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0414', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_04'])

        # Adding model 'BillingHistory_2014_05'
        db.create_table('billing_billinghistory_2014_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0514', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_05'])

        # Adding model 'BillingHistory_2014_06'
        db.create_table('billing_billinghistory_2014_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0614', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_06'])

        # Adding model 'BillingHistory_2014_07'
        db.create_table('billing_billinghistory_2014_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0714', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_07'])

        # Adding model 'BillingHistory_2014_08'
        db.create_table('billing_billinghistory_2014_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0814', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_08'])

        # Adding model 'BillingHistory_2014_09'
        db.create_table('billing_billinghistory_2014_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0914', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_09'])

        # Adding model 'BillingHistory_2014_10'
        db.create_table('billing_billinghistory_2014_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1014', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_10'])

        # Adding model 'BillingHistory_2014_11'
        db.create_table('billing_billinghistory_2014_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1114', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_11'])

        # Adding model 'BillingHistory_2014_12'
        db.create_table('billing_billinghistory_2014_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1214', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2014_12'])

        # Adding model 'BillingHistory_2015_01'
        db.create_table('billing_billinghistory_2015_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0115', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_01'])

        # Adding model 'BillingHistory_2015_02'
        db.create_table('billing_billinghistory_2015_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0215', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_02'])

        # Adding model 'BillingHistory_2015_03'
        db.create_table('billing_billinghistory_2015_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0315', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_03'])

        # Adding model 'BillingHistory_2015_04'
        db.create_table('billing_billinghistory_2015_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0415', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_04'])

        # Adding model 'BillingHistory_2015_05'
        db.create_table('billing_billinghistory_2015_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0515', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_05'])

        # Adding model 'BillingHistory_2015_06'
        db.create_table('billing_billinghistory_2015_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0615', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_06'])

        # Adding model 'BillingHistory_2015_07'
        db.create_table('billing_billinghistory_2015_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0715', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_07'])

        # Adding model 'BillingHistory_2015_08'
        db.create_table('billing_billinghistory_2015_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0815', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_08'])

        # Adding model 'BillingHistory_2015_09'
        db.create_table('billing_billinghistory_2015_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0915', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_09'])

        # Adding model 'BillingHistory_2015_10'
        db.create_table('billing_billinghistory_2015_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1015', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_10'])

        # Adding model 'BillingHistory_2015_11'
        db.create_table('billing_billinghistory_2015_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1115', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_11'])

        # Adding model 'BillingHistory_2015_12'
        db.create_table('billing_billinghistory_2015_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1215', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2015_12'])

        # Adding model 'BillingHistory_2016_01'
        db.create_table('billing_billinghistory_2016_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0116', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_01'])

        # Adding model 'BillingHistory_2016_02'
        db.create_table('billing_billinghistory_2016_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0216', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_02'])

        # Adding model 'BillingHistory_2016_03'
        db.create_table('billing_billinghistory_2016_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0316', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_03'])

        # Adding model 'BillingHistory_2016_04'
        db.create_table('billing_billinghistory_2016_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0416', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_04'])

        # Adding model 'BillingHistory_2016_05'
        db.create_table('billing_billinghistory_2016_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0516', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_05'])

        # Adding model 'BillingHistory_2016_06'
        db.create_table('billing_billinghistory_2016_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0616', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_06'])

        # Adding model 'BillingHistory_2016_07'
        db.create_table('billing_billinghistory_2016_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0716', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_07'])

        # Adding model 'BillingHistory_2016_08'
        db.create_table('billing_billinghistory_2016_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0816', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_08'])

        # Adding model 'BillingHistory_2016_09'
        db.create_table('billing_billinghistory_2016_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0916', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_09'])

        # Adding model 'BillingHistory_2016_10'
        db.create_table('billing_billinghistory_2016_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1016', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_10'])

        # Adding model 'BillingHistory_2016_11'
        db.create_table('billing_billinghistory_2016_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1116', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_11'])

        # Adding model 'BillingHistory_2016_12'
        db.create_table('billing_billinghistory_2016_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1216', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2016_12'])

        # Adding model 'BillingHistory_2017_01'
        db.create_table('billing_billinghistory_2017_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0117', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_01'])

        # Adding model 'BillingHistory_2017_02'
        db.create_table('billing_billinghistory_2017_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0217', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_02'])

        # Adding model 'BillingHistory_2017_03'
        db.create_table('billing_billinghistory_2017_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0317', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_03'])

        # Adding model 'BillingHistory_2017_04'
        db.create_table('billing_billinghistory_2017_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0417', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_04'])

        # Adding model 'BillingHistory_2017_05'
        db.create_table('billing_billinghistory_2017_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0517', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_05'])

        # Adding model 'BillingHistory_2017_06'
        db.create_table('billing_billinghistory_2017_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0617', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_06'])

        # Adding model 'BillingHistory_2017_07'
        db.create_table('billing_billinghistory_2017_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0717', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_07'])

        # Adding model 'BillingHistory_2017_08'
        db.create_table('billing_billinghistory_2017_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0817', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_08'])

        # Adding model 'BillingHistory_2017_09'
        db.create_table('billing_billinghistory_2017_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc0917', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_09'])

        # Adding model 'BillingHistory_2017_10'
        db.create_table('billing_billinghistory_2017_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1017', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_10'])

        # Adding model 'BillingHistory_2017_11'
        db.create_table('billing_billinghistory_2017_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1117', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_11'])

        # Adding model 'BillingHistory_2017_12'
        db.create_table('billing_billinghistory_2017_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_history_sc1217', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingHistory_2017_12'])

        # Adding model 'BillingPreview'
        db.create_table('billing_billingpreview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('demarrage_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_applied_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_subtract_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('billing_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('billing_date_from', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('bill_generation_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('generation_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('payment_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('service_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('education_secondary_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cess_higher_secondary_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_charge_pretax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_payable_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('balance', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('received', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('adjustment', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('adjustment_cr', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment_count', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_chargeable_weight', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingPreview'])

        # Adding M2M table for field shipments on 'BillingPreview'
        db.create_table('billing_billingpreview_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('billingpreview', models.ForeignKey(orm['billing.billingpreview'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('billing_billingpreview_shipments', ['billingpreview_id', 'shipment_id'])

        # Adding model 'BillingSubCustomerPreview'
        db.create_table('billing_billingsubcustomerpreview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subcustomer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('demarrage_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_applied_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_subtract_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('billing_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('billing_date_from', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('generation_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('payment_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['billing.Billing'], null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment_count', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_chargeable_weight', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingSubCustomerPreview'])

        # Adding M2M table for field shipments on 'BillingSubCustomerPreview'
        db.create_table('billing_billingsubcustomerpreview_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('billingsubcustomerpreview', models.ForeignKey(orm['billing.billingsubcustomerpreview'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('billing_billingsubcustomerpreview_shipments', ['billingsubcustomerpreview_id', 'shipment_id'])

        # Adding model 'ProvisionalBillingQueue'
        db.create_table('billing_provisionalbillingqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('billing_from', self.gf('django.db.models.fields.DateField')()),
            ('billing_to', self.gf('django.db.models.fields.DateField')()),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('billing', ['ProvisionalBillingQueue'])

        # Adding M2M table for field bills on 'ProvisionalBillingQueue'
        db.create_table('billing_provisionalbillingqueue_bills', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('provisionalbillingqueue', models.ForeignKey(orm['billing.provisionalbillingqueue'], null=False)),
            ('billingpreview', models.ForeignKey(orm['billing.billingpreview'], null=False))
        ))
        db.create_unique('billing_provisionalbillingqueue_bills', ['provisionalbillingqueue_id', 'billingpreview_id'])

        # Adding model 'ProvisionalProductBilling'
        db.create_table('billing_provisionalproductbilling', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Product'])),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['billing.Billing'])),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_applied_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cod_subtract_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('service_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('education_secondary_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('cess_higher_secondary_tax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('bill_generation_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('total_charge_pretax', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_payable_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment_count', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('total_chargeable_weight', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['ProvisionalProductBilling'])

        # Adding model 'BillingQueue'
        db.create_table('billing_billingqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('billing_from', self.gf('django.db.models.fields.DateField')()),
            ('billing_to', self.gf('django.db.models.fields.DateField')()),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingQueue'])

        # Adding M2M table for field bills on 'BillingQueue'
        db.create_table('billing_billingqueue_bills', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('billingqueue', models.ForeignKey(orm['billing.billingqueue'], null=False)),
            ('billing', models.ForeignKey(orm['billing.billing'], null=False))
        ))
        db.create_unique('billing_billingqueue_bills', ['billingqueue_id', 'billing_id'])

        # Adding model 'CustomerBillingReport'
        db.create_table('billing_customerbillingreport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('billqueue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['billing.BillingQueue'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['billing.Billing'])),
            ('bill_type', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('invoice_report', self.gf('django.db.models.fields.URLField')(default='', max_length=300)),
            ('headless_invoice_report', self.gf('django.db.models.fields.URLField')(default='', max_length=300)),
            ('awb_pdf_report', self.gf('django.db.models.fields.URLField')(default='', max_length=300)),
            ('awb_excel_report', self.gf('django.db.models.fields.URLField')(default='', max_length=300)),
            ('ebs_invoice_report', self.gf('django.db.models.fields.URLField')(default='', max_length=300)),
            ('headless_ebs_invoice_report', self.gf('django.db.models.fields.URLField')(default='', max_length=300)),
        ))
        db.send_create_signal('billing', ['CustomerBillingReport'])

        # Adding unique constraint on 'CustomerBillingReport', fields ['customer', 'billing', 'billqueue']
        db.create_unique('billing_customerbillingreport', ['customer_id', 'billing_id', 'billqueue_id'])

        # Adding model 'BillingReportQueue'
        db.create_table('billing_billingreportqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('billqueue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['billing.BillingQueue'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('invoice_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('headless_invoice_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('awb_pdf_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('awb_excel_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ebs_invoice_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('headless_ebs_invoice_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('summary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('msr', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BillingReportQueue'])

        # Adding model 'BackdatedBatch'
        db.create_table('billing_backdatedbatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_from', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_to', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('count', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('processed_count', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0, db_index=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('product_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Product'], null=True, blank=True)),
            ('org_zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='back_dated_org_zone', null=True, to=orm['location.Zone'])),
            ('dest_zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='back_dated_dest_zone', null=True, to=orm['location.Zone'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BackdatedBatch'])

        # Adding model 'BackdatedShipmentBillingQueue'
        db.create_table('billing_backdatedshipmentbillingqueue', (
            ('backdated_bacth', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['billing.BackdatedBatch'])),
            ('airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True, db_index=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('shipment_date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('shipment_type', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('product_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Product'], null=True, blank=True)),
        ))
        db.send_create_signal('billing', ['BackdatedShipmentBillingQueue'])


    def backwards(self, orm):
        # Removing unique constraint on 'CustomerBillingReport', fields ['customer', 'billing', 'billqueue']
        db.delete_unique('billing_customerbillingreport', ['customer_id', 'billing_id', 'billqueue_id'])

        # Deleting model 'Billing'
        db.delete_table('billing_billing')

        # Removing M2M table for field shipments on 'Billing'
        db.delete_table('billing_billing_shipments')

        # Removing M2M table for field demarrage_shipments on 'Billing'
        db.delete_table('billing_billing_demarrage_shipments')

        # Deleting model 'ProductBilling'
        db.delete_table('billing_productbilling')

        # Deleting model 'BillingSubCustomer'
        db.delete_table('billing_billingsubcustomer')

        # Removing M2M table for field shipments on 'BillingSubCustomer'
        db.delete_table('billing_billingsubcustomer_shipments')

        # Removing M2M table for field demarrage_shipments on 'BillingSubCustomer'
        db.delete_table('billing_billingsubcustomer_demarrage_shipments')

        # Deleting model 'BillingCutOff'
        db.delete_table('billing_billingcutoff')

        # Deleting model 'BillDocument'
        db.delete_table('billing_billdocument')

        # Deleting model 'RateMatrix'
        db.delete_table('billing_ratematrix')

        # Deleting model 'ShipmentBillingQueue'
        db.delete_table('billing_shipmentbillingqueue')

        # Deleting model 'ShipmentCharges'
        db.delete_table('billing_shipmentcharges')

        # Removing M2M table for field slabs on 'ShipmentCharges'
        db.delete_table('billing_shipmentcharges_slabs')

        # Deleting model 'BillingHistory_2013_06'
        db.delete_table('billing_billinghistory_2013_06')

        # Deleting model 'BillingHistory_2013_07'
        db.delete_table('billing_billinghistory_2013_07')

        # Deleting model 'BillingHistory_2013_08'
        db.delete_table('billing_billinghistory_2013_08')

        # Deleting model 'BillingHistory_2013_09'
        db.delete_table('billing_billinghistory_2013_09')

        # Deleting model 'BillingHistory_2013_10'
        db.delete_table('billing_billinghistory_2013_10')

        # Deleting model 'BillingHistory_2013_11'
        db.delete_table('billing_billinghistory_2013_11')

        # Deleting model 'BillingHistory_2013_12'
        db.delete_table('billing_billinghistory_2013_12')

        # Deleting model 'BillingHistory_2013_02'
        db.delete_table('billing_billinghistory_2013_02')

        # Deleting model 'BillingHistory_2013_03'
        db.delete_table('billing_billinghistory_2013_03')

        # Deleting model 'BillingHistory_2013_04'
        db.delete_table('billing_billinghistory_2013_04')

        # Deleting model 'BillingHistory_2013_05'
        db.delete_table('billing_billinghistory_2013_05')

        # Deleting model 'BillingHistory_2014_01'
        db.delete_table('billing_billinghistory_2014_01')

        # Deleting model 'BillingHistory_2014_02'
        db.delete_table('billing_billinghistory_2014_02')

        # Deleting model 'BillingHistory_2014_03'
        db.delete_table('billing_billinghistory_2014_03')

        # Deleting model 'BillingHistory_2014_04'
        db.delete_table('billing_billinghistory_2014_04')

        # Deleting model 'BillingHistory_2014_05'
        db.delete_table('billing_billinghistory_2014_05')

        # Deleting model 'BillingHistory_2014_06'
        db.delete_table('billing_billinghistory_2014_06')

        # Deleting model 'BillingHistory_2014_07'
        db.delete_table('billing_billinghistory_2014_07')

        # Deleting model 'BillingHistory_2014_08'
        db.delete_table('billing_billinghistory_2014_08')

        # Deleting model 'BillingHistory_2014_09'
        db.delete_table('billing_billinghistory_2014_09')

        # Deleting model 'BillingHistory_2014_10'
        db.delete_table('billing_billinghistory_2014_10')

        # Deleting model 'BillingHistory_2014_11'
        db.delete_table('billing_billinghistory_2014_11')

        # Deleting model 'BillingHistory_2014_12'
        db.delete_table('billing_billinghistory_2014_12')

        # Deleting model 'BillingHistory_2015_01'
        db.delete_table('billing_billinghistory_2015_01')

        # Deleting model 'BillingHistory_2015_02'
        db.delete_table('billing_billinghistory_2015_02')

        # Deleting model 'BillingHistory_2015_03'
        db.delete_table('billing_billinghistory_2015_03')

        # Deleting model 'BillingHistory_2015_04'
        db.delete_table('billing_billinghistory_2015_04')

        # Deleting model 'BillingHistory_2015_05'
        db.delete_table('billing_billinghistory_2015_05')

        # Deleting model 'BillingHistory_2015_06'
        db.delete_table('billing_billinghistory_2015_06')

        # Deleting model 'BillingHistory_2015_07'
        db.delete_table('billing_billinghistory_2015_07')

        # Deleting model 'BillingHistory_2015_08'
        db.delete_table('billing_billinghistory_2015_08')

        # Deleting model 'BillingHistory_2015_09'
        db.delete_table('billing_billinghistory_2015_09')

        # Deleting model 'BillingHistory_2015_10'
        db.delete_table('billing_billinghistory_2015_10')

        # Deleting model 'BillingHistory_2015_11'
        db.delete_table('billing_billinghistory_2015_11')

        # Deleting model 'BillingHistory_2015_12'
        db.delete_table('billing_billinghistory_2015_12')

        # Deleting model 'BillingHistory_2016_01'
        db.delete_table('billing_billinghistory_2016_01')

        # Deleting model 'BillingHistory_2016_02'
        db.delete_table('billing_billinghistory_2016_02')

        # Deleting model 'BillingHistory_2016_03'
        db.delete_table('billing_billinghistory_2016_03')

        # Deleting model 'BillingHistory_2016_04'
        db.delete_table('billing_billinghistory_2016_04')

        # Deleting model 'BillingHistory_2016_05'
        db.delete_table('billing_billinghistory_2016_05')

        # Deleting model 'BillingHistory_2016_06'
        db.delete_table('billing_billinghistory_2016_06')

        # Deleting model 'BillingHistory_2016_07'
        db.delete_table('billing_billinghistory_2016_07')

        # Deleting model 'BillingHistory_2016_08'
        db.delete_table('billing_billinghistory_2016_08')

        # Deleting model 'BillingHistory_2016_09'
        db.delete_table('billing_billinghistory_2016_09')

        # Deleting model 'BillingHistory_2016_10'
        db.delete_table('billing_billinghistory_2016_10')

        # Deleting model 'BillingHistory_2016_11'
        db.delete_table('billing_billinghistory_2016_11')

        # Deleting model 'BillingHistory_2016_12'
        db.delete_table('billing_billinghistory_2016_12')

        # Deleting model 'BillingHistory_2017_01'
        db.delete_table('billing_billinghistory_2017_01')

        # Deleting model 'BillingHistory_2017_02'
        db.delete_table('billing_billinghistory_2017_02')

        # Deleting model 'BillingHistory_2017_03'
        db.delete_table('billing_billinghistory_2017_03')

        # Deleting model 'BillingHistory_2017_04'
        db.delete_table('billing_billinghistory_2017_04')

        # Deleting model 'BillingHistory_2017_05'
        db.delete_table('billing_billinghistory_2017_05')

        # Deleting model 'BillingHistory_2017_06'
        db.delete_table('billing_billinghistory_2017_06')

        # Deleting model 'BillingHistory_2017_07'
        db.delete_table('billing_billinghistory_2017_07')

        # Deleting model 'BillingHistory_2017_08'
        db.delete_table('billing_billinghistory_2017_08')

        # Deleting model 'BillingHistory_2017_09'
        db.delete_table('billing_billinghistory_2017_09')

        # Deleting model 'BillingHistory_2017_10'
        db.delete_table('billing_billinghistory_2017_10')

        # Deleting model 'BillingHistory_2017_11'
        db.delete_table('billing_billinghistory_2017_11')

        # Deleting model 'BillingHistory_2017_12'
        db.delete_table('billing_billinghistory_2017_12')

        # Deleting model 'BillingPreview'
        db.delete_table('billing_billingpreview')

        # Removing M2M table for field shipments on 'BillingPreview'
        db.delete_table('billing_billingpreview_shipments')

        # Deleting model 'BillingSubCustomerPreview'
        db.delete_table('billing_billingsubcustomerpreview')

        # Removing M2M table for field shipments on 'BillingSubCustomerPreview'
        db.delete_table('billing_billingsubcustomerpreview_shipments')

        # Deleting model 'ProvisionalBillingQueue'
        db.delete_table('billing_provisionalbillingqueue')

        # Removing M2M table for field bills on 'ProvisionalBillingQueue'
        db.delete_table('billing_provisionalbillingqueue_bills')

        # Deleting model 'ProvisionalProductBilling'
        db.delete_table('billing_provisionalproductbilling')

        # Deleting model 'BillingQueue'
        db.delete_table('billing_billingqueue')

        # Removing M2M table for field bills on 'BillingQueue'
        db.delete_table('billing_billingqueue_bills')

        # Deleting model 'CustomerBillingReport'
        db.delete_table('billing_customerbillingreport')

        # Deleting model 'BillingReportQueue'
        db.delete_table('billing_billingreportqueue')

        # Deleting model 'BackdatedBatch'
        db.delete_table('billing_backdatedbatch')

        # Deleting model 'BackdatedShipmentBillingQueue'
        db.delete_table('billing_backdatedshipmentbillingqueue')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'authentication.department': {
            'Meta': {'object_name': 'Department'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'authentication.employeemaster': {
            'Meta': {'object_name': 'EmployeeMaster'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'allow_concurent_login': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'base_service_centre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'emp_base_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.Department']"}),
            'ebs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ebs_customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'effective_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'employee_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'login_active': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'mobile_no': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'query_limit': ('django.db.models.fields.IntegerField', [], {'default': '50', 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'service_centre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'staff_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'temp_days': ('django.db.models.fields.IntegerField', [], {'default': '7', 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'temp_emp_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'Staff'", 'max_length': '15', 'blank': 'True'})
        },
        'billing.backdatedbatch': {
            'Meta': {'object_name': 'BackdatedBatch'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'date_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dest_zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'back_dated_dest_zone'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'org_zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'back_dated_org_zone'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'processed_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'product_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Product']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'billing.backdatedshipmentbillingqueue': {
            'Meta': {'object_name': 'BackdatedShipmentBillingQueue'},
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True', 'db_index': 'True'}),
            'backdated_bacth': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['billing.BackdatedBatch']"}),
            'product_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Product']", 'null': 'True', 'blank': 'True'}),
            'shipment_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'shipment_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'billing.billdocument': {
            'Meta': {'object_name': 'BillDocument'},
            'excel_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'billing.billing': {
            'Meta': {'object_name': 'Billing'},
            'adjustment': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'adjustment_cr': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'bill_generation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cess_higher_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_applied_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_subtract_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'demarrage_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'demarrage_shipments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'billing_demarrage_shipments'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"}),
            'education_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'generation_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'received': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'service_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment_count': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'ship_bills'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_charge_pretax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_payable_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billingcutoff': {
            'Meta': {'object_name': 'BillingCutOff'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {}),
            'cutoff_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'billing.billinghistory_2013_02': {
            'Meta': {'object_name': 'BillingHistory_2013_02'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0213'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_03': {
            'Meta': {'object_name': 'BillingHistory_2013_03'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0313'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_04': {
            'Meta': {'object_name': 'BillingHistory_2013_04'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0413'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_05': {
            'Meta': {'object_name': 'BillingHistory_2013_05'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0513'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_06': {
            'Meta': {'object_name': 'BillingHistory_2013_06'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0613'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_07': {
            'Meta': {'object_name': 'BillingHistory_2013_07'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0713'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_08': {
            'Meta': {'object_name': 'BillingHistory_2013_08'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0813'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_09': {
            'Meta': {'object_name': 'BillingHistory_2013_09'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0913'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_10': {
            'Meta': {'object_name': 'BillingHistory_2013_10'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1013'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_11': {
            'Meta': {'object_name': 'BillingHistory_2013_11'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1113'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2013_12': {
            'Meta': {'object_name': 'BillingHistory_2013_12'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1213'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_01': {
            'Meta': {'object_name': 'BillingHistory_2014_01'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0114'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_02': {
            'Meta': {'object_name': 'BillingHistory_2014_02'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0214'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_03': {
            'Meta': {'object_name': 'BillingHistory_2014_03'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0314'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_04': {
            'Meta': {'object_name': 'BillingHistory_2014_04'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0414'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_05': {
            'Meta': {'object_name': 'BillingHistory_2014_05'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0514'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_06': {
            'Meta': {'object_name': 'BillingHistory_2014_06'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0614'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_07': {
            'Meta': {'object_name': 'BillingHistory_2014_07'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0714'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_08': {
            'Meta': {'object_name': 'BillingHistory_2014_08'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0814'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_09': {
            'Meta': {'object_name': 'BillingHistory_2014_09'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0914'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_10': {
            'Meta': {'object_name': 'BillingHistory_2014_10'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1014'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_11': {
            'Meta': {'object_name': 'BillingHistory_2014_11'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1114'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2014_12': {
            'Meta': {'object_name': 'BillingHistory_2014_12'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1214'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_01': {
            'Meta': {'object_name': 'BillingHistory_2015_01'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0115'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_02': {
            'Meta': {'object_name': 'BillingHistory_2015_02'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0215'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_03': {
            'Meta': {'object_name': 'BillingHistory_2015_03'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0315'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_04': {
            'Meta': {'object_name': 'BillingHistory_2015_04'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0415'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_05': {
            'Meta': {'object_name': 'BillingHistory_2015_05'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0515'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_06': {
            'Meta': {'object_name': 'BillingHistory_2015_06'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0615'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_07': {
            'Meta': {'object_name': 'BillingHistory_2015_07'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0715'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_08': {
            'Meta': {'object_name': 'BillingHistory_2015_08'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0815'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_09': {
            'Meta': {'object_name': 'BillingHistory_2015_09'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0915'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_10': {
            'Meta': {'object_name': 'BillingHistory_2015_10'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1015'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_11': {
            'Meta': {'object_name': 'BillingHistory_2015_11'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1115'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2015_12': {
            'Meta': {'object_name': 'BillingHistory_2015_12'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1215'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_01': {
            'Meta': {'object_name': 'BillingHistory_2016_01'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0116'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_02': {
            'Meta': {'object_name': 'BillingHistory_2016_02'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0216'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_03': {
            'Meta': {'object_name': 'BillingHistory_2016_03'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0316'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_04': {
            'Meta': {'object_name': 'BillingHistory_2016_04'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0416'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_05': {
            'Meta': {'object_name': 'BillingHistory_2016_05'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0516'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_06': {
            'Meta': {'object_name': 'BillingHistory_2016_06'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0616'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_07': {
            'Meta': {'object_name': 'BillingHistory_2016_07'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0716'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_08': {
            'Meta': {'object_name': 'BillingHistory_2016_08'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0816'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_09': {
            'Meta': {'object_name': 'BillingHistory_2016_09'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0916'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_10': {
            'Meta': {'object_name': 'BillingHistory_2016_10'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1016'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_11': {
            'Meta': {'object_name': 'BillingHistory_2016_11'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1116'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2016_12': {
            'Meta': {'object_name': 'BillingHistory_2016_12'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1216'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_01': {
            'Meta': {'object_name': 'BillingHistory_2017_01'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0117'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_02': {
            'Meta': {'object_name': 'BillingHistory_2017_02'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0217'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_03': {
            'Meta': {'object_name': 'BillingHistory_2017_03'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0317'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_04': {
            'Meta': {'object_name': 'BillingHistory_2017_04'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0417'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_05': {
            'Meta': {'object_name': 'BillingHistory_2017_05'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0517'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_06': {
            'Meta': {'object_name': 'BillingHistory_2017_06'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0617'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_07': {
            'Meta': {'object_name': 'BillingHistory_2017_07'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0717'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_08': {
            'Meta': {'object_name': 'BillingHistory_2017_08'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0817'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_09': {
            'Meta': {'object_name': 'BillingHistory_2017_09'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc0917'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_10': {
            'Meta': {'object_name': 'BillingHistory_2017_10'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1017'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_11': {
            'Meta': {'object_name': 'BillingHistory_2017_11'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1117'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billinghistory_2017_12': {
            'Meta': {'object_name': 'BillingHistory_2017_12'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_history_sc1217'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billingpreview': {
            'Meta': {'object_name': 'BillingPreview'},
            'adjustment': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'adjustment_cr': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'bill_generation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cess_higher_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_applied_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_subtract_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'demarrage_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'education_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'generation_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'received': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'service_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment_count': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.Shipment']", 'symmetrical': 'False'}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_charge_pretax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_payable_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billingqueue': {
            'Meta': {'object_name': 'BillingQueue'},
            'billing_from': ('django.db.models.fields.DateField', [], {}),
            'billing_to': ('django.db.models.fields.DateField', [], {}),
            'bills': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['billing.Billing']", 'symmetrical': 'False'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'billing.billingreportqueue': {
            'Meta': {'object_name': 'BillingReportQueue'},
            'awb_excel_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'awb_pdf_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'billqueue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['billing.BillingQueue']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'ebs_invoice_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'headless_ebs_invoice_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'headless_invoice_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'msr': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'summary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'billing.billingsubcustomer': {
            'Meta': {'object_name': 'BillingSubCustomer'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['billing.Billing']", 'null': 'True', 'blank': 'True'}),
            'billing_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cod_applied_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_subtract_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'demarrage_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'demarrage_shipments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'billingsubcustomer_demarrage_shipments'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'generation_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment_count': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.Shipment']", 'symmetrical': 'False'}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billingsubcustomerpreview': {
            'Meta': {'object_name': 'BillingSubCustomerPreview'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['billing.Billing']", 'null': 'True', 'blank': 'True'}),
            'billing_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cod_applied_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_subtract_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'demarrage_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'generation_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment_count': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.Shipment']", 'symmetrical': 'False'}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'billing.customerbillingreport': {
            'Meta': {'unique_together': "(('customer', 'billing', 'billqueue'),)", 'object_name': 'CustomerBillingReport'},
            'awb_excel_report': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '300'}),
            'awb_pdf_report': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '300'}),
            'bill_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['billing.Billing']"}),
            'billqueue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['billing.BillingQueue']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'ebs_invoice_report': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '300'}),
            'headless_ebs_invoice_report': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '300'}),
            'headless_invoice_report': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_report': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '300'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'billing.productbilling': {
            'Meta': {'object_name': 'ProductBilling'},
            'bill_generation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['billing.Billing']"}),
            'cess_higher_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_applied_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_subtract_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'education_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Product']"}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'service_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment_count': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_charge_pretax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_payable_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'billing.provisionalbillingqueue': {
            'Meta': {'object_name': 'ProvisionalBillingQueue'},
            'billing_from': ('django.db.models.fields.DateField', [], {}),
            'billing_to': ('django.db.models.fields.DateField', [], {}),
            'bills': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['billing.BillingPreview']", 'symmetrical': 'False'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'billing.provisionalproductbilling': {
            'Meta': {'object_name': 'ProvisionalProductBilling'},
            'bill_generation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['billing.Billing']"}),
            'cess_higher_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_applied_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_subtract_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'education_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Product']"}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'service_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment_count': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_charge_pretax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_payable_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'billing.ratematrix': {
            'Meta': {'object_name': 'RateMatrix'},
            'counter': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'slab': ('django.db.models.fields.IntegerField', [], {})
        },
        'billing.shipmentbillingqueue': {
            'Meta': {'object_name': 'ShipmentBillingQueue'},
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True', 'db_index': 'True'}),
            'product_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Product']"}),
            'shipment_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'shipment_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'billing.shipmentcharges': {
            'Meta': {'object_name': 'ShipmentCharges'},
            'actual_weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True', 'db_index': 'True'}),
            'bredth': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cess_higher_secondary_tax': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'chargeable_weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'cod_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'destination_city': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipcharges_destination_city'", 'null': 'True', 'to': "orm['location.City']"}),
            'destination_zone': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipcharges_destination_zone'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'education_sec_tax': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'grand_total': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'net_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'origin_city': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipcharges_origin_city'", 'null': 'True', 'to': "orm['location.City']"}),
            'origin_zone': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipcharges_origin_zone'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'ref_airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'service_tax': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'slabs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['billing.RateMatrix']", 'symmetrical': 'False'}),
            'topay_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'vchc_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'customer.customer': {
            'Meta': {'object_name': 'Customer'},
            'activation_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'activation_by'", 'null': 'True', 'to': "orm['auth.User']"}),
            'activation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'activation_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Address2']", 'null': 'True', 'blank': 'True'}),
            'approved': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'approver'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'authorized': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'authorizer'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'bill_delivery_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bill_delivery_hand': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'billing_schedule': ('django.db.models.fields.IntegerField', [], {'default': '7', 'max_length': '3'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'contact_person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Contact']", 'null': 'True', 'blank': 'True'}),
            'contract_from': ('django.db.models.fields.DateField', [], {}),
            'contract_to': ('django.db.models.fields.DateField', [], {}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_by'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit_limit': ('django.db.models.fields.IntegerField', [], {'default': '10000', 'max_length': '10'}),
            'credit_period': ('django.db.models.fields.IntegerField', [], {'default': '10', 'max_length': '3'}),
            'day_of_billing': ('django.db.models.fields.SmallIntegerField', [], {'default': '7'}),
            'decision_maker': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'decision_maker'", 'null': 'True', 'to': "orm['location.Contact']"}),
            'demarrage_min_amt': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'demarrage_perkg_amt': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'flat_cod_amt': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge_applicable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'legality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Legality']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'next_bill_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'pan_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'referred_by': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'remittance_cycle': ('django.db.models.fields.SmallIntegerField', [], {'default': '7'}),
            'return_to_origin': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'reverse_charges': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'saleslead': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'saleslead'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'signed': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'signatory'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'tan_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'to_pay_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'updated_by'", 'null': 'True', 'to': "orm['auth.User']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'vchc_min': ('django.db.models.fields.DecimalField', [], {'default': '0.5', 'max_digits': '6', 'decimal_places': '2'}),
            'vchc_min_amnt_applied': ('django.db.models.fields.IntegerField', [], {'default': '5000', 'max_length': '5'}),
            'vchc_rate': ('django.db.models.fields.DecimalField', [], {'default': '0.5', 'max_digits': '4', 'decimal_places': '2'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zone_label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ZoneLabel']", 'null': 'True', 'blank': 'True'})
        },
        'customer.product': {
            'Meta': {'object_name': 'Product'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'customer.shipper': {
            'Meta': {'object_name': 'Shipper'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Address']", 'null': 'True', 'blank': 'True'}),
            'alias_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'ecomm_admin.legality': {
            'Meta': {'object_name': 'Legality'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legality_type': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'ecomm_admin.mode': {
            'Meta': {'object_name': 'Mode'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'ecomm_admin.shipmentstatusmaster': {
            'Meta': {'ordering': "['code']", 'object_name': 'ShipmentStatusMaster'},
            'code': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'code_description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'code_redirect': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'location.address': {
            'Meta': {'object_name': 'Address'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.State']"})
        },
        'location.address2': {
            'Meta': {'object_name': 'Address2'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        },
        'location.areamaster': {
            'Meta': {'object_name': 'AreaMaster'},
            'area_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'area_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'branch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Branch']"}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'location.branch': {
            'Meta': {'object_name': 'Branch'},
            'branch_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'branch_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'branch_type': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '13'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'location.city': {
            'Meta': {'object_name': 'City'},
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'city_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labeled_zones': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'label_city'", 'symmetrical': 'False', 'to': "orm['location.Zone']"}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Region']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.State']"}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Zone']"})
        },
        'location.contact': {
            'Meta': {'object_name': 'Contact'},
            'address1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'address4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']", 'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'default': "'0000-00-00'", 'null': 'True', 'blank': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.State']", 'null': 'True', 'blank': 'True'})
        },
        'location.region': {
            'Meta': {'object_name': 'Region'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'region_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'location.servicecenter': {
            'Meta': {'ordering': "['center_shortcode']", 'object_name': 'ServiceCenter'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Address']"}),
            'center_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'center_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']"}),
            'contact': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['location.Contact']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'})
        },
        'location.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'state_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'location.zone': {
            'Meta': {'object_name': 'Zone'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ZoneLabel']", 'null': 'True', 'blank': 'True'}),
            'location_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'max_length': '1'}),
            'zone_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'zone_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'location.zonelabel': {
            'Meta': {'object_name': 'ZoneLabel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'pickup.pickupregistration': {
            'Meta': {'object_name': 'PickupRegistration'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'address_line3': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'address_line4': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.AreaMaster']", 'null': 'True', 'blank': 'True'}),
            'caller_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'callers_number': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'customer_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'customer_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']", 'null': 'True', 'blank': 'True'}),
            'office_close_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'pickup_date': ('django.db.models.fields.DateField', [], {}),
            'pickup_route': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'pickup_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'pieces': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'product_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'regular_pickup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'reminder': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'reverse_pickup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'service_centre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'subcustomer_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']", 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'to_pay': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'volume_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.shipment': {
            'Meta': {'object_name': 'Shipment'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {}),
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_ships'", 'null': 'True', 'to': "orm['billing.Billing']"}),
            'breadth': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'consignee': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'consignee_address1': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'consignee_address2': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'consignee_address3': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'consignee_address4': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'declared_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'destination_city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'item_description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'manifest_location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manifest_location'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'mobile': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipment_origin_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'pickup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipment_pickup'", 'null': 'True', 'to': "orm['pickup.PickupRegistration']"}),
            'pieces': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'rd_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'ref_airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rejection': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'return_shipment': ('django.db.models.fields.SmallIntegerField', [], {'default': 'False'}),
            'reverse_pickup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rto_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rts_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rts_reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rts_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sbilling': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subbilling_ships'", 'null': 'True', 'to': "orm['billing.BillingSubCustomer']"}),
            'sdd': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'service_centre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipment_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'shipment_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'shipper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'status_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'tab': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['billing']