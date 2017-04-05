import datetime
import calendar
from xlsxwriter.workbook import Workbook
from decimal import Decimal
from collections import defaultdict

from django.conf import settings
from django.db.models import Count, Sum
from django.core.mail import send_mail

from service_centre.models import Shipment
from billing.models import Billing
from location.models import Pincode
from customer.models import Customer
from reports.report_api import ReportGenerator


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

class SalesComparisonReport(object):

    def __init__(self, date_str):
        self.date_str = date_str

        self.report_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

        self.from_date = self.report_date.strftime('%Y-%m-01')
        self.to_date = self.report_date.strftime('%Y-%m-%d')
        lastdate = add_months(self.report_date, 1)
        self.last_date = lastdate.strftime('%Y-%m-01')

        self.fromdate = datetime.datetime.strptime(self.from_date, "%Y-%m-%d").date()
        self.todate = datetime.datetime.strptime(self.to_date, "%Y-%m-%d").date()
        self.lastdate = datetime.datetime.strptime(self.last_date, "%Y-%m-%d").date()

        self.year = self.report_date.year
        self.month = self.report_date.month
        self.day = self.report_date.day

        self.file_name = 'sales_comparison_report_{0}.xlsx'.format(date_str)
        self.report = ReportGenerator(self.file_name)

        prev_month = calendar.month_name[self.month - 1]
        sec_prev_month = calendar.month_name[self.month - 2]

        self.col_heads = ("Customer Code",
                "Account Incharge",
                "Customer Name",
               
                "Zone",
 #              sec_prev_month + " Rev", 
 #               prev_month + " Rev", 
 #               "Rev as of date", 
 #               "Proj Rev", 
                sec_prev_month + " pcs",
                prev_month + " pcs",
                "pcs as of date",
                "Sec. Prev day pcs",
                "Prev day pcs",
                "Proj pcs")
        self.report.write_header(self.col_heads)

    def get_prev_month_dates(self, stride=1):
        if self.month - stride != 0:
            month = self.month - stride
            year = self.year
        else:
            month = 12
            year = self.year - 1
        return (year, month)

    def fix_decimal(self, val):
        TW = Decimal(10)** -2
        return Decimal(val).quantize(TW)

    def revenue_pieces_for_month(self, cid, stride=1):
        if stride == 2:
            year, month = self.get_prev_month_dates(stride=2)
        else:
            year, month = self.get_prev_month_dates()

        billing = Billing.objects.using('local_ecomm').filter(customer__id=cid, billing_date__year=year, billing_date__month=month).\
                    values_list('total_charge_pretax', 'shipment_count')

        return billing[0] if billing else (0, 0)

    def revenue_pieces_for_current_month(self, cid):
        month_data = Shipment.objects.using('local_ecomm').filter(shipper__id=cid,
                shipment_date__range=(self.from_date, self.to_date)).\
            aggregate(
                ship_count=Count('id'),
                freight_sum=Sum('order_price__freight_charge'),
                sdl_sum=Sum('order_price__sdl_charge'),
                fuel_sum=Sum('order_price__fuel_surcharge'),
                rto_sum=Sum('order_price__rto_charge'),
                sdd_sum=Sum('order_price__sdd_charge'),
                reverse_sum=Sum('order_price__reverse_charge'),
                vchc_sum=Sum('order_price__valuable_cargo_handling_charge'),
                to_pay_sum=Sum('order_price__to_pay_charge'))

        cod_positive = Shipment.objects.using('local_ecomm').filter(shipper__id=cid,
                shipment_date__range=(self.from_date, self.to_date)).\
                exclude(rts_status = 1).\
                aggregate(cod_sum=Sum('codcharge__cod_charge'))

        cod_negative =Shipment.objects.using('local_ecomm').filter(shipper__id=cid,
                shipment_date__range=(self.from_date, self.to_date), rts_status=1).\
                aggregate(cod_sum=Sum('codcharge__cod_charge'))

        frt_sum = month_data.get('freight_sum') if month_data.get('freight_sum') else 0
        sdl_sum = month_data.get('sdl_sum')  if month_data.get('sdl_sum') else 0
        fuel_sum = month_data.get('fuel_sum') if month_data.get('fuel_sum') else 0
        rto_sum = month_data.get('rto_sum') if month_data.get('rto_sum') else 0
        sdd_sum = month_data.get('sdd_sum') if month_data.get('sdd_sum') else 0
        reverse_sum = month_data.get('reverse_sum') if month_data.get('reverse_sum') else 0
        vchc_sum = month_data.get('vchc_sum') if month_data.get('vchc_sum') else 0
        to_pay_sum = month_data.get('to_pay_sum') if month_data.get('to_pay_sum') else 0
        cod_pos = cod_positive.get('cod_sum') if cod_positive.get('cod_sum') else 0
        cod_neg = cod_negative.get('cod_sum') if cod_negative.get('cod_sum') else 0

        total = frt_sum + sdl_sum + fuel_sum + rto_sum + sdd_sum + reverse_sum + vchc_sum + to_pay_sum

        revenue = total + cod_pos - cod_neg
        return (revenue, month_data.get('ship_count'))

    def work_day_calculator(self):
        daygenerator = (self.fromdate + datetime.timedelta(x + 1) for x in xrange((self.todate - self.fromdate).days))
        projected_days_now = sum(1 for day in daygenerator if day.weekday() < 6)    #getting days excluding sundays

        daygeneratormonth = (self.fromdate + datetime.timedelta(x + 1) for x in xrange((self.lastdate - self.fromdate).days))
        total_projected_days = sum(1 for day in daygeneratormonth if day.weekday() < 6)    #getting days excluding sundays

        return (projected_days_now, total_projected_days)

    def projected_revenue_pieces(self, revenue, pieces):
        projected_days_now, total_projected_days  = self.work_day_calculator()
        if projected_days_now == 0:
            return (revenue * total_projected_days, pieces * total_projected_days)

        proj_revenue = (revenue / projected_days_now) * total_projected_days
        proj_pcs = (pieces / projected_days_now) * total_projected_days

        return (proj_revenue, proj_pcs)

    def pieces_for_day(self, cid, stride=1):
        if stride == 2:
            ship_date = self.report_date - datetime.timedelta(days=2)
        else:
            ship_date = self.report_date - datetime.timedelta(days=1)
        pcs_count = Shipment.objects.using('local_ecomm').filter(shipper__id=cid, shipment_date=ship_date).count()
        return pcs_count

    def get_display_data(self):
        customer_ids = Customer.objects.using('local_ecomm').filter(activation_status=True).exclude(id=12).values_list('id', flat=True)

        data = []
        for cid in customer_ids:
            # get constant values
            cust_detail = Customer.objects.using('local_ecomm').filter(id=cid).values_list('name', 'website',
                    'activation_by__employeemaster__firstname', 'activation_by__employeemaster__lastname',
                    'activation_by__employeemaster__employee_code', 'code', 'address__pincode')
            cust_detail = cust_detail[0]
            account_in_charge = cust_detail[2]  + ' ' + cust_detail[3] + '-' + str(cust_detail[4])
            zone = Pincode.objects.using('local_ecomm').filter(pincode=cust_detail[6]).values_list('service_center__city__zone__zone_name', flat=True)
            zone_name = zone[0] if zone else ''

            # get revenue data
            sec_prev_month_rev, sec_prev_month_pcs = self.revenue_pieces_for_month(cid, stride=2)
            prev_month_rev, prev_month_pcs = self.revenue_pieces_for_month(cid, stride=1)
            curr_month_rev, curr_month_pcs = self.revenue_pieces_for_current_month(cid)
            proj_rev, proj_pcs = self.projected_revenue_pieces(curr_month_rev, curr_month_pcs)

            # get pieces data
            sec_prev_day_pcs = self.pieces_for_day(cid, 2)
            prev_day_pcs = self.pieces_for_day(cid, 1)

            data.append((cust_detail[5], account_in_charge, cust_detail[0], zone_name,
                    sec_prev_month_pcs, prev_month_pcs, curr_month_pcs,
                    sec_prev_day_pcs, prev_day_pcs, proj_pcs))

#        sec_prev_revenue_total = sum(d[4] for d in data)
#        prev_revenue_total = sum(d[5] for d in data)
#        curr_prev_revenue_total = sum(d[6] for d in data)
#        proj_revenue_total = sum(d[7] for d in data)

        sec_prev_pcs_total = sum(d[4] for d in data)
        prev_pcs_total = sum(d[5] for d in data)
        curr_prev_pcs_total = sum(d[6] for d in data)
        sec_prev_day_pcs_total = sum(d[7] for d in data)
        prev_day_pcs_total = sum(d[8] for d in data)
        proj_pcs_total = sum(d[9] for d in data)

        data.append(('', '', '', 'Total', sec_prev_pcs_total,
            prev_pcs_total, curr_prev_pcs_total, sec_prev_day_pcs_total,
            prev_day_pcs_total, proj_pcs_total))
        return data

    def generate_excel(self):
        data_gen = self.get_display_data()
        self.report.write_body(data_gen)
        return self.file_name

