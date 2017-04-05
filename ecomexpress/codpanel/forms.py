from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button, Field

from django import forms

from customer.models import Customer
from reports.report_api import ReportGenerator
from service_centre.models import CODDeposits, DeliveryOutscan
from location.models import ServiceCenter


class OriginWiseSearchForm(forms.Form):
    REPORTS = [(0, 'Delivery Outscans'), 
               (1, 'COD Deposits'), 
               (2, 'COD Outstanding')]
    scs = ServiceCenter.objects.values_list('id', 'center_name')
    report_type = forms.IntegerField(widget=forms.HiddenInput())
    from_date = forms.DateField()
    to_date = forms.DateField()
    delivery_center = forms.ChoiceField(choices=scs)

    def __init__(self, all_origin, *args, **kwargs):
        super(OriginWiseSearchForm, self).__init__(*args, **kwargs)
        # selectively add all orign option
        if all_origin:
            scs = list(ServiceCenter.objects.values_list('id', 'center_name'))
            scs.insert(0, (0, 'All'))
            self.fields['delivery_center'].choices = scs
        self.helper = FormHelper()
        self.helper.form_id = 'id_origin_wise_search_form'
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            'report_type', 'from_date', 'to_date', 'delivery_center',
            Button(
                'search', "Search",
                css_class='tm10 btn btn-primary',
                css_id="id_codpanel_search_button"),
            Button(
                'download', "Download",
                css_class='tm10 btn btn-primary',
                css_id="id_origin_download_button"))

    def outscan_search(self):
        from_date = self.cleaned_data.get('from_date').strftime('%Y-%m-%d')
        to_date = self.cleaned_data.get('to_date').strftime('%Y-%m-%d')
        delivery_center = self.cleaned_data.get('delivery_center')
        return DeliveryOutscan.objects.filter(
            added_on__range=(from_date + ' 00:00:00', to_date + ' 23:59:59'), 
            origin_id=delivery_center)

    def codd_search(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        delivery_center = self.cleaned_data.get('delivery_center')
        return CODDeposits.objects.filter(
            date__range=(from_date, to_date), origin_id=delivery_center)

    def cod_outstanding_search(self):
        from reports.cod_outstanding_reports import outstanding_report_data
        from_date = self.cleaned_data.get('from_date').strftime('%Y-%m-%d')
        to_date = self.cleaned_data.get('to_date').strftime('%Y-%m-%d')
        sc_id = self.cleaned_data.get('delivery_center')
        return outstanding_report_data(from_date, to_date, sc_id)

    def search(self):
        report_type = self.cleaned_data.get('report_type')
        if report_type == 0:
            data = self.outscan_search()
        elif report_type == 1:
            data = self.codd_search()
        elif report_type == 2:
            data = self.cod_outstanding_search()
        return report_type, data

    def download(self):
        report_type = self.cleaned_data.get('report_type')
        from_date = self.cleaned_data.get('from_date').strftime('%Y-%m-%d')
        to_date = self.cleaned_data.get('to_date').strftime('%Y-%m-%d')
        dc = self.cleaned_data.get('delivery_center')
        if report_type == 0:
            outscans = self.outscan_search().values(
                'id', 'employee_code__employee_code', 'added_on', 
                'amount_to_be_collected', 'amount_collected', 
                'collection_status', 'amount_mismatch')
            status_map = {0: 'Pending', 2: 'Mismatch', 1: 'Collected'}
            data = [[outscan['id'], outscan['employee_code__employee_code'], 
                    outscan['added_on'], outscan['amount_to_be_collected'], 
                    outscan['amount_collected'], 
                    status_map[outscan['collection_status']], 
                    outscan['amount_mismatch']] for outscan in outscans]
            report = ReportGenerator('outscans_{0}_{1}.xlsx'.format(to_date, dc))
            report.write_header(('Outscan Id', 'Employee Code', 'Outscan Date', 
                                 'Amount to be Collected', 'Amount Collected', 
                                 'Status', 'Mismatch'))
            report.write_body(data)
            return report.file_url
        elif report_type == 1:
            data = self.codd_search().values_list(
                'id', 'origin__center_name', 'date', 'slip_number', 
                'codd_code', 'total_amount', 'collected_amount')
            report = ReportGenerator('coddeposits_{0}_{1}.xlsx'.format(to_date, dc))
            report.write_header(('CODD Id', 'DC', 'Date', 'Slip No', 
                                 'COD Code', 'Total Amount', 'Collected Amt'))
            report.write_body(data)
            return report.file_url
        elif report_type == 2:
            from reports.cod_outstanding_reports import outstanding_report
            return outstanding_report(from_date, to_date, dc)
        return report_type, data


class DateWiseSearchForm(forms.Form):
    REPORTS = [(0, 'Correction Report')]
    report = forms.ChoiceField(choices=REPORTS)
    from_date = forms.DateField()
    to_date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super(DateWiseSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id_codpanel_reports_form'
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            'report', 'from_date', 'to_date',
            Button(
                'search', "Search",
                css_class='tm10 btn btn-primary',
                css_id="id_codpanel_report_button"),
            Button(
                'download', "Download",
                css_class='tm10 btn btn-primary',
                css_id="id_reports_download_button"))

    def search(self):
        from mongoadmin.models import view_shipment_correction
        from_date = self.cleaned_data.get('from_date').strftime('%Y-%m-%d')
        to_date = self.cleaned_data.get('to_date').strftime('%Y-%m-%d')
        data = view_shipment_correction(from_date, to_date)
        return [x for x in data]

    def download(self):
        from_date = self.cleaned_data.get('from_date').strftime('%Y-%m-%d')
        to_date = self.cleaned_data.get('to_date').strftime('%Y-%m-%d')
        data_dict = self.search()
        data = [(x['awb'], x['date'], x['sc'], x['remark'], x['emp']) 
                for x in data_dict]
        report = ReportGenerator('correction_report_{0}_{1}.xlsx'.format(from_date, to_date))
        report.write_header(('Awb', 'Date', 'Service Center', 'Remark', 'Employee'))
        report.write_body(data)
        return report.file_url


class LedgerForm(forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.filter(activation_status=True))
    ledger_name = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        super(LedgerForm, self).__init__(*args, **kwargs)
        # selectively add all orign option
        self.helper = FormHelper()
        self.helper.form_id = 'id_ledger_form'
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('customer', css_class="col-lg-6"), 
            Field('ledger_name', css_class="col-lg-6"), 
            Button(
                'submit', "Submit",
                css_class='tm10 btn btn-primary',
                css_id="id_ledger_form_submit"))

    def save(self):
        from mongoadmin.models import add_ledger_name
        customer = self.cleaned_data.get('customer')
        ledger_name = self.cleaned_data.get('ledger_name')
        result = add_ledger_name(customer.code, ledger_name)
        return result
