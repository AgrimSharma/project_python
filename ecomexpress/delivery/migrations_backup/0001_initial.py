# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CreditcardDelivery'
        db.create_table('delivery_creditcarddelivery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('credit_card_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('credit_card_owner', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bank_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transaction_date', self.gf('django.db.models.fields.DateField')()),
            ('transaction_time', self.gf('django.db.models.fields.TimeField')()),
            ('collected_amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['CreditcardDelivery'])

        # Adding model 'UpdateCardPaymentModified'
        db.create_table('delivery_updatecardpaymentmodified', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('payment_type', self.gf('django.db.models.fields.IntegerField')(default=1, max_length=1)),
            ('airwaybill_number', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('airwaybill_amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('credit_payment_recvd_amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('delivery_centre_name', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('transaction_slip_no', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('transaction_date', self.gf('django.db.models.fields.DateField')()),
            ('remarks', self.gf('django.db.models.fields.TextField')()),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='employee', to=orm['authentication.EmployeeMaster'])),
            ('updated_employee', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='updated_employee', null=True, to=orm['authentication.EmployeeMaster'])),
            ('updated_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('corrected_employee', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='corrected_employee', null=True, to=orm['authentication.EmployeeMaster'])),
            ('corrected_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['UpdateCardPaymentModified'])

        # Adding model 'UpdateCardPayment'
        db.create_table('delivery_updatecardpayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('payment_type', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')()),
            ('airwaybill_amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('card_payment_recvd_amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('transaction_slip_no', self.gf('django.db.models.fields.BigIntegerField')()),
            ('transaction_date', self.gf('django.db.models.fields.DateField')()),
            ('remarks', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('delivery', ['UpdateCardPayment'])

        # Adding model 'CreditCardPaymentDeposit'
        db.create_table('delivery_creditcardpaymentdeposit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry_date', self.gf('django.db.models.fields.DateField')()),
            ('system_date', self.gf('django.db.models.fields.DateField')()),
            ('payment_type', self.gf('django.db.models.fields.SmallIntegerField')(default=1, max_length=1)),
            ('transaction_slip_no', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('transaction_date', self.gf('django.db.models.fields.DateField')()),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'])),
            ('updated_date', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['CreditCardPaymentDeposit'])

        # Adding model 'CreditPaymentAwbDetails'
        db.create_table('delivery_creditpaymentawbdetails', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creditcardpaymentdeposit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['delivery.CreditCardPaymentDeposit'])),
            ('shipment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Shipment'])),
            ('airwaybill_amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('credit_card_payment_received', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('balance', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('delivery_centre', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['CreditPaymentAwbDetails'])

        # Adding model 'DashboardVisiblity'
        db.create_table('delivery_dashboardvisiblity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.State'], null=True, blank=True)),
            ('ncr_state', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1, null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['DashboardVisiblity'])

        # Adding model 'BaggingHistory_2014_01'
        db.create_table('delivery_bagginghistory_2014_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_01'])

        # Adding model 'BaggingHistory_2014_02'
        db.create_table('delivery_bagginghistory_2014_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_02'])

        # Adding model 'BaggingHistory_2014_03'
        db.create_table('delivery_bagginghistory_2014_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_03'])

        # Adding model 'BaggingHistory_2014_04'
        db.create_table('delivery_bagginghistory_2014_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_04'])

        # Adding model 'BaggingHistory_2014_05'
        db.create_table('delivery_bagginghistory_2014_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_05'])

        # Adding model 'BaggingHistory_2014_06'
        db.create_table('delivery_bagginghistory_2014_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_06'])

        # Adding model 'BaggingHistory_2014_07'
        db.create_table('delivery_bagginghistory_2014_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_07'])

        # Adding model 'BaggingHistory_2014_08'
        db.create_table('delivery_bagginghistory_2014_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_08'])

        # Adding model 'BaggingHistory_2014_09'
        db.create_table('delivery_bagginghistory_2014_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_09'])

        # Adding model 'BaggingHistory_2014_10'
        db.create_table('delivery_bagginghistory_2014_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_10'])

        # Adding model 'BaggingHistory_2014_11'
        db.create_table('delivery_bagginghistory_2014_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_11'])

        # Adding model 'BaggingHistory_2014_12'
        db.create_table('delivery_bagginghistory_2014_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2014_12'])

        # Adding model 'BaggingHistory_2015_01'
        db.create_table('delivery_bagginghistory_2015_01', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_01'])

        # Adding model 'BaggingHistory_2015_02'
        db.create_table('delivery_bagginghistory_2015_02', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_02'])

        # Adding model 'BaggingHistory_2015_03'
        db.create_table('delivery_bagginghistory_2015_03', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_03'])

        # Adding model 'BaggingHistory_2015_04'
        db.create_table('delivery_bagginghistory_2015_04', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_04'])

        # Adding model 'BaggingHistory_2015_05'
        db.create_table('delivery_bagginghistory_2015_05', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_05'])

        # Adding model 'BaggingHistory_2015_06'
        db.create_table('delivery_bagginghistory_2015_06', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_06'])

        # Adding model 'BaggingHistory_2015_07'
        db.create_table('delivery_bagginghistory_2015_07', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_07'])

        # Adding model 'BaggingHistory_2015_08'
        db.create_table('delivery_bagginghistory_2015_08', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_08'])

        # Adding model 'BaggingHistory_2015_09'
        db.create_table('delivery_bagginghistory_2015_09', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_09'])

        # Adding model 'BaggingHistory_2015_10'
        db.create_table('delivery_bagginghistory_2015_10', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_10'])

        # Adding model 'BaggingHistory_2015_11'
        db.create_table('delivery_bagginghistory_2015_11', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_11'])

        # Adding model 'BaggingHistory_2015_12'
        db.create_table('delivery_bagginghistory_2015_12', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_centre.Bags'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.EmployeeMaster'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('expected_dod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('bag_sc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'], null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.ShipmentStatusMaster'], null=True, blank=True)),
        ))
        db.send_create_signal('delivery', ['BaggingHistory_2015_12'])


    def backwards(self, orm):
        # Deleting model 'CreditcardDelivery'
        db.delete_table('delivery_creditcarddelivery')

        # Deleting model 'UpdateCardPaymentModified'
        db.delete_table('delivery_updatecardpaymentmodified')

        # Deleting model 'UpdateCardPayment'
        db.delete_table('delivery_updatecardpayment')

        # Deleting model 'CreditCardPaymentDeposit'
        db.delete_table('delivery_creditcardpaymentdeposit')

        # Deleting model 'CreditPaymentAwbDetails'
        db.delete_table('delivery_creditpaymentawbdetails')

        # Deleting model 'DashboardVisiblity'
        db.delete_table('delivery_dashboardvisiblity')

        # Deleting model 'BaggingHistory_2014_01'
        db.delete_table('delivery_bagginghistory_2014_01')

        # Deleting model 'BaggingHistory_2014_02'
        db.delete_table('delivery_bagginghistory_2014_02')

        # Deleting model 'BaggingHistory_2014_03'
        db.delete_table('delivery_bagginghistory_2014_03')

        # Deleting model 'BaggingHistory_2014_04'
        db.delete_table('delivery_bagginghistory_2014_04')

        # Deleting model 'BaggingHistory_2014_05'
        db.delete_table('delivery_bagginghistory_2014_05')

        # Deleting model 'BaggingHistory_2014_06'
        db.delete_table('delivery_bagginghistory_2014_06')

        # Deleting model 'BaggingHistory_2014_07'
        db.delete_table('delivery_bagginghistory_2014_07')

        # Deleting model 'BaggingHistory_2014_08'
        db.delete_table('delivery_bagginghistory_2014_08')

        # Deleting model 'BaggingHistory_2014_09'
        db.delete_table('delivery_bagginghistory_2014_09')

        # Deleting model 'BaggingHistory_2014_10'
        db.delete_table('delivery_bagginghistory_2014_10')

        # Deleting model 'BaggingHistory_2014_11'
        db.delete_table('delivery_bagginghistory_2014_11')

        # Deleting model 'BaggingHistory_2014_12'
        db.delete_table('delivery_bagginghistory_2014_12')

        # Deleting model 'BaggingHistory_2015_01'
        db.delete_table('delivery_bagginghistory_2015_01')

        # Deleting model 'BaggingHistory_2015_02'
        db.delete_table('delivery_bagginghistory_2015_02')

        # Deleting model 'BaggingHistory_2015_03'
        db.delete_table('delivery_bagginghistory_2015_03')

        # Deleting model 'BaggingHistory_2015_04'
        db.delete_table('delivery_bagginghistory_2015_04')

        # Deleting model 'BaggingHistory_2015_05'
        db.delete_table('delivery_bagginghistory_2015_05')

        # Deleting model 'BaggingHistory_2015_06'
        db.delete_table('delivery_bagginghistory_2015_06')

        # Deleting model 'BaggingHistory_2015_07'
        db.delete_table('delivery_bagginghistory_2015_07')

        # Deleting model 'BaggingHistory_2015_08'
        db.delete_table('delivery_bagginghistory_2015_08')

        # Deleting model 'BaggingHistory_2015_09'
        db.delete_table('delivery_bagginghistory_2015_09')

        # Deleting model 'BaggingHistory_2015_10'
        db.delete_table('delivery_bagginghistory_2015_10')

        # Deleting model 'BaggingHistory_2015_11'
        db.delete_table('delivery_bagginghistory_2015_11')

        # Deleting model 'BaggingHistory_2015_12'
        db.delete_table('delivery_bagginghistory_2015_12')


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
            'zone_label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ZoneLabel']", 'null': 'True', 'blank': 'True'})
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
        'delivery.bagginghistory_2014_01': {
            'Meta': {'object_name': 'BaggingHistory_2014_01'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_02': {
            'Meta': {'object_name': 'BaggingHistory_2014_02'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_03': {
            'Meta': {'object_name': 'BaggingHistory_2014_03'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_04': {
            'Meta': {'object_name': 'BaggingHistory_2014_04'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_05': {
            'Meta': {'object_name': 'BaggingHistory_2014_05'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_06': {
            'Meta': {'object_name': 'BaggingHistory_2014_06'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_07': {
            'Meta': {'object_name': 'BaggingHistory_2014_07'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_08': {
            'Meta': {'object_name': 'BaggingHistory_2014_08'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_09': {
            'Meta': {'object_name': 'BaggingHistory_2014_09'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_10': {
            'Meta': {'object_name': 'BaggingHistory_2014_10'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_11': {
            'Meta': {'object_name': 'BaggingHistory_2014_11'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2014_12': {
            'Meta': {'object_name': 'BaggingHistory_2014_12'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_01': {
            'Meta': {'object_name': 'BaggingHistory_2015_01'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_02': {
            'Meta': {'object_name': 'BaggingHistory_2015_02'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_03': {
            'Meta': {'object_name': 'BaggingHistory_2015_03'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_04': {
            'Meta': {'object_name': 'BaggingHistory_2015_04'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_05': {
            'Meta': {'object_name': 'BaggingHistory_2015_05'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_06': {
            'Meta': {'object_name': 'BaggingHistory_2015_06'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_07': {
            'Meta': {'object_name': 'BaggingHistory_2015_07'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_08': {
            'Meta': {'object_name': 'BaggingHistory_2015_08'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_09': {
            'Meta': {'object_name': 'BaggingHistory_2015_09'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_10': {
            'Meta': {'object_name': 'BaggingHistory_2015_10'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_11': {
            'Meta': {'object_name': 'BaggingHistory_2015_11'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.bagginghistory_2015_12': {
            'Meta': {'object_name': 'BaggingHistory_2015_12'},
            'bag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Bags']"}),
            'bag_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'delivery.creditcarddelivery': {
            'Meta': {'object_name': 'CreditcardDelivery'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'collected_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'credit_card_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'credit_card_owner': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'transaction_date': ('django.db.models.fields.DateField', [], {}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'transaction_time': ('django.db.models.fields.TimeField', [], {}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'delivery.creditcardpaymentdeposit': {
            'Meta': {'object_name': 'CreditCardPaymentDeposit'},
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']"}),
            'entry_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'max_length': '1'}),
            'system_date': ('django.db.models.fields.DateField', [], {}),
            'transaction_date': ('django.db.models.fields.DateField', [], {}),
            'transaction_slip_no': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'delivery.creditpaymentawbdetails': {
            'Meta': {'object_name': 'CreditPaymentAwbDetails'},
            'airwaybill_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'credit_card_payment_received': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'creditcardpaymentdeposit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['delivery.CreditCardPaymentDeposit']"}),
            'delivery_centre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"})
        },
        'delivery.dashboardvisiblity': {
            'Meta': {'object_name': 'DashboardVisiblity'},
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.EmployeeMaster']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ncr_state': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.State']", 'null': 'True', 'blank': 'True'})
        },
        'delivery.updatecardpayment': {
            'Meta': {'object_name': 'UpdateCardPayment'},
            'airwaybill_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {}),
            'card_payment_recvd_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'remarks': ('django.db.models.fields.TextField', [], {}),
            'transaction_date': ('django.db.models.fields.DateField', [], {}),
            'transaction_slip_no': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'delivery.updatecardpaymentmodified': {
            'Meta': {'object_name': 'UpdateCardPaymentModified'},
            'airwaybill_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'airwaybill_number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'corrected_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'corrected_employee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'corrected_employee'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'credit_payment_recvd_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'delivery_centre_name': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'employee'", 'to': "orm['authentication.EmployeeMaster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '1'}),
            'remarks': ('django.db.models.fields.TextField', [], {}),
            'shipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['service_centre.Shipment']"}),
            'transaction_date': ('django.db.models.fields.DateField', [], {}),
            'transaction_slip_no': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'updated_employee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'updated_employee'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"})
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

    complete_apps = ['delivery']