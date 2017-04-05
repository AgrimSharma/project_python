import calendar
import datetime

from django.db.models import Q, get_model
from django.conf import settings
from django.core.mail import send_mail
#from django.db.models import Count

from customer.models import Customer
from service_centre.models import ServiceCenter, Shipment, ShipmentStatusMaster, StatusUpdate
from reports.report_api import ReportGenerator
from reports.customer_emails import customer_emails_dict
from reports.ecomm_mail import ecomm_send_mail

def mail_ndr_report(code,name):
    all_mails = customer_emails_list +  ['jinesh@prtouch.com', 'onkar@prtouch.com']
    ndr(code)
    file_link = settings.ROOT_URL + '/static/uploads/reports/' + file_name
    ecomm_send_mail('NDR  Report '+ code, file_link, all_mails)
    return True

def ndr(code):
        customer_emails_list=[]        
        now=datetime.datetime.now()
        sc="0"
        name=now.strftime('%Y-%m-%d')+"_"+str(code)
        report = ReportGenerator('ndr_report_{0}.xlsx'.format(name))
        q = Q()
        if code == "0":
            code = None
        else:
            q = q & Q(shipper__code = int(code))
        if sc=="0":
            sc = None
        else:
            q = q & Q(service_centre=int(sc))
        shipments=Shipment.objects.using('local_ecomm').filter(
                status__in=[7,8], shipper__code=code).\
                exclude(reason_code__code__in=[208,216,202,311,200,111, 777, 999, 888, 333, 310,213]).\
                exclude(rts_status__gte=1).exclude(rto_status=1)
        shipment_info={}
        download_list = []

        col_heads =("Air waybill Number", "Order Number", "Pickup Date", "Origin Service Centre", "Destination Service Centre","Shipper","Consignee",  "Collectable Value","Status Updated On", "Mobile Number", "Reason Description", "Remarks", "Number of attempts" )
        report.write_header(col_heads)
        for a in shipments:
	    if a.reason_code_id != 1:
                if not shipment_info.get(a):
                    upd_time = a.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    history = shipment_history.objects.filter(shipment=a)
                    if history.filter(reason_code__code__in = [208,216,202,311,200,111, 777, 999, 888, 333, 310,213]):
                           continue
                    upd_date = history.latest('updated_on').updated_on.date() if history.exists() else ''
                    supd = a.statusupdate_set.filter()
                    if supd:
                       su = supd.latest('added_on')
                       rs = su.reason_code.code
                       #rsd = su.reason_code.code_description
                       remarks = su.remarks
                    else:
                       continue     
                       #print a.airwaybill_number
                       rs = ""
                       rsd=""
                       #irsd =a.reason_code.code_description
                       remarks = ""
                    try:
                      rc = a.reason_code if a.reason_code else history.filter(reason_code__isnull = False).latest('updated_on').reason_code
                      code_description=rc.code_description
                    except:
                      code_description=""
                      #print a.airwaybill_number
                      #continue
   
                    sc = a.original_dest
                    if a.ref_airwaybill_number and Shipment.objects.filter(airwaybill_number = a.ref_airwaybill_number):
                                    rts_shipment = Shipment.objects.get(airwaybill_number = a.ref_airwaybill_number)
                                    try:
                                        rts_history = shipment_history.objects.filter(shipment=rts_shipment).latest('updated_on')
                                    except:
                                        rts_history = ""
                       # rts_updated_on = rts_history
                                    if rts_history:
                                        rts_updated_on = rts_history.updated_on.strftime("%d-%m-%Y")
                                    else:
                                        rts_updated_on = ""
                                    u = (a.airwaybill_number, a.order_number, a.added_on.date(), a.pickup.service_centre.center_name, sc, a.shipper, a.consignee, a.collectable_value, upd_date, a.mobile,code_description,remarks,a.deliveryoutscan_set.filter().only('id').count())
                    else:
                        u = (a.airwaybill_number, a.order_number, a.added_on.date(), a.pickup.service_centre.center_name, sc, a.shipper, a.consignee, a.collectable_value, upd_date, a.mobile, code_description, remarks,a.deliveryoutscan_set.filter().only('id').count())

                    download_list.append(u)
                    shipment_info[a]=history
        path = report.write_body(download_list)
        cdict = customer_emails_dict.get(int(code))
        if cdict:
            customer_emails_list = cdict.get('to') + cdict.get('cc')
        else:
            customer_emails_list = []
        cust=Customer.objects.get(code=code)
        all_mails = customer_emails_list +  ['sravank@ecomexpress.in','onkar@prtouch.com','jinesh@prtouch.com', 'nithinp@prtouch.com']
        file_link = settings.ROOT_URL + 'static/uploads/reports/' +path
        subject = "NDR Report for %s"%(cust.name)
        from_email = "support@ecomexpress.in"
        email_msg = " Dear Team,\nNDR Report can be access from %s"%(file_link)
        ecomm_send_mail(subject, '', all_mails, content=email_msg)
        return subject
