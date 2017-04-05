import datetime

from django.db.models import get_model, Q

from service_centre.models import (Shipment,
        get_internal_shipment_status, StatusUpdate, ServiceCenter)
from shacti_api.models import *
from service_centre.models import *
from datetime import *
import csv
from ftplib import FTP


def upload_dc_shipments():
    shacti_ftp_details = SchactiFTPDetails.objects.all() 
    header = ( "AWB","DC","PC","RTS","Weight","Status","Package Shipper","Package Consignee","Package Origin","Package Destination","Item Description","Package Pieces","Package Value", "order_id")
    for shacti_ftp_detail in shacti_ftp_details:
        sc = ServiceCenter.objects.get(center_shortcode = shacti_ftp_detail.service_center)
        filename = 'shacti_packageinfo_%s.csv'% datetime.now().strftime("%Y%m%d%H%M%S")
        csv_file_path = settings.FILE_UPLOAD_TEMP_DIR + "/" + filename
        csv_out = open(csv_file_path,"wb")
        mywriter = csv.writer(csv_out)
        mywriter.writerow(header)
        shipments = Shipment.objects.filter(status__in = [0,1], current_sc = sc, )
        if not shipments:
            continue
        for s in shipments:
            if not s.pincode:
                continue
            if s.service_centre:
                dest = s.service_centre.center_shortcode
            else:
                dest = s.original_dest.center_shortcode
            item_description = s.item_description.encode('ascii', 'replace')
            consignee = s.consignee.encode('ascii', 'replace')
            u = ( s.airwaybill_number,dest,s.pincode,s.rts_status,s.actual_weight,0,"\""+s.shipper.name+"\"",consignee,s.pickup.service_centre.center_shortcode,dest,item_description,s.pieces,s.declared_value, s.order_number)
            mywriter.writerow(u)
    #   ftp = FTP(shacti_ftp_detail.ftp_ip_address, shacti_ftp_detail.ftp_username, shacti_ftp_detail.ftp_password)  
    #   file = open(csv_file_path,'rb') 
    #   ftp.storbinary(filename, file)
    #   file.close()
    #   ftp.quit()
    return True
