# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Customer'
        db.create_table('customer_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('activation_status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('activation_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('contract_from', self.gf('django.db.models.fields.DateField')()),
            ('contract_to', self.gf('django.db.models.fields.DateField')()),
            ('legality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Legality'])),
            ('billing_schedule', self.gf('django.db.models.fields.IntegerField')(default=7, max_length=3)),
            ('day_of_billing', self.gf('django.db.models.fields.SmallIntegerField')(default=7)),
            ('remittance_cycle', self.gf('django.db.models.fields.SmallIntegerField')(default=7)),
            ('credit_limit', self.gf('django.db.models.fields.IntegerField')(default=10000, max_length=10)),
            ('activation_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='activation_by', null=True, to=orm['auth.User'])),
            ('credit_period', self.gf('django.db.models.fields.IntegerField')(default=10, max_length=3)),
            ('fuel_surcharge_applicable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2, blank=True)),
            ('vchc_rate', self.gf('django.db.models.fields.DecimalField')(default=0.5, max_digits=4, decimal_places=2)),
            ('vchc_min', self.gf('django.db.models.fields.DecimalField')(default=0.5, max_digits=6, decimal_places=2)),
            ('vchc_min_amnt_applied', self.gf('django.db.models.fields.IntegerField')(default=5000, max_length=5)),
            ('return_to_origin', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2, blank=True)),
            ('flat_cod_amt', self.gf('django.db.models.fields.IntegerField')(max_length=4, null=True, blank=True)),
            ('demarrage_min_amt', self.gf('django.db.models.fields.IntegerField')(max_length=4, null=True, blank=True)),
            ('demarrage_perkg_amt', self.gf('django.db.models.fields.IntegerField')(max_length=4, null=True, blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_by', null=True, to=orm['auth.User'])),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='updated_by', null=True, to=orm['auth.User'])),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.Address2'], null=True, blank=True)),
            ('contact_person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.Contact'], null=True, blank=True)),
            ('decision_maker', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='decision_maker', null=True, to=orm['location.Contact'])),
            ('pan_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('tan_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('saleslead', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='saleslead', null=True, to=orm['authentication.EmployeeMaster'])),
            ('signed', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='signatory', null=True, to=orm['authentication.EmployeeMaster'])),
            ('approved', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='approver', null=True, to=orm['authentication.EmployeeMaster'])),
            ('authorized', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='authorizer', null=True, to=orm['authentication.EmployeeMaster'])),
            ('bill_delivery_email', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('bill_delivery_hand', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('invoice_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('next_bill_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('reverse_charges', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2, blank=True)),
            ('zone_label', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['location.ZoneLabel'], null=True, blank=True)),
            ('referred_by', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('deactivation_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('customer', ['Customer'])

        # Adding model 'Shipper'
        db.create_table('customer_shipper', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('alias_code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.Address'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('customer', ['Shipper'])

        # Adding model 'ShipperMapping'
        db.create_table('customer_shippermapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'])),
            ('forward_pincode', self.gf('django.db.models.fields.IntegerField')(max_length=8)),
            ('return_pincode', self.gf('django.db.models.fields.IntegerField')(max_length=8)),
        ))
        db.send_create_signal('customer', ['ShipperMapping'])

        # Adding model 'Product'
        db.create_table('customer_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('customer', ['Product'])

        # Adding model 'CashOnDelivery'
        db.create_table('customer_cashondelivery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('COD_service_charge', self.gf('django.db.models.fields.FloatField')()),
            ('start_range', self.gf('django.db.models.fields.FloatField')()),
            ('end_range', self.gf('django.db.models.fields.FloatField')()),
            ('flat_COD_charge', self.gf('django.db.models.fields.FloatField')()),
            ('minimum_COD_charge', self.gf('django.db.models.fields.FloatField')()),
            ('effective_date', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('customer', ['CashOnDelivery'])

        # Adding model 'CashOnDeliveryZone'
        db.create_table('customer_cashondeliveryzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('c_zone_org', self.gf('django.db.models.fields.related.ForeignKey')(related_name='c_zone_org', to=orm['location.Zone'])),
            ('c_zone_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='c_zone_dest', to=orm['location.Zone'])),
            ('COD_service_charge', self.gf('django.db.models.fields.FloatField')()),
            ('start_range', self.gf('django.db.models.fields.FloatField')()),
            ('end_range', self.gf('django.db.models.fields.FloatField')()),
            ('flat_COD_charge', self.gf('django.db.models.fields.FloatField')()),
            ('minimum_COD_charge', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('customer', ['CashOnDeliveryZone'])

        # Adding model 'FuelSurcharge'
        db.create_table('customer_fuelsurcharge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('fuelsurcharge_min_rate', self.gf('django.db.models.fields.FloatField')()),
            ('fuelsurcharge_min_fuel_rate', self.gf('django.db.models.fields.FloatField')()),
            ('flat_fuel_surcharge', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_fuel_surcharge', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('effective_date', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('customer', ['FuelSurcharge'])

        # Adding model 'FuelSurchargeZone'
        db.create_table('customer_fuelsurchargezone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fuelsurcharge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.FuelSurcharge'])),
            ('f_zone_org', self.gf('django.db.models.fields.related.ForeignKey')(related_name='f_zone_org', to=orm['location.Zone'])),
            ('f_zone_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='f_zone_dest', to=orm['location.Zone'])),
            ('fuelsurcharge_min_rate', self.gf('django.db.models.fields.FloatField')()),
            ('fuelsurcharge_min_fuel_rate', self.gf('django.db.models.fields.FloatField')()),
            ('flat_fuel_surcharge', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_fuel_surcharge', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('customer', ['FuelSurchargeZone'])

        # Adding M2M table for field product on 'FuelSurchargeZone'
        db.create_table('customer_fuelsurchargezone_product', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('fuelsurchargezone', models.ForeignKey(orm['customer.fuelsurchargezone'], null=False)),
            ('product', models.ForeignKey(orm['customer.product'], null=False))
        ))
        db.create_unique('customer_fuelsurchargezone_product', ['fuelsurchargezone_id', 'product_id'])

        # Adding model 'FreightSlab'
        db.create_table('customer_freightslab', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=500, max_length=5)),
            ('weight_rate', self.gf('django.db.models.fields.FloatField')(default=35)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
        ))
        db.send_create_signal('customer', ['FreightSlab'])

        # Adding model 'RateVersion'
        db.create_table('customer_rateversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('effective_date', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('customer', ['RateVersion'])

        # Adding model 'ForwardFreightRate'
        db.create_table('customer_forwardfreightrate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.RateVersion'])),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=500, max_length=5)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6, db_index=True)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6, db_index=True)),
            ('org_zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ff_org_zone', to=orm['location.Zone'])),
            ('dest_zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ff_dest_zone', to=orm['location.Zone'])),
            ('rate_per_slab', self.gf('django.db.models.fields.FloatField')(default=20)),
        ))
        db.send_create_signal('customer', ['ForwardFreightRate'])

        # Adding M2M table for field product on 'ForwardFreightRate'
        db.create_table('customer_forwardfreightrate_product', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('forwardfreightrate', models.ForeignKey(orm['customer.forwardfreightrate'], null=False)),
            ('product', models.ForeignKey(orm['customer.product'], null=False))
        ))
        db.create_unique('customer_forwardfreightrate_product', ['forwardfreightrate_id', 'product_id'])

        # Adding model 'FreightSlabCity'
        db.create_table('customer_freightslabcity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=500, max_length=5)),
            ('weight_rate', self.gf('django.db.models.fields.FloatField')(default=35)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
            ('city_org', self.gf('django.db.models.fields.related.ForeignKey')(related_name='city_org', to=orm['location.City'])),
            ('city_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='city_dest', to=orm['location.City'])),
            ('rate_per_slab', self.gf('django.db.models.fields.FloatField')(default=20)),
        ))
        db.send_create_signal('customer', ['FreightSlabCity'])

        # Adding M2M table for field product on 'FreightSlabCity'
        db.create_table('customer_freightslabcity_product', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('freightslabcity', models.ForeignKey(orm['customer.freightslabcity'], null=False)),
            ('product', models.ForeignKey(orm['customer.product'], null=False))
        ))
        db.create_unique('customer_freightslabcity_product', ['freightslabcity_id', 'product_id'])

        # Adding model 'FreightSlabOriginZone'
        db.create_table('customer_freightslaboriginzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=500, max_length=5)),
            ('weight_rate', self.gf('django.db.models.fields.FloatField')(default=35)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
            ('org_zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='org_zone', to=orm['location.Zone'])),
            ('city_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='freight_city_dest', to=orm['location.City'])),
            ('rate_per_slab', self.gf('django.db.models.fields.FloatField')(default=20)),
        ))
        db.send_create_signal('customer', ['FreightSlabOriginZone'])

        # Adding M2M table for field product on 'FreightSlabOriginZone'
        db.create_table('customer_freightslaboriginzone_product', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('freightslaboriginzone', models.ForeignKey(orm['customer.freightslaboriginzone'], null=False)),
            ('product', models.ForeignKey(orm['customer.product'], null=False))
        ))
        db.create_unique('customer_freightslaboriginzone_product', ['freightslaboriginzone_id', 'product_id'])

        # Adding model 'FreightSlabDestZone'
        db.create_table('customer_freightslabdestzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=500, max_length=5)),
            ('weight_rate', self.gf('django.db.models.fields.FloatField')(default=35)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
            ('dest_zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dest_zone', to=orm['location.Zone'])),
            ('city_org', self.gf('django.db.models.fields.related.ForeignKey')(related_name='freight_city_org', to=orm['location.City'])),
            ('rate_per_slab', self.gf('django.db.models.fields.FloatField')(default=20)),
        ))
        db.send_create_signal('customer', ['FreightSlabDestZone'])

        # Adding M2M table for field product on 'FreightSlabDestZone'
        db.create_table('customer_freightslabdestzone_product', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('freightslabdestzone', models.ForeignKey(orm['customer.freightslabdestzone'], null=False)),
            ('product', models.ForeignKey(orm['customer.product'], null=False))
        ))
        db.create_unique('customer_freightslabdestzone_product', ['freightslabdestzone_id', 'product_id'])

        # Adding model 'FreightSlabZone'
        db.create_table('customer_freightslabzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('freight_slab', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.FreightSlab'])),
            ('zone_org', self.gf('django.db.models.fields.related.ForeignKey')(related_name='zone_org', to=orm['location.Zone'])),
            ('zone_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='zone_dest', to=orm['location.Zone'])),
            ('rate_per_slab', self.gf('django.db.models.fields.FloatField')(default=20)),
        ))
        db.send_create_signal('customer', ['FreightSlabZone'])

        # Adding model 'CODFreightSlab'
        db.create_table('customer_codfreightslab', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=500, max_length=5)),
            ('weight_rate', self.gf('django.db.models.fields.FloatField')(default=35)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
        ))
        db.send_create_signal('customer', ['CODFreightSlab'])

        # Adding model 'CODFreightSlabZone'
        db.create_table('customer_codfreightslabzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('freight_slab', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.CODFreightSlab'])),
            ('zone_org', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cod_zone_org', to=orm['location.Zone'])),
            ('zone_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cod_zone_dest', to=orm['location.Zone'])),
            ('rate_per_slab', self.gf('django.db.models.fields.FloatField')(default=20)),
        ))
        db.send_create_signal('customer', ['CODFreightSlabZone'])

        # Adding model 'RTSFreightSlab'
        db.create_table('customer_rtsfreightslab', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=500, max_length=5)),
            ('weight_rate', self.gf('django.db.models.fields.FloatField')(default=35)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
        ))
        db.send_create_signal('customer', ['RTSFreightSlab'])

        # Adding model 'RTSFreightSlabZone'
        db.create_table('customer_rtsfreightslabzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('freight_slab', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.RTSFreightSlab'])),
            ('zone_org', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rts_zone_org', to=orm['location.Zone'])),
            ('zone_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rts_zone_dest', to=orm['location.Zone'])),
            ('rate_per_slab', self.gf('django.db.models.fields.FloatField')(default=20)),
        ))
        db.send_create_signal('customer', ['RTSFreightSlabZone'])

        # Adding model 'ReverseFreightSlab'
        db.create_table('customer_reversefreightslab', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=500, max_length=5)),
            ('weight_rate', self.gf('django.db.models.fields.FloatField')(default=35)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
        ))
        db.send_create_signal('customer', ['ReverseFreightSlab'])

        # Adding model 'ReverseFreightSlabZone'
        db.create_table('customer_reversefreightslabzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('freight_slab', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.ReverseFreightSlab'])),
            ('zone_org', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rev_zone_org', to=orm['location.Zone'])),
            ('zone_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rev_zone_dest', to=orm['location.Zone'])),
            ('rate_per_slab', self.gf('django.db.models.fields.FloatField')(default=20)),
        ))
        db.send_create_signal('customer', ['ReverseFreightSlabZone'])

        # Adding model 'SDLSlab'
        db.create_table('customer_sdlslab', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=1000, max_length=5)),
            ('weight_rate', self.gf('django.db.models.fields.IntegerField')(default=100, max_length=5)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
        ))
        db.send_create_signal('customer', ['SDLSlab'])

        # Adding model 'SDDZone'
        db.create_table('customer_sddzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('shortcode', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('customer', ['SDDZone'])

        # Adding M2M table for field pincode on 'SDDZone'
        db.create_table('customer_sddzone_pincode', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sddzone', models.ForeignKey(orm['customer.sddzone'], null=False)),
            ('pincode', models.ForeignKey(orm['location.pincode'], null=False))
        ))
        db.create_unique('customer_sddzone_pincode', ['sddzone_id', 'pincode_id'])

        # Adding model 'SDDSlabZone'
        db.create_table('customer_sddslabzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('freight_slab', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.FreightSlab'])),
            ('zone_org', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sdd_zone_org', null=True, to=orm['location.Zone'])),
            ('zone_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sdd_zone_dest', null=True, to=orm['location.Zone'])),
            ('sddzone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.SDDZone'])),
            ('rate_per_slab', self.gf('django.db.models.fields.FloatField')(default=20)),
        ))
        db.send_create_signal('customer', ['SDDSlabZone'])

        # Adding model 'ExceptionMaster'
        db.create_table('customer_exceptionmaster', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fk_customer', to=orm['customer.Customer'])),
            ('exception_code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('meaning', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('contact_customer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contact_customer', to=orm['customer.Customer'])),
            ('admin_contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'])),
        ))
        db.send_create_signal('customer', ['ExceptionMaster'])

        # Adding model 'BrandedFleetCustomer'
        db.create_table('customer_brandedfleetcustomer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('branded_fleet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.BrandedFleet'])),
            ('number_of_fleet', self.gf('django.db.models.fields.IntegerField')(max_length=3)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('customer', ['BrandedFleetCustomer'])

        # Adding model 'BrandedFullTimeEmployeeCustomer'
        db.create_table('customer_brandedfulltimeemployeecustomer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('branded_full_time_employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.BrandedFullTimeEmployee'])),
            ('number_of_employee', self.gf('django.db.models.fields.IntegerField')(max_length=3)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('customer', ['BrandedFullTimeEmployeeCustomer'])

        # Adding model 'Remittance'
        db.create_table('customer_remittance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('remitted_on', self.gf('django.db.models.fields.DateField')()),
            ('remitted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='remitted_by', null=True, to=orm['auth.User'])),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('bank_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bank_ref_number', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('customer', ['Remittance'])

        # Adding model 'VolumetricWeightDivisor'
        db.create_table('customer_volumetricweightdivisor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('divisor', self.gf('django.db.models.fields.IntegerField')(max_length=6)),
        ))
        db.send_create_signal('customer', ['VolumetricWeightDivisor'])

        # Adding model 'MinActualWeight'
        db.create_table('customer_minactualweight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('weight', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('customer', ['MinActualWeight'])

        # Adding model 'SDLSlabCustomer'
        db.create_table('customer_sdlslabcustomer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=1000, max_length=5)),
            ('weight_rate', self.gf('django.db.models.fields.IntegerField')(default=100, max_length=5)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
        ))
        db.send_create_signal('customer', ['SDLSlabCustomer'])

        # Adding model 'CustomerAPI'
        db.create_table('customer_customerapi', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=24)),
            ('ipaddress', self.gf('django.db.models.fields.CharField')(default=0, max_length=255)),
        ))
        db.send_create_signal('customer', ['CustomerAPI'])

        # Adding model 'RTSFreightZone'
        db.create_table('customer_rtsfreightzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('freight_slab', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.FreightSlab'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='freight_origin', null=True, to=orm['location.Zone'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='freight_dest', null=True, to=orm['location.Zone'])),
            ('rate', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('customer', ['RTSFreightZone'])

        # Adding model 'RTSFuelZone'
        db.create_table('customer_rtsfuelzone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='fuel_origin', null=True, to=orm['location.Zone'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='fuel_dest', null=True, to=orm['location.Zone'])),
            ('rate', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('customer', ['RTSFuelZone'])

        # Adding model 'RTSFreight'
        db.create_table('customer_rtsfreight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('rate', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('customer', ['RTSFreight'])

        # Adding model 'RTSFuel'
        db.create_table('customer_rtsfuel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('rate', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('customer', ['RTSFuel'])

        # Adding model 'RTSFreightSlabRate'
        db.create_table('customer_rtsfreightslabrate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('slab', self.gf('django.db.models.fields.IntegerField')(default=1000, max_length=5)),
            ('range_from', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('range_to', self.gf('django.db.models.fields.IntegerField')(default=999999, max_length=6)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='freightslab_origin', null=True, to=orm['location.Zone'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='freightslab_dest', null=True, to=orm['location.Zone'])),
            ('rate', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('normal_applicable', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('customer', ['RTSFreightSlabRate'])

        # Adding model 'SubcustomerDetailsUpload'
        db.create_table('customer_subcustomerdetailsupload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('filepath', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('customer', ['SubcustomerDetailsUpload'])

        # Adding model 'CustomerReportNames'
        db.create_table('customer_customerreportnames', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('invoice_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('cash_tally_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('customer', ['CustomerReportNames'])

        # Adding model 'CustomerAWBUsedLimit'
        db.create_table('customer_customerawbusedlimit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'])),
            ('awb_limit', self.gf('django.db.models.fields.IntegerField')(default=3000, max_length=6)),
        ))
        db.send_create_signal('customer', ['CustomerAWBUsedLimit'])


    def backwards(self, orm):
        # Deleting model 'Customer'
        db.delete_table('customer_customer')

        # Deleting model 'Shipper'
        db.delete_table('customer_shipper')

        # Deleting model 'ShipperMapping'
        db.delete_table('customer_shippermapping')

        # Deleting model 'Product'
        db.delete_table('customer_product')

        # Deleting model 'CashOnDelivery'
        db.delete_table('customer_cashondelivery')

        # Deleting model 'CashOnDeliveryZone'
        db.delete_table('customer_cashondeliveryzone')

        # Deleting model 'FuelSurcharge'
        db.delete_table('customer_fuelsurcharge')

        # Deleting model 'FuelSurchargeZone'
        db.delete_table('customer_fuelsurchargezone')

        # Removing M2M table for field product on 'FuelSurchargeZone'
        db.delete_table('customer_fuelsurchargezone_product')

        # Deleting model 'FreightSlab'
        db.delete_table('customer_freightslab')

        # Deleting model 'RateVersion'
        db.delete_table('customer_rateversion')

        # Deleting model 'ForwardFreightRate'
        db.delete_table('customer_forwardfreightrate')

        # Removing M2M table for field product on 'ForwardFreightRate'
        db.delete_table('customer_forwardfreightrate_product')

        # Deleting model 'FreightSlabCity'
        db.delete_table('customer_freightslabcity')

        # Removing M2M table for field product on 'FreightSlabCity'
        db.delete_table('customer_freightslabcity_product')

        # Deleting model 'FreightSlabOriginZone'
        db.delete_table('customer_freightslaboriginzone')

        # Removing M2M table for field product on 'FreightSlabOriginZone'
        db.delete_table('customer_freightslaboriginzone_product')

        # Deleting model 'FreightSlabDestZone'
        db.delete_table('customer_freightslabdestzone')

        # Removing M2M table for field product on 'FreightSlabDestZone'
        db.delete_table('customer_freightslabdestzone_product')

        # Deleting model 'FreightSlabZone'
        db.delete_table('customer_freightslabzone')

        # Deleting model 'CODFreightSlab'
        db.delete_table('customer_codfreightslab')

        # Deleting model 'CODFreightSlabZone'
        db.delete_table('customer_codfreightslabzone')

        # Deleting model 'RTSFreightSlab'
        db.delete_table('customer_rtsfreightslab')

        # Deleting model 'RTSFreightSlabZone'
        db.delete_table('customer_rtsfreightslabzone')

        # Deleting model 'ReverseFreightSlab'
        db.delete_table('customer_reversefreightslab')

        # Deleting model 'ReverseFreightSlabZone'
        db.delete_table('customer_reversefreightslabzone')

        # Deleting model 'SDLSlab'
        db.delete_table('customer_sdlslab')

        # Deleting model 'SDDZone'
        db.delete_table('customer_sddzone')

        # Removing M2M table for field pincode on 'SDDZone'
        db.delete_table('customer_sddzone_pincode')

        # Deleting model 'SDDSlabZone'
        db.delete_table('customer_sddslabzone')

        # Deleting model 'ExceptionMaster'
        db.delete_table('customer_exceptionmaster')

        # Deleting model 'BrandedFleetCustomer'
        db.delete_table('customer_brandedfleetcustomer')

        # Deleting model 'BrandedFullTimeEmployeeCustomer'
        db.delete_table('customer_brandedfulltimeemployeecustomer')

        # Deleting model 'Remittance'
        db.delete_table('customer_remittance')

        # Deleting model 'VolumetricWeightDivisor'
        db.delete_table('customer_volumetricweightdivisor')

        # Deleting model 'MinActualWeight'
        db.delete_table('customer_minactualweight')

        # Deleting model 'SDLSlabCustomer'
        db.delete_table('customer_sdlslabcustomer')

        # Deleting model 'CustomerAPI'
        db.delete_table('customer_customerapi')

        # Deleting model 'RTSFreightZone'
        db.delete_table('customer_rtsfreightzone')

        # Deleting model 'RTSFuelZone'
        db.delete_table('customer_rtsfuelzone')

        # Deleting model 'RTSFreight'
        db.delete_table('customer_rtsfreight')

        # Deleting model 'RTSFuel'
        db.delete_table('customer_rtsfuel')

        # Deleting model 'RTSFreightSlabRate'
        db.delete_table('customer_rtsfreightslabrate')

        # Deleting model 'SubcustomerDetailsUpload'
        db.delete_table('customer_subcustomerdetailsupload')

        # Deleting model 'CustomerReportNames'
        db.delete_table('customer_customerreportnames')

        # Deleting model 'CustomerAWBUsedLimit'
        db.delete_table('customer_customerawbusedlimit')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'customer.brandedfleetcustomer': {
            'Meta': {'object_name': 'BrandedFleetCustomer'},
            'branded_fleet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.BrandedFleet']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_of_fleet': ('django.db.models.fields.IntegerField', [], {'max_length': '3'})
        },
        'customer.brandedfulltimeemployeecustomer': {
            'Meta': {'object_name': 'BrandedFullTimeEmployeeCustomer'},
            'branded_full_time_employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.BrandedFullTimeEmployee']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_of_employee': ('django.db.models.fields.IntegerField', [], {'max_length': '3'})
        },
        'customer.cashondelivery': {
            'COD_service_charge': ('django.db.models.fields.FloatField', [], {}),
            'Meta': {'object_name': 'CashOnDelivery'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'effective_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'end_range': ('django.db.models.fields.FloatField', [], {}),
            'flat_COD_charge': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_COD_charge': ('django.db.models.fields.FloatField', [], {}),
            'start_range': ('django.db.models.fields.FloatField', [], {})
        },
        'customer.cashondeliveryzone': {
            'COD_service_charge': ('django.db.models.fields.FloatField', [], {}),
            'Meta': {'object_name': 'CashOnDeliveryZone'},
            'c_zone_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'c_zone_dest'", 'to': "orm['location.Zone']"}),
            'c_zone_org': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'c_zone_org'", 'to': "orm['location.Zone']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'end_range': ('django.db.models.fields.FloatField', [], {}),
            'flat_COD_charge': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_COD_charge': ('django.db.models.fields.FloatField', [], {}),
            'start_range': ('django.db.models.fields.FloatField', [], {})
        },
        'customer.codfreightslab': {
            'Meta': {'object_name': 'CODFreightSlab'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '500', 'max_length': '5'}),
            'weight_rate': ('django.db.models.fields.FloatField', [], {'default': '35'})
        },
        'customer.codfreightslabzone': {
            'Meta': {'object_name': 'CODFreightSlabZone'},
            'freight_slab': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.CODFreightSlab']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate_per_slab': ('django.db.models.fields.FloatField', [], {'default': '20'}),
            'zone_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cod_zone_dest'", 'to': "orm['location.Zone']"}),
            'zone_org': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cod_zone_org'", 'to': "orm['location.Zone']"})
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
            'deactivation_date': ('django.db.models.fields.DateField', [], {}),
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
            'zone_label': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['location.ZoneLabel']", 'null': 'True', 'blank': 'True'})
        },
        'customer.customerapi': {
            'Meta': {'object_name': 'CustomerAPI'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'customer.customerawbusedlimit': {
            'Meta': {'object_name': 'CustomerAWBUsedLimit'},
            'awb_limit': ('django.db.models.fields.IntegerField', [], {'default': '3000', 'max_length': '6'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'customer.customerreportnames': {
            'Meta': {'object_name': 'CustomerReportNames'},
            'cash_tally_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'customer.exceptionmaster': {
            'Meta': {'object_name': 'ExceptionMaster'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'admin_contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']"}),
            'contact_customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contact_customer'", 'to': "orm['customer.Customer']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fk_customer'", 'to': "orm['customer.Customer']"}),
            'exception_code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meaning': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'customer.forwardfreightrate': {
            'Meta': {'object_name': 'ForwardFreightRate'},
            'dest_zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ff_dest_zone'", 'to': "orm['location.Zone']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['ecomm_admin.Mode']"}),
            'org_zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ff_org_zone'", 'to': "orm['location.Zone']"}),
            'product': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['customer.Product']", 'null': 'True', 'blank': 'True'}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6', 'db_index': 'True'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6', 'db_index': 'True'}),
            'rate_per_slab': ('django.db.models.fields.FloatField', [], {'default': '20'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '500', 'max_length': '5'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.RateVersion']"})
        },
        'customer.freightslab': {
            'Meta': {'object_name': 'FreightSlab'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '500', 'max_length': '5'}),
            'weight_rate': ('django.db.models.fields.FloatField', [], {'default': '35'})
        },
        'customer.freightslabcity': {
            'Meta': {'object_name': 'FreightSlabCity'},
            'city_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'city_dest'", 'to': "orm['location.City']"}),
            'city_org': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'city_org'", 'to': "orm['location.City']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'product': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['customer.Product']", 'null': 'True', 'blank': 'True'}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'rate_per_slab': ('django.db.models.fields.FloatField', [], {'default': '20'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '500', 'max_length': '5'}),
            'weight_rate': ('django.db.models.fields.FloatField', [], {'default': '35'})
        },
        'customer.freightslabdestzone': {
            'Meta': {'object_name': 'FreightSlabDestZone'},
            'city_org': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'freight_city_org'", 'to': "orm['location.City']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'dest_zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dest_zone'", 'to': "orm['location.Zone']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'product': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['customer.Product']", 'null': 'True', 'blank': 'True'}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'rate_per_slab': ('django.db.models.fields.FloatField', [], {'default': '20'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '500', 'max_length': '5'}),
            'weight_rate': ('django.db.models.fields.FloatField', [], {'default': '35'})
        },
        'customer.freightslaboriginzone': {
            'Meta': {'object_name': 'FreightSlabOriginZone'},
            'city_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'freight_city_dest'", 'to': "orm['location.City']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'org_zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'org_zone'", 'to': "orm['location.Zone']"}),
            'product': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['customer.Product']", 'null': 'True', 'blank': 'True'}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'rate_per_slab': ('django.db.models.fields.FloatField', [], {'default': '20'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '500', 'max_length': '5'}),
            'weight_rate': ('django.db.models.fields.FloatField', [], {'default': '35'})
        },
        'customer.freightslabzone': {
            'Meta': {'object_name': 'FreightSlabZone'},
            'freight_slab': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.FreightSlab']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate_per_slab': ('django.db.models.fields.FloatField', [], {'default': '20'}),
            'zone_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'zone_dest'", 'to': "orm['location.Zone']"}),
            'zone_org': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'zone_org'", 'to': "orm['location.Zone']"})
        },
        'customer.fuelsurcharge': {
            'Meta': {'object_name': 'FuelSurcharge'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'effective_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'flat_fuel_surcharge': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'fuelsurcharge_min_fuel_rate': ('django.db.models.fields.FloatField', [], {}),
            'fuelsurcharge_min_rate': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_fuel_surcharge': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'customer.fuelsurchargezone': {
            'Meta': {'object_name': 'FuelSurchargeZone'},
            'f_zone_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'f_zone_dest'", 'to': "orm['location.Zone']"}),
            'f_zone_org': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'f_zone_org'", 'to': "orm['location.Zone']"}),
            'flat_fuel_surcharge': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'fuelsurcharge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.FuelSurcharge']"}),
            'fuelsurcharge_min_fuel_rate': ('django.db.models.fields.FloatField', [], {}),
            'fuelsurcharge_min_rate': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_fuel_surcharge': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['customer.Product']", 'null': 'True', 'blank': 'True'})
        },
        'customer.minactualweight': {
            'Meta': {'object_name': 'MinActualWeight'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {})
        },
        'customer.product': {
            'Meta': {'object_name': 'Product'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'customer.rateversion': {
            'Meta': {'object_name': 'RateVersion'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'effective_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'customer.remittance': {
            'Meta': {'object_name': 'Remittance'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'bank_ref_number': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remitted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'remitted_by'", 'null': 'True', 'to': "orm['auth.User']"}),
            'remitted_on': ('django.db.models.fields.DateField', [], {}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'customer.reversefreightslab': {
            'Meta': {'object_name': 'ReverseFreightSlab'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '500', 'max_length': '5'}),
            'weight_rate': ('django.db.models.fields.FloatField', [], {'default': '35'})
        },
        'customer.reversefreightslabzone': {
            'Meta': {'object_name': 'ReverseFreightSlabZone'},
            'freight_slab': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.ReverseFreightSlab']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate_per_slab': ('django.db.models.fields.FloatField', [], {'default': '20'}),
            'zone_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rev_zone_dest'", 'to': "orm['location.Zone']"}),
            'zone_org': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rev_zone_org'", 'to': "orm['location.Zone']"})
        },
        'customer.rtsfreight': {
            'Meta': {'object_name': 'RTSFreight'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'customer.rtsfreightslab': {
            'Meta': {'object_name': 'RTSFreightSlab'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '500', 'max_length': '5'}),
            'weight_rate': ('django.db.models.fields.FloatField', [], {'default': '35'})
        },
        'customer.rtsfreightslabrate': {
            'Meta': {'object_name': 'RTSFreightSlabRate'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'freightslab_dest'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'normal_applicable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'freightslab_origin'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '1000', 'max_length': '5'})
        },
        'customer.rtsfreightslabzone': {
            'Meta': {'object_name': 'RTSFreightSlabZone'},
            'freight_slab': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.RTSFreightSlab']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate_per_slab': ('django.db.models.fields.FloatField', [], {'default': '20'}),
            'zone_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rts_zone_dest'", 'to': "orm['location.Zone']"}),
            'zone_org': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rts_zone_org'", 'to': "orm['location.Zone']"})
        },
        'customer.rtsfreightzone': {
            'Meta': {'object_name': 'RTSFreightZone'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'freight_dest'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'freight_slab': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.FreightSlab']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'freight_origin'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'customer.rtsfuel': {
            'Meta': {'object_name': 'RTSFuel'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'customer.rtsfuelzone': {
            'Meta': {'object_name': 'RTSFuelZone'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fuel_dest'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fuel_origin'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'customer.sddslabzone': {
            'Meta': {'object_name': 'SDDSlabZone'},
            'freight_slab': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.FreightSlab']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate_per_slab': ('django.db.models.fields.FloatField', [], {'default': '20'}),
            'sddzone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.SDDZone']"}),
            'zone_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sdd_zone_dest'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'zone_org': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sdd_zone_org'", 'null': 'True', 'to': "orm['location.Zone']"})
        },
        'customer.sddzone': {
            'Meta': {'object_name': 'SDDZone'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'pincode': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sddzone_pincode'", 'symmetrical': 'False', 'to': "orm['location.Pincode']"}),
            'shortcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'customer.sdlslab': {
            'Meta': {'object_name': 'SDLSlab'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '1000', 'max_length': '5'}),
            'weight_rate': ('django.db.models.fields.IntegerField', [], {'default': '100', 'max_length': '5'})
        },
        'customer.sdlslabcustomer': {
            'Meta': {'object_name': 'SDLSlabCustomer'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'range_from': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'range_to': ('django.db.models.fields.IntegerField', [], {'default': '999999', 'max_length': '6'}),
            'slab': ('django.db.models.fields.IntegerField', [], {'default': '1000', 'max_length': '5'}),
            'weight_rate': ('django.db.models.fields.IntegerField', [], {'default': '100', 'max_length': '5'})
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
        'customer.shippermapping': {
            'Meta': {'object_name': 'ShipperMapping'},
            'forward_pincode': ('django.db.models.fields.IntegerField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'return_pincode': ('django.db.models.fields.IntegerField', [], {'max_length': '8'}),
            'shipper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"})
        },
        'customer.subcustomerdetailsupload': {
            'Meta': {'object_name': 'SubcustomerDetailsUpload'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'filepath': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'customer.volumetricweightdivisor': {
            'Meta': {'object_name': 'VolumetricWeightDivisor'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'divisor': ('django.db.models.fields.IntegerField', [], {'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'ecomm_admin.brandedfleet': {
            'Meta': {'object_name': 'BrandedFleet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'max_length': '5'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'ecomm_admin.brandedfulltimeemployee': {
            'Meta': {'object_name': 'BrandedFullTimeEmployee'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'max_length': '5'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
        'location.pincode': {
            'Meta': {'object_name': 'Pincode'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'area': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_of_discontinuance': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pickup_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pickup'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'pin_route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.PinRoutes']", 'null': 'True', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.IntegerField', [], {}),
            'return_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'return'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'sdl': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'service_center': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '1'})
        },
        'location.pinroutes': {
            'Meta': {'object_name': 'PinRoutes'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pinroute_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'processing_center': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        }
    }

    complete_apps = ['customer']