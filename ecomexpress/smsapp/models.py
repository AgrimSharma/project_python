from django.db import models

# Create your models here.
class SMSQueue(models.Model):
    awb = models.BigIntegerField()
    types = models.CharField(max_length=10, null=True, blank=True)
    short_name = models.CharField(max_length=10, null=True, blank=True)
    order_no = models.CharField(max_length=20, null=True, blank=True)
    cod_amount = models.FloatField(null=True, blank=True, default=0)
    item_description = models.TextField()
    status = models.IntegerField(max_length=1, default=0,db_index=True)
    updated_on = models.DateTimeField(auto_now_add = True)
    #sms_type = models.IntegerField(max_length=1)

class SMSTemplate(models.Model):
    prod_type = models.CharField(max_length=100, null=True, blank=True)
    customer = models.CharField(max_length=100, null=True, blank=True,db_index=True)
    template = models.CharField(max_length=160, null=True, blank=True)
    #sms_type = models.IntegerField(max_length=1)
    def __unicode__(self):
        return  self.prod_type    

class SMSConfig(models.Model):
    url = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    key = models.CharField(max_length=100, null=True, blank=True)


