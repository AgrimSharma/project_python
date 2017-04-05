from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import Paragraph, SimpleDocTemplate,\
    Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib import styles
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Image
from reportlab.rl_config import defaultPageSize
from django.conf import settings
from billing.models import Billing
from customer.models import Product
from service_centre.models import Shipment
from location.models import *

def get_zones(awb):
     shipment=Shipment.objects.get(airwaybill_number=awb)
     customer=shipment.shipper
     
     #get customer labelled zone
     city=shipment.pickup.service_centre.city
     #org_zone=City.objects.filter(labeled_zones=customer.zone_label)
     if shipment.shipper.zone_label:
        cust_zone=shipment.shipper.zone_label.zone_set.filter()
        if cust_zone :
           if cust_zone[0] in shipment.pickup.service_centre.city.labeled_zones.all():
             origin_zone=cust_zone[0]
           else:
              origin_zone=city.zone  
           if cust_zone[0] in shipment.original_dest.city.labeled_zones.all():
              dest_zone= cust_zone[0]
           else:
              dest_zone=shipment.original_dest.city.zone
        else:
           origin_zone=city.zone
           dest_zone=shipment.original_dest.city.zone
     else:
         origin_zone=city.zone
         dest_zone=shipment.original_dest.city.zone
     #city=shipment.orignal_dest.city
     
         #origin_zone=shipment.pickup.service_centre.city.zone
     #if dest_zone=City.objects.filter(labeled_zones=customer.zone_label,zone=)    
     #if org_zone:
         #org_zone=
         
     #get origin and dest combo for the zones
     #return the combination
     return origin_zone,dest_zone
