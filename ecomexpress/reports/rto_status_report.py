import datetime

from django.db.models import Q

from reports.report_api import ReportGenerator
from service_centre.models import Shipment, get_internal_shipment_status


class RtoStatusReport(object):

    def __init__(self, date_from, date_to, cust_id=None):
        self.file_name = "rtostatus_report{0}.xlsx".format(date_to)
        self.date_from = date_from
        self.date_to = date_to
        self.cust_id = cust_id

        col_heads = (
            "Airwaybill Number",
            "Added On",
            "Origin",
            "Current SC",
            "Destination",
            "Original Destination"
            "Status",
            "Reason Code",
            "Updated On",
            "New AWB",
            "Status",
            "Updated On",
            "Shipper",
            "Current SC shortcode")
        self.report = ReportGenerator(self.file_name)
        self.report.write_header(col_heads)

    def get_query(self):
        q = Q()
        dt = datetime.datetime.strptime(self.date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
        self.date_to = dt.strftime("%Y-%m-%d")
        q = q & Q(shipment_date__range=(self.date_from, self.date_to))
        if cust_id:
            q = q & Q(shipper__id=cust_id)
        q = q & Q(rto_status=1)
        q = q & ~Q(status=9)
        q = q & ~Q(rts_status=1)
        return q

    def get_data(self):
        #ship = Shipment.objects.filter(rto_status=1, added_on__range=(date_from,date_to)).filter(q).exclude(status=9).exclude(rts_status=1)
        shipments = Shipment.objects.filter(q).exclude(ref_airwaybill_number=None).\
                values_list('id', 'airwaybill_number',
                            'added_on', 'status',
                            'ref_airwaybill_number', 'service_centre__center_name',
                            'pickup__service_centre__center_name', 'original_dest__center_name',
                            'reason_code__code_description', 'shipper__name')
        row = 0
        for ship in shipments:
            monthdir = ship[2].strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            hist = shipment_history.objects.filter(shipment__id=ship[0]).exclude(status__in=[11,12,16]).latest('updated_on')
            int_status = get_internal_shipment_status(ship[3])

            ref_sh = Shipment.objects.filter(airwaybill_number=ship[4]).exclude(status=9)
            if not ref_sh:
               continue
            else:
              ref_sh = ref_sh[0]

            rts_status = get_internal_shipment_status(ref_sh.status)
            rts_updated_on = ref_sh.updated_on.strftime('%Y-%m-%d')

            center_shortcode = hist.current_sc.center_shortcode if hist.current_sc else ''
            yield (ship[1], ship[2], ship[6], hist.current_sc, ship[5], ship[7],
                int_status, ship[8], hist.updated_on, ship[4], rts_status,
                rts_updated_on, ship[9], center_shortcode)

    def generate_report(self):
        data_gen = self.get_data()
        path = self.report.write_body(data_gen)
        print path
