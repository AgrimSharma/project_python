# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'APIAwbOrderNumberHistory'
        db.create_table('airwaybill_apiawbordernumberhistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
            ('order_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('airwaybill', ['APIAwbOrderNumberHistory'])


    def backwards(self, orm):
        # Deleting model 'APIAwbOrderNumberHistory'
        db.delete_table('airwaybill_apiawbordernumberhistory')


    models = {
        'airwaybill.airwaybillcustomer': {
            'Meta': {'object_name': 'AirwaybillCustomer'},
            'airwaybill_number': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'awbc_info'", 'symmetrical': 'False', 'to': "orm['airwaybill.AirwaybillNumbers']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        'airwaybill.airwaybillnumbers': {
            'Meta': {'object_name': 'AirwaybillNumbers'},
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'airwaybill.apiawbordernumberhistory': {
            'Meta': {'object_name': 'APIAwbOrderNumberHistory'},
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'airwaybill.cod': {
            'Meta': {'object_name': 'COD'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'airwaybill.codzero': {
            'Meta': {'object_name': 'CODZero'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'airwaybill.ppd': {
            'Meta': {'object_name': 'PPD'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'airwaybill.ppdzero': {
            'Meta': {'object_name': 'PPDZero'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'airwaybill.reversepickup': {
            'Meta': {'object_name': 'ReversePickup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
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
        'ecomm_admin.legality': {
            'Meta': {'object_name': 'Legality'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legality_type': ('django.db.models.fields.CharField', [], {'max_length': '40'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ZoneLabel']", 'null': 'True', 'blank': 'True'}),
            'zone_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'zone_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'location.zonelabel': {
            'Meta': {'object_name': 'ZoneLabel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['airwaybill']