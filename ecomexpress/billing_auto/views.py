import ntpath
import os
import ntpath
from decimal import *
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.utils import simplejson
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from jsonview.decorators import json_view

from customer.models import *
from billing.models import *
from service_centre.models import *
import utils
from datetime import timedelta, datetime, date
import xlwt
import json
from calendar import monthrange
from xlsxwriter.workbook import Workbook
from billing.forms import UploadFileForm, CutOffForm, BillingPreviewForm, BillingReportsForm
from billing.forms import BillingGenerationForm, ProvisionalBillingGenerationForm, BillingReportQueueForm
from billing.reconciliation import generate_reconciliation_excel, get_main_sheet_data
from reports.pdsr_report import write_pdsr_to_excel
from nimda.views import update_customer
from ecomm_admin.models import update_changelog
from billing.generate_bill_pdf import generate_bill_pdf
from billing.generate_bill_reports import generate_awbpdf_report, generate_awbexcel_report
from billing.generate_bill_pdf import generate_bill_summary_xls
from billing.jasper_update import generate_report as jasper_generate_report
from billing.provisional_reports import generate_provisional_bill_summary_xls


PROJECT_ROOT='/home/web/ecomm.prtouch.com/ecomexpress'
root_url = 'http://billing.ecomexpress.in/'
now = datetime.now()

monthdir = now.strftime("%Y_%m")
monthdir = now.strftime("%Y_%m")
nextmonth = now + timedelta(days=1)
nextmonth = nextmonth.strftime("%Y_%m")

yesterday_now = datetime.now() - timedelta(1)
nowdsr = now.strftime("%Y%m%d")
yesdsr = yesterday_now.strftime("%Y%m%d")
monthmcsr = now.strftime("%Y%m")
if now.month == 1:
    prevmonthmcsr = datetime.strptime(str(now.year-1)+str(now.month+11),"%Y%m").date().strftime("%Y%m")
else:
    prevmonthmcsr = datetime.strptime(str(now.year)+str(now.month-1),"%Y%m").date().strftime("%Y%m")


book = xlwt.Workbook(encoding='utf8')
default_style = xlwt.Style.default_style
datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
header_style = xlwt.XFStyle()
category_style = xlwt.XFStyle()
status_style = xlwt.XFStyle()
proj_style = xlwt.XFStyle()
font = xlwt.Font()
font.bold = True

pattern = xlwt.Pattern()
pattern.pattern = xlwt.Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = 5

pattern1 = xlwt.Pattern()
pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
pattern1.pattern_fore_colour = 7

pattern2 = xlwt.Pattern()
pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
pattern2.pattern_fore_colour = 0x31


borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
header_style.pattern = pattern
status_style.pattern = pattern1
proj_style.pattern=pattern2
header_style.font = font
category_style.font = font
header_style.borders=borders
status_style.borders=borders
status_style.font = font
default_style.borders=borders

def dsr_excel_download(distinct_list, report_date):

    sheet = book.add_sheet(report_date)
    sheet.write(0, 2, "%s Daily Sales Report "%(report_date), style=header_style)
    for a in range(20):
        sheet.col(a).width = 6000
    #   u = (shipment.airwaybill_number, shipment.airwaybill_number, shipment.product_type, shipment.added_on, shipment.collectable_value, shipment.customer.code, shipment.customer.name, status,             freight_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge)
    sheet.write(3, 0, "Air waybill Number", style=header_style)
    sheet.write(3, 1, "Order Number", style=header_style)
    sheet.write(3, 2, "Product", style=header_style)
    sheet.write(3, 3, "Added On", style=header_style)
    sheet.write(3, 4, "Chargeable Wt", style=header_style)
    sheet.write(3, 5, "Collectable Value", style=header_style)
    sheet.write(3, 6, "Declared Value", style=header_style)
    sheet.write(3, 7, "Customer Code", style=header_style)
    sheet.write(3, 8, "Customer", style=header_style)
    sheet.write(3, 9, "Status", style=header_style)
    sheet.write(3, 10, "Freight", style=header_style)
    sheet.write(3, 11, "SDL", style=header_style)
    sheet.write(3, 12, "Fuel Surcharge", style=header_style)
    sheet.write(3, 13, "VCHC Charge", style=header_style)
    sheet.write(3, 14, "To Pay", style=header_style)
    sheet.write(3, 15, "RTS", style=header_style)
    sheet.write(3, 16, "COD", style=header_style)
    sheet.write(3, 17, "Total", style=header_style)
    sheet.write(3, 18, "Origin", style=header_style)
    sheet.write(3, 19, "Destination", style=header_style)

    for row, rowdata in enumerate(distinct_list, start=4):
        for col, val in enumerate(rowdata, start=0):
                     style = datetime_style
                     sheet.write(row, col, str(val), style=style)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    return response



def remit_excel_download(distinct_list, client):

    sheet = book.add_sheet(client)
    sheet.write(0, 2, "%s Remittance Report "%(client), style=header_style)

    for a in range(10):
        sheet.col(a).width = 6000
    sheet.write(3, 0, "AWB Number", style=header_style)
    sheet.write(3, 1, "Order Number", style=header_style)
    sheet.write(3, 2, "Added Date", style=header_style)
    sheet.write(3, 3, "Delivery Date", style=header_style)
    sheet.write(3, 4, "COD Amount", style=header_style)
    sheet.write(3, 5, "Remit Amount", style=header_style)
    sheet.write(3, 6, "Remit Difference", style=header_style)
    sheet.write(3, 7, "Bank Name", style=header_style)
    sheet.write(3, 8, "Reference No. & Date", style=header_style)
    sheet.write(3, 9, "Location", style=header_style)
    #sheet.write(3, 5, "", style=header_style)
    #sheet.write(3, 6, "Reason Code", style=header_style)
    #sheet.write(3, 7, "Status Updated On", style=header_style)

    for row, rowdata in enumerate(distinct_list, start=4):
        for col, val in enumerate(rowdata, start=0):
                     style = datetime_style
                     try:
                       sheet.write(row, col, str(val), style=style)
                     except:
                        pass
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    return response


def billing_details(request, updated):
    upload_form = UploadFileForm()
    preview_form = BillingPreviewForm()
    reports_form = BillingReportsForm()
    customers = Customer.objects.all() #.values_list('id', 'code', 'name', 'activation_status')
    can_view_awb_correction = True if request.user.employeemaster.email in [
        'prashanta@ecomexpress.in', 'rajivj@ecomexpress.in','jaideeps@ecomexpress.in',
         'sravank@ecomexpress.in', 'freeman@prtouch.com', 'guido@prtouch.com'] else False
    return render_to_response("billing/billingdetails.html",
                              {'can_view_awb_correction': can_view_awb_correction,
                              'nowdsr':nowdsr,
                              'yesdsr':yesdsr,
                              'monthmcsr':monthmcsr,
                              'prevmonthmcsr':prevmonthmcsr,
                              'upload_form':upload_form,
                              'preview_form':preview_form,
                              'reports_form':reports_form,
                              'updated':updated,
                              'customers':customers},
                              context_instance=RequestContext(request))


def manifest(request, cid, bid, typ):
    customer=Customer.objects.get(id=cid)
    billing=Billing.objects.get(id=bid)
    shipper = customer.shipper_set.all()
    billingsubcustomer = BillingSubCustomer.objects.filter(billing = billing)
    br_rate = Brentrate.objects.filter(todays_date__lte=billing.billing_date).order_by("-todays_date")[0].todays_rate
    br_rate = Brentrate.objects.filter(todays_date__lte=billing.billing_date).order_by("-todays_date")[0].todays_rate
    if billing.billing_date:
        due_date = billing.billing_date + timedelta(10)
    else:
        due_date = ""
    if not billing.balance:
        billing.balance = 0
    if not billing.total_payable_charge:
        billing.total_payable_charge = 0
    if not billing.adjustment:
        billing.adjustment = 0
    if not billing.received:
        billing.received = 0
    if typ=='1':
	    html_text = render_to_string("billing/manifest.html",
                              {'customer':customer,
                               'due_date':due_date,
                               'br_rate':br_rate,
                               'total_amount':billing.balance + billing.total_payable_charge + billing.adjustment - billing.received - billing.adjustment_cr,
                               'total_post_duedate':round((billing.balance + billing.total_payable_charge + billing.adjustment - billing.received)*1.015,2),
                               'due_date':due_date,
                               'billing':billing,
                               'billingsubcustomer':billingsubcustomer},
                               context_instance=RequestContext(request))

            file_name = "/bill_manifest%d.html" % billing.id
            path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
            f = open(path_to_save,"w")
            f.write( html_text )
            return HttpResponseRedirect("/static/uploads/%s"%(file_name))

	    return render_to_response("billing/manifest.html",
                              {'customer':customer,
                               'due_date':due_date,
                               'total_amount':billing.balance + billing.total_payable_charge + billing.adjustment - billing.received - billing.adjustment_cr,
                               'total_post_duedate':round((billing.balance + billing.total_payable_charge + billing.adjustment - billing.received)*1.015,2),
                               'due_date':due_date,
                               'billing':billing,
                               'billingsubcustomer':billingsubcustomer},
                               context_instance=RequestContext(request))
    if typ=='2':
            html_text =  render_to_string("billing/summary.html",
                              {'customer':customer,
                               'due_date':due_date,
                               'total_amount':billing.balance + billing.total_payable_charge + billing.adjustment - billing.received,
                               'total_post_duedate':round((billing.balance + billing.total_payable_charge + billing.adjustment - billing.received)*1.015,2),
                               'due_date':due_date,
                               'billing':billing,
                               'billingsubcustomer':billingsubcustomer},
                               )

            file_name = "/bill_summary%d.html" % billing.id
            path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
            f = open(path_to_save,"w")
            f.write( html_text )
            return HttpResponseRedirect("/static/uploads/%s"%(file_name))

            return render_to_response("billing/summary.html",
                              {'customer':customer,
                               'due_date':due_date,
                               'total_amount':billing.balance + billing.total_payable_charge + billing.adjustment - billing.received,
                               'total_post_duedate':round((billing.balance + billing.total_payable_charge + billing.adjustment - billing.received)*1.015,2),
                               'due_date':due_date,
                               'billing':billing,
                               'billingsubcustomer':billingsubcustomer},
                               context_instance=RequestContext(request))





#   customer=Customer.objects.get(id=cid)
#   billing=Billing.objects.get(id=bid)
#   #billing.total_charge_pretax = billing.freight_charge+ billing.fuel_surcharge+billing.valuable_cargo_handling_charge+billing.to_pay_charge+billing.rto_charge+billing.cod_applied_charge-billing.cod_subtract_charge
#   #billing.save()
#   if billing.billing_date:
#       due_date = billing.billing_date + timedelta(10)
#   else:
#       due_date = ""

#   if not billing.balance:
#       billing.balance = 0

#   if not billing.total_payable_charge:
#       billing.total_payable_charge = 0

#   if not billing.adjustment:
#       billing.adjustment = 0

#   if not billing.received:
#       billing.received = 0



#   return render_to_response("billing/manifest.html",
#                             {'customer':customer,
#                              'due_date':due_date,
#                              '':due_date,
#                              'total_amount':billing.balance + billing.total_payable_charge + billing.adjustment - billing.received,
#                              'total_post_duedate':round((billing.balance + billing.total_payable_charge + billing.adjustment - billing.received)*1.015,2),
#                              'due_date':due_date,
#                              'billing':billing},
#                              context_instance=RequestContext(request))

def previous(request, cid):
    customer=Customer.objects.get(id=cid)
    return render_to_response("billing/previous.html",
                              {'customer':customer},
                               context_instance=RequestContext(request))

def customer(request, cid):
    customer=Customer.objects.get(id=cid)
    billing=Billing.objects.filter(customer=customer)
    shipper = Shipper.objects.filter(customer=customer)
    shipper_billing={}
    for a in shipper:
        if not shipper_billing.get(a):
            billing_subcustomer = BillingSubCustomer.objects.filter(subcustomer=a).reverse()[0:1]
            for b in billing_subcustomer:
                shipper_billing[a]=BillingSubCustomer.objects.get(id=b.id)

    return render_to_response("billing/customer.html",
                              {'customer':customer,
                               'billing':billing,
                               'shipper_billing':shipper_billing},
                               context_instance=RequestContext(request))

def airwaybill(request, bid):
    subbilling=BillingSubCustomer.objects.get(id=bid)
    return render_to_response("billing/airwaybill.html",
                              {'subbilling':subbilling},
                               context_instance=RequestContext(request))

def subcust_previous(request, sid):
    subbilling=BillingSubCustomer.objects.filter(id=sid)
    return render_to_response("billing/subcust_bill.html",
                              {'subbilling':subbilling},
                               context_instance=RequestContext(request))

def update_bill(request, cid):
    obj_returned = utils.update_billing(cid, datetime.today().date() + timedelta(1))
    #obj_returned = utils.update_demarrage(cid, datetime.today().date()  + timedelta(1))

    #return HttpResponse("Updated")
    return HttpResponse("%s"% obj_returned)


def generate_bill(request, cid):
    try:
        date = request.POST.get("date")
        adjustments = request.POST.get("adjustments")
        balance = request.POST.get("balance")
        payment = request.POST.get("payment")
        adjustment_cr = request.POST.get("adjustment_cr")
    except ValueError:
        return HttpResponse("No Inputs provided")
    billing = utils.update_billing(cid, datetime.strptime(date,"%d/%m/%Y").date()  + timedelta(1))
    #return HttpResponse(billing)
    #billing = utils.update_demarrage(cid, datetime.strptime(date,"%d/%m/%Y").date()  + timedelta(1))
    billing.billing_date = datetime.strptime(date,"%d/%m/%Y")
    billing.balance = balance
    billing.received = payment
    billing.adjustment = adjustments
    billing.adjustment_cr = adjustment_cr

    billing.total_charge = billing.freight_charge + billing.sdl_charge + billing.fuel_surcharge + billing.valuable_cargo_handling_charge + billing.to_pay_charge + billing.rto_charge
    billing.total_cod_charge = billing.cod_applied_charge - billing.cod_subtract_charge
    billing.total_charge_pretax = billing.freight_charge + billing.sdl_charge + billing.fuel_surcharge + billing.valuable_cargo_handling_charge + billing.to_pay_charge + billing.rto_charge + billing.demarrage_charge +  billing.total_cod_charge
    billing.service_tax = round(billing.total_charge_pretax * 0.12, 2)
    billing.education_secondary_tax = round(billing.service_tax * 0.02,2)
    billing.cess_higher_secondary_tax = round(billing.service_tax * 0.01,2)
    billing.total_payable_charge = billing.total_charge_pretax + billing.service_tax + billing.education_secondary_tax + billing.cess_higher_secondary_tax
    billing.generation_status = 1
    billing.save()

    shippers = Shipper.objects.filter(customer=billing.customer)
    for shipper in shippers:
        if BillingSubCustomer.objects.filter(subcustomer=shipper):
            if BillingSubCustomer.objects.filter(subcustomer=shipper, generation_status=0):
                sbilling = BillingSubCustomer.objects.get(subcustomer=shipper, generation_status=0)
                sbilling.billing_date = datetime.strptime(date,"%d/%m/%Y")
                sbilling.generation_status = 1
                sbilling.save()


    return HttpResponse("Updated")

def remittance_home(request):
    customers = Customer.objects.filter(activation_status=True) #.values_list('id', 'code', 'name', 'activation_status')
    return render_to_response("billing/remittance_home.html",
                              {'customers':customers},
                              context_instance=RequestContext(request))

def remittance(request, cid):
    customer = Customer.objects.get(id=cid)
    error = False
    if request.POST:
        if request.POST.get("remittance_date") and request.POST.get("amount"):
            if Remittance.objects.filter(remitted_on = request.POST.get("remittance_date"), customer=customer):
                error = "You have already remitted all cod upto " + request.POST.get("remittance_date") + ". Please choose another date:"
            elif datetime.strptime(request.POST.get("remittance_date"),"%Y-%m-%d").date() >= datetime.now().date():
                error = "You are not allowed to  remitted for this date: " + request.POST.get("remittance_date") + ". Please choose another date:"
            else:
                remittance_date = datetime.strptime(request.POST.get("remittance_date"),"%Y-%m-%d").date()
                amount = float(request.POST.get("amount"))
                remittance = Remittance(customer=customer, amount = amount, remitted_on = request.POST.get("remittance_date"), remitted_by = request.user )
                remittance.save()
                codcharges = CODCharge.objects.filter(shipment__statusupdate__date__lte = request.POST.get("remittance_date"),  shipment__shipper = customer, shipment__statusupdate__status = 2, remittance_status=0)
                for codcharge in codcharges:
                    codcharge.remittance_status = 1
                    codcharge.remitted_on = now
                    codcharge.save()
                    remittance_codcharge = RemittanceCODCharge(remittance = remittance, codcharge=codcharge)
                    remittance_codcharge.save()
    remittances = Remittance.objects.filter(customer=customer).order_by("-remitted_on")
    if remittances:
        last_remit = remittances[0]
        next_remit_date = last_remit.remitted_on + timedelta(customer.remittance_cycle)
    else:
        next_remit_date = datetime.now().date()
    today = datetime.now().date()
    if next_remit_date <= today:
        remittance_delayed = True
    else:
        remittance_delayed = False

    return render_to_response("billing/remittance.html",
                              {'customer':customer,
                               'remittances':remittances,
                               'error':error,
                               'today':today,
                               'next_remit_date':next_remit_date,
                               'remittance_delayed':remittance_delayed,
                              },
                               context_instance=RequestContext(request))



def remittance_report(request, cid, remit_id):
    customer = Customer.objects.get(id=cid)
    error = False
    report = []
    if Remittance.objects.filter(id=remit_id):
        remittance = Remittance.objects.get(id=remit_id)


    for rcod in remittance.remittancecodcharge_set.all():
        if rcod.codcharge.shipment.statusupdate_set.filter(status=2):
          added_on = rcod.codcharge.shipment.statusupdate_set.filter(status=2)[0].added_on
        else:
          added_on = ""
        u = (rcod.codcharge.shipment.airwaybill_number, rcod.codcharge.shipment.order_number, rcod.codcharge.shipment.added_on, added_on, rcod.codcharge.shipment.collectable_value, rcod.codcharge.remitted_amount, rcod.codcharge.shipment.collectable_value - rcod.codcharge.remitted_amount, rcod.bank_name, rcod.bank_ref_number, rcod.codcharge.shipment.service_centre.center_shortcode)
        report.append(u)

    response = remit_excel_download(report, customer.code)
    response['Content-Disposition'] = 'attachment; filename=past_remittance_report.xls'
    book.save(response)
    return response


def remittance_report_all(request):
    remittances = Remittance.objects.all()
    error = False
    report = []
    #if Remittance.objects.filter(id=remit_id):
    #    remittance = Remittance.objects.get(id=remit_id)

    file_name = "/remittance_report_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()

    sheet.write(0, 2, "%s Remittance Report "%("All Remitted for Reconcillation"))

    sheet.write(3, 0, "AWB Number")
    sheet.write(3, 1, "Order Number")
    sheet.write(3, 2, "Added Date")
    sheet.write(3, 3, "Delivery Date")
    sheet.write(3, 4, "COD Amount")
    sheet.write(3, 5, "Remit Amount")
    sheet.write(3, 6, "Remit Difference")
    sheet.write(3, 7, "Bank Name")
    sheet.write(3, 8, "Reference No. & Date")
    sheet.write(3, 9, "Location")
    sheet.write(3, 10, "Customer")
    sheet.write(3, 11, "Code")
    #sheet.write(3, 5, "", style=header_style)
    #sheet.write(3, 6, "Reason Code", style=header_style)
    #sheet.write(3, 7, "Status Updated On", style=header_style)

    row = 4

    for rcod in RemittanceCODCharge.objects.all().order_by('remittance'):
        if rcod.codcharge.shipment.statusupdate_set.filter(status=2):
          added_on = rcod.codcharge.shipment.statusupdate_set.filter(status=2)[0].added_on
        else:
          added_on = ""
        u = (rcod.codcharge.shipment.airwaybill_number, rcod.codcharge.shipment.order_number, rcod.codcharge.shipment.added_on, added_on, rcod.codcharge.shipment.collectable_value, rcod.codcharge.remitted_amount, rcod.codcharge.shipment.collectable_value - rcod.codcharge.remitted_amount, rcod.bank_name, rcod.bank_ref_number, rcod.codcharge.shipment.service_centre.center_shortcode, rcod.remittance.customer, rcod.remittance.customer.code)

        row = row + 1
        for col, val in enumerate(u, start=0):
            style = datetime_style
            try:
               sheet.write(row, col, str(val))
            except:
               pass
    workbook.close()
    return HttpResponseRedirect("/static/uploads/%s"%(file_name))
    #response = remit_excel_download(report, customer.code)
    #response['Content-Disposition'] = 'attachment; filename=past_remittance_report.xls'
    #book.save(response)
    #return response


def expected_remittance_report(request, cid, remit_date):
    customer = Customer.objects.get(id=cid)
    error = False
    report = []
    codcharges = []
    if remit_date == "all":
        codcharges = CODCharge.objects.filter(shipment__shipper = customer, status = 1, remittance_status=0)
    else:
        remittance_date = datetime.strptime(remit_date,"%Y%m%d").date()
        remittances =  Remittance.objects.filter(customer = customer).order_by("-remitted_on")
        if remittances:
            remittance = remittances[0]
            from_remit_date = remittance.remitted_on + timedelta(1)
            to_remit_date = remittance_date + timedelta(1)
            codcharges = CODCharge.objects.filter(shipment__statusupdate__date__lte = request.POST.get("remittance_date"),  shipment__shipper = customer, shipment__statusupdate__status = 2, remittance_status=0)
        else:
            codcharges = CODCharge.objects.filter(shipment__shipper = customer, status = 1, remittance_status=0)

    for codcharge in codcharges:
        u = (codcharge.shipment.airwaybill_number, codcharge.shipment.airwaybill_number, codcharge.shipment.added_on, codcharge.updated_on, codcharge.shipment.collectable_value, customer.code, codcharge.shipment.service_centre.center_shortcode)
        report.append(u)

    response = remit_excel_download(report, customer.code)
    response['Content-Disposition'] = 'attachment; filename=remittance_report.xls'
    book.save(response)
    return response


