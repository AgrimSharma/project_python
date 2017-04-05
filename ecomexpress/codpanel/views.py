from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from jsonview.decorators import json_view

from service_centre.models import CODDeposits
from codpanel.forms import OriginWiseSearchForm, DateWiseSearchForm


def cash_tally_admin(function):
    from django.core.exceptions import PermissionDenied
    def _inner(request, *args, **kwargs):
        if not request.user.employeemaster.employee_code in ['124','11190', '26388', '10612']:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner


@cash_tally_admin
@login_required
def cod_panel(request):
    return render_to_response(
        'codpanel/cod_panel.html', context_instance=RequestContext(request))


@json_view
@cash_tally_admin
def trackme(request):
    html = render_to_string(
        "codpanel/cod_panel_trackme.html",
        context_instance=RequestContext(request))
    return {'html': html}


@json_view
@cash_tally_admin
def remove_coddeposit(request):
    if request.is_ajax() and request.method == 'POST':
        coddid = request.POST.get('coddid')
        codd = CODDeposits.objects.get(id=coddid)
        codd.remove()
        return {
            'success': True, 'coddid': coddid,
            'message': '{0} Succesfully Removed'.format(coddid)}


@json_view
@cash_tally_admin
def coddshipments(request):
    from codpanel.cash_tally_reports import coddeposit_shipments_report
    coddid = request.GET.get('coddid')
    action = request.GET.get('action')
    if action == 'download':
        file_url = coddeposit_shipments_report(coddid)
        return {'file_url': file_url}
    else:
        codd = CODDeposits.objects.get(id=coddid)
        html = render_to_string(
            "codpanel/cod_panel_codd_shipments.html", {'codd': codd},
            context_instance=RequestContext(request))
        return {'html': html, 'title': 'CODD Shipments'}


@json_view
@cash_tally_admin
def report_search(request):
    """Date Wise Search form submit Comes Here"""
    # initialize data variable to null list
    data = []
    # if form is valid get the display data
    action = request.GET.get('action')
    if request.GET: 
        form = DateWiseSearchForm(request.GET)
        if form.is_valid():
            if action == 'download':
                file_url = form.download()
                return {'file_url': file_url}
            else:
                data = form.search()
                # create html from data for display
        html = render_to_string(
            "codpanel/correction_report.html", {'data': data, 'form': form},
            context_instance=RequestContext(request))
        return {'html': html}


@json_view
@cash_tally_admin
def show_report_form(request):
    # select the relevent form
    if request.GET.get('form_type') == 'origin':
        report_type = int(request.GET.get('report_type'))
        all_origin = True if report_type == 2 else False
        form = OriginWiseSearchForm(all_origin,
                                    initial={'report_type': report_type})
    else:
        form = DateWiseSearchForm()
    html = render_to_string(
        "codpanel/reports_search.html", {'form': form},
        context_instance=RequestContext(request))
    return {'html': html}


@json_view
@cash_tally_admin
def submit_origin_report_form(request):
    """Origin wise form Search Comes Here"""
    # select the relevent form
    report_type = int(request.GET.get('report_type'))
    all_origin = True if report_type == 2 else False
    form = OriginWiseSearchForm(all_origin, request.GET)

    if form.is_valid():
        report_type, data = form.search()
        message = True
    else:
        report_type, data = 2, []
        message = 'False ' + str(form.errors)

    if report_type == 0:
        template = "codpanel/cod_panel_outscans.html"
    elif report_type == 1:
        template = "codpanel/cod_panel_coddeposits.html"
    elif report_type == 2:
        template = "codpanel/cod_outstanding.html"
    else:
        template = "codpanel/reports_result.html"

    html = render_to_string(template, {'data': data, 'form': form},
                            context_instance=RequestContext(request))
    return {'html': html, 'message': message}


@cash_tally_admin
@json_view
def excel_download(request):
    """Origin wise form report excel download Comes Here"""
    # select the relevent form
    report_type = int(request.GET.get('report_type'))
    all_origin = True if report_type == 2 else False
    form = OriginWiseSearchForm(all_origin, request.GET)

    file_url = ''
    success = False
    if form.is_valid():
        file_url = form.download()
        success = True

    return {'file_url': file_url, 'success': success}


@cash_tally_admin
@json_view
def ledger_name(request):
    from codpanel.forms import LedgerForm
    from mongoadmin.models import get_ledger_name_list
    message = ''
    if request.method == 'POST':
        form = LedgerForm(request.POST)
        if form.is_valid():
            form.save()
            message = 'Ledger name updated'
    else:
        form = LedgerForm()

    names = get_ledger_name_list()
    html = render_to_string('codpanel/ledger_form.html', 
                            {'form': form, 'names': names},
                            context_instance=RequestContext(request))
    return {'html': html, 'message': message}
