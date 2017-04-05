from datetime import datetime
from service_centre.models import Shipment
from reports.report_api import ReportGenerator


def generate_shipment_search_report(service_center,date_from, date_to):
    if date_to:
        report = ReportGenerator('correction_report{0}.xlsx'.format(date_to))
    else:
        report = ReportGenerator('correction_report.xlsx')

    # report column headings
    col_heads = ('Sr No',
        'AWB No', #1
        'Shipper Name', #2
        'Destination', #3
        'Bag Inscan', #4
        'Bag Outscan', #5
        'Shipment Center Day', #6
        'Shipment Center Time', #7
        '1st OutScan Date', #8
        '2nd OutScan Date', #9
        'No. of OutScan', #10 shipment current status
        'LastUpdate date', #11
        'Current Status') #12
          
    shipment_report = Shipment.objects.filter(
        service_centre=service_center,
        added_on__range=(date_from,date_to)
    ).values('airwaybill_number','shipper','original_dest','updated_on','status').order_by('added_on')
    #missing fields set
    bag_inscan = ''
    bag_outscan = ''
    ship_cd = ''
    ship_ct = ''
    outscan_d1 = ''
    outscan_d2 = ''
    no_outscan = ''
    #body of report 
    shipment_details = []
   
    #if len(shipment_details) > 0:
    for ship in shipment_report:
        shipment_details.append([ship.airwaybill_number,ship.shipper,bag_inscan,bag_outscan,ship_cd,ship_ct,outscan_d1,outscan_d2,no_outscan,ship.updated_on,ship.status])
    report.write_header(col_heads)
    path = report.write_body(shipment_details)	    
    return path