def cod_not_deposited_report(request, cid, remit_date):
    customer = Customer.objects.get(id=cid)
    error = False
    report = []
    codcharges = []
    codcharges = CODCharge.objects.filter(shipment__shipper = customer, status = 0, remittance_status=0, shipment__reason_code__id = 1).exclude(shipment__return_shipment=3)

    for codcharge in codcharges:
        if codcharge.shipment.statusupdate_set.all():
            delivery_date = codcharge.shipment.statusupdate_set.all()[:1][0].date
            delivery_time = codcharge.shipment.statusupdate_set.all()[:1][0].time
        else:
            delivery_date = ""
            delivery_time = ""
        u = (codcharge.shipment.airwaybill_number, codcharge.shipment.airwaybill_number, codcharge.shipment.added_on, delivery_date, delivery_time, codcharge.shipment.collectable_value, customer.code, codcharge.shipment.service_centre.center_shortcode)
        report.append(u)

    #response = remit_excel_download(report, customer.code)

    sheet = book.add_sheet(customer.code)
    sheet.write(0, 2, "%s Remittance Report "%(customer.code), style=header_style)

    for a in range(8):
        sheet.col(a).width = 6000
    sheet.write(3, 0, "Air waybill Number", style=header_style)
    sheet.write(3, 1, "Order Number", style=header_style)
    sheet.write(3, 2, "Added Date", style=header_style)
    sheet.write(3, 3, "Delivery Date", style=header_style)
    sheet.write(3, 4, "Delivery Time", style=header_style)
    sheet.write(3, 5, "COD Amount", style=header_style)
    sheet.write(3, 6, "Shipper Code", style=header_style)
    sheet.write(3, 7, "Location", style=header_style)

    for row, rowdata in enumerate(report, start=4):
        for col, val in enumerate(rowdata, start=0):
                     style = datetime_style
                     sheet.write(row, col, str(val), style=style)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=cod_exception_report.xls'
    book.save(response)
    return response



def daily_sales_report(request, report_date_str):
    report_date = datetime.strptime(report_date_str,"%Y%m%d").date()
    file_name = "/DSR_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()
    #sheet = book.add_sheet(report_date_str)
    sheet.write(0, 2, "%s Daily Sales Report "%(report_date_str))
    #for a in range(22):
        #sheet.col(a).width = 6000
    #   u = (shipment.airwaybill_number, shipment.airwaybill_number, shipment.product_type, shipment.added_on, shipment.collectable_value, shipment.customer.code, shipment.customer.name, status,             freight_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge)
    sheet.write(3, 0, "Air waybill Number")
    sheet.write(3, 1, "Order Number")
    sheet.write(3, 2, "Product")
    sheet.write(3, 3, "Added On")
    sheet.write(3, 4, "Chargeable Wt")
    sheet.write(3, 5, "Collectable Value")
    sheet.write(3, 6, "Declared Value")
    sheet.write(3, 7, "Customer Code")
    sheet.write(3, 8, "Customer")
    sheet.write(3, 9, "Status")
    sheet.write(3, 10, "Freight")
    sheet.write(3, 11, "SDL")
    sheet.write(3, 12, "SDD")
    sheet.write(3, 13, "Reverse Charge")
    sheet.write(3, 14, "Fuel Surcharge")
    sheet.write(3, 15, "VCHC Charge")
    sheet.write(3, 16, "To Pay")
    sheet.write(3, 17, "RTS")
    sheet.write(3, 18, "COD")
    sheet.write(3, 19, "Total")
    sheet.write(3, 20, "Origin")
    sheet.write(3, 21, "Destination")
    sheet.write(3, 22, "Orig. Dest.")
    sheet.write(3, 23, "RTS")

    row = 3

    nextdate=report_date +timedelta(days=1)
    next_date = nextdate.strftime('%Y-%m-%d')
    report_date = report_date.strftime('%Y-%m-%d')
#    shipments = Shipment.objects.filter(inscan_date__year=report_date.year, inscan_date__month=report_date.month, inscan_date__day=report_date.day).order_by("shipper")
    #shipments = Shipment.objects.filter(inscan_date__range=(report_date, next_date)).order_by("shipper")
    shipments = Shipment.objects.filter(shipment_date__gte=report_date, shipment_date__lt=next_date).order_by("inscan_date")
    report = []
    total_max_weight_dimension = 0
    total_freight_charge = 0
    total_sdl_charge = 0
    total_sdd_charge = 0
    total_reverse_charge = 0
    total_fuel_surcharge = 0
    total_valuable_cargo_handling_charge = 0
    total_to_pay_charge = 0
    total_rto_charge = 0
    total_cod_charge = 0
    total_total_charge = 0
    total_collectable_value = 0
    total_declared_value = 0
    for shipment in shipments:
        #return HttpResponse("%d" % shipment.status)
        if shipment.status == 0:
            status = "Uploaded in DB"
        elif shipment.status == 1:
            status = "Picked"
        elif shipment.status >= 2 :
            status = "Active"

        if not shipment.order_price_set.all():
            freight_charge = 0
            sdl_charge = 0
            sdd_charge = 0
            reverse_charge = 0
            fuel_surcharge = 0
            valuable_cargo_handling_charge = 0
            to_pay_charge = 0
            rto_charge = 0
        else:
            op = shipment.order_price_set.all()[0]
            freight_charge = op.freight_charge
            sdl_charge = op.sdl_charge
            sdd_charge = op.sdd_charge
            if op.reverse_charge:
               reverse_charge = op.reverse_charge
            else:
               reverse_charge = 0
            fuel_surcharge = op.fuel_surcharge
            valuable_cargo_handling_charge = op.valuable_cargo_handling_charge
            to_pay_charge = op.to_pay_charge
            rto_charge = op.rto_charge

        if not shipment.codcharge_set.all():
            cod_charge = 0
        else:
            cod = shipment.codcharge_set.all()[0]
            cod_charge = cod.cod_charge
        if shipment.rts_status == 1:
	    total_charge = freight_charge + sdl_charge + sdd_charge + reverse_charge + fuel_surcharge + valuable_cargo_handling_charge + to_pay_charge + rto_charge - cod_charge
            cod_charge = 0 - cod_charge
        else:
	    total_charge = freight_charge + sdl_charge + sdd_charge + reverse_charge + fuel_surcharge + valuable_cargo_handling_charge + to_pay_charge + rto_charge + cod_charge
	if MinActualWeight.objects.filter(customer=shipment.shipper):
            min_actual_weight = MinActualWeight.objects.get(customer=shipment.shipper).weight
        else:
            min_actual_weight = 0

        max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        if min_actual_weight:
            if max_weight_dimension <= min_actual_weight:
                max_weight_dimension =  shipment.actual_weight
            else:
                max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        else:
            max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)

        #max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        total_max_weight_dimension = total_max_weight_dimension +          max_weight_dimension
        total_freight_charge = total_freight_charge +                freight_charge
        total_sdl_charge = total_sdl_charge +                sdl_charge
        total_sdd_charge = total_sdd_charge +                sdd_charge
        total_reverse_charge = total_reverse_charge +                reverse_charge
        total_fuel_surcharge = total_fuel_surcharge +                fuel_surcharge
        total_valuable_cargo_handling_charge = total_valuable_cargo_handling_charge + valuable_cargo_handling_charge
        total_to_pay_charge = total_to_pay_charge +                 to_pay_charge
        total_rto_charge = total_rto_charge +                    rto_charge
        total_cod_charge = total_cod_charge +                    cod_charge
        total_total_charge = total_total_charge +                        total_charge
        total_collectable_value = total_collectable_value +                        shipment.collectable_value
        total_declared_value = total_declared_value +                        shipment.declared_value


        if shipment.service_centre:
            dest_code = shipment.service_centre.center_shortcode
        else:
            dest_code = ""

        if shipment.original_dest:
            original_dest = shipment.original_dest.center_shortcode
        else:
            original_dest = ""

        if shipment.rts_status:
            rts = shipment.rts_status
        else:
            rts = ""

        u = (shipment.airwaybill_number, shipment.order_number, shipment.product_type, shipment.inscan_date,  max_weight_dimension, shipment.collectable_value, shipment.declared_value, shipment.shipper.code, shipment.shipper.name, status,             freight_charge, sdl_charge, sdd_charge, reverse_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge, total_charge, shipment.pickup.service_centre.center_shortcode, dest_code, original_dest, rts)
        #report.append(u)
        row = row + 1
        for col, val in enumerate(u, start=0):
            style = datetime_style
            try:
               sheet.write(row, col, str(val))
            except:
               pass

    u = ("Total", len(shipments), len(shipments), "", total_max_weight_dimension, total_collectable_value, total_declared_value, "", "", "", total_freight_charge, total_sdl_charge, total_sdd_charge, total_reverse_charge, total_fuel_surcharge, total_valuable_cargo_handling_charge, total_to_pay_charge, total_rto_charge,total_cod_charge, total_total_charge)
    #report.append(u)
    row = row + 1
    for col, val in enumerate(u, start=0):
        style = datetime_style
        sheet.write(row, col, str(val))

    #response = dsr_excel_download(report, report_date_str)
    #response['Content-Disposition'] = 'attachment; filename=dsr_report_%s.xls' % report_date_str
    #book.save(response)
    workbook.close()
    return HttpResponseRedirect("/static/uploads/%s"%(file_name))
    #return response


def monthly_awb_sales_report(request, report_date_str, cron=1):
    report_date_str = datetime.strptime(report_date_str,"%Y%m%d").date()
    file_name = "/MSR_%s.xlsx" % (now.strftime("%d%m%Y%H%M%S%s"))
   #file_name = "/jasper_MSR_%s.xlsx" % (now.strftime("%d%m%Y%H%M%S%s"))
   #file_name = "/tv18_MSR_%s.xlsx" % (now.strftime("%d%m%Y%H%M%S%s"))
   #file_name = "/flipkart_MSR_%s.xlsx" % (now.strftime("%d%m%Y%H%M%S%s"))
   #file_name = "/awari_MSR_%s.xlsx" % (now.strftime("%d%m%Y%H%M%S%s"))
    #file_name_csv = "/flipkart_MSR_%s.csv" % (now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    #csv_path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name_csv
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()
    #sheet = book.add_sheet(report_date_str)
    #f = open(csv_path_to_save,"w")
    #f.write("%s Monthly Sales Report "%(report_date_str))
    #f.write("Air waybill Number,Order Number,Product,Added On,Chargeable Wt,Collectable Value,Declared Value,Customer Code,Customer,Status,Freight,SDL,SDD,Reverse,Fuel Surcharge,VCHC Charge,To Pay,RTS,COD,Total,Origin,Destination,Orig. Dest.,RTS,Reverse")
    sheet.write(0, 2, "%s Monthly Sales Report "%(report_date_str))
    #for a in range(22):
    #    sheet.col(a).width = 6000
    #   u = (shipment.airwaybill_number, shipment.airwaybill_number, shipment.product_type, shipment.added_on, shipment.collectable_value, shipment.customer.code, shipment.customer.name, status,             freight_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge)
    sheet.write(3, 0, "Air waybill Number")
    sheet.write(3, 1, "Order Number")
    sheet.write(3, 2, "Product")
    sheet.write(3, 3, "Added On")
    sheet.write(3, 4, "Chargeable Wt")
    sheet.write(3, 5, "Collectable Value")
    sheet.write(3, 6, "Declared Value")
    sheet.write(3, 7, "Customer Code")
    sheet.write(3, 8, "Customer")
    sheet.write(3, 9, "Status")
    sheet.write(3, 10, "Freight")
    sheet.write(3, 11, "SDL")
    sheet.write(3, 12, "SDD")
    sheet.write(3, 13, "Reverse")
    sheet.write(3, 14, "Fuel Surcharge")
    sheet.write(3, 15, "VCHC Charge")
    sheet.write(3, 16, "To Pay")
    sheet.write(3, 17, "RTS")
    sheet.write(3, 18, "COD")
    sheet.write(3, 19, "Total")
    sheet.write(3, 20, "Origin")
    sheet.write(3, 21, "Destination")
    sheet.write(3, 22, "Orig. Dest.")
    sheet.write(3, 23, "RTS")
    sheet.write(3, 24, "Reverse")

    row = 3

    nextmonthdate = report_date_str +timedelta(days=1)
    nextmonth_date = nextmonthdate.strftime('%Y-%m-%d')
    report_date = report_date_str.strftime('%Y-%m-01')
  #  nextmonthdate = report_date.replace(month=report_date.month+1)
  #  nextmonth_date= nextmonthdate.strftime('%Y-%m-01 07:00:00')
  #  report_date = report_date.strftime('%Y-%m-01 07:01:00')
#    shipments = Shipment.objects.filter(inscan_date__year=report_date.year, inscan_date__month=report_date.month).order_by("shipper")
    #report_date="2013-10-29"
   #q = Q(shipper__id__in = [92,6,7,13])
   #q = Q(shipper__id__in = [6])
   #q = Q(shipper__id__in = [7])
   #q = Q(shipper__id__in = [92])
   #q = Q(shipper__id__in = [13])
    #shipments = Shipment.objects.filter(shipment_date__gte=report_date, shipment_date__lt=nextmonth_date).exclude(q)
   #shipments = Shipment.objects.filter(shipment_date__gte=report_date, shipment_date__lt=nextmonth_date).filter(q)
    shipments = Shipment.objects.filter(shipment_date__gte=report_date, shipment_date__lt=nextmonth_date)
    report = []
    total_max_weight_dimension = 0
    total_freight_charge = 0
    total_sdl_charge = 0
    total_sdd_charge = 0
    total_sdd_charge = 0
    total_reverse_charge = 0
    total_fuel_surcharge = 0
    total_valuable_cargo_handling_charge = 0
    total_to_pay_charge = 0
    total_rto_charge = 0
    total_cod_charge = 0
    total_total_charge = 0
    total_collectable_value = 0
    total_declared_value = 0
    for shipment in shipments.iterator():
        #return HttpResponse("%d" % shipment.status)
        if shipment.status == 0:
            status = "Uploaded in DB"
        elif shipment.status == 1:
            status = "Picked"
        elif shipment.status >= 2 :
            status = "Active"

        oprice = shipment.order_price_set.all()
        if not oprice:
            freight_charge = 0
            sdl_charge = 0
            sdd_charge = 0
            reverse_charge = 0
            fuel_surcharge = 0
            valuable_cargo_handling_charge = 0
            to_pay_charge = 0
            rto_charge = 0
        else:
            op = oprice[0]
            freight_charge = op.freight_charge
            sdl_charge = op.sdl_charge
            sdd_charge = op.sdd_charge
            if op.reverse_charge :
                reverse_charge = op.reverse_charge
            else:
                reverse_charge = 0
            fuel_surcharge = op.fuel_surcharge
            valuable_cargo_handling_charge = op.valuable_cargo_handling_charge
            to_pay_charge = op.to_pay_charge
            rto_charge = op.rto_charge

        ccharge = shipment.codcharge_set.all()
        if not ccharge:
            cod_charge = 0
        else:
            cod = ccharge[0]
            cod_charge = cod.cod_charge
        if shipment.rts_status == 1:
	    total_charge = freight_charge + sdl_charge + sdd_charge + fuel_surcharge + valuable_cargo_handling_charge + to_pay_charge + rto_charge - cod_charge
            cod_charge = 0 - cod_charge
        else:
	    total_charge = freight_charge + sdl_charge + sdd_charge + reverse_charge +  fuel_surcharge + valuable_cargo_handling_charge + to_pay_charge + rto_charge + cod_charge

#        min_wt = MinActualWeight.objects.filter(customer=shipment.shipper)
#	if min_wt:
#            min_actual_weight = min_wt[0].weight
#        else:
 #           min_actual_weight = 0

  #      max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
  #      if min_actual_weight:
  #          if max_weight_dimension <= min_actual_weight:
  #              max_weight_dimension =  shipment.actual_weight
  #          else:
  #              max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
  #      else:
  #          max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)

        max_weight_dimension = shipment.chargeable_weight
        #max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
        total_max_weight_dimension = total_max_weight_dimension +          max_weight_dimension
        total_freight_charge = total_freight_charge +                freight_charge
        total_sdl_charge = total_sdl_charge +                sdl_charge
        total_sdd_charge = total_sdd_charge +                sdd_charge
        total_reverse_charge = total_reverse_charge +                reverse_charge
        total_fuel_surcharge = total_fuel_surcharge +                fuel_surcharge
        total_valuable_cargo_handling_charge = total_valuable_cargo_handling_charge + valuable_cargo_handling_charge
        total_to_pay_charge = total_to_pay_charge +                 to_pay_charge
        total_rto_charge = total_rto_charge +                    rto_charge
        total_cod_charge = total_cod_charge +                    cod_charge
        total_total_charge = total_total_charge +                        total_charge
        total_collectable_value = total_collectable_value +                        shipment.collectable_value
        total_declared_value = total_declared_value +                        shipment.declared_value

        if not shipment.original_dest:
               if not shipment.service_centre:
                   dest_code = ""
               else:
                   dest_code = shipment.service_centre.center_shortcode
        else:
            dest_code = shipment.original_dest.center_shortcode


        if shipment.service_centre:
            dest_code = shipment.service_centre.center_shortcode
        else:
            dest_code = ""

        if shipment.original_dest:
            original_dest = shipment.original_dest.center_shortcode
        else:
            original_dest = ""

        if shipment.rts_status:
            rts = shipment.rts_status
        else:
            rts = ""


        #u = (shipment.airwaybill_number, shipment.order_number, shipment.product_type, shipment.inscan_date,  max_weight_dimension, shipment.collectable_value, shipment.declared_value, shipment.shipper.code, shipment.shipper.name, status,             freight_charge, sdl_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge, total_charge, shipment.pickup.service_centre.center_shortcode, dest_code)
        u = (shipment.airwaybill_number, shipment.order_number, shipment.product_type, shipment.inscan_date,  max_weight_dimension, shipment.collectable_value, shipment.declared_value, shipment.shipper.code, shipment.shipper.name, status,             freight_charge, sdl_charge, sdd_charge, reverse_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge, total_charge, shipment.pickup.service_centre.center_shortcode, dest_code, original_dest, rts, shipment.reverse_pickup)
        #f.write("%d,%s,%s,%s,%d,%d,%d,%s,%s,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s,%s,%s,%s,%s"%(shipment.airwaybill_number, shipment.order_number, shipment.product_type, shipment.inscan_date,  max_weight_dimension, shipment.collectable_value, shipment.declared_value, shipment.shipper.code, shipment.shipper.name, status,             freight_charge, sdl_charge, sdd_charge, reverse_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge, total_charge, shipment.pickup.service_centre.center_shortcode, dest_code, original_dest, str(rts), shipment.reverse_pickup))
        #f.write("%d,%s,%s,%s,%d,%d,%d,%s,%s,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s,%s,%s,%d,%s"%(shipment.airwaybill_number, shipment.order_number, shipment.product_type, shipment.inscan_date,  max_weight_dimension, shipment.collectable_value, shipment.declared_value, shipment.shipper.code, shipment.shipper.name, status,             freight_charge, sdl_charge, sdd_charge, reverse_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge, total_charge, shipment.pickup.service_centre.center_shortcode, dest_code, original_dest, rts, shipment.reverse_pickup))
        #report.append(u)
        row = row + 1
        for col, val in enumerate(u, start=0):
            style = datetime_style
            s=val.encode('ascii','ignore') if isinstance(val,unicode) else str(val)
	    sheet.write(row, col, s)


    u = ("Total", len(shipments), len(shipments), "", total_max_weight_dimension, total_collectable_value, total_declared_value, "", "", "", total_freight_charge, total_sdl_charge, total_sdd_charge, total_reverse_charge, total_fuel_surcharge, total_valuable_cargo_handling_charge, total_to_pay_charge, total_rto_charge,total_cod_charge, total_total_charge)
    #f.write("%d,%s,%s,%s,%d,%d,%d,%s,%s,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d"%("Total", len(shipments), len(shipments), "", total_max_weight_dimension, total_collectable_value, total_declared_value, "", "", "", total_freight_charge, total_sdl_charge, total_sdd_charge, total_reverse_charge, total_fuel_surcharge, total_valuable_cargo_handling_charge, total_to_pay_charge, total_rto_charge,total_cod_charge, total_total_charge))
    #report.append(u)
    row = row + 1
    for col, val in enumerate(u, start=0):
        style = datetime_style
        sheet.write(row, col, str(val))

   #response = dsr_excel_download(report, report_date_str)
   # upload_file = book.save(response)
   # response['Content-Disposition'] = 'attachment; filename=msr_report_%s.xls' % report_date_str
    #file_name = "/MSR_%s.xls"%(now.strftime("%H%M%S%s"))
    #path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
 #   return HttpResponse(path_to_save)
    #book.save(path_to_save)
#    upload_file = book.temporary_file_path()
   # return HttpResponse("chk")
    workbook.close()
    #f.close()
    if cron == 2:
       return "/home/web/ecomm.prtouch.com/ecomexpress/static/uploads%s"%(file_name)
    return HttpResponseRedirect("/static/uploads/%s"%(file_name))
   # return HttpResponse(upload_file)
   # path_to_save = settings.FILE_UPLOAD_TEMP_DIR+"MSR/%s"%(now.time())
   # file_move_safe(upload_file, path_to_save, allow_overwrite=True)
   # return HttpResponse("ihi")
