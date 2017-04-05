from django.db import models
from service_centre.models import Shipment
# Create your models here.
class SecurityModule(models.Model):
      shipment = models.ForeignKey(Shipment)
      remarks_add = models.CharField(max_length=200)
