# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Shipment'
        db.create_table('service_centre_shipment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pickup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipment_pickup', null=True, to=orm['pickup.PickupRegistration'])),
            ('reverse_pickup', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('return_shipment', self.gf('django.db.models.fields.SmallIntegerField')(default=False)),
            ('airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')()),
            ('order_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('product_type', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('shipper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('consignee', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('consignee_address1', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('consignee_address2', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('consignee_address3', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('consignee_address4', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('destination_city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('pincode', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('manifest_location', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='manifest_location', null=True, to=orm['location.ServiceCenter'])),
            ('service_centre', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipment_sc', null=True, to=orm['location.ServiceCenter'])),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc', null=True, to=orm['location.ServiceCenter'])),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('mobile', self.gf('django.db.models.fields.BigIntegerField')(default=0, null=True, blank=True)),
            ('telephone', self.gf('django.db.models.fields.CharField')(default=0, max_length=100, null=True, blank=True)),
            ('item_description', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('pieces', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('declared_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('length', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('breadth', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status_type', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('remark', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ref_airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipment_origin_sc', null=True, to=orm['location.ServiceCenter'])),
            ('rts_reason', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rts_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('inscan_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('rts_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True, blank=True)),
            ('rd_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True, blank=True)),
            ('rto_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True, blank=True)),
            ('sdd', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True, blank=True)),
            ('rejection', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True, blank=True)),
            ('billing', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='billing_ships', null=True, to=orm['billing.Billing'])),
            ('sbilling', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subbilling_ships', null=True, to=orm['billing.BillingSubCustomer'])),
            ('sdl', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True, blank=True)),
            ('tab', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True, blank=True)),
            ('chargeable_weight', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('shipment_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['Shipment'])

        # Adding model 'ShipmentExtension'
        db.create_table('service_centre_shipmentextension', (
            ('shipment', self.gf('django.db.models.fields.related.OneToOneField')(related_name='shipext', unique=True, primary_key=True, to=orm['service_centre.Shipment'])),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipextraorg', null=True, to=orm['location.ServiceCenter'])),
            ('subcust_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'], null=True, blank=True)),
            ('zone_origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipextrazono', null=True, to=orm['location.Zone'])),
            ('zone_destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipextrazond', null=True, to=orm['location.Zone'])),
            ('bagging_origin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shipextraborg', null=True, to=orm['location.ServiceCenter'])),
            ('bagging_destination', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shipextrabdes', null=True, to=orm['location.ServiceCenter'])),
            ('delivered_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.DecimalField')(default=0.0, null=True, max_digits=8, decimal_places=2)),
            ('lon', self.gf('django.db.models.fields.DecimalField')(default=0.0, null=True, max_digits=8, decimal_places=2)),
            ('status_bk', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('current_sc_bk', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipextracsc', null=True, to=orm['location.ServiceCenter'])),
            ('current_return_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipextracod', null=True, to=orm['location.ServiceCenter'])),
            ('return_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('original_pincode', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('bag_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('orig_expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('recieved_by', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('su_rem', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('firstsu_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('firstsu_rc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipextfirstsurc', null=True, to=orm['ecomm_admin.ShipmentStatusMaster'])),
            ('prev_su_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('original_act_weight', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('original_vol_weight', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('misroute_code', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipextmisroutecode', null=True, to=orm['ecomm_admin.ShipmentStatusMaster'])),
            ('delay_code', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipextdelaycode', null=True, to=orm['ecomm_admin.ShipmentStatusMaster'])),
            ('rev_shipment', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='shipextrevshipment', unique=True, null=True, to=orm['service_centre.Shipment'])),
            ('collected_amount', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('upd_product_type', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('cash_tally_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('cash_deposit_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('partial_payment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='shipextproduct', null=True, to=orm['customer.Product'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentExtension'])

        # Adding model 'ReverseShipment'
        db.create_table('service_centre_reverseshipment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reverse_pickup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='rev_pickup', null=True, to=orm['pickup.ReversePickupRegistration'])),
            ('pickup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='normal_pickup', null=True, to=orm['pickup.PickupRegistration'])),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='normal_shipment_pickup', null=True, to=orm['service_centre.Shipment'])),
            ('revpickup_status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('order_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('product_type', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('shipper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('vendor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Shipper'], null=True, blank=True)),
            ('pickup_consignee', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('pickup_consignee_address1', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('pickup_consignee_address2', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('pickup_consignee_address3', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('pickup_consignee_address4', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('pickup_pincode', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pickup_service_centre', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='rev_shipment_sc', null=True, to=orm['location.ServiceCenter'])),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='rev_current_sc', null=True, to=orm['location.ServiceCenter'])),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('mobile', self.gf('django.db.models.fields.BigIntegerField')(default=0, null=True, blank=True)),
            ('telephone', self.gf('django.db.models.fields.CharField')(default=0, max_length=100, null=True, blank=True)),
            ('item_description', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('pieces', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('declared_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('volumetric_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('length', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('breadth', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('status_type', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.PickupStatusMaster'], null=True, blank=True)),
            ('remark', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ref_airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('original_dest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='rev_shipment_origin_sc', null=True, to=orm['location.ServiceCenter'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['ReverseShipment'])

        # Adding model 'CODCharge'
        db.create_table('service_centre_codcharge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('cod_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('remittance_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('remitted_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('remitted_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['CODCharge'])

        # Adding model 'RemittanceCODCharge'
        db.create_table('service_centre_remittancecodcharge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('remittance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Remittance'])),
            ('codcharge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.CODCharge'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('bank_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bank_ref_number', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('service_centre', ['RemittanceCODCharge'])

        # Adding model 'CODDeposits'
        db.create_table('service_centre_coddeposits', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slip_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('codd_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('total_amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('collected_amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('bank_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')(auto_now_add=True, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='codd_origin', null=True, to=orm['location.ServiceCenter'])),
            ('deposited_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['CODDeposits'])

        # Adding M2M table for field denomination on 'CODDeposits'
        db.create_table('service_centre_coddeposits_denomination', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('coddeposits', models.ForeignKey(orm['service_centre.coddeposits'], null=False)),
            ('denomination', models.ForeignKey(orm['service_centre.denomination'], null=False))
        ))
        db.create_unique('service_centre_coddeposits_denomination', ['coddeposits_id', 'denomination_id'])

        # Adding M2M table for field cod_shipments on 'CODDeposits'
        db.create_table('service_centre_coddeposits_cod_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('coddeposits', models.ForeignKey(orm['service_centre.coddeposits'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('service_centre_coddeposits_cod_shipments', ['coddeposits_id', 'shipment_id'])

        # Adding model 'CODDepositShipments'
        db.create_table('service_centre_coddepositshipments', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('coddeposit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.CODDeposits'], null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['CODDepositShipments'])

        # Adding M2M table for field shipments on 'CODDepositShipments'
        db.create_table('service_centre_coddepositshipments_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('coddepositshipments', models.ForeignKey(orm['service_centre.coddepositshipments'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('service_centre_coddepositshipments_shipments', ['coddepositshipments_id', 'shipment_id'])

        # Adding model 'CODDepositsRemovedShipment'
        db.create_table('service_centre_coddepositsremovedshipment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['CODDepositsRemovedShipment'])

        # Adding model 'Denomination'
        db.create_table('service_centre_denomination', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('service_centre', ['Denomination'])

        # Adding model 'Order_price'
        db.create_table('service_centre_order_price', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('freight_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('fuel_surcharge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('valuable_cargo_handling_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('to_pay_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('rto_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdl_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('sdd_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('reverse_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('tab_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['Order_price'])

        # Adding model 'RTSPrice'
        db.create_table('service_centre_rtsprice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='rts_origin', null=True, to=orm['location.ServiceCenter'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='rts_dest', null=True, to=orm['location.ServiceCenter'])),
            ('charge_apply', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rate', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['RTSPrice'])

        # Adding model 'Bags'
        db.create_table('service_centre_bags', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('bag_size', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='bag_origin', null=True, to=orm['location.ServiceCenter'])),
            ('hub', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='bag_hub', null=True, to=orm['location.ServiceCenter'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='bag_dest', null=True, to=orm['location.ServiceCenter'])),
            ('bag_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bag_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('status_type', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('actual_weight', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='bag_sc', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['Bags'])

        # Adding M2M table for field shipments on 'Bags'
        db.create_table('service_centre_bags_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bags', models.ForeignKey(orm['service_centre.bags'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('service_centre_bags_shipments', ['bags_id', 'shipment_id'])

        # Adding M2M table for field ship_data on 'Bags'
        db.create_table('service_centre_bags_ship_data', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bags', models.ForeignKey(orm['service_centre.bags'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('service_centre_bags_ship_data', ['bags_id', 'shipment_id'])

        # Adding model 'Connection'
        db.create_table('service_centre_connection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('coloader', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='connection_coloader', null=True, to=orm['ecomm_admin.Coloader'])),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='conn_origin', null=True, to=orm['location.ServiceCenter'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='connection_dest', null=True, to=orm['location.ServiceCenter'])),
            ('vehicle_number', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('connection_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['Connection'])

        # Adding M2M table for field bags on 'Connection'
        db.create_table('service_centre_connection_bags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('connection', models.ForeignKey(orm['service_centre.connection'], null=False)),
            ('bags', models.ForeignKey(orm['service_centre.bags'], null=False))
        ))
        db.create_unique('service_centre_connection_bags', ['connection_id', 'bags_id'])

        # Adding model 'Octroi'
        db.create_table('service_centre_octroi', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='oct_origin', to=orm['location.ServiceCenter'])),
            ('octroi_slip_no', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('total_amount', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('total_ship', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('service_centre', ['Octroi'])

        # Adding model 'OctroiShipments'
        db.create_table('service_centre_octroishipments', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'], unique=True)),
            ('octroi', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Octroi'])),
            ('serial_no', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('shipper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
            ('octroi_billing', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='octroi_billing', null=True, to=orm['octroi.OctroiBilling'])),
            ('octroi_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('octroi_ecom_charge', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('receipt_number', self.gf('django.db.models.fields.CharField')(default='', max_length=20)),
        ))
        db.send_create_signal('service_centre', ['OctroiShipments'])

        # Adding model 'OctroiAirportConfirmation'
        db.create_table('service_centre_octroiairportconfirmation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('airportconfirmation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.AirportConfirmation'])),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'], unique=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['OctroiAirportConfirmation'])

        # Adding model 'NFormAirportConfirmation'
        db.create_table('service_centre_nformairportconfirmation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('airportconfirmation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.AirportConfirmation'])),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'], unique=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['NFormAirportConfirmation'])

        # Adding model 'NForm'
        db.create_table('service_centre_nform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nhform_origin', to=orm['location.ServiceCenter'])),
            ('nform_slip_no', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('total_amount', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('total_ship', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('service_centre', ['NForm'])

        # Adding model 'NFormShipments'
        db.create_table('service_centre_nformshipments', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'], unique=True)),
            ('nhform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.NForm'])),
            ('serial_no', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('shipper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['NFormShipments'])

        # Adding model 'RunCode'
        db.create_table('service_centre_runcode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('coloader', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='runcode_coloader', null=True, to=orm['ecomm_admin.Coloader'])),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='runcode_origin', null=True, to=orm['location.ServiceCenter'])),
            ('vehicle_number', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('runcode_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['RunCode'])

        # Adding M2M table for field destination on 'RunCode'
        db.create_table('service_centre_runcode_destination', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('runcode', models.ForeignKey(orm['service_centre.runcode'], null=False)),
            ('servicecenter', models.ForeignKey(orm['location.servicecenter'], null=False))
        ))
        db.create_unique('service_centre_runcode_destination', ['runcode_id', 'servicecenter_id'])

        # Adding M2M table for field connection on 'RunCode'
        db.create_table('service_centre_runcode_connection', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('runcode', models.ForeignKey(orm['service_centre.runcode'], null=False)),
            ('connection', models.ForeignKey(orm['service_centre.connection'], null=False))
        ))
        db.create_unique('service_centre_runcode_connection', ['runcode_id', 'connection_id'])

        # Adding model 'AirportConfirmation'
        db.create_table('service_centre_airportconfirmation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('run_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.RunCode'], null=True, blank=True)),
            ('flight_num', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('std', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('atd', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('num_of_bags', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='origin_ac', null=True, to=orm['location.ServiceCenter'])),
            ('cnote', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('status_code', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['AirportConfirmation'])

        # Adding model 'ReverseOutscan'
        db.create_table('service_centre_reverseoutscan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('route', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='revoutscan_origin', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ReverseOutscan'])

        # Adding model 'ReverseOutscanShipment'
        db.create_table('service_centre_reverseoutscanshipment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reverseshipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.ReverseShipment'])),
            ('outscan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.ReverseOutscan'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('serial', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['ReverseOutscanShipment'])

        # Adding model 'DeliveryOutscan'
        db.create_table('service_centre_deliveryoutscan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('route', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='outscan_origin', null=True, to=orm['location.ServiceCenter'])),
            ('collection_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('amount_to_be_collected', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('amount_collected', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('amount_mismatch', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('mismatch', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('cod_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1, null=True, blank=True)),
            ('unupdated_count', self.gf('django.db.models.fields.IntegerField')(default=-1, null=True, blank=True)),
            ('mobile_no', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['DeliveryOutscan'])

        # Adding M2M table for field shipments on 'DeliveryOutscan'
        db.create_table('service_centre_deliveryoutscan_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('deliveryoutscan', models.ForeignKey(orm['service_centre.deliveryoutscan'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('service_centre_deliveryoutscan_shipments', ['deliveryoutscan_id', 'shipment_id'])

        # Adding model 'OutscanShipments'
        db.create_table('service_centre_outscanshipments', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('outscan', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('awb', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('serial', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('service_centre', ['OutscanShipments'])

        # Adding unique constraint on 'OutscanShipments', fields ['outscan', 'serial']
        db.create_unique('service_centre_outscanshipments', ['outscan', 'serial'])

        # Adding model 'DOShipment'
        db.create_table('service_centre_doshipment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('deliveryoutscan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.DeliveryOutscan'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['DOShipment'])

        # Adding unique constraint on 'DOShipment', fields ['shipment', 'deliveryoutscan']
        db.create_unique('service_centre_doshipment', ['shipment_id', 'deliveryoutscan_id'])

        # Adding model 'CODDepositsOutscan'
        db.create_table('service_centre_coddepositsoutscan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('coddeposit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.CODDeposits'])),
            ('deliveryoutscan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.DeliveryOutscan'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['CODDepositsOutscan'])

        # Adding model 'CashAdjustment'
        db.create_table('service_centre_cashadjustment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deliveryoutscan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.DeliveryOutscan'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('remark', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['CashAdjustment'])

        # Adding model 'StatusUpdate'
        db.create_table('service_centre_statusupdate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('data_entry_emp_code', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='statsupd_dataemp', null=True, to=orm['authentication.EmployeeMaster'])),
            ('delivery_emp_code', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='statsupd_deliveryemp', null=True, to=orm['authentication.EmployeeMaster'])),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('recieved_by', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='statsupd_origin', null=True, to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('ajax_field', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['StatusUpdate'])

        # Adding model 'ShipmentAtLocation'
        db.create_table('service_centre_shipmentatlocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_entry_emp_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sal_origin', null=True, to=orm['location.ServiceCenter'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['ShipmentAtLocation'])

        # Adding M2M table for field scanned_shipments on 'ShipmentAtLocation'
        db.create_table('service_centre_shipmentatlocation_scanned_shipments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shipmentatlocation', models.ForeignKey(orm['service_centre.shipmentatlocation'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('service_centre_shipmentatlocation_scanned_shipments', ['shipmentatlocation_id', 'shipment_id'])

        # Adding M2M table for field total_undelivered_shipment on 'ShipmentAtLocation'
        db.create_table('service_centre_shipmentatlocation_total_undelivered_shipment', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shipmentatlocation', models.ForeignKey(orm['service_centre.shipmentatlocation'], null=False)),
            ('shipment', models.ForeignKey(orm['service_centre.shipment'], null=False))
        ))
        db.create_unique('service_centre_shipmentatlocation_total_undelivered_shipment', ['shipmentatlocation_id', 'shipment_id'])

        # Adding model 'SALScanType'
        db.create_table('service_centre_salscantype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.ShipmentAtLocation'], null=True, blank=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'], null=True, blank=True)),
            ('sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('scan_type', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('emp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['SALScanType'])

        # Adding unique constraint on 'SALScanType', fields ['sal', 'shipment']
        db.create_unique('service_centre_salscantype', ['sal_id', 'shipment_id'])

        # Adding model 'AirwaybillTally'
        db.create_table('service_centre_airwaybilltally', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='awbt_scanned', to=orm['service_centre.Shipment'])),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='awbt_origin', null=True, to=orm['location.ServiceCenter'])),
            ('cash_tally_emp_code', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='awbt_cashemp', null=True, to=orm['authentication.EmployeeMaster'])),
            ('delivery_emp_code', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='awbt_delemp', null=True, to=orm['authentication.EmployeeMaster'])),
            ('collectable_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('amount_collected', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['AirwaybillTally'])

        # Adding model 'DeliveryDeposits'
        db.create_table('service_centre_deliverydeposits', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bank_code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('bank_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('emp_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('emp_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('codd', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.CODDeposits'], null=True, blank=True)),
            ('sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='dd_origin', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['DeliveryDeposits'])

        # Adding model 'CashTallyHistory'
        db.create_table('service_centre_cashtallyhistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('current_collection', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('updated_amount', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True)),
            ('sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('coddeposit', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['service_centre.CODDeposits'], null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['CashTallyHistory'])

        # Adding model 'ShipmentHistory_2019_01'
        db.create_table('service_centre_shipmenthistory_2019_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1901', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2019_01'])

        # Adding model 'ShipmentHistory_2013_01'
        db.create_table('service_centre_shipmenthistory_2013_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1301', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_01'])

        # Adding model 'ShipmentHistory_2013_02'
        db.create_table('service_centre_shipmenthistory_2013_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1302', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_02'])

        # Adding model 'ShipmentHistory_2013_03'
        db.create_table('service_centre_shipmenthistory_2013_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1303', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_03'])

        # Adding model 'ShipmentHistory_2013_04'
        db.create_table('service_centre_shipmenthistory_2013_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1304', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_04'])

        # Adding model 'ShipmentHistory_2013_05'
        db.create_table('service_centre_shipmenthistory_2013_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1305', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_05'])

        # Adding model 'ShipmentHistory_2013_06'
        db.create_table('service_centre_shipmenthistory_2013_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1306', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_06'])

        # Adding model 'ShipmentHistory_2013_07'
        db.create_table('service_centre_shipmenthistory_2013_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1307', null=True, to=orm['location.ServiceCenter'])),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_07'])

        # Adding model 'ShipmentHistory_2013_08'
        db.create_table('service_centre_shipmenthistory_2013_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1308', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_08'])

        # Adding model 'ShipmentHistory_2013_09'
        db.create_table('service_centre_shipmenthistory_2013_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1309', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_09'])

        # Adding model 'ShipmentHistory_2013_10'
        db.create_table('service_centre_shipmenthistory_2013_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1310', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_10'])

        # Adding model 'ShipmentHistory_2013_11'
        db.create_table('service_centre_shipmenthistory_2013_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1311', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_11'])

        # Adding model 'ShipmentHistory_2013_12'
        db.create_table('service_centre_shipmenthistory_2013_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1312', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2013_12'])

        # Adding model 'ShipmentHistory_2014_01'
        db.create_table('service_centre_shipmenthistory_2014_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1401', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_01'])

        # Adding model 'ShipmentHistory_2014_02'
        db.create_table('service_centre_shipmenthistory_2014_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1402', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_02'])

        # Adding model 'ShipmentHistory_2014_03'
        db.create_table('service_centre_shipmenthistory_2014_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1403', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_03'])

        # Adding model 'ShipmentHistory_2014_04'
        db.create_table('service_centre_shipmenthistory_2014_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1404', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_04'])

        # Adding model 'ShipmentHistory_2014_05'
        db.create_table('service_centre_shipmenthistory_2014_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1405', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_05'])

        # Adding model 'ShipmentHistory_2014_06'
        db.create_table('service_centre_shipmenthistory_2014_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1406', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_06'])

        # Adding model 'ShipmentHistory_2014_07'
        db.create_table('service_centre_shipmenthistory_2014_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1407', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_07'])

        # Adding model 'ShipmentHistory_2014_08'
        db.create_table('service_centre_shipmenthistory_2014_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1408', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_08'])

        # Adding model 'ShipmentHistory_2014_09'
        db.create_table('service_centre_shipmenthistory_2014_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1409', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_09'])

        # Adding model 'ShipmentHistory_2014_10'
        db.create_table('service_centre_shipmenthistory_2014_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1410', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_10'])

        # Adding model 'ShipmentHistory_2014_11'
        db.create_table('service_centre_shipmenthistory_2014_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1411', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_11'])

        # Adding model 'ShipmentHistory_2014_12'
        db.create_table('service_centre_shipmenthistory_2014_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1412', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2014_12'])

        # Adding model 'ShipmentHistory_2015_01'
        db.create_table('service_centre_shipmenthistory_2015_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1501', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_01'])

        # Adding model 'ShipmentHistory_2015_02'
        db.create_table('service_centre_shipmenthistory_2015_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1502', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_02'])

        # Adding model 'ShipmentHistory_2015_03'
        db.create_table('service_centre_shipmenthistory_2015_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1503', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_03'])

        # Adding model 'ShipmentHistory_2015_04'
        db.create_table('service_centre_shipmenthistory_2015_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1504', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_04'])

        # Adding model 'ShipmentHistory_2015_05'
        db.create_table('service_centre_shipmenthistory_2015_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1505', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_05'])

        # Adding model 'ShipmentHistory_2015_06'
        db.create_table('service_centre_shipmenthistory_2015_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1506', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_06'])

        # Adding model 'ShipmentHistory_2015_07'
        db.create_table('service_centre_shipmenthistory_2015_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1507', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_07'])

        # Adding model 'ShipmentHistory_2015_08'
        db.create_table('service_centre_shipmenthistory_2015_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1508', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_08'])

        # Adding model 'ShipmentHistory_2015_09'
        db.create_table('service_centre_shipmenthistory_2015_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1509', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_09'])

        # Adding model 'ShipmentHistory_2015_10'
        db.create_table('service_centre_shipmenthistory_2015_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1510', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_10'])

        # Adding model 'ShipmentHistory_2015_11'
        db.create_table('service_centre_shipmenthistory_2015_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1511', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_11'])

        # Adding model 'ShipmentHistory_2015_12'
        db.create_table('service_centre_shipmenthistory_2015_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1512', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2015_12'])

        # Adding model 'ShipmentHistory_2016_01'
        db.create_table('service_centre_shipmenthistory_2016_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1601', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_01'])

        # Adding model 'ShipmentHistory_2016_03'
        db.create_table('service_centre_shipmenthistory_2016_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1603', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_03'])

        # Adding model 'ShipmentHistory_2016_04'
        db.create_table('service_centre_shipmenthistory_2016_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1604', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_04'])

        # Adding model 'ShipmentHistory_2016_05'
        db.create_table('service_centre_shipmenthistory_2016_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1605', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_05'])

        # Adding model 'ShipmentHistory_2016_06'
        db.create_table('service_centre_shipmenthistory_2016_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1606', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_06'])

        # Adding model 'ShipmentHistory_2016_07'
        db.create_table('service_centre_shipmenthistory_2016_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1607', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_07'])

        # Adding model 'ShipmentHistory_2016_08'
        db.create_table('service_centre_shipmenthistory_2016_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1608', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_08'])

        # Adding model 'ShipmentHistory_2016_09'
        db.create_table('service_centre_shipmenthistory_2016_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1609', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_09'])

        # Adding model 'ShipmentHistory_2016_10'
        db.create_table('service_centre_shipmenthistory_2016_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1610', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_10'])

        # Adding model 'ShipmentHistory_2016_11'
        db.create_table('service_centre_shipmenthistory_2016_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1611', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_11'])

        # Adding model 'ShipmentHistory_2016_12'
        db.create_table('service_centre_shipmenthistory_2016_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1612', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2016_12'])

        # Adding model 'ShipmentHistory_2017_01'
        db.create_table('service_centre_shipmenthistory_2017_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1701', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_01'])

        # Adding model 'ShipmentHistory_2017_02'
        db.create_table('service_centre_shipmenthistory_2017_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1702', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_02'])

        # Adding model 'ShipmentHistory_2017_03'
        db.create_table('service_centre_shipmenthistory_2017_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1703', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_03'])

        # Adding model 'ShipmentHistory_2017_04'
        db.create_table('service_centre_shipmenthistory_2017_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1704', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_04'])

        # Adding model 'ShipmentHistory_2017_05'
        db.create_table('service_centre_shipmenthistory_2017_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1705', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_05'])

        # Adding model 'ShipmentHistory_2017_06'
        db.create_table('service_centre_shipmenthistory_2017_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1706', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_06'])

        # Adding model 'ShipmentHistory_2017_07'
        db.create_table('service_centre_shipmenthistory_2017_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1707', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_07'])

        # Adding model 'ShipmentHistory_2017_08'
        db.create_table('service_centre_shipmenthistory_2017_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1708', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_08'])

        # Adding model 'ShipmentHistory_2017_09'
        db.create_table('service_centre_shipmenthistory_2017_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1709', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_09'])

        # Adding model 'ShipmentHistory_2017_10'
        db.create_table('service_centre_shipmenthistory_2017_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1710', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_10'])

        # Adding model 'ShipmentHistory_2017_11'
        db.create_table('service_centre_shipmenthistory_2017_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1711', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_11'])

        # Adding model 'ShipmentHistory_2017_12'
        db.create_table('service_centre_shipmenthistory_2017_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1712', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2017_12'])

        # Adding model 'ShipmentHistory_2018_01'
        db.create_table('service_centre_shipmenthistory_2018_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1801', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_01'])

        # Adding model 'ShipmentHistory_2018_02'
        db.create_table('service_centre_shipmenthistory_2018_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1802', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_02'])

        # Adding model 'ShipmentHistory_2018_03'
        db.create_table('service_centre_shipmenthistory_2018_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1803', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_03'])

        # Adding model 'ShipmentHistory_2018_04'
        db.create_table('service_centre_shipmenthistory_2018_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1804', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_04'])

        # Adding model 'ShipmentHistory_2018_05'
        db.create_table('service_centre_shipmenthistory_2018_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1805', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_05'])

        # Adding model 'ShipmentHistory_2018_06'
        db.create_table('service_centre_shipmenthistory_2018_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1806', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_06'])

        # Adding model 'ShipmentHistory_2018_07'
        db.create_table('service_centre_shipmenthistory_2018_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1807', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_07'])

        # Adding model 'ShipmentHistory_2018_08'
        db.create_table('service_centre_shipmenthistory_2018_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1808', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_08'])

        # Adding model 'ShipmentHistory_2018_09'
        db.create_table('service_centre_shipmenthistory_2018_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1809', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_09'])

        # Adding model 'ShipmentHistory_2018_10'
        db.create_table('service_centre_shipmenthistory_2018_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1810', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_10'])

        # Adding model 'ShipmentHistory_2018_11'
        db.create_table('service_centre_shipmenthistory_2018_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1811', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_11'])

        # Adding model 'ShipmentHistory_2018_12'
        db.create_table('service_centre_shipmenthistory_2018_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('current_sc', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_sc_hist1812', null=True, to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('service_centre', ['ShipmentHistory_2018_12'])

        # Adding model 'ConnectionQueue'
        db.create_table('service_centre_connectionqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('connection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Connection'])),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('service_centre', ['ConnectionQueue'])


    def backwards(self, orm):
        # Removing unique constraint on 'SALScanType', fields ['sal', 'shipment']
        db.delete_unique('service_centre_salscantype', ['sal_id', 'shipment_id'])

        # Removing unique constraint on 'DOShipment', fields ['shipment', 'deliveryoutscan']
        db.delete_unique('service_centre_doshipment', ['shipment_id', 'deliveryoutscan_id'])

        # Removing unique constraint on 'OutscanShipments', fields ['outscan', 'serial']
        db.delete_unique('service_centre_outscanshipments', ['outscan', 'serial'])

        # Deleting model 'Shipment'
        db.delete_table('service_centre_shipment')

        # Deleting model 'ShipmentExtension'
        db.delete_table('service_centre_shipmentextension')

        # Deleting model 'ReverseShipment'
        db.delete_table('service_centre_reverseshipment')

        # Deleting model 'CODCharge'
        db.delete_table('service_centre_codcharge')

        # Deleting model 'RemittanceCODCharge'
        db.delete_table('service_centre_remittancecodcharge')

        # Deleting model 'CODDeposits'
        db.delete_table('service_centre_coddeposits')

        # Removing M2M table for field denomination on 'CODDeposits'
        db.delete_table('service_centre_coddeposits_denomination')

        # Removing M2M table for field cod_shipments on 'CODDeposits'
        db.delete_table('service_centre_coddeposits_cod_shipments')

        # Deleting model 'CODDepositShipments'
        db.delete_table('service_centre_coddepositshipments')

        # Removing M2M table for field shipments on 'CODDepositShipments'
        db.delete_table('service_centre_coddepositshipments_shipments')

        # Deleting model 'CODDepositsRemovedShipment'
        db.delete_table('service_centre_coddepositsremovedshipment')

        # Deleting model 'Denomination'
        db.delete_table('service_centre_denomination')

        # Deleting model 'Order_price'
        db.delete_table('service_centre_order_price')

        # Deleting model 'RTSPrice'
        db.delete_table('service_centre_rtsprice')

        # Deleting model 'Bags'
        db.delete_table('service_centre_bags')

        # Removing M2M table for field shipments on 'Bags'
        db.delete_table('service_centre_bags_shipments')

        # Removing M2M table for field ship_data on 'Bags'
        db.delete_table('service_centre_bags_ship_data')

        # Deleting model 'Connection'
        db.delete_table('service_centre_connection')

        # Removing M2M table for field bags on 'Connection'
        db.delete_table('service_centre_connection_bags')

        # Deleting model 'Octroi'
        db.delete_table('service_centre_octroi')

        # Deleting model 'OctroiShipments'
        db.delete_table('service_centre_octroishipments')

        # Deleting model 'OctroiAirportConfirmation'
        db.delete_table('service_centre_octroiairportconfirmation')

        # Deleting model 'NFormAirportConfirmation'
        db.delete_table('service_centre_nformairportconfirmation')

        # Deleting model 'NForm'
        db.delete_table('service_centre_nform')

        # Deleting model 'NFormShipments'
        db.delete_table('service_centre_nformshipments')

        # Deleting model 'RunCode'
        db.delete_table('service_centre_runcode')

        # Removing M2M table for field destination on 'RunCode'
        db.delete_table('service_centre_runcode_destination')

        # Removing M2M table for field connection on 'RunCode'
        db.delete_table('service_centre_runcode_connection')

        # Deleting model 'AirportConfirmation'
        db.delete_table('service_centre_airportconfirmation')

        # Deleting model 'ReverseOutscan'
        db.delete_table('service_centre_reverseoutscan')

        # Deleting model 'ReverseOutscanShipment'
        db.delete_table('service_centre_reverseoutscanshipment')

        # Deleting model 'DeliveryOutscan'
        db.delete_table('service_centre_deliveryoutscan')

        # Removing M2M table for field shipments on 'DeliveryOutscan'
        db.delete_table('service_centre_deliveryoutscan_shipments')

        # Deleting model 'OutscanShipments'
        db.delete_table('service_centre_outscanshipments')

        # Deleting model 'DOShipment'
        db.delete_table('service_centre_doshipment')

        # Deleting model 'CODDepositsOutscan'
        db.delete_table('service_centre_coddepositsoutscan')

        # Deleting model 'CashAdjustment'
        db.delete_table('service_centre_cashadjustment')

        # Deleting model 'StatusUpdate'
        db.delete_table('service_centre_statusupdate')

        # Deleting model 'ShipmentAtLocation'
        db.delete_table('service_centre_shipmentatlocation')

        # Removing M2M table for field scanned_shipments on 'ShipmentAtLocation'
        db.delete_table('service_centre_shipmentatlocation_scanned_shipments')

        # Removing M2M table for field total_undelivered_shipment on 'ShipmentAtLocation'
        db.delete_table('service_centre_shipmentatlocation_total_undelivered_shipment')

        # Deleting model 'SALScanType'
        db.delete_table('service_centre_salscantype')

        # Deleting model 'AirwaybillTally'
        db.delete_table('service_centre_airwaybilltally')

        # Deleting model 'DeliveryDeposits'
        db.delete_table('service_centre_deliverydeposits')

        # Deleting model 'CashTallyHistory'
        db.delete_table('service_centre_cashtallyhistory')

        # Deleting model 'ShipmentHistory_2019_01'
        db.delete_table('service_centre_shipmenthistory_2019_01')

        # Deleting model 'ShipmentHistory_2013_01'
        db.delete_table('service_centre_shipmenthistory_2013_01')

        # Deleting model 'ShipmentHistory_2013_02'
        db.delete_table('service_centre_shipmenthistory_2013_02')

        # Deleting model 'ShipmentHistory_2013_03'
        db.delete_table('service_centre_shipmenthistory_2013_03')

        # Deleting model 'ShipmentHistory_2013_04'
        db.delete_table('service_centre_shipmenthistory_2013_04')

        # Deleting model 'ShipmentHistory_2013_05'
        db.delete_table('service_centre_shipmenthistory_2013_05')

        # Deleting model 'ShipmentHistory_2013_06'
        db.delete_table('service_centre_shipmenthistory_2013_06')

        # Deleting model 'ShipmentHistory_2013_07'
        db.delete_table('service_centre_shipmenthistory_2013_07')

        # Deleting model 'ShipmentHistory_2013_08'
        db.delete_table('service_centre_shipmenthistory_2013_08')

        # Deleting model 'ShipmentHistory_2013_09'
        db.delete_table('service_centre_shipmenthistory_2013_09')

        # Deleting model 'ShipmentHistory_2013_10'
        db.delete_table('service_centre_shipmenthistory_2013_10')

        # Deleting model 'ShipmentHistory_2013_11'
        db.delete_table('service_centre_shipmenthistory_2013_11')

        # Deleting model 'ShipmentHistory_2013_12'
        db.delete_table('service_centre_shipmenthistory_2013_12')

        # Deleting model 'ShipmentHistory_2014_01'
        db.delete_table('service_centre_shipmenthistory_2014_01')

        # Deleting model 'ShipmentHistory_2014_02'
        db.delete_table('service_centre_shipmenthistory_2014_02')

        # Deleting model 'ShipmentHistory_2014_03'
        db.delete_table('service_centre_shipmenthistory_2014_03')

        # Deleting model 'ShipmentHistory_2014_04'
        db.delete_table('service_centre_shipmenthistory_2014_04')

        # Deleting model 'ShipmentHistory_2014_05'
        db.delete_table('service_centre_shipmenthistory_2014_05')

        # Deleting model 'ShipmentHistory_2014_06'
        db.delete_table('service_centre_shipmenthistory_2014_06')

        # Deleting model 'ShipmentHistory_2014_07'
        db.delete_table('service_centre_shipmenthistory_2014_07')

        # Deleting model 'ShipmentHistory_2014_08'
        db.delete_table('service_centre_shipmenthistory_2014_08')

        # Deleting model 'ShipmentHistory_2014_09'
        db.delete_table('service_centre_shipmenthistory_2014_09')

        # Deleting model 'ShipmentHistory_2014_10'
        db.delete_table('service_centre_shipmenthistory_2014_10')

        # Deleting model 'ShipmentHistory_2014_11'
        db.delete_table('service_centre_shipmenthistory_2014_11')

        # Deleting model 'ShipmentHistory_2014_12'
        db.delete_table('service_centre_shipmenthistory_2014_12')

        # Deleting model 'ShipmentHistory_2015_01'
        db.delete_table('service_centre_shipmenthistory_2015_01')

        # Deleting model 'ShipmentHistory_2015_02'
        db.delete_table('service_centre_shipmenthistory_2015_02')

        # Deleting model 'ShipmentHistory_2015_03'
        db.delete_table('service_centre_shipmenthistory_2015_03')

        # Deleting model 'ShipmentHistory_2015_04'
        db.delete_table('service_centre_shipmenthistory_2015_04')

        # Deleting model 'ShipmentHistory_2015_05'
        db.delete_table('service_centre_shipmenthistory_2015_05')

        # Deleting model 'ShipmentHistory_2015_06'
        db.delete_table('service_centre_shipmenthistory_2015_06')

        # Deleting model 'ShipmentHistory_2015_07'
        db.delete_table('service_centre_shipmenthistory_2015_07')

        # Deleting model 'ShipmentHistory_2015_08'
        db.delete_table('service_centre_shipmenthistory_2015_08')

        # Deleting model 'ShipmentHistory_2015_09'
        db.delete_table('service_centre_shipmenthistory_2015_09')

        # Deleting model 'ShipmentHistory_2015_10'
        db.delete_table('service_centre_shipmenthistory_2015_10')

        # Deleting model 'ShipmentHistory_2015_11'
        db.delete_table('service_centre_shipmenthistory_2015_11')

        # Deleting model 'ShipmentHistory_2015_12'
        db.delete_table('service_centre_shipmenthistory_2015_12')

        # Deleting model 'ShipmentHistory_2016_01'
        db.delete_table('service_centre_shipmenthistory_2016_01')

        # Deleting model 'ShipmentHistory_2016_03'
        db.delete_table('service_centre_shipmenthistory_2016_03')

        # Deleting model 'ShipmentHistory_2016_04'
        db.delete_table('service_centre_shipmenthistory_2016_04')

        # Deleting model 'ShipmentHistory_2016_05'
        db.delete_table('service_centre_shipmenthistory_2016_05')

        # Deleting model 'ShipmentHistory_2016_06'
        db.delete_table('service_centre_shipmenthistory_2016_06')

        # Deleting model 'ShipmentHistory_2016_07'
        db.delete_table('service_centre_shipmenthistory_2016_07')

        # Deleting model 'ShipmentHistory_2016_08'
        db.delete_table('service_centre_shipmenthistory_2016_08')

        # Deleting model 'ShipmentHistory_2016_09'
        db.delete_table('service_centre_shipmenthistory_2016_09')

        # Deleting model 'ShipmentHistory_2016_10'
        db.delete_table('service_centre_shipmenthistory_2016_10')

        # Deleting model 'ShipmentHistory_2016_11'
        db.delete_table('service_centre_shipmenthistory_2016_11')

        # Deleting model 'ShipmentHistory_2016_12'
        db.delete_table('service_centre_shipmenthistory_2016_12')

        # Deleting model 'ShipmentHistory_2017_01'
        db.delete_table('service_centre_shipmenthistory_2017_01')

        # Deleting model 'ShipmentHistory_2017_02'
        db.delete_table('service_centre_shipmenthistory_2017_02')

        # Deleting model 'ShipmentHistory_2017_03'
        db.delete_table('service_centre_shipmenthistory_2017_03')

        # Deleting model 'ShipmentHistory_2017_04'
        db.delete_table('service_centre_shipmenthistory_2017_04')

        # Deleting model 'ShipmentHistory_2017_05'
        db.delete_table('service_centre_shipmenthistory_2017_05')

        # Deleting model 'ShipmentHistory_2017_06'
        db.delete_table('service_centre_shipmenthistory_2017_06')

        # Deleting model 'ShipmentHistory_2017_07'
        db.delete_table('service_centre_shipmenthistory_2017_07')

        # Deleting model 'ShipmentHistory_2017_08'
        db.delete_table('service_centre_shipmenthistory_2017_08')

        # Deleting model 'ShipmentHistory_2017_09'
        db.delete_table('service_centre_shipmenthistory_2017_09')

        # Deleting model 'ShipmentHistory_2017_10'
        db.delete_table('service_centre_shipmenthistory_2017_10')

        # Deleting model 'ShipmentHistory_2017_11'
        db.delete_table('service_centre_shipmenthistory_2017_11')

        # Deleting model 'ShipmentHistory_2017_12'
        db.delete_table('service_centre_shipmenthistory_2017_12')

        # Deleting model 'ShipmentHistory_2018_01'
        db.delete_table('service_centre_shipmenthistory_2018_01')

        # Deleting model 'ShipmentHistory_2018_02'
        db.delete_table('service_centre_shipmenthistory_2018_02')

        # Deleting model 'ShipmentHistory_2018_03'
        db.delete_table('service_centre_shipmenthistory_2018_03')

        # Deleting model 'ShipmentHistory_2018_04'
        db.delete_table('service_centre_shipmenthistory_2018_04')

        # Deleting model 'ShipmentHistory_2018_05'
        db.delete_table('service_centre_shipmenthistory_2018_05')

        # Deleting model 'ShipmentHistory_2018_06'
        db.delete_table('service_centre_shipmenthistory_2018_06')

        # Deleting model 'ShipmentHistory_2018_07'
        db.delete_table('service_centre_shipmenthistory_2018_07')

        # Deleting model 'ShipmentHistory_2018_08'
        db.delete_table('service_centre_shipmenthistory_2018_08')

        # Deleting model 'ShipmentHistory_2018_09'
        db.delete_table('service_centre_shipmenthistory_2018_09')

        # Deleting model 'ShipmentHistory_2018_10'
        db.delete_table('service_centre_shipmenthistory_2018_10')

        # Deleting model 'ShipmentHistory_2018_11'
        db.delete_table('service_centre_shipmenthistory_2018_11')

        # Deleting model 'ShipmentHistory_2018_12'
        db.delete_table('service_centre_shipmenthistory_2018_12')

        # Deleting model 'ConnectionQueue'
        db.delete_table('service_centre_connectionqueue')


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
            'zone_label': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['location.ZoneLabel']", 'null': 'True', 'blank': 'True'})
        },
        'customer.product': {
            'Meta': {'object_name': 'Product'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        'customer.shipper': {
            'Meta': {'object_name': 'Shipper'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Address']", 'null': 'True', 'blank': 'True'}),
            'alias_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'ecomm_admin.coloader': {
            'Meta': {'object_name': 'Coloader'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.IntegerField', [], {'max_length': '0'})
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
        'ecomm_admin.pickupstatusmaster': {
            'Meta': {'object_name': 'PickupStatusMaster'},
            'code': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'code_description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'code_redirect': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        'octroi.octroibilling': {
            'Meta': {'object_name': 'OctroiBilling'},
            'adjustment': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'adjustment_cr': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'bill_generation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'bill_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'billing_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cess_higher_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'education_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'octroi_charge': ('django.db.models.fields.FloatField', [], {}),
            'octroi_ecom_charge': ('django.db.models.fields.FloatField', [], {}),
            'received': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'service_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.OctroiShipments']", 'symmetrical': 'False'}),
            'total_charge_pretax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_payable_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
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
        'pickup.reversepickupregistration': {
            'Meta': {'object_name': 'ReversePickupRegistration'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pickup': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['pickup.PickupRegistration']", 'null': 'True', 'blank': 'True'}),
            'pickup_date': ('django.db.models.fields.DateField', [], {}),
            'pickup_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'reverse_pickup': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.airportconfirmation': {
            'Meta': {'object_name': 'AirportConfirmation'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'atd': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cnote': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'flight_num': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_of_bags': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'origin_ac'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'run_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.RunCode']", 'null': 'True', 'blank': 'True'}),
            'status_code': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'std': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'service_centre.airwaybilltally': {
            'Meta': {'object_name': 'AirwaybillTally'},
            'amount_collected': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'cash_tally_emp_code': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'awbt_cashemp'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'delivery_emp_code': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'awbt_delemp'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'awbt_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'awbt_scanned'", 'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.bags': {
            'Meta': {'object_name': 'Bags'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'bag_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'bag_size': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bag_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'bag_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bag_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bag_dest'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'hub': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bag_hub'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bag_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'ship_data': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'shipment_data'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.Shipment']", 'symmetrical': 'False'}),
            'status_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'service_centre.cashadjustment': {
            'Meta': {'object_name': 'CashAdjustment'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deliveryoutscan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.DeliveryOutscan']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.cashtallyhistory': {
            'Meta': {'object_name': 'CashTallyHistory'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'coddeposit': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['service_centre.CODDeposits']", 'null': 'True', 'blank': 'True'}),
            'current_collection': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'updated_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'service_centre.codcharge': {
            'Meta': {'object_name': 'CODCharge'},
            'cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remittance_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'remitted_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'remitted_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.coddeposits': {
            'Meta': {'object_name': 'CODDeposits'},
            'bank_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'cod_shipments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'codd_shipments'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"}),
            'codd_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'collected_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'denomination': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'codd_denomination'", 'symmetrical': 'False', 'to': "orm['service_centre.Denomination']"}),
            'deposited_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'codd_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'slip_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'total_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'service_centre.coddepositshipments': {
            'Meta': {'object_name': 'CODDepositShipments'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'coddeposit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.CODDeposits']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.Shipment']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.coddepositsoutscan': {
            'Meta': {'object_name': 'CODDepositsOutscan'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'coddeposit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.CODDeposits']"}),
            'deliveryoutscan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.DeliveryOutscan']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'service_centre.coddepositsremovedshipment': {
            'Meta': {'object_name': 'CODDepositsRemovedShipment'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'service_centre.connection': {
            'Meta': {'object_name': 'Connection'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'bags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.Bags']", 'symmetrical': 'False'}),
            'coloader': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'connection_coloader'", 'null': 'True', 'to': "orm['ecomm_admin.Coloader']"}),
            'connection_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'connection_dest'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'conn_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'vehicle_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.connectionqueue': {
            'Meta': {'object_name': 'ConnectionQueue'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Connection']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'service_centre.deliverydeposits': {
            'Meta': {'object_name': 'DeliveryDeposits'},
            'amount': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'bank_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'codd': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.CODDeposits']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emp_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'emp_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'dd_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'service_centre.deliveryoutscan': {
            'Meta': {'object_name': 'DeliveryOutscan'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'amount_collected': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'amount_mismatch': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'amount_to_be_collected': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'collection_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mismatch': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'mobile_no': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'outscan_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.Shipment']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'unupdated_count': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.denomination': {
            'Meta': {'object_name': 'Denomination'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'service_centre.doshipment': {
            'Meta': {'unique_together': "(('shipment', 'deliveryoutscan'),)", 'object_name': 'DOShipment'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deliveryoutscan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.DeliveryOutscan']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'service_centre.nform': {
            'Meta': {'object_name': 'NForm'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nform_slip_no': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nhform_origin'", 'to': "orm['location.ServiceCenter']"}),
            'shipper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_amount': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_ship': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'service_centre.nformairportconfirmation': {
            'Meta': {'object_name': 'NFormAirportConfirmation'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'airportconfirmation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.AirportConfirmation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']", 'unique': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'service_centre.nformshipments': {
            'Meta': {'object_name': 'NFormShipments'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nhform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.NForm']"}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'serial_no': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']", 'unique': 'True'}),
            'shipper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'})
        },
        'service_centre.octroi': {
            'Meta': {'object_name': 'Octroi'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'octroi_slip_no': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'oct_origin'", 'to': "orm['location.ServiceCenter']"}),
            'shipper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_amount': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_ship': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'service_centre.octroiairportconfirmation': {
            'Meta': {'object_name': 'OctroiAirportConfirmation'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'airportconfirmation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.AirportConfirmation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']", 'unique': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'service_centre.octroishipments': {
            'Meta': {'object_name': 'OctroiShipments'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'octroi': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Octroi']"}),
            'octroi_billing': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'octroi_billing'", 'null': 'True', 'to': "orm['octroi.OctroiBilling']"}),
            'octroi_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'octroi_ecom_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'receipt_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'serial_no': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']", 'unique': 'True'}),
            'shipper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'service_centre.order_price': {
            'Meta': {'object_name': 'Order_price'},
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'tab_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.outscanshipments': {
            'Meta': {'unique_together': "(('outscan', 'serial'),)", 'object_name': 'OutscanShipments'},
            'awb': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'outscan': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'serial': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'service_centre.remittancecodcharge': {
            'Meta': {'object_name': 'RemittanceCODCharge'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'bank_ref_number': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'codcharge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.CODCharge']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remittance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Remittance']"})
        },
        'service_centre.reverseoutscan': {
            'Meta': {'object_name': 'ReverseOutscan'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'revoutscan_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.reverseoutscanshipment': {
            'Meta': {'object_name': 'ReverseOutscanShipment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'outscan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.ReverseOutscan']"}),
            'reverseshipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.ReverseShipment']"}),
            'serial': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'service_centre.reverseshipment': {
            'Meta': {'object_name': 'ReverseShipment'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'breadth': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rev_current_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'declared_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rev_shipment_origin_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'pickup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'normal_pickup'", 'null': 'True', 'to': "orm['pickup.PickupRegistration']"}),
            'pickup_consignee': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'pickup_consignee_address1': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'pickup_consignee_address2': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'pickup_consignee_address3': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'pickup_consignee_address4': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'pickup_pincode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pickup_service_centre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rev_shipment_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'pieces': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.PickupStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'ref_airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'reverse_pickup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rev_pickup'", 'null': 'True', 'to': "orm['pickup.ReversePickupRegistration']"}),
            'revpickup_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'normal_shipment_pickup'", 'null': 'True', 'to': "orm['service_centre.Shipment']"}),
            'shipper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'status_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'vendor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']", 'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.rtsprice': {
            'Meta': {'object_name': 'RTSPrice'},
            'charge_apply': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rts_dest'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rts_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.runcode': {
            'Meta': {'object_name': 'RunCode'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'coloader': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'runcode_coloader'", 'null': 'True', 'to': "orm['ecomm_admin.Coloader']"}),
            'connection': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.Connection']", 'symmetrical': 'False'}),
            'destination': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'runcode_dest'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['location.ServiceCenter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'runcode_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'runcode_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'vehicle_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.salscantype': {
            'Meta': {'unique_together': "(('sal', 'shipment'),)", 'object_name': 'SALScanType'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'emp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.ShipmentAtLocation']", 'null': 'True', 'blank': 'True'}),
            'sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'scan_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
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
        },
        'service_centre.shipmentatlocation': {
            'Meta': {'object_name': 'ShipmentAtLocation'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_entry_emp_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sal_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'scanned_shipments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sal_scanned'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_undelivered_shipment': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sal_total_undelivered'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"})
        },
        'service_centre.shipmentextension': {
            'Meta': {'object_name': 'ShipmentExtension'},
            'bag_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'bagging_destination': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shipextrabdes'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'bagging_origin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shipextraborg'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'cash_deposit_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cash_tally_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collected_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'current_return_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipextracod'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'current_sc_bk': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipextracsc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'delay_code': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipextdelaycode'", 'null': 'True', 'to': "orm['ecomm_admin.ShipmentStatusMaster']"}),
            'delivered_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'firstsu_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'firstsu_rc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipextfirstsurc'", 'null': 'True', 'to': "orm['ecomm_admin.ShipmentStatusMaster']"}),
            'lat': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'misroute_code': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipextmisroutecode'", 'null': 'True', 'to': "orm['ecomm_admin.ShipmentStatusMaster']"}),
            'orig_expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipextraorg'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'original_act_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'original_pincode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_vol_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'partial_payment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prev_su_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipextproduct'", 'null': 'True', 'to': "orm['customer.Product']"}),
            'recieved_by': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'return_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rev_shipment': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'shipextrevshipment'", 'unique': 'True', 'null': 'True', 'to': "orm['service_centre.Shipment']"}),
            'shipment': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'shipext'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['service_centre.Shipment']"}),
            'status_bk': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'su_rem': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'subcust_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']", 'null': 'True', 'blank': 'True'}),
            'upd_product_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'zone_destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipextrazond'", 'null': 'True', 'to': "orm['location.Zone']"}),
            'zone_origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipextrazono'", 'null': 'True', 'to': "orm['location.Zone']"})
        },
        'service_centre.shipmenthistory_2013_01': {
            'Meta': {'object_name': 'ShipmentHistory_2013_01'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1301'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_02': {
            'Meta': {'object_name': 'ShipmentHistory_2013_02'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1302'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_03': {
            'Meta': {'object_name': 'ShipmentHistory_2013_03'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1303'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_04': {
            'Meta': {'object_name': 'ShipmentHistory_2013_04'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1304'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_05': {
            'Meta': {'object_name': 'ShipmentHistory_2013_05'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1305'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_06': {
            'Meta': {'object_name': 'ShipmentHistory_2013_06'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1306'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_07': {
            'Meta': {'object_name': 'ShipmentHistory_2013_07'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1307'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_08': {
            'Meta': {'object_name': 'ShipmentHistory_2013_08'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1308'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_09': {
            'Meta': {'object_name': 'ShipmentHistory_2013_09'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1309'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_10': {
            'Meta': {'object_name': 'ShipmentHistory_2013_10'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1310'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_11': {
            'Meta': {'object_name': 'ShipmentHistory_2013_11'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1311'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2013_12': {
            'Meta': {'object_name': 'ShipmentHistory_2013_12'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1312'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_01': {
            'Meta': {'object_name': 'ShipmentHistory_2014_01'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1401'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_02': {
            'Meta': {'object_name': 'ShipmentHistory_2014_02'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1402'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_03': {
            'Meta': {'object_name': 'ShipmentHistory_2014_03'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1403'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_04': {
            'Meta': {'object_name': 'ShipmentHistory_2014_04'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1404'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_05': {
            'Meta': {'object_name': 'ShipmentHistory_2014_05'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1405'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_06': {
            'Meta': {'object_name': 'ShipmentHistory_2014_06'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1406'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_07': {
            'Meta': {'object_name': 'ShipmentHistory_2014_07'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1407'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_08': {
            'Meta': {'object_name': 'ShipmentHistory_2014_08'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1408'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_09': {
            'Meta': {'object_name': 'ShipmentHistory_2014_09'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1409'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_10': {
            'Meta': {'object_name': 'ShipmentHistory_2014_10'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1410'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_11': {
            'Meta': {'object_name': 'ShipmentHistory_2014_11'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1411'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2014_12': {
            'Meta': {'object_name': 'ShipmentHistory_2014_12'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1412'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_01': {
            'Meta': {'object_name': 'ShipmentHistory_2015_01'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1501'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_02': {
            'Meta': {'object_name': 'ShipmentHistory_2015_02'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1502'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_03': {
            'Meta': {'object_name': 'ShipmentHistory_2015_03'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1503'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_04': {
            'Meta': {'object_name': 'ShipmentHistory_2015_04'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1504'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_05': {
            'Meta': {'object_name': 'ShipmentHistory_2015_05'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1505'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_06': {
            'Meta': {'object_name': 'ShipmentHistory_2015_06'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1506'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_07': {
            'Meta': {'object_name': 'ShipmentHistory_2015_07'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1507'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_08': {
            'Meta': {'object_name': 'ShipmentHistory_2015_08'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1508'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_09': {
            'Meta': {'object_name': 'ShipmentHistory_2015_09'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1509'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_10': {
            'Meta': {'object_name': 'ShipmentHistory_2015_10'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1510'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_11': {
            'Meta': {'object_name': 'ShipmentHistory_2015_11'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1511'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2015_12': {
            'Meta': {'object_name': 'ShipmentHistory_2015_12'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1512'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_01': {
            'Meta': {'object_name': 'ShipmentHistory_2016_01'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1601'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_03': {
            'Meta': {'object_name': 'ShipmentHistory_2016_03'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1603'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_04': {
            'Meta': {'object_name': 'ShipmentHistory_2016_04'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1604'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_05': {
            'Meta': {'object_name': 'ShipmentHistory_2016_05'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1605'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_06': {
            'Meta': {'object_name': 'ShipmentHistory_2016_06'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1606'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_07': {
            'Meta': {'object_name': 'ShipmentHistory_2016_07'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1607'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_08': {
            'Meta': {'object_name': 'ShipmentHistory_2016_08'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1608'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_09': {
            'Meta': {'object_name': 'ShipmentHistory_2016_09'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1609'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_10': {
            'Meta': {'object_name': 'ShipmentHistory_2016_10'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1610'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_11': {
            'Meta': {'object_name': 'ShipmentHistory_2016_11'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1611'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2016_12': {
            'Meta': {'object_name': 'ShipmentHistory_2016_12'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1612'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_01': {
            'Meta': {'object_name': 'ShipmentHistory_2017_01'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1701'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_02': {
            'Meta': {'object_name': 'ShipmentHistory_2017_02'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1702'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_03': {
            'Meta': {'object_name': 'ShipmentHistory_2017_03'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1703'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_04': {
            'Meta': {'object_name': 'ShipmentHistory_2017_04'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1704'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_05': {
            'Meta': {'object_name': 'ShipmentHistory_2017_05'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1705'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_06': {
            'Meta': {'object_name': 'ShipmentHistory_2017_06'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1706'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_07': {
            'Meta': {'object_name': 'ShipmentHistory_2017_07'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1707'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_08': {
            'Meta': {'object_name': 'ShipmentHistory_2017_08'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1708'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_09': {
            'Meta': {'object_name': 'ShipmentHistory_2017_09'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1709'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_10': {
            'Meta': {'object_name': 'ShipmentHistory_2017_10'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1710'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_11': {
            'Meta': {'object_name': 'ShipmentHistory_2017_11'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1711'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2017_12': {
            'Meta': {'object_name': 'ShipmentHistory_2017_12'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1712'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_01': {
            'Meta': {'object_name': 'ShipmentHistory_2018_01'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1801'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_02': {
            'Meta': {'object_name': 'ShipmentHistory_2018_02'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1802'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_03': {
            'Meta': {'object_name': 'ShipmentHistory_2018_03'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1803'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_04': {
            'Meta': {'object_name': 'ShipmentHistory_2018_04'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1804'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_05': {
            'Meta': {'object_name': 'ShipmentHistory_2018_05'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1805'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_06': {
            'Meta': {'object_name': 'ShipmentHistory_2018_06'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1806'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_07': {
            'Meta': {'object_name': 'ShipmentHistory_2018_07'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1807'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_08': {
            'Meta': {'object_name': 'ShipmentHistory_2018_08'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1808'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_09': {
            'Meta': {'object_name': 'ShipmentHistory_2018_09'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1809'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_10': {
            'Meta': {'object_name': 'ShipmentHistory_2018_10'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1810'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_11': {
            'Meta': {'object_name': 'ShipmentHistory_2018_11'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1811'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2018_12': {
            'Meta': {'object_name': 'ShipmentHistory_2018_12'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1812'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.shipmenthistory_2019_01': {
            'Meta': {'object_name': 'ShipmentHistory_2019_01'},
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc_hist1901'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'employee_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'service_centre.statusupdate': {
            'Meta': {'object_name': 'StatusUpdate'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ajax_field': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'data_entry_emp_code': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsupd_dataemp'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'delivery_emp_code': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsupd_deliveryemp'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'statsupd_origin'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'recieved_by': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['service_centre']