#    return response



def daily_outscan_collection_report(request, report_date_str):

    if len(report_date_str) == 6:
        report_date = datetime.strptime(report_date_str,"%Y%m").date()
        coddos = CODDepositsOutscan.objects.filter(updated_on__year=report_date.year, updated_on__month=report_date.month)
    else:
        report_date = datetime.strptime(report_date_str,"%Y%m%d").date()
        coddos = CODDepositsOutscan.objects.filter(updated_on__year=report_date.year, updated_on__month=report_date.month, updated_on__day=report_date.day)

    report = []
    total_amount_to_be_collected = 0
    total_amount_collected = 0
    total_amount_mismatch = 0
    for coddo in coddos:
        total_amount_to_be_collected = total_amount_to_be_collected + coddo.deliveryoutscan.amount_to_be_collected
        total_amount_collected = total_amount_collected + coddo.deliveryoutscan.amount_to_be_collected
        total_amount_mismatch =  total_amount_mismatch + coddo.deliveryoutscan.amount_mismatch

        if coddo.deliveryoutscan.collection_status == 2:
            remarks = "MISMATCH"
        else:
            remarks = ""

        u = (coddo.deliveryoutscan.id, coddo.deliveryoutscan.employee_code.employee_code, coddo.deliveryoutscan.employee_code.firstname+" "+coddo.deliveryoutscan.employee_code.lastname, coddo.deliveryoutscan.employee_code.service_centre, coddo.deliveryoutscan.added_on, coddo.updated_on, coddo.deliveryoutscan.amount_to_be_collected, coddo.deliveryoutscan.amount_collected, coddo.deliveryoutscan.amount_mismatch, coddo.deliveryoutscan.collection_status, remarks)

        report.append(u)

    u = ("total", "", "", "", "", "", total_amount_to_be_collected, total_amount_collected, total_amount_mismatch, "", "")
    report.append(u)


    sheet = book.add_sheet("outscan_cod_"+report_date_str)
    sheet.write(0, 2, "%s Daily Collection Report "%(report_date), style=header_style)

    for a in range(10):
        sheet.col(a).width = 6000
    sheet.write(3, 0, "Outscan Number", style=header_style)
    sheet.write(3, 1, "Emp. Code", style=header_style)
    sheet.write(3, 2, "Emp. Name", style=header_style)
    sheet.write(3, 3, "Location", style=header_style)
    sheet.write(3, 4, "Added Date", style=header_style)
    sheet.write(3, 5, "COD Date", style=header_style)
    sheet.write(3, 6, "Collectable", style=header_style)
    sheet.write(3, 7, "Deposited", style=header_style)
    sheet.write(3, 8, "Mismatch", style=header_style)
    sheet.write(3, 9, "Remarks", style=header_style)

    for row, rowdata in enumerate(report, start=4):
        for col, val in enumerate(rowdata, start=0):
                     style = datetime_style
                     sheet.write(row, col, str(val), style=style)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=daily_cod_report_%s.xls' % report_date_str
    book.save(response)
    return response


def customer_sales_report(request, report_date_str):
    if len(report_date_str) == 6:
        report_date = datetime.strptime(report_date_str,"%Y%m").date()
    else:
        report_date = datetime.strptime(report_date_str,"%Y%m%d").date()

    customers = Customer.objects.all()
    for customer in customers:
        if len(report_date_str) == 6:
             shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month).order_by("added_on")
        else:
             shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month, added_on__day=report_date.day).order_by("added_on")
        report = []
        total_max_weight_dimension = 0
        total_freight_charge = 0
        total_sdl_charge = 0
        total_fuel_surcharge = 0
        total_valuable_cargo_handling_charge = 0
        total_to_pay_charge = 0
        total_rto_charge = 0
        total_cod_charge = 0
        total_total_charge = 0
        total_collectable_value = 0
        total_declared_value = 0
        for shipment in shipments:
            if not shipment.order_price_set.all():
                freight_charge = 0
                sdl_charge = 0
                fuel_surcharge = 0
                valuable_cargo_handling_charge = 0
                to_pay_charge = 0
                rto_charge = 0
            else:
                op = shipment.order_price_set.all()[0]
                freight_charge = op.freight_charge
                sdl_charge = op.sdl_charge
                fuel_surcharge = op.fuel_surcharge
                valuable_cargo_handling_charge = op.valuable_cargo_handling_charge
                to_pay_charge = op.to_pay_charge
                rto_charge = op.rto_charge

            if not shipment.codcharge_set.all():
                cod_charge = 0
            else:
                cod = shipment.codcharge_set.all()[0]
                cod_charge = cod.cod_charge
            if shipment.rts_status == 1:
    	        total_charge = freight_charge + sdl_charge + fuel_surcharge + valuable_cargo_handling_charge + to_pay_charge + rto_charge - cod_charge
                cod_charge = 0 - cod_charge
            else:
    	        total_charge = freight_charge + sdl_charge + fuel_surcharge + valuable_cargo_handling_charge + to_pay_charge + rto_charge + cod_charge

            max_weight_dimension = max(float(shipment.volumetric_weight), shipment.actual_weight)
            total_max_weight_dimension = total_max_weight_dimension +          max_weight_dimension
            total_freight_charge = total_freight_charge +                freight_charge
            total_sdl_charge = total_sdl_charge +                sdl_charge
            total_fuel_surcharge = total_fuel_surcharge +                fuel_surcharge
            total_valuable_cargo_handling_charge = total_valuable_cargo_handling_charge + valuable_cargo_handling_charge
            total_to_pay_charge = total_to_pay_charge +                 to_pay_charge
            total_rto_charge = total_rto_charge +                    rto_charge
            total_cod_charge = total_cod_charge +                    cod_charge
            total_total_charge = total_total_charge +                        total_charge
            total_collectable_value = total_collectable_value +                        shipment.collectable_value
            total_declared_value = total_declared_value +                        shipment.declared_value


            if shipment.service_centre:
                dest_code = shipment.service_centre.center_shortcode
            else:
                dest_code = ""


            #u = (shipment.airwaybill_number, shipment.order_number, shipment.product_type, shipment.added_on,  max_weight_dimension, shipment.collectable_value, shipment.shipper.code, shipment.shipper.name, status,             freight_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge, total_charge, shipment.pickup.service_centre.center_shortcode, dest_code)
            #report.append(u)

            u = (customer.name, len(shipments), report_date, "", total_max_weight_dimension, total_collectable_value, total_declared_value, customer.code, "", "", total_freight_charge, total_sdl_charge, total_fuel_surcharge, total_valuable_cargo_handling_charge, total_to_pay_charge, total_rto_charge,total_cod_charge, total_total_charge)
            report.append(u)
    response = dsr_excel_download(report, "Customer "+report_date_str)
    response['Content-Disposition'] = 'attachment; filename=dsr_report_%s.xls' % report_date_str
    book.save(response)
    return response



def customer_projection_sales_report(request, report_date_str):
    if len(report_date_str) == 6:
        report_date = datetime.strptime(report_date_str,"%Y%m").date()
    else:
        report_date = datetime.strptime(report_date_str,"%Y%m%d").date()

    prev_month = utils.monthdelta(report_date,-1)

    customers = Customer.objects.all()
    client_report = []
    for customer in customers:
       #if len(report_date_str) == 6:
       #     shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month).order_by("added_on")
       #     ppd_shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month, product_type="ppd").order_by("added_on")
       #     cod_shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month, product_type="cod").order_by("added_on")
       #     ppd_shipments_count = (len(ppd_shipments))
       #     cod_shipments_count = (len(cod_shipments))
       #else:
        shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month).order_by("added_on")
        ppd_shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month, product_type="ppd").order_by("added_on")
        cod_shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month, product_type="cod").order_by("added_on")
        ppd_shipments_count = len(ppd_shipments)
        cod_shipments_count = len(cod_shipments)

        monthly_report_data = psr_calculation(shipments)

        prev_shipments = Shipment.objects.filter(shipper=customer, added_on__year=prev_month.year, added_on__month=prev_month.month).order_by("added_on")
        prev_ppd_shipments = Shipment.objects.filter(shipper=customer, added_on__year=prev_month.year, added_on__month=prev_month.month, product_type="ppd").order_by("added_on")
        prev_cod_shipments = Shipment.objects.filter(shipper=customer, added_on__year=prev_month.year, added_on__month=prev_month.month, product_type="cod").order_by("added_on")
        prev_ppd_shipments_count = len(ppd_shipments)
        prev_cod_shipments_count = len(cod_shipments)

        prev_monthly_report_data = psr_calculation(prev_shipments)

        d_shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month, added_on__day=report_date.day).order_by("added_on")
        d_ppd_shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month, product_type="ppd").order_by("added_on")
        d_cod_shipments = Shipment.objects.filter(shipper=customer, added_on__year=report_date.year, added_on__month=report_date.month, product_type="cod").order_by("added_on")
        d_ppd_shipments_count = len(ppd_shipments)
        d_shipments_count = len(cod_shipments)

        daily_report_data = psr_calculation(d_shipments)

        month_range = monthrange(report_date.year, report_date.month)
        day = report_date.day
        total_sales_days =  day - round((day)/month_range[1])
        total_sales_days_left =  month_range[1] - day - round((day - month_range[1])/month_range[1])

        proj_freight_charge = 0
        proj_fuel_surcharge = 0
        proj_valuable_cargo_handling_charge = 0
        proj_to_pay_charge = 0
        proj_rto_charge = 0
        proj_cod_charge = 0
        proj_total_charge = 0


        #u = (0customer.name, 1customer.code, 2"PPD", 3ppd_shipments_count, 4total_collectable_value, 5total_declared_value, 6total_freight_charge, 7total_fuel_surcharge, 8total_valuable_cargo_handling_charge+ total_to_pay_charge+ total_rto_charge,9total_cod_charge, 10total_total_charge)
        u = (customer.name, customer.code, "PPD", prev_ppd_shipments_count, monthly_report_data[0][7], prev_monthly_report_data[0][7], prev_monthly_report_data[0][8], prev_monthly_report_data[0][9], prev_monthly_report_data[0][10], ppd_shipments_count, monthly_report_data[0][7], monthly_report_data[0][7], monthly_report_data[0][8], monthly_report_data[0][9], monthly_report_data[0][10], d_ppd_shipments_count, daily_report_data[0][7], daily_report_data[0][7], daily_report_data[0][8], daily_report_data[0][9], daily_report_data[0][10], total_sales_days_left * ppd_shipments_count/total_sales_days / total_sales_days, total_sales_days_left * monthly_report_data[0][7]/ total_sales_days, total_sales_days_left * monthly_report_data[0][7]/ total_sales_days, total_sales_days_left * monthly_report_data[0][8]/ total_sales_days, total_sales_days_left * monthly_report_data[0][9]/ total_sales_days, total_sales_days_left * monthly_report_data[0][10]/ total_sales_days)
        client_report.append(u)

        #return HttpResponse("monthly_report_data %s "% str(monthly_report_data[1][2]))

        u = (customer.name, customer.code, "COD", prev_cod_shipments_count, prev_monthly_report_data[1][7], prev_monthly_report_data[1][7], prev_monthly_report_data[1][8], prev_monthly_report_data[1][9], prev_monthly_report_data[1][10], cod_shipments_count, monthly_report_data[1][7], monthly_report_data[1][7], monthly_report_data[1][8], monthly_report_data[1][9], monthly_report_data[1][10], d_shipments_count, daily_report_data[1][7], daily_report_data[1][7], daily_report_data[1][8], daily_report_data[1][9], daily_report_data[1][10], total_sales_days_left * cod_shipments_count/total_sales_days / total_sales_days, total_sales_days_left * monthly_report_data[1][7]/ total_sales_days, total_sales_days_left * monthly_report_data[1][7]/ total_sales_days, total_sales_days_left * monthly_report_data[1][8]/ total_sales_days, total_sales_days_left * monthly_report_data[1][9]/ total_sales_days, total_sales_days_left * monthly_report_data[1][10]/ total_sales_days)
        client_report.append(u)
        u = (customer.name, customer.code, "Total", len(prev_shipments), prev_monthly_report_data[2][7], prev_monthly_report_data[2][7], prev_monthly_report_data[2][8], prev_monthly_report_data[2][9], monthly_report_data[2][10], len(d_shipments),  len(shipments), monthly_report_data[2][7], monthly_report_data[2][7], monthly_report_data[2][8], monthly_report_data[2][9], monthly_report_data[2][10], len(d_shipments), daily_report_data[2][7], daily_report_data[2][7], daily_report_data[2][8], daily_report_data[2][9], daily_report_data[2][10], total_sales_days_left * len(shipments)/total_sales_days / total_sales_days, total_sales_days_left * monthly_report_data[2][7]/ total_sales_days, total_sales_days_left * monthly_report_data[2][7]/ total_sales_days, total_sales_days_left * monthly_report_data[2][8]/ total_sales_days, total_sales_days_left * monthly_report_data[2][9]/ total_sales_days, total_sales_days_left * monthly_report_data[2][10]/ total_sales_days)
        client_report.append(u)
        u = ("")
        client_report.append(u)



    sheet = book.add_sheet("psr-%s-%s" % (report_date.year,report_date.month ))
    sheet.write(0, 2, "%s Monthly Projection Sales Report "%(report_date), style=header_style)
    sheet.write(2, 3, "Prev Month Sales Report ", style=header_style)
    sheet.write(2, 9, "Monthly Sales Report ", style=header_style)
    sheet.write(2, 15, "Daily Sales Report ", style=header_style)
    sheet.write(2, 21, "Projected Sales Report ", style=header_style)
    for a in range(27):
        sheet.col(a).width = 6000
    #   u = (shipment.airwaybill_number, shipment.airwaybill_number, shipment.product_type, shipment.added_on, shipment.collectable_value, shipment.customer.code, shipment.customer.name, status,             freight_charge, fuel_surcharge, valuable_cargo_handling_charge, to_pay_charge, rto_charge,cod_charge)
    sheet.write(3, 0, "Customer", style=header_style)
    sheet.write(3, 1, "Code", style=header_style)
    sheet.write(3, 2, "Product", style=header_style)

    sheet.write(3, 3, "Count", style=header_style)
    sheet.write(3, 4, "Freight", style=header_style)
    sheet.write(3, 5, "fuel Surcharge", style=header_style)
    sheet.write(3, 6, "Others", style=header_style)
    sheet.write(3, 7, "COD", style=header_style)
    sheet.write(3, 8, "total", style=header_style)


    sheet.write(3, 9, "Count", style=header_style)
    sheet.write(3, 10, "Freight", style=header_style)
    sheet.write(3, 11, "fuel Surcharge", style=header_style)

    sheet.write(3, 9, "Count", style=header_style)
    sheet.write(3, 10, "Freight", style=header_style)
    sheet.write(3, 11, "fuel Surcharge", style=header_style)
    sheet.write(3, 12, "Others", style=header_style)
    sheet.write(3, 13, "COD", style=header_style)
    sheet.write(3, 14, "total", style=header_style)

    sheet.write(3, 15, "Daily Count", style=header_style)
    sheet.write(3, 16, "Daily Freight", style=header_style)
    sheet.write(3, 17, "Daily fuel Surcharge", style=header_style)
    sheet.write(3, 18, "Daily Others", style=header_style)
    sheet.write(3, 19, "Daily COD", style=header_style)
    sheet.write(3, 20, "Daily total", style=header_style)

    sheet.write(3, 21, "Projected Count", style=header_style)
    sheet.write(3, 22, "Projected Freight", style=header_style)
    sheet.write(3, 23, "Projected fuel Surcharge", style=header_style)
    sheet.write(3, 24, "Projected Others", style=header_style)
    sheet.write(3, 25, "Projected COD", style=header_style)
    sheet.write(3, 26, "Projected total", style=header_style)




    for row, rowdata in enumerate(client_report, start=4):
        for col, val in enumerate(rowdata, start=0):
                     style = datetime_style
                     sheet.write(row, col, str(val), style=style)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=dsr_report_%s.xls' % report_date_str
    book.save(response)
    return response




def remittance_update(request, cid):
     upload_file = request.FILES['upload_file']
     date = request.POST['date']
     customer = Customer.objects.get(id=cid)
     file_contents = upload_file.read()
     import_wb = xlrd.open_workbook(file_contents=file_contents)
     import_sheet = import_wb.sheet_by_index(0)
     if Remittance.objects.filter(customer=customer, remitted_on=date):
        remittance = Remittance.objects.get(customer=customer, remitted_on=date)
     else:
        try:
          bank_name= import_sheet.cell_value(rowx=1, colx=14)
        except:
          bank_name = ""
        try:
           bank_ref_number= import_sheet.cell_value(rowx=1, colx=15)
        except:
           bank_ref_number = ""
        remittance = Remittance.objects.create(customer=customer, remitted_on=date, remitted_by=request.user, amount=0, bank_name=bank_name, bank_ref_number=bank_ref_number)

     for rx in range(1, import_sheet.nrows):
            airwaybill_num = import_sheet.cell_value(rowx=rx, colx=1)
            shipment = Shipment.objects.filter(airwaybill_number=int(airwaybill_num), rts_status=0, reason_code__id=1)
            if shipment:
                 shipment = shipment[0]
            else:
                 continue
            if shipment.shipper <> customer:
                  continue
            collected_amount= import_sheet.cell_value(rowx=rx, colx=8)
            try:
              bank_name= import_sheet.cell_value(rowx=1, colx=14)
            except:
               bank_name = ""
            try:
                bank_ref_number= import_sheet.cell_value(rowx=1, colx=15)
            except:
                bank_ref_number = ""

            if CODCharge.objects.filter(shipment=shipment):
                 if CODCharge.objects.filter(shipment=shipment)[0].remittance_status == 0:
                     cod_charge = CODCharge.objects.get(shipment=shipment, remittance_status=0)
#                     return HttpResponse(cod_charge)
                     cod_charge.remittance_status = 1
                     cod_charge.remitted_on=date
                     cod_charge.remitted_amount=collected_amount
                     cod_charge.save()
                     RemittanceCODCharge.objects.create(remittance = remittance, codcharge=cod_charge, bank_name=bank_name, bank_ref_number=bank_ref_number)
                     remittance.amount=remittance.amount+collected_amount
                     remittance.save()
            else:
                return HttpResponse("%s not found, file cannot be processed further, please contact site admin"%(airwaybill_num))
     return HttpResponseRedirect('/billing/remittance/%s/'%cid)

def unremitted_report(request, cid):
    q = Q()
    if cid <> '0':
       customer = Customer.objects.get(id=cid)
       q = q & Q(shipper=customer)
#  date_from = request.GET['from_date']
    date_to = request.GET['to_date']
    if (date_to):
        q = q & Q(statusupdate__added_on__lte = date_to+" 23:59:59", statusupdate__status = 2, product_type="cod")
        q = q & Q(reason_code__id=1)
    shipment = Shipment.objects.filter(q).exclude(rts_status__gte=1).filter(codcharge__remittance_status=0).distinct()

    row = 0
    file_name = "/Billing_Unremitted_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()

    #sheet.write(0, 14, "%s Remittance Report "%(customer))

   # for a in range(7):
   #     sheet.col(a).width = 6000
    sheet.write(0, 0, "Sr")
    sheet.write(0, 1, "AWB Number")
    sheet.write(0, 2, "Order Number")
    sheet.write(0, 3, "Pickup Date")
    sheet.write(0, 4, "Origin")
    sheet.write(0, 5, "Shipper")
    sheet.write(0, 6, "Consignee")
    sheet.write(0, 7, "COD Due")
    sheet.write(0, 8, "Remitted Amount")
    sheet.write(0, 9, "Balance")
    sheet.write(0, 10, "Dest Centre")
    sheet.write(0, 11, "Status")
    sheet.write(0, 12, "Del Date")
    sheet.write(0, 13, "Payment Ref & Date")
    sheet.write(0, 14, "Bank Name")
    sheet.write(0, 15, "Bank Ref")
    #sheet.write(3, 5, "", style=header_style)
    #sheet.write(3, 6, "Reason Code", style=header_style)
    #sheet.write(3, 7, "Status Updated On", style=header_style)
    total_charge = 0
    for ship in shipment:
        su = ship.statusupdate_set.filter(status=2).latest('added_on')
        if su.added_on.strftime("%Y-%m-%d") <= date_to:
          u = ("",ship.airwaybill_number, ship.order_number, ship.added_on,  ship.pickup.service_centre.center_shortcode, ship.shipper, ship.consignee, ship.collectable_value, ship.collectable_value, 0, ship.original_dest, ship.reason_code, su.added_on)
          total_charge = total_charge+ship.collectable_value
          row = row + 1
          for col, val in enumerate(u, start=0):
            try:      #   val = val.encode('utf-8') if isinstance(val,unicode)  else val
              sheet.write(row, col, str(val))
            except:
              pass
    u = ("Total", len(shipment), "", "", "", "", "", total_charge)
    row = row + 1
    for col, val in enumerate(u, start=0):
      try:    # val = val.encode('utf-8') if isinstance(val,unicode)  else val
       sheet.write(row, col, str(val))
      except:
       pass
    workbook.close()
    return HttpResponseRedirect("/static/uploads/%s"%(file_name))
    #response = HttpResponse(mimetype='application/vnd.ms-excel')


def billing_reconciliation_stmt_home(request):
    customers = Customer.objects.all()
    html = render_to_string('billing/input_form.html',
            {'url': reverse('billing-reconciliation-report'),
             'customers': customers
            }
    )

    data = {'html':html}
    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')


