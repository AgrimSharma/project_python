# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Bag_shipment_table.added_on'
        db.alter_column('hub_bag_shipment_table', 'added_on', self.gf('django.db.models.fields.DateField')(auto_now_add=True))

    def backwards(self, orm):

        # Changing field 'Bag_shipment_table.added_on'
        db.alter_column('hub_bag_shipment_table', 'added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

    models = {
        'hub.bag_shipment_table': {
            'Meta': {'object_name': 'Bag_shipment_table'},
            'added_on': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {}),
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_bag_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'scanned_bag_number': ('django.db.models.fields.CharField', [], {'max_length': '20'})
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

    complete_apps = ['hub']