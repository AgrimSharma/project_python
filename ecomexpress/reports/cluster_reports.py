import datetime
from reports.report_api import ReportGenerator
from service_centre.models import Shipment, get_internal_shipment_status
from service_centre.models import ShipmentAtLocation
from reports.models import Cluster, ClusterDCMapping, ClusterEmailMapping
from reports.ecomm_mail import ecomm_send_mail

"""
This are the reports generated for sending shipment inbound exception &
outbound exception to clusters.
"""

now = datetime.datetime.now()
before_day = now - datetime.timedelta(days=15)
end_day = now - datetime.timedelta(days=1)


def inbound_exception_ageing_report(cluster):
    """Report for ageing greater than 15 days"""
    cluster_dcmap = ClusterDCMapping.objects.filter(cluster=cluster)
    cluster_emailmap = ClusterEmailMapping.objects.filter(cluster=cluster
        ).values_list('email', flat=True)
    file_name ="inbound_exception_ageing_gt_15_{0}_{1}.xlsx".format(cluster,
        now.strftime('%Y-%m-%d'))
    report = ReportGenerator(file_name)

    col_head = (
        "Airwaybill Number", "Order Number", "Origin SC", "Destination SC", 
        "Original Dest", "Current SC", "Pickup Date", "Shipper Code", "Consignee", 
        "Mobile Number", "Collectable Value", "Reason Code", "Status")
    report.write_header(col_head)
    
    for cl_dc in cluster_dcmap:
        ships = Shipment.objects.filter(
            shipper__activation_status=True, added_on__lte=before_day,
            original_dest=cl_dc.dc_code, 
            status__lte=8).exclude(shipper__code=32012
        ).exclude(rts_status=2).values(
            'airwaybill_number', 'order_number', 'pickup__service_centre__center_name',
            'service_centre__center_name', 'original_dest__center_name', 'current_sc__center_name',
            'added_on', 'shipper', 'consignee', 'mobile', 'collectable_value', 
            'reason_code__code_description', 'status')
        
        for ship in ships:
            ship_status = get_internal_shipment_status(ship.get('status'))
            row_data = [ship.get('airwaybill_number'), ship.get('order_number'),
                ship.get('pickup__service_centre__center_name'),
                ship.get('service_centre__center_name'),
                ship.get('original_dest__center_name'),
                ship.get('current_sc__center_name'), ship.get('added_on'),
                ship.get('shipper'), ship.get('consignee'),
                ship.get('mobile'), ship.get('collectable_value'),
                ship.get('reason_code__code_description'), ship_status]
            report.write_row(row_data)
    
    file_name = report.manual_sheet_close()
    """
    ecomm_send_email("Inbound Exception Report - Shipment older than 15 days", cluster_emailmap, 
                     "http://billing.ecomexpress.in/static/uploads/reports/{0}".format(file_name))
    """
    return file_name
         

def inbound_exception_status_dlvry_centre(cluster):
    """Report having shipment status at delivery centre"""
    cluster_dcmap = ClusterDCMapping.objects.filter(cluster=cluster)
    cluster_emailmap = ClusterEmailMapping.objects.filter(cluster=cluster
        ).values_list('email', flat=True)
    file_name ="inbound_exception_shipment_status_dlvry_centre_{0}_{1}.xlsx".format(cluster,
        now.strftime('%Y-%m-%d'))
    report = ReportGenerator(file_name)

    col_head = (
        "Airwaybill Number", "Order Number", "Origin SC", "Destination SC", 
        "Original Dest", "Current SC", "Pickup Date", "Shipper Code", "Consignee", 
        "Mobile Number", "Collectable Value", "Reason Code", "Status")
    report.write_header(col_head)
    
    for cl_dc in cluster_dcmap:
        ships = Shipment.objects.filter(
            shipper__activation_status=True,
            original_dest=cl_dc.dc_code, 
            status=6).exclude(shipper__code=32012
        ).exclude(rts_status=2
        ).values('airwaybill_number', 'order_number', 'pickup__service_centre__center_name',
                 'service_centre__center_name', 'original_dest__center_name',
                 'current_sc__center_name', 'added_on', 'shipper', 'consignee', 'mobile', 
                 'collectable_value', 'reason_code', 'status')
        
        for ship in ships:
            ship_status = get_internal_shipment_status(ship.get('status'))
            row_data = [ship.get('airwaybill_number'), ship.get('order_number'),
                ship.get('pickup__service_centre__center_name'), 
                ship.get('service_centre__center_name'),
                ship.get('original_dest__center_name'),
                ship.get('current_sc__center_name'), ship.get('added_on'),
                ship.get('shipper'), ship.get('consignee'),
                ship.get('mobile'), ship.get('collectable_value'),
                ship.get('reason_code__code_description'), ship_status]

            report.write_row(row_data)
    
    file_name = report.manual_sheet_close()
    """
    ecomm_send_email("Inbound Exception Report having shipment status shipment at delivery center'", cluster_emailmap, 
                     "http://billing.ecomexpress.in/static/uploads/reports/{0}".format(file_name))
    """
    return file_name

    