@csrf_exempt
def billing_reconciliation_stmt(request):
    """ this view will provide the Reconciliation Statement
        info: http://projects.prtouch.com/issues/574
    """
    # first get the information from the request
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    cust_id = request.GET.get('cust_id')

    # if request is ajax get, then it is a request to view the report in html.
    if request.is_ajax() and request.method == 'GET':
        # get the display information
        result = get_main_sheet_data(date_from, date_to, cust_id)
        shipments_booked_dict = result[0]
        status_code_data_list = result[1]
        sub_total_dict = result[2]
        net_payable_dict =result[3]
        remittance_list = result[4]
        # add the display information to a html page and make a string
        # to send as json object to the ajax request
        html = render_to_string('billing/reconciliation_stmt_data.html',
                {'shipments_booked_dict':shipments_booked_dict,
                 'status_code_data_list':status_code_data_list,
                 'sub_total_dict':sub_total_dict,
                 'net_payable_dict':net_payable_dict
                 })

        data = {'html':html}
        json = simplejson.dumps(data)
        return HttpResponse(json, mimetype='application/json')

        # otherwise if it is a get request then it is a excel file download
        # request.
    elif request.method == 'GET':
        file_name = generate_reconciliation_excel(date_from, date_to, cust_id)
        return HttpResponseRedirect("/static/uploads%s"%(file_name))

    return HttpResponse('This is Reconciliation Report')


def handle_uploaded_file(f):
    pdf_home = PROJECT_ROOT + settings.STATIC_URL + 'uploads/billing/'
    path = pdf_home + 'bill.xls'
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path

def generate_pdf(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        #date_from = request.POST.get('date_from')
        #date_to = request.POST.get('date_to')
        #if not date_from and not date_to:
            #return HttpResponse('Date fields are not given')
        if form.is_valid():
            data = request.FILES['excel_file']
            #newdoc = BillDocument(excel_file=data)
            #newdoc.save()
            file_path = handle_uploaded_file(data)
            pdf_home = PROJECT_ROOT + settings.STATIC_URL + 'uploads/billing/'
            with open(pdf_home+'bill_month.txt', 'w') as f:
                f.write(str(date.today()))
            return HttpResponseRedirect(reverse('billing-details-updated', kwargs={'updated':True}))
        else:
            return HttpResponse('file upload failed')

    return HttpResponseRedirect(reverse('billing-details'))

def get_billing_reports(request):
    pdf_home = PROJECT_ROOT + settings.STATIC_URL + 'uploads/billing/'
    with open(pdf_home+'bill_reports.txt', 'w') as f:
        f.write(str(date.today()))
    return HttpResponseRedirect(reverse('billing-details-updated'))

def download_pdf(request, bid):
    try:
        bill = Billing.objects.get(pk=int(bid))
    except Billing.DoesNotExist:
        return HttpResponse('inproper file')

    cust_id = bill.customer.pk
    bill_date = bill.billing_date.strftime('%Y_%m_%d')
    filename = 'awb_wise_%s_%s_%s.pdf' % (
        str(cust_id), str(bill.pk), str(bill_date))

    #filename = pdf_home + file_name
    fullpath = os.path.join(pdf_home, filename)
    response = HttpResponse(file(fullpath).read())
    response['Content-Type'] = 'application/pdf'
    response['Content-disposition'] = 'attachment'
    return response


def get_finance_data(awb_num):
    """ return format:
        result = {'success': False, 'html':''}
    """
    try:
        shipment = Shipment.objects.get(airwaybill_number=int(awb_num))
    except Shipment.DoesNotExist:
        return {'success': False, 'html':''}
    data = {}
    data['shipment_id'] = shipment.id
    data['rts_status'] = shipment.rts_status
    data['billing'] = 1 if shipment.billing else 0
    data['ref_awb_num'] = shipment.ref_airwaybill_number
    data['product_type'] = shipment.product_type
    data['destination_city'] = shipment.original_dest.center_name
    data['inscan_date'] = shipment.inscan_date.strftime('%Y-%m-%d') if shipment.inscan_date else 'Not Inscaned'
    data['customer'] = shipment.shipper.name
    data['subcustomer'] = shipment.pickup.subcustomer_code.name
    data['billing_date'] = shipment.billing.billing_date.strftime('%Y-%m-%d') if shipment.billing else None
    delivery_dates = shipment.deliveryoutscan_set.all().order_by('-added_on')
    data['delivery_date'] = delivery_dates[0].added_on.strftime('%Y-%m-%d') if delivery_dates else 'In Transit'
    data['current_status'] = get_internal_shipment_status(shipment.status)
    data['reason_code'] = shipment.reason_code.code_description if shipment.reason_code else ' '
    data['origin'] = shipment.pickup.service_centre.center_name
    data['actual_weight'] = shipment.actual_weight
    data['volumetric_weight'] = shipment.volumetric_weight
    data['collectable_value'] = shipment.collectable_value

    vol_div = VolumetricWeightDivisor.objects.filter(customer=shipment.shipper)
    if vol_div.exists():
        volumetric_weight_divisor = vol_div[0].divisor
    else:
        volumetric_weight_divisor = 5000
    data['volumetric_wt_divisor'] = volumetric_weight_divisor

    minwt = MinActualWeight.objects.filter(customer=shipment.shipper).values('weight')
    min_actual_weight = minwt[0]['weight'] if minwt.exists() else 0
    data['min_wt'] = min_actual_weight
    data['chargeable_wt'] = shipment.chargeable_weight
    data['shipment_date'] = shipment.shipment_date.strftime('%Y-%m-%d') if shipment.shipment_date else None

    order_prices = shipment.order_price_set.all()
    cod_charges = shipment.codcharge_set.all()
    if cod_charges:
        data['cod_charge'] = cod_charges[0].cod_charge
        data['remittance_status'] = cod_charges[0].remittance_status
        data['remitted_on'] = cod_charges[0].remitted_on.strftime('%Y-%m-%d') if cod_charges[0].remitted_on else 'Not Remitted'
        data['remitted_amount'] = cod_charges[0].remitted_amount
    else:
        data['cod_charge'] = 0
        data['remittance_status'] = 0
        data['remitted_on'] = 0
        data['remitted_amount'] = 0
    if order_prices:
        data['freight_charge'] = order_prices[0].freight_charge
        data['fuel_surcharge'] = order_prices[0].fuel_surcharge
        data['valuable_cargo_handling_charge'] = order_prices[0].\
            valuable_cargo_handling_charge
        data['to_pay_charge'] = order_prices[0].\
                to_pay_charge
        data['rto_charge'] = order_prices[0].rto_charge
        data['sdl_charge'] = order_prices[0].sdl_charge
        data['sdd_charge'] = order_prices[0].sdd_charge
        data['reverse_charge'] = order_prices[0].reverse_charge
    else:
        data['freight_charge'] = 0
        data['fuel_surcharge'] = 0
        data['valuable_cargo_handling_charge'] = 0
        data['to_pay_charge'] = 0
        data['rto_charge'] = 0
        data['sdl_charge'] = 0
        data['sdd_charge'] = 0
        data['reverse_charge'] = 0

    result = {'success': True, 'html':''}
    result['html'] = render_to_string('billing/awb_finance_data.html', data)
    result['rts_status'] = data['rts_status']
    result['shipment_id'] = shipment.id
    result['content'] = data
    return result

def get_awb_finance(request):
    if request.is_ajax() and request.method == 'GET':
        awb_num = request.GET.get('awb_num')
        data = get_finance_data(awb_num)
    else:
        data = {'success': False, 'html':''}

    json_data = simplejson.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')

def get_awb_correction_data(shipment):
    data = {'success': True}
    total = 0
    if shipment.order_price_set.exists():
        order_price = shipment.order_price_set.get()
        print order_price.__dict__
        rev_chg = order_price.reverse_charge if order_price.reverse_charge else 0
        total = total + order_price.freight_charge + \
                     order_price.sdd_charge + \
                     order_price.sdl_charge + \
                     order_price.fuel_surcharge +\
                     order_price.valuable_cargo_handling_charge +\
                     order_price.to_pay_charge +\
                     order_price.rto_charge +\
                     rev_chg
    else:
        order_price = None
    if shipment.codcharge_set.exists():
        codcharge = shipment.codcharge_set.get()
        total = total + codcharge.cod_charge
    else:
        codcharge = None
    if utils.is_changeable and not shipment.billing:
        editable = True
    else:
        editable = False
    data['html'] = render_to_string('billing/awb_correction_data.html',
                                    {'shipment':shipment,
                                     'order_price':order_price,
                                     'codcharge':codcharge,
                                     'editable':editable,
                                     'total':total})
    return data

def get_awb_correction(request):
    if request.is_ajax() and request.method == 'GET':
        awb_num = request.GET.get('awb_num')
        try:
            shipment = Shipment.objects.get(airwaybill_number=awb_num)
            data = get_awb_correction_data(shipment)
        except Shipment.DoesNotExist:
            data = {'success': False, 'html':''}
    else:
        data = {'success': False, 'html':''}

    json_data = simplejson.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')

@csrf_exempt
def awb_correction_edit(request):
    if request.is_ajax() and request.method == 'POST':
        data = dict(request.POST.iterlists())
        awb = data.pop('awb_number')[0].strip()
        shipment = Shipment.objects.get(airwaybill_number=awb)
        result = {}

        if not utils.is_changeable(shipment) and shipment.billing:
            result['edit'] = 'Cant edit'
            json_data = simplejson.dumps(result)
            return HttpResponse(json_data, mimetype='application/json')

        for k, v in data.items():
            obj, field_name = k.strip().split('-')
            value = v[0].strip()

            if obj == 'sc':
                try:
                    value = value.upper()
                    sc = ServiceCenter.objects.get(center_shortcode=value)
                    update_changelog(shipment, 'original_dest', shipment.shipper, request.user, sc.id)
                    Shipment.objects.filter(airwaybill_number=awb).update(original_dest=sc)
                    if shipment.rts_status == 1:
                        utils.rts_pricing(shipment)
                    else:
                        utils.price_updated(shipment)
                except ServiceCenter.DoesNotExist:
                    result[field_name] = v
                    break
            elif obj == 's':
                update_changelog(shipment, field_name, shipment.shipper, request.user, value)
                if field_name == 'collectable_value':
                    Shipment.objects.filter(airwaybill_number=awb).update(collectable_value=float(value))
                elif field_name == 'actual_weight':
                    Shipment.objects.filter(airwaybill_number=awb).update(actual_weight=float(value))
                elif field_name in ['length', 'breadth', 'height']:
                    Shipment.objects.filter(airwaybill_number=awb).update(volumetric_weight=0)
                    if field_name == 'length':
                        Shipment.objects.filter(airwaybill_number=awb).update(length=float(value))
                    elif field_name == 'breadth':
                        Shipment.objects.filter(airwaybill_number=awb).update(breadth=float(value))
                    elif field_name == 'height':
                        Shipment.objects.filter(airwaybill_number=awb).update(height=float(value))
                elif field_name == 'consignee':
                        Shipment.objects.filter(airwaybill_number=awb).update(consignee=value)
                elif field_name == 'consignee_address1':
                        Shipment.objects.filter(airwaybill_number=awb).update(consignee_address2=value)
                elif field_name == 'consignee_address2':
                        Shipment.objects.filter(airwaybill_number=awb).update(consignee_address2=value)
                elif field_name == 'consignee_address3':
                        Shipment.objects.filter(airwaybill_number=awb).update(consignee_address3=value)
                elif field_name == 'consignee_address4':
                        Shipment.objects.filter(airwaybill_number=awb).update(consignee_address4=value)
                shipment = Shipment.objects.get(airwaybill_number=awb)
                if not 'consignee' in field_name:
                    if shipment.rts_status == 1:
                        utils.rts_pricing(shipment)
                    else:
                        utils.price_updated(shipment)
            elif obj == 'sub':
                try:
                    update_customer(shipment, value)
                    update_changelog(shipment, 'pickup', shipment.shipper, request.user, value)
                    if shipment.rts_status == 1:
                        utils.rts_pricing(shipment)
                    else:
                        utils.price_updated(shipment)
                except Shipper.DoesNotExist:
                    result[field_name] = v
            else:
                result[field_name] = v

        json_data = simplejson.dumps(result)
        return HttpResponse(json_data, mimetype='application/json')
    else:
        return HttpResponse('Error')


@csrf_exempt
def update_pricing(request):
    if request.is_ajax() and request.method == 'POST':
        ship_id = request.POST.get('ship_id')
        rts_update = request.POST.get('rts_update')
        shipment = Shipment.objects.get(pk=int(ship_id))
        if int(rts_update):
            res = utils.rts_pricing(shipment)
        else:
            res = utils.price_updated(shipment)
        awb_num = shipment.airwaybill_number
        data = get_finance_data(awb_num)
    else:
        data = {'success': False, 'html':''}

    json_data = simplejson.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


def billing_cutoff(request):
    if request.method == 'POST':
        form = CutOffForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            return HttpResponse('Bill cutoff date not created')

    return HttpResponseRedirect(reverse('billing-details'))

def daily_sales_report_zone_wise(request,report_date_str):
    report_date = datetime.strptime(report_date_str,"%Y%m%d").date()
    zones=Zone.objects.all()
    zone_wise_list=[]
    customer_wise_list=[]
    print "length of zone",len(zones)
    for zone in zones:
        shipments=Shipment.objects.filter(inscan_date=report_date,service_centre__city__zone=zone)
        weight=0
        frieght=0
        sdl=0
        fs=0
        cod_charge=0
        total=0
        wt_ship=0#weight/len(shipments)
        yld_ship=0#total/len(shipments)
        yld_kilo=0#total/weight
        cod_coll_value=0
        cod_percent=0#cod_charge/cod_coll_value*100

        for ship in shipments:
            weight=weight+chargeable_weight(ship)
            frieght=frieght+freight_charge(ship)
            op = Order_price.objects.filter(shipment = ship)
            if op:
                shipment_charges = op[0]
                sdl=sdl+shipment_charges.sdl_charge
                fs=fs+shipment_charges.fuel_surcharge
            try:
                cod_charge=cod_charge+ship.codcharge_set.get().cod_charge
            except:
                pass
            total=total+ship.collectable_value
            if len(shipments) <> 0:
                wt_ship=float((float(weight))/float((len(shipments))))
                yld_ship=float((float(total))/float((len(shipments))))
            else:
                wt_ship=0
                yld_ship=0
            wt_ship=Decimal(str(wt_ship)).quantize(Decimal('0.01'))
            yld_ship=Decimal(str(yld_ship)).quantize(Decimal('0.01'))
            if weight <> 0:
                yld_kilo=yld_ship=float((float(total))/float(weight))
            else:
                yld_kilo=0
            yld_kilo=Decimal(str(yld_kilo)).quantize(Decimal('0.01'))
            cod_coll_value=ship.collectable_value+cod_coll_value
            if cod_coll_value <> 0:
                cod_percent=yld_ship=float(((float(cod_charge))/float(cod_coll_value))*100.0)
            else:
                cod_percent=0
            cod_percent=Decimal(str(cod_percent)).quantize(Decimal('0.01'))

            #tmp=chargeable_weight(shipment)
        u=[zone,len(shipments),weight,frieght,sdl,fs,cod_charge,total,wt_ship,yld_ship,yld_kilo,cod_coll_value,cod_percent]
        zone_wise_list.append(u)
        customers=Customer.objects.all()
        for customer in customers:
            ppd_shipments=shipments.filter(product_type='ppd',shipper=customer).exclude(reason_code_id=48).exclude(rts_status__gt=0)

            ppd_weight=0
            ppd_frieght=0
            ppd_sdl=0
            ppd_fs=0
            ppd_cod_charge=0
            ppd_total=0
            ppd_wt_ppd_shipment=0#ppd_weight/len(ppd_shipmentments)
            ppd_yld_ppd_shipment=0#ppd_total/len(ppd_shipmentments)
            ppd_yld_kilo=0#ppd_total/ppd_weight
            ppd_cod_coll_value=0
            ppd_cod_percent=0#ppd_cod_charge/ppd_cod_coll_value*100

            for ppd_shipment in ppd_shipments:
                ppd_weight=ppd_weight+chargeable_weight(ppd_shipment)
                ppd_frieght=ppd_frieght+freight_charge(ppd_shipment)
                op=Order_price.objects.filter(ppd_shipmentment = ppd_shipment)
                if op:
                    ppd_shipmentment_charges = op[0]
                    ppd_sdl=ppd_sdl+ppd_shipmentment_charges.ppd_sdl_charge
                    ppd_fs=ppd_fs+ppd_shipmentment_charges.fuel_surcharge
                try:
                    ppd_cod_charge=ppd_cod_charge+ppd_shipment.codcharge_set.get().ppd_cod_charge
                except:
                    pass
                ppd_cod_coll_value=ppd_shipment.collectable_value+ppd_cod_coll_value
                ppd_total=ppd_total+ppd_shipment.collectable_value
            if len(ppd_shipments) <> 0:
                    ppd_wt_ppd_shipment=float((float(ppd_weight))/float((len(ppd_shipments))))
                    ppd_yld_ppd_shipment=float((float(ppd_total))/float((len(ppd_shipments))))
            else:
                    ppd_wt_ppd_shipment=0
                    ppd_yld_ppd_shipment=0
            ppd_wt_ppd_shipment=Decimal(str(ppd_wt_ppd_shipment)).quantize(Decimal('0.01'))
            ppd_yld_ppd_shipment=Decimal(str(ppd_yld_ppd_shipment)).quantize(Decimal('0.01'))
            if ppd_weight <> 0:
                    ppd_yld_kilo=ppd_yld_ppd_shipment=float((float(ppd_total))/float(ppd_weight))
            else:
                    ppd_yld_kilo=0
            ppd_yld_kilo=Decimal(str(ppd_yld_kilo)).quantize(Decimal('0.01'))

            if ppd_cod_coll_value <> 0:
                    ppd_cod_percent=ppd_yld_ppd_shipment=float(((float(ppd_cod_charge))/float(ppd_cod_coll_value))*100.0)
            else:
                    ppd_cod_percent=0
            ppd_cod_percent=Decimal(str(ppd_cod_percent)).quantize(Decimal('0.01'))

                #tmp=chargeable_ppd_weight(ppd_shipmentment)
            v=[zone,customer,'PPD',len(ppd_shipments),ppd_weight,ppd_frieght,ppd_sdl,ppd_fs,ppd_cod_charge,ppd_total,ppd_wt_ppd_shipment,ppd_yld_ppd_shipment,ppd_yld_kilo,ppd_cod_coll_value,ppd_cod_percent]
            customer_wise_list.append(v)

            cod_shipments=shipments.filter(product_type='cod',shipper=customer).exclude(reason_code_id=48).exclude(rts_status__gt=0)
            for ppd_shipment in cod_shipments:
                ppd_weight=ppd_weight+chargeable_weight(ppd_shipment)
                ppd_frieght=ppd_frieght+freight_charge(ppd_shipment)
                if Order_price.objects.filter(ppd_shipmentment = ppd_shipment):
                    ppd_shipmentment_charges = Order_price.objects.get(ppd_shipmentment = ppd_shipment)
                    ppd_sdl=ppd_sdl+ppd_shipmentment_charges.ppd_sdl_charge
                    ppd_fs=ppd_fs+ppd_shipmentment_charges.fuel_surcharge
                try:
                    ppd_cod_charge=ppd_cod_charge+ppd_shipment.codcharge_set.get().ppd_cod_charge
                except:
                    pass
                ppd_total=ppd_total+ppd_shipment.collectable_value
                ppd_cod_coll_value=ppd_shipment.collectable_value+ppd_cod_coll_value

            if len(cod_shipments) <> 0:
                    ppd_wt_ppd_shipment=float((float(ppd_weight))/float((len(cod_shipments))))
                    ppd_yld_ppd_shipment=float((float(ppd_total))/float((len(cod_shipments))))
            else:
                    ppd_wt_ppd_shipment=0
                    ppd_yld_ppd_shipment=0
            ppd_wt_ppd_shipment=Decimal(str(ppd_wt_ppd_shipment)).quantize(Decimal('0.01'))
            ppd_yld_ppd_shipment=Decimal(str(ppd_yld_ppd_shipment)).quantize(Decimal('0.01'))
            if ppd_weight <> 0:
                    ppd_yld_kilo=ppd_yld_ppd_shipment=float((float(ppd_total))/float(ppd_weight))
            else:
                    ppd_yld_kilo=0
            ppd_yld_kilo=Decimal(str(ppd_yld_kilo)).quantize(Decimal('0.01'))
            if ppd_cod_coll_value <> 0:
                    ppd_cod_percent=ppd_yld_ppd_shipment=float(((float(ppd_cod_charge))/float(ppd_cod_coll_value))*100.0)
            else:
                    ppd_cod_percent=0
            ppd_cod_percent=Decimal(str(ppd_cod_percent)).quantize(Decimal('0.01'))

                #tmp=chargeable_ppd_weight(ppd_shipmentment)
            v=[zone,customer,'COD',len(ppd_shipments),ppd_weight,ppd_frieght,ppd_sdl,ppd_fs,ppd_cod_charge,ppd_total,ppd_wt_ppd_shipment,ppd_yld_ppd_shipment,ppd_yld_kilo,ppd_cod_coll_value,ppd_cod_percent]
            customer_wise_list.append(v)
            ppd_sdl_shipments=shipments.filter(product_type='ppd',reason_code_id=48,shipper=customer).exclude(rts_status__gt=0)
            for ppd_shipment in ppd_sdl_shipments:
                ppd_weight=ppd_weight+chargeable_weight(ppd_shipment)
                ppd_frieght=ppd_frieght+freight_charge(ppd_shipment)
                op=Order_price.objects.filter(ppd_shipmentment = ppd_shipment)
                if op:
                    ppd_shipmentment_charges = op[0]
                    ppd_sdl=ppd_sdl+ppd_shipmentment_charges.ppd_sdl_charge
                    ppd_fs=ppd_fs+ppd_shipmentment_charges.fuel_surcharge
                try:
                    ppd_cod_charge=ppd_cod_charge+ppd_shipment.codcharge_set.get().ppd_cod_charge
                except:
                    pass
                ppd_total=ppd_total+ppd_shipment.collectable_value
                ppd_cod_coll_value=ppd_shipment.collectable_value+ppd_cod_coll_value
            if len(ppd_shipments) <> 0:
                    ppd_wt_ppd_shipment=float((float(ppd_weight))/float((len(ppd_shipments))))
                    ppd_yld_ppd_shipment=float((float(ppd_total))/float((len(ppd_shipments))))
            else:
                    ppd_wt_ppd_shipment=0
                    ppd_yld_ppd_shipment=0
            ppd_wt_ppd_shipment=Decimal(str(ppd_wt_ppd_shipment)).quantize(Decimal('0.01'))
            ppd_yld_ppd_shipment=Decimal(str(ppd_yld_ppd_shipment)).quantize(Decimal('0.01'))
            if ppd_weight <> 0:
                    ppd_yld_kilo=ppd_yld_ppd_shipment=float((float(ppd_total))/float(ppd_weight))
            else:
                    ppd_yld_kilo=0
            ppd_yld_kilo=Decimal(str(ppd_yld_kilo)).quantize(Decimal('0.01'))

            if ppd_cod_coll_value <> 0:
                    ppd_cod_percent=ppd_yld_ppd_shipment=float(((float(ppd_cod_charge))/float(ppd_cod_coll_value))*100.0)
            else:
                    ppd_cod_percent=0
            ppd_cod_percent=Decimal(str(ppd_cod_percent)).quantize(Decimal('0.01'))

                #tmp=chargeable_ppd_weight(ppd_shipmentment)
            v=[zone,customer,'PPD-SDL',len(ppd_shipments),ppd_weight,ppd_frieght,ppd_sdl,ppd_fs,ppd_cod_charge,ppd_total,ppd_wt_ppd_shipment,ppd_yld_ppd_shipment,ppd_yld_kilo,ppd_cod_coll_value,ppd_cod_percent]
            customer_wise_list.append(v)
            cod_sdl_shipments=shipments.filter(product_type='cod',reason_code_id=48,shipper=customer).exclude(rts_status__gt=0)
            for ppd_shipments in cod_sdl_shipments:
                ppd_weight=ppd_weight+chargeable_weight(ppd_shipment)
                ppd_frieght=ppd_frieght+freight_charge(ppd_shipment)
                if Order_price.objects.filter(ppd_shipmentment = ppd_shipment):
                    ppd_shipmentment_charges = Order_price.objects.get(ppd_shipmentment = ppd_shipment)
                    ppd_sdl=ppd_sdl+ppd_shipmentment_charges.ppd_sdl_charge
                    ppd_fs=ppd_fs+ppd_shipmentment_charges.fuel_surcharge
                try:
                    ppd_cod_charge=ppd_cod_charge+ppd_shipment.codcharge_set.get().ppd_cod_charge
                except:
                    pass
                ppd_total=ppd_total+ppd_shipment.collectable_value
                if len(ppd_shipments) <> 0:
                    ppd_wt_ppd_shipment=float((float(ppd_weight))/float((len(ppd_shipments))))
                    ppd_yld_ppd_shipment=float((float(ppd_total))/float((len(ppd_shipments))))
                else:
                    ppd_wt_ppd_shipment=0
                    ppd_yld_ppd_shipment=0
                ppd_wt_ppd_shipment=Decimal(str(ppd_wt_ppd_shipment)).quantize(Decimal('0.01'))
                ppd_yld_ppd_shipment=Decimal(str(ppd_yld_ppd_shipment)).quantize(Decimal('0.01'))
                if ppd_weight <> 0:
                    ppd_yld_kilo=ppd_yld_ppd_shipment=float((float(ppd_total))/float(ppd_weight))
                else:
                    ppd_yld_kilo=0
                ppd_yld_kilo=Decimal(str(ppd_yld_kilo)).quantize(Decimal('0.01'))
                ppd_cod_coll_value=ppd_shipment.collectable_value+ppd_cod_coll_value
                if ppd_cod_coll_value <> 0:
                    ppd_cod_percent=ppd_yld_ppd_shipment=float(((float(ppd_cod_charge))/float(ppd_cod_coll_value))*100.0)
                else:
                    ppd_cod_percent=0
                ppd_cod_percent=Decimal(str(ppd_cod_percent)).quantize(Decimal('0.01'))

                #tmp=chargeable_ppd_weight(ppd_shipmentment)
                v=[zone,customer,'COD-SDL',len(ppd_shipments),ppd_weight,ppd_frieght,ppd_sdl,ppd_fs,ppd_cod_charge,ppd_total,ppd_wt_ppd_shipment,ppd_yld_ppd_shipment,ppd_yld_kilo,ppd_cod_coll_value,ppd_cod_percent]
                customer_wise_list.append(v)
            rts_ppd=shipments.filter(product_type='ppd',rts_status__in = [1,2])
            for ppd_shipment in rts_ppd:
                ppd_weight=ppd_weight+chargeable_weight(ppd_shipment)
                ppd_frieght=ppd_frieght+freight_charge(ppd_shipment)
                op=Order_price.objects.filter(ppd_shipmentment = ppd_shipment)
                if op:
                    ppd_shipmentment_charges = op[0]
                    ppd_sdl=ppd_sdl+ppd_shipmentment_charges.ppd_sdl_charge
                    ppd_fs=ppd_fs+ppd_shipmentment_charges.fuel_surcharge
                try:
                    ppd_cod_charge=ppd_cod_charge+ppd_shipment.codcharge_set.get().ppd_cod_charge
                except:
                    pass
                ppd_total=ppd_total+ppd_shipment.collectable_value
                if len(ppd_shipments) <> 0:
                    ppd_wt_ppd_shipment=float((float(ppd_weight))/float((len(ppd_shipments))))
                    ppd_yld_ppd_shipment=float((float(ppd_total))/float((len(ppd_shipments))))
                else:
                    ppd_wt_ppd_shipment=0
                    ppd_yld_ppd_shipment=0
                ppd_wt_ppd_shipment=Decimal(str(ppd_wt_ppd_shipment)).quantize(Decimal('0.01'))
                ppd_yld_ppd_shipment=Decimal(str(ppd_yld_ppd_shipment)).quantize(Decimal('0.01'))
                if ppd_weight <> 0:
                    ppd_yld_kilo=ppd_yld_ppd_shipment=float((float(ppd_total))/float(ppd_weight))
                else:
                    ppd_yld_kilo=0
                ppd_yld_kilo=Decimal(str(ppd_yld_kilo)).quantize(Decimal('0.01'))
                ppd_cod_coll_value=ppd_shipment.collectable_value+ppd_cod_coll_value
                if ppd_cod_coll_value <> 0:
                    ppd_cod_percent=ppd_yld_ppd_shipment=float(((float(ppd_cod_charge))/float(ppd_cod_coll_value))*100.0)
                else:
                    ppd_cod_percent=0
                ppd_cod_percent=Decimal(str(ppd_cod_percent)).quantize(Decimal('0.01'))

                #tmp=chargeable_ppd_weight(ppd_shipmentment)
                v=[zone,customer,'RTS-PPD',len(ppd_shipments),ppd_weight,ppd_frieght,ppd_sdl,ppd_fs,ppd_cod_charge,ppd_total,ppd_wt_ppd_shipment,ppd_yld_ppd_shipment,ppd_yld_kilo,ppd_cod_coll_value,ppd_cod_percent]
                customer_wise_list.append(v)
            rts_cod=shipments.filter(product_type='cod',rts_status__in=[1,2])
            for ppd_shipment in rts_cod:
                ppd_weight=ppd_weight+chargeable_weight(ppd_shipment)
                ppd_frieght=ppd_frieght+freight_charge(ppd_shipment)
                if Order_price.objects.filter(ppd_shipmentment = ppd_shipment):
                    ppd_shipmentment_charges = Order_price.objects.get(ppd_shipmentment = ppd_shipment)
                    ppd_sdl=ppd_sdl+ppd_shipmentment_charges.ppd_sdl_charge
                    ppd_fs=ppd_fs+ppd_shipmentment_charges.fuel_surcharge
                try:
                    ppd_cod_charge=ppd_cod_charge+ppd_shipment.codcharge_set.get().ppd_cod_charge
                except:
                    pass
                ppd_total=ppd_total+ppd_shipment.collectable_value
                if len(ppd_shipments) <> 0:
                    ppd_wt_ppd_shipment=float((float(ppd_weight))/float((len(ppd_shipments))))
                    ppd_yld_ppd_shipment=float((float(ppd_total))/float((len(ppd_shipments))))
                else:
                    ppd_wt_ppd_shipment=0
                    ppd_yld_ppd_shipment=0
                ppd_wt_ppd_shipment=Decimal(str(ppd_wt_ppd_shipment)).quantize(Decimal('0.01'))
                ppd_yld_ppd_shipment=Decimal(str(ppd_yld_ppd_shipment)).quantize(Decimal('0.01'))
                if ppd_weight <> 0:
                    ppd_yld_kilo=ppd_yld_ppd_shipment=float((float(ppd_total))/float(ppd_weight))
                else:
                    ppd_yld_kilo=0
                ppd_yld_kilo=Decimal(str(ppd_yld_kilo)).quantize(Decimal('0.01'))
                ppd_cod_coll_value=ppd_shipment.collectable_value+ppd_cod_coll_value
                if ppd_cod_coll_value <> 0:
                    ppd_cod_percent=ppd_yld_ppd_shipment=float(((float(ppd_cod_charge))/float(ppd_cod_coll_value))*100.0)
                else:
                    ppd_cod_percent=0
                ppd_cod_percent=Decimal(str(ppd_cod_percent)).quantize(Decimal('0.01'))

                #tmp=chargeable_ppd_weight(ppd_shipmentment)
                v=[zone,customer,'RTS-COD',len(ppd_shipments),ppd_weight,ppd_frieght,ppd_sdl,ppd_fs,ppd_cod_charge,ppd_total,ppd_wt_ppd_shipment,ppd_yld_ppd_shipment,ppd_yld_kilo,ppd_cod_coll_value,ppd_cod_percent]
                customer_wise_list.append(v)

        print zone.zone_name,len(shipments)
    print "this is the length of zwlr",len(zone_wise_list)
    for a in zone_wise_list:
            print "zone wise list record",a
    for b in customer_wise_list:
        print b
    style = datetime_style
    sheet = book.add_sheet('Daily Sales Report Zone Wise')
            #distinct_list = download_list
    sheet.write(0, 2, "Performance Analysis Customer Report", style=header_style)
    sheet.write(2,0, 'Customer',style=header_style)
    sheet.write(2,4, 'Date',style=header_style)
    sheet.write(2,5, report_date, style = style)
    #sheet.write(2,6,'to',style=header_style)
    #sheet.write(2,7,todate,style=style)
    for a in range(1,6):
        sheet.col(a).width = 7000
    sheet.write(5, 0, "Sr No", style=header_style)
    sheet.write(5, 1, "Zone Name", style=header_style)
    sheet.write(5, 2, "Total Shipments", style=header_style)
    sheet.write(5, 3, "Total Weight ", style=header_style)
    sheet.write(5, 4, "Total Frieght", style=header_style)
    sheet.write(5, 5, "Total SDL", style=header_style)
    sheet.write(5, 6, "Total FS", style=header_style)
    sheet.write(5, 7, "COD", style=header_style)
    sheet.write(5, 8, "Total", style=header_style)
    sheet.write(5, 9, "Wt/Shipment", style=header_style)
    sheet.write(5, 10, "Yld/Shipment", style=header_style)
    sheet.write(5, 11, "Yld/Kilos", style=header_style)
    sheet.write(5, 12, " COD Value ", style=header_style)
    sheet.write(5, 13, " COD %age ", style=header_style)
    counter = 1
    for row, rowdata in enumerate(zone_wise_list, start=6):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col == 4 or col == 6 or col == 9:
                            sheet.write(row, col, str(val)+'%', style=style)
                        else:
                            sheet.write(row, col, str(val), style=style)
    new_size=11+len(zone_wise_list)
    sheet.write(new_size-3, 4, " Detailed ", style=header_style)
    sheet.write(new_size-2, 0, "Zone", style=header_style)
    sheet.write(new_size-2, 1, "Customer", style=header_style)
    sheet.write(new_size-2, 2, "Type Shipments", style=header_style)
    sheet.write(new_size-2, 3, "Total Shipments", style=header_style)
    sheet.write(new_size-2, 4, "Total Weight ", style=header_style)
    sheet.write(new_size-2, 5, "Total Frieght", style=header_style)
    sheet.write(new_size-2, 6, "Total SDL", style=header_style)
    sheet.write(new_size-2, 7, "Total FS", style=header_style)
    sheet.write(new_size-2, 8, "COD", style=header_style)
    sheet.write(new_size-2, 9, "Total", style=header_style)
    sheet.write(new_size-2, 10, "Wt/Shipment", style=header_style)
    sheet.write(new_size-2, 11, "Yld/Shipment", style=header_style)
    sheet.write(new_size-2, 12, "Yld/Kilos", style=header_style)
    sheet.write(new_size-2, 13, " COD Value ", style=header_style)
    sheet.write(new_size-2, 14, " COD %age ", style=header_style)
    for row1, rowdata1 in enumerate(customer_wise_list, start=new_size):
                    for col1, val1 in enumerate(rowdata1, start=1):
                        if col1 == 4 or col1 == 6 or col1 == 9:
                            sheet.write(row1, col1, str(val1)+'%', style=style)
                        else:
                            sheet.write(row1, col1, str(val1), style=style)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Daily-Sales-Zone%s.xls',report_date
    book.save(response)
    return response


def update_general_section(user, field_name, obj_id, value):
    customer = Customer.objects.get(id=int(obj_id))
    # if there is not change log exists for given field name then create one
    # This must the initial change to the field

    if field_name == 'volumetricweightdivisor':
        volwt = customer.volumetricweightdivisor_set.all()
        if volwt.exists():
            volwt.update(divisor=int(value))
            vw = volwt[0]
        else:
            vw = VolumetricWeightDivisor.objects.create(customer=customer, divisor=int(value))

        prev = ChangeLogs.objects.get_previous_value(vw, 'volumetricweightdivisor')

        if prev is not None and (int(prev) == int(value)):
            return
        else:
            ChangeLogs.objects.create(customer=customer, user=user, field_name=field_name, content_object=vw, change_message=int(value))

        return

    if field_name == 'minactualweight':
        minwt = customer.minactualweight_set.all()
        if minwt.exists():
            minwt.update(weight=float(value))
            minwt = minwt[0]
        else:
            minwt = MinActualWeight.objects.create(customer=customer, weight=float(value))

        prev = ChangeLogs.objects.get_previous_value(minwt, 'minactualweight')

        if prev is not None and (prev==float(value)):
            return
        else:
            ChangeLogs.objects.create(customer=customer, user=user, field_name=field_name,
                                      content_object=minwt, change_message=int(value))
        return

    prev = ChangeLogs.objects.get_previous_value(customer, field_name)

    if prev == customer.__dict__[field_name]:
        return
    else:
        cl = ChangeLogs.objects.create(customer=customer, user=user, field_name=field_name,
            content_object=customer, change_message=customer.__dict__.get(field_name))

    cl.content_object = customer
    cl.change_message = float(value)
    if field_name == 'to_pay_charge':
        customer.to_pay_charge = float(value)
    elif field_name == 'demarrage_min_amt':
        customer.demarrage_min_amt = float(value)
    elif field_name == 'demarrage_perkg_amt':
        customer.demarrage_perkg_amt = float(value)
    elif field_name == 'reverse_charges':
        customer.reverse_charges = float(value)
    elif field_name == 'vchc_min':
        customer.vchc_min = float(value)
    elif field_name == 'vchc_min_amnt_applied':
        customer.vchc_min = int(float(value))
    elif field_name == 'vchc_rate':
        customer.vchc_rate = float(value)
        cl.change_message = int(float(value))
    elif field_name == 'flat_cod_amt':
        customer.flat_cod_amt = int(float(value))
        cl.change_message = int(float(value))

    cl.save()
    customer.save()

def update_defaultfreight_section(user, field_name, obj_id, value):
    freight = FreightSlab.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(FreightSlab).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=int(obj_id))
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=freight.customer, user=user,
            field_name=field_name, content_object=freight, change_message=freight.__dict__[field_name])

    cl = ChangeLogs(customer=freight.customer, user=user, field_name=field_name, content_object=freight)

    if field_name == 'slab':
        freight.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_from':
        freight.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        freight.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        freight.weight_rate = float(value)
        cl.change_message = float(value)
    cl.save()
    freight.save()
    BackDated.objects.create(customer=freight.customer,
            effective_date=freight.effective_date)


