# Create your views here.
import os
import datetime
from collections import defaultdict
from xlsxwriter.workbook import Workbook

from utils import history_update
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.conf import settings
from django.template import RequestContext
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from service_centre.models import *
from octroi.forms import OctroiBillingForm
from octroi.models import OctroiBilling,CustomerOctroiCharges
from octroi.oct_reports import get_invoice_summary, get_octroi_excel_report, get_octroi_pdf_report
from octroi.custom_billing import CustomBilling

import imp
ReportGenerator = imp.load_source('ReportGenerator', settings.PROJECT_ROOT_DIR + 'reports/report_api.py')

now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")
before = now - datetime.timedelta(days=10)
beforem = now - datetime.timedelta(days=30)

def octroi_billing_details(request, updated):
    oct_ships = OctroiShipments.objects.filter(status=1, octroi_billing=None).exclude(receipt_number="")\
            .values('shipper').annotate(Count('shipper'))

    unbilled_customers_id = [int(d.get('shipper')) for d in oct_ships]
    all_customers = list(Customer.objects.values_list('id', flat=True))
    billed_customers_id = list(set(all_customers) - set(unbilled_customers_id))

    billed_customers = Customer.objects.filter(id__in=billed_customers_id)
    unbilled_customers = Customer.objects.filter(id__in=unbilled_customers_id)
    cust=Customer.objects.all() 
    return render_to_response("octroi/octroibillingdetails.html",
                              {'billed_customers':billed_customers,'cust':cust,
                               'unbilled_customers':unbilled_customers},
                              context_instance=RequestContext(request))

def customer(request, cid):
    if request.method == 'GET':
        customer = Customer.objects.get(id=cid)
        octroi_form = OctroiBillingForm(initial={"customer":customer.pk})
        octroi_billings = OctroiBilling.objects.filter(customer=customer).order_by('-id')[:10]
        unbilled_ship_count = OctroiShipments.objects.filter(shipper__id=cid, octroi_billing=None, status=1).exclude(receipt_number="").only('id').count()
        try:
            octroi_charge = CustomerOctroiCharges.objects.get(customer__id =cid)
        except CustomerOctroiCharges.DoesNotExist:
            octroi_charge = CustomerOctroiCharges.objects.create(customer=customer,octroi_rate=5.5,octroi_charge=5.0)
        return render_to_response("octroi/customer.html",
                    {'customer':customer,
                     'unbilled_ship_count':unbilled_ship_count,
                     'octroi_form':octroi_form,
		     'octroi_charge':octroi_charge,
                     'octroi_billings':octroi_billings},
                    context_instance=RequestContext(request))
    elif request.method == 'POST':
        cid=request.POST['cid']
        oct_file = request.FILES['oct_file']
        octroi_value = request.POST['octroi_value']
        if not octroi_value == '':
            octroi_value = octroi_value
        else:
            octroi_value = 5.5

        content = oct_file.read()
        c = CustomBilling(cid, content, octroi_value)
        generate_result = c.generate_bill()
        if generate_result[0]:
            error_list = []
            error_awbs = []
        else:
            error_list = generate_result[1]['error_list']
            error_awbs = generate_result[1]['error_awbs']
        customer = Customer.objects.get(id=cid)
        octroi_form = OctroiBillingForm(initial={"customer":customer.pk})
        octroi_billings = OctroiBilling.objects.filter(customer=customer).order_by('-id')[:10]
        unbilled_ship_count = OctroiShipments.objects.filter(shipper__id=cid, octroi_billing=None, status=1).exclude(receipt_number="").count()

        return render_to_response("octroi/customer.html",
                    {'customer':customer,
                     'unbilled_ship_count':unbilled_ship_count,
                     'octroi_form':octroi_form,
                     'octroi_billings':octroi_billings,
                     'error_list':error_list,
                     'error_awbs':error_awbs},
                    context_instance=RequestContext(request))

def unbilled_ships(request, cid):
    customer = Customer.objects.get(id=cid)
    octroi_shipments = OctroiShipments.objects.filter(shipper__id=cid, octroi_billing=None, status=1).exclude(receipt_number="")
    return render_to_response("octroi/unbilled_ships.html",
            {'octroi_shipments': octroi_shipments, 'customer':customer},
            context_instance=RequestContext(request))