def inbound_exception_outscan_gt_24(cluster):
    """Report having shipment outscanned greater than 24 hrs"""
    cluster_dcmap = ClusterDCMapping.objects.filter(cluster=cluster)
    cluster_emailmap = ClusterEmailMapping.objects.filter(cluster=cluster
        ).values_list('email', flat=True)
    file_name ="inbound_exception_outscan_gt_24_{0}_{1}.xlsx".format(cluster,
        now.strftime('%Y-%m-%d'))
    report = ReportGenerator(file_name)

    col_head = (
        "Airwaybill Number", "Order Number", "Origin SC", "Destination SC", 
        "Original Dest", "Current SC", "Pickup Date", "Shipper Code", "Consignee", 
        "Mobile Number", "Collectable Value", "Reason Code", "Status")
    report.write_header(col_head)
    
    for cl_dc in cluster_dcmap:
        ships = Shipment.objects.filter(
            original_dest=cl_dc.dc_code, updated_on__lt=end_day, 
            status=7).exclude(shipper__code=32012
        ).exclude(rts_status=2)

        for ship in ships:
            """
            upd_time = ship.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            history = shipment_history.objects.filter(shipment=ship, status=7)
            h = history.latest('updated_on')
            if h.updated_on < end_day:
            """
            row_data = (ship.airwaybill_number, ship.order_number,
                ship.pickup.service_centre, ship.service_centre,
                ship.original_dest, ship.current_sc.center_name, 
                ship.added_on, ship.shipper, ship.consignee,
                ship.mobile, ship.collectable_value, ship.reason_code,
                get_internal_shipment_status(ship.status))

            report.write_row(row_data)
    
    file_name = report.manual_sheet_close()
    """
    ecomm_send_email("Inbound Exception Report having shipment outscanned>24 hrs", cluster_emailmap, 
                     "http://billing.ecomexpress.in/static/uploads/reports/{0}".format(file_name))
    """
    return file_name


def inbound_exception_notin_EEPL_gt_24(cluster):
    """ Report having shipment not updated in EEPL greater than 24 hrs"""
    cluster_dcmap = ClusterDCMapping.objects.filter(cluster=cluster)
    cluster_emailmap = ClusterEmailMapping.objects.filter(cluster=cluster
        ).values_list('email', flat=True)
    file_name ="inbound_exception_notin_EEPL_gt_24_{0}_{1}.xlsx".format(cluster,
        now.strftime('%Y-%m-%d'))
    report = ReportGenerator(file_name)

    col_head = (
        "Airwaybill Number", "Order Number", "Origin SC", "Destination SC", 
        "Original Dest", "Current SC", "Pickup Date", "Shipper Code", "Consignee", 
        "Mobile Number", "Collectable Value", "Reason Code", "Status")
    report.write_header(col_head)
    
    for cl_dc in cluster_dcmap:
        ships = Shipment.objects.filter(
            original_dest=cl_dc.dc_code, updated_on__lt=end_day,
        ).exclude(shipper__code=32012
        ).exclude(rts_status=2)

        for ship in ships:
            """
            upd_time = ship.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            history = shipment_history.objects.filter(shipment=ship)
            h = history.latest('updated_on')
            if h.updated_on < end_day:
            """
            sal = ShipmentAtLocation.objects.filter(scanned_shipments=ship, added_on__gt=end_day)
            if not sal:
                row_data = (ship.airwaybill_number, ship.order_number,
                    ship.pickup.service_centre, ship.service_centre,
                    ship.original_dest, ship.current_sc,
                    ship.added_on, ship.shipper, ship.consignee,
                    ship.mobile, ship.collectable_value, ship.reason_code,
                    get_internal_shipment_status(ship.status))

                report.write_row(row_data)
    
    file_name = report.manual_sheet_close()
    """
    ecomm_send_email("Inbound Exception Report not updated in EEPL>24 hrs", cluster_emailmap, 
                     "http://billing.ecomexpress.in/static/uploads/reports/{0}".format(file_name))
    """
    return file_name