def update_freight_section(user, field_name, obj_id, value):
    freight = FreightSlabZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(FreightSlabZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=int(obj_id))
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=freight.customer, user=user,
            field_name=field_name, content_object=freight, change_message=freight.__dict__[field_name])

    cl = ChangeLogs(customer=freight.customer, user=user, field_name=field_name, content_object=freight)

    if field_name == 'slab':
        freight.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'rate_per_slab':
        freight.rate_per_slab = float(value)
        cl.change_message = float(value)
    elif field_name == 'range_from':
        freight.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        freight.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        freight.weight_rate = float(value)
        cl.change_message = float(value)
    cl.save()
    freight.save()
    BackDated.objects.create(customer=freight.customer,
            origin=freight.zone_org,
            destination=freight.zone_dest,
            effective_date=freight.effective_date)

def update_rtsfreight_section(user, field_name, obj_id, value):
    rts = RTSFreightSlabZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RTSFreightSlabZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=rts.id)
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=rts.customer, user=user,
            field_name=field_name, content_object=rts, change_message=rts.__dict__[field_name])

    cl = ChangeLogs(customer=rts.customer, user=user, field_name=field_name, content_object=rts)
    if field_name == 'slab':
        rts.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'rate_per_slab':
        rts.rate_per_slab = float(value)
        cl.change_message = float(value)
    elif field_name == 'range_from':
        rts.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        rts.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        rts.weight_rate = float(value)
        cl.change_message = float(value)
    rts.save()
    cl.save()
    BackDated.objects.create(customer=rts.customer,
            origin=rts.zone_org,
            destination=rts.zone_dest,
            rts=1,
            effective_date=rts.effective_date)

def update_sddfreight_section(user, field_name, obj_id, value):
    sdd = SDDSlabZone.objects.get(id=int(obj_id))

    cid = ContentType.objects.get_for_model(SDDSlabZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=int(obj_id))
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=sdd.customer, user=user,
            field_name=field_name, content_object=sdd, change_message=sdd.__dict__[field_name])

    cl = ChangeLogs(customer=sdd.customer, user=user, field_name=field_name, content_object=sdd)
    if field_name == 'slab':
        rts.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'rate_per_slab':
        rts.rate_per_slab = float(value)
        cl.change_message = float(value)
    elif field_name == 'range_from':
        rts.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        rts.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        rts.weight_rate = float(value)
        cl.change_message = float(value)
    sdd.save()
    cl.save()
    BackDated.objects.create(customer=sdd.customer,
            origin=sdd.zone_org,
            destination=sdd.zone_dest,
            sdd=1,
            effective_date=sdd.effective_date)

def update_reversefreight_section(user, field_name, obj_id, value):
    rev = ReverseFreightSlabZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(ReverseFreightSlabZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=rev.id)
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=rev.customer, user=user,
            field_name=field_name, content_object=rev, change_message=rev.__dict__[field_name])

    cl = ChangeLogs(customer=rev.customer, user=user, field_name=field_name, content_object=rev)
    if field_name == 'slab':
        rev.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'rate_per_slab':
        rev.rate_per_slab = float(value)
        cl.change_message = float(value)
    elif field_name == 'range_from':
        rev.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        rev.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        rev.weight_rate = float(value)
        cl.change_message = float(value)

    cl.save()
    rev.save()
    BackDated.objects.create(customer=rev.customer,
            origin=rev.zone_org,
            destination=rev.zone_dest,
            effective_date=rev.effective_date)

def update_defaults_section(user, field_name, obj_id, value):
    customer = Customer.objects.get(id=int(obj_id))
    fs = customer.fuelsurcharge_set.all()[0]
    cid = ContentType.objects.get_for_model(Customer).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fs.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fs.customer, user=user,
            field_name=field_name, content_object=fs, change_message=fs.__dict__[field_name])

    ChangeLogs.objects.create(customer=customer, user=user,
            field_name=field_name, content_object=fs, change_message=float(value))

    if field_name == 'fuelsurcharge_min_rate':
        fs.fuelsurcharge_min_rate = float(value)
    elif field_name == 'fuelsurcharge_min_fuel_rate':
        fs.fuelsurcharge_min_fuel_rate = float(value)
    elif field_name == 'flat_fuel_surcharge':
        fs.flat_fuel_surcharge = float(value)
    elif field_name == 'max_fuel_surcharge':
        fs.max_fuel_surcharge = float(value)
    fs.save()
    BackDated.objects.create(customer=fs.customer,
            effective_date=fs.effective_date)

def update_fuelsczone_section(user, field_name, obj_id, value):
    fsz = FuelSurchargeZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(FuelSurchargeZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fsz.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fsz.fuelsurcharge.customer, user=user,
            field_name=field_name, content_object=fsz, change_message=fsz.__dict__[field_name])

    ChangeLogs.objects.create(customer=fsz.fuelsurcharge.customer, user=user,
            field_name=field_name, content_object=fsz, change_message=float(value))

    if field_name == "fuelsurcharge_min_rate":
        fsz.fuelsurcharge_min_rate = float(value)
    elif field_name == "fuelsurcharge_min_fuel_rate":
        fsz.fuelsurcharge_min_fuel_rate = float(value)
    elif field_name == "flat_fuel_surcharge":
        fsz.flat_fuel_surcharge = float(value)
    elif field_name == "max_fuel_surcharge":
        fsz.max_fuel_surcharge = float(value)
    fsz.save()
    BackDated.objects.create(customer=fsz.customer,
            origin=fsz.f_zone_org,
            destination=fsz.f_zone_dest,
            effective_date=fsz.effective_date)

