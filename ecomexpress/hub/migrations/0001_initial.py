# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Bag_shipment_table'
        db.create_table('hub_bag_shipment_table', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')()),
            ('bag_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('hub', ['Bag_shipment_table'])


    def backwards(self, orm):
        # Deleting model 'Bag_shipment_table'
        db.delete_table('hub_bag_shipment_table')


    models = {
        'hub.bag_shipment_table': {
            'Meta': {'object_name': 'Bag_shipment_table'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {}),
            'bag_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['hub']