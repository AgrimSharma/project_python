from django.db.models import Sum

from reports.report_api import ReportGenerator
from customer.models import Customer
from service_centre.models import Shipment, StatusUpdate


def unremitted_report(cid, date_to):
    col_heads = ('Sr',
                'AWB Number',
                'Order Number',
                'Pickup Date',
                'Origin',
                'Shipper',
                'Consignee',
                'COD Due',
                'Remitted Amount',
                'Balance',
                'Dest Centre',
                'Status',
                'Del Date',
                'Payment Ref & Date',
                'Bank Name',
                'Bank Ref')
    name = Customer.objects.get(id=cid).name
    cust_name = name.lower().replace(' ', '_').replace('.', '_').\
                            replace(')', '_').replace('(', '_').replace('&', '_and_').replace(',', '_')
    report = ReportGenerator('unremitted_shipments_{0}_{1}.xlsx'.format(cust_name, date_to))
    report.write_header(col_heads)

    status_updates = StatusUpdate.objects.using('local_ecomm').filter(added_on__lte=date_to + ' 23:59:59',
                        shipment__shipper__id=cid, status=2, shipment__codcharge__remittance_status=0, 
                        shipment__product_type='cod', shipment__rts_status=0, shipment__reason_code_id=1,
                        added_on__gte='2014-01-01').values_list('shipment_id', flat=True)
    shipments = Shipment.objects.using('local_ecomm').filter(id__in=status_updates)

    total_charge = shipments.aggregate(cv=Sum('collectable_value'))
    ships = shipments.values_list('airwaybill_number','order_number','added_on','shipext__origin__center_shortcode',
             'shipper__name','consignee','collectable_value','original_dest__center_shortcode',
             'reason_code__code_description','shipext__updated_on')
    count = 0
    for ship in ships:
        count = count + 1
        u = (count, ship[0], ship[1], ship[2], ship[3], ship[4],
             ship[5], ship[6], ship[6], 0, ship[7], ship[8], ship[9])      
        report.write_row(u)
    if count == 0:
       return None
    u = ("Total", count, "", "", "", "", "", total_charge)
    report.write_row(u)
    path = report.manual_sheet_close()
    return path

def generate_report_for_all_customers(date_to):
   customer_ids = Customer.objects.using('local_ecomm').filter(activation_status=True).values_list('id', flat=True)
   # call the below function for all customers
   files_list = []
   for cid in customer_ids:
       file_path = unremitted_report(cid, date_to)
       if file_path:
           files_list.append(file_path)

   return files_list

def generate_report_for_selected_customers(remit):
    files_list = []
    for cust, tdate in remit.items():
       file_path = unremitted_report(cust, str(tdate))
       if file_path:
           files_list.append(file_path)

    return files_list