def update_rtsfuelsczone_section(user, field_name, obj_id, value):
    rfz = RTSFuelZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RTSFuelZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=rfz.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=rfz.customer, user=user,
            field_name=field_name, content_object=rfz, change_message=rfz.__dict__[field_name])

    ChangeLogs.objects.create(customer=rfz.customer, user=user, field_name=field_name,
            content_object=rfz, change_message=float(value))

    if field_name == 'rate':
        rfz.rate = float(value)
    rfz.save()
    BackDated.objects.create(customer=rfz.customer,
            origin=rfz.origin,
            destination=rfz.destination,
            rts=1,
            effective_date=rfz.effective_date)

def update_codcharge_section(user, field_name, obj_id, value, sect='codcharge'):
    if sect == 'codcharge':
        codcs = CashOnDelivery.objects.get(id=int(obj_id))
        cid = ContentType.objects.get_for_model(CashOnDelivery).id
        cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=codcs.id)
        org = None
        dest = None
    else:
        codcs = CashOnDeliveryZone.objects.get(id=int(obj_id))
        org = codcs.c_zone_org
        dest = codcs.c_zone_dest
        cid = ContentType.objects.get_for_model(CashOnDeliveryZone).id
        cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=codcs.id)

    if not cle.exists():
        ChangeLogs.objects.create(customer=codcs.customer, user=user,
            field_name=field_name, content_object=codcs, change_message=codcs.__dict__[field_name])

    ChangeLogs.objects.create(customer=codcs.customer, user=user, field_name=field_name,
            content_object=codcs, change_message=float(value))

    if field_name == 'COD_service_charge':
        codcs.COD_service_charge = float(value)
    elif field_name == 'start_range':
        codcs.start_range = float(value)
    elif field_name == 'end_range':
        codcs.end_range = float(value)
    elif field_name == 'flat_COD_charge':
        codcs.flat_COD_charge = float(value)
    elif field_name == 'minimum_COD_charge':
        codcs.minimum_COD_charge = float(value)
    codcs.save()
    BackDated.objects.create(customer=codcs.customer,
            origin=org,
            destination=dest,
            product_type=Product.objects.get(product_name='cod'),
            effective_date=codcs.effective_date)

def update_sdlslab_section(user, field_name, obj_id, value):
    sdl = SDLSlabCustomer.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(SDLSlabCustomer).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=sdl.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=sdl.customer, user=user,
            field_name=field_name, content_object=sdl, change_message=sdl.__dict__[field_name])

    ChangeLogs.objects.create(customer=sdl.customer, user=user, field_name=field_name,
            content_object=sdl, change_message=int(value))

    if field_name == 'slab':
        sdl.slab = int(value)
    elif field_name == 'weight_rate':
        sdl.weight_rate = int(value)
    elif field_name == 'range_from':
        sdl.range_from = int(value)
    elif field_name == 'range_to':
        sdl.range_to = int(value)
    sdl.save()
    BackDated.objects.create(customer=sdl.customer, sdl=1,
            effective_date=sdl.effective_date)

def update_rtsfreightzone_section(user, field_name, obj_id, value):
    fz = RTSFreightZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RtsFreightZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fz.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fz.customer, user=user,
            field_name=field_name, content_object=fz, change_message=fz.__dict__[field_name])

    ChangeLogs.objects.create(customer=fz.customer, user=user, field_name=field_name,
            content_object=fz, change_message=float(value))

    if field_name == 'rate':
        fz.rate = float(value)
    elif field_name == 'freight_charge':
        fz.freight_charge= float(value)
    elif field_name == 'slab':
        fz.slab = int(value)
    elif field_name == 'weight_rate':
        fz.weight_rate = int(value)
    elif field_name == 'range_from':
        fz.range_from = int(value)
    elif field_name == 'range_to':
        fz.range_to = int(value)
    fz.save()
    BackDated.objects.create(customer=fz.customer,
            origin=fz.origin,
            destination=fz.destination,
            rts=1,
            effective_date=fz.effective_date)

def update_rtsfuelzone_section(user, field_name, obj_id, value):
    fz = RTSFuelZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RtsFuelZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fz.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fz.customer, user=user,
            field_name=field_name, content_object=fz, change_message=fz.__dict__[field_name])

    ChangeLogs.objects.create(customer=fz.customer, user=user, field_name=field_name,
            content_object=fz, change_message=float(value))

    if field_name == 'rate':
        fz.rate = float(value)
    fz.save()
    BackDated.objects.create(customer=fz.customer,
            origin=fz.origin,
            destination=fz.destination,
            rts=1,
            effective_date=fz.effective_date)

def update_rtsfreightslab_section(user, field_name, obj_id, value):
    fs = RTSFreightSlabRate.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RTSFreightSlabRate).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fs.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fs.customer, user=user,
            field_name=field_name, content_object=fs, change_message=fs.__dict__[field_name])

    cl = ChangeLogs(customer=fs.customer, user=user, field_name=field_name,
                    content_object=freight, change_message=int(value))

    if field_name == 'slab':
        fs.slab = int(value)
    elif field_name == 'range_from':
        fs.range_from = int(value)
    elif field_name == 'range_to':
        fs.range_to = int(value)
    elif field_name == 'rate':
        fs.rate = float(value)
        cl.change_message = float(value)
    cl.save()
    fs.save()
    BackDated.objects.create(customer=fs.customer,
            origin=fs.origin,
            destination=fs.destination,
            rts=1,
            effective_date=fs.effective_date)

@csrf_exempt
def edit_field(request):
    f_id = request.POST.get('id').strip().split('-')
    value = request.POST.get('value')
    sect = f_id[0].strip()
    field_name = f_id[1].strip()
    obj_id = f_id[2].strip()
    user = request.user

    # GENERAL SECTION
    if sect == 'gen':
        update_general_section(user, field_name, obj_id, value)
    elif sect == 'defaultfreight':
        update_defaultfreight_section(user, field_name, obj_id, value)
    elif sect in ['freight', 'codfreight']:
        update_freight_section(user, field_name, obj_id, value)
    elif sect == 'rtsfreight':
        update_rtsfreight_section(user, field_name, obj_id, value)
    elif sect == 'sddfreight':
        update_sddfreight_section(user, field_name, obj_id, value)
    elif sect == 'reversefreight':
        update_reversefreight_section(user, field_name, obj_id, value)
    elif sect == 'defaultfs':
        update_defaults_section(user, field_name, obj_id, value)
    elif sect == 'fuelsc_zone':
        update_fuelsczone_section(user, field_name, obj_id, value)
    elif sect == 'rtsfuelsc_zone':
        update_rtsfuelsczone_section(user, field_name, obj_id, value)
    elif sect == 'codcharge':
        update_codcharge_section(user, field_name, obj_id, value)
    elif sect == 'codzone':
        update_codcharge_section(user, field_name, obj_id, value, 'codzone')
    elif sect == 'sdlcharge':
        update_sdlslab_section(user, field_name, obj_id, value)
    elif sect == 'rtsfreightzone':
        update_rtsfreightzone_section(user, field_name, obj_id, value)
    elif sect == 'rtsfuelzone': # not used now
        update_rtsfuelzone_section(user, field_name, obj_id, value)
    elif sect == 'rtsfreightslab':
        update_rtsfreightslab_section(user, field_name, obj_id, value)

    return HttpResponse(value)

def add_freight_section(user, data_dict, ptype='freight'):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    freight = FreightSlabZone()
    freight.customer = customer
    freight.mode = Mode.objects.get(id=1)
    if ptype == 'cod':
        freight.product = Product.objects.get(product_name='cod')
    field_name = data_dict.keys()

    if 'slab' in field_name:
        freight.slab = data_dict['slab']
    if 'rate_per_slab' in field_name:
        freight.rate_per_slab = data_dict['rate_per_slab']
    if 'range_from' in field_name:
        freight.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        freight.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        freight.weight_rate = data_dict['weight_rate']
    if 'zone_org' in field_name:
        freight.zone_org = Zone.objects.get(zone_shortcode = data_dict['zone_org'])
    if 'zone_dest' in field_name:
        freight.zone_dest = Zone.objects.get(zone_shortcode = data_dict['zone_dest'])
    freight.save()

def add_defaultfreight_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    freight = FreightSlab()
    freight.customer = customer
    freight.mode = Mode.objects.get(id=1)
    field_name = data_dict.keys()

    if 'slab' in field_name:
        freight.slab = data_dict['slab']
    if 'range_from' in field_name:
        freight.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        freight.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        freight.weight_rate = data_dict['weight_rate']
    freight.save()

def add_rtsfreight_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    rts = RTSFreightSlabZone()
    rts.customer = customer
    rts.mode = Mode.objects.get(id=1)
    field_name = data_dict.keys()

    if 'zone_org' in field_name:
        rts.zone_org = Zone.objects.get(zone_shortcode = data_dict['zone_org'])
    if 'zone_dest' in field_name:
        rts.zone_dest = Zone.objects.get(zone_shortcode = data_dict['zone_dest'])
    if 'slab' in field_name:
        rts.slab = data_dict['slab']
    if 'rate_per_slab' in field_name:
        rts.rate_per_slab = data_dict['rate_per_slab']
    if 'range_from' in field_name:
        rts.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        rts.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        rts.weight_rate = data_dict['weight_rate']

    rts.save()

def add_sddfreight_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    sdd = SDDSlabZone()
    sdd.customer = customer
    sdd.sddzone = SDDZone.objects.get(id=1)
    sdd.mode = Mode.objects.get(id=1)

    if 'zone_org' in field_name:
        sdd.zone_org = Zone.objects.get(zone_shortcode = data_dict['zone_org'])
    if 'zone_dest' in field_name:
        sdd.zone_dest = Zone.objects.get(zone_shortcode = data_dict['zone_dest'])
    if 'slab' in field_name:
        sdd.slab = data_dict['slab']
    if 'rate_per_slab' in field_name:
        sdd.rate_per_slab = data_dict['rate_per_slab']
    if 'range_from' in field_name:
        sdd.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        sdd.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        sdd.weight_rate = data_dict['weight_rate']
    sdd.save()

def add_reversefreight_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    rev = ReverseFreightSlabZone()
    rev.customer = customer
    rev.mode = Mode.objects.get(id=1)

    if 'zone_org' in field_name:
        rev.zone_org = Zone.objects.get(zone_shortcode = data_dict['zone_org'])
    if 'zone_dest' in field_name:
        rev.zone_dest = Zone.objects.get(zone_shortcode = data_dict['zone_dest'])
    if 'slab' in field_name:
        rev.slab = data_dict['slab']
    if 'rate_per_slab' in field_name:
        rev.rate_per_slab = data_dict['rate_per_slab']
    if 'range_from' in field_name:
        rev.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        rev.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        rev.weight_rate = data_dict['weight_rate']

    rev.save()

def add_defaults_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    if FuelSurcharge.objects.filter(customer=customer).exists():
        return

    field_name = data_dict.keys()
    fs = FuelSurcharge()
    fs.customer = customer

    if 'fuelsurcharge_min_rate' in field_name:
        fs.fuelsurcharge_min_rate = data_dict['fuelsurcharge_min_rate']
    if 'fuelsurcharge_min_fuel_rate' in field_name:
        fs.fuelsurcharge_min_fuel_rate = data_dict['fuelsurcharge_min_fuel_rate']
    if 'flat_fuel_surcharge' in field_name:
        fs.flat_fuel_surcharge = data_dict['flat_fuel_surcharge']
    if 'max_fuel_surcharge' in field_name:
        fs.max_fuel_surcharge = data_dict['max_fuel_surcharge']
    fs.save()

def add_fuelsczone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    fs = FuelSurchargeZone()
    fs.customer = customer

    if 'f_zone_org' in field_name:
        fs.f_zone_org = Zone.objects.get(zone_shortcode = data_dict['f_zone_org'])
    if 'f_zone_dest' in field_name:
        fs.f_zone_dest = Zone.objects.get(zone_shortcode = data_dict['f_zone_dest'])
    if 'fuelsurcharge_min_rate' in field_name:
        fs.fuelsurcharge_min_rate = data_dict['fuelsurcharge_min_rate']
    if 'fuelsurcharge_min_fuel_rate' in field_name:
        fs.fuelsurcharge_min_fuel_rate = data_dict['fuelsurcharge_min_fuel_rate']
    if 'flat_fuel_surcharge' in field_name:
        fs.flat_fuel_surcharge = data_dict['flat_fuel_surcharge']
    if 'max_fuel_surcharge' in field_name:
        fs.max_fuel_surcharge = data_dict['max_fuel_surcharge']
    fs.save()

def add_rtsfuelsczone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    rfz = RTSFuelZone()
    rfz.customer = customer

    if 'origin' in field_name:
        rfz.origin = Zone.objects.get(zone_shortcode = data_dict['origin'])
    if 'destination' in field_name:
        rfz.destination = Zone.objects.get(zone_shortcode = data_dict['destination'])
    if 'rate' in field_name:
        rfz.rate = data_dict['rate']
    rfz.save()

def add_codcharge_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    if CashOnDelivery.objects.filter(customer=customer).exists():
        return
    codcs = CashOnDelivery()
    codcs.customer = customer

    if 'COD_service_charge' in field_name:
        codcs.COD_service_charge = data_dict['COD_service_charge']
    if 'start_range' in field_name:
        codcs.start_range = data_dict['start_range']
    if 'end_range' in field_name:
        codcs.end_range = data_dict['end_range']
    if 'flat_COD_charge' in field_name:
        codcs.flat_COD_charge = data_dict['flat_COD_charge']
    if 'minimum_COD_charge' in field_name:
        codcs.minimum_COD_charge = data_dict['minimum_COD_charge']
    codcs.save()

def add_codchargezone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    if CashOnDeliveryZone.objects.filter(customer=customer).exists():
        return
    codcs = CashOnDeliveryZone()
    codcs.customer = customer

    if 'COD_service_charge' in field_name:
        codcs.COD_service_charge = data_dict['COD_service_charge']
    if 'start_range' in field_name:
        codcs.start_range = data_dict['start_range']
    if 'end_range' in field_name:
        codcs.end_range = data_dict['end_range']
    if 'flat_COD_charge' in field_name:
        codcs.flat_COD_charge = data_dict['flat_COD_charge']
    if 'minimum_COD_charge' in field_name:
        codcs.minimum_COD_charge = data_dict['minimum_COD_charge']
    if 'c_zone_org' in field_name:
        cod.c_zone_org = Zone.objects.get(zone_shortcode = data_dict['c_zone_org'])
    if 'c_zone_dest' in field_name:
        cod.c_zone_dest = Zone.objects.get(zone_shortcode = data_dict['c_zone_dest'])

    codcs.save()

def add_sdlslab_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    sdl = SDLSlabCustomer()
    sdl.mode = Mode.objects.get(id=1)
    sdl.customer = customer

    if 'slab' in field_name:
        sdl.slab = data_dict['slab']
    if 'range_from' in field_name:
        sdl.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        sdl.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        sdl.weight_rate = data_dict['weight_rate']

    sdl.save()

def add_rtsfreightzone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    fz = RTSFreightZone()
    fz.customer = customer
    fz.mode = Mode.objects.get(id=1)

    if 'origin' in field_name:
        fz.origin = Zone.objects.get(zone_shortcode = data_dict['origin'])
    if 'destination' in field_name:
        fz.destination = Zone.objects.get(zone_shortcode = data_dict['destination'])
    if 'rate' in field_name:
        fz.rate = data_dict['rate']
    if 'freight_charge' in field_name:
        fz.freight_charge = data_dict['freight_charge']
    if 'slab' in field_name:
        fz.slab = data_dict['slab']
    if 'range_from' in field_name:
        fz.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        fz.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        fz.weight_rate = data_dict['weight_rate']
    fz.save()

def add_rtsfuelzone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    fz = RTSFuelZone()

    if 'rate' in field_name:
        fz.rate = data_dict['rate']
    if 'origin' in field_name:
        fz.origin = data_dict['origin']
    if 'destination' in field_name:
        fz.destination = data_dict['destination']

    fz.save()

def add_rtsfreightslab_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    fs = RTSFreightSlabRate()
    fs.customer = customer

    if 'slab' in field_name:
        fs.slab = data_dict['slab']
    if 'range_from' in field_name:
        fs.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        fs.range_to = data_dict['range_to']
    if 'rate' in field_name:
        fs.rate = data_dict['rate']
    if 'origin' in field_name:
        fz.origin = data_dict['origin']
    if 'destination' in field_name:
        fz.destination = data_dict['destination']

    fs.save()

@csrf_exempt
def add_row(request):
    user = request.user
    data_dict = {}
    for k, v in request.POST.items():
        data_dict[k] = v

    sect = data_dict.pop('model_name')
    # GENERAL SECTION
    if sect == 'freight': #checked
        add_freight_section(user, data_dict)
    elif sect == 'codfreight':
        add_freight_section(user, data_dict, ptype='cod')
    elif sect == 'defaultfreight': #checked
        add_defaultfreight_section(user, data_dict)
    elif sect == 'rtsfreight': #checked
        add_rtsfreight_section(user, data_dict)
    elif sect == 'sddfreight': # checked
        add_sddfreight_section(user, data_dict) #checked
    elif sect == 'reversefreight': #checked
        add_reversefreight_section(user, data_dict)
    elif sect == 'defaultfs': #checked
        add_defaults_section(user, data_dict)
    elif sect == 'fuelsc_zone': #checked
        add_fuelsczone_section(user, data_dict)
    elif sect == 'rtsfuelsc_zone': #checked***********
        add_rtsfuelsczone_section(user, data_dict)
    elif sect == 'codcharge': #checked
        add_codcharge_section(user, data_dict)
    elif sect == 'codzone': #checked
        add_codchargezone_section(user, data_dict)
    elif sect == 'sdlcharge': #check
        add_sdlslab_section(user, data_dict) #checked
    elif sect == 'rtsfreightzone': #checked
        add_rtsfreightzone_section(user, data_dict)
    elif sect == 'rtsfuelzone': #checked - not used now
        add_rtsfuelzone_section(user, data_dict)
    elif sect == 'rtsfreightslab':
        add_rtsfreightslab_section(user, data_dict)
    data = simplejson.dumps({'success':True})
    return HttpResponse(data, mimetype='application/json')

@csrf_exempt
def return_value(request):
    value = request.POST.get('value')
    return HttpResponse(value)

@csrf_exempt
def update_effective_date(request):
    eff_date = request.POST.get('effective_date')
    effective_date = datetime.strptime(eff_date, '%Y-%m-%d')

    input_id = request.POST.get('input_id')
    input_str = input_id.strip().split('-')
    sect = input_str[0]

    obj_id = input_str[1]
    customer = Customer.objects.get(id=int(obj_id))

    if sect == 'freight': #checked
        cod_product = Product.objects.get(product_name='cod')
        FreightSlabZone.objects.filter(customer=customer).exclude(product=cod_product).update(effective_date=effective_date)
    elif sect == 'codfreight':#checked
        cod_product = Product.objects.get(product_name='cod')
        FreightSlabZone.objects.filter(customer=customer, product=cod_product).update(effective_date=effective_date)
    elif sect == 'defaultfreight': #c
        FreightSlab.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfreight': #checked
        RTSFreightSlabZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'sddfreight': # checked
        SDDSlabZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'reversefreight': #checked
        ReverseFreightSlabZone.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'defaultfs': #checked
        FuelSurcharge.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'fuelsc_zone': #checked
        FuelSurchargeZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfuelsc_zone': #checked***********
        RTSFuelZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'codcharge': #checked
        CashOnDelivery.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'codzone': #checked
        CashOnDeliveryZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'sdlcharge': #check
        SDLSlabCustomer.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfreightzone': #checked
        RTSFreightZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfuelzone': #checked - not used now
        RTSFuelZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfreightslab':
        RTSFreightSlabRate.objects.filter(customer=customer).update(effective_date=effective_date)

    data = simplejson.dumps({'success':True})
    return HttpResponse(data, mimetype='application/json')

def add_backdated(request):
    cust = request.POST['cust_id']
    org = request.POST['origin']
    origin = [int(x) for x in org.split(",")]
    dest = request.POST['dest']
    destination = [int(x) for x in dest.split(",")]
    product_type = request.POST['product_type']
    product_type = [int(x) for x in product_type.split(",")]
    date_from = request.POST['date_from']
    date_to = request.POST['date_to']

def previous_day_sales_report(request):
    return HttpRespose('This view has been removed.. use pdsr instead')

def pdsr(request, report_date_str):
    # expect date string in the following format: yyyy-mm-dd
    # Daily Report
    date_str = report_date_str
    if len(report_date_str.strip()) == 8:
        date_str = report_date_str[:4] + '-' + report_date_str[4:6] + '-' + report_date_str[6:]

    file_name = write_pdsr_to_excel(date_str)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s_report_%s.xls' % (file_name ,report_date_str)

    return HttpResponseRedirect("/static/uploads/%s"%(file_name))

def pds_report(request, report_date_str):
    if len(report_date_str.strip()) == 8:
        date_str = report_date_str[:4] + '-' + report_date_str[4:6] +'-' + report_date_str[6:]
    else:
        date_str = report_date_str

    file_name = write_pdsr_to_excel(date_str)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s_report_%s.xls' % (file_name ,report_date_str)

    return HttpResponseRedirect("/static/uploads/%s"%(file_name))