@csrf_exempt
def octroiupdate(request):
   if request.is_ajax():
      date = request.POST['oct_date']
      ship = OctroiAirportConfirmation.objects.filter(status=0)
      if not ship:
         return HttpResponse("No shipments for Octroi")
      oct = Octroi.objects.create(date = date, origin=request.user.employeemaster.service_centre)
      for a in ship:
                OctroiShipments.objects.create(octroi=oct, shipment=a.shipment, shipper=a.shipment.shipper, origin=a.origin)
                OctroiAirportConfirmation.objects.filter(id=a.id).update(status=1, updated_on=now)
      return render_to_response("hub/octroi_data.html",
                        {"a":oct},)
   else:
      if request.user.employeemaster.employee_code in ['10500','10612','11662']:
         octroi = Octroi.objects.filter().order_by('-id')
      else:
          octroi = Octroi.objects.filter(origin=request.user.employeemaster.service_centre).order_by('-id')
      shipper = Customer.objects.all()

   return render_to_response("octroi/octroi_update.html",
                                  {"octroi":octroi,
                                   'shipper':shipper},
                                  # 'origin_sc':request.user.employeemaster.service_centre},
                                  context_instance=RequestContext(request))

def octroibilling(request, oid):
    octroi=Octroi.objects.get(id=oid)
    shipments = OctroiShipments.objects.filter(octroi=octroi)
    weight = shipments.aggregate(Sum('shipment__chargeable_weight'))
    weight = weight['shipment__chargeable_weight__sum']
    dec_value = shipments.aggregate(Sum('shipment__declared_value'))
    dec_value = dec_value['shipment__declared_value__sum']
   # bags = shipments.aggregate(Count('shipment__bags'))
   # bags = bags['shipment__bags__count']
    ls = []
    for a in shipments:
        if a.shipment.bags_set.filter():
            ls.append(a.shipment.bags_set.filter()[0])
    bags = len(set(ls))
    text = render_to_string("hub/manifest_txt.html",
                                  {'bags':bags,
                                   'dec_value':dec_value,
                                   'weight':weight,
                                   'shipments':shipments},
                                   context_instance=RequestContext(request))
    response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=octroi_manifest.txt'
    return response

def octroi_summary_edit(request,oid):
    octroi=Octroi.objects.get(id=oid)
    shipments = OctroiShipments.objects.filter(octroi=octroi)
    text=render_to_string("hub/manisfest_txt_rates.html",
				{
					'shipments':shipments
				},context_instance=RequestContext(request))
    response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=octroi_manifest.txt'
    return response

def add_billing(request):
    if request.method == 'POST':
        form = OctroiBillingForm(request.POST)
        if form.is_valid():
            octroi_billing = form.save()
            if octroi_billing == None:
                return HttpResponse('There are no octroi shipments in the given date range')
            return HttpResponseRedirect(reverse('octroi-customer', kwargs={'cid':octroi_billing.customer.id}))
        else:
            return HttpResponseRedirect(reverse('octroi-billing-details'))
    else:
        return HttpResponseRedirect(reverse('octroi-billing-details'))

def invoice_summary(request, bid):
    file_name = 'octroi_invoice_summary_{0}.pdf'.format(bid)
    fp = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/billing/{0}'.format(file_name)
    if not os.path.exists(fp):
        file_path = get_invoice_summary(bid, file_name)
    else:
        file_path = '/static/uploads/billing/{0}'.format(file_name)
    return HttpResponseRedirect(file_path)

def invoice_summary_without_header(request, bid):
    file_name = 'octroi_invoice_summary_headless_{0}.pdf'.format(bid)
    fp = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/billing/{0}'.format(file_name)
    if not os.path.exists(fp):
        file_path = get_invoice_summary(bid, file_name, with_header=False)
    else:
        file_path = '/static/uploads/billing/{0}'.format(file_name)
    return HttpResponseRedirect(file_path)

def awb_pdf(request, bid):
    file_name = 'octroi_awb_pdf_{0}.pdf'.format(bid)
    fp = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/billing/{0}'.format(file_name)
    if not os.path.exists(fp):
        file_path = get_octroi_pdf_report(bid)
    else:
        file_path = '/static/uploads/billing/{0}'.format(file_name)
    return HttpResponseRedirect(file_path)

def awb_excel(request, bid):
    file_name = 'octroi_awb_excel_{0}.xlsx'.format(bid)
    fp = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/billing/{0}'.format(file_name)
    if not os.path.exists(fp):
        file_path = get_octroi_excel_report(bid)
    else:
        file_path = '/static/uploads/billing/{0}'.format(file_name)
    return HttpResponseRedirect(file_path)

