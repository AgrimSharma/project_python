# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ShipmentUndelivered'
        db.create_table('nimda_shipmentundelivered', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('airwaybill_number', self.gf('django.db.models.fields.BigIntegerField')()),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('nimda', ['ShipmentUndelivered'])


    def backwards(self, orm):
        # Deleting model 'ShipmentUndelivered'
        db.delete_table('nimda_shipmentundelivered')


    models = {
        'nimda.shipmentundelivered': {
            'Meta': {'object_name': 'ShipmentUndelivered'},
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['nimda']