def get_customer_pricing(request):
    cid = request.GET.get('customer_id')
    print 'cid is ',cid
    customer = Customer.objects.get(id=cid)

    fsz = FreightSlabZone.objects.filter(customer=customer).order_by('zone_org__zone_name', 'zone_dest__zone_name','range_from')
    cod = CODFreightSlabZone.objects.filter(customer=customer).order_by('zone_org__zone_name', 'zone_dest__zone_name','range_from')
    rts = RTSFreightSlabZone.objects.filter(customer=customer).order_by('zone_org__zone_name', 'zone_dest__zone_name','range_from')
    rev = ReverseFreightSlabZone.objects.filter(customer=customer).order_by('zone_org__zone_name', 'zone_dest__zone_name','range_from')
    sdd = SDDSlabZone.objects.filter(customer=customer).order_by('zone_org__zone_name','zone_dest__zone_name','range_from')
    sdd = SDDSlabZone.objects.filter(customer=customer).order_by('zone_org__zone_name','zone_dest__zone_name','range_from')
    org_city = FreightSlabCity.objects.filter(customer=customer).order_by('range_from')
    org_zone = FreightSlabOriginZone.objects.filter(customer=customer).order_by('range_from')

    data = {'freights': fsz, 'codfreights':cod, 'rtsfreights': rts,
            'freight_org_city': org_city, 'freight_org_zone': org_zone,
            'reversefreights':rev, 'sddfreights':sdd, 'customer': customer}
    html = render_to_string('billing/customer_pricing.html', data)
    json = simplejson.dumps({'html': html})
    return HttpResponse(json, mimetype="application/json")


def update_general_section(user, field_name, obj_id, value):
    customer = Customer.objects.get(id=int(obj_id))
    # if there is not change log exists for given field name then create one
    # This must the initial change to the field

    if field_name == 'volumetricweightdivisor':
        volwt = customer.volumetricweightdivisor_set.all()
        if volwt.exists():
            volwt.update(divisor=int(value))
            vw = volwt[0]
        else:
            vw = VolumetricWeightDivisor.objects.create(customer=customer, divisor=int(value))

        prev = ChangeLogs.objects.get_previous_value(vw, 'volumetricweightdivisor')

        if prev is not None and (int(prev) == int(value)):
            return
        else:
            ChangeLogs.objects.create(customer=customer, user=user, field_name=field_name, content_object=vw, change_message=int(value))

        return

    if field_name == 'minactualweight':
        minwt = customer.minactualweight_set.all()
        if minwt.exists():
            minwt.update(weight=float(value))
            minwt = minwt[0]
        else:
            minwt = MinActualWeight.objects.create(customer=customer, weight=float(value))

        prev = ChangeLogs.objects.get_previous_value(minwt, 'minactualweight')

        if prev is not None and (prev==float(value)):
            return
        else:
            ChangeLogs.objects.create(customer=customer, user=user, field_name=field_name,
                                      content_object=minwt, change_message=int(value))
        return

    prev = ChangeLogs.objects.get_previous_value(customer, field_name)

    if prev == customer.__dict__[field_name]:
        return
    else:
        cl = ChangeLogs.objects.create(customer=customer, user=user, field_name=field_name,
            content_object=customer, change_message=customer.__dict__.get(field_name))

    cl.content_object = customer
    cl.change_message = float(value)
    if field_name == 'to_pay_charge':
        customer.to_pay_charge = float(value)
    elif field_name == 'demarrage_min_amt':
        customer.demarrage_min_amt = float(value)
    elif field_name == 'demarrage_perkg_amt':
        customer.demarrage_perkg_amt = float(value)
    elif field_name == 'reverse_charges':
        customer.reverse_charges = float(value)
    elif field_name == 'vchc_min':
        customer.vchc_min = float(value)
    elif field_name == 'vchc_min_amnt_applied':
        customer.vchc_min = int(float(value))
    elif field_name == 'vchc_rate':
        customer.vchc_rate = float(value)
        cl.change_message = int(float(value))
    elif field_name == 'flat_cod_amt':
        customer.flat_cod_amt = int(float(value))
        cl.change_message = int(float(value))

    cl.save()
    customer.save()

def update_defaultfreight_section(user, field_name, obj_id, value):
    freight = FreightSlab.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(FreightSlab).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=int(obj_id))
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=freight.customer, user=user,
            field_name=field_name, content_object=freight, change_message=freight.__dict__[field_name])

    cl = ChangeLogs(customer=freight.customer, user=user, field_name=field_name, content_object=freight)

    if field_name == 'slab':
        freight.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_from':
        freight.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        freight.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        freight.weight_rate = float(value)
        cl.change_message = float(value)
    cl.save()
    freight.save()
    BackDated.objects.create(customer=freight.customer,
            effective_date=freight.effective_date)


def update_freight_section(user, field_name, obj_id, value):
    freight = FreightSlabZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(FreightSlabZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=int(obj_id))
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=freight.customer, user=user,
            field_name=field_name, content_object=freight, change_message=freight.__dict__[field_name])

    cl = ChangeLogs(customer=freight.customer, user=user, field_name=field_name, content_object=freight)

    if field_name == 'slab':
        freight.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'rate_per_slab':
        freight.rate_per_slab = float(value)
        cl.change_message = float(value)
    elif field_name == 'range_from':
        freight.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        freight.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        freight.weight_rate = float(value)
        cl.change_message = float(value)
    cl.save()
    freight.save()
    BackDated.objects.create(customer=freight.customer,
            origin=freight.zone_org,
            destination=freight.zone_dest,
            effective_date=freight.effective_date)

def update_rtsfreight_section(user, field_name, obj_id, value):
    rts = RTSFreightSlabZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RTSFreightSlabZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=rts.id)
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=rts.customer, user=user,
            field_name=field_name, content_object=rts, change_message=rts.__dict__[field_name])

    cl = ChangeLogs(customer=rts.customer, user=user, field_name=field_name, content_object=rts)
    if field_name == 'slab':
        rts.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'rate_per_slab':
        rts.rate_per_slab = float(value)
        cl.change_message = float(value)
    elif field_name == 'range_from':
        rts.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        rts.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        rts.weight_rate = float(value)
        cl.change_message = float(value)
    rts.save()
    cl.save()
    BackDated.objects.create(customer=rts.customer,
            origin=rts.zone_org,
            destination=rts.zone_dest,
            rts=1,
            effective_date=rts.effective_date)

def update_sddfreight_section(user, field_name, obj_id, value):
    sdd = SDDSlabZone.objects.get(id=int(obj_id))

    cid = ContentType.objects.get_for_model(SDDSlabZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=int(obj_id))
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=sdd.customer, user=user,
            field_name=field_name, content_object=sdd, change_message=sdd.__dict__[field_name])

    cl = ChangeLogs(customer=sdd.customer, user=user, field_name=field_name, content_object=sdd)
    if field_name == 'slab':
        rts.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'rate_per_slab':
        rts.rate_per_slab = float(value)
        cl.change_message = float(value)
    elif field_name == 'range_from':
        rts.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        rts.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        rts.weight_rate = float(value)
        cl.change_message = float(value)
    sdd.save()
    cl.save()
    BackDated.objects.create(customer=sdd.customer,
            origin=sdd.zone_org,
            destination=sdd.zone_dest,
            sdd=1,
            effective_date=sdd.effective_date)

def update_reversefreight_section(user, field_name, obj_id, value):
    rev = ReverseFreightSlabZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(ReverseFreightSlabZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=rev.id)
    if not cle.exists():
        cl_init = ChangeLogs.objects.create(customer=rev.customer, user=user,
            field_name=field_name, content_object=rev, change_message=rev.__dict__[field_name])

    cl = ChangeLogs(customer=rev.customer, user=user, field_name=field_name, content_object=rev)
    if field_name == 'slab':
        rev.slab = int(value)
        cl.change_message = int(value)
    elif field_name == 'rate_per_slab':
        rev.rate_per_slab = float(value)
        cl.change_message = float(value)
    elif field_name == 'range_from':
        rev.range_from = int(value)
        cl.change_message = int(value)
    elif field_name == 'range_to':
        rev.range_to = int(value)
        cl.change_message = int(value)
    elif field_name == 'weight_rate':
        rev.weight_rate = float(value)
        cl.change_message = float(value)

    cl.save()
    rev.save()
    BackDated.objects.create(customer=rev.customer,
            origin=rev.zone_org,
            destination=rev.zone_dest,
            effective_date=rev.effective_date)

def update_defaults_section(user, field_name, obj_id, value):
    customer = Customer.objects.get(id=int(obj_id))
    fs = customer.fuelsurcharge_set.all()[0]
    cid = ContentType.objects.get_for_model(Customer).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fs.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fs.customer, user=user,
            field_name=field_name, content_object=fs, change_message=fs.__dict__[field_name])

    ChangeLogs.objects.create(customer=customer, user=user,
            field_name=field_name, content_object=fs, change_message=float(value))

    if field_name == 'fuelsurcharge_min_rate':
        fs.fuelsurcharge_min_rate = float(value)
    elif field_name == 'fuelsurcharge_min_fuel_rate':
        fs.fuelsurcharge_min_fuel_rate = float(value)
    elif field_name == 'flat_fuel_surcharge':
        fs.flat_fuel_surcharge = float(value)
    elif field_name == 'max_fuel_surcharge':
        fs.max_fuel_surcharge = float(value)
    fs.save()
    BackDated.objects.create(customer=fs.customer,
            effective_date=fs.effective_date)

def update_fuelsczone_section(user, field_name, obj_id, value):
    fsz = FuelSurchargeZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(FuelSurchargeZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fsz.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fsz.fuelsurcharge.customer, user=user,
            field_name=field_name, content_object=fsz, change_message=fsz.__dict__[field_name])

    ChangeLogs.objects.create(customer=fsz.fuelsurcharge.customer, user=user,
            field_name=field_name, content_object=fsz, change_message=float(value))

    if field_name == "fuelsurcharge_min_rate":
        fsz.fuelsurcharge_min_rate = float(value)
    elif field_name == "fuelsurcharge_min_fuel_rate":
        fsz.fuelsurcharge_min_fuel_rate = float(value)
    elif field_name == "flat_fuel_surcharge":
        fsz.flat_fuel_surcharge = float(value)
    elif field_name == "max_fuel_surcharge":
        fsz.max_fuel_surcharge = float(value)
    fsz.save()
    BackDated.objects.create(customer=fsz.customer,
            origin=fsz.f_zone_org,
            destination=fsz.f_zone_dest,
            effective_date=fsz.effective_date)

def update_rtsfuelsczone_section(user, field_name, obj_id, value):
    rfz = RTSFuelZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RTSFuelZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=rfz.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=rfz.customer, user=user,
            field_name=field_name, content_object=rfz, change_message=rfz.__dict__[field_name])

    ChangeLogs.objects.create(customer=rfz.customer, user=user, field_name=field_name,
            content_object=rfz, change_message=float(value))

    if field_name == 'rate':
        rfz.rate = float(value)
    rfz.save()
    BackDated.objects.create(customer=rfz.customer,
            origin=rfz.origin,
            destination=rfz.destination,
            rts=1,
            effective_date=rfz.effective_date)

def update_codcharge_section(user, field_name, obj_id, value, sect='codcharge'):
    if sect == 'codcharge':
        codcs = CashOnDelivery.objects.get(id=int(obj_id))
        cid = ContentType.objects.get_for_model(CashOnDelivery).id
        cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=codcs.id)
        org = None
        dest = None
    else:
        codcs = CashOnDeliveryZone.objects.get(id=int(obj_id))
        org = codcs.c_zone_org
        dest = codcs.c_zone_dest
        cid = ContentType.objects.get_for_model(CashOnDeliveryZone).id
        cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=codcs.id)

    if not cle.exists():
        ChangeLogs.objects.create(customer=codcs.customer, user=user,
            field_name=field_name, content_object=codcs, change_message=codcs.__dict__[field_name])

    ChangeLogs.objects.create(customer=codcs.customer, user=user, field_name=field_name,
            content_object=codcs, change_message=float(value))

    if field_name == 'COD_service_charge':
        codcs.COD_service_charge = float(value)
    elif field_name == 'start_range':
        codcs.start_range = float(value)
    elif field_name == 'end_range':
        codcs.end_range = float(value)
    elif field_name == 'flat_COD_charge':
        codcs.flat_COD_charge = float(value)
    elif field_name == 'minimum_COD_charge':
        codcs.minimum_COD_charge = float(value)
    codcs.save()
    BackDated.objects.create(customer=codcs.customer,
            origin=org,
            destination=dest,
            product_type=Product.objects.get(product_name='cod'),
            effective_date=codcs.effective_date)

def update_sdlslab_section(user, field_name, obj_id, value):
    sdl = SDLSlabCustomer.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(SDLSlabCustomer).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=sdl.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=sdl.customer, user=user,
            field_name=field_name, content_object=sdl, change_message=sdl.__dict__[field_name])

    ChangeLogs.objects.create(customer=sdl.customer, user=user, field_name=field_name,
            content_object=sdl, change_message=int(value))

    if field_name == 'slab':
        sdl.slab = int(value)
    elif field_name == 'weight_rate':
        sdl.weight_rate = int(value)
    elif field_name == 'range_from':
        sdl.range_from = int(value)
    elif field_name == 'range_to':
        sdl.range_to = int(value)
    sdl.save()
    BackDated.objects.create(customer=sdl.customer, sdl=1,
            effective_date=sdl.effective_date)

def update_rtsfreightzone_section(user, field_name, obj_id, value):
    fz = RTSFreightZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RtsFreightZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fz.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fz.customer, user=user,
            field_name=field_name, content_object=fz, change_message=fz.__dict__[field_name])

    ChangeLogs.objects.create(customer=fz.customer, user=user, field_name=field_name,
            content_object=fz, change_message=float(value))

    if field_name == 'rate':
        fz.rate = float(value)
    elif field_name == 'freight_charge':
        fz.freight_charge= float(value)
    elif field_name == 'slab':
        fz.slab = int(value)
    elif field_name == 'weight_rate':
        fz.weight_rate = int(value)
    elif field_name == 'range_from':
        fz.range_from = int(value)
    elif field_name == 'range_to':
        fz.range_to = int(value)
    fz.save()
    BackDated.objects.create(customer=fz.customer,
            origin=fz.origin,
            destination=fz.destination,
            rts=1,
            effective_date=fz.effective_date)

def update_rtsfuelzone_section(user, field_name, obj_id, value):
    fz = RTSFuelZone.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RtsFuelZone).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fz.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fz.customer, user=user,
            field_name=field_name, content_object=fz, change_message=fz.__dict__[field_name])

    ChangeLogs.objects.create(customer=fz.customer, user=user, field_name=field_name,
            content_object=fz, change_message=float(value))

    if field_name == 'rate':
        fz.rate = float(value)
    fz.save()
    BackDated.objects.create(customer=fz.customer,
            origin=fz.origin,
            destination=fz.destination,
            rts=1,
            effective_date=fz.effective_date)

def update_rtsfreightslab_section(user, field_name, obj_id, value):
    fs = RTSFreightSlabRate.objects.get(id=int(obj_id))
    cid = ContentType.objects.get_for_model(RTSFreightSlabRate).id
    cle = ChangeLogs.objects.filter(field_name=field_name, content_type_id=cid, object_id=fs.id)
    if not cle.exists():
        ChangeLogs.objects.create(customer=fs.customer, user=user,
            field_name=field_name, content_object=fs, change_message=fs.__dict__[field_name])

    cl = ChangeLogs(customer=fs.customer, user=user, field_name=field_name,
                    content_object=freight, change_message=int(value))

    if field_name == 'slab':
        fs.slab = int(value)
    elif field_name == 'range_from':
        fs.range_from = int(value)
    elif field_name == 'range_to':
        fs.range_to = int(value)
    elif field_name == 'rate':
        fs.rate = float(value)
        cl.change_message = float(value)
    cl.save()
    fs.save()
    BackDated.objects.create(customer=fs.customer,
            origin=fs.origin,
            destination=fs.destination,
            rts=1,
            effective_date=fs.effective_date)

@csrf_exempt
def edit_field(request):
    f_id = request.POST.get('id').strip().split('-')
    value = request.POST.get('value')
    sect = f_id[0].strip()
    field_name = f_id[1].strip()
    obj_id = f_id[2].strip()
    user = request.user

    # GENERAL SECTION
    if sect == 'gen':
        update_general_section(user, field_name, obj_id, value)
    elif sect == 'defaultfreight':
        update_defaultfreight_section(user, field_name, obj_id, value)
    elif sect in ['freight', 'codfreight']:
        update_freight_section(user, field_name, obj_id, value)
    elif sect == 'rtsfreight':
        update_rtsfreight_section(user, field_name, obj_id, value)
    elif sect == 'sddfreight':
        update_sddfreight_section(user, field_name, obj_id, value)
    elif sect == 'reversefreight':
        update_reversefreight_section(user, field_name, obj_id, value)
    elif sect == 'defaultfs':
        update_defaults_section(user, field_name, obj_id, value)
    elif sect == 'fuelsc_zone':
        update_fuelsczone_section(user, field_name, obj_id, value)
    elif sect == 'rtsfuelsc_zone':
        update_rtsfuelsczone_section(user, field_name, obj_id, value)
    elif sect == 'codcharge':
        update_codcharge_section(user, field_name, obj_id, value)
    elif sect == 'codzone':
        update_codcharge_section(user, field_name, obj_id, value, 'codzone')
    elif sect == 'sdlcharge':
        update_sdlslab_section(user, field_name, obj_id, value)
    elif sect == 'rtsfreightzone':
        update_rtsfreightzone_section(user, field_name, obj_id, value)
    elif sect == 'rtsfuelzone': # not used now
        update_rtsfuelzone_section(user, field_name, obj_id, value)
    elif sect == 'rtsfreightslab':
        update_rtsfreightslab_section(user, field_name, obj_id, value)

    return HttpResponse(value)

def add_freight_section(user, data_dict, ptype='freight'):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    freight = FreightSlabZone()
    freight.customer = customer
    freight.mode = Mode.objects.get(id=1)
    if ptype == 'cod':
        freight.product = Product.objects.get(product_name='cod')
    field_name = data_dict.keys()

    if 'slab' in field_name:
        freight.slab = data_dict['slab']
    if 'rate_per_slab' in field_name:
        freight.rate_per_slab = data_dict['rate_per_slab']
    if 'range_from' in field_name:
        freight.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        freight.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        freight.weight_rate = data_dict['weight_rate']
    if 'zone_org' in field_name:
        freight.zone_org = Zone.objects.get(zone_shortcode = data_dict['zone_org'])
    if 'zone_dest' in field_name:
        freight.zone_dest = Zone.objects.get(zone_shortcode = data_dict['zone_dest'])
    freight.save()

def add_defaultfreight_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    freight = FreightSlab()
    freight.customer = customer
    freight.mode = Mode.objects.get(id=1)
    field_name = data_dict.keys()

    if 'slab' in field_name:
        freight.slab = data_dict['slab']
    if 'range_from' in field_name:
        freight.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        freight.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        freight.weight_rate = data_dict['weight_rate']
    freight.save()

def add_rtsfreight_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    rts = RTSFreightSlabZone()
    rts.customer = customer
    rts.mode = Mode.objects.get(id=1)
    field_name = data_dict.keys()

    if 'zone_org' in field_name:
        rts.zone_org = Zone.objects.get(zone_shortcode = data_dict['zone_org'])
    if 'zone_dest' in field_name:
        rts.zone_dest = Zone.objects.get(zone_shortcode = data_dict['zone_dest'])
    if 'slab' in field_name:
        rts.slab = data_dict['slab']
    if 'rate_per_slab' in field_name:
        rts.rate_per_slab = data_dict['rate_per_slab']
    if 'range_from' in field_name:
        rts.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        rts.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        rts.weight_rate = data_dict['weight_rate']

    rts.save()

def add_sddfreight_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    sdd = SDDSlabZone()
    sdd.customer = customer
    sdd.sddzone = SDDZone.objects.get(id=1)
    sdd.mode = Mode.objects.get(id=1)

    if 'zone_org' in field_name:
        sdd.zone_org = Zone.objects.get(zone_shortcode = data_dict['zone_org'])
    if 'zone_dest' in field_name:
        sdd.zone_dest = Zone.objects.get(zone_shortcode = data_dict['zone_dest'])
    if 'slab' in field_name:
        sdd.slab = data_dict['slab']
    if 'rate_per_slab' in field_name:
        sdd.rate_per_slab = data_dict['rate_per_slab']
    if 'range_from' in field_name:
        sdd.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        sdd.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        sdd.weight_rate = data_dict['weight_rate']
    sdd.save()

def add_reversefreight_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    rev = ReverseFreightSlabZone()
    rev.customer = customer
    rev.mode = Mode.objects.get(id=1)

    if 'zone_org' in field_name:
        rev.zone_org = Zone.objects.get(zone_shortcode = data_dict['zone_org'])
    if 'zone_dest' in field_name:
        rev.zone_dest = Zone.objects.get(zone_shortcode = data_dict['zone_dest'])
    if 'slab' in field_name:
        rev.slab = data_dict['slab']
    if 'rate_per_slab' in field_name:
        rev.rate_per_slab = data_dict['rate_per_slab']
    if 'range_from' in field_name:
        rev.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        rev.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        rev.weight_rate = data_dict['weight_rate']

    rev.save()

def add_defaults_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    if FuelSurcharge.objects.filter(customer=customer).exists():
        return

    field_name = data_dict.keys()
    fs = FuelSurcharge()
    fs.customer = customer

    if 'fuelsurcharge_min_rate' in field_name:
        fs.fuelsurcharge_min_rate = data_dict['fuelsurcharge_min_rate']
    if 'fuelsurcharge_min_fuel_rate' in field_name:
        fs.fuelsurcharge_min_fuel_rate = data_dict['fuelsurcharge_min_fuel_rate']
    if 'flat_fuel_surcharge' in field_name:
        fs.flat_fuel_surcharge = data_dict['flat_fuel_surcharge']
    if 'max_fuel_surcharge' in field_name:
        fs.max_fuel_surcharge = data_dict['max_fuel_surcharge']
    fs.save()