def custom_billing(request):
    if request.method == 'POST':
        cid=request.POST['cid']
        oct_file = request.FILES['oct_file']
        octroi_value = request.POST['octroi_value']
        if not octroi_value == '':
            octroi_value = octroi_value
        else:
            octroi_value = 5.5

        content = oct_file.read()
        c = CustomBilling(cid, content, octroi_value)
        generate_result = c.generate_bill()
        if generate_result[0]:
            error_list = []
            error_awbs = []
        else:
            error_list = generate_result[1]['error_list']
            error_awbs = generate_result[1]['error_awbs']
        customer = Customer.objects.get(id=cid)
        octroi_form = OctroiBillingForm(initial={"customer":customer.pk})
        octroi_billings = OctroiBilling.objects.filter(customer=customer)[:10]
        unbilled_ship_count = OctroiShipments.objects.filter(shipper__id=cid, octroi_billing=None, status=1).exclude(receipt_number="").count()

        return render_to_response("octroi/customer.html",
                    {'customer':customer,
                     'unbilled_ship_count':unbilled_ship_count,
                     'octroi_form':octroi_form,
                     'octroi_billings':octroi_billings,
                     'error_list':error_list,
                     'error_awbs':error_awbs},
                    context_instance=RequestContext(request))

@csrf_exempt
def process_reports(request):
   download_list = []
   if request.method == 'POST':
        date_from=request.POST['date_from'] 
        date_to=request.POST['date_to']
        cust=request.POST['cust']
        report_type=request.POST['report_type']
        t = datetime.datetime.strptime(date_from, "%Y%m%d") 
        date_from=t.strftime("%Y-%m-%d")
        t = datetime.datetime.strptime(date_to, "%Y%m%d") 
        date_to=t.strftime("%Y-%m-%d")
        if cust=="All":
            oct_bills=OctroiBilling.objects.all()
        else:
           cust_code=cust.split("-")
           cust=Customer.objects.get(code=int(cust_code[1]))
           oct_bills=OctroiBilling.objects.filter(customer=cust)
        return HttpResponse(str(date_from))
    
@csrf_exempt
def octroi_cus_process_reports(request):
    if request.method == 'POST':
        report_type = request.POST['oc_reports']
        if report_type == '2':
            date_from=request.POST['date_from']
            date_to=request.POST['date_to']
            t = datetime.datetime.strptime(date_from, "%Y%m%d")
            date_from=t.strftime("%Y-%m-%d")
            t = datetime.datetime.strptime(date_to, "%Y%m%d")
            date_to=t.strftime("%Y-%m-%d")
            report = ReportGenerator.ReportGenerator('octroi_customer_wise_report.xlsx')
            col_heads = ('Customer',
	    	'Octroi Charge', #2
	    	'Ecomm Charge', #3
	    	'Total') #8
            data =[]
            oct_list = OctroiBilling.objects.filter( bill_generation_date__range=[date_from,date_to]).values('customer__name').annotate( oct_charge=Sum('octroi_charge'),octroi_ecom_charge =Sum('octroi_ecom_charge'),total_payable_charge =Sum('total_payable_charge'))
            for li in oct_list:
                data.append([li['customer__name'],li['oct_charge'],li['octroi_ecom_charge'],li['total_payable_charge']])
            report.write_header(col_heads)
            path = report.write_body(data)
            return HttpResponseRedirect("/static/uploads/reports/%s"%(path))
        elif report_type == '1':
            date_from=request.POST['date_from']
            date_to=request.POST['date_to']
            cust=request.POST['cust_name']
            t = datetime.datetime.strptime(date_from, "%Y%m%d")
            date_from=t.strftime("%Y-%m-%d")
            t = datetime.datetime.strptime(date_to, "%Y%m%d")
            date_to=t.strftime("%Y-%m-%d")
            report = ReportGenerator.ReportGenerator('octroi_customer_report.xlsx')
            col_heads = ('Bill ID',
        	'Bill Date', #1
	        'Octroi Charge', #2
	        'Ecomm Charge', #3
	        'Total') #8
            data =[]
            octroi_bill = OctroiBilling.objects.filter( bill_generation_date__range=[date_from,date_to],customer__id=cust)
            if cust =='0':
                octroi_bill = OctroiBilling.objects.filter( bill_generation_date__range=[date_from,date_to])
            for octroi in  octroi_bill:
                bill_id = octroi.bill_id
                bill_generation_date = octroi.bill_generation_date
                octroi_charge = octroi.octroi_charge
                octroi_ecom_charge = octroi.octroi_ecom_charge
                total_payable_charge = octroi.total_payable_charge
                data.append([bill_id,bill_generation_date,octroi_charge,octroi_ecom_charge,total_payable_charge])
            report.write_header(col_heads)
            path = report.write_body(data)
            return HttpResponseRedirect("/static/uploads/reports/%s"%(path))


@csrf_exempt
def octroi_charge_change(request):
    if request.method == 'POST':
        oct_charge=request.POST['oct_charge']    
        ecomm_charge=request.POST['ecomm_charge']
        cu_id = request.POST['cu_id']
        obj = CustomerOctroiCharges.objects.get(customer__id = cu_id)
        obj.octroi_rate = oct_charge
        obj.octroi_charge = ecomm_charge
        obj.save()
        return HttpResponse("sucess")

