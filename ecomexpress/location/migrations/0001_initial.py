# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Region'
        db.create_table('location_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('region_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('region_shortcode', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('location', ['Region'])

        # Adding model 'ZoneLabel'
        db.create_table('location_zonelabel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('location', ['ZoneLabel'])

        # Adding model 'Zone'
        db.create_table('location_zone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zone_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('zone_shortcode', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('label', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ZoneLabel'], null=True, blank=True)),
            ('location_type', self.gf('django.db.models.fields.SmallIntegerField')(default=0, max_length=1)),
        ))
        db.send_create_signal('location', ['Zone'])

        # Adding model 'State'
        db.create_table('location_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('state_shortcode', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('location', ['State'])

        # Adding model 'City'
        db.create_table('location_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('city_shortcode', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.State'])),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.Zone'])),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.Region'])),
        ))
        db.send_create_signal('location', ['City'])

        # Adding M2M table for field labeled_zones on 'City'
        db.create_table('location_city_labeled_zones', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('city', models.ForeignKey(orm['location.city'], null=False)),
            ('zone', models.ForeignKey(orm['location.zone'], null=False))
        ))
        db.create_unique('location_city_labeled_zones', ['city_id', 'zone_id'])

        # Adding model 'Branch'
        db.create_table('location_branch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('branch_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('branch_shortcode', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('branch_type', self.gf('django.db.models.fields.CharField')(default=1, max_length=13)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.City'])),
        ))
        db.send_create_signal('location', ['Branch'])

        # Adding model 'AreaMaster'
        db.create_table('location_areamaster', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('area_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('area_shortcode', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('branch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.Branch'])),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.City'])),
        ))
        db.send_create_signal('location', ['AreaMaster'])

        # Adding model 'Address'
        db.create_table('location_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('address3', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('address4', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.City'])),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.State'])),
            ('pincode', self.gf('django.db.models.fields.CharField')(default='', max_length=15, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
        ))
        db.send_create_signal('location', ['Address'])

        # Adding model 'Address2'
        db.create_table('location_address2', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('address3', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('address4', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('pincode', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
        ))
        db.send_create_signal('location', ['Address2'])

        # Adding model 'Contact'
        db.create_table('location_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('designation', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True, blank=True)),
            ('address1', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True, blank=True)),
            ('address3', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True, blank=True)),
            ('address4', self.gf('django.db.models.fields.CharField')(default='', max_length=100, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.City'], null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.State'], null=True, blank=True)),
            ('pincode', self.gf('django.db.models.fields.CharField')(default='', max_length=15, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default='', max_length=15, null=True, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(default='0000-00-00', null=True, blank=True)),
        ))
        db.send_create_signal('location', ['Contact'])

        # Adding model 'ServiceCenter'
        db.create_table('location_servicecenter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('center_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('center_shortcode', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.Address'])),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.City'])),
            ('contact', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['location.Contact'], unique=True, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
        ))
        db.send_create_signal('location', ['ServiceCenter'])

        # Adding model 'HubServiceCenter'
        db.create_table('location_hubservicecenter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hub', self.gf('django.db.models.fields.related.ForeignKey')(related_name='hub_hubsc', to=orm['location.ServiceCenter'])),
            ('sc', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sc_hubsc', to=orm['location.ServiceCenter'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('location', ['HubServiceCenter'])

        # Adding unique constraint on 'HubServiceCenter', fields ['hub', 'sc']
        db.create_unique('location_hubservicecenter', ['hub_id', 'sc_id'])

        # Adding model 'InnerMumbaiOctroiSc'
        db.create_table('location_innermumbaioctroisc', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sc', self.gf('django.db.models.fields.related.ForeignKey')(related_name='inmumsc_hubsc', to=orm['location.ServiceCenter'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('location', ['InnerMumbaiOctroiSc'])

        # Adding model 'OuterMumbaiOctroiSc'
        db.create_table('location_outermumbaioctroisc', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sc', self.gf('django.db.models.fields.related.ForeignKey')(related_name='outmumsc_hubsc', to=orm['location.ServiceCenter'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('location', ['OuterMumbaiOctroiSc'])

        # Adding model 'PinRoutes'
        db.create_table('location_pinroutes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pinroute_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('location', ['PinRoutes'])

        # Adding model 'Pincode'
        db.create_table('location_pincode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pincode', self.gf('django.db.models.fields.IntegerField')()),
            ('service_center', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
            ('pin_route', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.PinRoutes'], null=True, blank=True)),
            ('area', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, max_length=1)),
            ('sdl', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('date_of_discontinuance', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('location', ['Pincode'])

        # Adding model 'PickupPincodeServiceCentreMAP'
        db.create_table('location_pickuppincodeservicecentremap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pincode', self.gf('django.db.models.fields.IntegerField')()),
            ('service_center', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('location', ['PickupPincodeServiceCentreMAP'])

        # Adding model 'RTSPincodeServiceCentreMAP'
        db.create_table('location_rtspincodeservicecentremap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pincode', self.gf('django.db.models.fields.IntegerField')()),
            ('service_center', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('location', ['RTSPincodeServiceCentreMAP'])

        # Adding model 'RTOPincodeServiceCentreMAP'
        db.create_table('location_rtopincodeservicecentremap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pincode', self.gf('django.db.models.fields.IntegerField')()),
            ('service_center', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('location', ['RTOPincodeServiceCentreMAP'])

        # Adding model 'TransitMasterGroup'
        db.create_table('location_transitmastergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('location', ['TransitMasterGroup'])

        # Adding model 'TransitMaster'
        db.create_table('location_transitmaster', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transit_master', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.TransitMasterGroup'])),
            ('org_service_center', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='service_center_org', null=True, to=orm['location.ServiceCenter'])),
            ('dest_service_center', self.gf('django.db.models.fields.related.ForeignKey')(related_name='service_center_dest', to=orm['location.ServiceCenter'])),
            ('duration', self.gf('django.db.models.fields.IntegerField')(default=1, max_length=1)),
            ('cutoff_time', self.gf('django.db.models.fields.CharField')(default='19:00', max_length=5)),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
        ))
        db.send_create_signal('location', ['TransitMaster'])

        # Adding model 'ServiceCenterTransitMasterGroup'
        db.create_table('location_servicecentertransitmastergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transit_master_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.TransitMasterGroup'])),
            ('service_center', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['location.ServiceCenter'])),
        ))
        db.send_create_signal('location', ['ServiceCenterTransitMasterGroup'])

        # Adding model 'TransitMasterCutOff'
        db.create_table('location_transitmastercutoff', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transit_master_orignal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transit_master_orignal', to=orm['location.TransitMasterGroup'])),
            ('transit_master_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transit_master_dest', to=orm['location.TransitMasterGroup'])),
            ('cutoff_time', self.gf('django.db.models.fields.CharField')(default='19:00', max_length=5)),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
        ))
        db.send_create_signal('location', ['TransitMasterCutOff'])

        # Adding model 'TransitMasterClusterBased'
        db.create_table('location_transitmasterclusterbased', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transit_master_orignal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transit_master_orignal_cm', to=orm['location.TransitMasterGroup'])),
            ('transit_master_dest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transit_master_dest_cm', to=orm['location.TransitMasterGroup'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customer.Customer'], null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(default=1, max_length=1)),
            ('cutoff_time', self.gf('django.db.models.fields.CharField')(default='19:00', max_length=5)),
            ('mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecomm_admin.Mode'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('location', ['TransitMasterClusterBased'])


    def backwards(self, orm):
        # Removing unique constraint on 'HubServiceCenter', fields ['hub', 'sc']
        db.delete_unique('location_hubservicecenter', ['hub_id', 'sc_id'])

        # Deleting model 'Region'
        db.delete_table('location_region')

        # Deleting model 'ZoneLabel'
        db.delete_table('location_zonelabel')

        # Deleting model 'Zone'
        db.delete_table('location_zone')

        # Deleting model 'State'
        db.delete_table('location_state')

        # Deleting model 'City'
        db.delete_table('location_city')

        # Removing M2M table for field labeled_zones on 'City'
        db.delete_table('location_city_labeled_zones')

        # Deleting model 'Branch'
        db.delete_table('location_branch')

        # Deleting model 'AreaMaster'
        db.delete_table('location_areamaster')

        # Deleting model 'Address'
        db.delete_table('location_address')

        # Deleting model 'Address2'
        db.delete_table('location_address2')

        # Deleting model 'Contact'
        db.delete_table('location_contact')

        # Deleting model 'ServiceCenter'
        db.delete_table('location_servicecenter')

        # Deleting model 'HubServiceCenter'
        db.delete_table('location_hubservicecenter')

        # Deleting model 'InnerMumbaiOctroiSc'
        db.delete_table('location_innermumbaioctroisc')

        # Deleting model 'OuterMumbaiOctroiSc'
        db.delete_table('location_outermumbaioctroisc')

        # Deleting model 'PinRoutes'
        db.delete_table('location_pinroutes')

        # Deleting model 'Pincode'
        db.delete_table('location_pincode')

        # Deleting model 'PickupPincodeServiceCentreMAP'
        db.delete_table('location_pickuppincodeservicecentremap')

        # Deleting model 'RTSPincodeServiceCentreMAP'
        db.delete_table('location_rtspincodeservicecentremap')

        # Deleting model 'RTOPincodeServiceCentreMAP'
        db.delete_table('location_rtopincodeservicecentremap')

        # Deleting model 'TransitMasterGroup'
        db.delete_table('location_transitmastergroup')

        # Deleting model 'TransitMaster'
        db.delete_table('location_transitmaster')

        # Deleting model 'ServiceCenterTransitMasterGroup'
        db.delete_table('location_servicecentertransitmastergroup')

        # Deleting model 'TransitMasterCutOff'
        db.delete_table('location_transitmastercutoff')

        # Deleting model 'TransitMasterClusterBased'
        db.delete_table('location_transitmasterclusterbased')


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
        'location.hubservicecenter': {
            'Meta': {'unique_together': "(('hub', 'sc'),)", 'object_name': 'HubServiceCenter'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hub': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hub_hubsc'", 'to': "orm['location.ServiceCenter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sc': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sc_hubsc'", 'to': "orm['location.ServiceCenter']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'location.innermumbaioctroisc': {
            'Meta': {'object_name': 'InnerMumbaiOctroiSc'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sc': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'inmumsc_hubsc'", 'to': "orm['location.ServiceCenter']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'location.outermumbaioctroisc': {
            'Meta': {'object_name': 'OuterMumbaiOctroiSc'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sc': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outmumsc_hubsc'", 'to': "orm['location.ServiceCenter']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'location.pickuppincodeservicecentremap': {
            'Meta': {'object_name': 'PickupPincodeServiceCentreMAP'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pincode': ('django.db.models.fields.IntegerField', [], {}),
            'service_center': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'location.pincode': {
            'Meta': {'object_name': 'Pincode'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'area': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_of_discontinuance': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pin_route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.PinRoutes']", 'null': 'True', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.IntegerField', [], {}),
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
        'location.rtopincodeservicecentremap': {
            'Meta': {'object_name': 'RTOPincodeServiceCentreMAP'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pincode': ('django.db.models.fields.IntegerField', [], {}),
            'service_center': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'location.rtspincodeservicecentremap': {
            'Meta': {'object_name': 'RTSPincodeServiceCentreMAP'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pincode': ('django.db.models.fields.IntegerField', [], {}),
            'service_center': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
        'location.servicecentertransitmastergroup': {
            'Meta': {'object_name': 'ServiceCenterTransitMasterGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service_center': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'transit_master_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.TransitMasterGroup']"})
        },
        'location.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'state_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'location.transitmaster': {
            'Meta': {'object_name': 'TransitMaster'},
            'cutoff_time': ('django.db.models.fields.CharField', [], {'default': "'19:00'", 'max_length': '5'}),
            'dest_service_center': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'service_center_dest'", 'to': "orm['location.ServiceCenter']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'org_service_center': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'service_center_org'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'transit_master': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.TransitMasterGroup']"})
        },
        'location.transitmasterclusterbased': {
            'Meta': {'object_name': 'TransitMasterClusterBased'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'cutoff_time': ('django.db.models.fields.CharField', [], {'default': "'19:00'", 'max_length': '5'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'transit_master_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transit_master_dest_cm'", 'to': "orm['location.TransitMasterGroup']"}),
            'transit_master_orignal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transit_master_orignal_cm'", 'to': "orm['location.TransitMasterGroup']"})
        },
        'location.transitmastercutoff': {
            'Meta': {'object_name': 'TransitMasterCutOff'},
            'cutoff_time': ('django.db.models.fields.CharField', [], {'default': "'19:00'", 'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']"}),
            'transit_master_dest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transit_master_dest'", 'to': "orm['location.TransitMasterGroup']"}),
            'transit_master_orignal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transit_master_orignal'", 'to': "orm['location.TransitMasterGroup']"})
        },
        'location.transitmastergroup': {
            'Meta': {'object_name': 'TransitMasterGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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

    complete_apps = ['location']