def inbound_exception_shipment_codes_report(cluster):
    """Report having shipment codes as 209,221,223,224,229,231,311"""
    cluster_dcmap = ClusterDCMapping.objects.filter(cluster=cluster)
    cluster_emailmap = ClusterEmailMapping.objects.filter(cluster=cluster
        ).values_list('email', flat=True)
    file_name ="inbound_exception_shipment_codes_{0}_{1}.xlsx".format(cluster,
        now.strftime('%Y-%m-%d'))
    report = ReportGenerator(file_name)

    col_head = (
        "Airwaybill Number", "Order Number", "Origin SC", "Destination SC", 
        "Original Dest", "Current SC", "Pickup Date", "Shipper Code", "Consignee", 
        "Mobile Number", "Collectable Value", "Reason Code", "Status")
    report.write_header(col_head)
    
    for cl_dc in cluster_dcmap:
        ships = Shipment.objects.filter(
            shipper__activation_status=True,
            original_dest=cl_dc.dc_code, 
            reason_code__code__in=[209,221,223,224,229,231,311]
        ).exclude(shipper__code=32012
        ).exclude(rts_status=2
        ).values('airwaybill_number', 'order_number', 
                 'pickup__service_centre__center_name', 'service_centre__center_name',
                 'original_dest__center_name', 'current_sc__center_name',
                 'added_on', 'shipper', 'consignee', 'mobile', 
                 'collectable_value', 'reason_code', 'status')
        
        for ship in ships:
            ship_status = get_internal_shipment_status(ship.get('status'))
            row_data = [ship.get('airwaybill_number'), ship.get('order_number'),
                ship.get('pickup__service_centre__center_name'),
                ship.get('service_centre__center_name'),
                ship.get('original_dest__center_name'),
                ship.get('current_sc__center_name'), ship.get('added_on'),
                ship.get('shipper'), ship.get('consignee'),
                ship.get('mobile'), ship.get('collectable_value'),
                ship.get('reason_code__code_description'), ship_status]

           
            report.write_row(row_data)
    
    file_name = report.manual_sheet_close()
    """
    ecomm_send_email("Inbound Exception report having codes 209,221,223,224,229,231,311", cluster_emailmap, 
                     "http://billing.ecomexpress.in/static/uploads/reports/{0}".format(file_name))
    """
    return file_name


def outbound_exception_softdata_gt_24(cluster):
    """Report having shipment softdata uploaded greater than 24 hrs"""
    cluster_dcmap = ClusterDCMapping.objects.filter(cluster=cluster)
    cluster_emailmap = ClusterEmailMapping.objects.filter(cluster=cluster
        ).values_list('email', flat=True)
    file_name ="outbound_exception_softdata_gt_24_{0}_{1}.xlsx".format(cluster,
        now.strftime('%Y-%m-%d'))
    report = ReportGenerator(file_name)

    col_head = (
        "Airwaybill Number", "Order Number", "Origin SC", "Destination SC", 
        "Original Dest", "Current SC", "Pickup Date", "Shipper Code", "Consignee", 
        "Mobile Number", "Collectable Value", "Reason Code", "Status")
    report.write_header(col_head)
    
    for cl_dc in cluster_dcmap:
        ships = Shipment.objects.filter(
            pickup__service_centre=cl_dc.dc_code, updated_on__lt=end_day, 
            status=0).exclude(shipper__code=32012).exclude( 
            reason_code__code__in=[200,310,888,999,777,111,333,302]
        )

        for ship in ships:
            """
            upd_time = ship.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            history = shipment_history.objects.filter(shipment=ship, status=0)
            h = history.latest('updated_on')
            if h.updated_on < end_day:
            """
            row_data = (ship.airwaybill_number, ship.order_number,
                ship.pickup.service_centre, ship.service_centre,
                ship.original_dest, ship.current_sc.center_name,
                ship.added_on, ship.shipper, ship.consignee, ship.mobile, 
                ship.collectable_value, ship.reason_code, 
                get_internal_shipment_status(ship.status))

            report.write_row(row_data)
    
    file_name = report.manual_sheet_close()
    """
    ecomm_send_email("Outbound Exception Report having softdata updated>24 hrs", cluster_emailmap, 
                     "http://billing.ecomexpress.in/static/uploads/reports/{0}".format(file_name))
    """
    return file_name