def add_fuelsczone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    fs = FuelSurchargeZone()
    fs.customer = customer

    if 'f_zone_org' in field_name:
        fs.f_zone_org = Zone.objects.get(zone_shortcode = data_dict['f_zone_org'])
    if 'f_zone_dest' in field_name:
        fs.f_zone_dest = Zone.objects.get(zone_shortcode = data_dict['f_zone_dest'])
    if 'fuelsurcharge_min_rate' in field_name:
        fs.fuelsurcharge_min_rate = data_dict['fuelsurcharge_min_rate']
    if 'fuelsurcharge_min_fuel_rate' in field_name:
        fs.fuelsurcharge_min_fuel_rate = data_dict['fuelsurcharge_min_fuel_rate']
    if 'flat_fuel_surcharge' in field_name:
        fs.flat_fuel_surcharge = data_dict['flat_fuel_surcharge']
    if 'max_fuel_surcharge' in field_name:
        fs.max_fuel_surcharge = data_dict['max_fuel_surcharge']
    fs.save()

def add_rtsfuelsczone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    rfz = RTSFuelZone()
    rfz.customer = customer

    if 'origin' in field_name:
        rfz.origin = Zone.objects.get(zone_shortcode = data_dict['origin'])
    if 'destination' in field_name:
        rfz.destination = Zone.objects.get(zone_shortcode = data_dict['destination'])
    if 'rate' in field_name:
        rfz.rate = data_dict['rate']
    rfz.save()

def add_codcharge_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    if CashOnDelivery.objects.filter(customer=customer).exists():
        return
    codcs = CashOnDelivery()
    codcs.customer = customer

    if 'COD_service_charge' in field_name:
        codcs.COD_service_charge = data_dict['COD_service_charge']
    if 'start_range' in field_name:
        codcs.start_range = data_dict['start_range']
    if 'end_range' in field_name:
        codcs.end_range = data_dict['end_range']
    if 'flat_COD_charge' in field_name:
        codcs.flat_COD_charge = data_dict['flat_COD_charge']
    if 'minimum_COD_charge' in field_name:
        codcs.minimum_COD_charge = data_dict['minimum_COD_charge']
    codcs.save()

def add_codchargezone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    if CashOnDeliveryZone.objects.filter(customer=customer).exists():
        return
    codcs = CashOnDeliveryZone()
    codcs.customer = customer

    if 'COD_service_charge' in field_name:
        codcs.COD_service_charge = data_dict['COD_service_charge']
    if 'start_range' in field_name:
        codcs.start_range = data_dict['start_range']
    if 'end_range' in field_name:
        codcs.end_range = data_dict['end_range']
    if 'flat_COD_charge' in field_name:
        codcs.flat_COD_charge = data_dict['flat_COD_charge']
    if 'minimum_COD_charge' in field_name:
        codcs.minimum_COD_charge = data_dict['minimum_COD_charge']
    if 'c_zone_org' in field_name:
        cod.c_zone_org = Zone.objects.get(zone_shortcode = data_dict['c_zone_org'])
    if 'c_zone_dest' in field_name:
        cod.c_zone_dest = Zone.objects.get(zone_shortcode = data_dict['c_zone_dest'])

    codcs.save()

def add_sdlslab_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    sdl = SDLSlabCustomer()
    sdl.mode = Mode.objects.get(id=1)
    sdl.customer = customer

    if 'slab' in field_name:
        sdl.slab = data_dict['slab']
    if 'range_from' in field_name:
        sdl.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        sdl.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        sdl.weight_rate = data_dict['weight_rate']

    sdl.save()

def add_rtsfreightzone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    fz = RTSFreightZone()
    fz.customer = customer
    fz.mode = Mode.objects.get(id=1)

    if 'origin' in field_name:
        fz.origin = Zone.objects.get(zone_shortcode = data_dict['origin'])
    if 'destination' in field_name:
        fz.destination = Zone.objects.get(zone_shortcode = data_dict['destination'])
    if 'rate' in field_name:
        fz.rate = data_dict['rate']
    if 'freight_charge' in field_name:
        fz.freight_charge = data_dict['freight_charge']
    if 'slab' in field_name:
        fz.slab = data_dict['slab']
    if 'range_from' in field_name:
        fz.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        fz.range_to = data_dict['range_to']
    if 'weight_rate' in field_name:
        fz.weight_rate = data_dict['weight_rate']
    fz.save()

def add_rtsfuelzone_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    fz = RTSFuelZone()

    if 'rate' in field_name:
        fz.rate = data_dict['rate']
    if 'origin' in field_name:
        fz.origin = data_dict['origin']
    if 'destination' in field_name:
        fz.destination = data_dict['destination']

    fz.save()

def add_rtsfreightslab_section(user, data_dict):
    cust_id = data_dict.pop('customer_id')
    customer = Customer.objects.get(id=int(cust_id))
    field_name = data_dict.keys()
    fs = RTSFreightSlabRate()
    fs.customer = customer

    if 'slab' in field_name:
        fs.slab = data_dict['slab']
    if 'range_from' in field_name:
        fs.range_from = data_dict['range_from']
    if 'range_to' in field_name:
        fs.range_to = data_dict['range_to']
    if 'rate' in field_name:
        fs.rate = data_dict['rate']
    if 'origin' in field_name:
        fz.origin = data_dict['origin']
    if 'destination' in field_name:
        fz.destination = data_dict['destination']

    fs.save()

@csrf_exempt
def add_row(request):
    user = request.user
    data_dict = {}
    for k, v in request.POST.items():
        data_dict[k] = v

    sect = data_dict.pop('model_name')
    # GENERAL SECTION
    if sect == 'freight': #checked
        add_freight_section(user, data_dict)
    elif sect == 'codfreight':
        add_freight_section(user, data_dict, ptype='cod')
    elif sect == 'defaultfreight': #checked
        add_defaultfreight_section(user, data_dict)
    elif sect == 'rtsfreight': #checked
        add_rtsfreight_section(user, data_dict)
    elif sect == 'sddfreight': # checked
        add_sddfreight_section(user, data_dict) #checked
    elif sect == 'reversefreight': #checked
        add_reversefreight_section(user, data_dict)
    elif sect == 'defaultfs': #checked
        add_defaults_section(user, data_dict)
    elif sect == 'fuelsc_zone': #checked
        add_fuelsczone_section(user, data_dict)
    elif sect == 'rtsfuelsc_zone': #checked***********
        add_rtsfuelsczone_section(user, data_dict)
    elif sect == 'codcharge': #checked
        add_codcharge_section(user, data_dict)
    elif sect == 'codzone': #checked
        add_codchargezone_section(user, data_dict)
    elif sect == 'sdlcharge': #check
        add_sdlslab_section(user, data_dict) #checked
    elif sect == 'rtsfreightzone': #checked
        add_rtsfreightzone_section(user, data_dict)
    elif sect == 'rtsfuelzone': #checked - not used now
        add_rtsfuelzone_section(user, data_dict)
    elif sect == 'rtsfreightslab':
        add_rtsfreightslab_section(user, data_dict)
    data = simplejson.dumps({'success':True})
    return HttpResponse(data, mimetype='application/json')

@csrf_exempt
def return_value(request):
    value = request.POST.get('value')
    return HttpResponse(value)

@csrf_exempt
def update_effective_date(request):
    eff_date = request.POST.get('effective_date')
    effective_date = datetime.strptime(eff_date, '%Y-%m-%d')

    input_id = request.POST.get('input_id')
    input_str = input_id.strip().split('-')
    sect = input_str[0]

    obj_id = input_str[1]
    customer = Customer.objects.get(id=int(obj_id))

    if sect == 'freight': #checked
        cod_product = Product.objects.get(product_name='cod')
        FreightSlabZone.objects.filter(customer=customer).exclude(product=cod_product).update(effective_date=effective_date)
    elif sect == 'codfreight':#checked
        cod_product = Product.objects.get(product_name='cod')
        FreightSlabZone.objects.filter(customer=customer, product=cod_product).update(effective_date=effective_date)
    elif sect == 'defaultfreight': #c
        FreightSlab.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfreight': #checked
        RTSFreightSlabZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'sddfreight': # checked
        SDDSlabZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'reversefreight': #checked
        ReverseFreightSlabZone.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'defaultfs': #checked
        FuelSurcharge.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'fuelsc_zone': #checked
        FuelSurchargeZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfuelsc_zone': #checked***********
        RTSFuelZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'codcharge': #checked
        CashOnDelivery.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'codzone': #checked
        CashOnDeliveryZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'sdlcharge': #check
        SDLSlabCustomer.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfreightzone': #checked
        RTSFreightZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfuelzone': #checked - not used now
        RTSFuelZone.objects.filter(customer=customer).update(effective_date=effective_date)
    elif sect == 'rtsfreightslab':
        RTSFreightSlabRate.objects.filter(customer=customer).update(effective_date=effective_date)

    data = simplejson.dumps({'success':True})
    return HttpResponse(data, mimetype='application/json')

def add_backdated(request):
    cust = request.POST['cust_id']
    org = request.POST['origin']
    origin = [int(x) for x in org.split(",")]
    dest = request.POST['dest']
    destination = [int(x) for x in dest.split(",")]
    product_type = request.POST['product_type']
    product_type = [int(x) for x in product_type.split(",")]
    date_from = request.POST['date_from']
    date_to = request.POST['date_to']

def pdsr(request, report_date_str):
    print 'inside pdsr...'
    # expect date string in the following format: yyyy-mm-dd
    # Daily Report
    date_str = report_date_str
    if len(report_date_str.strip()) == 8:
        date_str = report_date_str[:4] + '-' + report_date_str[4:6] + '-' + report_date_str[6:]

    file_name = write_pdsr_to_excel(date_str)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s_report_%s.xls' % (file_name ,report_date_str)

    return HttpResponseRedirect("/static/uploads/%s"%(file_name))



def pds_report(request, report_date_str):
    if len(report_date_str.strip()) == 8:
        date_str = report_date_str[:4] + '-' + report_date_str[4:6] +'-' + report_date_str[6:]
    else:
        date_str = report_date_str

    file_name = write_pdsr_to_excel(date_str)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s_report_%s.xls' % (file_name ,report_date_str)

    return HttpResponseRedirect("/static/uploads/%s"%(file_name))

def get_customer_pricing(request):
    cid = request.GET.get('customer_id')
    print 'cid is ',cid
    customer = Customer.objects.get(id=cid)

    fsz = FreightSlabZone.objects.filter(freight_slab__customer=customer)\
                      .order_by('zone_org__zone_name', 'zone_dest__zone_name','freight_slab__range_from')
    cod = CODFreightSlabZone.objects.filter(freight_slab__customer=customer)\
                      .order_by('zone_org__zone_name', 'zone_dest__zone_name','freight_slab__range_from')
    rts = RTSFreightSlabZone.objects.filter(freight_slab__customer=customer)\
                      .order_by('zone_org__zone_name', 'zone_dest__zone_name','freight_slab__range_from')
    rev = ReverseFreightSlabZone.objects.filter(freight_slab__customer=customer)\
                      .order_by('zone_org__zone_name', 'zone_dest__zone_name','freight_slab__range_from')
    sdd = SDDSlabZone.objects.filter(freight_slab__customer=customer)\
                      .order_by('zone_org__zone_name','zone_dest__zone_name','freight_slab__range_from')
    org_city = FreightSlabCity.objects.filter(customer=customer).order_by('range_from')
    org_zone = FreightSlabOriginZone.objects.filter(customer=customer).order_by('range_from')

    data = {'freights': fsz, 'codfreights':cod, 'rtsfreights': rts,
            'freight_org_city': org_city, 'freight_org_zone': org_zone,
            'reversefreights':rev, 'sddfreights':sdd, 'customer': customer}
    html = render_to_string('billing/customer_pricing_test.html', data)
    json = simplejson.dumps({'html': html})
    return HttpResponse(json, mimetype="application/json")

def preview_billing(request):
    if request.method == 'POST':
        form = BillingPreviewForm(request.POST)
        if form.is_valid():
            file_path, month = form.save()
            if file_path:
                file_name = ntpath.basename(file_path)
                file_name = '{0}_preview/{1}'.format(month, file_name)
                return HttpResponseRedirect('/static/uploads/billing/' + file_name)
    return HttpResponseRedirect(reverse('billing-details'))

@json_view
def generate_report(request):
    year = request.GET.get('year')
    month = request.GET.get('month')
    customer = request.GET.get('customer')
    report_type = request.GET.get('report_type')
    q = Q()
    if int(customer):
        q = q & Q(customer=customer)
    bills = Billing.objects.filter(
        q, billing_date__year=year,billing_date__month=month)
    if bills.exists():
        bill_id = bills.latest('id').id
        if report_type == 'bill_summary':
            bill_list = Billing.objects.filter(billing_date__year=year,
                billing_date__month=month).values_list('id', flat=True)
            file_name = generate_bill_summary_xls(bill_list)
            file_path = root_url + file_name.split('ecomexpress')[1]
        elif report_type == 'awb_pdf':
            file_name = generate_awbpdf_report(bill_id)
            file_path = root_url + file_name.split('ecomexpress')[1]
        elif report_type == 'awb_excel':
            file_name = generate_awbexcel_report(bill_id)
            file_path = root_url + file_name.split('ecomexpress')[1]
        elif report_type == 'invoice_pdf':
            file_name = generate_bill_pdf(bill_id)
            file_path = root_url + file_name.split('ecomexpress')[1]
        elif report_type == 'invoice_pdf_headless':
            file_name = generate_bill_pdf(bill_id, with_header=False)
            file_path = root_url + file_name.split('ecomexpress')[1]
        elif report_type == 'jasper_report':
            bill = bills.latest('id')
            file_name = jasper_generate_report(bill.billing_date_from, bill.billing_date)
            file_path = root_url + '/static/uploads/reports/' + file_name
        return {'success': True, 'file_path': file_path}

    return {'success': False}


def auto_billing(request):
    bill_generation_form = BillingGenerationForm()
    provisional_form = ProvisionalBillingGenerationForm()
    return render_to_response(
        'billing_admin/home.html',
        {'bill_generation_form': bill_generation_form,
         'provisional_form': provisional_form},
        context_instance=RequestContext(request))


@json_view
def provisional_billing(request):
    if request.method == 'POST' and request.is_ajax():
        form = ProvisionalBillingGenerationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            ProvisionalBillingQueue.objects.create(
                billing_from=data.get('provisional_billing_from'),
                billing_to=data.get('provisional_billing_to'))
            message = ("Provisional Billing has been started."
                 "You will be notified by a mail once billing is done.")
            return {'success': True, 'message': message, 'data': data}
        else:
            return {'success': False, 'errors': form.errors}


def ebs_report(request):
    return HttpResponse("success")


@json_view
def update_provisional_reports(request):
    queue = ProvisionalBillingQueue.objects.order_by('-id')[:10].values(
        'id', 'status', 'billing_from', 'billing_to')
    html = render_to_string('billing_admin/provisional_reports.html', {'queue': queue})
    return {'html': html}


def provisional_report(request, queue_id):
    queue = ProvisionalBillingQueue.objects.get(id=queue_id)
    bill_ids = queue.bills.values_list('id', flat=True)
    full_path = generate_provisional_bill_summary_xls(bill_ids)
    file_name = ntpath.basename(full_path)
    return HttpResponseRedirect('/static/uploads/billing/{0}'.format(file_name))


@json_view
def generate_billing(request):
    if request.method == 'POST' and request.is_ajax():
        form = BillingGenerationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            BillingQueue.objects.create(
                billing_from=data.get('billing_from'),
                billing_to=data.get('billing_to'))
            message = ("Billing has been started."
                 "You will be notified by a mail once billing is done.")
            return {'success': True, 'message': message, 'data': data}
        else:
            return {'success': False, 'errors': form.errors}


@json_view
def update_billing_status(request):
    queue = BillingQueue.objects.order_by('-id')[:10].values(
        'id', 'status', 'billing_from', 'billing_to')
    html = render_to_string('billing_admin/billing_status.html', {'queue': queue})
    return {'html': html}

def bill_summary(request, queue_id):
    queue = BillingQueue.objects.get(id=queue_id)
    bill_ids = queue.bills.values_list('id', flat=True)
    full_path = generate_bill_summary_xls(bill_ids)
    file_name = ntpath.basename(full_path)
    return HttpResponseRedirect('/static/uploads/billing/{0}'.format(file_name))


@json_view
def update_billing_reports(request):
    queue = BillingQueue.objects.order_by('-id')[:10].values(
        'id', 'status', 'billing_from', 'billing_to')
    customers = Customer.objects.values('code', 'name')
    bill_report_form = BillingReportQueueForm()
    html = render_to_string(
        'billing_admin/billing_reports.html',
        {'queue': queue, 'customers': customers, 
         'bill_report_form': bill_report_form})
    return {'html': html}

@csrf_exempt
def add_to_report_queue(request):
    if request.method == 'POST':
        form = BillingReportQueueForm(request.POST)
        billqueue = request.POST.get('billqueue')
        bill_queue = BillingQueue.objects.get(id=billqueue)
        if form.is_valid():
            form.save(bill_queue)
            return HttpResponse('success!. Mail will be send to your registered email, when the report generation is completed.')
        else:
            return HttpResponse('fail')
    else:
        return HttpResponseRedirect(reverse('auto-billing'))

@json_view
def get_customer_reports(request):
    if request.method == 'GET' and request.is_ajax():
        queue_id = request.GET.get('queue_id')
        queue = BillingQueue.objects.get(id=queue_id)
        reports = CustomerBillingReport.objects.filter(billqueue=queue)
        html = render_to_string(
            'billing_admin/customer_billing_reports_list.html',
            {'reports': reports})
    
        return {'html': html, 'success': True}
    else:
        return {'html': '<h3>customer report link</h3>', 'success': False}


@csrf_exempt
def run_backdated(request):
     if request.POST:
         shipper = Customer.objects.get(id=request.POST['cust_name'])
         from_date = request.POST['date_from']
         date_to = request.POST['date_to']
         zone_from = request.POST['zone_from']
         zone_to = request.POST['zone_to']
         prod_type = request.POST['type']
         rts_status = request.POST['checkbox']
         if zone_from == "0":
            org_zone = None
         else:
            org_zone = Zone.objects.get(id=zone_from)
         if zone_to == "0":
            dest_zone = None
         else:
            dest_zone = Zone.objects.get(id=zone_to)
         if prod_type == "all_type":
            product  =  None
         if product:
            product= Product.objects.get(product_name=prod_type)

         check = BackdatedBatch.objects.filter(product_type=product,\
                 date_from=from_date,date_to=date_to, customer=shipper,org_zone=org_zone,dest_zone=dest_zone,status__in=[0,1])
         
         if not check:
             BackdatedBatch.objects.create(date_from=from_date,product_type=product,date_to=date_to,customer=shipper,org_zone=org_zone,dest_zone=dest_zone)
         process_batch()
         return HttpResponse(rts_status)
     else:
         customer = Customer.objects.filter(activation_status = True)
         zone = Zone.objects.filter(id__gte=13)
         batches=BackdatedBatch.objects.filter().order_by('status')
         return render_to_response("billing/run_bacdated.html",
                               {'customer':customer,'zone':zone,'batch':batches},
                               context_instance=RequestContext(request))

def process_batch():
         for batch in BackdatedBatch.objects.filter(status=0):
                 zone_label = batch.customer.zone_label
                 q = Q(shipment_date__range=(batch.date_from,batch.date_to),billing=None, shipper_id = batch.customer_id)
                 if batch.org_zone:
                      q = q & Q(pickup__service_centre__city__labeled_zones = batch.org_zone)

                 if batch.dest_zone:
                      q = q & Q(original_dest__city__labeled_zones = batch.dest_zone)

                 #get client zonelabel,city__Label_Zone=zone
                 ships=Shipment.objects.filter(q)
                 #ships=Shipment.objects.filter(shipment_date__range=(batch.date_from,batch.date_to),billing=None,pickup__service_centre__city__zone=batch.org_zone,original_dest__city__zone=batch.dest_zone,shipper=batch.customer)
                 #batch.status = 1
                 #batch.update()
                 batch=BackdatedBatch.objects.filter(id=batch.id)
                 count = 0
                 for s in ships:
                        add_awb(s.awb,bid)
                        count += 1
                 batch.update(count=count,status=1)



def add_awb(awb,bid):
     batch=BackdatedBatch.objects.get(id=bid)
     ship=Shipment.objects.get(airwaybill_number=awb)
     if ship.rts_status == 1:
        rts=1
     else:
        rts=0
     check = BackdatedShipmentBillingQueue.objects.filter(backdated_bacth=batch,airwaybill_number=awb)
     if not check:
          BackdatedShipmentBillingQueue.objects.getcreate(backdated_bacth=batch,airwaybill_number=awb,shipment_date=ship.shipment_date,shipment_type=rts,product_type=ship.shipext.product)




def process_queue():
       error_list=[]
       pending_ships = BackdatedShipmentBillingQueue.objects.filter(status = 0)[5000]
       for sh in  pending_ships:
               ship = Shipment.objects.get(airwaybill_number=sh.airwaybill_number)
               if not ship.billing:
                  if not ship.shipext.product:
                            ShipmentExtension.objects.filter(shipment__airwaybill_number = shipment.airwaybill_number).update(product=shipment.product_type)
                            try:
                                  if ship.rts_status == 1:
                                       rts_pricing(ship)
                                  else:
                                      price_updated(ship)
                                  btch= sh.backdated_bacth
                                  cnt=btch.processed_count
                                  cnt=cnt+1
                                  BackdatedBatch.objects.filter(id=btc.id).update(processed_count=cnt)
                            except:
                                  error_list.append(shipment.airwaybill_number)
